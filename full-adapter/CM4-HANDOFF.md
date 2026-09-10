# CM4 Lite carrier continuation — 2026-09-10

## User decision and scope

Latest approval: “could we still keep poe if we did this? if so then i think we
should proceed with cm4 lite + gbe”. Yes: gigabit data and PoE power coexist.
Use a PoE-rated Ethernet connector/magnetics and a qualified isolated PD supply;
the CM4 itself is not a 48 V PoE input. Select the PoE class from the complete
simultaneous load and conversion-loss budget.

Work in `/Users/alex/sierra-to-usb`, branch `codex/full-adapter`. Preserve local
milestones and user edits. Never push, purchase, reserve stock or order fabrication.
Coordinate with existing tasks before editing. At handoff, the other tasks using
this repository were not loaded; this was the only active task here. Avoid
`/Users/alex/nandapters`, its router container, and shared stale KiCad windows.

Read the original objective:
`/Users/alex/.codex/attachments/9070579f-f60d-47d5-8fe5-bbe63ea3adf6/pasted-text-1.txt`.
The user's new architecture and cost direction supersede its discrete RK3568,
MT7981 alternative and 2.5GbE requirements. Retain the remaining deliverables:

- CM4 Lite, preferably 1 GB for cost, with microSD storage. Choose the exact
  currently obtainable variant; wireless is not required by the board objective.
- Native CM4 gigabit Ethernet. No RTL8125 or USB RTL8156 is needed.
- Linux-hosted USB3 M.2 Key-B modem path. CM4 exposes native USB2 only, so add a
  qualified PCIe-to-USB3 host controller. Do not silently accept USB2 throughput.
- Exact Sierra/Semtech EM919x/EM929x and documented Quectel variant qualification,
  physical isolation of incompatible M.2 contacts and safe default profiles.
- Standards-based isolated PoE, USB-C auxiliary power and safe source arbitration.
- SIM, antenna/mounting/cooling provisions, independent modem power control,
  radio-disable, reset, labeled controls and useful test points.
- Accessible GPIO, UART, SPI, I²C/Qwiic, practical analog inputs, debug console
  and programming/recovery. Add a supervisor MCU only if its benefits justify cost.
- Preserve external-host USB3 access if practical with verified host selection;
  never join two hosts or their power outputs together.
- A readable hierarchical schematic, fully routed PCB, verified symbols and
  footprints, exact BOM/placement data, reviewed manufacture outputs and a
  programming/recovery/manufacturing test plan. Prefer JLC assembly where supported;
  document separately fitted SoM, microSD and any other unavoidable manual parts.

## Exact saved state

Hardware checkpoint `289e747` contains a 29-page **RK3568** hierarchy with sixteen
unfinished integration ERC findings. Cost checkpoint `3ccb4f2` adds COST.md and
the catalog snapshot. There is **no integrated PCB**. The only PCB is the
processor escape coupon, with 114 escaped signals and 251 unconnected items.
Neither the coupon nor old ERC/DRC results qualify a complete system.

No CM4 symbols, circuits, PCB or new manufacturing outputs have been created.
`tools/build_ethernet_sequencing.py` and
`research/ethernet-sequencing-parts.json` are preserved, unintegrated historical
drafts. Their proposed reset/discharge timing has not been validated. Do not
spend effort finishing these obsolete circuits for the CM4 design.

Retain existing CAD, libraries, research and reviews. A sensible next step is a
clearly current `full-adapter/cm4/` project while labeling existing RK3568 CAD as
historical. This structure has not yet been created. Avoid destructive mass moves
that break existing generators. Adapt root staged checks to validate the new CAD
and preserve the old checkpoint; do not merely disable validation or bless new
files without electrical assertions. The current checker has an exact CAD whitelist.

## Research already established; candidates still require qualification

Official Raspberry Pi sources:

