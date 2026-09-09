# Compact USB-C modem carrier

The current design is [carrier/carrier.kicad_pro](carrier/carrier.kicad_pro), with a complete10-page schematic and a deliberately placed, entirely unrouted110×100mm PCB. Open it in KiCad10.99 or a compatible newer build. The original root project is preserved.

Start with [handoff artifacts](carrier/HANDOFF.md), [review and open gates](carrier/REVIEW.md), and [routing guide](carrier/ROUTING.md). The carrier has159 placed schematic components, zero ERC findings, zero parity findings and zero placement DRC violations;446 unconnected findings are intentional. No tracks, vias, filled copper or production Gerbers were created.

The design uses one USB-C port with3A current authorization, automatic USB3 orientation, module-powered nano-SIM, fixed vendor profiles, accessible controls and four edge SMA breakouts. Scope is EM9190 sub-6 and document-qualified RM520N-GL V1.0; RM551E is excluded. macOS networking remains a separate firmware/hardware test.

The4.0V input design has only69.8mW of calculated surplus under stated hot-loss allocations. It is a placement-stage prototype, not a fabrication-ready or bench-qualified design. Exact buck/socket sourcing, accepted stackup, CC configuration/readback, actual module/cooler/coax fit and all electrical/thermal/interface bench tests remain explicit gates in the review.

`energy-storage.kicad_sch` and the earlier TPS259470L/LTC3128/TPS62816 analyses are historical rejected candidates. Their passing subset checks do not apply to the current carrier. Current power calculations and source/compatibility records are under `review/`; final carrier checks and artifacts are under `carrier/build/`.

Generators use SHA-256 preflight guards. Preserve all generated/manual work; reconcile changes into generator sources rather than refreshing hashes to bypass a conflict. Once manual PCB routing starts, do not regenerate over it. Reproduction instructions are in the handoff index.
