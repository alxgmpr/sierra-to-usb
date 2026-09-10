# Cost checkpoint — 2026-09-10

The captured schematic BOM is **$108.65 per board** at the catalog's reported
quantity-10 unit prices. A reasonable planning allowance for the complete board
is **$160–220 in components** and **$200–300 assembled per board for ten boards**.
These are USD estimates, not an uploaded-design JLCPCB quote. The integrated
PCB has not been placed/routed, and its dimensions and stackup are not frozen.

## Captured components

The XML netlist exported from schematic checkpoint `289e747` contains 361 fitted
components with 60 distinct LCSC codes. Two DNP capacitors and 18 copper-only
testpoints/net ties were excluded. Each captured MPN matches the corresponding
catalog lookup. Prices were retrieved through PCBParts `jlc_get_part` on
2026-09-10; this is a catalog snapshot, not a live checkout or reserved stock.

| Captured item | USD per board |
|---|---:|
| SanDisk SDINBDG4-8G, 8 GB eMMC | 34.54 |
| Two H5TQ4G63EFR-RDC DDR3 devices, 1 GiB total | 31.60 |
| Rockchip RK3568B2 | 16.89 |
| RTL8125BG-CG Ethernet controller | 3.80 |
| All other captured components | 21.82 |
| **Captured component total** | **108.65** |

The remaining captured components include PMIC/regulators, inductors, 64 fitted
22 uF capacitors ($8.34 at this conservative price tier), clocks, recovery USB,
console, reset/control circuitry, buttons and other passives. The calculation
uses `price_10` for every line; actual batch quantities may give better tiers,
especially for common capacitors. Procurement minimums and assembly attrition
are additional quote items. The raw part responses, references, quantities and
line extensions are in [the cost snapshot](research/cost-snapshot-2026-09-10.json).

The earlier $88.04 number in QUALIFICATION.md is a historical candidate-IC
subtotal using a different eMMC and optional RP2350. It is superseded for costing
the captured schematic by this netlist-based checkpoint.

## Complete-board planning allowance

| Item | USD per board, ten-board run |
|---|---:|
| Complete component BOM | 160–220 |
| Bare PCB | 10–30 |
| Assembly, setup allocation and inspection, excluding components | 25–50 |
| **Assembled board, rounded planning range** | **200–300** |

The unfinished component allowance is approximately $50–110 above the captured
BOM. It covers isolated PoE conversion and protection, qualified Ethernet
magnetics/RJ45, M.2/SIM connectors, modem power, auxiliary USB-C power and source
arbitration, remaining development interfaces and practical host selection.
Those parts are not yet a final qualified BOM; the range is an engineering
allowance, not the sum of selected orderable parts.

The bare-PCB allowance assumes roughly 100 × 150 mm, six to eight layers,
conventional through vias and controlled impedance. These are costing
assumptions, not chosen dimensions or a stackup decision. A larger board, HDI,
filled/capped vias or other premium processing would require a new estimate.

Assembly assumes Standard PCBA and roughly 80–110 final distinct component
types, with possible placement on both sides. JLC's fee page updated 2026-09-09
lists $51.12 double-sided setup, $16.42 double-sided stencil, $1.53 feeder loading
per basic/extended type, and $0.0016 per SMT joint in this quantity range.
Fixtures, X-ray inspection and any manual operations also contribute. These
fees support the assembly allowance; the final quote requires the actual
BOM, placement and board files. Source: [JLCPCB assembly pricing](https://jlcpcb.com/help/article/pcb-assembly-price).

For five boards, allow roughly **$230–350 each** because setup, tooling and
component-loading costs are spread across fewer boards. Neither batch estimate
includes cellular modem, antennas/coax, SIM/service, heatsink/fan, enclosure,
cables, shipping, taxes, engineering or a custom functional-test service.
JLC assembly and X-ray inspection do not establish successful Linux boot or
modem/network functionality. No purchase or fabrication order was made.

## Alternatives actually evaluated

These were architecture and sourcing screens, not completed competing PCB
implementations or measured performance comparisons. The original objective
explicitly asks to evaluate RK3568B2 first while retaining Sierra-compatible
Linux hosting.

| Option | Recorded outcome |
|---|---|
| RK3568B2 + DDR/PMIC/eMMC + RTL8125BG | Current implementation path. Better documented public supply than the MediaTek candidate in the recorded screen; external memory and power circuitry add substantial cost. |
| MT7981BA/A | Conditional Linux/router alternative. About $8.26 per processor in the September 9 screen, but only 14 public-stock parts; exact variant, memory/power and boot implementation were not qualified. |
| RK3566 | About $11.73 per processor in the same screen. Denser BGA package needed an escape assessment, so lower processor price did not establish a cheaper complete PCBA. |
| MT7986, MT7988, Allwinner T527 | Screened for JLC sourcing. No credible stocked exact processor established in those searches; assembly placeholder entries were rejected. This is not proof that special sourcing is impossible. |
| RP2350B + modem-direct RTL8125BG path | Much cheaper core chips, about $5 combined in the screen, for compatible Quectel operation. Does not meet the required Sierra USB3-to-Ethernet path. RP2350 remains an optional supervisor alongside Linux. |

Supporting-part alternatives included discrete Ethernet magnetics plus a plain
RJ45 versus an integrated PoE magjack, several PoE controllers/transformers,
and alternative eMMC/SPI NAND parts. None establishes a complete lower-cost
replacement board. Details and dated supply evidence are in the
[architecture sourcing screen](../docs/jlc-manufacturability-2026-09-09.md) and
[qualification record](QUALIFICATION.md).

There is no completed like-for-like cost/performance comparison against retail
5G routers, SBCs or compute-module carrier solutions in the current record.
The custom board has not been demonstrated to beat those products on price.
The $66.15 memory subtotal is the largest obvious cost-reduction target;
cheaper compatible memory/storage would need electrical, boot and sourcing
qualification before substitution.
