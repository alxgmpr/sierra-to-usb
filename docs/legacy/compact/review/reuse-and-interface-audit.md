> Historical evidence from superseded designs. See the [current full adapter](../../../../full-adapter/README.md). Circuit status and artifact paths below refer to the historical checkpoint, not the replacement.

> Historical review context. Current placed-board mechanics, circuit changes and complete qualification gates are in [carrier/REVIEW.md](../carrier/REVIEW.md), [mechanical-review.md](../carrier/mechanical-review.md) and [ROUTING.md](../carrier/ROUTING.md); those supersede earlier candidate/status statements below.

# Audited reuse and interface requirements

2026-09-05. This is an audit record, not a completed interface schematic. Root circuitry was read directly and its exported netlist inspected. The root project was not edited. References below use root designators.

## Reuse decisions

| Root section | Disposition and concrete reason |
|---|---|
| USB J1 and USB2 data | Reuse the verified hybrid connector geometry as a candidate. A6/B6 share D+; A7/B7 share D-. Preserve these two joins immediately at the connector. No USB2 polarity crossover. The exact connector's Gen2 insertion-loss performance remains unqualified. |
| USB U1 HD3SS3220 | Candidate only. PORT=GND correctly selects UFP, ADDR open selects GPIO, ENn_CC=GND enables CC. Both current outputs 25/26 are currently NC, so this sheet cannot authorize 3A. VDD5 is connected directly to VBUS_DATA, but its recommended minimum is **4.5V**, while VBUS_DET permits 4V through 900k. The detector specification does not expand the supply specification. Do not reuse at 4.0/4.25V without a valid supply redesign or a replacement CC/mux solution. |
| USB U1 current authorization | In GPIO UFP mode, OUT1/OUT2 are open drain: default H/H, 1.5A L/H, 3A L/L. Pull-ups and fail-safe decode are required. Qualify decode with valid supplies, VBUS and normal sink attachment. ID is a source-attachment indication, **not** the sink's permission to consume 3A. OUT3 detects audio; it alone is not complete debug-accessory rejection. |
| USB mux orientation | Existing mapping matches TI signal pin names: module TX± -> U1 pins6/7 -> connector TX1 A2/A3 or TX2 B2/B3; connector RX1 B11/B10 or RX2 A11/A10 -> U1 pins9/10 -> module RX±. Label nets from the module point of view to eliminate the root names SS_MOD_RX (which actually carry module TX). DIR requires its pull-up. Verify both attachment orientations electrically. |
| USB C58/C59 | **Do not blindly copy.** They are in the laptop-TX/module-RX path. Laptop TX already owns its coupling capacitors. Quectel Figure19 puts its C3/C4 at the actual host transmitter; this carrier is not that transmitter. Both module documents draw 220nF inside module TX. Sierra Figure3-2's prose says host Rx but the drawing puts the extra pair on host Tx: retain this document discrepancy explicitly. TI requires mux common-mode 0-2V; adding series capacitors without bias can float the mux. Final capacitor ownership and receiver bias need closure, not an ERC waiver. |
| USB D20/D21/D22/D23 | Reuse ESD strategy, audit exact channel mapping and loading; select rated Gen2 protection from manufacturer data. No board-level SI validation exists. |
| USB U4 AP2112 | Re-evaluate input voltage, reverse conduction and off-state supply sequencing. Do not allow an always-on host rail to feed an unpowered modem through GPIO, ESD, USB2 or SS switches. |
| power_input | Omit PoE, bridges, transformer, flyback, ORing and CH224K 12V configuration. Connecting CH224K and HD3SS3220 CC pins to the same receptacle would create two CC owners. |
| power_rails | Old TPS565201 architecture and capacitor values are not approved for the new source envelope. Omit Ethernet and MCU supply branches; retain concepts only. |
| M.2 CN1 geometry | Reuse LOTES APCI0105-P001A geometry subject to the original manufacturer/mating/height review; preserve corrected NPTH pegs. Rebuild the symbol with neutral pin numbers and explicit profile-specific functions rather than the EM92xx/RM520N merged labels. |
| M.2 JP1/2/3 | Root puts 24/38/68 on independent jumpers. In EM9190 Rev8 these three supplies are required; Quectel24 is a supply OUTPUT, 38 an input and 68 reserved. Independent jumpers do not enforce a coherent profile. Redesign as one keyed/interlocked assembly or equivalent hardware isolation plus validity detection. |
| M.2 pin20/pin22 networks | Sierra-only. Physical open circuit on Quectel, including removal of pull-ups, dividers, LEDs and probe stubs beyond isolation where they violate NC. Grounding a reserved pin is not compliance. |
| M.2 SIM2/PCIe | Omit pins40/42/44/46/48 circuitry entirely: Sierra uses these for mmWave power control/supply, Quectel for SIM2. Omit PCIe PHY/clock/reset wiring in this USB-only carrier. |
| M.2 C44/45/46 and ceramics | Do not copy the three 470uF parts. Combined carrier and module C must fit the selected regulator and soft-start. |
| SIM1 | Reuse XKNANO-113 candidate, module-supplied VDD, normally closed CD contact and protection concept. Root has no series damping resistors in SIM1 clock/reset/data. Quectel Figure15 specifies 22ohm, 10pF and 10-20kohm data pull-up; audit Sierra timing and protection C before choosing final values. Root's blanket 22pF cannot be declared independently qualified. |
| SIM2/eSIM/mux | Omit SIM2, TS3A27518 and ST4SIM. No value for the requested one physical SIM. |
| RF | Keep four sub-6 paths, omit fifth dedicated GNSS path. Existing BWSMA-KE-Z001 is not accepted as edge-launch merely because of its footprint filename. Use an exact edge-launch part after drawing verification. |
| MCU | No optional MCU copied yet. A MCU would have a concrete benefit if needed to read CC attachment/orientation, enforce timed reset and request graceful shutdown; it must never be the only protection against a dangerous vendor profile. |
| Ethernet/debug extras | Omit RTL8125, transformers/magnetics and dedicated USB2 MCU/debug port. Keep manual test pads and controls. |

