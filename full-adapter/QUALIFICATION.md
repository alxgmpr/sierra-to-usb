# Replacement-board qualification — 2026-09-09

## Delivery status

The requested integrated board has **not been implemented**. There is no new
schematic, PCB, routed layout, released BOM or fabrication/assembly package.
The following is preserved engineering research, not a design release.

Implementation has resumed. The [processor escape study](studies/README.md)
cross-checks all 636 balls and routes 114 selected signals outside the package
using three signal layers with no copper/drill-clearance violations in its first
KiCad check. It does not yet include matched pairs, an impedance-qualified
stackup, power planes, DDR devices or a bootable subsystem. These remain active
engineering work, not a demonstrated external blocker. Historical results below
are superseded only where newer evidence is explicitly linked.

## Candidate architecture, not frozen

The credible Sierra-compatible path is modem USB3 → RK3568B2 Linux host → PCIe
Gen2 x1 RTL8125BG-CG → 2.5GbE. The nominal USB and PCIe payload capacities after
8b/10b encoding are each 4 Gb/s before protocol overhead. This supports further
evaluation, but establishes neither sustained Linux forwarding speed nor modem
performance. The modem's direct Ethernet features cannot replace this path for
Sierra models.

RK809-5, two x16 H5TQ4G63EFR-RDC DDR3 devices and an 8 GB eMMC were screened as
companions. They are not a qualified subsystem. A separate CPU regulator is
required; the Rockchip guide calls for at least 4 A capability. RK809 feedback,
sequencing and DDR voltage configuration must match the actual memory type.
The Radxa ROCK 3B LPDDR4X circuit is not a drop-in reference for this DDR3 BOM.

RP2350B is a reasonable optional supervisor for GPIO, ADC, UART/SPI/I²C, modem
controls and recovery when Linux is down. Its inclusion, independent supply,
flash and reset arbitration have not been designed. MT7981BA/A remains an
unqualified alternative: its exact marking/revision, memory/power implementation
and boot support need to be established together. Fourteen live-stock parts do
not provide a stronger supply case than the RK3568B2 candidate.

External USB3 modem access would require switching both SuperSpeed pairs and
USB2 D+/D−, with break-before-make selection and hardware interlocking. VBUS
must not join hosts or back-power either host. Coupling-capacitor ownership,
off-state loading and module detection must be checked against both endpoint
documents. No mux part or circuit has been qualified; there is no implemented
host-selection circuit to validate.

## Refreshed supply evidence

PCBParts live JLC queries were collected on 2026-09-09 at approximately
15:32–15:44 UTC. Counts are a point-in-time observation, not reserved inventory.
The prices below are reported USD quantity-10 unit prices, excluding fees.
Raw queries and replies are in `research/stock-refresh-core.json` and
`research/stock-refresh-support.json`. Database results are distinguished from
live checks in those files. No parts have been ordered.

| Exact candidate | LCSC | Live count | Unit USD | Qualification status |
|---|---|---:|---:|---|
| RK3568B2 | C3345225 | 111 | 17.5365 | Exact B2 datasheet obtained; pin/rail/escape audit incomplete |
| RK809-5 | C2939628 | 2333 | 2.1103 | Datasheet obtained; sequencing and DDR configuration incomplete |
| H5TQ4G63EFR-RDC | C2803259 | 3177 | 15.8248 | Two proposed; RD speed grade correction below |
| THGBMUG6C1LBAIL | C7509349 | 840 | 31.7407 | Exact full electrical/boot qualification incomplete |
| W25N01GVZEIG | C88868 | 4812 | 9.7185 | Alternative storage only; exact boot configuration incomplete |
| RTL8125BG-CG | C3013605 | 2136 | 3.8025 | Datasheet and newer reference obtained; regulator not selected |
| RP2350B | C42415655 | 3061 | 1.1959 | Optional, not implemented |
| MT7981BA/A | C45354767 | 14 | 8.2590 | Exact variant and complete subsystem not qualified |
| TPS2373-4RGWR | C470963 | 89 | 2.6440 | PD front end only; isolated converter still required |
| TPS23730RMTR | C3189530 | 2 | 3.1126 | Insufficient public stock for ten boards |
| V24P05S | C2827281 | 1506 | 0.6086 | Rejected for PoE: manufacturer explicitly says Non-PoE |
| H24308C | C4155004 | 1052 | 0.8754 | No documented PoE DC-current/unbalance rating found in drawing |
| PLN070-ED21A05S | C17215888 | 16 | 11.6270 | Forward transformer candidate, not qualified for chosen converter |
| 750313355 | C17216829 | 0 | 10.9778 | No public assembly stock observed |
| 2250504-1 | C6662524 | 0 | 15.8606 | No public assembly stock observed; through-hole |

