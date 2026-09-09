> Historical evidence from superseded designs. See the [current full adapter](../../../../full-adapter/README.md). Circuit status and artifact paths below refer to the historical checkpoint, not the replacement.

> Historical review context. Current placed-board mechanics, circuit changes and complete qualification gates are in [carrier/REVIEW.md](../carrier/REVIEW.md), [mechanical-review.md](../carrier/mechanical-review.md) and [ROUTING.md](../carrier/ROUTING.md); those supersede earlier candidate/status statements below.

# RF, mechanical and routing review basis

2026-09-05. No placement-stage board or fabrication release. These are requirements and screened parts; unresolved dimensions are not silently frozen.

## Antenna paths

Use four **module MHF4 plug -> coax -> carrier MHF4 receptacle -> short 50ohm PCB line -> edge SMA** paths if edge-mounted PCB SMA connectors are retained. In that architecture the carrier MHF4 receptacle is necessary to terminate the double-ended pigtail. A direct MHF4-to-bulkhead-SMA cable instead eliminates both carrier RF connectors/trace; do not add a second SMA or MHF4 to such a cable. The present requirement asks for edge-launch SMA, so the bulkhead-only alternative is not silently substituted.

EM9190 sub-6: label by module **MAIN, MIMO1, MIMO2, AUX**. GNSS L1 shares AUX and L5 shares MIMO2 per Rev8 system block diagram. Four cables do not implement mmWave IF/QTM hardware. Rev8 Table4-1 defines per-band antenna use; MAIN/AUX include low band, and four-path MIMO assignments vary by band. Do not infer antenna order from another module's physical connector order.

RM520N-GL V1.0 Table29 pp53-54:

| Module connector | Required roles / frequency coverage |
|---|---|
| ANT0 | LB/MHB main TX/PRX and UHB TX1/DRX; n41 TX0/PRX; n77/78/79 TX1/DRX. LB617-960MHz, MHB1452-2690MHz, UHB3400-3800MHz; n77/78 3300-4200MHz and n79 4400-5000MHz. |
| ANT1 | MHB/UHB PRX MIMO, n41 and n77/78/79 PRX MIMO, LTE LAA PRX5150-5925MHz; GNSS L5 1166-1187MHz. |
| ANT2 | MHB TX1/DRX MIMO and UHB TX0/PRX; n41 TX1/DRX MIMO; n77/78/79 TX0/PRX. |
| ANT3 | LB TX1/DRX, MHB DRX, UHB DRX MIMO; n41 and n77/78/79 DRX; LTE LAA DRX5150-5925MHz; GNSS L1 1559-1609MHz. |

Implement all four paths through at least6GHz for this audited scope. Quectel's cellular antenna requirements are50ohm, VSWR<=3, efficiency>30%; cable insertion loss<1dB below1GHz, <1.5dB from1-2.3GHz, <2dB above2.3GHz. Its GNSS guidance specifies passive gain>0dBi, typical VSWR<2, and recommends passive GNSS when B13/B14 are supported. No active-GNSS bias circuit is selected. External antenna gain/regulatory requirements remain part of module-system qualification.

RM551E antenna count, per-port functions, frequency envelope and any IF/mmWave requirements remain **unknown**. A catalogue's cellular band list is not its RF-interface specification.

## Screened exact parts, not BOM release

- **Taoglas CAB.01072**,100mm,1.13mm microcoax, MHF4L-compatible plug at each end: manufacturer cable catalogue SPE-24-8-198-C lists this construction. I-PEX states MHF4 and MHF4L intermate. DigiKey exact match997 available in this check. Individual cable drawing, bend radius and insertion loss through6GHz are not obtained; do not call the complete path qualified.
- **I-PEX 20449-001E-03** is an exact stocked carrier-receptacle candidate (70,085). Quectel identifies its module receptacle as20579-001E (MHF4L); do not confuse receptacle ordering codes with cable plug ordering codes. Root TE CONMHF4-SMD-G-T footprint must not be relabelled as I-PEX without comparing the manufacturer land patterns.
- **Amphenol RF 132289**, ordinary SMA female,50 Ω,18 GHz. Manufacturer drawing132289 Rev B2011-11-30 was visually recovered from the current product page on2026-09-06. Recommended signal pad5.20×1.50 mm; four ground pads4.90×1.60 mm, at±4.25 mm centre spacing and0.30 mm setback from the edge. The installed KiCad footprint differs (5.08×1.50 mm grounds); `carrier:SMA_Amphenol_132289_Manufacturer` follows the drawing. Body width9.52 mm, panel hole6.60 mm, maximum panel thickness3.5 mm, maximum finished PCB thickness1.57 mm. Reserve at least16 mm connector centre spacing for body/nut access; verify the actual antenna plug and wrench in assembly. No manufacturer STEP has been downloaded.

The read-only stock snapshot is [interface-stock.json](interface-stock.json); broad query near matches such as132289RP and an unrelated oscillator were not selected. No purchases, carts, accounts or supplier contacts were made.

## Mechanical requirements before outline freeze

