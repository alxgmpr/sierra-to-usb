# Isolated 12 V to main 5 V stage — selection open

TPS56637RPAR is a source-audited candidate (TI, RPA 10-pin 3 x 3 mm
HotRod VQFN, C841386). It accepts 4.5–28 V and is rated 6 A. It must
use the isolated 12 V intermediate, not raw PoE. Manufacturer datasheet
Rev A is archived and hashed. Its Figure 17 is a 5 V/6 A reference.

Table 4 recommends 3.3 uH and 20–100 uF **effective** output capacitance
(30 uF typical) at 5 V, with 73.2 kOhm / 10 kOhm divider. Nominal
output is 4.992 V. Optional feed-forward is 100–220 pF with 20 kOhm
series resistance; do not assume it is mandatory. Output-bank sizing
must include all downstream input caps and reflected startup loads.

A simultaneous-rating scenario gives 35.412 W or 7.082 A at 5 V:
CPU 1.025 V/6 A, logic and GPU each 0.9 V/2.5 A, buck5 1.8 V/2.5 A,
main 3.3 V/3 A and illustrative DDR 1.1 V/1.5 A, each at assumed 85%
efficiency; add 4 W for two 400 mA LDO inputs directly from 5 V.
Main 3.3 V-fed LDO loads are included in its 3 A scenario, not added twice.
This is not actual processor or memory demand, and 85% is not guaranteed.
It shows 6 A cannot cover all stated downstream ratings concurrently.

Do not freeze this regulator before domain load/peak/sequence budgeting.
Evaluate an 8 A stage if the verified workload requires it; do not silently
limit downstream scope to make a 6 A circuit pass. Modem supply routing
and isolated PoE peak allocation remain separately unresolved. Main 5 V
must stay within RK809/MP2143 5.5 V operating limits including transients.
No upstream regulator symbol or circuit is yet captured.

Source: https://www.ti.com/lit/ds/symlink/tps56637.pdf, sections 8.2/8.2.2.
Catalog C841386 showed 5915 indexed parts on 2026-10-03, not reserved.
Raw scenario: hardware/reference/main-5v-rating-scenario.json.

## Preferred 8 A candidate and native source

TPS56837RPAR (TI, C22428366) is the preferred stage candidate for
capture while the actual peak budget remains open. Manufacturer Rev B
(SLVSGM3B, January 2024) is archived. It retains RPA 10-pin HotRod
package, 4.5–28 V input, and adds selectable frequency/current limit
and adjustable soft start. The source catalog incorrectly says through-hole;
manufacturer RPA package is surface mount. C22428366 has 2306 indexed
units, not reserved inventory.

The installed EasyEDA converter exported all 10 pins, whose names and
numbers match manufacturer Table 4-1. Raw symbol and footprint archived;
correct electrical types recorded in hardware/pinmaps/tps56837.csv.
Footprint source name refers to TPS56838RPAR; dimension/pad audit is
required before using this shared family geometry.

At 500 kHz and 5 V, manufacturer table recommends 3.3 uH and a
nominal 22 uF bank (one minimum, two typical, ten maximum), based
on specific Murata parts/derating described in the table notes. This differs
from the older TPS56637 effective-capacitance table and must be checked
directly. Current-limit and MODE selection, exact inductor, capacitors,
upstream supervisor enable and full load/thermal qualification remain open.
Source: https://www.ti.com/lit/ds/symlink/tps56837.pdf.

## Imported footprint audit

Inspected TI RPA0010A package and land-pattern drawings, PDF pages
31–32 (drawing 4224047/A 01/2018). Imported model is rotated relative
to TI view, which is permissible, but SW pad 6 is 1.8 x 0.25 mm rather
than the recommended 1.7 x 0.25 mm. Its courtyard is essentially the
3 x 3 mm body boundary and does not enclose all pad copper; it also
references an absent temporary-directory 3D model. VIN pad 8 uses a
custom comb polygon whose copper and paste need separate review.
These prevent direct registration as a fabrication-ready footprint.

Generate a local RPA0010A footprint from the TI land pattern, preserve
10 logical pins (no extra exposed-pad number), and check the large
VIN/PGND copper plus manufacturer stencil example separately. Do not
substitute a generic QFN-10 with a central exposed pad. Circuit capture
can proceed after local footprint/symbol review; assembly and thermal
qualification remain independent.

## Typed regulator symbol

Recovery:TPS56837RPAR is registered with ten unique pins and audited
electrical types. Native symbol render inspected. check_tps56837_symbol.py
verifies the manufacturer-reviewed table. Footprint field intentionally blank
pending RPA geometry review. No circuit is represented by this symbol alone.

