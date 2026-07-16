#!/usr/bin/env python3
"""Netclass-membership regression gate.

Verifies that the netclass patterns in sierra-to-usb.kicad_pro actually
match the hierarchical net names in the board, because KiCad patterns
match the FULL net name including sheet path ("/Power Input/POE_VSS"),
and a bare pattern like "POE_*" silently matches nothing hierarchical.
This exact failure made the 2.5mm PoE moat and every impedance rule a
no-op until 2026-07-16 (patterns restored from Task 15 matched only the
4 global magjack tap nets, and RF_50 matched zero nets).

Checks:
  1. POE_PRI class == the primary domain derived by connectivity walk
     (BFS from the PoE input nets, crossing every component except the
     certified barrier parts T1/U20/U23/C19/J8, which only conduct on
     their primary-side pads) + U10's unconnected-pad nets. Extra OR
     missing nets are both failures (a rename, a new clamp part, or a
     pattern typo shows up here).
  2. The walk must never reach GND or any secondary rail (barrier
     integrity at netlist level).
  3. POE_STS_RAW (opto-isolated secondary status) must NOT be POE_PRI.
  4. Each impedance class matches a sane, non-zero net count:
     DIFF_USB_90 >= 12, DIFF_PCIE_85 >= 6, DIFF_MDI_100 == 8, RF_50 == 5.

Run from the repo root: uv run tools/check_netclasses.py
"""
import fnmatch
import json
import re
import sys
from collections import defaultdict, deque
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PCB = ROOT / "sierra-to-usb.kicad_pcb"
PRO = ROOT / "sierra-to-usb.kicad_pro"

# Barrier parts: ref -> pads on the PRIMARY side (conduction stops here)
BARRIER = {
    "T1": {"1", "2", "3", "4", "5"},
    "U20": {"3", "4"},
    "U23": {"1", "2"},
    "C19": set(),
    "J8": {"13", "14", "15", "16"},
}
SEEDS = {
    "POE_VA+", "POE_VA-", "POE_VB+", "POE_VB-",
    "/Power Input/POE_VDD54", "/Power Input/POE_VDD54_F",
    "/Power Input/POE_VSS", "/Power Input/POE_RTN",
}
FORBIDDEN = {"GND", "+3V3", "+12V", "+5V", "+1V8", "POE_STS_RAW"}


def main() -> int:
    text = PCB.read_text()
    nets = sorted(set(re.findall(r'\(net "([^"]+)"\)', text)))

    compnets = defaultdict(list)
    for block in text.split("\n\t(footprint ")[1:]:
        rm = re.search(r'\(property "Reference" "([^"]+)"', block)
        if not rm:
            continue
        for pm in re.finditer(
            r'\(pad "([^"]*)"[^\n]*\n(?:(?!\t\t\(pad )(?:.|\n))*?\(net "([^"]+)"\)',
            block,
        ):
            compnets[rm.group(1)].append((pm.group(1), pm.group(2)))

    net2pins = defaultdict(list)
    for ref, pins in compnets.items():
        for pad, net in pins:
            net2pins[net].append((ref, pad))

    primary = {s for s in SEEDS if s in net2pins}
    queue = deque(primary)
    while queue:
        net = queue.popleft()
        for ref, pad in net2pins[net]:
            allowed = BARRIER.get(ref)
            if allowed is not None and pad not in allowed:
                continue
            for pad2, net2 in compnets[ref]:
                if allowed is not None and pad2 not in allowed:
                    continue
                if net2 not in primary:
                    primary.add(net2)
                    queue.append(net2)

    failures = []
    hit = primary & FORBIDDEN
    if hit:
        failures.append(f"barrier breach: walk reached {sorted(hit)}")

    pro = json.loads(PRO.read_text())
    pats = pro["net_settings"]["netclass_patterns"]

    def members(cls):
        plist = [x["pattern"] for x in pats if x["netclass"] == cls and x["pattern"]]
        return {n for n in nets for p in plist if fnmatch.fnmatchcase(n, p)}

    poe = members("POE_PRI")
    if "POE_STS_RAW" in poe:
        failures.append("POE_STS_RAW (secondary, opto-isolated) classed POE_PRI")
    missing = primary - poe
    extra = {n for n in poe - primary if not n.startswith("unconnected-(U10-")}
    if missing:
        failures.append(f"primary nets NOT in POE_PRI class: {sorted(missing)}")
    if extra:
        failures.append(f"POE_PRI class contains non-primary nets: {sorted(extra)}")

    for cls, op, want in (
        ("DIFF_USB_90", ">=", 12),
        ("DIFF_PCIE_85", ">=", 6),
        ("DIFF_MDI_100", "==", 8),
        ("RF_50", "==", 5),
    ):
        n = len(members(cls))
        ok = n >= want if op == ">=" else n == want
        if not ok:
            failures.append(f"{cls}: {n} nets matched, expected {op}{want}")

    if failures:
        for f in failures:
            print(f"FAIL: {f}")
        return 1
    print(f"all netclass checks pass ({len(primary)} primary nets, "
          f"{len(poe)} in POE_PRI class)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
