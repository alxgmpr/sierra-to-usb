# DDR selection remains open

NanoPi R3S LTS 2411 sheet 7 uses a generic LPDDR4_200p symbol, not
an exact manufacturer MPN. FriendlyElec specifies 1/2 GB LPDDR4X for
R3S. The reference therefore proves an architecture, not our exact BOM.

A 2 GB x32, 200-ball Micron candidate is MT53E512M32D1ZW family.
The manufacturer catalog lists MT53E512M32D1ZW-046BWT:B as Production,
16 Gb, 4266 MT/s, 1.1/0.6 V, -25 to +85 C, 10 x 14.5 x 1.05 mm.
The indexed assembly database instead returns MT53E512M32D1ZW-046 WT:B
(C5330500, 38 indexed units). Do not assume these strings establish the
same orderable revision without manufacturer clarification.

Production datasheet Embedded LPDDR4/LPDDR4X SDRAM (Z42M) covers
MT53E512M32D1 / MT53E1G32D2 / MT53E512M64D2 and is access-controlled
on the manufacturer site. Public marketing voltage data is insufficient
for package-ball, current, timing and power-sequence capture. Automotive
AAT:B variant is Contact Sales in manufacturer catalog. Do not replace
missing data with a distributor single-rail voltage description.

Required before selection: exact revision and lifecycle, complete controlled
ball table, VDD1/VDD2/VDDQ ranges and sequencing, current/decoupling,
RK3566 DDR training support for this density/die, and assembly availability.
LPDDR4X requires a separate 0.6 V domain per RK3566 hardware guide;
BUCK3 DDR rail must not be arbitrarily set to DDR4 1.2 V.

Primary sources reviewed 2026-10-03:
- https://wiki.friendlyelec.com/wiki/index.php/NanoPi_R3S
- Archived hardware/reference/nanopi-r3s-lts-2411.pdf sheet 7.
- https://in.micron.com/products/memory/lpddr-components/lpddr4/part-catalog
- https://www.micron.com/products/memory/lpddr-components/lpddr4/part-catalog/part-detail/mt53e1g32d2fw-046-wt-b

No DDR symbol, footprint or regulator divider has been generated from this
candidate. Continued supply/processor/storage/modem work remains possible.

## Manufacturer loader and WDQS wiring requirements

Pinned rockchip-linux/rkbin revision
3e288fe814e059dd06833495f845cab04ac20a5c includes RK3566 200-ball
LPDDR4X templates and a separate WDQS loader family. The specific
release note dated 2025-11-20 requires a 560R weak pull-up on DQSn
for WDQS support. It warns that boards without DQSn pull-ups must use
regular bin/rk35 loaders, while boards with these pull-ups must use
WDQS loaders; mismatching them can cause reliability issues.
The template table identifies parts needing WDQS through application
notes in Rockchip's controlled DDR approved/reference vendor lists.
Those lists remain unavailable, so we cannot infer WDQS requirements
from a generic LPDDR4X marketing description or ball count.

The default RK3566MINIALL.ini uses the regular 1056MHz v1.26 loader,
USB plug v1.17 and SPL v1.14. Standard release notes report single-channel
LPDDR4/LPDDR4X support and capacity/startup fixes in v1.26. Special
mixed-package latency-mode parts require a separate v1.26 loader and
matching BL31; this does not prove our Micron candidate uses that mode.
Preserve the original RK3568 CHIP_NAME in the archived manufacturer INI;
it is not a typo we have independently qualified for correction.

Before RAM capture, resolve exact-part vendor-list classification and
DQSn pull-up requirements together with its ball map and power sequence.
Before firmware release, choose and hash the matching DDR loader and
BL31, then verify training, repeated cold/warm starts, suspend/resume,
voltage/frequency transitions and memory margins on the actual PCB.
Manufacturer full-space test notes explicitly say the test does not detect
all faulty cells; max-frequency scan is only an approximate aid.
No binary has been installed or executed on hardware.

Original manufacturer documents and SHA-256 provenance are archived in
hardware/reference/rockchip-ddr-template-table.md,
rockchip-rk3566-ddr-release.md, rockchip-rk3566-ddr-specific-release.md
and rockchip-rk3566-loader.ini, with URLs in sources.json.

## Public Micron Z42M revision located

