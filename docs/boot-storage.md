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

## Candidate investigation — 2026-10-04

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
