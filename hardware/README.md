# Appliance schematic

The complete engineering capture is [appliance.kicad_sch](appliance.kicad_sch), with
33 sheets, 818 components and 856 native nets. Open [appliance.kicad_pro](appliance.kicad_pro)
in KiCad. [appliance.kicad_pcb](appliance.kicad_pcb) contains all 818 footprints
with native schematic links; placement and routing are still pending.

The remaining processor, boot storage, CPU power, Ethernet, isolated PoE,
modem power, M.2, SIM and USB isolation circuits are now captured. The engineering
capture passes full ERC at all severities, with **zero violations and no exclusions**.
Current CLI schematic/PCB parity is clean. The October 7 bidirectional native
update-dialog checks reported zero errors/warnings and no proposed changes. This is not a manufacturing or four-modem release.

[Review PDF](review/2026-10-07/appliance.pdf) ·
[Native BOM inventory](review/2026-10-07/bom.csv) ·
[Validation report](review/2026-10-07/capture-report.json) ·
[Footprint and model audit](../docs/footprint-audit.md) ·
[Detailed completion and release holds](../docs/schematic-completion.md)

## Reproduce and inspect

Requires KiCad CLI 10.99 (the version used for native Altium reference import) and
Python 3. Run without `python -O`; the checker uses assertions.

```sh
python3 hardware/check.py --output /tmp/sierra-appliance-check
python3 hardware/tools/check_board_sync.py --output /tmp/sierra-board-check
python3 hardware/tools/review_modem_power.py --output /tmp/modem-power-analysis.json
python3 hardware/tools/export_appliance.py --output /tmp/sierra-appliance-review
```

The checker validates the native netlist and all-severity ERC; all 565 RK3566,
200 RAM, 153 eMMC and other major-device contacts are accounted for. It checks
65 manufacturer DDR pair mappings, the complete retained TI bridge/flyback net
partitions, critical rail/reset/interface connections, four assembly-profile power
maps, deterministic identities and exact pad-number parity for all 818 assigned
footprints. Pad parity establishes identity, not a fabrication land-pattern review.
791 components use default KiCad footprints, including 521 stock hand-solder
variants. Existing package sizes are retained. All attached model paths resolve;
missing or mechanically unverified models are explicitly recorded in
[footprint-policy.json](footprint-policy.json). Imported TI embedded STEP assets
are now stored in the project.

The [BGA/model follow-up](../docs/bga-model-review-2026-10-21.md) records six new
package-envelope models covering 16 components, all 18 remaining missing-model
holds, and measured mask/stencil limits for the two unreleased BGAs. The full
checker validates model source hashes, attachment rotations and these holds;
`tools/check_model_reviews.py --geometry` additionally checks the six STEP solids
and sourced bounds with CadQuery.

The [2026-11-21 model follow-up](reference/model-reviews-2026-11-21.json) closes 11
more holds with `tools/build_models.py`: the archived Amphenol M.2 STEP attached
with a measured datum transform, the TI-embedded PowerDI-5 STEP re-oriented to its
lands, and nine envelopes (nominal XY, maximum height, drawing terminals) for U1301,
U701, U2002, U1902, U1901, U1001, L401, Y1101 and U1101. Every envelope terminal is
cross-checked against its footprint copper. Remaining holds stay in the policy.
Every generated model is a single flat, coloured STEP product with its datum transform
baked in and attaches with a zero transform, so KiCad and Backplane's 3D tab agree.

Use the native Update PCB / Update Schematic dialogs for normal edits, with
reference relinking off. `build_capture.py` regenerates the original capture and
applies the footprint policy; it overwrites manual schematic graphics. Preserve
editor changes before regeneration. `sync_board.py` is only an unrouted-board
refresh helper and refuses routed boards.

The PDF was rendered and all 30 sheets inspected. Cropped modem content, a duplicate
crystal-ground wire and the recovery USB shell-pad model were corrected during review.

## Bring-up additions — 2026-11-22

Four sheets from [tools/build_management.py](tools/build_management.py), plus native label edits on the
supervisor, processor, modem-socket, flyback, PMIC and 3.3 V sheets:

- **SoC <-> STM32 UART.** RK3566 UART3_M0 (A22 RX, B22 TX, VCCIO1 = 3V3_MAIN) to STM32 LPUART2
  (PC7 RX, PC6 TX) through two LVC1G125 buffers, each powered by its receiving side so neither
  back-powers the other. Carries telemetry, LED overrides, power-cycle requests and reset cause.
- **Status LEDs.** PWR/SYS/WAN (green) and FAULT (yellow) sink into STM32 PA8/PA15/PD0/PD1, all
  timer-PWM pins. They are dark from MCU reset until firmware drives them; Linux overrides over the UART.
- **Sensing on the STM32 ADC.** To free seven ADC inputs, seven digital signals moved to spare GPIOs
  ([assignment table](pinmaps/supervisor-appliance-assignment.csv)). PA0 AUX_12V/11, PA1 5V_MAIN/2,
  PA4 3V3_MAIN/2, PA5 MODEM_VCC/2, PA6 modem current from the TPS25947 ILM pin (R2213 must sit at U1902
  pin 9: the pin tolerates < 50 pF), PA7/PB2 10k NTCs at the M.2 bay and the flyback secondary.
  INA226 (I2C1 PB8/PB9, 0x40, alert on PC14) measures the whole 12 V bus through a 10 mOhm shunt.
- **Aux 12 V input.** J2101 (ED555) feeds ISO_12V_BUS through an LM74700 + CSD17577Q5A ideal diode; the
  flyback output (now `ISO_12V_PSU`) gets its own. `ISO_12V` is the monitored bus after the shunt.
  **Firmware:** aux power gives no PoE grant (TPH_N/TPL_N/BT_N all high). Bypass the grant gate only while
  ADC_AUX_12V reads above 10.5 V, and re-apply it as soon as aux drops. Aux is 12 V nominal, 12.6 V max.
- **Boot media.** 1.8 V SPI NOR W25Q128JWEIQ on FSPI CS0/CLK/D0/D1/D3 (D2 shares 1B16 with EMMC_RESET_N,
  so x1/x2 only); the WSON-8 8x6 land also takes W25N01GWZEIG SPI NAND. DNP microSD on SDMMC0
  (VCCIO_SD) with a TPS22965 card switch on GPIO0_A6 (SD_PWR_EN) and SDMMC0_DET card detect.
- **eSIM.** DNP MFF2 land on M.2 SIM2 contacts 42/44/46/48 through DNP 0R links, so every modem profile
  keeps those contacts open by default. The land is a placeholder pending a chosen eUICC drawing.
- **Test pads.** 80 bare 1.0 mm pads (TP2401-TP2480): 44 resets/enables/power-goods, 26 rails, 10 GND.
  PMIC_PWRON_N and MAIN3V3_EN became global nets for this. MCU_NRST_N/SWD stay on J201 and the
  service UART/modem controls on J102.

Board: placed incrementally with `place_board.py --keep` after `sync_board.py`, which now keeps existing
footprints byte-for-byte except changed pad nets. The top side had no room for 20 new parts, so they
fell back to the bottom: the aux power path and INA226 under the flyback secondary, and the SPI flash
under the SoC. J2101 is a bottom-side through-hole terminal block. The DNP microSD group is on the bottom
by design, under the M.2 card with the card opening at the right edge. DRC adds no shorts, bridges or courtyard overlaps; the six new clearance
findings are pad-to-pad inside U2103's 0.5 mm MSOP. `check_board_sync.py` still stops on six
`lib_footprint_mismatch` findings (J101, J102, J201, J202, J1202, J1701) that were already present at
the previous commit.

Open before order: SPI flash and SMBJ12CA LCSC stock; RK3566 FSPI boot behavior with a blank or
present NOR; the MFF2 land against a real eUICC drawing; microSD trace length (about 80 mm, fine for
SDR25, marginal for SDR104); the WSON-8 8x6 STEP model hold.

## PoE stage: TPS23730 / PMP22477 — 2026-11-22