Micron-authored Rev. I (04/2023), mirrored by RS, is readable through
web PDF extraction at https://docs.rs-online.com/a381/A700000015750630.pdf.
Local retrieval returned HTTP 403, so no original PDF/hash is archived yet.
This is an older manufacturer document hosted by a distributor, not proof
that it is Micron's latest controlled revision.

Table 2 separately lists both -046 WT:B and -046B WT:B; the part-number
chart identifies the extra B as an alternate substrate option. Therefore
the previously observed catalog strings need not be a transcription error;
they represent distinct ordering options. Exact package option must still
be frozen. Figure 5 (printed page 22) is the single-rank 200-ball map;
Figure 6 is dual-rank and must not be substituted. ZW package dimensions
are in Figure 9 (printed page 28).

Table 160 (printed page 214) gives LPDDR4X ranges: VDD1 1.70–1.95V,
VDD2 1.06–1.17V and VDDQ 0.57–0.65V, nominal 1.8/1.1/0.6V.
This removes the public voltage-data gap, but current/sequence review,
exact native model audit and WDQS classification remain pending.

## Native standard-substrate candidate preserved

C5330500 resolves exactly to MT53E512M32D1ZW-046 WT:B, the standard
substrate option. Its native EasyEDA symbol and footprint were converted
with easyeda2kicad v1.0.1 and preserved unregistered in hardware/reference.
A structural check found 200 unique symbol ball identifiers, matching all
200 footprint pad identifiers. The native pin inventory is saved as CSV.
This checks internal consistency only, not the manufacturer ball map.
The footprint's name references MT53D512M32D2DS; package identity must
therefore be established from geometry and ball map, not its library name.
The single oversized symbol and unspecified electrical pin types require
audit and readable grouping before schematic use. No production footprint
or RAM symbol has been registered. Indexed stock of 38 is not reserved.

## Power-sequence and rank-specific audit findings

Micron Rev. I printed pages 43–44 require VDD1 to rise no later than
VDD2, and VDD2 no later than VDDQ. During ramp, RESET_n stays low
and both channels initialize together. Rail ordering must be reviewed
against actual RK809 startup slots and the separate 0.6V regulator.
Printed page 46 also requires ordered shutdown; uncontrolled power loss
is limited to 400 occurrences over device life. Persistent appliance power
loss therefore needs a shutdown/hold-up review, not just startup wiring.

The native model has generic NC/second-rank aliases on H3, R3, J5, P5
and A8. These must be resolved for the selected single-rank part before
registration. No full manufacturer ball-map match is claimed from flattened
PDF text. check_micron_native.py now verifies the preserved 200-entry
inventory and symbol/footprint identity consistency.

## Original PDF retrieved and visually inspected

The RS URL with ?download=1 and a browser User-Agent returned the original
9,334,735-byte PDF. It is now archived as micron-z42m-rev-i.pdf with
SHA-256 provenance. This supersedes the earlier local-retrieval failure;
its age and distributor-hosting boundary remain unchanged. A rendered
printed page 22 was inspected: A8, H3, R3, J5 and P5 are NC for the
single-rank device, resolving the native model's five second-rank aliases.
Full 200-ball comparison is still pending.

RK809 Rev 2.4 printed pages 29–30 describe RESETB assertion followed by
power-channel shutdown 2ms later for normal shutdown. Undervoltage uses
a separate path with immediate buck shutdown. Neither statement proves
Micron's CKE/input-level or rail-decay limits at the memory balls. Extra
hold-up is a possible implementation, not an established requirement;
first review regulator disable/discharge paths and worst-case capacitance,
load and decay trajectories for planned and abrupt loss of input power.

## Complete native ball-name comparison

The archived single-rank diagram was extracted by its cell coordinates,
including split subscript text, and compared with the existing native model.
All 200 identifiers were covered: 195 names match exactly; the remaining
five are the previously reviewed NC/second-rank aliases. There are no other
name differences. The RESET_n spelling is preserved exactly.
The reproducible extraction audit and result CSV are now saved. This audits
an existing native model; it does not register a new PDF-derived symbol.
Electrical pin typing, readable unit grouping, package geometry and WDQS
classification remain before RAM schematic integration.

## Native-model electrical review derivative

