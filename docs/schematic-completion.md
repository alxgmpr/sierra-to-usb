# Complete appliance schematic — in progress

Authorized 2026-10-03. Work branch: `codex/complete-appliance-schematic`.
The original dirty checkout was copied to the isolated worktree without changing
its files. Prior recovery circuitry is retained. No procurement or fabrication.

## Scope and completion evidence

| Required block | Current authoritative state | Required before schematic completion |
|---|---|---|
| Recovery MCU, watchdog, SWD and reset outputs | 26-component recovery circuitry in four-sheet, 32-component supply-integrated capture; native connectivity verified; standalone recovery ERC now reports boundary labels for appliance-only signals | MCU pin audit closure; physical startup/reset behavior; target-domain interface integration |
| Independent always-on supply | `hardware/always-on.kicad_sch`, 6 components, TPS62177DQCR, LPS4018-103MRC; integrated recovery hierarchy and PG fault net; typical capacitor bias reviewed | Guaranteed capacitor corners/aging and loop behavior; rail load; complete appliance hierarchy |
| RK3566 / DDR / PMIC | RK809-5 registered 69-pin symbol; 56-component PMIC draft with native captured-net checks; 565-ball RK3566 table awaits user review | Complete PMIC capture/sequence/thermal budget; exact supported RAM and training route; processor symbol approval and complete capture/decoupling/clocks |
| Main 5 V and 3.3 V supplies | Native 15-part TPS56837 main 5 V draft and 13-part MP2143 3.3 V draft; MCU enable/PG and shared ISO_12V captured | TPS56837 footprint approval, combined capacitor/compensation and startup/current/thermal budget closure; reviewed interface states |
| External CPU supply | Missing; NanoPi reference uses I²C-controlled TCS4525 | Exact programmable regulator, boot voltage/OPP/driver compatibility, RK809 EXT_EN sequence, input/output bank and complete capture |
| Boot storage and recovery | 16 GB native-mode A/B sizing proposal; Kingston exact candidate has lifecycle hold; storage not selected | Capacity budget, exact eMMC, SD/USB recovery circuit and boot strap audit |
| 2.5GbE | RTL8125BG-CG remains candidate | Exact pin/reference circuit, clocks/rails/reset/PCIe coupling and 2.5G PoE-rated magnetics; symbol and footprint checks |
| Isolated PoE | Archived TI TIDA-050023 schematic and BOM as candidate reference | Whole-appliance peak and startup budget, exact class, transformer/protection/feedback/MPS/allocation integration; isolation boundary audit |
| Modem power | Requirements only | Voltage/current envelope per model, switch/eFuse/ramp/discharge, default-off controls and fault sensing |
| EM9190 / EM9293 sockets and SIM | Older manufacturer PTS research; contacts 24/38/68 conflict with Quectel | Current controlled pin tables, complete per-model profile and power/control/SIM/USB3 capture |
| RM520N-GL / RM551E-GL sockets and SIM | RM520 guide exists; current RM551 production guide still missing | Current controlled hardware guides and per-model pin/voltage/control/SIM/USB3 capture |
| Full hierarchy and BOM | Draft appliance root exports 116 annotated components; major subsystem sheets remain absent | One integrated appliance root; exact MPN/manufacturer/footprint for every fitted component; BOM exported from native netlist |
| Visual and electrical review | Always-on draft rendered and corrected; recovery tests rerun | All sheets and circuit crops inspected, native ERC and complete critical-net assertions, manufacturer pin fidelity, footprint pad parity |

No PCB file exists. Do not start placement until the integrated schematic and
exact parts meet the criteria above. Physical throughput, thermal/EMC/isolation,
power interruption and unattended recovery remain separate qualification work.

## Current verification snapshot — 2026-10-04

Appliance capture checker exports the native XML and verifies 116 components,
recovery/main rail separation, PMIC restart, main 5 V enable/PG, bootstrap,
soft start, input bypass and output-filter connectivity. It is not a full-appliance
checker. The last full ERC run reported 25 violations: 16 unconnected pins,
4 undriven signal pins and 5 undriven power pins. No exclusions added.
The processor, RAM, storage, Ethernet, PoE and modem circuits are still absent.

The dated sections below preserve intermediate research and capture decisions;
older component counts, ERC claims and unconnected-interface descriptions are
superseded by this snapshot and the current native files. Physical verification
remains separate from schematic capture and is not implied by netlist checks.

## Always-on circuit decisions

Input is the **isolated nominal 12 V intermediate rail**, not raw PoE.
TPS62177 has 4.75–28 V operating input and fixed 3.3 V / 0.5 A output.
EN is connected to the isolated input; SLEEP to output for normal operation.
FB and NC are grounded as recommended; exposed pad, AGND and PGND connect to
local ground. VOS senses after the 10 uH inductor. PG has a 100 kR pull-up
and is not yet wired to the MCU. No downstream power enable gates this supply.

TI SLVSB35C Table 2 recommends the nominal 10 uH / 22 uF combination, assuming
approximately 20 percent component variation. The two capacitor MPNs are
**provisional until DC-bias curves establish effective capacitance**:
CL31B225KBHNNNE (2.2 uF, 50 V, X7R, 1206) and CL32B226KAJNNNE (22 uF,
25 V, X7R, 1210). Manufacturer pages identify both as mass-production products.
The originally researched Murata input capacitor was rejected after an obsolete
lifecycle indication; it is not captured.

Coilcraft LPS4018-103MRC is the current packaging variant of a TI-listed family.
Manufacturer data: 10 uH ±20 percent, 0.2 ohm maximum DCR, saturation current
1.1/1.2/1.3 A at 10/20/30 percent inductance drop; RMS 0.9/1.25 A at 20/40 C
rise. Do not use the catalog's 1.3 A number as a no-drop rating. Worst-case
switch current limit can reach 1.2 A. Transient margin and inductance at that
current still require review; this is a draft selection, not a released BOM.

