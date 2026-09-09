> Historical evidence from superseded designs. See the [current full adapter](../../../../full-adapter/README.md). Circuit status and artifact paths below refer to the historical checkpoint, not the replacement.

# Routing handoff

Open `carrier.kicad_pro` and `carrier.kicad_pcb` together in KiCad10.99 or a compatible newer version. The board is deliberately **entirely unrouted**. It contains161 schematic footprints,6 mechanical holes and1 board-only card model. References are on F.Fab; enable that layer while routing or use the assembly PDF. Root project files are a preserved reference, not the new carrier.

## Before routing

1. Read `REVIEW.md`, `power-review.md`, `mechanical-review.md` and `build/board-checks.json`. Confirm the exact supported module: EM9190 sub-6 per SierraRev8, or RM520N-GL perV1.0. RM551E remains excluded. Match the physical module to its fixed profile assembly before powering it.
2. Resolve the fabrication stack before freezing impedances. The board requests1.50±0.05 mm finished thickness to fit the132289 launch. The old1.6 mm OSH Park stack is superseded. PCBWay advanced/custom is a candidate only: its published±7% thickness tolerance does not meet this request. No fabricator has accepted the custom stack. Do not order its stock service unchanged.
3. The current four-layer proposal is F.Cu35 µm /180 µm dielectric /In1.Cu18 µm /1.004 mm core /In2.Cu18 µm /180 µm dielectric /B.Cu35 µm, with15 µm mask per face. Requested FR408HR construction and frequency-dependent Dk remain to be confirmed. `stackup.py` and `build/stackup-and-impedance.json` reproduce the preliminary calculation.
4. Complete first-article fit planning for module support, adhesive cooling and four cellular plus an optional fifth GPS coax harness. The USB connector's close locating/shield holes require a0.14 mm finished hole-clearance capability. Review stencil, solder-mask, plating and board-edge launch processing with the chosen fabricator/assembler; no production outputs are supplied.

## Suggested routing order

**Power loops first.** Keep U401,C401,C402 and L401 as one placement cluster. C401/C402 are on opposite sides of the buck for short VIN/PGND loops. All four SW contacts join directly into L401; keep this node compact and away from feedback, current sensing, USB and SIM. C403/C404 close the local output-current loop. C405/C406 and C415/C416 sit on opposite sides of the module socket for local storage; use broad supply/return copper and distribute power to every common VCC and ground contact. Sierra's supplemental supplies route through the fixed profile assembly. The budget does not assume those extra contacts in Quectel mode.

At3 A, total PCB supply-plus-return drop is allocated10 mV (3.33 mOhm); connector allowance dominates the remainder of the80 mV distribution budget. Establish that resistance with finished-copper dimensions, plane/pour spreading and via resistance. A1 mm netclass width is a starting UI default, not proof of this resistance or current capability. Measure distribution drop and individual contact heating on hardware.

Route USB VBUS through D301/U301 and R307 before the converter. D301's ground discharge path must be short and separate from sensitive return paths. R307 pads1/2 carry force current; pads3/4 are independent Kelvin sense connections to U303. Do not tap the sense pair from a remote force pour. Place U303's local return/reference at quiet ground. Keep its sense pair closely coupled, short and clear of SW. Keep U402/U403 reference, divider and compensation returns quiet; D401 can reduce ITH only. Sense buck feedback from the output bank, after the inductor, with a quiet return. The current-limit loop needs nonlinear/load-step verification after routing; the averaged model is not a switching simulation.

**USB next.** Route all high-speed pairs on F.Cu over a continuous In1.Cu ground reference where possible. J101 -> D101/D102 -> U104 -> J201 are the SuperSpeed paths; J101 -> D103 -> U105 -> J201 is USB2. Preserve the exact exported polarity and C/B orientation mapping. CC1 selects muxC; CC2 selectsB. The module TX and host TX own their AC-coupling capacitors: do not insert duplicate series capacitors.

Pairs use `_P`/`_N` net suffixes, including `USB_D_P/N` and `MOD_USB_D_P/N`, so KiCad can identify USB2 as well as SuperSpeed pairs. USB90 defaults are0.263 mm width /0.150 mm gap from the provisional closed-form model; request90 ohms differential from the fabricator. RF50 starts at0.327 mm width for50 ohms. These values omit soldermask, roughness, launches, neck-downs and etch tolerance; vendor field-solver/coupon values supersede them.

Keep pair members symmetric, minimize uncoupled breakout length and layer transitions, and use matched transitions with adjacent ground-return vias if a transition is unavoidable. Start with intra-pair mismatch<=0.25 mm for SuperSpeed and<=0.5 mm for USB2 as engineering layout targets, not vendor compliance guarantees. Do not serpentine unrelated TX and RX pairs to equal overall lengths. Neck down only through tight pad escapes, then restore the solved geometry. Avoid stubs and unnecessary test pads on data nets. Keep CC/SBU/unused contacts as captured; do not add another Rd or a second CC owner.