Prepared an unregistered derivative using Micron Table 5 (printed page 24):
110 power/ground inputs, 44 bidirectional data/strobe/DMI pins, 23 inputs,
10 NC pins and 13 passive pins (12 DNU plus ZQ0). The five rank aliases
are resolved to NC while all 200 ball identifiers are preserved. DNU is
passive because Micron permits grounding or floating; it is not treated as
an ordinary signal. ZQ0 requires a 240R ±1% connection to VDDQ. ODT_CA
must have a valid logic level even though LPDDR4X ignores its function.
A per-ball review CSV and deterministic preparation script are saved.
This derivative still needs readable symbol grouping and visual review;
it has not been registered or connected into the appliance hierarchy.

## Readable unit grouping prepared

The audited native derivative is split into seven review units: channel A
(33 pins), channel B (33), VDD1/VDD2 (32), VDDQ (20), two ground banks
(29 each), and reset/ZQ/DNU/NC controls (24). A generation-time equality
check verifies all 200 ball identifiers, resolved names and electrical types
are unchanged. The grouped symbol has a blank footprint and remains an
unregistered review candidate. Rendering and final supply/ground pin
orientation cleanup remain before schematic use; this is not a completed
RAM circuit or land-pattern approval.

## Grouped-symbol render review

Rendered all seven RAM units with KiCad and inspected their fields and
pins. The controls unit initially reserved visible space for hidden NCs;
NCs now use hidden zero-length pins on the body outline and the body
height excludes them. A second enlarged render confirmed the corrected
control unit. Temporary review-sheet generation is reproducible with
render_micron_review.py. Native XML export parses the seven units as one
component with all 200 expected library pins. Power-bank orientation and
land-pattern review remain; the appliance hierarchy is unchanged.

## Native package-grid audit

Rendered and inspected Micron Figure 9, printed page 28. The ZW package
uses 0.8mm column pitch and 0.65mm row pitch, with omitted columns 6/7
and rows L/M. The native footprint is rotated 90 degrees relative to the
top-view ball diagram; all 200 pad centers match the expected grid within
0.006mm, including its 8.8mm and 13.65mm center spans. A reproducible
check verifies every ball identifier and coordinate, rather than only pitch.

Native circular copper pads are 0.35mm. Micron's package drawing states
its post-reflow solder-ball dimensions apply on 0.4mm SMD pads; that is
not a complete fabrication land-pattern specification. Do not silently
approve the native pad size or resize copper alone: solder mask opening,
paste aperture, assembly process and substrate option still need review.
The native courtyard coincides with the nominal 14.5 x 10mm body and
provides no assembly clearance. It has ball Fab marks but lacks a
package-body Fab outline.
The existing blank schematic footprint assignment remains appropriate.

## Power-bank orientation reviewed

The four power/ground review units now use horizontal banks: VDD1/VDD2
and VDDQ pins enter from above, and both VSS banks exit below. Every
ball remains separately identified; no hidden stacking or duplicate ball
numbers were introduced. The generator's full name/type/identity equality
check passes, and KiCad XML export still contains all 200 library pins.
The complete re-render was inspected with reference/value fields clear of
pin numbers. This completes the current symbol orientation review, while
RAM power/bus circuitry and the fabrication footprint remain unfinished.

## RAM draft attached to appliance

Registered the audited grouped model in MemoryDraft with blank footprint
and added ram.kicad_sch as appliance page 12. U901 carries exact MPN
MT53E512M32D1ZW-046 WT:B / C5330500. All 58 ground balls are connected
and verified in the integrated native netlist; twelve permitted floating
DNU balls have no-connect markers. The ten NC pins retain no-connect type.
Supplies, bus, ODT_CA and reset remain visibly unfinished. No RAM operation
or final selection qualification is claimed. The regenerated RAM sheet was
visually reviewed after grid alignment and exact value-field updates.
Integrated capture checks pass for 169 components across 12 sheets; full
ERC reports 645 violations, including newly exposed unfinished RAM pins.

## VDD1 and LPDDR4X ODT control capture

Connected all eight U901 VDD1 balls to existing RK809 BUCK5 VCC_1V8.
The integrated checker verifies these are the only RAM balls on that rail,
so adjacent VDD2 pins are not accidentally joined. Micron's 1.70–1.95V
VDD1 range contains the nominal 1.8V source; aggregate load, tolerance,
local bypass and transient qualification remain incomplete. Startup ordering
must still be checked against the future VDD2/VDDQ supplies.

Grounded ODT_CA_A G2 and ODT_CA_B T2 to satisfy the valid-logic-level
requirement for LPDDR4X. This is specific to the intended LPDDR4X mode;
LPDDR4 topology changes require revisiting the termination policy. RAM
VDD2/VDDQ, reset, ZQ and bus remain unfinished. Rendered the updated
sheet and moved power-unit fields clear of the new VDD1 bank. Native
integration checks pass; full ERC remains incomplete.

