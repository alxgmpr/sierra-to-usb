> Historical evidence from superseded designs. See the [current full adapter](../full-adapter/README.md). Circuit status and artifact paths below refer to the historical checkpoint, not the replacement.

# Prompt: finish the compact carrier through placement, leave routing to me

Continue my compact USB-C M.2 cellular modem carrier in `/Users/alex/sierra-to-usb`. Execute the stages below, not just a plan. My endpoint is a complete, reviewed schematic and an unrouted PCB with deliberate component placement, mechanical definition and routing rules. **I will route the board. Do not add signal/power tracks, routing vias or autorouting.** Mounting holes and component pads are allowed. Document suggested thermal/stitching vias for me to implement.

## Working rules and scope

Preserve the existing root KiCad project as a reference. Adapt useful existing schematic circuits and libraries into `compact/`; make a fresh compact PCB. Do not duplicate work already valid in either project. Audit copied circuits instead of assuming the old schematic is correct. Keep project/library paths portable and reconcile generated sources with manual edits so regeneration cannot silently erase changes.

Use the available KiCad schematic, BOM, symbol, footprint, PCB and export skills. Inspect actual manufacturer documents and reference circuits; identify exact revisions and regional suffixes. Use distributor credentials programmatically from the git-ignored `.env.distributors`, without exposing them in outputs, arguments or commits. Do not purchase anything or contact suppliers.

Read first:
- `docs/compact-usb-carrier-review.md` — contains historical alternatives; the one-port requirement below supersedes them.
- `docs/eaton-supercapacitor-selection.md`
- `docs/compact-usb-tasks.md`
- `docs/power-design-review.md`
- `compact/README.md`, `compact/energy-storage.kicad_sch` and its generators/calculations.
- Relevant root sheets and libraries before copying circuitry.

Requirements: one USB-C cable directly to an M1 Pro MacBook Pro for data and power; target 5 V/3 A, with proper current authorization and no dependency on 12 V. USB3 SuperSpeed with automatic orientation switching. Physical nano-SIM, accessible reset/power controls, hardware-safe vendor profiles, four EM9190 antenna breakouts, compact mechanics and cooling. MCU optional. Exact Quectel antenna requirements must be verified.

Make routine reversible decisions autonomously. Continue independent work when one item is blocked. Ask only for missing information that changes a material design decision; do not silently relax requirements. Keep the task list current and distinguish datasheet facts, calculations, assumptions and unperformed bench tests. ERC is not electrical validation.

## Layer 1 — establish the supported configurations and reuse map

Create a pin-by-pin compatibility matrix for EM9190 and the exact RM520N/RM551E suffixes and revisions. Include supplies, reserved pins, USB, SIM, reset, enable, boot straps, logic voltages, antenna interfaces and power-off behavior. Identify which existing sheet sections can be copied, must change or should be omitted.

Do not use RM50xQ current figures for RM551E. If an applicable RM551E hardware document cannot be obtained, explicitly exclude that configuration from verified support and preserve an unresolved compatibility gate. Do not guess its reserved-pin behavior. Record macOS network/firmware requirements separately from electrical compatibility; enumeration is not proof of networking. Prepare a test procedure where hardware testing is unavailable.

Deliver: compatibility matrix, source/revision register and precise supported-versus-unverified scope.

## Layer 2 — close the power architecture before committing placement

Re-evaluate the current TPS259470L/LTC3128/TPS62816 candidate. Its zero ERC does not resolve the documented low-line/aged failures. Select or revise the architecture using verified source/load limits and a total current budget covering all circuitry. The Eaton cells and controller choices are provisional and may be replaced with justified alternatives.

Prove from circuit operation that storage supplements a LIVE current-limited USB source. Budget losses, input-current tolerances, cable drop, regulator dropout, ESR, capacitance tolerance, startup, recharge and repeated bursts. Separate supply-capability requirements from measured or specified consumption. Obtain/define justified pulse durations; do not invent them as module specifications. Increasing capacitance cannot fix a sustained power deficit.

