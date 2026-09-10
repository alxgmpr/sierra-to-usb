# CM4 core capture review, 2026-09-10

This is a capture milestone, not an electrically complete board or a release.
The six-page hierarchy contains both 100-pin sockets, local 5 V bypass, microSD
data and power switching, and four physical control buttons. Exported-net
assertions verify 200 contacts, two physical socket BOM entries, six SD data
connections, native power-stack expansion, rail separation and button wiring.
The remaining 56 ERC findings are tracked unfinished integration; no exclusions
are installed. No CM4 PCB has yet been created at this milestone.

Sources: current [CM4 datasheet](https://datasheets.raspberrypi.com/cm4/cm4-datasheet.pdf),
[official CM4IO archive](https://datasheets.raspberrypi.com/cm4io/CM4IO-KiCAD.zip),
[Hirose drawing](https://www.hirose.com/en/product/document?clcode=CL0684-4033-4-58&documentid=0001210104&documenttype=2DDrawing&lang=en&productname=DF40C-100DS-0.4V%2858%29&series=DF40),
and [Richtek DS9742-10](https://www.richtek.com/assets/product_file/RT9742/DS9742-10.pdf).
CM4 source hashes and independently extracted names are in `cm4-pins.json`.

The official archive README supplies no separate general CAD license; the
Raspberry Pi USB3 application note explicitly permits using relevant sections
in designs using Raspberry Pi products. Connector symbols here are newly drawn
from factual pin tables. The standard KiCad Hirose footprint is vendored
unchanged from the installed KiCad library. Its 0.4 mm pitch, 0.2 x 0.7 mm lands,
19.6 mm pin-row span and 3.08 mm row-centre separation match the manufacturer
drawing. Hirose specifies 120 um stencil thickness and 80% aperture opening;
paste reduction still needs incorporation into the assembly release.

The Molex footprint is from the official CM4IO reference; physical shell pads
11 have been renamed SH to match the current KiCad Micro_SD_Card_Det2 symbol.
Its manufacturer drawing, modern footprint formatting and STEP model require
final verification. It must not be treated as qualified merely because it
appears in the reference. Alps switch footprint/model are reused from the
previous manufacturer-reviewed capture; only the local model path changed.

CM4 datasheet Figure 4 sets the module to 55 x 40 mm, connector centres at
3 and 37 mm across the 40 mm dimension, four M2.5 holes 3.5 mm from edges,
and the connector longitudinal centre 25 mm from the end of the 55 mm dimension.
The reference archive combined footprint has a 33.92 mm connector separation;
do not inherit that old placement blindly. Final placement must use the current
34.00 mm dimension and independently verify top/bottom pin orientation.
The selected 1.5 mm mating height gives **zero guaranteed component clearance
under CM4**, so the carrier must keep components out of that region.

The CM4IO legacy symbol incorrectly labels Ethernet SYNC as 1.8 V and SYNC_OUT
as input; the current datasheet specifies 3.3 V signalling and output direction.
Unused SYNC contacts are disconnected. Differential pin names retain P/N
suffixes. The CM4 already contains PCIe TX/clock AC capacitors; external
controller TX capacitors remain required. Native USB2 is a recovery interface.

CM4_3V3 and CM4_1V8 are internally generated outputs, each limited to 600 mA
total. They are kept separate from the 5 V input. GPIO_VREF is tied to CM4_3V3.
The microSD switch defaults on through 10kR and can discharge its output when
disabled. Its 1 A limit does not establish a 600 mA source protection limit:
SD/accessory current budget and fault behaviour remain open integration work.
Actual microSD model, effective MLCC capacitance, inrush, ESD and external-port
backfeed also require closure. CM4 operating current in its datasheet is
typical, not a worst-case load guarantee.

Local review PDF/PNGs are under ignored `build/`. All six sheets were inspected;
power-stack overlap and global-label alignment were corrected. Layout will be
compacted as the remaining interfaces are integrated. The KLC checker reports
intentional assembly fields and its incompatibility with KiCad 10.99 native
power-symbol conventions (blank visible pin and reference convention).
Footprint existence is independently checked; no KLC output is a release waiver.

Renesas status: catalog C3025201 is the -711 variant; C2916548 is -701. Linux
`xhci-pci-renesas.c` implements loading `renesas_usb_fw.mem`. The current
manufacturer manual/datasheet URLs require access (HTTP 403). The LCSC
datasheet mirror downloaded successfully but is scanned Rev.5.00 (2013), not
the current manual. Official forum material distinguishes -711 firmware loading
from -701 serial-ROM operation. Do not assume those suffixes differ only in
temperature. Firmware acquisition, licence, exact variant and reset/rail
qualification remain open; independent CM4 capture continues.