## BUCK3 circuit resolved for capture

RK809-5 Rev 2.4 Table 4-4 starts BUCK3 in slot 3, after BUCK5's
1.8V slot 2. PMIC_POWER_CONFIG 0xB9 bit 6 resets to zero, selecting
external feedback. Native pin identities are VCC3=24, SW3=25,
VBUCK3=26 and FB3=27. Do not treat FB3 as a direct output sense pin
or copy the 2.5A BUCK1/2 rating: BUCK3 is rated 1.5A.

Rendered NanoPi R3S LTS sheet 14 and confirmed its LPDDR4/4X divider:
47kR from output to FB3, 120kR from FB3 to ground, with 0.8V feedback.
Nominal output is 1.11333V; independent ±1% resistor corners alone give
1.10713–1.11966V. Both lie within Micron's VDD2 1.06–1.17V range,
but PMIC feedback accuracy, drift, ripple and transient errors remain.
The reference output bank is 22uF + 10uF and input bypass 10uF; its
0.47uH inductor is rated above the buck's load current. Retain these
nominal values using already reviewed capacitor/inductor parts.

Exact divider candidates for capture: Yageo RC0603FR-0747KL / C105579
and RC0603FR-07120KL / C114607, 0603 ±1%, 0.1W. Indexed catalog
entries resolve the exact MPNs; current inventory is not reserved.
Next capture uses VDD_DDR_1V1 for VBUCK3/output, separate DDR_FB for
FB3, and the divider at the sense connection. The later 0.6V VDDQ rail
must rise after VDD2; no complete rail-sequencing proof exists yet.

## BUCK3 and RAM VDD2 captured

Added ddr-power.kicad_sch (page 13): L901 0.47uH XGL4020-471MEC,
C901 22uF CL32B226KAJNNNE, C902/C903 10uF CL31B106KAHNNNE,
and R901/R902 47kR/120kR exact Yageo parts. Input bypass connects
5V_MAIN to ground at VCC3; output uses the reference 22uF + 10uF bank.
U501 pins 24/25/26/27 connect respectively to 5V_MAIN, PMIC_SW3,
VDD_DDR_1V1 and DDR_FB. All 24 RAM VDD2 balls join VDD_DDR_1V1.

Native checks verify the exact switch, feedback, output/load memberships
and capacitor/resistor ground returns. Initial short wire placements crossed
existing PMIC supply wiring; the failing integration checks caught this and
the final placement corrected it before commit. The supply, RAM, PMIC and
root renders were reviewed; root notes moved clear of the title block.
Capture now has 175 components across 13 sheets. Local bypass, 0.6V rail,
DDR bus and load/loop/thermal/sequence qualification remain incomplete.

## ZQ calibration and VDDQ domain captured

Added R903 240R ±1%, Yageo RC0603FR-07240RL / C114613, 0603,
from U901 ZQ0 A5 to VDD_DDR_0V6 as required by Micron Table 5.
All twenty RAM VDDQ balls now join that named domain. Exact native
net membership checks prevent joining VDDQ to VDD1/VDD2 and verify
ZQ0 reaches only the resistor's opposite terminal. The 0.6V source is
still absent, visibly leaving a power-not-driven ERC condition; no label
or PWR_FLAG is used to claim a working supply. ZQ and VDDQ enlarged
renders were visually reviewed. Integrated capture checks pass for
176 components; full ERC reports 533 violations. The drop in ERC count
reflects captured wiring, not completed supply or functional qualification.

## Processor-to-RAM bus mapping prepared

Rendered NanoPi R3S sheet 6 and compared its LPDDR4 channel/function
labels with our audited RK3566 ball table. The reference explicitly forbids
LPDDR4 data-sequence swaps; command/address sequences also cannot swap.
Prepared ddr-bus-map.csv for 65 exact processor/RAM endpoint pairs:
32 DQ, four DMI, eight differential strobe pins, twelve CA, four clock
pins, two CS0, two CKE0 and reset. Both endpoint sets are unique.
DQS t/c map respectively to P/N; DMI maps to the SoC DM function.
No lane, bit or channel permutation is introduced. ODT controls retain the
previous LPDDR4X-specific valid-level policy; single-rank CS1/CKE1 are
not mapped to the RAM's NC balls. Physical bus wiring and unused SoC
pin policy remain the next capture steps.

