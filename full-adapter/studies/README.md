# Processor escape work

`processor-escape.kicad_pcb` is a geometric routing coupon, **not the integrated
board and not for fabrication**. It includes the exact 636 populated balls and
408 signal/power/ground via obstacles. All 114 selected signals reach beyond the
package body: 82 on F.Cu, 28 on In2.Cu and 4 on In4.Cu. The three copper plots
were visually inspected. The first KiCad 10.99 DRC found no clearance, short,
track-width, hole-clearance or annular-ring violations. Its complete report is
retained, including 251 unconnected items, 199 dangling vias, 114 dangling trace
ends and one library-table warning. These are unfinished coupon connections,
not release waivers. No system DRC/ERC result is implied.

The study uses 0.09 mm local escape traces, 0.15 mm through drills, 0.30 mm lands,
0.10 mm copper clearance and 0.20 mm drill-edge clearance. Filled, plated-over
vias are required if these on-pad vias are used. JLC's
[published capabilities](https://jlcpcb.com/capabilities/pcb-capabilities/) list this drill process;
it costs more than the preferred 0.20 mm process. A 0.20 mm uniform via grid was
already shown inadequate by the earlier arithmetic. This coupon demonstrates
a concrete alternative without reducing the 0.20 mm hole clearance.

Still to do: choose and model the dielectric stack, shorten neckdowns, route
differential pairs together and match lengths including package/vias, add
reference planes and check their continuity, complete power distribution and
decoupling, and connect DDR and the surrounding system. The current 0.09 mm
width over the entire coupon trace is **not an impedance prescription**.

Reproduce the ball cross-check and initial coupon with:

```sh
full-adapter/.venv/bin/python full-adapter/research/extract_processor_pins.py
full-adapter/.venv/bin/python full-adapter/research/processor_escape.py
/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli pcb drc \
  full-adapter/studies/processor-escape.kicad_pcb --format json \
  -o full-adapter/studies/processor-escape-drc.json
```

Pin data come from the local source hashes recorded in `processor-pins.json`.
623 names agree automatically between the workbook and B2 V2.3. Ten signal
names add LVDS aliases and two rail names add LVDS usage; these were reviewed
visually on B2 pages 24–25 and 28–29. H24 is truncated in Table 2-1 at the page
break; its full name matches Table 2-3 on page 34. None changes a DDR3 ball.
The ball grid was checked in PCB top view against the mirrored package bottom
view. All generated pad numbers and coordinates were checked against that grid.

The footprint was generated using official KiCad Library Tools revision
`475bd27b9a521418c3732ff2ee5efea98525d2c7`, package/grid_array generator, from
`../lib/processor-footprint.yaml`. Its 0.30 mm NSMD land and 0.05 mm mask
expansion are engineering choices; the source drawing specifies package balls,
not a PCB land recommendation. The nominal 3D model uses the same generator and
636-ball pattern: 19 × 19 mm, 1.04 mm nominal overall height, 0.35 mm balls and
0.25 mm seating gap. Mechanical clearance must use the 1.111 mm maximum height.
