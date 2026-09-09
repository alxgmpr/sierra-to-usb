# CPU power qualification — integration in progress

RK860-0, LCSC C19188628, is the selected regulator candidate. The current library
checkpoint verifies its 20 physical balls, native KiCad pin-stack expansion,
0.4 mm pitch, and manufacturer drawing. This is not a completed power circuit
or assembly approval.

## Source and variant

[Rockchip RK860 Rev 1.7](https://rockchip.fr/RK860%20datasheet%20V1.7.pdf),
pages 8–9, identifies A4 as the output **sense input**. Its table's I/O column
says Output; the functional description and both application circuits establish
the sense function. The schematic therefore uses an input pin. All four LX
balls must connect to the inductor input. All four VIN and seven ground balls
must be physically connected on the PCB.

The exact **-0** variant uses I2C address 0x40 and device ID 8. Both voltage
registers start enabled at 1.0 V, with a 12.5 mV step from 0.7125 V. Mainline
Linux's `fan53555` driver supports `rockchip,rk8600`; the TCS4525 register map and
address must not be substituted. The B2 processor's operating voltage limit is
1.15 V for CPU, so firmware must clamp its operating points accordingly.

## Capacitance and remote feedback

The RK3568 Hardware Design Guide §2.2.2.4 requires a regulator rated at least
4 A and total nominal CPU capacitance above 135 uF. The pinned Rockchip tablet
reference schematic, pages 11 and 24, explicitly lists TCS4525_WT / RK860-0:

- Regulator local output: three populated 22 uF capacitors plus a fourth DNP.
- Processor: 100 nF, 4.7 uF and three 22 uF capacitors; nominal total for the
  populated output network is 136.8 uF.
- A 100 ohm resistor and 1 uF capacitor connect **between the regulator output
  and the remote feedback net**, which returns from processor ball M15.
  That 1 uF capacitor is not a feedback-to-ground capacitor.
- Input: two 22 uF capacitors. EN has a 51 kohm pull-up to VCC3V3_PMU;
  an optional 100 nF capacitor permits an enable delay.
- VSEL follows PMIC_SLEEP_H, requiring compatible run/suspend voltage register
  programming.

RK860's 44–88 uF recommended COUT is thus a local output bank in this documented
processor application; the processor adds remote decoupling. Exact capacitor
DC-bias curves, aging/tolerance bounds and the finished transient response still
need qualification. Do not interpret the reference nominal total as a measured
effective capacitance guarantee.

The captured 22 uF part is now Samsung CL21A226MAYNNNE (C602037), a current
production replacement for NRND CL21A226MAQNNNE. Samsung's embedded 25 C curve
gives approximately 21.0 uF at 1.15 V and 9.2 uF at 5.25 V. The curve and
interpolations are retained in `core-22uf-qualification.json`. The planned
5 V input bank therefore uses four capacitors; two would fall below the
regulator's 20 uF input recommendation even before tolerance. Combined
temperature/bias and aging qualification remains open.

## Current and temperature

Rockchip's pinned RK356X Power Consumption Test Report gives CPU 3 A, GPU 1.2 A,
NPU 1 A and LOGIC 1.2 A as limit-current design references. Its CPU voltage of
1.2 V is not applicable to B2's 1.15 V maximum. The report's SoC thermal design
reference is 6 W. These are design references, not absolute guarantees for
every workload or peripheral configuration.

RK860 advertises 6 A, but page 20 also specifies 0.5 W continuous package
dissipation, theta-JA 64.44 C/W and theta-JC 17.76 C/W on a two-layer PCB.
The loss budget must respect these limits and the 125 C operating junction
limit. The PMOS peak-current limit is listed as 8.5 A **minimum**, with no
maximum; it is not an upper bound for inductor fault-current qualification.

## Library generation and review

`extract_cpu_regulator_pins.py` pins the PDF hash and records the reviewed
top-view ball map. `tools/build_core_symbols.py` generates the native stacks.
`tools/check_cpu_regulator.py` checks every ball and exports a temporary
schematic through KiCad to prove that all stack members become distinct
netlist pins. DDR remains independently validated.

`lib/cpu-regulator-footprint.yaml` is input to official KiCad Library Tools
revision 475bd27b9a521418c3732ff2ee5efea98525d2c7, generator
`package/grid_array`. The body envelope covers both H and D package codes.
The drawing explicitly recommends 0.15 mm lands. The small-land assembly
process remains to be qualified; no substitution of an EasyEDA footprint is
implied. After generation, the model path is made project-relative and the
fabrication reference font is increased from 0.48 to 0.5 mm.

KLC exceptions are explicit: the ground pins remain on the lower right so
the six-number ground stack is readable; A4's input type follows its function;
Manufacturer/MPN/LCSC fields are intentional. The footprint's 0.05 mm mask
expansion and project-relative STEP path are intentional local-library choices.
No electrical-rule exclusion was added.