## Logic and sequencing facts

- Both audited modules accept VCC 3.135-4.4V, ripple at most/about 100mV per their respective specifications. This is a module-pin condition including return drop.
- Pin6: Sierra high >=1.0V, low <=0.5V; Quectel high >=1.19V, low <=0.2V, high max4.4V with internal100k pulldown. A derived 1.8V signal is suitable only after sequencing and tolerance checks.
- Sierra pin20 high range1.35-2.10V; USB selected at boot. It is RESERVED in Quectel. Sierra pin22 high >=1.6V, max5.25V; gate it from live host presence and module power, not a permanently live input.
- Sierra pins8/26 high>=0.7V, low<=0.4V, high max4.4V. Quectel specifies1.8/3.3V-compatible control and internal1.8V pull-ups. Use open-drain assertion; do not add independent high-level drives.
- Reset pin67 must remain high-impedance when released. Sierra explicitly prohibits a host pull-up/drive-high and specifies400-800ms low. Quectel warm reset specifies>=200ms,400ms typical. A manually held button is emergency access, not a guaranteed400-800ms pulse; a timed hardware pulse or qualified control is needed for repeatable reset.
- Sierra Rev8 forbids host signal drive until >100ms from start of power-on; its USB power-down sequence can take8s. Quectel provides a separate graceful shutdown handshake and a900ms minimum off interval for hard reset. Immediate regulator STOP in the current power sheet is an emergency power cut, not graceful module shutdown.
- Sierra SIM detect is GND=absent/open=present. Quectel hot-plug is disabled by default; normally closed socket requires AT+QSIMDET=1,1 then restart. Do not mistake SIM detect firmware configuration for hardware vendor isolation.
- No guaranteed powered-off USB2 leakage or cross-domain back-power closure has been established. Test these states with the modem supply discharged and USB still attached.

## Source anchors

- Sierra 41113174 Rev8: Table3-1 pp25-29, Table3-2 p30, Figure3-2 p31, Table3-8 p39, USB timing pp65-67. See [source register](source-register.json).
- [Quectel RM520N-GL V1.0](https://forums.quectel.com/uploads/short-url/1zkjPRnxF5BZ2woox386baCZx4g.pdf): pin table pp19-23, supply p27, reset pp33-35, SIM pp37-40, USB pp41-42.
- [TI HD3SS3220 SLLSES1E](https://www.ti.com/lit/ds/symlink/hd3ss3220.pdf): pin table pp3-4, recommended conditions p5, UFP example pp30-31. Document pin mapping checked independently of the root symbol.
