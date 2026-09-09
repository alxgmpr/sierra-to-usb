> Historical evidence from superseded designs. See the [current full adapter](../../../../full-adapter/README.md). Circuit status and artifact paths below refer to the historical checkpoint, not the replacement.

> Historical review context. Current placed-board mechanics, circuit changes and complete qualification gates are in [carrier/REVIEW.md](../carrier/REVIEW.md), [mechanical-review.md](../carrier/mechanical-review.md) and [ROUTING.md](../carrier/ROUTING.md); those supersede earlier candidate/status statements below.

# Qualification procedures - none performed

2026-09-05. Each result must record DUT revision, module full ordering code/hardware marking, firmware, carrier assembly/profile, cable, instrument settings, temperature and raw captures. ERC is not a substitute.

## Host and networking, before carrier freeze

1. On an existing known-good adapter, record Mac model, exact macOS build, cable rating/length and modem identification/firmware with manufacturer-documented commands. Retain `system_profiler SPUSBDataType` and `networksetup -listallhardwareports` output. Observe attachment in both cable orientations.
2. Use a USB-C analyzer to record Rp advertisements and available PDOs at attach, after PD negotiation, during sleep/wake, bus reset, hot-plug and simultaneous use of the other Mac ports. Confirm 5V/3A authorization actually exists. If the Mac offers only default/1.5A, carrier must remain off; do not assume Thunderbolt branding guarantees this attachment behavior.
3. Identify the exact exported USB network class and firmware mode. Confirm a supported macOS driver or native class path on Apple Silicon and an actual connection-management method for SIM PIN/APN/session establishment. QMI/MBIM enumeration alone is not networking. Do not flash unverified alternate firmware during this test.
4. Demonstrate DHCP or documented address configuration, DNS, bidirectional traffic, sustained upload/download and reconnect after sleep. Log operating-system interface counters and modem registration/session state. Repeat after cold reboot and power cycle. No module has passed this procedure in this project.

## Empty socket electrical safety

- Verify no profile, each valid profile, conflicting code, contact bounce and interrupted insertion. Invalid/default must leave MODEM_VCC discharged and enable low.
- Sierra: verify all eight supply contacts; pin20 correctly timed1.8V and pin22 host-presence indication; no drive before permitted startup time. Quectel: verify20/22/24/38/68 physically isolated with power off and on. Check leakage under both USB-present and storage-charged conditions. Do not insert RM551E.
- Check pin67 released voltage comes from the module only; confirm timed pulse400-800ms for Sierra. Confirm W_DISABLE assertion does not back-power anything. Verify SIM socket contact map, polarity and CD contact with a continuity fixture before a live SIM.

## Power path and energy storage

- Sweep source voltage and programmed current limit; add cable resistance separately. Capture voltage at receptacle, protection output, storage terminals, each cell, regulator output and M.2 far-end VCC/GND with short differential connections. Capture total cable current including CC/mux/logic and charger.
- Require the final rail to supply3A continuously for RM520N-GL supply capability. This is not a claim of3A continuous module consumption. For EM9190 sub-6, record2.3A continuous and3A peak as datasheet sizing values. No RM50xQ values apply to RM551E.
- Use a load-step sweep of10us,100us,1ms,10ms,100ms,500ms,1s and DC up to3A. These are laboratory stress durations, **not module pulse specifications**. Sweep edge rates and duty cycle until continuous load. Preserve raw waveforms; do not use a100us numerical integrator to establish sub-100us ripple compliance.
- Measure real RF transmit current across supported bands, EN-DC/CA configurations, low signal/high TX power, thermal throttling and startup. Use sufficient bandwidth to measure pulse widths and duty cycles. Replace stress-envelope assumptions with measurements plus justified margin.
- Demonstrate LIVE-source assistance: force the source into its authorized current limit while pulsing the load, and show positive source current plus storage discharge at the same time. Repeated pulses must reach a stable cycle with recharge before the next pulse and no rising temperature trend beyond the permitted equilibrium.
- Characterize efficiency at low line and hot junction; include cable, eFuse/sense-FET, inductors, charger, converter and auxiliaries. Check UVLO and dropout before declaring a voltage envelope. Validate converter interaction under constant-power loading; test both empty and maximum module/local C.
- If retaining supercapacitors: exercise zero-charge startup, cell imbalance, minimum C/maximum ESR, cold ESR, hot leakage, one weak cell, detached long-tail discharge, open midpoint, capacitor short/open, reverse discharge and reconnect. Individual cells must never exceed their temperature-derated maximum or reverse-bias. Schottky clamps are not proof of zero reverse voltage.
- Record inrush peak/duration/charge at insertion, precharge completion, eFuse latch behavior, source foldback and repeated retries. Keep heavy load off until supply authorization and all ready conditions are valid. Confirm no reservoir discharge reaches the Mac connector.
- Validate feedback compensation using an appropriate manufacturer model and bench loop-gain/load-step checks over actual C/ESR/bias ranges. The manufacturer model is not a bench result.

## USB, SIM, RF and thermal

- Verify SuperSpeed enumeration and sustained error-free transfer in both orientations. Measure differential impedance and channel loss/eye margin using a suitable fixture; preserve a continuous reference plane. Confirm USB2 firmware-recovery path separately.
- Test USB-connected/modem-off, brownout, host-detach and asymmetric power sequencing for back-power current and phantom partial startup.
- Test1.8V and3V SIMs, insertion/removal detection, ESD protection loading, clock edges and communication errors. The module alone supplies SIM voltage.
- Measure each complete RF path (module connector, coax, carrier launch/trace, SMA) through at least the highest supported band. Compare insertion loss with Quectel's band-dependent limits; confirm GNSS L1/L5 antenna sharing and no accidental DC feed into an incompatible antenna.
- Fit actual SMA nuts, antenna plugs and wrench; verify torque support, coax insertion/removal tool access, minimum bend radius and strain relief. Fit the selected heatsink and module screw. Measure temperatures under sustained TX; cell target<=60C if Eaton candidate retained, never assume the2.7V rating applies at85C.
