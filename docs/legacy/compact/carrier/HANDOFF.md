> Historical evidence from superseded designs. See the [current full adapter](../../../../full-adapter/README.md). Circuit status and artifact paths below refer to the historical checkpoint, not the replacement.

# Placement-stage handoff

All paths below are relative to this directory. Use the files listed here as the current handoff; other build images/logs may be intermediate review material. No fabrication release is implied.

| Artifact | File |
|---|---|
| KiCad project / schematic / unrouted board | [carrier.kicad_pro](carrier.kicad_pro), [carrier.kicad_sch](carrier.kicad_sch), [carrier.kicad_pcb](carrier.kicad_pcb) |
| Complete schematic PDF | [build/carrier-development.pdf](build/carrier-development.pdf) — legacy filename, currentPLACEMENT1 content |
| Circuit BOM / netlist | [build/development-bom.csv](build/development-bom.csv), [build/carrier.xml](build/carrier.xml) |
| Off-board/mechanical assembly materials | [assembly-materials.csv](assembly-materials.csv) |
| Placement / dimensions | [build/placement-drawing.pdf](build/placement-drawing.pdf), [build/mechanical-drawing.pdf](build/mechanical-drawing.pdf), [build/component-positions.csv](build/component-positions.csv) |
| Assembly envelope STEP / views | [build/assembly-envelopes.step](build/assembly-envelopes.step), [isometric](build/assembly-3d-isometric.png), [top](build/assembly-3d-top.png) |
| Checks / visual evidence | [build/check-summary.json](build/check-summary.json), [build/erc.json](build/erc.json), [build/placement-drc.json](build/placement-drc.json), [build/board-checks.json](build/board-checks.json), [build/model-checks.json](build/model-checks.json), [build/visual-review.json](build/visual-review.json) |
| Routing / design gates | [ROUTING.md](ROUTING.md), [REVIEW.md](REVIEW.md) |
| Electrical reviews | [source-to-pin-review.md](source-to-pin-review.md), [power-review.md](power-review.md), [passive-review.md](passive-review.md), [protection-review.md](protection-review.md), [sequencing-review.md](sequencing-review.md) |
| Assembly / programming | [mechanical-review.md](mechanical-review.md), [profile-assembly.md](profile-assembly.md), [cc-programming.md](cc-programming.md) |
| Compatibility / sources | [../review/compatibility-matrix.md](../review/compatibility-matrix.md), [../review/compatibility-matrix.csv](../review/compatibility-matrix.csv), [../review/source-register.json](../review/source-register.json) |

The STEP and renders retain the module/support and component models, including all five exact-part KiCad SMA models and the reconstructed TI RPW package. The large cooler, retention frame/posts, thermal tape and orange profile-service placeholder have been removed. Adhesive cooling is selected at assembly and intentionally unmodeled. J202 remains the standard keyed 20-pin 3M IDC profile header. J201/J202 and the RM520N-style card/support now have opaque detailed reconstructed models; see model-sources.md for provenance. Rounded mounting ears give a110×114 mm overall outline, with selectable3042/3052 support holes. Bounds verification and visual review are not a detailed mechanical interference certification.

## Reproduce without changing placement

From repository root, run `compact/.venv/bin/python compact/carrier/export_handoff.py`. It exports/checks the existing schematic and board, runs19 unit tests, refreshes power/stack calculations, verifies custom STEP bounds and exports review PDFs/SVG/positions/STEP/PNG. It never invokes zone fill or produces fabrication outputs. Re-render the mechanical drawing with the bundled Python containing ReportLab, using `compact/carrier/mechanical_pdf.py`. Manually review changed outputs before updating visual-review.json and the final summary.

The environment uses KiCad10.99.0-3397-g20deb141, Python3.13 with sexpdata/KicadModTree/numpy/scipy/cadquery-ocp, ReportLab for the mechanical PDF, and Poppler for visual review. The export script uses an isolated `build/viewer-config/` so mechanical envelopes appear without changing the user's3D preferences. Paths to KiCad and the bundled runtime may need adjustment on another machine. Standard KiCad libraries and the root `lib/` assets remain dependencies; keep the full repository together.

## Rebuild generated design only before manual routing

Run, in order: `footprints.py`, `models.py`, `detailed_models.py`, `build.py`, `export_review.py`, then `board.py`, all with `compact/.venv/bin/python` and the `compact/carrier/` prefix. Then run `export_handoff.py` and visually review. Each design/model generator checks its own existing output hashes before writing. `placement.json` is the deliberate placement source; carrier.kicad_pro and carrier.kicad_dru retain the review rules. Do not bypass a guard or run the board generator over a manually routed board.

The raw schematic and PCB export filenames retain some development naming for reproducibility. Final checks identify the actualPLACEMENT1 design by file hashes. Historical rejected-power files elsewhere under compact/ are not part of the circuit BOM.