## Processor-to-RAM bus captured

Connected all 65 mapped signal nets using the exact unswapped ball pairs.
Differential clock and strobe net names now end in P/N for PCB pair recognition.
Native KiCad netlist checks assert exactly one processor ball and one RAM ball
per bus net, with no third endpoint. Processor and integrated capture checks
pass for 176 components. The RAM channel units were spaced for readable labels;
the manual reset control moved clear of the newly connected processor bus.
RAM and reset-control renders were visually reviewed. Full ERC still reports
382 violations: this is partial capture, with DDR rail source, local bypass,
unused processor DDR pins and functional qualification still open.

## Processor DDR power domains captured

NanoPi R3S sheet 6 distinguishes LPDDR4X DDRPHY VDDQ (1.1V) from
VDDQL (0.6V). Connected eight processor balls 1D5/1D6/1D7/1D8/1D9/
1E4/1F4/1G4 to VDD_DDR_1V1 and five 1E6/1E7/1E9/1F5/1G5 to
VDD_DDR_0V6. Exact integrated net memberships include these balls and
the existing RAM domains; the regulator for 0.6V remains absent.
The first placement touched the MCU recovery-control wire; the native
check caught the accidental join. Moving the complete recovery sink
50.8mm right preserves its endpoint assignments and clears the new labels.
Processor and integrated checks pass; enlarged render reviewed. Local
bypass, processor RZQ and unused DDR pin policy are still incomplete.

## Processor DDR local bypass captured

Added C837-C841 on VDD_DDR_1V1: 3x100nF, 4.7uF, 10uF;
C842-C846 on VDD_DDR_0V6: 3x100nF and 2x4.7uF, matching
NanoPi R3S sheet 6 nominal banks. Exact selected Samsung parts are
CL10B104KA8NNNC (0603 X7R), CL10A475KA8NQNC (0603 X5R),
and CL31B106KAHNNNE (1206 X7R), all 25V. Each bank is explicitly
processor-local, separate from regulator output capacitance. Native
checks verify the complete rail memberships, all ground returns and
MPN/rating fields; integrated capture now contains 186 components.
The bypass sheet expanded to A3 and its render was reviewed. Fixed
a pre-existing literal-newline text encoding that prevented standalone
sheet export; both standalone export and integrated checks now pass.
Reference under-package placement remains intent: our larger packages,
especially 1206 10uF, require escape/assembly feasibility review.
Effective capacitance, PDN impedance and regulator stability remain
unqualified. RAM-local bypass is still separate unfinished work.

## Processor DDR calibration captured

Added R904 120R ±1%, Yageo RC0603FR-07120RL / C114640,
0603 0.1W 75V, from U801 DDR_RZQ ball 1F3 to VDD_DDR_1V1.
This follows the explicit LP4/LP4X pull-up note on NanoPi R3S sheet 6.
It is separate from Micron ZQ0's 240R resistor to VDD_DDR_0V6.
DDR_VREFOUT ball 1H3 is explicitly no-connect, matching that reference.
Native processor/integrated checks verify the exact calibration endpoints
and supply membership; enlarged pin and supply renders reviewed.
Capture now contains 187 components. Other unused DDR outputs, RAM-local
bypass, the 0.6V source and electrical/boot qualification remain open.

## Unused processor DDR outputs made explicit

For the selected single-rank part, mark LPDDR4 CKE1 and CS1n outputs
unused: 1A2/1C3 and 1A5/A3 respectively. LPDDR4X ignores ODT_CA
while requiring valid RAM input levels (our RAM inputs remain grounded),
so the processor's four ODT outputs 1A4/1C2/A10/E2 also remain unused.
Together with DDR_VREFOUT 1H3 these nine pins have explicit no-connect
markers. Native checks ensure none joins another endpoint; marker coordinates
are checked against the audited native pin positions. Enlarged render reviewed.
Firmware must initialize the selected single-rank LPDDR4X topology. This
capture policy does not establish loader compatibility or physical training.

## RAM-local bypass reference inventory

Visually reviewed NanoPi R3S LTS 2411 sheet 7 and prepared
ram-local-bypass-plan.csv with fifty distinct capacitor references C905-C954:
- VDD1: 2x10uF plus 6x100nF (C3848-C3851 and C3823-C3826).
- VDD2: 22uF plus 3x10uF plus 16x100nF (C3801-C3820).
- VDDQ: 22uF plus 3x10uF plus 18x100nF
  (C3828-C3846, C3854, C3821, C3822).

