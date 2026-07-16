#!/usr/bin/env python3
"""Assert 3D-model + geometry-source coverage for every footprint in use (Task 14b gate).

Checks, for every unique footprint referenced by a BOM symbol:
  1. MODEL: the resolved .kicad_mod contains at least one (model ...) entry whose
     file actually exists on disk after variable expansion
     (${KIPRJMOD} -> this project, ${KICADn_3DMODEL_DIR} -> the KiCad app's
     SharedSupport/3dmodels), OR the footprint is listed in MODEL_ALLOWLIST
     below with a documented reason. An allowlisted footprint whose model
     STARTS resolving flags the entry as stale.
  2. GEOMETRY SOURCE: docs/footprint-verification.md contains a table row for
     the footprint whose Source column is one of the accepted tags
     (JLC-verified / mfr-drawing / KiCad-stock / approximation). A source of
     'approximation' is only accepted for footprints in APPROX_REFLAGGED
     below (explicitly re-flagged with what is still unobtainable).

Rows with an empty Footprint field are skipped here -- check_footprints.py
owns that failure mode.

Usage: uv run tools/check_3d.py [--sch sierra-to-usb.kicad_sch]
Exit 0 = all assertions pass. Prints each failure.
"""
import argparse, csv, re, subprocess, sys, tempfile
from pathlib import Path

KCLI = "/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli"
STOCK_FP_ROOT = Path("/Applications/KiCad/KiCad.app/Contents/SharedSupport/footprints")
STOCK_3D_ROOT = Path("/Applications/KiCad/KiCad.app/Contents/SharedSupport/3dmodels")
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DOCS_TABLE = PROJECT_ROOT / "docs" / "footprint-verification.md"

ACCEPTED_SOURCES = {"JLC-verified", "mfr-drawing", "KiCad-stock", "approximation"}

# Footprints allowed to have NO resolvable 3D model -- each with a documented
# reason. Anything else in use must carry a (model ...) whose file exists.
MODEL_ALLOWLIST = {
    "TestPoint:TestPoint_Pad_D1.5mm":
        "Bare copper test pad -- no physical component body exists; KiCad's "
        "own TestPoint footprints ship without models.",
    "Jumper:SolderJumper-2_P1.3mm_Open_RoundedPad1.0x1.5mm":
        "Copper-only solder-jumper feature -- no physical component body; "
        "KiCad's own SolderJumper footprints ship without models.",
    "Connector_USB:USB_C_Receptacle_HRO_TYPE-C-31-M-12":
        "KiCad 10 official footprint references "
        "${KICAD10_3DMODEL_DIR}/Connector_USB.3dshapes/...M-12.step which the "
        "official 3dmodels package simply does not ship (KiCad's model "
        "library lags its footprint library). Geometry unaffected; an "
        "EasyEDA C165948 STEP was cross-checked against this footprint at "
        "Task 14b (A-row pads agree within 0.11mm).",
    "Inductor_SMD:L_6.3x6.3_H3":
        "KiCad 10 official footprint; its referenced official model is not "
        "shipped in the 3dmodels package. Generic 6.3x6.3mm body.",
    "Inductor_SMD:L_Bourns-SRN8040_8x8.15mm":
        "KiCad 10 official footprint; its referenced official model is not "
        "shipped in the 3dmodels package.",
    "Package_DFN_QFN:QFN-48-1EP_6x6mm_P0.4mm_EP4.3x4.3mm":
        "KiCad 10 official footprint; its referenced official model is not "
        "shipped in the 3dmodels package.",
    "Package_DFN_QFN:Texas_RNH0030A_WQFN-30-1EP_2.5x4.5mm_P0.4mm_EP1.2x3.2mm":
        "KiCad 10 official footprint; its referenced official model is not "
        "shipped in the 3dmodels package.",
}

# Footprints whose docs Source row is allowed to read 'approximation' -- the
# durable re-flag demanded by Task 14b for anything still unobtainable.
APPROX_REFLAGGED = {
    "sierra-to-usb:NanoSIM_JXTCONN_CSIM-H137-7P":
        "JXTCONN CSIM-H137-7P (LCSC C42420236): JLC stocks the part but the "
        "EasyEDA API has no footprint/CAD data for it (verified again at "
        "Task 14b: easyeda2kicad and the raw EasyEDA products API both "
        "return 404 'Component not found'), and no JXTCONN drawing is "
        "machine-retrievable. Pad grid remains the ATTEND 115U-A103 "
        "cross-vendor commodity pattern -- needs physical-sample "
        "confirmation before fab.",
}