The TPS2373-3 PD and the LM5155 / TL431 / opto flyback (TIDA-050023, 88 parts on two sheets) are
replaced by TI's TPS23730 PD + primary-side-regulated flyback from reference design PMP22477
(63 parts on one sheet, `poe-flyback`), per [the evaluation](../docs/poe-tps23730-evaluation.md).
[tools/build_poe_tps23730.py](tools/build_poe_tps23730.py) captures it from TI's native Altium
project (`reference/pmp22477-cad.zip`, Rev C sheet 2, imported to `reference/pmp22477-import/`).
`check_appliance_capture.py` proves the captured net partition against that import, the same way
the TIDA input bridge is still proven.

- Kept: our TIDA active input bridge (`poe-input`, option B in the evaluation, about 1 W better than
  PMP's Schottky bridge) and the three TLP293 grant optos. Grant decoding stays parallel: R65
  (SCDIS to VSS, serial mode) is left out, so firmware still enforces TPH_N/TPL_N/BT_N = 0/1/0.
  TPH/TPL optos now pull up from TPS23730 VCC (`POE_VCC`); the BT opto hangs off VB (`POE_VB`)
  through R1803 = 2.2 kOhm, because the BT pin is rated 6.5 V absolute maximum.
- Dropped from PMP sheet 2: the adapter input path (D10, L4–L6, C15, C19, C20, J10–J12), output and
  jumper terminals (J13, J14), the setpoint-shift circuit (U11, Q5, R54, R56, R57, R62), the input TVS
  D13 (D1705 on the bridge already clamps), and the whole power-limit sheet 3. The 0 Ohm straps
  R48/R49/R52/R55/R59/R60/R73 became direct ties; PPD is tied to VSS. R58 stays: it is the PSR
  feedback divider's bottom resistor, not part of the setpoint shift.
- Added: R1775, 470 Ohm 1 W preload on `ISO_12V_PSU`. The PSR output rises to about 15.7 V with no
  load (TIDT259); the preload holds about 13.4 V in standby. The `ISO_12V` normal maximum is now
  14 V (was 13.2 V); TPS54620 keeps 3.6 V margin to its 17 V limit.
- Passives use the board's standard MPNs where the spec is the same or better; the TPS23730
  (RMT0045A), LDT9055-51R transformer, FSV1060V (TO-277A) and the 47 uF can use TI's land patterns
  from the PMP22477 PCB (`PoE.pretty/TI_*`). The RMT0045A and radial-G lands have no STEP (model holds).

**Firmware:** with PSR the flyback droops with load, so with aux present the PoE share is set by the
two curves, not by the grant. Never run loads on aux while PoE is present with a grant other than
0/1/0 (PMP22477's power limiter, which handled this, is not fitted).

**Release holds:** LDT9055-51R (and its alternates Würth 750320319, Sumida PS21-212) had no
distributor stock on 2026-11-22: get a quote and samples before ordering. Confirm its isolation
rating against 802.3 / IEC 62368-1. Bench: light-load and no-load VOUT with the preload, load release
at the TPS54620 input, grant timing on a real Type 3 PSE, droop sharing with aux. The flyback layout
from 997fb5e/cff4aee is gone; the new stage is placed by `place_board.py --keep` and needs a
hand-layout pass (rectifier loop, output caps currently partly on the bottom).

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

- Two BGA PCB land/mask/paste process holds remain: U801 RK3566 and U901 Micron RAM.
  The [October 21 review](../docs/footprint-review-2026-10-21.md) closes the other four
  drawing geometry holds and records the corrected native geometry.
  Exact land patterns, copper/mask/paste, orientation and retention need review.
  RK/RAM retain the audited ball centers; connector lands follow archived vendor
  drawings. The detailed audit records mask, stencil and mechanical limitations.
- The staged board has no routing or outline. All-severity physical DRC remains
  open; the native synchronization check reports the actual counts without
  suppressing rules. Do not export it for fabrication.
- [Current modem access and order-code gates](../docs/modem-documentation.md) remain open.
  RM520N Series V1.4 is login-gated; the archived V1.0 remains provisional.
  Current controlled EM919x and EM92xx technical specifications and the RM551E-GL
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
TI's source archives retain their notices. The active input bridge is derived from TIDA-050023 (its
golden check excludes the deleted evaluation headers, auxiliary input and old 1 GbE transformer). The
PD and flyback come from PMP22477 (below). The capture requests Class 6, extracts all four PoE pairs
with 2.5 GbE magnetics, and isolates allocation status.
