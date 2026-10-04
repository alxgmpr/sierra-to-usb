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