These are RAM-local banks, additional to BUCK3 output capacitors and
processor-local DDR bypass. Inventory is a capture plan, not yet fitted.
The reference uses 0201 high-frequency capacitors and 0402/0603 bulk
parts; our selected larger parts cannot be treated as equivalent physical
PDN performance. Package, bias, placement and impedance review remains.
Reference VDD1 is ferrite-fed VCCA1V8_PMU; our current RAM VDD1 is
BUCK5 VCC_1V8. Review source loading and sequencing before introducing
the reference bead or changing the source rail.

Sheet 7 also identifies a SY8089A 0.6V buck, 2.2uH inductor,
2kR/100kR feedback for LPDDR4X, and 20kR/100nF enable network
driven by VCC1V8_DDR. Capture requires exact regulator variant/model,
feedback accuracy, load and sequence checks. Its generic dual-rank RAM
symbol is not authority to reconnect our audited single-rank NC balls.

## RAM-local bypass captured

Captured all fifty planned capacitors C905-C954 directly in ram.kicad_sch,
with separate visible banks on VCC_1V8, VDD_DDR_1V1 and VDD_DDR_0V6.
Used the already selected exact Samsung 25V X7R parts: 100nF
CL10B104KA8NNNC/0603, 10uF CL31B106KAHNNNE/1206 and 22uF
CL32B226KAJNNNE/1210. Each capacitor records its reference-design
source designator. Native checks verify all fifty rail and ground
endpoints, values, MPNs and ratings, while retaining the exact processor/
RAM bus assertions. Standalone RAM SVG exported and visually reviewed.
Capture now has 237 components. Larger packages remain a placement/PDN
qualification gap versus the reference 0201/0402/0603 implementation;
nominal capture is not physical equivalence. The 0.6V regulator remains
absent, and RAM VDD1 source/filter/sequence review is still required.

## Exact 0.6V regulator variant checked

Archived Silergy-authored AN_SY8089/A Rev 0.9A from LCSC C78988.
Ordering table explicitly lists SY8089AAAC, SOT23-5; older 1MHz part
with 2.7-5.5V input, 2A nominal continuous capability and -40..85C
ambient range. Do not conflate it with current SY8089A1AAC/SY20149A1AAC
1.5MHz variant. Pinout visually reviewed: EN1, GND2, LX3, IN4, FB5.
Input requires at least 10uF ceramic locally.

Reference 2kR upper /100kR lower gives 0.612V nominal. Combining
0.588..0.612V reference limits with independent +/-1% resistors gives
0.5995275..0.6244873V before FB leakage, ripple and dynamic effects.
This fits the Micron static 0.57..0.65V window but does not prove the
complete PDN or processor load limits. FB leakage spec +/-50nA adds
about 0.1mV at this divider impedance. Limits table is stated at
VIN=5V/TA=25C; do not assume full-temperature accuracy from this alone.

EN rising threshold is listed 1.5V minimum; no guaranteed maximum
is stated here. The reference 20kR/100nF network gives nominal 2ms RC
and crosses 1.5V about 3.58ms after an ideal 1.8V step. Typical soft
start is 1.2ms. Neither typical timing nor this incomplete threshold
spec proves VDD1/VDD2/VDDQ order at corners. Disable/undervoltage
output decay and PMIC sequencing also remain to verify before release.
Native symbol acquisition, exact inductor and circuit capture remain next.

## Native SY8089 model audited

Archived EasyEDA C78988 native symbol and footprint via easyeda2kicad
1.0.1. All five symbol identities match AN_SY8089/A page 2. Prepared
an unregistered derivative with EN/FB input, IN/GND power-in and LX
power-out; no production footprint assigned. The native footprint remains
a candidate pending dimensional review. No new datasheet-derived pin
table or speculative symbol identities were introduced.

Application-note page 7 recommends 10kR..1MR for both divider resistors,
while NanoPi uses a 2kR upper resistor. That reference exception should
be retained explicitly or reviewed with its 100pF feed-forward network
before choosing a different divider. Page 8 states EN >1.5V turns on,
EN <0.4V turns off, and recommends a 1MR pull-down if the driving
source becomes high impedance in shutdown. Review BUCK5 discharge and
IN persistence; the reference RC alone does not establish the off state.
Output-capacitor recommendation is >22uF X5R or better; verify effective
capacitance of the reference 2x22uF+10uF bank and RAM-local loading.