JLCPCB Assembly placeholder entries, including C9900136656 for RK3568B2 and
C9900146789 for MT7981BA, were rejected as supply evidence. Their nominal price
or package text must not be substituted for genuine component inventory.

The six proposed IC line items (CPU, PMIC, two DDR chips, eMMC, Ethernet IC and
optional RP2350B) total **$88.04**. This is not a board price or qualified BOM.
It excludes the CPU regulator, every other power component, PoE, magnetics,
connectors, passives, MCU flash, PCB, assembly, testing, cooling, modem, antennas,
shipping and taxes. The complete-PCBA preference is not yet satisfied.

## Manufacturer-document corrections

1. **DDR grade:** SK hynix's H5TQ4G63EFR data sheet Rev. 1.2 specifies RD as
   DDR3-1866, not the database's advertised 2133 rate. Two x16 devices would
   provide 1 GiB on a 32-bit bus. A preliminary 780 MHz DDR clock is within the
   grade and appears in Rockchip's DDR configuration tooling; that does not
   qualify timing, training, PCB topology or the final boot image.
2. **Ethernet core supply:** the Realtek reference dated 2024-08-27 requires
   both 3.3 V and 0.95 V switching regulators to operate in PWM mode at ≥1 MHz.
   Do not reuse an older conclusion that a power-save-mode core regulator is
   acceptable. BG needs the external core supply; variant-specific enable and
   resistor options must follow the BG branch of the reference. The data sheet
   gives rise-time limits of 0.5–10 ms for 3.3 V and 0.5–5 ms for 0.95 V.
3. **Signal magnetics:** JASN's catalog explicitly lists V24P05S as Non-PoE.
   H24308C's exact drawing gives four 1:1 center-tapped channels and 180 µH OCL;
   the database's 0.5 µH refers to leakage inductance. Neither a center tap nor
   a 2.5GbE label proves PoE-current or DC-unbalance suitability. V24C13SWU is
   listed as 2.5G/4PPoE/100 W in the JASN catalog, but no matching public JLC
   stock was obtained in these queries.
4. **Power transformer:** TI TIDA-050023 uses 750317065 in a flyback converter.
   The 750313355 and Bourns PLN070-ED21A05S forward transformers are not drop-in
   replacements. The Bourns 5 V/14 A example and 1750 VDC test do not alone
   establish the required converter operation or standards-compliant isolation.
5. **PoE output:** TIDA-050023's Class-6 PD design supplies 12 V × 3.7 A =
   44.4 W on PoE. A 51 W PD input allocation cannot be budgeted as 51 W of
   usable isolated output. Alternate-adapter output claims must be kept separate.

## Modem qualification boundaries

- EM9190 Rev. 8 requires supplemental VCC contacts 24, 38 and 68, alongside
  2, 4, 70, 72 and 74. The optional-VCC footnote applies to EM7690. The EM929x
  r7.2 document treats those contacts differently; there is no generic shared
  Sierra profile without exact-model checks.
- RM520N-GL V1.0 assigns pin 24 to a 1.8 V output, 38 to WLAN_TX_EN and 68 to
  reserved. Connecting the Sierra supplemental supply to them is unsafe.
  Quectel reserved contacts 20 and 22 must also be isolated.
- EM9190 assigns contacts used for Quectel SIM2 to mmWave controls. Do not copy
  a universal second-SIM circuit from the retired design.
- Profile validity must gate modem power in hardware; absent or invalid settings
  default off. A selected profile does not automatically identify the module.
  Shutdown timing, reset behavior, radio-disable voltage domains and all other
  module contacts require separate model-specific net assertions.
