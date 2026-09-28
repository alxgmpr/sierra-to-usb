# Power and complete-cost envelope

2026-09-28. **Planning estimates, not a released BOM, guaranteed power bound,
quotation, or selected PoE class.** Packet-processor choice and exact modem SKU
remain open. One modem is installed; do not sum two mutually exclusive cards.

## Simultaneous power

Sierra PTS r5 table 3-2 gives EM9190 5 A peak with mmWave, 3 A without, and
EM9191 2.7 A. RM520N-GL Hardware Design §3.3 requires at least 3 A continuous
capability and shows a 5 A reference regulator; **5 A regulator rating is not a
documented modem peak**. Obtain actual burst bounds and latest-revision limits.
Sources are linked in [architecture.md](architecture.md).

Preliminary design allocation, at the loads:

| Load | Simultaneous allocation | Basis / remaining uncertainty |
|---|---:|---|
| Modem including allocated RF load | 18.87 W | 3.7 V +2%, 5 A design allocation; not measured or guaranteed for all RM5x/mmWave accessories |
| Packet processor + RAM + storage | 12 W | Estimate pending SoC and simultaneous CPU/DDR/USB activity |
| 2.5GbE controller/PHY + clocks | 3 W | Estimate pending exact part, temperature and cable length |
| Supervisor, watchdog, status | 0.7 W | Conservative allocation pending rail BOM |
| Miscellaneous / fan reserve | 1 W | No fan selected; cooling requirement unqualified |
| **Allocated load total** | **35.57 W** | All concurrent |

At assumed minimum point-of-load efficiency 90% and isolated converter efficiency
85%, plus 1 W primary bridge/PD/control loss:

`PD input = 35.57 / 0.90 / 0.85 + 1 = 47.50 W`.

This envelope exceeds Type 2/Class 4's 25.5 W and Type 3/Class 5's 40 W at the PD.
Type 3/Class 6 provides 51 W at the PD (60 W PSE rating); it is a **candidate**,
with only 3.5 W headroom in this envelope. Do not select a 25.5 W PD because the
modem's average power looks small. A true worst-case bound needs component maximum
losses, startup/inrush, tolerance, thermal derating, USB load and mmWave antenna
power ownership. If these exceed 51 W, reduce the design load or move to a higher
class; do not spend the same margin twice.

[TI PD controller overview](https://www.ti.com/product-category/power-management/power-over-ethernet-ics/powered-devices/overview.html)
describes a Type 3/Class 6 reference design.
[TPS2373](https://www.ti.com/product/TPS2373) distinguishes 51 W delivered PD power
from 60 W PSE output. IEEE 802.3bt power demotion must gate large loads; the
appliance may provide a fault indication on insufficient allocation but must not
boot-loop or exceed the granted power. PD status crossing the isolation barrier
requires an isolator/optocoupler or a documented module output.

Isolation has two paths: Ethernet transformer for data and isolated DC/DC for
power. Cable-side PoE return is never tied directly to system GND. All four data
pairs need 2.5G-capable magnetics with appropriate PoE current rating and accessible
cable-side center taps. Connector shield/EMC termination and surge protection
need a separate safety/EMC review; a generic RJ45 symbol proves none of this.

Modem regulator must support controlled startup, overload protection and an
independent disconnect/discharge switch. Output bulk is sized from measured
load-step duration and permitted droop, not average current. `C >= I*dt/dV` is only
the capacitive term; include ESR, regulator response, connector and copper loss.
At 3.3 V nominal the 3.135 V modem minimum leaves little droop margin. A 3.7 V
target is a candidate within both documented ranges, requiring exact SKU review.

## Assembled cost comparison

USD per unit, indicative **100-unit assembly lot**, no tax/shipping/NRE, broad
uncertainty. These are budgeting ranges, not distributor quotes. All options
include PCB, assembly, thermal/mechanical items and the same modem installation
allowances; comparing only MCU prices would be misleading.

| Assembly category | Quectel offload + MCU | Cost-reduced SoC + MCU, both vendors | LS1028A + MCU reference route |
|---|---:|---:|---:|
| MCU, clock, storage, debug, watchdog | $5–10 | $5–10 | $5–10 |
| Packet SoC + DDR + boot flash + PMIC | — | $18–35 | $45–85 |
| 2.5GbE silicon, clock, supporting power | $5–9 | $4–9 | $5–12 |
| PoE PD, bridges, isolation transformer/converter, protection | $14–25 | $16–28 | $16–28 |
| Other regulators, switching, bulk capacitors | $5–9 | $6–12 | $7–14 |
| Magnetics/RJ45, M.2, SIM, remaining passives/connectors | $8–15 | $8–15 | $8–15 |
| PCB + assembly + programming/test allowance | $12–24 | $16–30 | $22–38 |
| Enclosure, heatsink, mounting | $10–22 | $12–25 | $14–28 |
| **Assembled appliance excluding modem/antennas** | **$59–114** | **$85–164** | **$122–230** |
| Modem allowance (exact SKU/new stock quote needed) | $100–300 | $100–350 | $100–350 |
| Antennas + RF leads, sub-6 allowance | $20–60 | $20–60 | $20–60 |
| **Installed hardware estimate, sub-6** | **$179–474** | **$205–574** | **$242–640** |

SIM service, PSE/injector, cable and RF/site installation are customer infrastructure
and excluded explicitly. mmWave antenna modules and cooling are **not priced**;
EM9190 mmWave complete cost needs a separate quote. Prototype quantities likely
cost more. Low-volume purchased host modules may reduce engineering expense but
increase unit cost. Compare real quotations after architecture approval.

Availability spot-check using PCBParts/JLC database, 2026-09-28 (cached inventory,
not a reservation): RTL8125BG-CG C3013605 $4.4448 / stock 1661; STM32G0B1CCT6
C5270241 $5.1187 / stock 100. TPS3431 returned no stocked result in this index;
TI lists it active, but second-source distributor availability needs checking.
Distributor metadata is not pinout evidence (the search returned questionable
interface descriptions for another RTL8125 variant). No purchasing performed.

## Software and sourcing tradeoffs

- Quectel offload: least packet-processing hardware, but closed modem routing,
  controller-driver and DHCP behavior bind the product to a specific firmware.
  Control transport, update interruption and persistent autoconnect must be proven.
- Common USB3 host: Linux vendor drivers / QMI or MBIM plus normal routing tools;
  more storage/boot/security maintenance. Open kernel drivers reduce porting work
  but do not establish carrier or throughput qualification.
- LS1028A: manufacturer documents suitable host/network interfaces and provides a
  development ecosystem; larger package, DDR and power cost make it a feasibility
  reference, not a demonstrated cost minimum.
- Low-cost networking SoC: pursue only with exact pinout, reference schematic,
  available BSP and orderable parts. No undocumented USB3/PCIe bridge is assumed.

The next cost decision should use actual assembled quotes and an evaluation-board
throughput measurement. No component-level price comparison establishes total
minimum cost while the packet architecture remains unresolved.