MODEL_RE = re.compile(r'\(model\s+"([^"]+)"')
VAR_RE = re.compile(r"\$\{([A-Za-z0-9_]+)\}")


def export_bom(sch: Path) -> list[dict]:
    with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as f:
        out = Path(f.name)
    subprocess.run(
        [KCLI, "sch", "export", "bom", str(sch),
         "--fields", "Reference,Value,Footprint",
         "-o", str(out)],
        check=True, capture_output=True,
    )
    return list(csv.DictReader(out.open()))


def fp_path(fp: str) -> Path:
    lib, name = fp.split(":", 1)
    if lib == "sierra-to-usb":
        return PROJECT_ROOT / "lib" / "sierra-to-usb.pretty" / f"{name}.kicad_mod"
    return STOCK_FP_ROOT / f"{lib}.pretty" / f"{name}.kicad_mod"


def expand(model: str) -> Path:
    def sub(m):
        var = m.group(1)
        if var == "KIPRJMOD":
            return str(PROJECT_ROOT)
        if re.fullmatch(r"KICAD\d+_3DMODEL_DIR", var):
            return str(STOCK_3D_ROOT)
        return m.group(0)
    return Path(VAR_RE.sub(sub, model))


def parse_docs_sources() -> dict[str, str]:
    """footprint -> source tag, from the markdown table in DOCS_TABLE."""
    sources = {}
    if not DOCS_TABLE.exists():
        return sources
    for line in DOCS_TABLE.read_text().splitlines():
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) >= 2 and ":" in cells[0]:
            fp = cells[0].strip("`")
            src = cells[1].strip("`* ")
            sources[fp] = src
    return sources


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sch", default="sierra-to-usb.kicad_sch")
    args = ap.parse_args()
    sch = Path(args.sch)
    if not sch.is_absolute():
        sch = PROJECT_ROOT / sch

    bom = export_bom(sch)
    fps = sorted({row["Footprint"].strip() for row in bom
                  if row["Footprint"].strip() and ":" in row["Footprint"]})
    docs_sources = parse_docs_sources()

    failures = []
    used_model_allow = set()
    n_model_ok = 0

    for fp in fps:
        path = fp_path(fp)
        if not path.exists():
            failures.append(f"{fp}: footprint file not found: {path}")
            continue
        text = path.read_text()
        models = MODEL_RE.findall(text)
        resolved = [m for m in models if expand(m).exists()]
        if resolved:
            n_model_ok += 1
            if fp in MODEL_ALLOWLIST:
                failures.append(
                    f"{fp}: MODEL_ALLOWLIST entry is stale -- footprint now "
                    f"has a resolving model ({resolved[0]}); remove the entry"
                )
        elif fp in MODEL_ALLOWLIST:
            used_model_allow.add(fp)
        elif models:
            failures.append(
                f"{fp}: (model) entry present but no referenced file exists "
                f"on disk: {models}"
            )
        else:
            failures.append(
                f"{fp}: no (model ...) entry and not in MODEL_ALLOWLIST"
            )

        src = docs_sources.get(fp)
        if src is None:
            failures.append(
                f"{fp}: no geometry-source row in {DOCS_TABLE.name}"
            )
        elif src not in ACCEPTED_SOURCES:
            failures.append(
                f"{fp}: docs source '{src}' not in {sorted(ACCEPTED_SOURCES)}"
            )
        elif src == "approximation" and fp not in APPROX_REFLAGGED:
            failures.append(
                f"{fp}: source 'approximation' but footprint is not "
                f"re-flagged in APPROX_REFLAGGED with a documented reason"
            )

    for fp, _ in APPROX_REFLAGGED.items():
        if fp in fps and docs_sources.get(fp) != "approximation":
            failures.append(
                f"APPROX_REFLAGGED entry {fp} is stale -- docs row no longer "
                f"says 'approximation'; remove the entry"
            )
    for fp in MODEL_ALLOWLIST:
        if fp not in fps:
            failures.append(
                f"MODEL_ALLOWLIST entry {fp} is stale -- footprint no longer "
                f"in use; remove the entry"
            )

    print(f"{len(fps)} unique footprints checked; "
          f"{n_model_ok} with resolving 3D model, "
          f"{len(used_model_allow)} allowlisted (no model)")
    if failures:
        print(f"{len(failures)} failure(s):")
        for f in failures:
            print(" ", f)
    else:
        print("all checks pass")
    sys.exit(1 if failures else 0)


if __name__ == "__main__":
    main()
