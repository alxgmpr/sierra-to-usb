#!/usr/bin/env python3
"""Assert footprint/assembly-split BOM hygiene for every schematic symbol.

Checks (Task 14 gate, mirrors check_nets.py's role for connectivity):
  1. Every BOM symbol has a non-empty Footprint and Assembly field.
  2. Every Assembly=JLC symbol has a non-empty LCSC field.
  3. Every symbol's resolved footprint file exists (stock KiCad library or
     this project's lib/sierra-to-usb.pretty) and its pad count is >= the
     symbol's pin count (parsed from the real .kicad_sym / stock library
     pin list via kicad-cli's netlist export -- not guessed).
  4. (Task 14 fix pass) Pad-NAME coverage: every symbol pin NUMBER (parsed
     from the same netlist export) has a matching pad number in the
     resolved footprint's real pad set. This is strictly stronger than #3's
     count-only check -- it catches a symbol/footprint pair where the
     counts happen to agree but KiCad's "Update PCB from Schematic" (which
     binds pads to pins by exact pin-number-string equality) would still
     fail to bind one or more pins, e.g. a letter-numbered symbol (D/G/S)
     bound to a numerically-padded real-world footprint (1/2/3...).
  5. (Task 15 import-mismatch fix) REVERSE pad coverage: every footprint PAD
     NUMBER must have a matching symbol pin, i.e. the mirror image of #4.
     This is the direction #4 cannot catch -- a symbol with FEWER distinct
     pin numbers than the footprint has pads (e.g. one symbol pin
     representing 3 physically-separate-but-electrically-tied footprint
     pads) leaves the extra pads with no home, and KiCad's "Update PCB from
     Schematic" reports them as orphaned/unconnected pads on import even
     though the symbol/footprint pair passes #3 and #4 cleanly. Any pad
     legitimately left unmapped (true no-connect pins, mechanical/thermal
     pads with no defined signal) must be listed in REVERSE_ALLOWLIST below
     with a documented reason -- silent gaps are a failure.

Usage: uv run tools/check_footprints.py [--sch sierra-to-usb.kicad_sch]
Exit 0 = all assertions pass. Prints each failure.
"""
import argparse, csv, re, subprocess, sys, tempfile, xml.etree.ElementTree as ET
from pathlib import Path

KCLI = "/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli"
STOCK_FP_ROOT = Path("/Applications/KiCad/KiCad.app/Contents/SharedSupport/footprints")
PROJECT_ROOT = Path(__file__).resolve().parent.parent


def export_bom(sch: Path) -> list[dict]:
    with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as f:
        out = Path(f.name)
    subprocess.run(
        [KCLI, "sch", "export", "bom", str(sch),
         "--fields", "Reference,Value,Footprint,Assembly,LCSC,MPN,Distributor",
         "-o", str(out)],
        check=True, capture_output=True,
    )
    return list(csv.DictReader(out.open()))


def export_netlist(sch: Path) -> ET.Element:
    with tempfile.NamedTemporaryFile(suffix=".xml", delete=False) as f:
        out = Path(f.name)
    subprocess.run(
        [KCLI, "sch", "export", "netlist", "--format", "kicadxml",
         "-o", str(out), str(sch)],
        check=True, capture_output=True,
    )
    return ET.parse(out).getroot()


def build_pin_counts(root: ET.Element):
    """(lib,part) -> distinct pin-number count, from <libparts>."""
    counts = {}
    for lp in root.iter("libpart"):
        lib, part = lp.get("lib"), lp.get("part")
        pins = lp.find("pins")
        nums = set()
        if pins is not None:
            for p in pins.findall("pin"):
                nums.add(p.get("num"))
        counts[(lib, part)] = len(nums)
    return counts


