# RPA0010A footprint geometry for review

Source: TI TPS5683x Rev B, package drawing 4224047/A, PDF pages 31–33.
View is from top; origin at package center, +x right, +y down. Body
3.0 x 3.0 mm nominal (2.9–3.1), height 0.8–1.0 mm. Pin 1 is upper left.

| Pad | Center x mm | Center y mm | Copper width x mm | Copper height y mm |
|---|---:|---:|---:|---:|
| 1 EN | -1.40 | -0.75 | 0.60 | 0.25 |
| 2 FB | -1.40 | -0.25 | 0.60 | 0.25 |
| 3 AGND | -1.40 | 0.25 | 0.60 | 0.25 |
| 4 PG | -1.40 | 0.75 | 0.60 | 0.25 |
| 5 SS | -0.93 | 1.40 | 0.25 | 0.60 |
| 6 SW | 0.37 | 0.85 | 0.25 | 1.70 |
| 7 BOOT | 0.87 | 1.40 | 0.25 | 0.60 |
| 9 PGND | -0.21 | -0.65 | 0.40 | 2.10 |
| 10 MODE | -0.93 | -1.40 | 0.25 | 0.60 |

Pad 8 VIN is continuous asymmetric copper: a 0.40 x 2.10 mm vertical
bar centered x=0.95, y=-0.65, joined to three 0.56 x 0.25 mm right-side
fingers centered x=1.42, y=-0.75/-0.25/+0.25. These are one electrical
pin, not an added exposed pad. The manufacturer's curved corners use
R0.05 typical. Copper union must preserve overlap and mask continuity.

Use nominal manufacturer land pattern rather than generic QFN arithmetic.
Courtyard must surround all copper with appropriate fabrication margin;
3D package orientation must match pin 1. TI page 33 stencil openings need
separate extraction; no full-area paste assumption for the VIN union.

The assigned engineering footprint is now
`Appliance:Texas_RPA0010A_TPS56837`, derived from the Component Search Engine
TPS56A37RPAR footprint for the same TI RPA0010A package. The untouched import is
archived as `hardware/reference/tps56a37-rpa0010a-cse.kicad_mod`. Its three right
VIN fingers were incorrectly numbered 11/12/13; all now use electrical pin 8.
The project retains its independently audited ten-pin TPS56837 symbol.

The [October 21 drawing review](footprint-review-2026-10-21.md) corrects the
previous interpretation: the right-side fingers were already the specified
0.56 mm long. The common −0.01 mm X displacement is now removed. Copper uses
R0.05 corners and explicit 0.07 mm mask clearance; pins 6 and 9 have split
paste-only openings per TI's 0.1 mm stencil example. The independent dimensional
checker verifies these against pp32–33. The drawing geometry hold is closed;
stencil/assembly process and board-level verification remain open. No unverified
3D model is attached.
