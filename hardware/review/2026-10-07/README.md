# Appliance engineering review — 2026-10-07

[30-sheet PDF](appliance.pdf) · [663-row BOM inventory](bom.csv) ·
[Full connectivity report](capture-report.json) · [All-severity ERC report](erc.json) ·
[Footprint / model / native synchronization audit](../../../docs/footprint-audit.md) ·
[Evidence and input hashes](evidence-manifest.json)

The export contains 663 components / 823 nets and zero ERC violations.
All 30 sheets were rendered and inspected during the original capture. Two successive capture regenerations
were byte-identical across 85 native source/map files. Independent native pin and
BGA-coordinate checks pass within the limitations printed by each checker.
The modem analytical report also reproduces exactly; it is not a measured result.

The BOM lists one row per reference, including 13 default DNP references and
three PCB test pads. It is an engineering inventory, not a purchasing release.
Default assembly is the Quectel stuffing pattern; the four modem profiles remain
unreleased. `appliance.xml` is the actual exported native netlist. The two
`poe-*.xml` files are original TI source netlists used for retained-topology checks.

All 663 footprints are now assigned, with 572 stock hand-solder choices. Both
native editor update directions report zero errors/warnings and no proposed
changes. The PCB remains unrouted: 791 physical DRC violations and 499
unconnected items. Six land-pattern release reviews and 34 component model
holds remain explicit. Current controlled modem guides, electrical/software/
thermal/isolation/RF tests, layout and fabrication release remain open.
See [completion and release holds](../../../docs/schematic-completion.md).

Run from the repository root:

```sh
python3 hardware/check.py --output /tmp/sierra-capture-check
python3 hardware/tools/check_board_sync.py --output /tmp/sierra-board-check
python3 hardware/tools/export_appliance.py --output /tmp/sierra-appliance-review
```

The evidence manifest records the KiCad version, base commit, source/input hashes
and exported artifact hashes. Exports may include timestamps and absolute paths;
the original regeneration claim is preserved in
`evidence-manifest-before-footprint-audit.json`. Current source and output hashes
are in `evidence-manifest.json`; no claim of regenerating manual editor graphics
is made for this footprint audit.
