# Appliance engineering review — 2026-10-07

[30-sheet PDF](appliance.pdf) · [663-row BOM inventory](bom.csv) ·
[Full connectivity report](capture-report.json) · [All-severity ERC report](erc.json) ·
[Evidence and input hashes](evidence-manifest.json)

The export contains 663 components / 823 nets and zero ERC violations.
All 30 sheets were rendered and inspected. Two successive capture regenerations
were byte-identical across 85 native source/map files. Independent native pin and
BGA-coordinate checks pass within the limitations printed by each checker.
The modem analytical report also reproduces exactly; it is not a measured result.

The BOM lists one row per reference, including 13 default DNP references and
three PCB test pads. It is an engineering inventory, not a purchasing release.
Default assembly is the Quectel stuffing pattern; the four modem profiles remain
unreleased. `appliance.xml` is the actual exported native netlist. The two
`poe-*.xml` files are original TI source netlists used for retained-topology checks.

Six footprints remain intentionally unassigned. Current controlled modem guides,
land patterns, electrical/software/thermal/isolation/RF tests, PCB and fabrication
outputs remain open. See [completion and release holds](../../../docs/schematic-completion.md).

Run from the repository root:

```sh
python3 hardware/tools/build_capture.py
python3 hardware/tools/export_appliance.py --output /tmp/sierra-appliance-review
```

The evidence manifest records the KiCad version, base commit, source/input hashes
and exported artifact hashes. Exports may include timestamps and absolute paths;
the regeneration claim applies to native capture sources, not PDF/XML metadata.
