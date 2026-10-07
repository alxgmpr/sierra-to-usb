# Boot storage selection — in progress

Evaluate 16 GB eMMC for the signed Linux A/B architecture. This is a sizing
proposal, not a measured image size or frozen BOM selection.

| User-area allocation | Proposed maximum |
|---|---:|
| Linux slot A | 2 GiB |
| Linux slot B | 2 GiB |
| Complete update staging | 2 GiB |
| Signed recovery assets | 1 GiB |
| Configuration journal | 256 MiB |
| Rotating diagnostic logs | 512 MiB |
| Partition/alignment allowance | 128 MiB |

Total: **7.875 GiB**, or 8,455,716,864 bytes. A nominal 8 GB device is about
7.45 GiB and cannot hold this proposal. Nominal 16 GB is about 14.90 GiB;
confirm the actual user-area capacity and any enhanced-area allocation.
Do not count boot hardware partitions or RPMB as extra user-area capacity.
Build and measure the intended image before freezing capacity. Firmware has
not been implemented here. Endurance, write amplification and log write-rate
limits also remain open.

## Candidate investigation — 2026-10-04 (lifecycle hold)

[Kingston's manufacturer page](https://www.kingston.com/en/embedded/emmc-embedded-flash)
lists EMMC16G-WW28: 16 GB, eMMC 5.1 (HS400), TLC, -40 to +85 C,
11.5 x 13 x 0.9 mm. Indexed JLC lookup returned the full suffix
EMMC16G-WW28-04B22, C50146107, stock 10 and an unknown package field.
Neither catalog stock nor family specifications qualify this exact suffix.
Obtain its manufacturer-controlled ball map, electrical limits and lifecycle
before selection. Package approval is pending; no symbol/footprint generated.
The manufacturer page was read through web search; raw archive retrieval
returned HTTP 403, so no archived-source hash is claimed.

An exact Micron MTFC16GAPALBH-IT lookup found no JLC entry. Its current
manufacturer detail page exposed no populated specifications. That evidence
does not establish an orderable alternative.

## Processor-side requirements

Archived RK3566 Hardware Design Guide V1.1 section 2.1.10 specifies eMMC
4.41/4.51/5.0/5.1 and HS200. Memory-side HS400 support does not establish
processor-side HS400 support. VCCIO2 voltage must match FLASH_VOL_SEL and
the chosen memory's VCCQ limits.

The guide requires D0/CMD external 10 kR pull-ups, CLK series 22 R at the
processor, provision for a DATA_STROBE pull-down, and short D0/CLK MaskROM
recovery test-point branches. Other data lines use internal pulls in this
guide. VDDi requires at least 2.2 uF or the exact memory's larger requirement.
VCC/VCCQ must be stable before commands; restore VCC before wake.

Exact supported memory list is on Rockchip's controlled support portal;
candidate compatibility remains unproved. Capture requires the selected
memory's reset policy, boot-partition configuration, supplies/bypassing and
processor integration. Retain independent USB MaskROM recovery: an eMMC
recovery partition cannot recover a failed eMMC or corrupt boot configuration.

## Exact-suffix lifecycle and firmware-mode audit

The [DigiKey exact-part page](https://www.digikey.com/en/products/detail/kingston-technology/EMMC16G-WW28-04B22/26975041)
lists EMMC16G-WW28-04B22 as Last Time Buy. A regional listing also reports
Not Recommended for New Designs. Do not freeze this ordering code from its
small indexed stock alone; request current manufacturer lifecycle evidence or
choose a supported successor. This lifecycle hold supersedes its earlier
candidate-family status; no replacement is selected yet. Datasheets found for
-01E10, -01E22 and -03022 do not establish exact -04B22 firmware behavior.

[Kingston's firmware configuration guide](https://media.kingston.com/pdfs/embedded/firmware-config_us.pdf)
distinguishes native NAND, fixed pSLC and Dynamic Boost. Fixed pSLC converts
TLC capacity to one third (MLC to one half); Dynamic Boost retains native
reported capacity but can reduce lifetime writes. For bounded router logging,
evaluate native mode without Dynamic Boost and obtain exact suffix mapping
from the manufacturer. Do not assume suffix decoding from another device.

The 7.875 GiB proposal therefore needs at least 8,455,716,864 bytes of actual
usable user area after firmware configuration. Nominal 16 GB TLC in full-device
pSLC mode would provide only about 4.97 GiB before other reservations, which
is insufficient. Nominal 32 GB TLC in that mode is about 9.93 GiB, subject to
exact-device user-area sizing; this is arithmetic, not a replacement selection.
Partial enhanced areas need separate accounting and endurance review.

The Kingston guide was read through the web tool. Direct raw PDF retrieval
returned HTTP 403; no archived PDF or hash is claimed.

The RK3566 guide section 2.1.4 specifies FLASH_VOL_SEL high during reset for
1.8 V VCCIO2, low for 3.3 V. Preserve this hardware strap requirement in
processor capture; a later software IO setting cannot substitute for the
correct boot strap and physical IO voltage.

## Supported-family investigation

ISSI IS21ES16G-JCLI has a public manufacturer datasheet, but exact catalog
C1236835 reports stock zero. Distributor search names IS21TF16G-JCLI as a
recommended successor; the indexed lookup has no exact entry. The newer
IS21/22TF family datasheet URL is known, but direct retrieval returned HTML
instead of a PDF and web retrieval returned 403. No file, hash or extracted
ball map is claimed for it. Do not equate a successor listing with component
availability or validated RK3566 compatibility.

Swissbit's manufacturer host-compatibility report Rev 1.0, 28-Feb-2024 is
archived as hardware/reference/swissbit-em30-host-compatibility.pdf with source
and hash in sources.json. Its table 2 explicitly tests the 16 GB TLC device
**SFEM016GB2ED1TO-I-5E-111-STD** (the generation suffix ends in letter O,
not zero). Other test devices include 64/256 GB TLC and 20/80 GB pSLC.

Tests include read/write, filesystem and OS boot at ambient temperature. The
listed Rockchip platform is RK3288 on ASUS Tinker Board S R2.0, **not RK3566**.
This source does not close the processor compatibility gate. Its family-wide
controller/NAND compatibility statement is reference evidence; the report
still calls for validation in the customer's system. Exact-part electrical
data, lifecycle, sourcing, package approval and RK3566 support remain open.

Source: https://www.swissbit.com/files/public/data-symlink/EM-30/Swissbit_Host_Chipset_eMMC_Compatibility_EM-30_Series.pdf
