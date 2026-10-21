# Footprint and modem review evidence — 2026-10-21

See [six-footprint disposition](../../../docs/footprint-review-2026-10-21.md)
and [modem blockers](../../../docs/modem-documentation.md) for sources and limits.

- `footprint-geometry.json`: all six independent drawing comparisons pass;
  four geometry holds closed, U801/U901 PCB land/process holds retained.
- `capture-report.json`, `erc.json`: 663 components, 823 nets, zero full ERC
  violations or exclusions; native major-pin coverage, DDR mappings, TI net
  partitions, modem stuffing isolation and electrical pad parity pass.
- `board-sync-report.json`, `drc.json`: 663 footprints, zero schematic parity
  issues and no attached-model path failures. The committed staging board has
  **771 physical DRC violations and 499 unconnected items**. It has no routing
  or outline. No rules/exclusions were weakened. It is not fabrication-ready.
- `step-model-report.json`: 48 unique attached STEP assets parse as valid shapes;
  this is not exact-MPN, tolerance or mechanical-clearance qualification.
- `modem-gates.json`: all four documentation gates remain enforced, with zero
  released profiles. Access checks and exact-module gaps are in the reference
  JSON, not inferred from an ERC pass.
- `negative-checks.json`: deliberately shifted VIN geometry, rounded RAM center,
  reversed RJ45 pin identity, wrong M.2 locating drill and unqualified modem
  release were each rejected. Temporary mutations were outside the repository.
- `svg/`: KiCad-native exports of the six reviewed footprints, plus a separate
  TPS56837 paste-only plot. The paste PNG was visually checked against TI p33.
- The two BGA model SVG/PNG views were visually inspected; package XY remains
  nominal and height uses the drawing maximum.
- `preservation-checks.json`: only U701/U801/U901 instances changed; 660 others,
  native links/transforms, net membership and non-footprint board items retained.
- `source-manifest.json`: native source hashes and KiCad version for this run.

Only U701/U801/U901 embedded PCB footprints were refreshed. Their native
component links, nets and board transforms were preserved. Other footprints and
schematic sources were not rewritten. October 7 native GUI round-trip reports
remain historical evidence; this run verifies native CLI parity and library
geometry, not a newly exercised pair of GUI dialogs.

The primary checkout already contained an uncommitted outline/UUID save. That
edit is deliberately excluded from this committed baseline and preserved during
integration. Its DRC counts can differ from the committed staging-board report.
Neither outline is an approved mechanical/manufacturing release.