- RM551E has not been qualified. Neither EM919x nor EM929x family names are an
  unconditional compatibility promise. No module has been physically tested.

## Power, stackup and outstanding design work

EM9190's documented sub-6 peak is 3 A, or 9.9 W at nominal 3.3 V; the mmWave
case reaches 5 A. The Realtek maximum test-current figures give approximately
0.95 W at nominal rails under the documented test conditions. These are partial
inputs, not a worst-case system budget. Rockchip regulator current requirements
cannot be substituted for measured or specified total SoC power. Storage startup,
DDR activity, simultaneous Linux workloads, hot converter losses, accessory and
fan limits, inrush, and final modem profiles remain unresolved. **No PoE class
has been selected.** USB-C input negotiation and safe source arbitration are
also undesigned.

The exact B2 package is 19 × 19 mm with 636 balls at 0.65 mm pitch. The
reproducible screening script tests hypothetical 0.30 mm lands, 0.20 mm drills,
0.40 mm via pads and 0.10 mm traces/clearances. An isolated dogbone has about
0.110 mm via-to-land clearance, but an adjacent uniform via grid leaves only
0.05 mm for an inner trace after 0.20 mm hole-to-track clearance. It therefore
does not prove a full escape. No layer count, stackup or controlled-impedance
geometry has been approved. JLC capabilities must be applied to the actual
chosen stackup, pad/via process and complete ball map.

Rockchip's high-speed guide requires DDR matching to include package and via
lengths. USB3 uses 90 Ω differential, PCIe data 85 Ω, and PCIe reference clock
100 Ω; assigning all high-speed pairs one generic rule would be incorrect.
DDR topology, escape, power planes, return paths, isolation barrier, Ethernet
magnetics and thermal/mechanical placement must be resolved before routing a
complete board. Cooling, connector assemblies and modem/antenna clearances have
not been modeled or checked.

## Evidence and verification

`research/source-downloads.json` records source URLs, successful-download hashes
and failed attempts. Later successful retrieval supersedes earlier failure of
the same document. Downloaded PDFs remain locally under `reference/`, ignored
as in the existing repository's datasheet policy. Pinout workbook and source
metadata are preserved in git. Relevant sources include:

- [Exact RK3568B2 data sheet V2.3](https://rockchip.fr/RK3568B2%20datasheet%20V2.3.pdf?download=1)
- [Rockchip hardware/DDR reference documents mirror](https://github.com/hqnicolas/RK3568-hardware-design)
- [Rockchip DDR release notes](https://github.com/rockchip-linux/rkbin/blob/master/doc/release/RK3568_EN.md)
- [SK hynix H5TQ4G63EFR data sheet](https://onwaytech.com/static/upload/datasheet/H5TQ4G63EFR.pdf)
- [Realtek reference schematic, 2024-08-27](https://edit.wpgdadawant.com/uploads/news_file/blog/2024/16434/tech_files/sv-1729732652.pdf)
- [RTL8125BG data sheet V1.5](https://atta.szlcsc.com/upload/public/pdf/source/20220512/84CEBB847F37F5F3AD7D5F5F4E80AB39.pdf)
- [JASN magnetics catalog](https://datasheet.lcsc.com/datasheet/pdf/043053ce7686c2cd4127f63a47fbe8fc.pdf?productCode=C20071250)
- [H24308C drawing](https://datasheet.lcsc.com/datasheet/pdf/10019263ded40dacc82a48fff3871b8d.pdf?productCode=C4155004)
- [TI TIDA-050023 design guide](https://www.ti.com/lit/ug/tiduel2/tiduel2.pdf)
- [Bourns PLN transformer data sheet](https://bourns.com/docs/product-datasheets/pln.pdf)
- [JLC PCB capabilities](https://jlcpcb.com/capabilities/pcb-capabilities/)

KiCad CLI 10.99.0 is available, but ERC, schematic/PCB parity, DRC, targeted
connectivity, route completion, layer rendering and 3D inspection are **NOT RUN:
no new CAD exists**. There are no electrical exceptions or unrouted-net waivers.
The retirement checks only establish that the obsolete tracked CAD was removed;
they are intentionally not substitutes for design checks. Fabrication files,
placement files and a schematic PDF are withheld because their source design
does not exist.
