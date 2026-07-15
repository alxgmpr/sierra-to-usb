#!/usr/bin/env python3
"""Assert pin->net connectivity against a KiCad netlist export.

Usage: uv run tools/check_nets.py [--sch sierra-to-usb.kicad_sch] [--checks tools/netchecks.txt]
Exit 0 = all assertions pass. Prints each failure.
"""
import argparse, re, subprocess, sys, tempfile, xml.etree.ElementTree as ET
from pathlib import Path

KCLI = "/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli"

def export_netlist(sch: Path) -> ET.Element:
    with tempfile.NamedTemporaryFile(suffix=".xml", delete=False) as f:
        out = Path(f.name)
    subprocess.run([KCLI, "sch", "export", "netlist", "--format", "kicadxml",
                    "-o", str(out), str(sch)], check=True, capture_output=True)
    return ET.parse(out).getroot()

def build_index(root: ET.Element):
    """pin_by_num[(ref, pinnum)] -> net ; pin_by_fn[(ref, pinfunction)] -> set(nets) ; net_pins[net] -> count"""
    by_num, by_fn, net_pins = {}, {}, {}
    for net in root.iter("net"):
        # hierarchical nets export as "/sheet_path/NAME" — match on the leaf name
        name = net.get("name").split("/")[-1]
        for node in net.iter("node"):
            ref, pin = node.get("ref"), node.get("pin")
            by_num[(ref, pin)] = name
            fn = node.get("pinfunction")
            if fn:
                # kicad-cli's kicadxml exporter always suffixes pinfunction
                # with "_<pin number>" (e.g. CFG1 on pad 9 -> "CFG1_9"), even
                # for genuinely KiCad-GUI-authored schematics (verified
                # against this project's original human-authored placeholder
                # schematic, commit 0cea16b) -- strip that exact suffix so
                # checks can match on the real pin function name.
                if fn.endswith(f"_{pin}"):
                    fn = fn[: -len(f"_{pin}")]
                by_fn.setdefault((ref, fn.upper()), set()).add(name)
            net_pins[name] = net_pins.get(name, 0) + 1
    return by_num, by_fn, net_pins

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sch", default="sierra-to-usb.kicad_sch")
    ap.add_argument("--checks", default="tools/netchecks.txt")
    args = ap.parse_args()
    by_num, by_fn, net_pins = build_index(export_netlist(Path(args.sch)))
    failures = 0
    for lineno, raw in enumerate(Path(args.checks).read_text().splitlines(), 1):
        line = raw.split("#")[0].strip()
        if not line:
            continue
        m = re.fullmatch(r"NET\s+(\S+)\s+PINS>=(\d+)", line)
        if m:
            net, need = m.group(1), int(m.group(2))
            if net_pins.get(net, 0) < need:
                print(f"FAIL L{lineno}: net {net} has {net_pins.get(net,0)} pins, need >={need}")
                failures += 1
            continue
        m = re.fullmatch(r"(\S+?)\.(pinfn:)?(\S+)\s*=\s*(\S+)", line)
        if not m:
            print(f"FAIL L{lineno}: unparseable: {raw}")
            failures += 1
            continue
        ref, isfn, pin, want = m.group(1), m.group(2), m.group(3), m.group(4)
        if isfn:
            got = by_fn.get((ref, pin.upper()), set())
            ok = want in got
            gotstr = ",".join(sorted(got)) or "<unconnected>"
        else:
            gotnet = by_num.get((ref, pin))
            ok = gotnet == want
            gotstr = gotnet or "<unconnected>"
        if not ok:
            print(f"FAIL L{lineno}: {ref}.{pin} on '{gotstr}', want '{want}'")
            failures += 1
    print(f"{failures} failure(s)" if failures else "all checks pass")
    sys.exit(1 if failures else 0)

if __name__ == "__main__":
    main()
