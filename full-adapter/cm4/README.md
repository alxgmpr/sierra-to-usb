# CM4 Lite integrated modem development board

Current implementation: `cad/cm4-carrier.kicad_pro`. Work in progress; fabrication
release requires the complete integration, routed PCB and release checks.
The historical RK3568 hierarchy in `../cad/` is preserved and is not this board.

Selected architecture: CM4001000 (1 GB, non-wireless, Lite), native gigabit
Ethernet, PCIe USB3 modem host, isolated PoE and USB-C auxiliary power.
The Renesas uPD720202 remains under electrical/firmware qualification.

The current eighteen-page hierarchy includes the CM4 core, native Ethernet
magnetics, connector, ESD, DC-blocked PoE termination and 36 components for
USB-C auxiliary power and input arbitration, plus modem profiles and two
protected nano-SIM sockets. It has 105 components including 11 DNP profile
links. See the current [modem review](research/MODEM-REVIEW.md),
[power-input review](research/POWER-INPUT-REVIEW.md),
[Ethernet review](research/ETHERNET-REVIEW.md) and
[core review](research/CORE-REVIEW.md). There are 67
unfinished integration ERC findings, no exclusions, and no integrated PCB yet.
Surge/thermal closure and the full simultaneous power budget remain open;
the PoE class is not yet finalized. The captured auxiliary circuit alone is
about $4.53 per board at quantities for ten boards, excluding assembly.

Two Hirose DF40C-100DS-0.4V(58) sockets are separate schematic/BOM components.
J100 contact numbers equal CM4 pins 1–100; J101 contact numbers equal CM4
pins 101–200 minus 100. All 200 contacts are explicit, including unused signals.
CM4 is a separately fitted module. Its GPIO voltage reference connects to its
own 3.3 V output. Its native USB2 interface serves recovery only.

Sources and reproducible checks are in `research/` and `tools/`. Downloaded
manufacturer material is cached in ignored `../reference/cm4/`; source URLs
and hashes are retained in the reviewed maps. Pin names come from the current
CM4 datasheet. The official CM4IO symbol is cross-check evidence: its legacy
Ethernet SYNC voltage labels and SYNC_OUT direction are superseded by the
current datasheet.

2026-09-10 coordination: clean branch at 340c622; no competing active task in
this repository. Previous task was notified of current write ownership. No
shared GUI, other repository, router container, or historical CAD was modified.
