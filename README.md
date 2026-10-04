# Sierra / Quectel 2.5GbE PoE modem appliance

Multi-gigabit WAN design study for **EM9190, EM9293, RM520N-GL and
RM551E-GL**. No CM4/CM5. **RK3566 is the selected Linux packet-processor
candidate for evaluation**, with an independent STM32 recovery MCU. The exact
modem tuples and complete appliance remain unqualified. Work is on `master`.

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

The three-sheet schematic implements an independent MCU/watchdog/reset subsystem.
It is **not the complete appliance**: PoE, modem socket/SIM, high-current power and
Ethernet capture remain gated by architecture and exact manufacturer evidence.
Native ERC and critical-net checks pass; no firmware or hardware qualification.
No PCB layout, procurement or fabrication outputs are included.

Previous designs remain only in Git history; none were restored for this work.

## Full schematic work — 2026-10-03

Complete appliance capture and exact parts selection are now authorized and in
progress on `codex/complete-appliance-schematic`. See
[completion criteria and live progress](docs/schematic-completion.md). The new
[always-on supply draft](hardware/always-on.kicad_sch) passes native ERC and
exact-net checks. It is not yet integrated into a complete appliance hierarchy.