- EM9190 envelope is30x52mm; Rev8 maximum thickness2.38mm. RM520N-GL is30x52x2.3mm. The inherited LOTES socket is rejected for its0.5 A/contact rating. The selected Amphenol MDT420B01411 has a manufacturer-qualified1 A power-contact rating at25°C and a new drawing-derived footprint. Exact stock remains unresolved. Its insertion and mounting datums must define the support. Nominal module length alone does not locate the mounting hole.
- Keep the socket/screw/heatsink as one mechanical cluster. Reserve access to the M.2 screw and MHF insertion tool; do not place a capacitor or SMA nut over either.
- Four SMA bodies, antenna mating plugs, nuts and wrench clearance set an edge-length floor. The132289 body drawing is now available; reserve16 mm centre spacing and verify actual mating-plug/wrench envelopes before locking centres.
- Reserve coax paths along the module sides with strain relief. The100mm pigtail may need a service loop; only the actual cable drawing can set its permitted minimum bend radius. Do not force it under the heatsink or across sharp component edges.
- Nano-SIM must be insertable/removable without dismounting the modem or SMA cables. Keep controls and their legends accessible with the heatsink installed.
- If Eaton cells remain: two separate10.5mm-max-diameter,22.3mm-max-height cylinders with5mm lead pitch. Upright mounting is the only currently dimensioned option. Formed horizontal leads require a new mechanical drawing and support; do not rotate a cylinder model and assume its leads fit.
- Thermal design requires the modem-specific thermal note, heatsink/thermal-pad stack and temperature limits. No generic heatsink model is qualified. Cooling and screw torque must not bow the modem into components underneath.

## Provisional stackup and rule inputs

The placement specification uses **four layers,1.50±0.05 mm finished thickness including finish at the SMA contact lands**, absolute maximum1.57 mm. This is a custom fabrication requirement, not a claim that an unspecified standard1.6 mm service fits. Nominal stack: F.Cu0.035 mm / dielectric0.20 mm / In1.Cu0.0175 mm GND / core0.995 mm / In2.Cu0.0175 mm / dielectric0.20 mm / B.Cu0.035 mm =1.50 mm before local finish; fabricator must compensate the actual finish/core to meet the finished requirement. Keep the connector lands free of excess solder before insertion. The opposite-side solder joint must be reviewed for the final board/connector gap.

The old OSH Park1.6 mm stackup is no longer the selected mechanical basis. `stackup-screening.json` remains historical analytical screening, not final routing rules. A custom controlled-dielectric build is supported in principle by [AdvancedPCB's published process](https://www.advancedpcb.com/en-us/resources/stackups/), but no quote, contact, order or acceptance of this exact build has occurred. Require the fabricator's final stackup, finish/thickness control and90 Ω differential/50 Ω RF impedance solution before routing release. Nominal widths must be recalculated for the accepted material Dk, solder mask and copper geometry.

Target classes: USB2 and USB3 90ohm differential; RF50ohm single-ended; power sized by current and voltage-drop budget; slow control at the fabricator's normal clearance. Use a continuous L2 GND reference for top-layer USB/RF. If bottom-layer high-speed routing is later used, give it a continuous adjacent reference too. Never cross a plane split or void.

For RM520N-GL, V1.0 p42 specifies USB3 within-pair mismatch<0.7mm and TX/RX inter-pair mismatch<10mm; USB2 within-pair mismatch<2mm. Use tighter practical targets where needed by the complete channel, include connector/package and any routing-via asymmetry, and keep discontinuities symmetric. These limits do not prove10Gb/s performance.

## Routing guide draft (routing remains entirely the user's work)

1. Complete power/profile/footprint gates and place from the final netlist before routing. Lock the agreed USB, SMA and mounting datums only after mechanical verification.
2. Keep each converter, input ceramics, inductor, output ceramics and power return as one cluster. Minimize input hot-loop area and SW-node copper; take feedback as a quiet Kelvin sense from the regulated output, away from SW/coax/SIM. Do not route large-current return through CC/mux ground connections.
3. Route USB protection and mux-to-socket pairs over uninterrupted GND, minimizing length, stubs and layer changes. Resolve AC coupling ownership before choosing populated series components. Keep USB2 joints at the receptacle short.
4. Route RF launches to the nearest carrier MHF4 with controlled50ohm geometry; include transition tuning and a nearby continuous reference. Avoid power-stage magnetic fields. Coax is a separate mechanical path, not a PCB RF net from M.2 contacts.
5. Route SIM power/clock/reset/data as a quiet group; place ESD and damping near the accessible socket. Keep long probe stubs off high-speed/RF signals; provide ground-adjacent test pads for power, current authorization, profile state, rail PG, reset and cell midpoint if retained.
6. **Suggested vias for the user:** ground stitching near connector shields, beside reference-layer transitions and around RF regions; multiple ground thermal vias at converter exposed pads, sized/segmented to the exact manufacturer's stencil instructions. As a first RF-fence spacing calculation, lambda_g/20 at6GHz and effective dielectric2.5 is about1.6mm; this is a provisional upper spacing, not a verified launch design. Do not use open via-in-pad where solder wicking is unacceptable or the fabricator cannot fill/cap it. The chosen OSH Park service does not provide filled/plated vias.
7. Ground-zone boundaries may be defined after placement, but connectivity must remain visibly unrouted until you add copper. Run final parity/DRC after your routing and repeat thermal/SI verification on hardware.

No signal tracks, power tracks, routing vias, stitching vias, filled zones, autorouting or production Gerbers were added.

Sources: [Quectel hardware document](https://forums.quectel.com/uploads/short-url/1zkjPRnxF5BZ2woox386baCZx4g.pdf), [I-PEX MHF4](https://www.i-pex.com/product/mhf-4), [Taoglas cable catalogue](https://www.taoglas.com/datasheets/Taoglas_Cable_Assembly_Catalog.pdf), [Amphenol132289](https://www.amphenolrf.com/en-us/part/132289/1030/).
