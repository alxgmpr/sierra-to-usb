# Complete appliance schematic — in progress

Authorized 2026-10-03. Work branch: `codex/complete-appliance-schematic`.
The original dirty checkout was copied to the isolated worktree without changing
its files. Prior recovery circuitry is retained. No procurement or fabrication.

## Scope and completion evidence

| Required block | Current authoritative state | Required before schematic completion |
|---|---|---|
| Recovery MCU, watchdog, SWD and reset outputs | 26-component recovery circuitry in four-sheet, 31-component supply-integrated capture; native ERC/connectivity passes again on 2026-10-03 | C203 effective-capacitance review pending; manufacturer MCU pin audit; reset voltage margin; target-domain interface integration |
| Independent always-on supply | `hardware/always-on.kicad_sch`, 5 components, TPS62177DQCR, LPS4018-103MRC; native ERC and all five circuit-net checks pass | Capacitor effective capacitance; rail load; power fault integration; final appliance hierarchy still required; now integrated into recovery hierarchy |
| RK3566 / DDR / PMIC | Archived reference schematic, Rockchip full datasheet and hardware guide; 565-ball CSV extracted; symbol-table review pending | Exact supported RAM and DDR training route; PMIC silicon/suffix and rail sequence; all package balls checked; native capture with complete decoupling and clocks |
| Boot storage and recovery | Signed A/B and recovery requirements exist; storage not selected | Capacity budget, exact eMMC, SD/USB recovery circuit and boot strap audit |
| 2.5GbE | RTL8125BG-CG remains candidate | Exact pin/reference circuit, clocks/rails/reset/PCIe coupling and 2.5G PoE-rated magnetics; symbol and footprint checks |
| Isolated PoE | Archived TI TIDA-050023 schematic and BOM as candidate reference | Whole-appliance peak and startup budget, exact class, transformer/protection/feedback/MPS/allocation integration; isolation boundary audit |
| Modem power | Requirements only | Voltage/current envelope per model, switch/eFuse/ramp/discharge, default-off controls and fault sensing |
| EM9190 / EM9293 sockets and SIM | Older manufacturer PTS research; contacts 24/38/68 conflict with Quectel | Current controlled pin tables, complete per-model profile and power/control/SIM/USB3 capture |
| RM520N-GL / RM551E-GL sockets and SIM | RM520 guide exists; current RM551 production guide still missing | Current controlled hardware guides and per-model pin/voltage/control/SIM/USB3 capture |
| Full hierarchy and BOM | Not yet present | One integrated appliance root; exact MPN/manufacturer/footprint for every fitted component; BOM exported from native netlist |
| Visual and electrical review | Always-on draft rendered and corrected; recovery tests rerun | All sheets and circuit crops inspected, native ERC and complete critical-net assertions, manufacturer pin fidelity, footprint pad parity |

No PCB file exists. Do not start placement until the integrated schematic and
exact parts meet the criteria above. Physical throughput, thermal/EMC/isolation,
power interruption and unattended recovery remain separate qualification work.

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