def build_pin_numbers(root: ET.Element):
    """(lib,part) -> list of (num, name) for every symbol pin, from <libparts>.

    Used for the pad-NAME coverage check (Task 14 fix pass): pad-COUNT alone
    (build_pin_counts above) cannot catch a symbol/footprint pair where the
    counts happen to agree but the individual pin NUMBERS don't actually
    exist on the footprint (e.g. letter-numbered symbol pins D/G/S bound to
    a numerically-padded real-world footprint) -- that's exactly the defect
    class the review flagged as the Task-15 blocker."""
    out = {}
    for lp in root.iter("libpart"):
        lib, part = lp.get("lib"), lp.get("part")
        pins = lp.find("pins")
        plist = []
        if pins is not None:
            for p in pins.findall("pin"):
                plist.append((p.get("num"), p.get("name")))
        out[(lib, part)] = plist
    return out


def build_ref_libsource(root: ET.Element):
    """ref -> (lib, part)"""
    out = {}
    for comp in root.iter("comp"):
        ref = comp.get("ref")
        ls = comp.find("libsource")
        if ls is not None:
            out[ref] = (ls.get("lib"), ls.get("part"))
    return out


# Task 15 reverse-check allowlist: (ref, pad_number) -> documented reason.
# Every entry here is a footprint pad KiCad's "Update PCB from Schematic"
# will legitimately leave unbound (no symbol pin claims it) -- verified
# against the real manufacturer datasheet/mechanical drawing, not guessed.
REVERSE_ALLOWLIST = {
    ("U22", "1"): (
        "TL431IDBVR, TI TL431/TL432 datasheet SLVS543S (rev. May 2024) "
        "Sec.5 pin diagram + Table 5-1: DBV (SOT-23-5) package pin 1 is "
        "NC (No internal connection) for the TL431x pinout -- there is no "
        "electrode to bind."
    ),
    ("U22", "2"): (
        "TL431IDBVR, same source: DBV package pin 2 is marked with a dagger "
        "footnote 'Pin 2 is attached to Substrate and must be connected to "
        "ANODE or left open.' Left open here (no netlist connection was "
        "added -- see Task 15 import-mismatch report for the net-to-"
        "electrode proof); a legitimate no-connect per TI's own datasheet, "
        "not a binding defect."
    ),
    ("U30", "9"): (
        "ST4SIM-200M (VFDFPN8_MFF2 custom footprint): pad 9 is the center "
        "exposed thermal/die-attach pad. Per the footprint's own descr "
        "field (sourced from ConnectedYou MFF2 Packaging spec v1.1 cross-"
        "checked against ST DB4082 Fig.12/Table 4), this pad 'carries no "
        "defined signal in either numbering scheme' -- mechanical/thermal "
        "only, correctly left off the 8-pin symbol."
    ),
}

PAD_RE = re.compile(r'\(pad\s+"([^"]*)"')


