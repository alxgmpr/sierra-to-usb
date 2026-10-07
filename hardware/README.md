# Appliance schematic

The complete engineering capture is [appliance.kicad_sch](appliance.kicad_sch), with
30 sheets, 663 components and 823 native nets. Open [appliance.kicad_pro](appliance.kicad_pro)
in KiCad. The isolated work branch is `codex/complete-appliance-schematic`.
The original checkout and unrelated changes were preserved.

The remaining processor, boot storage, CPU power, Ethernet, isolated PoE,
modem power, M.2, SIM and USB isolation circuits are now captured. The engineering
capture passes full ERC at all severities, with **zero violations and no exclusions**.
It has no PCB layout and is not released for manufacturing or four-modem operation.

[Review PDF](review/2026-10-07/appliance.pdf) ·
[Native BOM inventory](review/2026-10-07/bom.csv) ·
[Validation report](review/2026-10-07/capture-report.json) ·
[Detailed completion and release holds](../docs/schematic-completion.md)

## Reproduce and inspect

Requires KiCad CLI 10.99 (the version used for native Altium reference import) and
Python 3. Run without `python -O`; the checker uses assertions.

```sh
python3 hardware/tools/build_capture.py
python3 hardware/check.py --output /tmp/sierra-appliance-check
python3 hardware/tools/review_modem_power.py --output /tmp/modem-power-analysis.json
python3 hardware/tools/export_appliance.py --output /tmp/sierra-appliance-review
```

The checker validates the native netlist and all-severity ERC; all 565 RK3566,
200 RAM, 153 eMMC and other major-device contacts are accounted for. It checks
65 manufacturer DDR pair mappings, the complete retained TI bridge/flyback net
partitions, critical rail/reset/interface connections, four assembly-profile power
maps, deterministic identities and exact pad-number parity for all 657 assigned
footprints. Pad parity establishes identity, not a fabrication land-pattern review.
Temporary 3D-model references were removed from imported appliance footprints;
their mechanical models remain unqualified.

The PDF was rendered and all 30 sheets inspected. Cropped modem content, a duplicate
crystal-ground wire and the recovery USB shell-pad model were corrected during review.

## Assembly and software obligations

The default is the Quectel stuffing pattern. R2011/R2012/R2013/R2016/R2017 and
C2036/C2037/C2038 are DNP. Sierra USB profiles require all eight populated after
exact module review. Never energize Quectel contacts 24, 38 or 68. The native
[profile file](reference/modem-assembly-profiles.json) is machine-checked; all four
profiles have `released: false`. This is assembly selection, not hot interchange.

The independent STM32 must keep main, modem and NIC loads off until an isolated
Class 6 grant is stable (TPH_N/TPL_N/BT_N = 0/1/0), and cut loads on loss of grant.
It controls power, reset and recovery while Linux runs the packet path. Firmware
for those policies and real recovery/traffic behavior still need qualification.
The no-detect SIM socket permits card changes only with modem power off.

Modem USB isolation is powered from the always-on rail. Hardware enables data
only with valid host power and modem power delayed by 180–420 ms. A latched eFuse,
independent monitor and explicit discharge support recovery; measured rail fall,
USB isolation, off-time and per-model timing remain required.

## Release holds

- Six intentionally unassigned footprints: U701 TPS56837 RPA, U801 RK3566,
  U901 Micron RAM, T1701 HX4110NLT, J1701 RJE491881401 and J2001 MDT420B01411.
  Exact land patterns, copper/mask/paste, orientation and retention need review.
  The existing RK/RAM candidates have audited ball centers, not approved lands.
- Current controlled EM919x and EM92xx technical specifications and the RM551E-GL
  production hardware guide remain unavailable. Older manufacturer guides and the
  RM520N V1.0 guide support provisional capture. Current pin/timing differences,
  exact firmware/composition and power envelopes must be closed per module.
- 5 A modem current is a provisional burst allocation. Connector hot derating,
  voltage drop, regulator stability/current, PoE startup/MPS/allocation, thermal,
  isolation/creepage, SI/EMC and RF operation require physical testing. HV MLCCs
  across isolation are not a certified safety-barrier assembly.
- CPU DVS/kernel/DDR training/eMMC/NIC drivers and unique Ethernet MAC provisioning
  require an actual software image and boot/traffic/recovery tests.

Sources, revisions and hashes are saved in [reference/sources.json](reference/sources.json).
TI's source archive retains its notices; imported symbols and footprints are derived
from TIDA-050023. The topology comparison excludes deleted evaluation headers,
auxiliary input and the old 1 GbE transformer. The new capture requests Class 6,
extracts all four PoE pairs with 2.5 GbE magnetics, and isolates allocation status.
