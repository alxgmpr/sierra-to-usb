> Historical evidence from superseded designs. See the [current full adapter](../../../../full-adapter/README.md). Circuit status and artifact paths below refer to the historical checkpoint, not the replacement.

# Direct-buck power review — conditional prototype design

The captured replacement uses TPS259470L input protection, a 10 mΩ four-terminal VPG shunt, INA190A1 current sensing, a REF3312/TLV333 analog current override, and LTC3310S regulating a nominal 3.33 V rail. Four T530D227M006ATE005 polymer capacitors and local ceramics shunt the live output. There is no two-stage supercapacitor charger in this architecture. The historical LTC3128/TPS62816 candidate remains rejected.

## Low-line capability

`../review/replacement-power-budget.py` evaluates 128 input-current tolerance corners. With the specified resistor/reference/shunt/gain errors and explicit additional allowances, normal current limit spans approximately 2.838–2.933 A. A separate 10 mA upstream reserve gives an upper steady input of approximately 2.943 A. The eFuse's approximately 3.27 A nominal fault setting is deliberately above that loop; it is not the normal 3 A limiter. Dynamic peaks are not bounded by this DC calculation.

At **4.0 V at the carrier**, the low current corner provides 11.351 W before the input path. Maximum-temperature eFuse resistance45 mΩ, shunt tolerance/aging and a5 mΩ routing allocation dissipate0.484 W. The high rail corner at3 A requires10.128 W. After0.12 W of auxiliary/bleeder allowance and0.55 W of converter-loss allowance, the conditional surplus is0.0698 W. Input-to-output headroom is0.454 V before buck switch/inductor conduction drop. These loss allocations are not guaranteed semiconductor maximums.

The itemized `../review/carrier-auxiliary-budget.py` calculation accounts for every AUX-connected resistor at full supply, both programmer pull-ups, all control ICs, output bleeder, feedback divider, supervisor SENSE currents, control LDO and polymer leakage. It gives9.631 mA auxiliary input current plus40.695 mW carrier load on the buck output:79.22 mW at4.0 V input,88.85 mW at5.0 V. This stays below the120 mW reserve. The bound deliberately sums incompatible resistor logic states. It distinguishes published limits from allowances for ST VSYS current, loaded LDO ground current, timer active current, amplifier output drive and miscellaneous leakage. Verify those allowances hot; no MCU, LED bank, fan or external accessory load is included. R410 dissipates34.9 mW at the revised rail corner.

The converter has typical, rather than maximum, internal on-resistance and transconductance specifications. Thus the0.55 W hot converter-loss allocation remains a **bench acceptance gate**. At this source-current corner, total converter plus downstream auxiliary losses must stay below approximately0.740 W just to avoid a sustained deficit. Require additional measured margin, not equality. A datasheet typical efficiency graph is not a worst-case proof. No conclusion that5 V/3 A is impossible follows from the old rejected candidate.

## Module contact and distribution budget

The inherited LOTES APCI0105-P001A drawing rates each contact at0.5 A. Quectel exposes only five common supply contacts, so that socket is rejected for the3 A engineering load case. The replacement Amphenol MDT420B01411 is rated1 A per power contact continuously at25°C still air, with30°C maximum rise under its qualification conditions. Hot operation and individual current sharing still require validation; the module's own contacts are not qualified merely by replacing the socket.

Amphenol specifies55 mΩ initial contact resistance and20 mΩ allowed change. Using75 mΩ with five supply and eleven electrical ground contacts gives65.45 mV round-trip drop at3 A under equal distribution. Add10 mV for supply/return PCB distribution and reserve80 mV total. The regulator setpoint is now3.33 V (R40156.2 kΩ plus R411402 Ω), with3.2845–3.3760 V tolerance corners. After80 mV distribution and50 mV transient allowance the module sees at least3.1545 V. Keep all supply and ground pins connected with balanced low-impedance distribution; do not count the socket solder tabs as extra module contacts. Supervisors sense the regulator output bank upstream of these drops.

## Constituent converter-loss envelope

`../review/carrier-buck-loss-envelope.py` separates switch conduction, inductor winding loss and remaining loss allowance. It uses twice the published25°C typical switch resistances (16/4.5 mΩ), explicitly as an engineering allowance, plus the4.6 mΩ maximum25°C inductor DCR adjusted with copper temperature coefficient to125°C. At4.0 V input and3.02 A including a small carrier-output reserve, the arithmetic gives duty0.910, switch conduction0.274 W and winding loss0.059 W. The0.55 W total converter allowance leaves0.218 W for core, switching, gate-drive and operating losses. Estimated100% duty headroom is0.338 V. These calculations provide measurable loss targets, not guaranteed production limits or a thermal simulation. Hot RDS/process variation and the residual loss sum must be demonstrated on hardware.

