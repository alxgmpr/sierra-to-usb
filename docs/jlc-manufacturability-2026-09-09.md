> Historical evidence from superseded designs. See the [current full adapter](../full-adapter/README.md). Circuit status and artifact paths below refer to the historical checkpoint, not the replacement.

# Full adapter: JLCPCB manufacturability screen
Date: 2026-09-09. Architecture assessment only; no schematic changes, orders, inventory reservations, PCB escape study, or assembly quote.

## Recommendation
The earlier MT7986 recommendation was based on architecture, not procurement. For a public-stock-first JLCPCB build, do not freeze MT7986: current live search returned only zero-stock JLCPCB Assembly entries. RP2350B + RTL8125BG-CG is the most approachable assembly architecture if compatible Quectel-only Ethernet operation is acceptable. This does not solve Sierra Ethernet.

For Sierra-capable Linux hosting, MT7981BA/A is a conditional candidate (only 14 public parts; confirm exact suffix against reference documentation and boot software). RK3568B2 is a more available alternative in this snapshot, but requires external DDR, PMIC, storage and PCIe NIC. RK3566 has stock too, but its denser package needs an escape-routing assessment; lower chip price alone does not establish a lower PCBA price. No Linux option is fully procurement-qualified yet.

## Live JLCPCB lookup
PCBParts jlc_search database was used first; jlc_stock_check then queried live JLCPCB data, including zero-stock listings. The raw responses are saved in jlc-manufacturability-stock-2026-09-09.json. USD quantities below use the live tool's price_10 field, not an assembly quote.

| Exact MPN | C number | Live quantity | USD each, 10+ | Package |
|---|---|---:|---:|---|
| RP2350B | C42415655 | 3061 | 1.1959 | QFN-80-EP, 10×10 |
| RTL8125BG-CG | C3013605 | 2136 | 3.8025 | QFN-48-EP, 6×6 |
| MT7981BA/A | C45354767 | 14 | 8.2590 | TFBGA, 13×11.7 |
| RK3566 | C2943786 | 293 | 11.7263 | BGA-565 |
| RK3568B2 | C3345225 | 111 | 17.5365 | FCCSP-636L |
| RK3568 | C2938930 | 157 | 19.7330 | BGA-636 |
| RTL8221B-VB-CG | C5155988 | 4594 | 3.0101 | QFN-48 |
| TPS23730RMTR | C3189530 | 2 | 3.1126 | VQFN-45 |
| Würth 750313355 | C17216829 | 0 | 10.9778 | Package not resolved |
| Bel 2250504-1 | C6662524 | 0 | 15.8606 | Through-hole |

All rows above are Extended. Stock may change; price breaks do not reserve stock. Zero-stock prices are not proof of purchase availability.

MT7986: only zero-stock assembly entries C9900094679 / C9900205587 returned. MT7988: no results. T527: broad text search includes unrelated capacitors and assembly entries, so no stocked exact Allwinner processor was established. C990... entries with manufacturer “JLCPCB Assembly” and nominal tiny prices are not treated as stocked purchasable processors. These searches are not proof that special sourcing is impossible.

## Supporting components and incomplete subsystems
Database-level checks found:
- RK809-5 PMIC, C2939628: 2467.
- W25Q128JVSIQ NOR, C97521: 94429; Basic listing. This is an example for MCU/recovery storage, not a selected complete Linux storage solution.
- H5TQ4G63EFR-RDC DDR3, C2803259: 3177.
- W25N01GVZEIG SPI NAND, C88868: 5301.
- LOTES APCI0105-P001A M.2 Key-B socket, C841658: 2911.
- TPS2378DDAR PoE PD interface, C337500: 4644. It requires a separate conversion design; not a drop-in TPS23730 replacement.

These are sourcing leads, not a matched/approved processor-memory-PMIC BOM. Exact memory voltage, bus width, capacity, bootloader support, PMIC sequencing and package drawings remain to be checked. The natural-language query “DDR3 256M” was incorrectly parsed as a resistor search; it was discarded and replaced by exact MPN searches.

The original project used a Würth power transformer and Bel 2.5GbE PoE magjack sourced outside JLC. Both now have catalog codes but zero live public stock. The original TPS23730 has only two. Thus the old power/Ethernet connector implementation is not ready for a public-stock-only batch.

Discrete Ethernet magnetics are a promising alternative to a scarce integrated magjack:
- JASN V24P05S, C2827281: 1506, cataloged 2.5G/PoE; 10+ USD 0.6086.
- E-NETTR H24308C, C4155004: 1052, cataloged 2.5G/PoE; 10+ USD 0.8754.
Neither is approved. Check manufacturer schematic, pair count, center taps, PoE DC current/unbalance, loss/return loss, isolation, PHY compatibility and footprint. LAN magnetics do not replace the isolated DC/DC power transformer. A plain RJ45 plus qualified discrete magnetics may broaden sourcing, at the cost of PCB area and routing.

## Assembly and PCB constraints
[JLCPCB assembly capabilities](https://jlcpcb.com/capabilities/pcb-assembly-capabilities) currently list:
- Economic: 2/4/6 layers, single-sided placement, 0402 minimum package, 0.5 mm minimum BGA pitch, standard stackups.
- Standard: double-sided placement available, 0201 minimum package, 0.35 mm minimum BGA pitch.
- X-ray inspection for hidden joints and mixed SMT/through-hole assembly are supported.

Those are service capabilities, not approval of this design. Plan the RP2350 version for single-sided assembly and accessible passives, with 4–6 layers evaluated against impedance and density. A processor with external DDR needs an early escape-routing and power-distribution study; evaluate 6–8 layers and Standard PCBA where required. Do not claim HDI is mandatory or unnecessary until checking actual ball maps, pad sizes, drills, annular rings and stackup. Assembly pitch acceptance does not establish routability.

The original 0603/hand-soldering preference should not force long decoupling paths around a Linux SoC. Any smaller passives should be explicitly justified at layout selection.

LCSC stock and JLC public assembly stock are distinct procurement states. [JLC sourcing instructions](https://jlcpcb.com/help/article/pcba-parts-sourcing-instruction) allow public stock, preorders, global sourcing and consigned inventory, but sourced components must arrive before use in an assembly order. For this project, prefer public stock and use private sourcing only for documented exceptions.

## What closes the decision
1. Decide whether Ethernet must support Sierra: this determines whether the MCU-only architecture can satisfy the requirement.
2. For a Linux candidate, qualify a complete exact-MPN processor/RAM/PMIC/flash/PHY cluster and replenish/reserve scarce parts before layout freeze.
3. Resolve PoE controller, isolated power transformer and 2.5GbE signal magnetics as separate design decisions.
4. Verify package/footprint drawings, silicon revision, references and license/access to required documentation.
5. Complete BGA escape and impedance study, DFM quote, BOM/CPL mapping and placement orientation verification.
6. Provide programming/recovery access and a functional test procedure: rails, boot/memory, modem USB3 enumeration, Ethernet link, traffic, PoE startup/load and thermal behavior. X-ray/ERC/DRC do not demonstrate these functions.

No claim of measured 2.5Gbps modem routing, completed board manufacturing qualification, or exact total PCBA price is made.
