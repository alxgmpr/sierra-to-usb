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
