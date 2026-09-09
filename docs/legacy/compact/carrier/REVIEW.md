> Historical evidence from superseded designs. See the [current full adapter](../../../../full-adapter/README.md). Circuit status and artifact paths below refer to the historical checkpoint, not the replacement.

# Compact carrier — reviewed unrouted placement

2026-09-06. The schematic and deliberate placement endpoint is complete:161 circuit components across9 functional sheets plus the hierarchy root, on a fresh110×100mm four-layer PCB. It contains no tracks, copper arcs, routing/stitching vias, filled copper or production Gerbers. Root project files and their pre-existing changes are preserved. This is a **placement-stage prototype, not a fabrication release or electrically qualified product**.

The one USB-C receptacle supplies data and5V power; STUSB4500L is the sole CC owner and authorizes advertised3A before enabling the modem. Hardware profiles support EM9190 sub-6 and RM520N-GL only within the documented revisions. RM551E is excluded. Physical nano-SIM, automatic USB3 orientation, USB2 isolation, ESD, guarded power/run/reset controls and five MHF4-to-edge-SMA paths (four cellular and optional dedicated GPS) are captured. The M.2 module support remains. Adhesive cooling is unmodeled; no large cooler or retention frame is fitted. J202 is a standard keyed20-pin IDC profile connection.

## Verification evidence

- ERC:0 findings. Exported-net assertions:88 passing. Unit tests:14 passing.
- PCB:161/161 schematic components;589 numeric pin/net entries match;0 schematic parity findings;0 placement DRC violations.454 expected unconnected findings remain for the user's routing.
- No routing or filled copper exists. Eleven rule areas reserve screw/washer, I-PEX and SIM contact exclusions. Mechanical anchors and controls are locked.
- All10 schematic pages were visually reviewed; local power/feedback wiring and text collisions were corrected. Placement/mechanical drawings and assembly views were inspected. Custom STEP files were read back and checked against their documented bounds; this is not an exact-solid collision certification.
- The narrow SMA edge-clearance exception permits its drawing-defined lands to meet the cut edge. I-PEX's continuous mask aperture and the buck's0.15mm internal land clearance are scoped exceptions, not blanket waivers.

See [source-to-pin review](source-to-pin-review.md), [machine-readable checks](build/check-summary.json), [routing guide](ROUTING.md) and [artifact index](HANDOFF.md).

## Replacement power result at4.0V carrier input

TPS259470L protection feeds a four-terminal shunt, auxiliary supply and LTC3310S3.330V buck. An INA190/REF3312/TLV333 analog loop limits input demand independently of firmware. Four parallel220µF polymers supplement the live converter. The rejected LTC3128/TPS62816 architecture remains historical; it is not used in this carrier.

Tolerance analysis gives2.8379–2.9328A input limit; with10mA upstream reserve the upper estimate is2.9428A. At3A rail load the allocated worst rail maximum is3.3760V. The4V budget leaves **69.8mW conditional surplus** after path loss,120mW auxiliary and550mW converter-loss allowances. That small margin depends on unverified hot loss bounds. Minimum module voltage after allocated80mV distribution and50mV transient drop is3.1545V. The design does not claim measured3A capability.

The storage calculation's5.91µs full3A deficit interval is an engineering envelope, not a modem burst duration. The216-case averaged sensitivity model, of which54 cases use the selected compensation, is not a switching simulation or proof of nonlinear current-loop interaction. [Power review](power-review.md) supplies the loss, startup, recharge, capacitance, ageing, timing and acceptance details.

## Open design and qualification gates

1. **Fabrication/assembly:** obtain acceptance of1.50±0.05mm finished board thickness and the proposed impedance stack. Published stock±7% tolerance does not meet the SMA requirement. Confirm USB short-tail soldering on this thickness,0.14mm hole spacing capability, annulus/mask/paste, exposed-pad process and launch geometry before ordering. Widths/gaps remain provisional.
2. **Exact sourcing:** LTC3310SIV#PBF availability and MDT420B01411 socket sourcing remain unresolved. Stock snapshots are dated observations, not reservations. Do not silently substitute a package, grade or socket. No purchases or supplier contact occurred.
3. **CC and actual modules:** produce/read back an L-compatible STUSB4500L configuration with GPIO_CFG10b(DEBUG); factory defaults inhibit modem enable. Verify actual module identity/revision/firmware and matching fixed profile. A wrong modem in an otherwise valid plug is not automatically identified. See cc-programming.md and profile-assembly.md.
4. **Power and sequencing bench tests — none performed:** establish hot4.0V/3A capability, actual losses/contact heating, input-current tolerance/overshoot/downgrade, downstream voltage below the buck limit on hot plug, both loop margins/nonlinear handoff, real modem demand/recharge, capacitor C/ESR and total capacitance, startup, short circuit, back-power, discharge and vendor shutdown timing.
5. **Mechanics and thermal:** measure full module insertion/support height, actual shield/tape stack and contact area, adhesive heatsink attachment, four cellular100mm harnesses plus an optional fifth GPS harness on both module variants, cable bend radius/loss and wrench/probe/control access. Current envelope CAD omits detailed cavities/threads/fins; no adhesive, shock or thermal test was performed. See mechanical-review.md.
6. **Interfaces:** USB eye/link/orientation/ESD/off-state behavior, SIM voltage/loading/detect, RF cable-plus-launch return/insertion loss and emissions remain untested. macOS enumeration and actual networking on M1 Pro must be qualified separately for each modem firmware; electrical compatibility does not establish networking.

## Safe continuation

Open carrier.kicad_pro with KiCad10.99 or a compatible newer build. Read ROUTING.md before adding copper. Guarded generators stop if their outputs were manually changed: reconcile changes into the sources; never refresh hashes to bypass a conflict. Once you start manual routing, do not regenerate the board over your edits. HANDOFF.md lists reproducible export/check commands and the authoritative artifacts.

Mechanical update: rounded110×114 mm overall board with symmetric corner mounts and selectable3042/3052 support holes. EM160R is mechanically accommodated only; qualify its exact pinout/profile, grounding and host interface before powering it. Detailed IDC/M.2/card/hardware reconstructions replace the active placeholder boxes; provenance and simplifications are in model-sources.md.
