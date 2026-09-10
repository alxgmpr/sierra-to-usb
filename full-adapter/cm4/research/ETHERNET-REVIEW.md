# Native gigabit Ethernet capture, 2026-09-10

T120, J120, U120/U121 and the termination network are now in the current CM4
hierarchy. The eight-page project still has 48 unfinished integration ERC
findings and no carrier PCB. This review qualifies the captured pin mapping and
lands; it is not system electrical or manufacturing release.

Manufacturer documents, versions and hashes are in `ethernet-sources.json`.
The current Molex PDF was retrieved through a browser request after command-line
downloads failed; its revision is B3, with the revised PCB layout. The old Pulse
selector is superseded by the current JK0-0177NL drawing: that magjack supports
only 30 W PD over four pairs and was rejected. The selected separate magnetics
and connector avoid that limitation.

## Electrical mapping

- HX6096NL: four 1:1 channels with chip-side CMC; 350 uH at 25 C / 300 uH across
  temperature, tested at 24 mA DC bias. Rated 720 mA at 57 V continuously;
  half-winding resistance 0.30 ohm typical and centre-tap resistance balance
  +/-0.05 ohm maximum. Primary isolation is 1500 Vrms for 60 seconds.
- CM4 pair 0 maps to T120 2/3, media 23/22, RJ45 1/2. Pair 1 maps to 5/6,
  20/19, RJ45 3/6. Pair 2 maps to 8/9, 17/16, RJ45 4/5. Pair 3 maps to 11/12,
  14/13, RJ45 7/8. All polarities match the CM4 datasheet.
- Chip centre taps 1/4/7/10 each use 100 nF to GND, as in CM4 datasheet Figure 2.
  They do not connect to 3.3 V. Media taps 24/21/18/15 remain independent and
  feed the future two PoE bridge inputs.
- Molex 855437002 is Cat5e per PS-85543-002, 125 VDC and 1.5 A per contact.
  The stated signal-to-shield proof voltage is **1500 V DC or AC peak**, not
  1500 Vrms. Do not mislabel the complete port's isolation test from the
  transformer rating alone. The final PoE assembly test must respect every
  component's specified isolation test, including the selected PD module.
- U120/U121 are the 10-pin DQA TPD4EUSB30, on the PHY side. Pins 1/2/4/5 protect
  signals, 3/8 are grounded, 6/7/9/10 are unconnected. No supply pin exists.
  The 5.5 V standoff arrays must never be placed on the 57 V cable side.
- Each media centre tap has a 22 nF / 100 V series capacitor before its 75 ohm
  resistor. The common termination star reaches secondary GND only through
  C134, exact Dersonic CY1102ME14EF45W2A2, 1 nF, Y1, 400 VAC. Thus opposite
  PoE polarities are not connected by DC termination resistors. Shell is GND.

## Lands and model review

Official KiCad Library Tools primitives generate all four custom footprints.
The standard USON-10 footprint did not match the exact TI DQA grounds and
signal-land dimensions, so a dedicated footprint is used.

- Pulse lands: 0.762 x 1.905 mm, 1.27 mm pitch, row centres +/-7.3025 mm.
  Pin 1 is lower left, 12 lower right, 13 upper right, 24 upper left.
- Molex B3 PCB pattern: 0.76 x 6.35 mm signal lands, 1.27 mm pitch. Origin is
  the PCB edge, port faces +Y. Signal pad centres are y=-18.515 mm. Shield pads
  are 2.54 x 3.60 mm, x=+/-8.085 mm, y=-4.740 mm. These derive from the drawing's
  15.15 mm pad-top separation, 6.54 mm shield-pad-top to PCB edge, and 0.4 mm
  housing overhang; the signal row is not assumed centred on the housing edge.
  The manufacturer housing keepout is a front-copper rule area. Signal escapes
  leave from the rear; no routing under the shielded housing on the top layer.
- TI signal pads: 0.565 x 0.20 mm, row centres +/-0.4175 mm, 0.5 mm pitch.
  Both ground lands are 0.4 mm wide as in DQA0010A and joined for the exposed
  central ground in DQA0010B. This is an explicit A/B-compatible land choice;
  it retains the larger A ground wings, rather than B's 0.3 mm outer wings.
  Final stencil review must account for the combined ground opening and vias.
- Dersonic: 10 mm lead pitch, 1.0 mm finished holes for 0.6 +/-0.1 mm wire,
  2 mm pads. Leads require normal forming/insertion to nominal 10 mm pitch.
  Maximum body envelope is 7.3 mm diameter x 5.2 mm thick, with 10.3 mm reserved
  height including coating rundown. It is a separately soldered through-hole
  part unless the assembler quotes that operation.

Generated STEP files are maximum mechanical envelopes, not vendor product
models. The RJ45 model is a closed housing envelope; plug/latch service space
must be added in the carrier mechanical constraints. Models are checked for
file existence and valid imported solids. The ignored library review fixture
contains only four footprints; it is not the integrated PCB.

## Checks and remaining work

`check_ethernet.py` independently checks fixed manufacturer pin anchors, all
four exported MDI and cable pairs, eight ESD channels, isolation-capacitor paths,
exact MPNs, NC contacts and pad coordinates. `check_core.py` invokes it in the
staged checks. Eight isolated MDI findings were resolved by actual connections;
no ERC exclusions were added. The root and new schematic pages were rendered
and reviewed; ESD field overlap was corrected.

PoE bridges, PD converter, completed simultaneous power budget and class,
isolation clearances, winding-current imbalance, converter thermal budget,
MDI routing, enclosure bonds and EMC/surge tests remain part of integration.
Keep 100 ohm MDI pairs short, maintain a continuous secondary reference until
the transformer, and apply the CM4 intrapair skew target (<0.15 mm). Do not use
the PHY-side ESD component alone as evidence of complete port surge compliance.

Captured JLC prices are in `ethernet-parts.json` and `ethernet-passives.json`.
Use the explicit quantity break arrays: the API's `price_10` field can refer to
a higher quantity. At ten boards, the selected jack, transformer, two ESD arrays,
four termination resistors, four 22 nF capacitors and Y1 capacitor total about
$5.515 per board, before the four 100 nF bypass capacitors and assembly. This
is a catalog calculation, not a complete BOM total or a JLC quote.
