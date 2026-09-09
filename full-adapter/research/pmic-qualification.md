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

The PMIC circuit, sequencing connections and regulator passives are the next
capture work. This library checkpoint does not establish full-system power
integrity or authorize fabrication.