## Control values selected for capture

Use the approved manufacturer reference-design package policy. MODE
30.1 kOhm (RC0603FR-0730K1L, 0603, 1%) selects 500 kHz and the
higher valley-current-limit option: 8 A minimum, 9.6 A typical,
11.1 A maximum. These are valley limits, not guaranteed load current
or acceptable inductor peak current. MODE is latched at startup.

The reference feedback pair is 73.2 kOhm / 10 kOhm; prefer
RT0603BRD0773K2L and RT0603BRD0710KL (0603, 0.1%, 25 ppm/K).
Nominal output is 4.992 V. The manufacturer's full-temperature feedback
limits are 0.591–0.609 V, rather than the 25 C ±1% figure. With opposing
0.1% resistor tolerances alone, output spans approximately 4.908–5.076 V.
Temperature coefficient, bias, ripple and transient effects remain additional
terms; this calculation does not close the downstream 5.5 V ceiling.

Reference SS capacitance is 47 nF. With typical 6 uA charge current
and 0.6 V reference, the nominal ramp is 4.7 ms (Equation 1). Exact
capacitor selection and minimum/maximum startup timing remain open.
No control circuit has been captured yet; footprint review is pending.
Source: archived tps56837.pdf, Sections 5.5, 6.3.1, 6.3.3 and Figure 7-1.

## Reference inductor and distributed capacitance audit

Archived current Würth 744325330 datasheet revision 004.001 (2025-02-06).
This is the 3.3 uH reference inductor, tolerance ±20%, DCR 5.9 mOhm
±10% at 20 C. Its 15 A typical saturation figure permits 30% inductance
loss; the 10% loss figure is only 5 A typical. Rated inductance is
2.4 uH typical at 12 A. The updated sheet specifies 12 A at 50 K
temperature rise, with application-dependent PCB cooling. Do not treat
the reference design's older 9.7 A heating figure as the current sheet.

At 13.2 V input, 4.992 V output, 8 A load and typical 500 kHz,
3.3 uH gives 1.88 A peak-to-peak ripple and 8.94 A peak current.
Using 1.848 uH as an illustrative compounded 20% tolerance and
30% bias loss gives 3.36 A ripple and 9.68 A peak. At the maximum
11.1 A valley-limit figure the latter ripple implies 14.46 A peak,
close to the 15 A typical 30% drop figure. This is sensitivity analysis,
not a proven minimum-inductance or hot/fault bound. The datasheet gives
500 kHz typical without minimum/maximum limits. Keep the exact inductor
selection open until bias/temperature and overload behavior are checked.

Existing main-5-V-connected capacitors already include C504, C508,
C512, C516, C533 and C601, each 22 uF nominal, plus C514 1 uF.
Thus the regulator sees at least 133 uF distributed nominal capacitance
before its local output bank and missing CPU/DDR inputs. TI's two
reference 22 uF Murata capacitors give 35 uF effective at 5 V; the
recommended maximum ten-part bank must be compared using effective
capacitance, with interconnect effects included. A local two-part bank
would bring the current nominal total to 177 uF. Do not qualify the
regulator using its local output capacitors alone. TI allows greater
capacitance only with carefully tuned feed-forward compensation.

Source: manufacturer 744325330.pdf and TPS56837 Sections 7.2.2.3–4;
sensitivity inputs/results in main-5v-inductor-sensitivity.json.

## Native control capture

main5v.kicad_sch is attached to the appliance root. U701 and R701–703
implement the reviewed MODE and feedback settings; AGND/PGND share
the electrical return. Four exact-MPN components increase the appliance
total to 96. Native XML checks verify the FB node, MODE resistor, ground
returns and global 5V_MAIN divider connection. Render inspected after
moving the regulator fields clear of its VIN/BOOT pin numbers.

The six other regulator pins remain visibly unconnected. No placeholder
inductor or false 5 V power source was added, and the footprint stays blank
pending review. This is a partial control capture, not a working power stage.

Full appliance ERC after this partial capture: 65 violations (45 unconnected
pins, 11 undriven signal pins, 9 undriven power pins). No ERC exclusions
or flags were introduced to mask unfinished circuits.

## Bootstrap captured

C701 is Samsung CL10B104KA8NNNC, 100 nF/25 V X7R in 0603,
connected directly between U701 BOOT pin 7 and SW pin 6. TI Section
7.2.2.5 requires 100 nF ceramic, X5R or better, rated at least 10 V.
The appliance now contains 97 components. Native netlist checks verify
that neither bootstrap terminal is grounded or tied directly to 5V_MAIN.
Physical placement and the remaining power stage are still unfinished.
