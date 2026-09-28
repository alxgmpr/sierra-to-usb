# Sierra / Quectel 2.5GbE PoE modem appliance

MCU-only, multi-gigabit WAN design study for **EM9190, EM9293, RM520N-GL and
RM551E-GL**. No CM4/CM5 or external application processor. Work is on `master`.

**Feasibility gate remains open.** Manufacturer documentation establishes Sierra
PCIe endpoint/USB-device operation, not modem-hosted Ethernet. A switch does not
supply the missing host and drivers. Quectel offload is a candidate requiring
exact firmware and NIC qualification. No modem combination is qualified.

- [Requirements and confirmed decisions](REQUIREMENTS.md)
- [Architecture, manufacturer evidence, networking and recovery](docs/architecture.md)
- [Packet-path / power-domain block diagram](docs/packet-path.svg)
- [Power and complete-cost estimates](docs/power-and-cost.md)
- [Actual KiCad recovery schematic](hardware/recovery.kicad_sch)
- [Implemented circuit, checks and outstanding qualification](hardware/README.md)

The three-sheet schematic implements an independent MCU/watchdog/reset subsystem.
It is **not the complete appliance**: PoE, modem socket/SIM, high-current power and
Ethernet capture remain gated by architecture and exact manufacturer evidence.
Native ERC and critical-net checks pass; no firmware or hardware qualification.
No PCB layout, procurement or fabrication outputs are included.

Previous designs remain only in Git history; none were restored for this work.
