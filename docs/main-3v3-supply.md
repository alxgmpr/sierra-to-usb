# Main 3.3 V supply candidate

MP2143DJ-LF-Z (MPS; TSOT23-8; LCSC C43427) is the candidate for
5V_MAIN to 3V3_MAIN. NanoPi R3S LTS 2411 sheet 17 uses MP2143DJ,
1 uH, 200 kOhm / 44.2 kOhm feedback and nominal 10 uF input/output.
The reference overview suggesting a direct 12 V input is not the circuit.
This regulator must not connect to the isolated 12 V intermediate rail.

Manufacturer Rev 1.07 specifies 2.5–5.5 V input, up to 3 A output,
0.600 V feedback and TSOT23-8. The reference divider gives
0.6*(1+200/44.2) = 3.3149 V nominal. Using 1% resistor corners and
±2% feedback over -40 to +85 C gives approximately 3.196 to 3.438 V,
before ripple, transient and layout drops. The all-temperature guarantee
through +125 C needs clarification; do not extend the ±2% figure.

Pin audit from manufacturer pages 2–3:

| Pin | Name | Capture requirement |
|---|---|---|
| 1 | PG | Internal 500 kOhm pull-up to VIN; high approaches 5 V. Never directly connect to the 3.3 V supervisor. |
| 2 | VIN | 5V_MAIN; input bypass and overshoot must keep <=5.5 V operating. |
| 3 | SW | External inductor input. |
| 4 | PGND | Switching return. |
| 5 | OUT | Output sensing; connect after inductor. |
| 6 | AGND | Quiet feedback return; layout connection per manufacturer. |
| 7 | FB | Divider midpoint; output bank and divider still to capture. |
| 8 | EN | Low <=0.4 V; high >=1.2 V. Main-power control and boot/shutdown sequence still to define. |

3 A is a regulator rating, not proof of appliance load/thermal margin.
Typical soft start is 1.3 ms and power-good delay 110 us. Reference
output capacitance cannot be copied without DC-bias and load review.
Inductor exact MPN, saturation/current-limit margin, capacitors,
feedback resistors, PG translation and schematic remain unfinished.

Primary sources:
- https://www.monolithicpower.com/media/document/MP2143_r1.07.pdf
- https://www.monolithicpower.com/en/products/power-management/switching-converters-controllers/step-down-buck/converters/mp2143.html
- Archived hardware/reference/nanopi-r3s-lts-2411.pdf sheet 17.

Catalog lookup on 2026-10-03 identified C43427, extended assembly library,
2047 indexed stock. This is neither reserved nor real-time stock proof.
The manufacturer PDF was read through web PDF extraction; direct download
returned non-PDF content and was rejected rather than archived as a PDF.

## Exact feedback candidates and corner correction

Upper: Yageo RC0603FR-07200KL, 200 kOhm, C105574. Lower:
Yageo RC0603FR-0744K2L, 44.2 kOhm. Both are manufacturer-verified
0603, 1%, 100 ppm/C, 100 mW, 75 V. Exact manufacturer spec sheets
are archived with hashes. The lower part was not found in the indexed
JLC database; its assembly availability remains unresolved.

The earlier 3.196–3.438 V estimate omits resistor temperature drift.
Conservatively summing initial tolerance and opposing 100 ppm/C drift
from 25 C, then applying +/-2% regulator feedback, gives:

| Temperature | Lower bound | Upper bound |
|---|---|---|
| -40 C | 3.1623 V | 3.4741 V |
| 25 C | 3.1959 V | 3.4372 V |
| 85 C | 3.1648 V | 3.4713 V |

These are calculated component corners, not measured regulation bounds.
No guaranteed maximum FB bias current was established; the datasheet
10 nA figure is typical. Dynamic errors remain additional. Raw calculation
inputs and results are in hardware/reference/main-3v3-divider-corners.json.

## Preferred precision divider

Use RT0603BRD07200KL (200 kOhm, C728585) and RT0603BRD0744K2L
(44.2 kOhm, C861410) for the capture. Manufacturer exact spec sheets
confirm 0603, 0.1%, 25 ppm/C and 0.1 W at 70 C; both were found in the
indexed assembly catalog. These replace the thick-film candidates above
for this feedback circuit. Nominal voltage stays 3.3149 V.

| Temperature | Lower calculated bound | Upper calculated bound |
|---|---|---|
| -40 C | 3.2347 V | 3.3958 V |
| 25 C | 3.2433 V | 3.3868 V |
| 85 C | 3.2354 V | 3.3951 V |

The 3.3 V +/-5% comparison window is 3.135–3.465 V. These component
corners fit that comparison window, but it is not an established common
requirement for every downstream device. Feedback bias, aging, ripple,
transients and load drops remain outside this calculation.

## Native symbol source audit

Installed easyeda2kicad v1.0.1 exported C43427 successfully after CSE
returned no model for both exact MPN and MP2143DJ. Raw symbol and footprint
are archived as mp2143-easyeda-candidate files. All eight source pin names
and numbers match manufacturer Rev 1.07. All source electrical types are
unspecified and therefore must be corrected before registration; proposed
types are recorded in hardware/pinmaps/mp2143.csv. In particular, OUT is
the sense input and SW is the power output. Native library registration,
KLC/render review and footprint dimensions still remain.

## Registered regulator symbol

