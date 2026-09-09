# RK809-5 capture preparation

The selected part is **RK809-5, C2939628**. The live query in `pmic-stock.json`
reports 2,333 units. RK809-5A and the zero-stock JLCPCB Assembly placeholder
are not substitutes for the qualified startup sequence.

`pmic-pins.json` records all 68 package pins plus project pad 69 for the
unnumbered exposed ground. The manufacturer PDF hash is checked before the
pin record is regenerated. Pages 15–17 provide the pin diagram and descriptions;
page 19 provides the 7 x 7 mm, 0.35 mm pitch package drawing. These were read
and the pin/package drawings were visually inspected.

The symbol has eleven functional units: five buck groups, three LDO groups,
switch 2, system control/RTC and unused audio. All pins are explicit. INT,
PWRON and RESETB show their active-low behavior. VBUCK3 is the external output
sense input, separate from FB3. Internal VCC_1P8A/VCC_1P8D and VREF are outputs
to be bypassed, not externally supplied rails.

Rockchip's tablet reference page 22 specifies the unused audio connections:
pins 14/15/16/17/19/40 to ground; pins 18/36/37/38/35/39/41/34/32/43/42 open.
PDMCLK is clocked by the processor's PDM clock output when that data interface
is enabled. These are recorded for subsequent circuit capture; the audio
block is not part of this board's intended feature set.

The native KiCad ArtInChip QFN68 footprint has matching lead geometry and
5.49 mm exposed pad. The vendoring script preserves geometry, sixteen 0.2 mm
thermal holes with 0.5 mm lands, top and bottom thermal copper, and nine
separate paste windows. Their rectangular bounding areas total about 60.2%
of the exposed-pad area. Filled/capped vias are required by the board's
planned assembly process. Source hashes are in `pmic-footprint-source.json`.
The native STEP is 7 x 7 x 0.9 mm: a conservative clearance envelope 0.1 mm
taller than RK809's maximum, not a manufacturer STEP model.

`check_pmic_library.py` independently verifies all pin names/types, physical
corner anchors, perimeter positions, lead/thermal geometry, paste windows and
model path. Official KLC findings retained as local-library exceptions are:

- Ground pin 69 is on the lower right of the control unit.
- VREF is an internal output, despite the generic checker's input suggestion.
- Manufacturer/MPN/LCSC metadata is intentional.
- EP paste is in separate windows; bottom thermal copper is mask-covered.
- The STEP path is project-relative.

The LDO groups are captured in `cad/pmic-ldo.kicad_sch`. AN_RK809 V1.1 section
6.5 calls for one 1 uF capacitor at each input group and each output; C400–C411
implement that arrangement with 25 V X5R CL05A105KA5NQNC, C52923. Datasheet
Table 4-4 supplies the exact -5 startup values shown on the schematic. LDO1,
LDO4 and LDO9 remain disabled/reserved. LDO6 feeds the existing CPU enable RC.

The shared inputs use VCC3V3_SYS. LDO5 and LDO6 therefore have less than 0.4 V
headroom at their 3.3 V setting, which reduces the permitted load to **200 mA**
each (datasheet pages 22–23). Their voltage loss and actual PMU/SDIO loads must
be included in the completed rail budget. The 0.9 V and 1.8 V groups retain
ample headroom; their thermal dissipation still belongs in the PMIC budget.

`check_pmic_ldo.py` checks the fresh exported physical-pin/output mapping,
all twelve capacitor returns and the CPU enable source. The remaining buck,
RTC/control, audio-unused and switch units are still being captured. This
checkpoint does not establish full-system power integrity or authorize fabrication.

## DDR buck capture

