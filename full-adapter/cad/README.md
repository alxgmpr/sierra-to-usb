# Current capture checkpoint — not for fabrication

Open `full-adapter.kicad_pro`. The root hierarchy currently contains the DDR
signal and power pages plus processor core power and ground. The integrated PCB and remaining functional pages
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

The current ERC result has eleven **unresolved integration findings**, with no
ERC exclusions: unplaced U1 units, input pins, bidirectional pins and power
pins; six undriven rails (VCC_DDR, GND, and the four core rails); and the isolated
VDD_CPU_COM label awaiting the regulator feedback circuit. The PMIC, CPU
regulator circuit and other processor units are not yet captured. These are
open work, not manufacturing exceptions. There are no
additional ERC findings in this checkpoint.

The schematic PDF was rendered and visually iterated to fix rotated passive
fields, supply-reference overlap, power-label collisions and page-boundary
placement. The checked working render is `../build/core-power-review.pdf`; it is
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

The pre-commit checks validate the staged snapshot and reject unregistered CAD.
Their DDR checkpoint success does not authorize fabrication or imply that the
full board is electrically complete or routed.