**RF launches.** Each RF1…RF4 net is a short carrier PCB path from MHF4 to its adjacent edge SMA. The separate CAB.01072 harness connects the modem's RF receptacle to the carrier MHF4. Route short, straight50-ohm paths over a continuous reference with a controlled launch transition. Maintain I-PEX's local no-copper/no-resist area and manufacturer stencil. Add ground connections on both SMA faces, via fences and return transitions during your routing; none exist now. Determine via-fence pitch and spacing with the chosen RF stack/launch model through the supported sub-6 bands. Keep all four port mappings labelled and measure cable-plus-launch loss/return loss. No active GNSS bias or mmWave routing is provided.

**SIM and controls last.** R205/R206/R207 are series elements in CLK/RST/DATA; keep module-to-resistor runs short and the module-powered SIM domain isolated from AUX. D203 and the10 pF shunts are near the socket. Verify cumulative SIM loading at both module SIM voltages. Route the profile validity logic, delayed rail/run controls and open-drain reset/FCPO after high-speed and power paths. Test points are intentionally accessible around the board edges; preserve their probe clearance.

## Planes, thermal paths and mechanics

In1.Cu should remain a continuous ground reference. Use In2.Cu for ground and bounded power distribution only where this does not split a high-speed return path. Add your ground stitching and device thermal vias to the manufacturer's package recommendations. U401's EP is PGND and has four paste windows; qualify via-in-pad/tenting/fill and paste transfer with the assembler. Do not accidentally drain solder through open vias. Similar review applies to U101 and U301 exposed pads. No thermal or stitching vias have been preinserted.

Mechanical anchors and controls are locked. Keepouts reserve screw/washer areas on every copper layer and I-PEX/SIM contact exclusions on the top layer. Adhesive cooling is unmodeled; there is no carrier-mounted cooler frame. Keep the physical nano-SIM, profile tail and control approach spaces available. Detach USB, wait10 s and verify TP505 below0.1 V before profile/module changes. Keep any adhesive heatsink clear of RF connectors and service access.

## Rules and qualification

The only ignored edge-clearance rule applies to the five drawing-defined SMA launches, whose centre lands meet the cut edge. I-PEX shared mask apertures are explicitly allowed inside those footprints. The buck's internal pad-to-pad clearance is locally0.15 mm; normal power clearance remains0.20 mm. No blanket clearance or unrouted waiver exists. The454 unconnected findings are expected at this stage. After routing, rerun full DRC, schematic parity and electrical/thermal/SI review; unconnected findings must then be resolved.

Program the sole STUSB4500L GPIO to DEBUG (`GPIO_CFG=10b`) using an L-compatible tool and preserve unrelated NVM bytes. Factory default must inhibit modem power. The complete settings and readback/analyzer procedure are in `cc-programming.md`; no binary image has been flashed or hardware-qualified.

The4.0 V power envelope is conditional on the0.55 W buck-loss and0.12 W auxiliary allocations, effective storage and loop response. Its minimum calculated sustained margin is only69.8 mW. Verify source-current overshoot, converter loss, dropout, rail transients, recharge, brownout/reconnect, off-state leakage, ESD, both USB orientations, both profile assemblies and thermal behavior. None of these bench tests has been performed. macOS enumeration and networking require separate firmware/driver qualification; electrical compatibility is not a promise of Mac network service.

## Safe regeneration

Edit the Python sources and `placement.json`; generators refuse to overwrite changed generated outputs. `board.py` builds only from the current exported netlist and library footprints. Once you start manual routing or moving generated footprints, do not rerun it over your changes. Preserve the manual PCB, reconcile changes in a scratch copy, or retire the PCB from generation. Never refresh the SHA-256 baseline to bypass a conflict. See the repository's safe-regeneration procedure.

GPS is the independent RF_GPS path between J609 and J610. Route it as a fifth 50 ohm launch; attach its cable only to a dedicated module GNSS port. Modules sharing GNSS on cellular ports keep their existing RF1–RF4 mapping and leave GPS unused. No GNSS bias supply is added.

## Orientation review — 2026-09-07

Rotated U101/U102/U103 to180°, U104 to270°, U301 to90°, U302 to270°, U303/U403 to180°, U105 to270°, U502 to180° and U508 to270°. U104 now faces its common USB bank toward J201 and its switched banks toward the host connector. U301 faces its output toward the shunt/buck. U401 stays at0° with SW toward L401 and feedback on the opposite side. Other changes reduce local signal/decoupling connection distances under a nearest-neighbor net heuristic. These are placement choices, not routed length or SI results; preserve local bypass and Kelvin loops when routing. Three pin-direction tests protect the principal USB/power orientation choices.