def footprint_pad_set(lib: str, name: str):
    """Return (set_of_distinct_pad_numbers, resolved_path) or (None, expected_path)
    if the footprint file is missing. Excludes empty-numbered pads (paste-only/
    mechanical relief pads carry no net)."""
    if lib == "sierra-to-usb":
        path = PROJECT_ROOT / "lib" / "sierra-to-usb.pretty" / f"{name}.kicad_mod"
    else:
        path = STOCK_FP_ROOT / f"{lib}.pretty" / f"{name}.kicad_mod"
    if not path.exists():
        return None, path
    text = path.read_text()
    nums = {m.group(1) for m in PAD_RE.finditer(text) if m.group(1) != ""}
    return nums, path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sch", default="sierra-to-usb.kicad_sch")
    args = ap.parse_args()
    sch = Path(args.sch)
    if not sch.is_absolute():
        sch = PROJECT_ROOT / sch

    bom = export_bom(sch)
    netlist_root = export_netlist(sch)
    pin_counts = build_pin_counts(netlist_root)
    pin_numbers = build_pin_numbers(netlist_root)
    ref_libsource = build_ref_libsource(netlist_root)

    failures = []
    used_allowlist_keys = set()

    for row in bom:
        ref = row["Reference"]
        fp = row["Footprint"].strip()
        asm = row["Assembly"].strip()
        lcsc = row["LCSC"].strip()

        if not fp:
            failures.append(f"{ref}: empty Footprint")
        if not asm:
            failures.append(f"{ref}: empty Assembly")
        if asm == "JLC" and not lcsc:
            failures.append(f"{ref}: Assembly=JLC but empty LCSC")

        if not fp or ":" not in fp:
            if fp:
                failures.append(f"{ref}: Footprint '{fp}' missing 'Library:Name' form")
            continue

        lib, name = fp.split(":", 1)
        pad_set, fp_path = footprint_pad_set(lib, name)
        if pad_set is None:
            failures.append(f"{ref}: footprint file not found: {fp_path}")
            continue
        pad_count = len(pad_set)

        libsrc = ref_libsource.get(ref)
        if libsrc is None:
            failures.append(f"{ref}: not found in netlist libsource map")
            continue
        pin_count = pin_counts.get(libsrc)
        if pin_count is None:
            failures.append(f"{ref}: no pin data for libsource {libsrc}")
            continue

        if pad_count < pin_count:
            failures.append(
                f"{ref}: footprint '{fp}' has {pad_count} pads < symbol "
                f"{libsrc} has {pin_count} pins"
            )

        # Pad-NAME coverage (Task 14 fix pass): pad-COUNT agreement alone does
        # not prove KiCad's "Update PCB from Schematic" can actually bind
        # every symbol pin -- that matches footprint pads to symbol pins by
        # EXACT pin-NUMBER-string equality, so a symbol with letter pin
        # numbers (D/G/S) bound to a footprint with numeric pads (1/2/3...)
        # can pass the count check above while every pin silently fails to
        # bind. Assert every symbol pin NUMBER has a matching pad in the
        # resolved footprint's real pad set.
        for num, pname in pin_numbers.get(libsrc, []):
            if num not in pad_set:
                failures.append(
                    f"{ref}: symbol pin {num} ('{pname}', {libsrc}) has no "
                    f"matching pad in footprint '{fp}' (pads: "
                    f"{','.join(sorted(pad_set, key=lambda s: (len(s), s)))})"
                )

        # Reverse pad coverage (Task 15 import-mismatch fix, item 5): every
        # footprint PAD must have a matching symbol pin, unless explicitly
        # allowlisted above with a documented reason. This is what actually
        # reproduces "Update PCB from Schematic"'s orphaned-pad warnings --
        # #4 above only proves every symbol pin has a home, not the reverse.
        pin_num_set = {num for num, _ in pin_numbers.get(libsrc, [])}
        for pad_num in sorted(pad_set - pin_num_set, key=lambda s: (len(s), s)):
            key = (ref, pad_num)
            reason = REVERSE_ALLOWLIST.get(key)
            if reason is None:
                failures.append(
                    f"{ref}: footprint '{fp}' pad {pad_num} has no matching "
                    f"symbol pin ({libsrc} pins: "
                    f"{','.join(sorted(pin_num_set, key=lambda s: (len(s), s)))}) "
                    f"-- not in REVERSE_ALLOWLIST"
                )
            else:
                used_allowlist_keys.add(key)

    # Every allowlist entry must actually have been exercised by the current
    # BOM/footprint state, otherwise it's a stale waiver silently masking a
    # regression (e.g. a footprint swap that removes the pad it was excusing,
    # or a ref that no longer exists).
    for key in REVERSE_ALLOWLIST:
        if key not in used_allowlist_keys:
            failures.append(
                f"REVERSE_ALLOWLIST entry {key} is stale -- no longer "
                f"matches an actual unmapped pad; remove it or investigate "
                f"why the pad it excused disappeared"
            )

    print(f"{len(bom)} BOM rows checked")
    if failures:
        print(f"{len(failures)} failure(s):")
        for f in failures:
            print(" ", f)
    else:
        print("all checks pass")
    sys.exit(1 if failures else 0)


if __name__ == "__main__":
    main()
