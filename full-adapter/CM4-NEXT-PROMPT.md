> **Superseded 2026-09-28:** CM4/RK3568 work is preserved as history.
> Do not execute the continuation instructions below. See the current
> [MCU / 2.5GbE PoE appliance requirements](../REQUIREMENTS.md).

# Continue the CM4 board

Paste the following into the continuing task:

```text
/goal Complete the CM4 Lite integrated modem development board in /Users/alex/sierra-to-usb on codex/full-adapter, continuing from the latest saved checkpoint. Preserve every subsequent commit and user edit; do not reset the branch.

First read full-adapter/cm4/CHECKPOINT.md, full-adapter/CM4-HANDOFF.md, full-adapter/CONTINUE.md, and the original objective they reference. Inspect repository instructions, git status and other active tasks before editing. The CAD milestone is 97f1c8f, followed by a documentation/research checkpoint. There are 18 schematic pages and 105 components, 67 unfinished ERC findings, and no integrated CM4 PCB. Historical RK3568 CAD and the escape coupon are not the CM4 board.

Retain the approved architecture: Raspberry Pi CM4 Lite, preferably non-wireless 1 GB, native gigabit Ethernet, standards-based isolated PoE, microSD and safely arbitrated USB-C auxiliary power. Saving money is a priority; do not substitute CM5 for convenience. Retain true Linux-hosted USB3 through a qualified PCIe-to-USB3 controller, including firmware acquisition/license and cold/warm/recovery boot qualification.

Resume actual implementation with modem and main regulators, independent modem power/control and protection, then isolated PoE and its class gating. Close the simultaneous worst-case power/thermal budget before selecting PoE class. Finish exact Sierra/Semtech and Quectel profiles, SIM, development IO, debug/recovery and antenna/mounting/cooling provisions. The regulator research is only a draft, not a qualified circuit. Resolve the documented external dependencies precisely and continue independent work while access is pending.

Use relevant KiCad skills and manufacturer documentation. Complete electrical qualification, readable hierarchical schematics, the fully placed and routed PCB, ERC, schematic/PCB parity, DRC, connectivity/profile assertions, mechanical review and reviewed fabrication/assembly outputs. Deliver exact BOM/placement, schematic PDF, board renders, programming/recovery instructions and manufacturing tests. Refresh availability and estimate complete BOM plus JLC PCB/PCBA costs, separating captured totals, allowances and actual quotes.

Do not stop at research, partial capture or partial routing. Bench-dependent tests may remain identified; missing CAD, electrical faults and unrouted nets cannot count as completion. Make local milestone commits. Never push, purchase, reserve inventory or order fabrication.
```
