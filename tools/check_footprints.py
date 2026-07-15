#!/usr/bin/env python3
"""Assert footprint/assembly-split BOM hygiene for every schematic symbol.

Checks (Task 14 gate, mirrors check_nets.py's role for connectivity):
  1. Every BOM symbol has a non-empty Footprint and Assembly field.
  2. Every Assembly=JLC symbol has a non-empty LCSC field.
  3. Every symbol's resolved footprint file exists (stock KiCad library or
     this project's lib/sierra-to-usb.pretty) and its pad count is >= the
     symbol's pin count (parsed from the real .kicad_sym / stock library
     pin list via kicad-cli's netlist export -- not guessed).

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


def build_ref_libsource(root: ET.Element):
    """ref -> (lib, part)"""
    out = {}
    for comp in root.iter("comp"):
        ref = comp.get("ref")
        ls = comp.find("libsource")
        if ls is not None:
            out[ref] = (ls.get("lib"), ls.get("part"))
    return out


PAD_RE = re.compile(r'\(pad\s+"([^"]*)"')


def footprint_pad_count(lib: str, name: str):
    """Return (pad_count, resolved_path) or (None, expected_path) if missing.
    Pad count = number of DISTINCT non-empty pad numbers (paste-only/mechanical
    relief pads use an empty pad number "" and carry no net -- excluded)."""
    if lib == "sierra-to-usb":
        path = PROJECT_ROOT / "lib" / "sierra-to-usb.pretty" / f"{name}.kicad_mod"
    else:
        path = STOCK_FP_ROOT / f"{lib}.pretty" / f"{name}.kicad_mod"
    if not path.exists():
        return None, path
    text = path.read_text()
    nums = {m.group(1) for m in PAD_RE.finditer(text) if m.group(1) != ""}
    return len(nums), path


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
    ref_libsource = build_ref_libsource(netlist_root)

    failures = []

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
        pad_count, fp_path = footprint_pad_count(lib, name)
        if pad_count is None:
            failures.append(f"{ref}: footprint file not found: {fp_path}")
            continue

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
