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
