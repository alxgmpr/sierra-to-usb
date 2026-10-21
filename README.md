# Sierra / Quectel 2.5GbE PoE modem appliance

Multi-gigabit WAN design study for **EM9190, EM9293, RM520N-GL and
RM551E-GL**. No CM4/CM5. **RK3566 is the selected Linux packet-processor
candidate for evaluation**, with an independent STM32 recovery MCU. The exact
modem tuples and complete appliance remain unqualified. The complete engineering
capture is in [hardware/appliance.kicad_pro](hardware/appliance.kicad_pro).

**Feasibility gate remains open.** Manufacturer documentation establishes Sierra
PCIe endpoint/USB-device operation, not modem-hosted Ethernet. A switch does not
supply the missing host and drivers. Quectel offload is a candidate requiring
exact firmware and NIC qualification. No modem combination is qualified.

- [Requirements and confirmed decisions](REQUIREMENTS.md)
- [Architecture, manufacturer evidence, networking and recovery](docs/architecture.md)
- [Historical MCU-only packet-path comparison](docs/packet-path.svg)
- [RK3566 processor qualification and current block diagram](docs/rockchip-qualification.md)
- [Block diagram and BOM qualification status](docs/qualification-status.md)
- [Power and complete-cost estimates](docs/power-and-cost.md)
- [Reopened Rockchip Linux comparison and sourcing](docs/rockchip-options.md)
- [Actual KiCad recovery schematic](hardware/recovery.kicad_sch)
- [Implemented circuit, checks and outstanding qualification](hardware/README.md)

The full [30-sheet appliance schematic](hardware/appliance.kicad_sch) now captures
processor/RAM/eMMC, all supplies, 2.5GbE, isolated PoE, modem/SIM and recovery
interfaces: 663 components, 823 nets, **zero full ERC violations**.
[Review PDF](hardware/review/2026-10-07/appliance.pdf) and
[completion / release holds](docs/schematic-completion.md) are available.
All 663 PCB footprints are assigned, including 572 stock hand-solder variants.
Current CLI schematic/PCB parity is clean. October 7 native update-dialog
results are retained in the [footprint and model audit](docs/footprint-audit.md). Two BGA land-pattern/process
reviews, remaining model holds, current modem guides and physical/software
qualification remain open. Placement, routing and manufacturing release remain
pending.

Previous designs remain only in Git history; none were restored for this work.

## Full schematic work — 2026-10-07

Complete appliance capture is saved in the canonical `hardware/appliance` project,
including the independent always-on supply and full recovery hierarchy. See
[completion evidence and release holds](docs/schematic-completion.md).

## Footprint and modem review — 2026-10-21

[Six-footprint review](docs/footprint-review-2026-10-21.md) closes four drawing
geometry holds and fixes TPS56837 paste/mask geometry and BGA grid rounding.
The two BGA PCB land/process holds remain. [Modem documentation gates](docs/modem-documentation.md)
record current download blockers and a PCIe-only RM520N order-code exclusion.
All four modem profiles remain unreleased. Full ERC and native parity still pass.
