# RK3566 processor clock — selection in progress

RK3566 hardware guide 2.1.1/Table 2-1 requires 24 MHz, ±20 ppm,
operation from −20 to +80 °C, and maximum 40 Ω ESR. The reference
uses a 22 Ω output-series resistor and 1 MΩ feedback resistor, with
C0G/NP0 load capacitors chosen for the exact crystal. Its illustrated
18 pF capacitors are explicitly not universal. A four-terminal crystal
with the two cover terminals grounded is recommended.

## Candidate boundary

Epson X1E0000210129 / JLC C255917 is a candidate, not selected.
The 2026-10-04 indexed record reports 24 MHz, 12 pF load, ±10 ppm
initial tolerance, −40 to +85 °C, 40 Ω ESR, SMD3225-4P and 10,553
parts; indexed stock is not reserved. The distributor record omits temperature-frequency tolerance. The exact
manufacturer record obtained below resolves it as ±20 ppm.

The archived manufacturer FA-238/TSX-3225 brief distinguishes the
families: TSX-3225 specifies 40 Ω maximum from 21 through 50 MHz,
whereas FA-238 specifies 60 Ω at 24 MHz. TSX-3225 permits 200 µW
maximum drive and recommends 10 µW. Cover pins 2 and 4 ground;
resonator terminals are 1 and 3. These are family data, not proof of
the exact candidate's frequency-temperature option.

Primary source: https://download.epsondevice.com/td/pdf/brief/FA-238_en.pdf

## Before capture

Obtain the exact part specification, including temperature frequency
tolerance and aging budget. Interpret the host ±20 ppm requirement
conservatively across initial tolerance, temperature, load error and aging
until a manufacturer timing budget establishes otherwise. Audit the native
model and standard footprint against the manufacturer geometry. Choose
load capacitors using CL=C1*C2/(C1+C2)+Cstray; for equal capacitors,
C=2*(CL−Cstray). Do not silently substitute estimated PCB stray capacitance
for measured values. Startup margin and drive power require prototype
verification at voltage/temperature corners. No clock parts have yet been
added to the appliance schematic.

## Exact manufacturer parametric evidence, 2026-10-04

The official search page loads `ps_common.js` and `ps_xu.js`. Those
scripts identify `https://download.epsondevice.com/td/ps/xtal_mhz.json`
as their product data source. The original JSON is archived with a hash
in sources.json. This is exact manufacturer data, not a distributor inference.

| Exact Epson part | Initial ppm | Temperature ppm | Temperature °C | CL pF | ESR max Ω | First-year aging ppm |
|---|---:|---:|---|---:|---:|---:|
| X1E0000210129 | ±10 | ±20 | −40 to +85 | 12 | 40 | ±1 |
| X1E0000210697 | ±10 | ±10 | −20 to +85 | 20 | 40 | ±1 |
| X1E0000211158 | ±10 | ±10 | −20 to +85 | 10 | 40 | ±1 |

All three are fundamental TSX-3225, 3.2×2.5×0.6 mm, 200 µW
maximum drive. JLC searches returned no indexed exact match for
X1E0000210697 or X1E0000211158. This is not proof that another
assembler or distributor cannot supply them. No order was placed.

Under the conservative total-error interpretation used here, X1E0000210129
has a 31 ppm worst-case initial+temperature+first-year sum before load
error. The tighter two have 21 ppm before load error. Neither sum proves
the total ±20 ppm condition. The Rockchip clock tolerance table does not
explicitly separate initial and temperature error; obtain clarification or
an exact tighter oscillator/crystal budget before claiming closure. A
specified total-error 1.8 V active oscillator is also an allowed host option,
but requires its own startup/power-sequencing check. No schematic
clock component was selected on the strength of incomplete data.