Recovery:MP2143DJ-LF-Z is now registered with eight explicitly typed pins.
VIN is on top, PG/SW on the right, EN/FB/OUT on the left and both returns
on the bottom. Native SVG was inspected. check_mp2143_symbol.py verifies
all eight names/types and official TSOT-23-8 pad-number parity. Package
dimensions, KLC review and regulator circuit capture remain unfinished.

## Inductor choice

Prefer Coilcraft XGL4030-102MEC (1 uH +/-20%, C6336766) over
XGL4020-102MEC for this 3 A regulator. Manufacturer data at 25 C:
7.2 mOhm maximum DCR; 10/20/30% inductance drop at 4.8/7.6/10.3 A;
RMS 10.8/13 A for 20/40 C rise. The catalog 10.3 A saturation number
is the 30% drop point, not the near-nominal-inductance rating.

Using 5.5 V input, 3.3958 V output, 0.9 MHz (-25% frequency),
0.8 uH initial minimum and an additional 10% bias drop gives
2.005 A ripple and 4.002 A peak at 3 A load. This is below
the 4.8 A 10% drop point at 25 C and the regulator 4.2 A minimum
current-limit figure, with little current-limit margin. XGL4020-102MEC
reaches 10% drop at 3.8 A and does not support the same assumption.
Hot saturation, fault current-limit upper bound, regulator thermals and
actual rail load remain open. Manufacturer footprint dimensions and
3.1 mm maximum height need checking before capture.

Primary source: https://www.coilcraft.com/en-us/products/power/shielded-inductors/molded-inductor/xgl/xgl4030/xgl4030-102/
Catalog C6336766 had 380 indexed parts on 2026-10-03; not reserved stock.

## Captured standalone draft

hardware/main3v3.kicad_sch now contains U601, L601, C601–603 and
R601–602 with exact MPN fields. Native netlist verifies separate switch
node, OUT sensing after L601 and the divider midpoint at FB. Initial SVG
review caught left-label overlap; label justification was corrected.
Input is one 22 uF capacitor and output two 22 uF capacitors; sizing
remains provisional pending loop and effective-capacitance review.
Enable and 5 V PG are explicit unfinished boundaries. This standalone
sheet is not yet joined to the appliance root and is not ERC-qualified.
Reproduce with python3 hardware/tools/build_main3v3.py.

The main regulator draft is now attached to the appliance root. Global
5V_MAIN/3V3_MAIN connections are native-netlist checked against the PMIC
input pins; recovery supply separation is asserted. The earlier standalone
integration limitation is superseded. Enable and PG remain unfinished.

## Main 3.3 V enable capture

R603 RC0603FR-0720KL (20 kOhm, C105575) from 5V_MAIN and
R604 RC0603FR-0710KL (10 kOhm, C98220) to ground now drive U601
EN pin 8. This follows the NanoPi MP2143 enable network and avoids
using a PMIC output to enable the rail supplying PMIC LDO inputs.
Nominal divider voltage is 1.667 V at 5 V, versus the 1.2 V enable-high
threshold. With +/-1% and 100 ppm/C over -40 to +85 C, unloaded
minimum at 4.75 V is approximately 1.549 V. Manufacturer internal
1 MOhm EN pulldown slightly lowers this (its tolerance is unspecified).
EN leakage/tolerance guarantee and startup ramp still need closure.
This does not define upstream 5 V generation or supervisor cold-cycle control.
Native appliance assertions verify U601:8/R603:2/R604:1 only, top
resistor on 5V_MAIN, and 88 total components. PG translation remains open.

## Captured power-good translation

U602 SN74LVC1G17DBVR (TI C7836, SOT-23-5) now buffers the MP2143
PG signal. VCC and C604 100 nF use independent recovery +3V3, while
input A tolerates up to 5.5 V per TI datasheet Rev Y. Pin mapping matches
the official 74xGxx:74LVC1G17 symbol: 1 NC, 2 A, 3 GND, 4 Y, 5 VCC.
R605 10 kOhm to 5V_MAIN strengthens the MP2143 internal 500 kOhm
pull-up; R606 100 kOhm to ground prevents an undriven high when main
5 V is absent. With only the internal pull-up, the buffer worst-case
5 uA input leakage could consume 2.5 V of high-level margin.

MAIN3V3_GOOD is currently a local output boundary, not yet assigned
to the supervisor. Native appliance assertions check exact PG net
membership and U602/C604 recovery-supply connections; 92 components.
Full voltage/threshold corners, visual review, NC/footprint checks and
MCU input integration remain required before this interface is closed.
TI primary datasheet archived with SHA-256 in sources.json.

## Supervisor PG integration and limits

MAIN3V3_GOOD now joins U602 output pin 4 to supervisor PB5/pin 44.
Native appliance checker asserts exactly those endpoints. Render review
caught overlap at the buffer supply text and regulator sense label; corrected
render inspected. Recovery-only ERC gains another isolated boundary warning
until viewed through the complete appliance hierarchy; no exclusion is added.

At 5.5 V and minimum 10 kOhm pull-up (including 1% and 100 ppm/C
over -40 to +85 C), PG sink loading stays below 0.56 mA, versus
MP2143 specification 0.4 V at 1 mA. High-level divider estimate at
4.75 V, opposing resistor corners and 5 uA TI input leakage remains
above 4.2 V. TI guarantees input operation through 5.5 V. The table
provides thresholds at 3.0/4.5 V rather than the exact 3.3 V supply;
full intermediate-supply proof and MP2143 off-state PG leakage remain
open. No physical signaling or firmware behavior is claimed.