BUCK3 is captured in `cad/pmic-ddr.kicad_sch`: pin 24 receives VCC3V3_SYS;
pin 25 drives L420; pin 26 senses the resulting VCC_DDR output; pin 27 receives
the hardware divider. The 0.47 uH SPM5030T-R47M (C501964, 257 units indexed)
uses the existing officially generated SPM5030 footprint. TDK's exact part
page specifies 5.94 mOhm maximum DCR, 11 A typical 20%-drop saturation current,
14 A typical 40 C-rise current, and the same 1.5 / 2.7 / 2.2 mm land dimensions.
See [TDK's exact part page](https://product.tdk.com/en/search/inductor/inductor/smd/info?part_no=SPM5030T-R47M).
Those typical current ratings are not guaranteed fault-current limits. RK809
BUCK3 remains a 1.5 A output. Stock and manufacturer facts are retained in
`pmic-buck-passives.json`; the smaller SPM4030 candidate was not selected.

R420 is 87.6 kohm RT0402BRD0787K6L (C852937); R421 is 100 kohm
RT0402BRD07100KL (C852472), both 0.1% / 25 ppm/C. The resulting nominal output
is 1.5008 V. With the PMIC's 0.784–0.816 V feedback limits, initial resistor
tolerance and opposing temperature coefficients over -40 to +85 C, the
calculated static range is 1.46719–1.53458 V. This leaves approximately
42.2 / 40.4 mV below/above for dynamic error and aging within the Hynix
1.425–1.575 V limits. Ripple, transients and aging are not yet qualified.
The reference design's 110k / 120k, 1% divider would exceed the upper DDR3
limit at a worst-case static corner; it is deliberately not copied.

C420/C421 provide 44 uF nominal local input bypass; C422–C424 provide 66 uF
nominal local output bypass, in addition to the DDR-side bank. All are the
already recorded Samsung 25 V X5R 22 uF part. The typical DC-bias data supports
the choice, but combined temperature/bias/aging remains a prototype check.
The VCC_DDR flag represents the actual SW3 -> L420 -> output path, as KiCad
does not propagate a power-output type through the passive inductor. It is
not an ERC exclusion. `check_pmic_ddr.py` verifies that path and the independent
divider nodes from a fresh exported netlist.

## Remaining power outputs and unused audio

`pmic-core.kicad_sch` captures BUCK1/2/4 with SPM5030T-R47M inductors,
two 22 uF local inputs and three 22 uF plus 100 nF local outputs each.
The 100 ohm resistors between output banks and feedback retain the topology
shown on the tablet reference page 22. NT430–NT432 are native KiCad copper-only
ties intended for U1 supply pads. They keep the dedicated feedback traces
separate in CAD until the physical load-side joining point. They must not
be placed at the PMIC, and are excluded from the assembly BOM. Actual placement,
transient/stability checks and PMIC thermal dissipation remain unfinished.

`pmic-aux.kicad_sch` captures the 1.8 V BUCK5 with the same inductor and
two input / three output 22 uF capacitors. FB5 senses its output bank directly.
SWOUT1 and SWOUT2 carry the 3.3 V inputs, not the BUCK5 output. They provide
VCC3V3_S0 and VCC3V3_SD respectively, with local 1 uF bypass; SD I/O remains
on the independently programmable LDO5 VCC_SDIO rail. Their final loads must
respect the switch current ratings, resistance/voltage drop and sequencing.

`pmic-control.kicad_sch` currently captures the unused codec. The six specified
pins are grounded and eleven specified pins are explicitly left open. C480/C481
are 1 uF on the internal 1.8 V outputs, with no external source connected.
Pin 33 receives 3.3 V with C482 10 uF bypass; its permitted input range is
2.7–5.5 V (datasheet page 25). System-control unit 10 is still absent.

The RTC candidates are recorded in `pmic-control-passives.json`. Epson's
FC-135R manufacturer drawing, `reference/fc-135r-en.pdf` page 4, was obtained
and visually reviewed: 3.2 x 1.5 x 0.9 mm, two 1.0 x 1.8 mm lands at 2.5 mm
center spacing and no circuit patterns under the shaded center. The candidate
is the 12.5 pF / 20 ppm variant; 22 pF capacitors require approximately 1.5 pF
stray loading for nominal tuning. Footprint verification, oscillator margin,
drive level and actual control capture remain next work. Auto-start VDC must
be delayed relative to the shared 3.3 V supply; do not assume the reference's
independent battery/VBUS timing applies to this board.

## Control and RTC capture

All 69 RK809 physical pins are now present in the exported netlist. SCL/SDA
use 22 ohm series resistors and 2.2 kohm pull-ups to VCC1V8_PMU. The future
processor PMUIO2 domain must therefore be powered/configured for 1.8 V.
RK860's SDA/SCL input-high threshold is 1.26 V (RK860 V1.7), compatible with
this bus. INT and RESET have separate 10 kohm pull-ups to VCC3V3_PMU; the
processor connections must use the corresponding 3.3 V PMU domain. RESET
retains 100 nF. PWRON retains 100 nF and its internal pull-up, ready for the
physical button/supervisor connection. SLEEP shares the existing CPU VSEL
net and its 100 kohm reset pull-down. Unused CLK32K/EXT_EN are explicitly open;
BATDIV/SNSP/SNSN and both ground pins are grounded. VREF is bypassed with 1 uF.

Y490 is FC-135R 32.7680KA-A3, C6554955, with two 22 pF C0G capacitors.
Its native 3215 land pattern matches the manufacturer's 1.0 x 1.8 mm pads at
2.5 mm center spacing. The local footprint adds the central 1.5 x 1.8 mm
keepout on every copper layer. The vendored STEP is 3.2 x 1.5 x 0.93 mm, a
clearance envelope 0.03 mm taller than the manufacturer's maximum, not a
manufacturer model. KLC exceptions are the retained rectangular manufacturer
lands and the project-relative STEP path. `rtc-footprint-source.json` records
the source hashes; the footprint plot and schematic were visually reviewed.

R496/R497/C487 form a 100k / 56k / 1 uF VDC network: 1.1846 V and 35.9 ms
nominal time constant. Its nominal 0.55 V crossing follows an ideal input step
by about 22.4 ms. The RK809 then qualifies VDC for 100 ms before starting its
sequence (datasheet section 4.1.2). The upstream 3.3 V rise must be <=10 ms,
subject to a completed tolerance/actual-capacitance timing budget.

**Open integration requirement:** RC delay alone does not prove recovery from
brief brownouts while VDC retains charge. Select/integrate upstream power-good
or reset behavior that forces VDC below its trigger threshold while the PMIC
supplies are invalid, or implement an equivalent verified PWRON restart path.
Do not waive this as a prototype-only issue. Cold/hot oscillator margin, drive
level, tuning, reset timing and the final startup circuit still require physical
qualification after that circuit is complete.
