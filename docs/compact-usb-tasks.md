# Compact USB carrier tasks

Updated2026-09-06. The requested schematic and unrouted-placement endpoint is complete. Authoritative current status: [carrier review](../compact/carrier/REVIEW.md) and [handoff index](../compact/carrier/HANDOFF.md). The root project and its pre-existing modifications remain preserved.

## Completed placement-stage work

- [x] Obtain/review Sierra and applicable Quectel documents; build contact compatibility matrix. Exclude RM551E; separate Mac networking qualification.
- [x] Reject the earlier LTC3128/TPS62816 power candidate; select direct LTC3310S buck with analog input-current override, live parallel storage and complete4.0V tolerance/loss/startup/recharge/transient calculations.
- [x] Complete USB-C3A authorization, sole CC ownership, automatic USB3 orientation, USB2 isolation and ESD.
- [x] Complete fixed vendor-profile isolation, module-powered nano-SIM, power/run/reset/RF controls and sequencing.
- [x] Capture four passive RF paths and select edge-launch SMA, MHF4 connectors and exact coax harnesses.
- [x] Review source-to-pin maps, critical packages, passive parts and mating drawings. Correct socket selection, USB/SIM details and custom land patterns.
- [x] Define110×100mm outline, provisional1.50mm four-layer stack, support/cooling/frame geometry, service access, anchors and keepouts.
- [x] Place all159 schematic components on a fresh unrouted board. Add no tracks, vias or filled copper.
- [x] Pass86 exported-net assertions,14 unit tests, ERC0, parity0 and placement DRC0; retain446 expected unconnected findings.
- [x] Export/review schematic, placement and mechanical PDFs, BOM/netlist/positions, STEP envelope assembly,3D views and routing instructions.

## Open design/bench qualification gates

- [ ] Obtain accepted finished-thickness/impedance stack and assembler acceptance of connector/paste/drill details before fabrication.
- [ ] Resolve exact LTC3310SIV#PBF and MDT420B01411 sourcing. No substitutions, purchases or supplier contact were made.
- [ ] Validate L-compatible CC image, readback and source-current/orientation behavior with an analyzer.
- [ ] Verify actual module identity and profile assembly; continuity-test both fixed plugs before use.
- [ ] Establish hot4.0V/3A performance, losses, current overshoot, both loop margins, actual demand/storage/recharge, inrush, voltage overshoot, faults, off-state and shutdown. No bench tests performed.
- [ ] First-article module seating, support/tape/cooler/frame/coax fit, attachment strength, service access and passive thermal performance.
- [ ] Qualify USB/SIM/RF/ESD/EMI and Mac networking for each exact firmware.
- [ ] User routing, full post-routing review and later fabrication release. Production Gerbers remain outside this task.