## Storage, startup, recharge and discharge

KEMET's current T2076_T52X-530 revision2026-08-20 lists the selected220 µF/6.3 V T530 part with5 mΩ ESR,7.1 A allowable ripple at45°C and125°C maximum operating temperature. Four give880 µF nominal. Applying−20% initial tolerance and−20% endurance change gives563.2 µF. The report separately applies a0.90 temperature capacitance allowance and2x temperature ESR allowance; those assumptions still require verification. The resulting analysis uses506.88 µF and5 mΩ bank ESR. These are not arbitrary unlimited-life guarantees.

The bank is always connected across the live buck output. It supplies `Iload − Iconverter` during a step and recharges from surplus converter power afterward. For a full3 A deficit, ESR alone consumes15 mV of a50 mV droop allowance. The remaining charge allowance is17.74 µC, equivalent to5.91 µs with **zero incremental converter response**. That is an engineering envelope, not a modem pulse duration. Actual burst duration/repetition must be measured; the source must support the average energy demand.

The stated2.2 mF ceiling includes carrier capacitors and module input capacitance. CSS=1 µF with the stated effective tolerance and IC charge-current limits gives24.75–93.79 ms soft start. The capacitor charging term is at most0.300 A at that total capacitance ceiling, before module off-state load. Hardware holds FCPO and USB off through subsequent qualification delays. Verify startup at cold/hot and with the actual module capacitance.

R410330 Ω continuously discharges VCC. The simple2.2 mF/330 Ω worst-tolerance RC calculation reaches0.1 V in about2.58 s, provided there is no continuing source/back-power path. For service, disconnect USB, wait10 s and verify TP505 below0.1 V before changing the module or profile. POWER off is not the normal first step in graceful shutdown; see sequencing-review.md.

The report calculates a conditional recharge interval from the capacitor energy deficit and available low-line surplus. Repeated events must satisfy average deficit energy/period below that surplus. Larger capacitors cannot correct sustained overload. No modem burst duration has been invented.

## Compensation and model limitations

`../review/carrier-loop-model.py` is an **exploratory averaged small-signal model**, not an ADI switching model. It uses the datasheet typical400 µS error-amplifier transconductance and18 A/V ITH gain. It sweeps each gain by±25% (sensitivity assumptions, not guaranteed tolerances), capacitance0.507–2.2 mF and ESR2.5–5 mΩ. Its200 kHz inner-loop pole is an assumed approximation. It includes the ITH compensation network and feedback feed-forward capacitor, and uses a current-source load without resistive damping.

The original22 kΩ/22 nF compensation produced up to190 mV predicted droop on the ideal3 A engineering step. The revised100 kΩ/4.7 nF network holds the compensation zero near its earlier frequency and gives at most46.9 mV predicted droop in the216-case sweep; only54 cases use the selected pair. The model reports stability for those linear cases. It omits switching ripple, pulse skipping, current-limit handoff, diode behavior, propagation delays and saturation. Its numerical phase margins are not measured margins and cannot replace a network-analyzer test.

D401 allows the input-current amplifier to lower ITH; it cannot increase the buck's demand. D402 limits positive current-integrator windup. Their nonlinear handoff, the current sensor's delay, actual current-loop phase margin and worst overshoot remain unverified. Run a switch-level/vendor model if available, then verify the real loops with an electronic load and current probe. ADI recommends20–100% load steps with1 µs rise time and direct loop-response measurement; this is a qualification stimulus, not a modem specification.

## Required power acceptance tests

At4.0 V carrier input and hot component conditions, demonstrate3 A DC rail load without source overdraw, rail brownout or thermal fault; record actual buck/input/auxiliary losses separately. Then characterize actual modem demand, load steps, repeated bursts, recharge, inrush, attach/detach, input-current downgrade, short circuit, reverse discharge, startup with maximum module capacitance and graceful/abrupt shutdown. Measure VCC at the socket and the source current at the receptacle. Confirm steady ripple below20 mV negative deviation to avoid a nuisance supervisor reset. No hardware tests or vendor switching simulation have been performed.