- [CM4 datasheet](https://datasheets.raspberrypi.com/cm4/cm4-datasheet.pdf)
- [CM4 IO datasheet](https://datasheets.raspberrypi.com/cm4io/cm4io-datasheet.pdf)
- [Design-file portal](https://pip.raspberrypi.com/categories/1210-design-files)
- [CM4 IO KiCad files](https://datasheets.raspberrypi.com/cm4io/CM4IO-KiCAD.zip)
- [USB3 reference KiCad files](https://datasheets.raspberrypi.com/cm4io/CM4IOUSB3-KiCAD.zip)
- [USB3 application note](https://datasheets.raspberrypi.com/cm4io/cm4iousb3-appnote.pdf)

Download and inspect these locally; web PDF opening hit a size limit, not a
missing-document blocker. Verify the actual design archive license before reuse.
The official module footprint uses two 100-pin Hirose DF40-family board-to-board
sockets. Check exact mating height, lands, 200-pin mapping and assembly quantity;
do not count one combined footprint as one physical connector in procurement.
Use the official reference as a starting point and verify the electrical design.

SC0691 = CM4101000, wireless 1 GB Lite (no eMMC). The user found it at $40;
DigiKey displayed $46.25 during research. SC0695 = CM4001000, non-wireless 1 GB
Lite, displayed $41.25. These are snapshots, not guaranteed pricing or supply.
CM5 was rejected on current cost. Retain CM4 unless a concrete incompatibility
requires revisiting it; do not restart broad platform selection for convenience.

CM4 provides a gigabit PHY and PCIe Gen2 x1. Its native USB is USB2. The official
USB3 reference uses VL805; no stocked VL805/VL806 candidate appeared in the JLC
catalog search. The reference's `VL805=1` firmware mechanism is VL805-specific.

Promising alternative: Renesas **uPD720202K8-711-BAA-A**, **C3025201**, two-port
USB3 host, PCIe Gen2 x1, QFN48-EP 7×7 mm, 1.05 V and 3.3 V, 24 MHz reference.
Catalog snapshot: 155 units, $4.7781 at one, $4.0893 at ten. Manufacturer lists
the family active with longevity through 2034:
[Renesas product/documentation](https://www.renesas.com/en/products/upd720202).
This is a candidate, **not an electrically or software-qualified selection**.
Read manufacturer datasheet/user manual and qualify reset, clock, rails, PCIe,
USB termination and Linux firmware availability/licensing/loading. Decide whether
external serial flash is required for reliable boot; do not assume enumeration
from a marketing statement. The 701 and 711 temperature variants differ.

PoE magnetics/transformer were unresolved in the old design. Re-evaluate for
native gigabit and the new load budget; do not inherit unqualified magnetics.
Old pitfalls: JASN V24P05S was explicitly non-PoE; Würth 750313355 is a forward
transformer and cannot be substituted into a flyback reference. Catalog labels
alone are insufficient. Use manufacturer isolation, current, turns-ratio and
imbalance evidence. Include modem transmit peaks and hardware accessory limits.

## Cost and implementation priorities

`COST.md` and `research/cost-snapshot-2026-09-10.json` describe the obsolete
RK3568 capture: approximately $108.65 in selected components at ten-unit price
breaks, of which CPU/DDR/eMMC were $83.03. They are not a CM4 quote. Old complete
board planning ranges also do not carry over as a current CM4 estimate.

Cost savings primarily come from replacing discrete CPU/memory/storage and their
carrier complexity with a SoM. Native gigabit additionally removes the external
2.5GbE controller and its support circuit. Price the complete new carrier,
connectors, microSD, USB3 host, isolated PoE and assembly; keep rough allowances
separate from captured BOM totals and an actual JLC quote. Do not invent a quote.

Start actual CM4 capture after source/pin/boot qualification, then integrate USB3,
modem profiles, power, Ethernet and development IO. Preserve the USB3 modem path
through the entire design. Qualify sequencing, unpowered backfeed, recovery and
simultaneous worst-case power/thermal behavior. Use the relevant KiCad skills,
manufacturer lands and visual schematic/footprint review. Choose a documented
JLC stackup and impedance rules from the actual carrier routing needs; the old
RK3568 BGA escape is not a requirement for this SoM carrier.

Tools: `full-adapter/.venv/bin/python`,
`/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli`, `pdftotext`, `pdftoppm`.
Root `tools/check_current_design.py` is run by staged checkpoint hooks; checks
presently target RK3568. Existing deterministic schematic helpers are in
`full-adapter/tools/schematic.py`. References and build outputs are ignored only
at existing paths; account for new subdirectory paths if used.

Continue autonomously through complete routing, ERC, schematic/PCB parity, DRC,
all unrouted nets, vendor-profile assertions, 3D/clearance review and reviewed
Gerbers/drills/BOM/placement/schematic PDF/board renders. Make local milestone
commits. Do not count research, plans, partial CAD or the historical coupon as
completion. Bench-dependent tests may remain explicitly identified; unresolved
electrical faults and missing design/manufacturing deliverables may not.
