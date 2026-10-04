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