## 0.6V package and inductor audit

Visually reviewed Silergy AN_SY8089/A page 9 recommended land pattern:
0.95mm pitch, 2.40mm row-center span, pads 0.55mm wide by 0.80mm
long. Native footprint (180-degree rotation relative to stock KiCad)
has matching pin ordering and pitch, but 2.60mm row span and
1.10x0.60mm copper pads. Its courtyard +/-0.80x+/-1.45mm excludes
pads extending to +/-1.85mm; it is not a production-ready courtyard.
Also retains a temporary /tmp model path and lacks a Fab body outline.
Stock KiCad SOT-23-5 has 2.275mm row span and 1.325x0.60mm pads,
so it is not an exact manufacturer-recommended land-pattern substitute.
No footprint assigned or modified; review manufacturer pattern and
assembly requirements before production assignment.

Exact reference inductor WPN201610H2R2MT / C97005 indexed as Sunlord
2.2uH +/-20%, 1.45A rated, 2.15A saturation, 170mR DCR. Supplier
values require manufacturer temperature/derating validation. Do not infer
a qualified 2A rail from the regulator rating when this inductor is used.
At 0.612V output, 3.3V input and nominal 1MHz, ripple estimate is
0.227A p-p with 2.2uH, increasing to 0.283A at -20% inductance;
this excludes frequency tolerances and inductance loss with current.
Select against the combined processor/RAM worst-case VDDQ load and
regulator fault current before freezing L902. A larger existing-footprint
inductor may be appropriate; XGL4020-222MEC had no exact JLC DB hit,
which is not proof of manufacturer unavailability.

## VDDQ regulator/input draft captured

Registered audited native SY8089AAAC as DdrPowerDraft and added U902
to the DDR power sheet, with blank footprint. IN4 joins 3V3_MAIN;
GND2 joins ground; C955 10uF CL31B106KAHNNNE/1206 provides local
input bypass. EN1, LX3 and FB5 have distinct draft net labels with no
other endpoints until their circuits are captured. Thus U902 does not
yet drive VDD_DDR_0V6. Explicit sheet note identifies the missing
output/feedback/enable network. Native integration checks pass for
239 components; enlarged render reviewed. No production readiness claim.

## VDDQ enable network captured

R907 20kR RC0603FR-0720KL/C105575 connects VCC_1V8 to
DDR_VDDQ_EN; C960 100nF CL10B104KA8NNNC/C1590 shunts EN
to ground, following reference values. Added R908 1MR
RC0603FR-071ML/C105578 pull-down per Silergy's shutdown guidance
for high-impedance driving sources. Both resistors 0603 +/-1%,
0.1W/75V; capacitor 0603 X7R 25V. Native checks verify exact EN
endpoint membership and rail/ground returns; enlarged render reviewed.
Capture now 242 components.

Nominal resistor divider makes the final EN level 1.7647V at 1.8V
source, neglecting EN leakage. Charging time constant is 1.9608ms
(20kR || 1MR with 100nF), reaching 1.5V around 3.72ms after an
ideal source step. With its source open the 1MR pull-down gives
100ms nominal time constant, so this is not a fast-off guarantee.
When source is actively discharged, its impedance changes decay.
Leakage, capacitor bias/tolerance, source ramp/discharge and input
persistence require qualification; nominal timing is not sequencing proof.
Switching output and feedback circuit remain absent.

## VDDQ feedback network captured

Added R905 2kR RC0603FR-072KL/C105576 upper and R906 100kR
RC0603FR-07100KL/C14675 lower, both 0603 +/-1%, 0.1W/75V.
C959 100pF CL10C101JB8NNNC/C14858, 0603 C0G 50V +/-5%,
bridges output to feedback in parallel with R905. This retains
NanoPi sheet 7 values and the recorded 2kR recommendation exception.
Native checks verify exact FB endpoint set U902.5/R905.2/R906.1/
C959.2, both output endpoints and lower ground return, plus MPNs.
Enlarged render reviewed; integrated capture has 245 components.
No inductor/output bank has been added yet: VDD_DDR_0V6 remains
unpowered. Loop, load, ripple, thermal and sequencing qualification
still required; 0.612V is nominal, not a guaranteed complete rail.