Sources:
- [TI TPS6217x datasheet](https://www.ti.com/lit/ds/symlink/tps62175.pdf), pin table and application section.
- [Coilcraft LPS4018 datasheet](https://www.coilcraft.com/getmedia/31b05c96-4c4c-4498-8dbb-fe092de76bad/lps4018.pdf).
- [Samsung input capacitor](https://product.samsungsem.com/mlcc/CL31B225KBHNNN.do).
- [Samsung output capacitor](https://product.samsungsem.com/mlcc/CL32B226KAJNNN.do).
- [FriendlyElec NanoPi R3S LTS reference](https://wiki.friendlyelec.com/wiki/images/f/fd/NanoPi_R3S_LTS_2411_SCH.pdf).
- [TI TIDA-050023](https://www.ti.com/tool/TIDA-050023). Its reference Ethernet magnetics must not be inherited as a 2.5G-qualified part.

Archived PDFs and SHA-256 provenance live in `hardware/reference/sources.json`.
Catalog stock observed via PCBParts on 2026-10-03 is not reserved inventory or a
production quote. The schematic is the BOM source; do not edit exported BOMs.

## Reproduce current checks

```sh
python3 hardware/check.py --output /tmp/sierra-recovery-check
python3 hardware/check_always_on.py --output /tmp/sierra-aon-check
```

The always-on checker validates native ERC of the recovery hierarchy,
exact supply-component membership of every supply net and five-component inventory, then exports SVG/PDF and BOM. It does not
verify DC bias, load margin, system integration or physical operation.
`hardware/tools/build_always_on.py` reconstructs only the new always-on draft;
it does not touch the preserved recovery sheets. Do not rerun it over manual
edits without preserving those edits first.

## 2026-10-03 processor and recovery progress

`hardware/pinmaps/rk3566.csv` preserves all 565 unique package ball names from
Rockchip datasheet Rev 1.2, pages 24–30, including wrapped mux names. The
reproducible extractor verifies the saved table against the PDF; this is not
yet a symbol, and it does not claim electrical pin types or unused-pin policy.
The KiCad symbol skill requires user review before the PDF-derived table is
used to generate a new processor symbol. That review is pending.

All eleven recovery resistors now have exact Yageo MPN, manufacturer, LCSC,
1 percent tolerance, 0.1 W rating and 75 V rating fields in the schematic.
At 3.3 V the worst full-rail dissipation is about 1.1 mW for a 10 kR part, well
below 0.1 W. Their operational leakage/default-state margins remain target
interface checks. The four headers are now Wuerth 61300211121 (J101/J202),
61300611121 (J201), and 61301011121 (J102). J202's native schematic field requires
the 60900213421 mating RUN shunt. Header pitch, height and recommended holes
were reviewed against the manufacturer drawings. The original generic KiCad
footprint holes were 1.00 mm; local variants use the recommended 1.10 mm
drill while retaining the original 1.70 mm pads and 2.54 mm pitch.

The local variants retain the official KiCad equivalent-envelope STEP models,
packaged locally under `hardware/Recovery.3dshapes`; these are not vendor-exact
models. Native footprint SVGs were rendered and inspected. Official library
tools KLC checks pass with the F9.3 official-library-path rule excluded because
this project deliberately uses `${KIPRJMOD}` local model paths. No geometry
rule is excluded. Full board-level 3D/mechanical review remains pending.

The recovery circuitry has 26/26 fitted components; its integrated supply adds five, giving 31/31 in the recovery hierarchy with exact MPN fields.
C203 is now CL31B106KAHNNNE (10 uF, 25 V, X7R, 1206), replacing
the provisional 4.7 uF / 0805 selection. Published typical loss at 3.6 V
is 15.26 percent. Combining that curve with -10 percent initial tolerance
and -15 percent X7R temperature change gives about 6.48 uF, providing
margin above ST's nominal 4.7 uF decoupling recommendation. This estimate
is not guaranteed combined-corner data and excludes aging; qualification
remains open. C201/C202/C204/C205 are now
Samsung CL10B104KA8NNNC, 100 nF, 25 V, X7R, +/-10 percent, 0603.
Published typical 25 C DC-bias data show +0.94 percent at 3.3 V and
+0.83 percent at 3.6 V; this is not guaranteed corner performance. SW201 is now E-Switch TL3342F160QG.
Its current P010632 Rev J drawing specifies 1.70 x 1.00 mm pads centered at
x = +/-3.15 mm and y = +/-1.90 mm, matching the installed KiCad footprint.
Each horizontal pair is internally common; the two rows are switched, matching
the footprint duplicate pad numbers. The rated 12 V / 50 mA exceeds the
3.3 V reset pull-up load. The switch limits ambient operation to -20 to +70 C;
whole-appliance temperature qualification remains open. The native checker
now exports the BOM and reports missing MPNs, so ERC cannot be mistaken for
parts-completion evidence. The complete appliance BOM is still absent.

The manufacturer RK3566 guide adds constraints that must carry into capture:
- 24 MHz crystal circuit requires its 22 R output resistor and 1 MR feedback;
  load capacitors depend on the selected crystal rather than a copied value.
- Reset pull-up must match PMUIO1; retain 100 nF at the reset input.
- VCCIO2 and FLASH_VOL_SEL must agree at reset (high for 1.8 V, low for 3.3 V).
- Keep USB OTG0 available for ROM recovery; use USB2 PHY1 with USB3 HOST1.
- PCIe clock-request and wake use actual function pins with the same MUX group;
  TX needs 100 nF coupling at the source and RX coupling belongs at the endpoint.
- RK809 RTC input must be supplied first and at the highest input potential;
  BUCK1/2 output capacitance must exceed 30 uF as specified by the guide.

Official Rockchip rkbin provides RK3566 DDR training binaries, but availability
is not proof of training with a selected RAM. Catalog searches returned costly,
low-stock Micron parts; those are research candidates, not substitutions for a
compatible, economical RAM selection. Exact RAM and eMMC remain open.

## Archived capacitor bias data

Samsung characteristic arrays are saved with source hashes in `hardware/reference`.
At 25 C, CL31B225KBHNNN loses 13.11 percent at 12 V and 15.40 percent
at 13.2 V. Its nominal 2.2 uF becomes about 1.91 uF typical at 12 V,
or 1.72 uF including -10 percent initial tolerance before temperature/aging.
CL32B226KAJNNN loses 7.33 percent at 3.3 V: 22 uF becomes about 20.39 uF
typical, or 18.35 uF including -10 percent initial tolerance before temperature/aging.
These data support the margin review but do not establish guaranteed minimum
capacitance across temperature, aging and bias. The supply selections stay provisional.

ST DS13560 Rev 6 specifies local 100 nF plus 4.7 uF supply decoupling;
[manufacturer datasheet](https://www.st.com/resource/en/datasheet/stm32g0b1kc.pdf).
NRST Table 60 requires low <=0.3 x VDDIO1 and high >=0.7 x VDDIO1,
with an internal 25-55 kR pull-up. Those limits must be used in the
watchdog/diode reset margin audit, including startup rail conditions.

## MCU reset low-margin audit

Native nets place D201 anode on MCU_NRST_N and cathode on WDT_RESET_N.
R201 pulls MCU_NRST_N to the same 3.3 V rail through 10 kR +/-1 percent;
ST DS13560 Rev 6 Table 60 adds an internal 25-55 kR pull-up. At the
MCU's 3.6 V supply maximum, total pull-up current is bounded by
3.6 / 9900 + 3.6 / 25000 = 0.508 mA (assuming reset is at ground).
This is below TI's 1.2 mA reset-output test load and Diodes' 1 mA VF point.

TI TPS3823-33 maximum VOL is 0.4 V at VDD = VIT- - 0.2 V. BAT54WS
maximum VF is 0.32 V at 1 mA and 25 C. Using those tabulated points
and monotonic forward conduction gives a 0.72 V reset-low bound at 25 C.
TI's minimum VIT- over -40 to +85 C is 2.86 V, so its lowest specified
VOL test supply is 2.66 V. ST's VIL limit there is 0.3 x 2.66 = 0.798 V:
78 mV margin at that test point, and 270 mV at nominal 3.3 V.

This is a bounded 25 C calculation, not a guarantee over the appliance's
temperature range or the entire supply ramp. The diode VF table is explicitly
at 25 C; below the watchdog VOL test supply, a comparable 1.2 mA bound
is not provided. TI's 0.9 V power-up reset point uses only 20 uA, while
the external plus internal pull-ups can exceed that load. Startup reset
behavior and cold-temperature VF therefore remain qualification gaps.
A direct open-drain supervisor interface may remove the series-diode drop,
but any replacement must preserve watchdog timing and manual-reset behavior.

## Reset-interface correction selected for next capture

TPS3828-33DBVR (TI, LCSC C20032) now replaces TPS3823-33DBVR.
D201 is removed; open-drain RESET connects directly to MCU_NRST_N.
Retain R201 and C205, the existing WDI RUN shunt/pulldown, and MR button.
This change is applied to the native schematic. Native ERC and direct-reset
connectivity assertions pass; the BOM contains 26/26 exact MPNs.

TI SLVS165O Rev O (March 2025), Device Comparison Table and Table 5-1:
TPS3828 retains WDI and MR, 200 ms nominal reset delay and 1.6 s nominal
watchdog timeout, and uses the same DBV pin map as TPS3823
(RESET 1, GND 2, MR 3, WDI 4, VDD 5). Its RESET output is open-drain,
so an external programmer can assert reset without fighting a high output.
Removing the series diode improves the tabulated reset-low bound from
0.72 V to 0.40 V at the specified TI test supply, increasing the
2.66 V test-point margin from 78 mV to 398 mV. The shared datasheet
power-up 20 uA condition still leaves a supply-ramp qualification gap;
this replacement must not be described as proving all startup behavior.

PCBParts catalog snapshot on 2026-10-03: C20032, SOT-23-5, 65,899
listed stock, $0.3713 single-unit indicative price. Stock is not reserved.
Installed KiCad Power_Supervisor library has no TPS3828 symbol; capture
uses a local open-drain variant of the existing pin-compatible
TPS3823 symbol rather than keeping its push-pull electrical type.
After capture, update critical-net assertions to require U202:1 directly
on MCU_NRST_N, exclude D201 from inventory, rerun ERC and inspect the
reset circuit render before updating the authoritative BOM status.

The always-on supply is now page 4 of `recovery.kicad_sch`. Native netlist
proves L401 output, U401 sense/SLEEP, output capacitor and PG pull-up
share +3V3 with the MCU and watchdog. Native ERC and supply/reset/control
assertions pass for 31 fitted components. ISO_12V remains a named external
input, not captured PoE; PG now connects through the sheet interface to MCU POWER_FAULT_N
and J102:9, with its 100 kR pull-up on the converter output. External
fault sources on J102:9 must be open-drain and compatible with 3.3 V. J101 remains a rail test/header boundary: do not connect a second
3.3 V source while the converter is active. This is recovery integration,
not the full appliance hierarchy.

Power-good integration checks require exactly U401:7, R401:2, U201:20
and J102:9 on POWER_FAULT_N. A low signifies at least one fault; firmware
must not infer which source asserted it. The separate supply checker now
uses the native integrated root, because its output is a real hierarchical
interface. It filters supply pins when checking shared power/ground nets;
`hardware/check.py` verifies MCU/watchdog rail membership and fault loads.

## Input capacitor margin correction

C401 now uses CL31B475KBHNNNE (4.7 uF, 50 V, X7R, 1206, C51205),
replacing the 2.2 uF part without changing footprint or connectivity.
Samsung typical loss is 24.16 percent at 12 V and 27.36 percent at 13.2 V.
Combining the 13.2 V curve with -10 percent tolerance and -15 percent
temperature allowance gives about 2.61 uF before aging, above the
reference's nominal 2.2 uF. The 13.2 V assumption corresponds to a
12 V +/-10 percent intermediate rail; final PoE regulation/transient limits
must confirm that envelope. This remains typical-data engineering margin,
not a guaranteed combined-corner minimum.

TI Table 2 explicitly permits 10 uH with nominal 22, 47, 100 or 200 uF,
assuming typical +/-20 percent variation. Output capacitor temperature/bias
margin may therefore be improved by moving toward the supported 47 uF
combination; current single 22 uF output selection remains provisional.

## Parallel output bank captured

C402/C403 are each CL32B226KAJNNNE, 22 uF / 25 V X7R 1210.
The output bank is now 44 uF nominal. At 3.6 V Samsung typical loss
is 9.60 percent: about 39.78 uF before tolerance and temperature, or
30.43 uF with -10 percent tolerance and -15 percent temperature allowance.
This improves absolute capacitance margin relative to the original single
22 uF part. Nominal 44 uF is near TI's supported 47 uF / 10 uH option,
but the combined low estimate falls below its assumed -20 percent range.
Loop stability and aging therefore remain open; this is not a claim of
guaranteed all-corner compliance with Table 2. Native ERC, supply net
membership, direct reset and fault net assertions pass with 32 fitted
components, all carrying exact MPNs. Prior 31-component figures describe
the earlier single-output-capacitor revision.

## PMIC reference identification

NanoPi R3S LTS 2411 power overview names **RK809-5**, but the actual
U2100 multi-unit symbols name **RK809A-5**. This naming discrepancy
must be resolved before freezing the orderable PMIC.
Page 3 assigns BUCK1/2 to logic/GPU (0.9 V defaults, slots 1/2),
BUCK3 to adjustable DDR (slot 3), BUCK5 to 1.8 V (slot 2), LDO2/3
to 0.9 V analog/PMU (slot 1), LDO6/7/8 to 3.3 V PMU and 1.8 V
analog/PMU (slot 2). SW1/SW2 supply 3.3 V system/SD in slot 4.
RESETn releases at slot 4+5. Two external 3 A buck circuits generate
3.3 V and 5 V system rails from 12 V before the PMIC sequence.
These are reference assignments, not yet this appliance's captured rails.
Do not use the independent 0.5 A recovery converter as the RK809 input.
Exact orderable suffix availability and manufacturer programming defaults
still require confirmation before committing native PMIC capture.

Updated supply and root renders were inspected. Root sheet placement
was moved above the control-header labels to remove an overlap. J101
now reads RAIL TEST rather than EVAL SUPPLY; its back-power warning
and root scope notes match the integrated supply. ERC/net assertions
pass after these drawing corrections.

## PMIC suffix evidence and sourcing

Rockchip-authored RK809 Rev 2.4 is archived with hash provenance from
its public mirror. Package ordering information lists RK809-5 and
RK809-5A separately; top markings also distinguish them. Table 4-8
for -5A gives the expected logic/GPU/DDR slots 1/2/3 and BUCK5 1.8 V
slot 2. LDO3 follows LDO2 by about 200 us; short PWRON press is 100 ms.
Do not assume the reference spelling RK809A-5 is an orderable alias for
RK809-5A without supplier/manufacturer confirmation.

PCBParts returns exact RK809-5 as C2939628, QFN-68-EP 7 x 7 mm,
1,521 listed stock and indicative $2.458 price on 2026-10-03. That
listing proves catalog availability of -5 only, not -5A equivalence or
startup compatibility. Selection remains pending suffix resolution.
The public distributor download initially returned HTML rather than PDF;
it was rejected and removed. Only the verified %PDF manufacturer-authored
Rev 2.4 file is recorded in the source manifest.

## PMIC selected independently of reference alias

Select **RK809-5 / C2939628** for this appliance. Rev 2.4 Tables 4-4
and 4-8 have identical listed default rail voltages and startup slots,
including the divider-defined BUCK3 in slot 3. Saved rail CSV records
Table 4-4 defaults for design review, not a symbol pin table. A text
comparison confirms the listed BUCK/LDO/SW/VB_OK rows match across
variants. Figures 4-2/4-3 distinguish timing: EXT_EN to conversion starts
after (4+N) ms for RK809-X, (12+N) ms for RK809-XA, where N is
preparation/charging time below 50 ms. VDC must be present for 140 ms,
and RESETB follows completion of the rail sequence by 2 ms.

The design will use the selected -5's documented timing rather than
claiming the reference's RK809A-5 is an alias. Capturing its pinout,
external components, reset/clock controls and rail load budgets remains
required; a compatible default table does not prove board qualification.
Earlier suffix-pending notes are superseded by this explicit selection.

## RK809 native-model candidate audit

PCBParts ComponentSearchEngine returned SamacSys model ID 21488395 for
exact RK809-5: 69 symbol pins (1-68 plus EPAD 69), QFN35P700X700X80-69N-D
footprint. Raw files are saved under `hardware/reference/rk809-5-cse-candidate.*`;
these are **not registered active project library parts**. The native
model uses an older Rev 1.01 datasheet URL. Against Rev 2.4 Table 2.7,
all 68 numbered pins match names except pin 42 MIC1N vs MICIN and
pin 43 MIC1P vs MICIP; descriptions identify the same negative/positive
microphone functions. EPAD 69 corresponds to manufacturer's exposed ground.
`hardware/pinmaps/rk809-cse-audit.csv` records every comparison.

All 69 supplied electrical types are passive, so the symbol cannot support
a meaningful power/input/output ERC review as supplied. Correct types and
functional grouping, current datasheet fields and native alternates must
be established before integration. The footprint has 0.35 mm lead pitch,
7 x 7 mm body, 5.59 mm exposed pad, one solid exposed-pad paste aperture
and a bare RK809-5.stp model reference without returned model data.
Its paste strategy, pad geometry, courtyard and model path still require
manufacturer/assembly review and official KiCad checks; catalog model
availability does not establish library qualification.

## PMIC electrical-type review draft

`hardware/reference/rk809-5-electrical-review.kicad_sym` adapts the native
CSE model for review, preserving all 69 existing pin numbers and geometry.
62 pins now have proposed input/output, bidirectional, power or open-drain
types based on their documented functions; seven analog/internal nodes
remain passive with explicit unresolved roles in
`hardware/pinmaps/rk809-electrical-review.csv`. Pin 18 displays SDO with
PDMDATA as a native input alternate instead of a slash-delimited name.
Reference prefix is U and datasheet points to Rev 2.4. KiCad's native
symbol exporter accepts the review library. This draft is not registered
in the active project, KLC-qualified, visually approved or integrated.
Its inherited physical-order pin layout still needs functional grouping,
and all electrical-type proposals require review before final capture.

A four-unit grouped PMIC review symbol is now saved under
`hardware/reference/rk809-5-grouped-review.kicad_sym`: buck/switch, LDO,
management/RTC, and audio units. All 69 audited native-model pins occur
exactly once across the units; native exporter recognizes four units.
Seven analog roles remain explicitly unresolved. This candidate still
needs visual/KLC review and footprint qualification before active capture.

Grouped PMIC renders were inspected; reference/value fields overlapped
top power pins in the first draft. They now sit at the upper left;
bodies are compacted and centered, pin offsets corrected and metadata
added. Official KiCad symbol checks exposed unresolved VREF electrical
type and the intentionally unassigned footprint, so KLC qualification
is still open. No rule exclusions are being treated as a release pass.
The manufacturer block diagram identifies VREF as an internal reference
node and the codec register identifies VCC_1P8A as an internal LDO
voltage; these support the remaining electrical-role review but do not
yet resolve every analog/switching node.

## PMIC footprint and reset-type progress

Official installed footprint candidate:
`Package_DFN_QFN:ArtInChip_QFN-68-1EP_7x7mm_P0.35mm_EP5.49x5.49mm_ThermalVias`.
Its 7 mm body, 0.35 mm pitch, 5.49 mm EP and 1-68 counterclockwise
numbering plus EP69 match Rockchip Rev 2.4 package dimensions. Lead
pads are 0.55 x 0.25 mm, centered 3.30 mm from origin, with 0.10 mm
adjacent copper gap. The EP is split into nine paste windows, and
includes 0.20 mm-drill thermal vias. Render inspected. This is an
equivalent-package candidate, not a vendor-specific assembly release;
via treatment, stencil and board thermal design remain open. Its
installed equivalent-envelope STEP model is referenced by the library.

Rev 2.4 page 27 explicitly lists CLK32K, RESETB, INT and SDA as
open-drain outputs. RESETB type is corrected to open_collector in the
grouped draft; SDA stays bidirectional to represent both I2C directions.
VREF is now proposed power_out from the internal reference generator;
its name triggers the KLC generic VREF-input heuristic, so that finding
requires a documented function-based review rather than blindly changing
it to an input. Six other analog roles remain unresolved. LRCLK/BCLK
are proposed bidirectional pending I2S-mode review. The active schematic
still does not contain this PMIC.

## PMIC symbol registered for circuit capture

`Recovery:RK809-5` is now registered in the project symbol library,
adapted from the native CSE model rather than generated from a new
PDF pin table. All 69 native-model numbers remain unique. Rev 2.4
Figure 1-2 returns the external buck3 output to VBUCK3 (power_in);
VCC_CPVSS is the generated negative headphone rail (power_out);
VCC_1P8A/D are internally generated bypassed rails (power_out).
CPP/CPN remain intentionally passive flying-capacitor terminals,
representing analog charge transfer without a fixed logic direction.
VREF is an internal-reference output, not an external reference input.
MICIN/MICIP display names now match the current pin table. These
electrical-role decisions supersede the six unresolved draft roles.
VREF still triggers the KLC name heuristic; its function-based exception
is documented here, not a blanket exclusion of electrical-type checking.
The registered symbol remains subject to final render and library checks
and does not constitute captured PMIC circuitry.

Registered PMIC symbol final four-unit renders inspected on 2026-10-03:
no text/pin overlap found. `python3 hardware/tools/check_pmic_symbol.py`
passes 69 unique pin inventory, current manufacturer names, unit count,
open-drain reset/interrupt/clock types, I2C direction, native alternate
and symbol-to-footprint numbered pad parity. Only CPP/CPN are passive.
Official KLC checks on the registered symbol leave the documented VREF
name heuristic; metadata description was corrected separately. Symbol
library version matches the installed checker schema. Recovery native
ERC and all critical net checks still pass after the library update
(32 components); PMIC circuitry remains uncaptured.

## PMIC headphone supply pin correction

Manufacturer Rev 2.4 Figure 1-1 (page 10) shows VCC_CPVDD (pin 38)
as the internal LDO_2V3 output, bypassed externally. Its registered symbol
type is now power_out rather than power_in, with an explicit audit assertion.
Do not connect this pin to an external 2.3 V source during capture.
This corrects the earlier candidate electrical-type proposal; no PMIC circuit
has yet been captured.

## PMIC input mapping from the actual reference circuit

`hardware/pinmaps/rk809-reference-inputs.csv` records the supply pins traced
on NanoPi R3S LTS 2411 sheet 14. VCC1/2/3/4 use its VCC5V0_SYS rail;
VCC5/6/7/8/9 and VCC_RTC use VCC3V3_SYS. The overview on sheet 2 lists
3.3 V for BUCK1-4 and conflicts with the actual circuit. Capture must follow
the reviewed circuit, with final input/load validation against RK809 limits.
The appliance names 5V_MAIN and 3V3_MAIN are distinct from recovery +3V3;
its 0.5 A always-on regulator cannot supply these processor rails.

This establishes a need for both main 5 V and main 3.3 V intermediate supplies
from isolated 12 V. Their startup order must satisfy the PMIC VCC_RTC/VCC9
requirement before enabling dependent rails. The reference mapping does not
prove appliance power budget, startup margin or load qualification.

Sheet 14 also explicitly describes unused codec handling. It grounds pins
14/15/16/17/19/44/40 and leaves 18/36/37/38/35/39/41/34/32/43/42 floating.
That is reference guidance to reconcile against the manufacturer hardware
requirements before capture; it is not permission to omit required internal
supply bypassing without that reconciliation. No audio function is required
for the cellular appliance.

## PMIC buck inductor selected for capture

Use Coilcraft XGL4020-471MEC (0.47 uH +/-20%, LCSC C5837785)
for the five PMIC buck channels, with standard KiCad footprint
`Inductor_SMD:L_Coilcraft_XxL4020`. Manufacturer drawing Document 1529-3
Rev 02/19/26 specifies two 0.98 x 3.4 mm lands at 2.37 mm center spacing;
the installed footprint has these exact dimensions. Body is 4.0 +/-0.3 mm,
height 2.10 mm maximum. Orient terminal-start marking to the quiet/output
side for the manufacturer's lowest-EMI guidance (not an electrical polarity).

Manufacturer Document 1529-1 gives 5.1 mOhm maximum DCR, 6.1/9.7/13.4 A
at 10/20/30 percent inductance drop, and 14.3/19.7 A RMS for 20/40 C rise
at 25 C. Catalog shorthand 13.4 A must not be mistaken for a no-drop rating.
At BUCK1/2 rated 2.5 A, 5.5 V maximum input, 2.25 MHz minimum switching
frequency and 0.376 uH initial minimum inductance, the maximum ideal CCM
ripple across any output voltage is Vin/(4*f*L) = 1.63 A peak-to-peak;
peak current is about 3.31 A before bias loss. Even applying 10 percent
inductance loss gives about 3.41 A peak, below the manufacturer's 6.1 A
10-percent-drop test point at 25 C. At 2.5 A, DC copper loss is about 32 mW
using maximum DCR; AC/core loss, hot saturation, fault current and actual
application temperature rise remain verification work. Manufacturer thermal
ratings are reference test conditions, not a board temperature guarantee.
The PMIC reference calls 0.47 uH/4 A for BUCK1/2/5 and /3 A for BUCK3/4;
this selection supplies current headroom at the expense of a larger 4 mm body.
Capacitor bank selection and complete buck capture remain open.

## Native PMIC capture begun

`hardware/pmic.kicad_sch` now contains all four units of U501 and complete
BUCK1/2 draft paths: 5V_MAIN inputs, separate input capacitors, selected
XGL4020-471MEC inductors, three CL32B226KAJNNNE 22 uF output capacitors
per channel, and explicit feedback-sense nets connected after each inductor.
These rails start at 0.9 V for the selected -5 variant. The 66 uF nominal bank
is provisional to provide margin for bias/tolerance/temperature/aging above
the hardware guide's >30 uF effective requirement; combined-corner and
loop-stability analysis remains required. Input capacitors also require their
5 V effective-capacitance check. This sheet is deliberately separate until
all PMIC channels and control requirements are resolved.

`python3 hardware/tools/check_pmic_capture.py` exports a native netlist and
verifies exact membership of the six captured nets and MPN coverage for its
11 fitted components. It does not claim full ERC: the remaining 63 PMIC pins
are deliberately unwired. All 69 pins remain in the four-unit native symbol.
The recovery hierarchy retains its independent 32-component checks.
Rendered draft inspected and corrected overlapping input labels and codec
unit/title-block overlap. `hardware/tools/build_pmic.py` reproduces this draft;
preserve manual changes before regeneration. Kelvin sense routes to processor
loads, placement and ground returns remain PCB-stage requirements.

## Captured PMIC capacitor bank margin

`python3 hardware/tools/review_pmic_capacitance.py` interpolates the archived
Samsung CL32B226KAJNNN typical 25 C DC-bias curve. With -10 percent initial
and -15 percent X7R temperature factors, and no credit for positive bias
change, the captured three-capacitor 66 uF bank estimates 50.49 uF at 0.9 V
and 49.86 uF at the PMIC's highest programmable 2.4 V output, before aging.
The latter allows about 39.8 percent additional loss before reaching 30 uF.
This supports retaining three capacitors instead of a marginal two-part bank;
it does not establish a guaranteed combined-corner minimum.

At the maximum 5.5 V input, the captured single 22 uF input capacitor loses
24.37 percent typically. With the same tolerance/temperature factors it
estimates 12.73 uF before aging, compared with the reference's nominal 10 uF.
The remaining additional-loss allowance is about 21.4 percent. The script's
10 uF comparison is a conservative design target, not a manufacturer stated
effective-capacitance minimum. Aging, supplier guaranteed data, ripple-current
and the larger output bank's loop/transient behavior remain required checks.
Schematic fields now distinguish this completed typical-bias review from the
remaining qualification work.

## BUCK5 native capture

The PMIC draft now captures BUCK5 as well: VCC9 pin 54 on 3V3_MAIN,
SW5 pin 53 through L505 XGL4020-471MEC, and FB5 pin 59 sensed after
the inductor on VCC_1V8. C509-C511 form a provisional 66 uF output bank;
C512 is the separate 22 uF input capacitor. Selected RK809-5 startup is
1.8 V at slot 2. VCC9 must be coordinated with VCC_RTC at system startup;
the latter is still unwired and cannot be treated as completed sequencing.

Native netlist checks now cover nine exact nets and 16 fitted components with
MPNs. BUCK3/4, LDOs, RTC/control and unused audio handling remain incomplete.
The updated A3 render was reviewed after moving the codec unit clear of the
third capacitor bank and title block. The reproducible bias calculator now
includes BUCK5 at 1.8 V and the maximum programmable 3.6 V; its 33 uF
comparison comes from the typical application nominal capacitor, not a
specified guaranteed minimum. Output-bank stability remains unqualified.

## PMIC ground and processor reset capture

U501 GNDREF pin 47 and exposed ground pad 69 now connect to GND. RESETB
pin 67 drives RK_RESET_N directly, with R501 10 kR pull-up to VCC3V3_PMU
and C513 100 nF to ground. Both use already-reviewed exact 0603 MPNs.
The RK3566 hardware guide section 2.1.3 requires 100 nF near nPOR and a
pull-up matching PMUIO1; its IO-domain table fixes PMUIO1 at 3.3 V. The
10 kR value is a design choice, giving approximately 1 ms RC and 0.33 mA
pull-up load at 3.3 V. The capacitor must be placed at the future processor
pin rather than next to the PMIC. The MCU recovery reset sink still needs
integration with this net, including fault/off-state behavior.

The guide additionally requires reset asserted before PMUIO1 falls below
2.93 V during shutdown. Connecting PMIC RESETB alone does not prove this
condition on brownout; threshold, sequencing and the recovery reset path
must be reviewed before release. VCC3V3_PMU is still an unresolved LDO
output in the draft. Netlist assertions now cover eleven nets and 18 exact
MPNs; full PMIC ERC remains intentionally incomplete. The render was checked
with the reset passives directly wired and both ground pins visibly joined.

## RTC and VREF bypass capture

Added C514 and C515 as Samsung CL10B105KA8NNNC, 1 uF / 25 V / X7R /
+/-10 percent / 0603 (C29936), matching the reference's nominal 1 uF RTC
and internal-reference bypasses. Manufacturer lists this family in mass
production; typical bias arrays are archived with SHA-256 provenance.
RTC pin 45 now joins 3V3_MAIN, and VREF pin 46 has its direct bypass.
Native checks cover twelve nets and twenty exact-MPN components, and the
updated render was reviewed.

Typical bias change is -0.31 percent at 1.2 V, -8.59 percent at 3.3 V and
-10.04 percent at 3.6 V. Combined with -10 percent initial and -15 percent
temperature factors, estimates are 0.763/0.699/0.688 uF before aging.
These are nominal-reference bypass selections, not proof of any guaranteed
1 uF effective minimum. Do not automatically reuse them for LDO outputs
until required minimum capacitance and stability are resolved.

The alternative CL21B225KAFNNNE was rejected for new capture because the
manufacturer marks it NRND, despite current catalog stock. Its mass-production
CL21B225KAFNFNE alternate is an available 2.2 uF / 25 V / 0805 candidate
(C364318), but has not been selected or substituted into the schematic.

## Manufacturer-priority correction and LDO6 capture

This section supersedes the earlier 3.3 V RTC/VCC9 reference mapping for
our appliance. RK809 Rev 2.4 Figure 1-2 explicitly requires VCC_RTC to be
the highest PMIC input. The RK3566 hardware guide repeats this (except
VCC_SPK_HP) and recommends sharing VCC9. NanoPi's actual sheet uses 3.3 V
RTC/VCC9 alongside 5 V buck inputs and therefore cannot be inherited as
proof of this manufacturer rule. Captured RTC pin 45 and VCC9 pin 54 are
now on 5V_MAIN. BUCK5 is specified for this input. SWOUT1 consequently
follows 5 V and must not later be labeled a 3.3 V output; its use is unresolved.
The reference input CSV header now says Reference Net, avoiding an appliance
mapping claim. RTC-first timing is still required; sharing a rail alone does
not prove it, particularly during differing input-capacitor ramps.

VCC6 pin 30 now uses 5V_MAIN with C516 22 uF input bypass. LDO6 pin 31
provides VCC3V3_PMU and the existing reset pull-up, with parallel C517/C518
1 uF capacitors. Manufacturer section 4.2.2 permits nominal 1 uF LDO output
capacitors; two parts estimate about 1.38 uF at 3.6 V including initial and
temperature factors before aging. The additional capacitance requires loop
review. Feeding a 3.3 V LDO from nominal 3.3 V lacks the datasheet's stated
0.2/0.4 V headroom for its 200/400 mA load ratings. 5 V supplies headroom,
but dissipation can reach 0.68 W at 400 mA and nominal voltages; total PMIC
thermal and actual PMU-domain load must be budgeted. All 5 V PMIC inputs
must remain within their 5.5 V maximum, including startup/transients.

Native captured-net checks pass for eleven nets and 23 exact-MPN parts.
Visual review exposed a BUCK5 note overlapping the new LDO capacitor bank;
the note was moved to the right. Remaining LDO banks, rail sequencing and
complete appliance integration are still unfinished.

## Analog LDO2/3 capture

VCC5 pin 22 now uses 3V3_MAIN with C519 22 uF input bypass. LDO2 pin 21
provides VDDA_0V9 and LDO3 pin 20 provides the separate VDDA0V9_PMU rail;
each has two selected 1 uF / 25 V / 0603 capacitors. These are the selected
-5 variant's 0.9 V slot-1 outputs; LDO3 starts 200 us after LDO2. The
manufacturer rates LDO2 up to 400 mA and high-PSRR LDO3 up to 100 mA;
actual analog-domain currents must be budgeted. At rated limits, their
nominal 3.3-to-0.9 V drops dissipate up to 0.96 W and 0.24 W respectively,
so these ratings cannot be treated as available continuous appliance load
without the combined PMIC thermal calculation. The two output nets must
remain distinct even though their voltage settings match.

Native connectivity audit now covers fourteen nets and 28 exact-MPN parts.
Both analog capacitor banks and the updated supply wiring were rendered and
reviewed. The sheet expanded to A2 to reserve space for remaining PMIC channels;
final compactness and complete hierarchy review remain pending. Neither output
is yet connected to a captured processor package. The selected 2 uF nominal
bypass banks exceed the reference's 1 uF nominal value; combined-corner aging,
actual load decoupling and loop behavior remain explicit checks.

## Remaining enabled LDO output capture

LDO7 pin 3 now supplies VCCA1V8_PMU and LDO8 pin 5 supplies VCCA_1V8,
both 1.8 V at slot 2, with independent two-part 1 uF bypass banks. VCC7
pin 4 uses 3V3_MAIN and C524 22 uF input bypass. LDO5 pin 29 now supplies
VCCIO_SD with the same two-part bank, starting at 3.3 V at slot 4 and
retaining software voltage adjustment for the SD IO domain. VCC6 already
uses 5 V, providing headroom for this 3.3 V rail as well as LDO6.
The SD card's actual switched supply and boot-mode circuitry remain absent.

Native netlist checks now prove exact membership for seventeen captured nets
and 35 exact-MPN parts. The render was reviewed for separate domain labels
and uncluttered bypass banks. LDO1/4/9 remain unused candidates awaiting
manufacturer unused-output policy. LDO7/8 ratings are 400 mA with stated
headroom; at rated maximum each would dissipate 0.6 W from 3.3 V, so actual
load and combined PMIC thermal qualification remain necessary.

The startup CSV now calls switch outputs input pass-through explicitly.
The table's nominal 3.3 V examples do not make SWOUT1/2 voltage regulators:
SWOUT1 follows VCC9 (5 V in the current appliance), while SWOUT2 follows
VCC8, still uncaptured. This prevents silently importing a 3.3 V switch-output
name after the manufacturer-priority RTC/VCC9 correction.

## PMIC I2C capture and unused-codec audit

SCL pin 1 and SDA pin 2 now have named PMIC_I2C_SCL/SDA nets and R502/R503
2.2 kR pull-ups to VCC3V3_PMU. Exact Yageo RC0603FR-072K2L / C114662
parts are 1 percent, 0.1 W, 75 V, 0603; the manufacturer exact-part specsheet
is archived with hash provenance. RK3566 guide section 2.1.14 assigns I2C0
primarily to the PMIC and to PMUIO2, selectable 1.8/3.3 V. Capture chooses
3.3 V PMUIO2 with the PMU supply; firmware IO-domain configuration must match.
Processor balls AJ37/AK38 remain unconnected until the processor symbol is
approved and captured. PMIC address is 0x20 and maximum clock is 400 kHz.

Using TI SLVA689's tr=0.8473*R*C relation, 2.2 kR +1 percent gives a 400 kHz
300 ns rise-time capacitance allowance of about 159 pF. At 100 pF the estimate
is 188 ns. With 3.3 V +5 percent and minimum resistor, a full-low sink sees
about 1.59 mA and resistor dissipation about 5.5 mW, below PMIC's 3 mA VOL
characterization and the resistor rating. Actual total capacitance, processor
sink limits, leakage, rise time and additional pull-ups remain to verify.
Source: https://www.ti.com/lit/an/slva689/slva689.pdf.

The manufacturer datasheet does not give a plain unused-codec pin policy;
the NanoPi reference explicitly grounds several codec pins and floats others.
Register defaults confirm disabled LDO1P8A_EN_CODEC and PDM_EN, but grounding
internal supply outputs still needs a complete enable/default audit. No codec
no-connect or ground markers were added just to suppress ERC. Unused handling
remains open. Native checks now cover nineteen nets and 37 exact-MPN parts.
The render exposed RTC ground-label proximity to the I2C label; the RTC ground
was moved upward before saving.

## PMIC interrupt capture

INT pin 7 now uses PMIC_INT_N with a 10 kR R504 pull-up to VCC3V3_PMU.
The selected Yageo RC0603FR-0710KL is already used in recovery/reset circuits.
The manufacturer electrical table defines INT as open drain; the processor
interrupt input must belong to the selected 3.3 V PMU domain. Pin selection,
firmware active-low configuration, wake behavior and off-state behavior remain
integration checks. At 3.3 V +5 percent and minimum 1-percent resistor, sink
current is at most about 0.35 mA with about 1.21 mW pull-up dissipation.
The input's inactive rise time depends on final trace/pin capacitance and
must satisfy the actual interrupt timing requirements.

The PMIC draft passes exact membership assertions for twenty captured nets
and MPN coverage for 38 fitted parts. Native SVG was visually reviewed.
The completion matrix was refreshed to remove stale 31-part recovery and
five-part supply claims; those earlier dated sections are historical progress.
Full schematic completion and PCB placement remain unachieved.

## PMIC SLEEP startup-state capture

SLEEP pin 49 now uses PMIC_SLEEP with R505 10 kR to ground. This is an
intentional change from the NanoPi reference pull-up: RK3566 guide section
2.2.7 defines normal operation low, standby high, and wake low. RK809
PMIC_SYS_CFG3 register 0xF4 resets SLP_POL to active-high and SLP_FUN to
no effect. The pull-down therefore keeps the intended inactive level while
the host is high impedance, rather than requesting standby immediately after
firmware enables sleep semantics. RK3566 ball 1P19 is the dedicated
PMIC_SLEEP function and must retain that role during processor capture.

A 10 kR sink allows up to about 39.6 uA aggregate leakage before crossing
the PMIC's 0.4 V input-low limit (maximum resistor 10.1 kR). No guaranteed
aggregate leakage budget has yet been proven. When asserted from 3.3 V +5
percent, resistor load is at most about 0.35 mA; host drive strength and
high-level margin still require final pin configuration review. Sleep control
must use active-high sleep mode, not the register's shutdown/restart modes.
The datasheet requires a register read and 2 ms delay between successive
0xF4 operations and about 66 us after each SLEEP-pin activation change;
carry these rules into firmware rather than treating the hardware net as proof
of correct suspend/resume behavior.

The updated render was inspected, and the native captured-net audit passes
for twenty-one nets and 39 exact-MPN components. Remaining power-on control,
RTC clock, DDR rail and unused-pin policy are still unfinished.

## VDC automatic-start sensing capture

VDC pin 61 now uses PMIC_VDC with R506/R507 100 kR / 100 kR divider
from 5V_MAIN and C531 100 nF to ground. All three are already-reviewed
exact 0603 parts. The manufacturer's no-battery reference uses a divider
and 100 nF filter; this design chooses a 1:1 ratio on the common 5 V rail
rather than sensing isolated 12 V ahead of RTC supply. At 5 V nominal,
VDC is 2.5 V. With a preliminary 5 V +/-5 percent rail and independent
1-percent resistors it spans approximately 2.35-2.65 V, below the 5.5 V
operating input limit and above the stated 0.55 V rising-edge threshold.
Threshold tolerance and VDC input leakage are not bounded in the reviewed
pin description, so this calculation is a design estimate rather than a
complete guaranteed startup margin. The nominal Thevenin resistance is
50 kR and RC is 5 ms; the divider load is 25 uA at 5 V.

The PMIC requires VDC asserted for 140 ms before startup, then its -5
variant EXT_EN-to-rail preparation delay (4+N ms, N<50 ms), 2 ms rail slots,
and final reset release. These timings still need full RTC-first/main-rail
integration. A continuously high VDC is rising-edge triggered and must not
be assumed to reboot the PMIC after software shutdown; independent recovery
must produce a valid power/start event. PWRON control remains uncaptured.

Native assertions pass for twenty-two nets and 42 exact-MPN components.
Render review exposed overlap between the bottom-divider resistor value and
filter-capacitor value; the capacitor was moved farther right and connectivity
was checked again. Full PMIC/appliance ERC and physical startup remain open.

## PWRON filter and recovery interface boundary

PWRON pin 52 now uses PMIC_PWRON_N with C532 100 nF / 25 V / 0603
(CL10B104KA8NNNC). The manufacturer's internal 35 kR +/-15 percent pull-up
connects to VCC_RTC, now 5 V; there is no added 3.3 V pull-up or direct MCU
drive. An open-drain transistor interface remains required before connecting
the 3.3 V recovery MCU. The nominal input RC is 3.5 ms, much shorter than
the PMIC's 100/500 ms power-on key debounce. Pulse lengths must still account
for the selected debounce setting and the long-press shutdown threshold.
At 5.5 V and minimum internal resistance 29.75 kR, a low sink carries about
0.185 mA before leakage. Off-state leakage and startup/release timing remain
integration checks. A named net and capacitor alone do not implement recovery.

Updated native checks pass for twenty-three nets and 43 exact-MPN parts;
the rendered filter and explicit 5 V/open-drain note were reviewed. RTC clock,
DDR rail, switch outputs, unused-pin handling and full hierarchy remain open.

## Recovery-to-PWRON sink interface captured

Q501 is the already-reviewed Nexperia MMBT3904,215 / SOT-23 transistor:
collector pin 3 connects to PMIC_PWRON_N, emitter pin 2 to ground, and base
pin 1 receives MCU_PWRON_KICK through R508 10 kR. R509 100 kR pulls the
base down while the MCU output is high impedance. The resolved recovery
symbol is reused with a checked B/E/C pad mapping. There is no 5 V connection
to the MCU input net. MCU_PWRON_KICK is still a boundary awaiting assignment
to an available supervisor GPIO in the integrated hierarchy; capture does not
yet prove independent restart behavior.

At nominal 3.3 V drive and an illustrative 0.8 V base-emitter drop, base
current after the pull-down load is about 0.24 mA, above the previously
calculated maximum 0.185 mA steady PWRON pull-up load. This is an estimate,
not a guaranteed saturation/temperature proof; check MCU VOH, transistor
low-voltage behavior, off-state leakage and filter discharge during bench
qualification. The driver inverts logical assertion: MCU high pulls PWRON low.
Firmware must pulse for the configured key debounce while avoiding a long
press that requests shutdown. Independent supply and MCU-watchdog operation
must be maintained during this action.

Native connectivity assertions now cover twenty-five nets and 46 exact-MPN
parts. Visual inspection caught horizontal base-resistor property rotation;
its reference/value placement was corrected. Full PMIC, MCU signal assignment
and appliance integration remain unfinished.

## Supervisor PWRON GPIO assignment audit

Reserve STM32G0B1CCT6 PB4 / LQFP48 pin 43 for MCU_PWRON_KICK.
The manufacturer DS13560 pinout confirms PB4 at pin 43, and the current
native recovery symbol has that pin marked unused. Existing watchdog,
modem/Ethernet controls, UART and SWD assignments remain occupied and unchanged.
The assignment is recorded in `hardware/pinmaps/supervisor-appliance-assignment.csv`.
Source: https://www.st.com/resource/en/datasheet/stm32g0b1cc.pdf.

An attempted standalone pin label produced the correct isolated-pin ERC
warning because the recovery and PMIC drafts are not yet connected under
one root. The temporary wiring was removed; PB4 remains NC in the
recovery-only hierarchy until its integration connects it to R508. No ERC
exception was added. Firmware must preload low before configuring PB4 as
push-pull output; high asserts the PWRON transistor. GPIO drive and physical
pulse timing still require validation. This is an audited allocation, not a
claim of completed connectivity or an operational restart path.

## Appliance root integration

`hardware/appliance.kicad_sch` now includes the recovery/always-on hierarchy and
the partial PMIC sheet. Native export contains 78 annotated components. Recovery
checks pass with zero ERC violations and 32/32 MPN coverage; the separate PMIC
capture checker passes 25 exact nets and 46 MPNs. These do not establish full
appliance ERC or schematic completion. MCU_PWRON_KICK is still an unjoined
PMIC boundary. Run `python3 hardware/tools/build_appliance.py` after regenerating
any child sheet to refresh appliance annotation contexts.

## Supervisor-to-PMIC restart integration

The appliance native netlist now joins U201 pin 43 (PB4) and R508 pin 1
on global MCU_PWRON_KICK. Q501 sinks PMIC PWRON when the supervisor
asserts this output. The PMIC capture checker still passes all 25 nets and
46 MPNs. Recovery-only ERC now reports one isolated_pin_label warning for
this off-sheet boundary; its previously recorded zero-violation result was
before integration. No exclusion was added. Full appliance ERC is still
incomplete because the remaining PMIC and subsystem circuits are absent.
Firmware pulse timing, reset-default behavior and physical restart require
verification after the full schematic is captured.

## Remaining buck rail audit

RK809 Rev 2.4 Table 4-4 specifies RK809-5 BUCK4 startup OFF, with a
0.5 V programmed default. It cannot supply boot-time 3V3_MAIN. VCC4 pin
66 now joins 5V_MAIN with C533 (CL32B226KAJNNNE) input bypass; SW4/FB4
remain unfinished. Native capture checks pass 47 PMIC components and 79
appliance components. A separate switched 3.3 V source remains required.

BUCK3 is a 1.5 A DDR regulator with 0.8 V feedback (0.784–0.816 V in
external-divider mode). DDR type determines its output and divider;
RK3566 guide section 2.4.4 differentiates LPDDR4 and LPDDR4X supplies.
No DDR output voltage or divider is committed before exact memory selection.
Sources: archived rk809-datasheet-v2.4.pdf pages 22, 34;
rk3566-hardware-guide-v1.1-cn.pdf page 32.

## Main 3.3 V regulator candidate

See main-3v3-supply.md: MP2143DJ-LF-Z is source-audited as a
5V_MAIN-to-3V3_MAIN candidate. Its PG output has an internal VIN pull-up
and cannot connect directly to the independent 3.3 V MCU. No regulator
circuit or exact passive BOM is captured yet.

## Main 3.3 V appliance integration

The main3v3 sheet is now in the appliance root. 5V_MAIN and 3V3_MAIN
are global between regulator and PMIC sheets. Native export contains 86
components. check_appliance_capture.py verifies exact 3V3_MAIN membership
including regulator output sensing and PMIC VCC5/VCC7 inputs, restart
connection, shared 5 V input and separation from the recovery MCU supply.
Root SVG inspected. No full ERC pass is claimed; enable, PG translation
and downstream load/sequence remain incomplete. Regenerate build_appliance.py
after either supply or PMIC generator.

The main 3.3 V enable divider is captured and appliance-netlist checked.
It follows 5V_MAIN; independent upstream 5 V power control remains absent.
No PMIC output feeds this enable, avoiding a boot dependency loop.

## Appliance ERC baseline after project configuration

Added hardware/appliance.kicad_pro so the root resolves registered local
symbol/footprint libraries. Native ERC initially reported 69 violations:
10 library configuration issues, 3 duplicate rail-name warnings and 56
electrical violations. Canonical rail labels now replace redundant SENSE
aliases on the same conductor without changing captured-net membership.

Current all-severity ERC: 56 violations (39 pin_not_connected,
10 pin_not_driven, 7 power_pin_not_driven). No exclusions were added.
The latter category includes the uncreated 5 V source, remaining PMIC
inputs and the main 3.3 V output source representation. These require
circuit/unused-pin policy closure, not blanket flags or suppression.
PMIC 25-net/47-MPN and appliance 92-component integration checks still pass.
This is an incomplete-design baseline, not a schematic release.

## DDR exact-part investigation

See ddr-selection.md. The NanoPi reference symbol has no exact memory
MPN. Micron Z42M 2 GB x32 candidate identified, but manufacturer full
datasheet access and orderable suffix reconciliation remain open. No
unsupported DDR ball map or voltage divider is captured.

## Main 5 V stage sizing investigation

TPS56637RPAR 5 V/6 A manufacturer reference archived. See
main-5v-supply.md: a simultaneous downstream-rating scenario exceeds
6 A, so the stage is not frozen before actual domain budgeting.
No 5 V input power flags were added to conceal the missing source.

## 2026-10-04 internal PMIC bypass capture

RK809 Rev 2.4 Figure 1-2 specifies separate 1 uF bypasses on VCC_CPVDD
(pin 38), VCC_1P8A (44) and VCC_1P8D (48). C534–C536 now capture those
internal regulator outputs using the existing Samsung CL10B105KA8NNNC
0603 selection. They are not connected to external supply rails. Native
checks verify all three exact two-node nets and their ground returns. The
PMIC draft has 50 components; the appliance root has 110. Audio charge-pump
and unused-pin policy remain unresolved; this addition does not close them.

## 2026-10-04 PMIC no-battery sense and audio-supply capture

RK809 Rev 2.4 Figure 1-2 grounds SNSP/SNSN in the no-battery application.
Pins 62/63 now share ground. HP_SNS pin 40 is the headphone reference return
and also connects to ground as shown. VCC_SPK_HP pin 33 now receives 5V_MAIN
with C537, Samsung CL31B106KBHNNNE, 10 uF / 50 V X7R 1206, matching the
reference's nominal 10 uF bypass. The datasheet speaker supply range is
2.7–5.5 V. This preserves the supply independently of the eventual disabled
codec policy; no audio output or internal regulator output was grounded.

Native exact-net checks pass for all new connections and the 111-component
appliance capture. The affected circuitry was rendered and visually reviewed.
Charge-pump wiring, digital audio unused-pin policy and full-system startup
remain open.

## 2026-10-04 PMIC switch-input supply capture

VCC8 pin 57 now connects to VCC_1V8 (BUCK5), following RK809 Rev 2.4
Figure 1-2, with C538 1 uF / 25 V Samsung CL10B105KA8NNNC bypass.
SWOUT2 remains unused and unconnected; any future use would pass through
1.8 V, not regulate an independent rail. Native checks verify exact membership
of the expanded VCC_1V8 net and ground return. The affected supply circuitry
was rendered and inspected. The PMIC draft has 52 components and the appliance
112. Full ERC reports 45 violations without exclusions.

## 2026-10-04 PMIC charge-pump capacitor capture

RK809 Rev 2.4 Figure 1-2 specifies 2.2 uF between CPP pin 37 and CPN pin 36,
and 2.2 uF from negative rail VCC_CPVSS pin 35 to ground. C539/C540 now
capture these with Samsung CL31B225KBHNNNE, 50 V X7R, 1206, 10 percent
(C50254), reusing the manufacturer bias-data family already archived. The
ceramic parts are nonpolar: C539 is a flying capacitor, not a ground bypass.
The negative rail was not tied directly to ground or fed externally.

Native checks verify exact CPP/CPN/CPVSS connections, C540 ground and 54
PMIC components (114 in appliance). The affected circuits were rendered and
inspected. This follows reference nominal values; effective capacitance across
combined bias/temperature/aging, charge-pump startup and disabled-codec policy
remain qualification/integration checks.

## 2026-10-04 correction: VCC8 operating range

The prior VCC8-to-BUCK5 capture followed the generic Figure 1-2 topology
without accounting for our BUCK5's 1.8 V output. RK809 Rev 2.4 DC
Characteristics, Switch2 table on page 25, specifies **2.7–5 V** input.
That contradicts using our 1.8 V rail even though a generic reference labels
the source BUCK5. VCC8 pin 57 and C538 now connect to **3V3_MAIN**.
This correction supersedes the earlier VCC8 entry. Native checks remove
VCC8/C538 from VCC_1V8 and require them on 3V3_MAIN. SWOUT2 remains
unused; any later use passes through 3.3 V and requires startup/load review.

## 2026-10-04 unused-codec capture

No audio function is required. RK809 Rev 2.4 section 4.4.5 identifies MCLK
as a fixed input and LRCLK/BCLK as mode-dependent inputs/outputs. MCLK 16
and SDI 17 now connect to ground. LRCLK 14/BCLK 15 use separate 10 kR
R510/R511 pull-downs (Yageo RC0603FR-0710KL, 0603). Unlike the NanoPi
reference's hard grounds, these permit an accidentally enabled output to
drive without a direct short. At 5.5 V and -1 percent resistance, each would
draw at most 0.56 mA / 3.1 mW, below the 0.1 W resistor rating. Actual
codec operating configuration remains disabled and must be enforced by firmware.

Unused SDO 18, PDMCLK 19, speaker outputs 32/34, headphone outputs 39/41
and microphone inputs 42/43 now have no-connect markers. The NanoPi reference
floats the corresponding audio pins except PDMCLK, which it grounds; we leave
PDMCLK open because the manufacturer pin table explicitly defines it as an
output. Internal supplies retain the captured bypass/charge-pump networks.
No supply output is grounded. Manufacturer register defaults leave PDM_EN
and SCK_EN zero (0x48); I2S_RX_MST resets to slave (section 5, page 109).

Native captured-net checks pass for 56 PMIC / 116 appliance components.
Rendered views were corrected for reset-label and title-block overlap.
Full ERC reports 25 violations without exclusions; this closes only the
captured unused audio circuitry, not the still-missing appliance blocks.

## 2026-10-04 native RK3566 model audit

C2943786 has an eight-unit native EasyEDA model. easyeda2kicad v1.0.1
converted it to the unregistered reference candidate
`hardware/reference/rk3566-native-candidate.kicad_sym`; the accompanying
footprint is also archived as a candidate, with hashes in sources.json.
This provides an existing native model to adapt and audit rather than
generating a new symbol from the pending PDF-derived table.

`python3 hardware/tools/check_rk3566_native.py` verifies all 565 unique
ball identifiers exactly match the manufacturer extraction. Names comprise
339 exact matches, 211 single manufacturer mux-function names and 15 other
differences. Thirteen differences shorten DDRPHY supply names to DDR; two
shorten USB3_HOST1_DP/DM to USB_HOST1_DP/DM. The saved audit CSV preserves
every comparison. All 565 electrical types are unspecified, so this model
cannot yet support meaningful ERC. Mux alternates, electrical directions,
functional grouping/visual review and package geometry need completion before
registration and processor capture. No new processor circuitry added yet.

## 2026-10-04 processor supply/ground electrical roles

`hardware/tools/prepare_rk3566_electrical.py` produces an unregistered native
model derivative and a per-ball evidence CSV. It types **80 supply and 187
ground balls** as power inputs, based on RK3566 Rev 1.2 power/ground groups
and recommended operating conditions. Thirteen DDRPHY supply names and two
USB3_HOST1 names are corrected to the manufacturer names. Power-pin shapes
are plain lines, avoiding native inversion glyphs on supply inputs.

All 565 ball identifiers remain unique and intact. The other **298 balls**
remain explicitly unspecified pending function/mux-direction review; TVSS
is among them and is not blindly classified as an ordinary ground. The
derivative is not registered for capture. Eight native units export through
KiCad, and the core-supply unit was visually inspected. Native spacing and
property placement still need cleanup and full multi-unit visual review.
This role pass does not choose voltages for unused PHY domains or prove
package geometry, processor sequencing or complete electrical fidelity.

## 2026-10-04 GPIO capabilities and mux identity preservation

The unregistered processor derivative now types 142 primary GPIO pads as
bidirectional, representing their GPIO input/output capability rather than
reset configuration or any selected alternate function. All 565 balls remain
intact: 267 supply/ground, 142 GPIO and 156 other unspecified pins.

For GPIO mux entries, 443 manufacturer function names are preserved as native
KiCad alternates instead of slash-delimited display names. Per-alternate
electrical directions remain explicitly unspecified and are recorded in
`hardware/pinmaps/rk3566-mux-review.csv`; they must be reviewed before selected
functions are captured. Native KiCad successfully exports all eight units.
The PMU/GPIO unit was visually inspected; original pin-number/name spacing,
clock glyphs, supply placement and in-body properties still need cleanup.
This does not claim a complete symbol or switch processor capture to an
unqualified model.

## 2026-10-04 processor interface electrical roles

The native derivative now types the DDR address/command outputs, bidirectional
data/strobes, output data masks, USB2 data pairs, USB3/PCIe transmit and
receive lanes, bidirectional PCIe reference clock and eDP AUX, video inputs
and outputs, 24 MHz oscillator pins, reset input and SARADC inputs.
Evidence: RK3566 Rev 1.2 Table 2-4, pages 42–51; DDR_RZQ/VREF analog roles
also follow hardware-guide sections 2.1.9.5–6. DDR_RZQ and HDMI_REXT are
passive resistor interfaces, not GPIO outputs. DDR_VREFOUT is an output.

Totals: 267 power inputs, 194 bidirectional pins, 76 outputs, 25 inputs,
2 passive pins and **one unspecified primary pin (TVSS)**. All 565 ball
identifiers are retained. The 443 GPIO alternate directions remain unreviewed.
Native KiCad exports all eight units; the high-speed interface unit was
visually inspected. Long protocol alternatives and native graphical markers
still need cleanup before active registration. No processor circuit is yet
connected, and these counts do not close pin selection, rail mapping, unused
PHY policy, memory training, footprint geometry or system qualification.

## 2026-10-04 processor protocol alternate cleanup

The native derivative now has 745 selectable alternates spanning GPIO, memory
and protocol functions. Primary display names no longer contain slash lists.
DDR and high-speed protocol alternate directions follow the already reviewed
manufacturer interface roles; unresolved GPIO directions remain unspecified.
Two MIPI_DSI_TX0/LVDS_TX0 supply-name shorthand entries are expanded into
complete primary/alternate supply names, both power inputs. No minus-sign
placeholder becomes an alternate function. All 565 balls remain unchanged.

Eight imported graphical circles were removed: these were pin-one decoration
at each unit's first row and visually resembled inversion bubbles despite not
being electrical pin shapes. Native KiCad exports all eight cleaned units;
the protocol unit was inspected. Functional regrouping, correct supply/ground
placement, property positioning and pin-number spacing remain before capture.

TVSS remains unresolved. Search located a newer manufacturer-authored Rev 1.5
PDF mirror, but direct retrieval returned 404; no archive or revision-parity
claim was made. The NanoPi reference connects TVSS, but that alone does not
establish its exact electrical type. No guesses were added to suppress ERC.

## 2026-10-04 serial/control GPIO alternate directions

Reviewed alternate directions now cover I2C, UART, SPI, PWM, eMMC/SDMMC,
I2S/PDM/SPDIF, smart-card, GMAC and camera functions. RK3566 Rev 1.2 Table
2-4 explicitly marks SPI and PWM pads bidirectional; they are not blindly
typed as master outputs. I2C SCL/SDA are also bidirectional. eMMC strobe
direction additionally follows hardware-guide Table 2-5.

There are 745 unique alternate identities: 294 bidirectional, 226 output,
107 input, 2 power input and **116 still unspecified**. Exact native
ball IDs and critical I2C0/eMMC roles were checked; all eight units load and
export through native KiCad. No primary-pin counts changed.

PCIe CLKREQ and PERST mux functions are manufacturer inputs, WAKE is
bidirectional. A root-complex NIC reset output must use a reviewed GPIO
output configuration rather than silently repurposing the input PERST mux.
Remaining alternate review includes flash, EBC/VOP, debug, PMIC sleep and
thermal-shutdown controls, plus the independent TVSS primary-pin question.

## 2026-10-04 flash, debug, shutdown and video alternate review

The unregistered native derivative retains all 565 balls and 745 selectable
alternates. Datasheet Rev 1.2 Table 2-4 resolves ARM SWD, MCU JTAG, NAND
and HDMI control directions. HDMI_TX_HPDIN is corrected from input to
bidirectional, matching the manufacturer table. FSPI data uses hardware-guide
Table 2-7 because the datasheet direction column conflicts with its own
“data inout” description. FSPI clocks and chip selects retain the table's
bidirectional capability rather than assuming a fixed host-only direction.

The hardware guide identifies TSADC_SHUT and PMIC_SLEEP as processor
outputs. Tables 2-30 through 2-32 resolve BT1120, BT656 and EBC outputs;
Table 2-19 resolves ETH1_REFCLKO_25M output. ISP flash/prelight outputs
and flash-trigger input follow datasheet Table 2-4.

There are now **19 unspecified alternate instances** and one unspecified
primary pin, TVSS. Unresolved alternates include AVS, audio PWM, SATA
controls, GPU power enable, FLASH_WPn, ETH0 clock, test clock and VOP PWM.
No processor has been added to the appliance schematic yet. All eight
units export successfully through native KiCad; functional grouping,
geometry and footprint review remain prerequisites for active capture.

## 2026-10-04 existing RK3566 footprint coordinate audit

`check_rk3566_footprint.py` checks the archived native footprint without
modifying its geometry. All 565 unique pad identifiers match the extracted
manufacturer ball table. Its 343 inner balls follow a 20-column, 18-row
0.65 mm lattice, while 222 outer balls follow a 38-column, 35-row 0.4 mm
lattice. Each coordinate matches within 0.011 mm, allowing the native
export's hundredth-millimetre rounding and 0.005 mm inner-array offset.

Visual inspection of Rev 1.2 Figures 2-3, 2-5 and 2-6 confirms the mixed
pitch arrangement, top-view row/column orientation and outer 14.8 x
13.6 mm ball-centre extent. Package body is nominally 15.5 x 14.4 mm,
height 0.794 mm (maximum 0.889 mm). The dimensional table's ball diameter
b is nominally 0.27 mm, range 0.22–0.32 mm; this is **not a PCB land
diameter recommendation**. The native footprint uses 0.22 mm circular
lands everywhere and lacks fabrication and courtyard layers and a 3D model.
Those manufacturing details remain unresolved; the footprint is not registered
as production-ready. This audit closes identifier/coordinate checking only.

## 2026-10-04 standalone processor capture draft

`hardware/processor.kicad_sch`, generated by `build_processor.py`, contains
all eight native RK3566 units as one U801 component and all 565 distinct
instance pins. Native KiCad netlist export confirms one U801 component.
The A2 render was inspected; reference/value fields sit above each unit,
and unit H was moved above the title block after detecting an overlap.

This standalone sheet intentionally has open connections and no assigned
production footprint. It is not yet attached to the appliance root and
does not change the root's 116-component count or ERC baseline. The
19 uncertain unused alternate roles and TVSS remain explicit. Processor
supply mapping, bypass capacitors, clocks, reset, boot straps, storage,
DDR and high-speed interfaces still require capture and validation.

## 2026-10-04 processor ground connections

The standalone processor sheet now connects exactly 187 documented
ground balls to global GND, including DDR_AVSS, PMUPLL_AVSS and
SYSPLL_AVSS. TVSS ball 1M18 remains unconnected and unspecified;
its name alone does not establish a ground connection.

`check_processor_capture.py` exports a native KiCad XML netlist and
verifies the exact ground membership against the reviewed manufacturer
ball table, one U801 component and 565 library pins. The updated A2
render was inspected for label/body and title-block overlaps. Supplies,
interfaces and appliance-root integration remain incomplete.

## 2026-10-04 processor PMIC control terminals

The standalone U801 capture now exposes global PMIC_I2C_SCL on AJ37,
PMIC_I2C_SDA on AK38 and PMIC_SLEEP on 1P19, matching the documented
processor assignments and existing PMIC net names. Native netlist assertions
verify each exact ball. The symbol retains the pads' GPIO primary names
and bidirectional electrical capability; a sheet note records the required
I2C0 and dedicated sleep functions. Firmware pinmux remains an integration
requirement, and the intended PMUIO2 3.3 V supply is not yet connected.

These terminals do not yet connect to U501 because the processor sheet
is standalone and the PMIC sheet's control labels remain local. Hierarchy
integration must explicitly join them and verify pull-up and sleep-pull-down
membership. The processor unit-D render was inspected for label collisions.

## 2026-10-04 processor hierarchy integration

The appliance root now includes processor.kicad_sch as page 9, with
U801 counted once: **117 components across nine sheets**. PMIC SCL,
SDA and SLEEP labels are now global. Exact combined-net assertions prove
AJ37 joins U501 pin 1 and R502 pin 2; AK38 joins U501 pin 2 and R503 pin 2;
1P19 joins U501 pin 49 and R505 pin 1. All 187 processor ground balls
join appliance GND. Existing restart and supply assertions continue to pass.

The root was enlarged to A3 after visual review found the fifth child sheet
outside the A4 border and a note overlapping the title block. The revised
root render fits all five direct child sheets and the draft note.

Full native ERC now reports **512 violations**: 391 pin_not_connected,
85 power_pin_not_driven, 28 pin_not_driven and 8 lib_symbol_issues.
The processor's unresolved supply/interface connections remain visible;
ProcessorDraft is embedded but not yet a registered project library. No ERC
exclusions were added. This integration is not full electrical sign-off.

## 2026-10-04 first processor supply connections

All nine VDD_LOGIC balls plus PMU_VDD_LOGIC_0V9 ball 1N16 join
VDD_LOGIC from PMIC buck 1. All five VDD_GPU balls join buck 2.
PMUIO1 ball 1P16 and PMUIO2 ball 1N15 join VCC3V3_PMU from LDO6,
matching the selected I2C0/reset IO voltage. The RK3566 recommended
conditions give PMU logic 0.81–0.99 V and PMUIO1 2.97–3.63 V;
PMUIO2's selected 3.3 V mode requires matching firmware IO-domain setup.

Exact appliance-net assertions now include all 17 processor supply balls,
the corresponding PMIC output/sense pins, inductors, output capacitor
banks and pull-ups. Native render inspection confirms readable rail labels.
This joins existing rail outputs only: processor-local bypass/placement,
rail load budgets and sequencing remain unfinished. CPU, NPU, DDR,
analog and other IO domains are still open. Full ERC reports 480
violations after these supply connections, without exclusions.

## 2026-10-04 processor reset integration and draft library

U801 nPOR_u ball AG38 now joins global RK_RESET_N with U501 RESETB
pin 67, R501 10 kR pull-up to the selected 3.3 V PMU rail and C513
100 nF to ground. Exact appliance netlist membership is asserted. The
processor unit-D render was inspected; reset and sleep labels remain distinct.
This connection does not prove reset timing during supply collapse, nor
complete the recovery MCU reset sink. C513 must be placed near AG38.

The reproducible processor generator now also writes ProcessorDraft.kicad_sym,
registered in the project's symbol table. The registered symbol matches the
embedded draft and deliberately has no production footprint assignment.
Native ERC no longer reports missing-library issues. Current full ERC is
**470 violations**: 373 unconnected pins, 70 undriven power pins and
27 undriven pins. No exclusions were used. Remaining supply, bypass,
interface and firmware sequencing work is still required.

## 2026-10-04 PMU logic correction and PLL supply capture

**Correction to the preceding supply mapping:** PMU_VDD_LOGIC_0V9
ball 1N16 belongs on VDDA0V9_PMU, not the switched VDD_LOGIC rail.
The NanoPi R3S reference sheet 8 explicitly places this PMU-domain logic
input on VDDA0V9_PMU. The hardware guide section 2.2.2.1 describes
that rail as retained for PMU-domain logic and oscillator operation. The
previous connection was changed and exact membership assertions updated
to prevent it silently reappearing. VDD_LOGIC now has only its nine
VDD_LOGIC balls; 1N16 shares the dedicated PMU analog LDO rail.

Guide Figures 2-17 and 2-18 additionally establish PMUPLL_AVDD_0V9
1P17 on VDDA0V9_PMU, PMUPLL_AVDD_1V8 1N18 on VCCA1V8_PMU,
SYSPLL_AVDD_0V9 1H5 on VDDA_0V9 and SYSPLL_AVDD_1V8 1H4 on
VCCA_1V8. Those four balls are now connected to their separate LDO rails.
Figure 2-17/18 require local 1 uF plus 100 nF bypass at each PLL supply;
these processor-local banks remain to be captured and must not be
confused with the existing PMIC output capacitor banks.

The combined netlist verifies exact LDO, existing output-capacitor and
processor membership on each of the four analog rails. Processor unit-D
render was inspected. Native full ERC is now 462 violations, without
exclusions. PMU retention and full power sequencing remain unqualified.
