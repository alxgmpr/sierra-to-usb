# DDR selection remains open

NanoPi R3S LTS 2411 sheet 7 uses a generic LPDDR4_200p symbol, not
an exact manufacturer MPN. FriendlyElec specifies 1/2 GB LPDDR4X for
R3S. The reference therefore proves an architecture, not our exact BOM.

A 2 GB x32, 200-ball Micron candidate is MT53E512M32D1ZW family.
The manufacturer catalog lists MT53E512M32D1ZW-046BWT:B as Production,
16 Gb, 4266 MT/s, 1.1/0.6 V, -25 to +85 C, 10 x 14.5 x 1.05 mm.
The indexed assembly database instead returns MT53E512M32D1ZW-046 WT:B
(C5330500, 38 indexed units). Do not assume these strings establish the
same orderable revision without manufacturer clarification.

Production datasheet Embedded LPDDR4/LPDDR4X SDRAM (Z42M) covers
MT53E512M32D1 / MT53E1G32D2 / MT53E512M64D2 and is access-controlled
on the manufacturer site. Public marketing voltage data is insufficient
for package-ball, current, timing and power-sequence capture. Automotive
AAT:B variant is Contact Sales in manufacturer catalog. Do not replace
missing data with a distributor single-rail voltage description.

Required before selection: exact revision and lifecycle, complete controlled
ball table, VDD1/VDD2/VDDQ ranges and sequencing, current/decoupling,
RK3566 DDR training support for this density/die, and assembly availability.
LPDDR4X requires a separate 0.6 V domain per RK3566 hardware guide;
BUCK3 DDR rail must not be arbitrarily set to DDR4 1.2 V.

Primary sources reviewed 2026-10-03:
- https://wiki.friendlyelec.com/wiki/index.php/NanoPi_R3S
- Archived hardware/reference/nanopi-r3s-lts-2411.pdf sheet 7.
- https://in.micron.com/products/memory/lpddr-components/lpddr4/part-catalog
- https://www.micron.com/products/memory/lpddr-components/lpddr4/part-catalog/part-detail/mt53e1g32d2fw-046-wt-b

No DDR symbol, footprint or regulator divider has been generated from this
candidate. Continued supply/processor/storage/modem work remains possible.

## Manufacturer loader and WDQS wiring requirements

Pinned rockchip-linux/rkbin revision
3e288fe814e059dd06833495f845cab04ac20a5c includes RK3566 200-ball
LPDDR4X templates and a separate WDQS loader family. The specific
release note dated 2025-11-20 requires a 560R weak pull-up on DQSn
for WDQS support. It warns that boards without DQSn pull-ups must use
regular bin/rk35 loaders, while boards with these pull-ups must use
WDQS loaders; mismatching them can cause reliability issues.
The template table identifies parts needing WDQS through application
notes in Rockchip's controlled DDR approved/reference vendor lists.
Those lists remain unavailable, so we cannot infer WDQS requirements
from a generic LPDDR4X marketing description or ball count.

The default RK3566MINIALL.ini uses the regular 1056MHz v1.26 loader,
USB plug v1.17 and SPL v1.14. Standard release notes report single-channel
LPDDR4/LPDDR4X support and capacity/startup fixes in v1.26. Special
mixed-package latency-mode parts require a separate v1.26 loader and
matching BL31; this does not prove our Micron candidate uses that mode.
Preserve the original RK3568 CHIP_NAME in the archived manufacturer INI;
it is not a typo we have independently qualified for correction.

Before RAM capture, resolve exact-part vendor-list classification and
DQSn pull-up requirements together with its ball map and power sequence.
Before firmware release, choose and hash the matching DDR loader and
BL31, then verify training, repeated cold/warm starts, suspend/resume,
voltage/frequency transitions and memory margins on the actual PCB.
Manufacturer full-space test notes explicitly say the test does not detect
all faulty cells; max-frequency scan is only an approximate aid.
No binary has been installed or executed on hardware.

Original manufacturer documents and SHA-256 provenance are archived in
hardware/reference/rockchip-ddr-template-table.md,
rockchip-rk3566-ddr-release.md, rockchip-rk3566-ddr-specific-release.md
and rockchip-rk3566-loader.ini, with URLs in sources.json.

## Public Micron Z42M revision located

Micron-authored Rev. I (04/2023), mirrored by RS, is readable through
web PDF extraction at https://docs.rs-online.com/a381/A700000015750630.pdf.
Local retrieval returned HTTP 403, so no original PDF/hash is archived yet.
This is an older manufacturer document hosted by a distributor, not proof
that it is Micron's latest controlled revision.

Table 2 separately lists both -046 WT:B and -046B WT:B; the part-number
chart identifies the extra B as an alternate substrate option. Therefore
the previously observed catalog strings need not be a transcription error;
they represent distinct ordering options. Exact package option must still
be frozen. Figure 5 (printed page 22) is the single-rank 200-ball map;
Figure 6 is dual-rank and must not be substituted. ZW package dimensions
are in Figure 9 (printed page 28).

Table 160 (printed page 214) gives LPDDR4X ranges: VDD1 1.70–1.95V,
VDD2 1.06–1.17V and VDDQ 0.57–0.65V, nominal 1.8/1.1/0.6V.
This removes the public voltage-data gap, but current/sequence review,
exact native model audit and WDQS classification remain pending.

## Native standard-substrate candidate preserved

C5330500 resolves exactly to MT53E512M32D1ZW-046 WT:B, the standard
substrate option. Its native EasyEDA symbol and footprint were converted
with easyeda2kicad v1.0.1 and preserved unregistered in hardware/reference.
A structural check found 200 unique symbol ball identifiers, matching all
200 footprint pad identifiers. The native pin inventory is saved as CSV.
This checks internal consistency only, not the manufacturer ball map.
The footprint's name references MT53D512M32D2DS; package identity must
therefore be established from geometry and ball map, not its library name.
The single oversized symbol and unspecified electrical pin types require
audit and readable grouping before schematic use. No production footprint
or RAM symbol has been registered. Indexed stock of 38 is not reserved.

## Power-sequence and rank-specific audit findings

Micron Rev. I printed pages 43–44 require VDD1 to rise no later than
VDD2, and VDD2 no later than VDDQ. During ramp, RESET_n stays low
and both channels initialize together. Rail ordering must be reviewed
against actual RK809 startup slots and the separate 0.6V regulator.
Printed page 46 also requires ordered shutdown; uncontrolled power loss
is limited to 400 occurrences over device life. Persistent appliance power
loss therefore needs a shutdown/hold-up review, not just startup wiring.

The native model has generic NC/second-rank aliases on H3, R3, J5, P5
and A8. These must be resolved for the selected single-rank part before
registration. No full manufacturer ball-map match is claimed from flattened
PDF text. check_micron_native.py now verifies the preserved 200-entry
inventory and symbol/footprint identity consistency.