Complete charging/inrush, individual-cell balancing and over/undervoltage behavior, reverse-discharge/fault handling, hot-cell derating, regulator compensation, local decoupling and power sequencing. Check converter interaction and combined module/local capacitance. Use manufacturer simulation models where available and useful; analytical models are not bench measurements.

Deliver: selected circuit, exact critical parts, reviewable calculations and explicit bench qualification plan. If the full required envelope cannot fit 5 V/3 A, expose the incompatibility and the smallest decision needed. Do not label a failed candidate ready for layout.

## Layer 3 — finish the complete schematic

Build a coherent compact hierarchy, reusing audited root circuits for:
- USB-C receptacle, ESD, one coordinated CC/PD owner, current authorization and SuperSpeed orientation mux. Check USB2 routing, SS mapping, AC-coupling ownership and powered-off behavior.
- M.2 socket and hardware vendor-profile isolation, including optional Sierra power pins and pins that Quectel requires unconnected. Invalid/default profiles must keep modem power disabled. No software-only safety dependencies.
- Module-supplied nano-SIM voltage, SIM protection, reset/power controls and necessary test points.
- Verified antenna arrangement: distinguish modem-to-SMA coax pigtails from carrier PCB RF traces. Choose exact MHF4-compatible cable/connector and edge-launch SMA parts; avoid redundant connectors. Confirm each required RF path and its frequency range.

Capture optional MCU circuitry only when it provides a concrete benefit. Maintain manual bring-up access.

Deliver: complete schematic, source-to-pin checks, netlist assertions, BOM and visually reviewed exports. Resolve electrical ERC findings; document deliberate exceptions. Include independent datasheet pin checks rather than only comparing a generator to its own output.

## Layer 4 — qualify footprints and define mechanics

Verify exact orderable MPNs, package variants, pad numbers, polarity, exposed-pad/stencil requirements, connector mating geometry and available stock. Replace provisional footprints and generic critical parts. Check 3D models against manufacturer dimensions; do not use misleading generic models.

Define a justified compact outline around the M.2 module, mounting support, USB-C access, SMA body/nut/wrench clearance, nano-SIM access, buttons, capacitor orientation, heatsink and coax bend radius. Do not chase a board size that makes these unserviceable.

Select a provisional fabricator stackup and calculate USB differential/RF impedance constraints from that actual stackup. If fabrication choices remain unknown, mark widths/gaps provisional rather than presenting generic widths as controlled impedance.

Deliver: mechanical drawing, verified footprint library, stackup assumptions and routing constraints.

## Layer 5 — create and place the unrouted PCB

Create the compact board from the final schematic. Place connectors/mounting features first, then power stages and their local capacitors, USB protection/mux, socket, SIM and controls. Arrange switching current loops, feedback paths, RF clearances and high-speed reference planes for practical manual routing. Reserve real space for cooling and mechanical support.

Configure net classes, differential-pair rules, clearance/keepout rules and labeled placement/routing guidance. Define ground-zone boundaries if useful, but do not use filled copper to imply routed connectivity. Lock mechanical anchors and explain which component clusters should move together.

Do not copy the root PCB's tracks or vias into the new board. **Leave all routing to me.**

## Layer 6 — review and hand off

Check schematic/PCB parity and component count. Run ERC and placement-stage DRC; distinguish expected unrouted connections from actual footprint, clearance, outline or placement defects. Visually inspect schematic, board layers and 3D/mechanical views. Do not claim routed signal integrity, thermal performance or fabrication readiness.

Deliver the KiCad project, placed unrouted PCB, BOM, netlist, readable schematic PDF, placement drawings, 3D views where models permit, checks and a concise routing guide. The guide should specify routing order, critical loops, differential/RF constraints, reference-plane continuity, thermal/stitching-via recommendations and test access. Finish with an explicit list of unresolved design gates and bench tests. No production Gerbers or fabrication release at this stage.
