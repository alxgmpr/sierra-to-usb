# Compact buffered power — P0 engineering review

2026-09-04. **Candidate captured, not electrically qualified or ready for fabrication.** Root KiCad files remain reference material. The original capacitor-only sheet is preserved in `compact/reference/energy-storage-initial.kicad_sch`.

## Decision and demonstrated operating principle

Capture TPS259470L → LTC3128 → two series Eaton HV1020 cells → TPS62816-Q1. The modem regulator connects directly to the storage bus. There is no USB bypass to the modem and no outage-triggered transfer switch. The LTC3128 continues to deliver its current-limited output while the capacitor supplies the difference between converter output and load demand. This behavior is explicitly described in **Pulsed Output Loads**, printed page 15 of the [LTC3128 datasheet](https://www.analog.com/media/en/technical-documentation/data-sheets/3128f.pdf). This establishes the operating principle, not this implementation's transient performance.

LTC4041 and conventional LTC3350 backup reference circuits were rejected for this topology: reducing charge current alone does not constrain an externally connected load, and their ordinary backup transitions do not establish assistance to a live current-limited source. LTC3128 is a useful prototype candidate, but its tapered charging and limited voltage window cause the failures below. **Do not freeze this controller/bank combination as the final all-modem solution.**

## Verified modem scope

| Exact documented module | Power requirement found | Consequence |
|---|---|---|
| EM9190, without mmWave antenna modules | 3.135–4.4 V; 3 A peak, 2.3 A continuous; 100 mV p-p supply ripple | Applicable initial load envelope. Pulse duration still must be obtained/measured. |
| EM9190 with mmWave modules | 5 A peak, 4 A continuous | 4 A × 3.394 V = 13.58 W output; conservative 5 V/3 A chain cannot sustain this. Excluded from present qualification. |
| RM520N-GL, Hardware Design V1.0 | 3.135–4.4 V, nominal 3.7 V; supply capability at least 3 A continuous | 10.18 W at selected 3.394 V exceeds the conservative 9.39 W budget below. No separate verified maximum peak established. |
| RM551E-GL | Manufacturer brochure identifies module, but applicable hardware pin/current specification not obtained | No compatibility claim. RM50xQ 3 A/4 A figures are not applicable evidence. |

Sources: [Sierra EM919x PTS 41113174 Rev5, table 3-2, printed p28](https://cdck-file-uploads-us1.s3.dualstack.us-west-2.amazonaws.com/flex025/uploads/sierrawireless/original/2X/1/1bd7a25d38d0c99ff10fe2000bcd4a6c2ee9dafa.pdf), [Quectel RM520N-GL Hardware Design V1.0, p27](https://forums.quectel.com/uploads/short-url/1zkjPRnxF5BZ2woox386baCZx4g.pdf), [Quectel product brochure V8.5](https://www.quectel.com/content/uploads/2026/01/Quectel_Product_Brochure_V8.5_2026.pdf). These are manufacturer-authored documents; two are hosted on vendor forums. A later Sierra revision must be checked before release.

EM9190 uses VCC pins 2, 4, 24, 38, 68, 70, 72, 74. RM520N-GL uses 2, 4, 70, 72, 74. Sierra USB boot/control pins 20 and 22 must not be indiscriminately connected to Quectel reserved pins. Exact regional suffixes, hardware revisions and vendor-profile isolation remain gates. RM551E-GL brochure lists four sub-6, two GNSS and three mmWave interfaces; that is not a pin/connector mapping and does not establish that four SMA paths suffice. Firmware and macOS networking remain unverified.

## Captured component settings

- **USB input:** TPS259470LRPWR, reverse-current blocking, OVLO 340 kΩ/100 kΩ = nominal 5.28 V, 10 nF dV/dt ≈ 0.2 V/ms. Input 1 µF/50 V and SMBJ6.0A are included. TVS clamping alone does not protect a 5.5 V-rated downstream controller; verify eFuse overshoot and OVLO response. [TI datasheet](https://www.ti.com/lit/ds/symlink/tps25947.pdf).
- **Normal average current:** LTC3128 RPROG 4.02 kΩ ±0.1% gives 11/4.02 = 2.736 A; CPROG 390 pF approximates 1600/RPROG. Applying a conservative ±4.5% current allowance, resistor tolerance and 50 mA for auxiliary/CC/data circuitry gives a 2.912 A upper budget. Actual CC/data demand must fit that reserve. This is average regulation; do not interpret it as a zero-duration 3 A peak clamp.
- **Fault current:** eFuse RILM 1.02 kΩ gives nominal 3.27 A with approximately ±10% threshold allowance. This is intentionally above normal LTC regulation. It is **not an absolute 3 A fault ceiling**; source response, eFuse/LTC loop interaction and inrush require validation. ITIMER is left open for the shortest fault interval.
- **Bank regulation:** LTC FB 600 kΩ/100 kΩ gives 4.06 V nominal, approximately 3.948–4.137 V with reference/divider extrema. MAXV 125 kΩ gives nominal 2.50 V per-cell ceiling, approximately 2.35–2.653 V including resistor tolerance. LTC datasheet full-temperature constraint is programmed VOUT ≤ 2 × (VMAXV − 0.440 V), so 4.06 V meets the 4.12 V nominal programming bound. A 4.8 V bank setting with this ceiling does not.
- **Balancing/protection:** LTC MID actively transfers charge between cells. Its approximately 400 mA peak balance action is not a constant bleed current. SS34 reversal clamps are secondary fault-energy clamps; a Schottky's negative clamp voltage is **not** permissible reverse bias for the Eaton cells. Bank undervoltage protects normal loaded operation but does not establish individual-cell safety under every leakage, detached-storage or single-fault condition. Long-tail discharge/reversal protection remains open.
- **Modem buck:** TPS62816QWRWYRQ1, nominal 3.394 V from 47.5 kΩ/10.2 kΩ, 0.22 µH XAL4020-221MEC, 82.5 kΩ COMP/FSET ≈ 2.182 MHz/compensation 2, 5.6 pF feedforward, forced PWM, 100 nF SS ≈ 6 ms (5–7.5 ms from current tolerance). Its 6 A rating provides current capacity for the verified 3 A peak; source energy remains the limiting factor. [TI datasheet](https://www.ti.com/lit/ds/symlink/tps62816-q1.pdf).
- **Brownout:** TPS3808G01, 787 kΩ/100 kΩ, 3.592 V nominal cutoff, 3.495–3.690 V including ±2% reference, ±0.1% resistors and ±25 nA sense bias. Reset clears a SN74LVC1G74 latch, with a manual START button qualified by charger PGOOD and a STOP button. Recharge cannot automatically reboot the modem. CT open gives nominal 20 ms reset-release delay. Removal of USB current authorization asserts MR. [Supervisor datasheet](https://www.ti.com/lit/ds/symlink/tps3808.pdf).

J1 is an explicitly labeled **integration boundary**, not a completed USB-C input: a sole CC/PD owner must supply USB_3A_OK only when 5 V/3 A is authorized. It must remain low for absent/default/1.5 A sources. No 12 V contract is used. The CC controller, USB connector, SS mux and their consumption are not yet captured. The current sheet therefore does not establish MacBook USB-C compliance.

## Energy, losses, startup and repeated bursts

Reproducible assumptions and results are in `compact/tools/power_budget.py`, `compact/build/power-budget.json` and `compact/build/power-budget.md`. The model solves capacitor terminal voltage including ESR, integrates stored charge at 100 µs intervals, and tests ten bursts every two seconds. It approximates the LTC's last-5%-of-voltage taper linearly from full current to 20%. **It is not a switching simulation, loop-stability analysis or a guaranteed waveform.** It treats source response as instantaneous, omits wiring inductance and does not resolve sub-100-µs transients. UV crossings are reported without assuming helpful supervisor delay.

| Assumption | Nominal | Low-line aged | Poor-cable aged |
|---|---:|---:|---:|
| VBUS at board | 5.0 V | 4.5 V | 4.25 V |
| eFuse resistance | 28 mΩ | 56 mΩ assumed | 56 mΩ assumed |
| Charger/buck efficiency | 93% / 95% assumed | 90% / 92% assumed | 90% / 92% assumed |
| Bank capacitance / ESR | 2.5 F / 80 mΩ | 1.575 F / 160 mΩ | 1.575 F / 160 mΩ |
| Full-current modem power available | 11.88 W | 9.39 W | 8.85 W |
| Idealized cold charge to 99% | 2.67 s | 1.73 s | 1.78 s |

Nominal input losses at full current: eFuse I²R ≈ 0.210 W, charger ≈ 0.943 W, buck ≈ 0.626 W at full available output, plus 20 mW modeled storage-side overhead. At 4.5 V aged assumptions: eFuse ≈ 0.382 W, charger ≈ 1.137 W, buck ≈ 0.817 W. These are efficiency-envelope heat estimates, not a thermal layout qualification. Smaller aged capacitance explains its shorter calculated charge time; it is not an improvement.

At nominal settings the bank contains 20.60 J, but energy between 4.06 V and nominal 3.592 V is only 4.47 J before ESR/dropout and taper effects. At worst regulation/aged capacitance/high UV, that window is approximately 1.55 J. Loaded equilibrium is below full-charge voltage: nominal 2.3 A load settles near 3.945 V in this model.

For a 2.3 A baseline and 3 A/100 ms pulses, modeled minimum bank terminal voltage is 3.914 V nominal, 3.742 V low-line aged and 3.693 V poor-cable aged. The last case has only about **3 mV** over worst UV and is not credible qualification margin. Nominal recharge to within 1 mV of baseline equilibrium takes 0.971 s; aged low-line takes 1.077 s. Ten nominal pulses dissipate 7.19 mJ in bank ESR.

A 3 A/500 ms pulse trips UV at approximately 449 ms low-line aged or 112 ms poor-cable aged. A 4 A/100 ms test pulse from 2.3 A baseline passes the nominal model (3.869 V minimum, 1.329 s recharge), but trips immediately in both aged cases from ESR sag. The 4 A and 5 A cases are **test envelopes**, not RM551E specifications. A 3 A continuous baseline exceeds both aged source budgets; capacitance cannot fix a sustained energy deficit.

Startup estimate uses an assumed 4 A charge-current ceiling and neglects detailed linear-mode losses. LTC linear current limit spans roughly 4–6.85 A; it is not precision cell-current control. The model predicts bank ESR startup heat 3.10 J nominal / 3.64 J aged. Charging over about 2 seconds can exceed the cells' continuous rating, and the manufacturer's 1-second pulse rating does not authorize arbitrary startup waveforms. Validate actual startup current, temperature, PGOOD timing and repeated reconnects; these times are not guaranteed ready delays.

[Eaton HV data](https://www.eaton.com/content/dam/eaton/products/electronic-components/resources/data-sheet/eaton-hv-supercapacitors-cylindrical-cells-data-sheet.pdf): initial capacitance −10/+30%, ESR 40 mΩ maximum each, 2.3 A continuous for 15 °C rise, 5.6 A conditional 1-second pulse, 73 °C/W thermal resistance per cell. The aged model combines −10% initial and −30% life capacitance with 200% ESR. At 2 A RMS, each aged cell dissipates 0.32 W, roughly 23 °C rise using that thermal resistance. Lifetime endpoints are conditional manufacturer tests, not universal field bounds. Cold ESR requires separate characterization.

Cells are 2.7 V rated through 65 °C, derating to 2.3 V at 85 °C. Balanced nominal operation is 2.03 V/cell, but a possible 2.653 V individual ceiling is **not safe at 85 °C**. Restrict prototype cells to ≤65 °C, target ≤60 °C, and add/validate thermal handling before claiming hot operation. The quoted 20 µA leakage after 72 h is not a worst-case hot-leakage guarantee.

## Local transient and magnetic checks

The two provisional 150 µF polymer parts plus three 22 µF ceramics give 266.4 µF assumed minimum (polymer −20%, ceramics −20% tolerance and −50% bias) and 439.2 µF maximum. TI allows up to 470 µF including the module. Only 30.8 µF worst-case allowance remains for module/input-network capacitance: **resolve this before selecting final bulk capacitors.** Exact polymer ESR and ceramic bias curves remain to be confirmed. RM520N's recommended two 220 µF parts cannot simply be added to this network.

For an illustrative 1 A step held by minimum C for 20 µs, capacitive droop alone is 75 mV; two 15 mΩ polymer ESRs in parallel add about 7.5 mV before layout/loop effects. At 50 µs capacitive droop alone is 188 mV. Thus 100 mV ripple/transient performance is not established by the capacitor count. Loop and RF load-step measurements are essential.

L2 ideal ripple at 4.06 V input is approximately 1.16 A p-p at nominal L/f. With −20% L, approximately 1.45 A p-p. At 3 A load, ideal peak is about 3.73 A, below the regulator's 7.3 A minimum high-side limit. Fault design must consider 10.4 A maximum limit plus comparator delay; using 50 ns and 0.176 µH gives up to 1.15 A extra at 4.06 V/shorted output. Verify actual inductor temperature/current ratings and layout. [Coilcraft XAL4020-221](https://www.coilcraft.com/en-us/products/power/shielded-inductors/molded-inductor/xal/xal40xx/xal4020-221/).

L1 XAL7030-332MEC has 21.5 mΩ maximum initial DCR and 12.3 A saturation rating; this exceeds the LTC's stated 9 A maximum peak limit at room conditions, but hot DCR and saturation need derating. At 3 A RMS, initial DCR loss is 0.194 W; a 30% hot-DCR assumption gives 0.252 W. [Coilcraft XAL7030-332](https://www.coilcraft.com/en-us/products/power/shielded-inductors/molded-inductor/xal/xal7030/xal7030-332/).

At lowest UV, nominal rail headroom is only 100 mV: allowable total buck/inductor/PCB resistance for maintaining 3.394 V at 3 A is about 33 mΩ. The modem's 3.135 V minimum allows more droop, but does not waive the ripple specification. TI high-side RDS(on) maxima specified at ≥5 V must not be applied as guaranteed values at this bank voltage. Dropout at low bank voltage remains a qualification gate.

## Procurement, libraries and verification

DigiKey API refresh stored only sanitized results in `compact/reference/stock-refresh.json`: Eaton HV1020-2R7505-R **145 available, $2.43 each**; LTC3128IFE#PBF **130, $16.33**; TPS62816QWRWYRQ1 cut tape **8495, $4.08**; TPS259470LRPWR cut tape **1347, $1.72**. USD quantity-one snapshot, not a reservation. QFN LTC3128IUFD had zero stock, motivating the TSSOP candidate. No orders or supplier messages were sent. Credentials were read programmatically and not included in outputs.

Custom IC symbols have explicit datasheet pin maps in `compact/reference/power-pin-map.json`. Custom TI RPW/RWY and LTC FE24 footprints were generated with official KiCad Library Tools; dimensions are in `compact/reference/land-pattern-dimensions.json`. TI land drawings were visually inspected. **These footprints are provisional:** LTC exposed-pad/paste geometry needs final drawing review, stencil segmentation remains unfinished, no 3D interference review has been performed, and exact TI package drawing variant must be confirmed. KLC reports retain style warnings (pin arrangement/grid/filter conventions); do not represent them as KLC-clean production libraries.

KiCad 10.99.0 exports: 69 symbols; **ERC zero errors/zero warnings**; **36 connectivity assertions passed** against exported XML, including storage midpoint and no source bypass; BOM CSV exported. Full-sheet and quadrant renders were visually inspected and component placement adjusted. Connectivity assertions compare intended capture to export; they cannot prove that a transcribed datasheet pin map is electrically correct. There is no compact PCB yet, so no DRC, thermal, routing, fabrication or 3D validation is claimed.

## Required next revision

1. Establish exact hardware/firmware/module variants and acquire RM551E hardware specification. Keep it excluded meanwhile.
2. Resolve conservative sustained power and burst failures: evaluate a higher-efficiency/direct power-assist architecture with independently limited total input, or revise the permitted load envelope/source requirement. Increasing capacitance alone cannot solve the 3 A sustained deficit.
3. Complete independent cell-fault/long-tail UV and temperature protection, charging-current validation and regulator capacitance/dropout/loop closure.
4. Capture CC authorization and USB3 orientation logic, then validate actual MacBook advertisements/contracts. Proceed to vendor profiles, socket, SIM and antenna/mechanical work after these power gates are resolved.
