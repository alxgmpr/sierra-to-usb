# Current capture checkpoint — not for fabrication

Open `full-adapter.kicad_pro`. The root hierarchy currently contains the DDR
signal and power pages, processor core power and ground, the CPU regulator,
the nine PMIC LDO outputs, and the DDR regulator.
The integrated PCB and remaining functional pages
are still being implemented.

U1 is the exact RK3568B2; U2/U3 are H5TQ4G63EFR-RDC, each 4 Gb x16, giving
1 GiB on one 32-bit rank. Both processor DDR supply domains and both DRAM
supplies use 1.5 V. The initial 780 MHz clock target still requires DDR loader
configuration and physical training tests. The RD speed grade is 1866 MT/s,
not the 2133 MT/s sometimes attached to distributor listings.

`../tools/check_ddr.py` exports a fresh KiCad XML netlist and checks every DQ,
DQS, DM, shared command/address and clock connection against the reviewed
manufacturer maps. It separately checks fixed physical-ball anchors, reference
and calibration circuits, all DRAM supplies, all decoupling, and exact part
fields. All 732 processor/memory symbol pins are unique and match the reviewed
names and footprint coordinates.

The core power sheet connects 30 CPU/LOGIC/GPU/NPU supply balls, 21 bypass
capacitors, and all 208 VSS/AVSS ground balls. `../tools/check_core_power.py`
checks their fresh exported nets against fixed package anchors and the source
ground-pin list. Ball M15 is a passive remote sense tap on VDD_CPU_COM, not an
additional external power feed. TVSS at AB24 remains a temperature reference
input and is not connected to ground.

U4 is RK860-0 with L300 SPM5030T-R35M. The CPU page includes four 22 uF input
capacitors, four 22 uF local output capacitors, a 51 kohm / 100 nF hardware
enable delay, a 100 kohm VSEL pull-down and the reference 100 ohm / 1 uF remote
sense network. `check_cpu_regulator.py` checks all 20 balls, native stack
expansion, switching-node isolation, feedback, defaults and exact passives.
The VDD_CPU power flag represents the verified U4 → L300 → CPU supply path;
KiCad does not propagate a power-output type through the passive inductor.

U5 is the exact RK809-5. Its three LDO groups have twelve local 1 uF bypass
capacitors and the startup voltages/sequencing from datasheet Table 4-4.
LDO6 now supplies the CPU regulator enable resistor. LDO5/6 are limited to
200 mA with less than 0.4 V headroom, as specified on datasheet pages 22–23.
`check_pmic_ldo.py` verifies all physical input/output pins and capacitor nets.

BUCK3 now supplies VCC_DDR through L420, with two local input and three local
output capacitors. Its 87.6k / 100k, 0.1% hardware divider selects 1.5008 V
before firmware runs. `check_pmic_ddr.py` verifies switching-node isolation,
the separate FB3 divider, VBUCK3 sense and resistor tolerance arithmetic.
The VCC_DDR flag represents this physical buck/inductor path.

The current ERC result has seventeen **unresolved integration findings**, with no
ERC exclusions: unplaced U1/U5 units, input pins, bidirectional pins and power
pins; six undriven rails (GND, LOGIC/GPU/NPU, VCC5V_SYS and
VCC3V3_SYS); isolated CPU regulator SDA/SCL labels; and undriven SCL. The remaining PMIC units,
upstream supplies and other processor units are not yet captured. These are
open work, not manufacturing exceptions. There are no
additional ERC findings in this checkpoint.

The schematic PDF was rendered and visually iterated to fix rotated passive
fields, supply-reference overlap, power-label collisions and page-boundary
placement. The checked working render is `../build/pmic-ddr-review.pdf`; it is
not a released schematic or fabrication deliverable.

## Library review

The Hynix map was checked against all 96 cells of manufacturer Rev. 1.2,
September 2016, page 6, with the overbars reviewed visually. Page 33 verifies
7.5 x 13 mm, 0.8 mm pitch and the top/bottom view orientation. The vendored
KiCad footprint's 0.36 mm lands are an engineering choice; the package drawing
does not specify a manufacturer land pattern. Source hashes are retained in
`../research/memory-pins.json`.

The official KiCad Library Tools checker at revision
`475bd27b9a521418c3732ff2ee5efea98525d2c7` reports these project-library exceptions:

- S4.5: 48 absent Hynix grid positions and 148 absent Rockchip grid positions.
  They are physically unpopulated, independently verified against manufacturer
  ball maps and footprint pads. They must not become symbol pins.
- S6.2: Manufacturer, MPN and LCSC are intentional assembly metadata on both ICs.
- The VCC_DDR and four core power symbols are renamed native KiCad 10.99 VDD symbols. The
  checker expects the older hidden/name-bearing power-pin convention and flags
  its native blank visible pin and reference convention (S4.1/S6.1/S7.1).
  KiCad's fresh exported netlist confirms the resulting global VCC_DDR net.

No actual component pin is hidden except the five NC balls on each Hynix
package. All populated balls remain explicit; alternate command functions use
KiCad alternates. Unused processor interfaces remain visible in separate units.

## Reproduction

Run from the repository root with `full-adapter/.venv/bin/python`:

1. `full-adapter/research/extract_memory_pins.py`
2. `full-adapter/tools/build_core_symbols.py`
3. `full-adapter/tools/build_ddr_schematic.py`
4. `full-adapter/tools/check_ddr.py full-adapter full-adapter/research/ddr-validation.json`
5. `full-adapter/tools/check_core_power.py`
6. `full-adapter/tools/check_cpu_regulator.py`
7. `full-adapter/tools/check_pmic_library.py`
8. `full-adapter/tools/check_pmic_ldo.py`
9. `full-adapter/tools/check_pmic_ddr.py`

The pre-commit checks validate the staged snapshot and reject unregistered CAD.
Their DDR checkpoint success does not authorize fabrication or imply that the
full board is electrically complete or routed.
