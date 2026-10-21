# BGA process and missing-model review — 2026-10-21

Six new package-envelope models cover 16 components. Missing-model holds fall from
34 components / 24 footprint types to 18 components / 18 types. Both BGA land-pattern
holds remain: the sources establish package geometry, but do not approve the PCB
copper, mask and assembly process. No copper, pad centers, nets or placement changed.

The [model record](../hardware/reference/model-reviews-2026-10-21.json) pins the
KiCad Library Tools revision, definition/source hashes, STEP bounds, board
references, rotations and every remaining blocker. The generator definitions are
co-located in `hardware/Appliance.pretty/sierra-*-model*.yaml` and `sierra-models.csv`.
The [review image](../hardware/review/2026-10-21/model-envelope-review.png) shows
installed orientations from above and below.

## BGA assembly holds

The [process checker](../hardware/tools/check_bga_process.py) measures all pad
pairs, including the mixed RK3566 grids. Results are saved in the
[process report](../hardware/review/2026-10-21/bga-process.json).

| Quantity | RK3566 U801 | Micron ZW U901 |
|---|---:|---:|
| Lands | 565 | 200 |
| Minimum center distance | 0.400 mm | 0.650 mm |
| Copper / mask / paste diameter | 0.220 / 0.220 / 0.220 mm | 0.450 / 0.400 / 0.400 mm |
| Minimum copper gap / mask web | 0.180 / 0.180 mm | 0.200 / 0.250 mm |
| Radial mask clearance | 0 mm | −0.025 mm (SMD) |
| Circular-aperture area ratio at 0.100 mm foil | 0.55 | 1.00 |
| Aperture diameter / foil thickness at 0.100 mm | 2.2 | 4.0 |
| Maximum foil under the screening criteria below | 0.0733 mm | 0.1333 mm |

For a circular aperture, area ratio is `diameter / (4 × foil thickness)` and
aspect ratio is `diameter / foil thickness`. Area ratio ≥0.66 and aspect ratio ≥3
are explicitly **engineering screening assumptions**, not Rockchip/Micron release
criteria. The RK3566 current aperture fails both at 100 µm; a 70 µm stepped foil
would pass the arithmetic screen (0.786 and 3.14), but paste release, foil handling,
solder volume and reflow still need assembler approval. Do not apply the TI power
IC's 100 µm stencil example to the entire board without reviewing this conflict.

The RAM's 0.400 mm paste aperture inherits the footprint-level −0.025 mm margin;
the checker accounts for this rather than mistaking the 0.450 mm copper for paste.
Its screening result does not validate the existing 25 µm mask overlap per side.
RK3566 zero mask clearance also needs explicit fabricator registration approval.

Rockchip's archived hardware guide has reflow guidance but no verified recommended
land/mask/stencil design was found. Micron's ZW Fig9 describes package measurement
on 0.4 mm SMD pads; it does not alone release our PCB. The current Micron CSN33 URL
returned a request-rejected HTML page, so no document was archived or treated as
controlled evidence. Generic guidance and search excerpts cannot close either hold.

Before escape routing, obtain a manufacturer- or assembler-approved copper/mask
plan, fabricator mask registration and minimum-web capability, approved stencil /
paste / reflow parameters, and an escape/via plus inspection strategy. Those
approvals are absent; `land_pattern_release_holds` remains U801/U901.

## Attached models

All six are generated envelopes with simplified terminals and package construction,
not vendor-exact solids or complete tolerance envelopes. Their seating plane is
Z=0. Shape validity, overall bounds, attachment, scale and rotation are checked;
physical fit and assembly qualification remain open.

| Components | Sourced geometry and orientation |
|---|---|
| L501/L502/L504/L505/L901/L902/L1001/L1501/L1707 | XGL4020 and XFL4020 share 4.0±0.3 mm XY, 2.10 mm max height and terminal geometry. Shared model uses maximum 4.3 mm XY and 2.10 mm height, nominal terminal geometry; no start-lead marking is represented. Archived XGL4020 and newly archived XFL4020 drawings. |
| L601 | XGL4030: maximum 4.3 mm XY and 3.10 mm height, nominal terminal geometry. New Coilcraft PDF and separate manufacturer dimensional GIF archived. |
| U1801/U1802/U1803 | Toshiba TLP293 package 11-4C5S, archived PDF p14: nominal 4.55 × 2.60 mm body, 7.0 mm lead span, 1.27 mm pitch, 2.20 mm maximum height envelope. Model rotates 180°: pin 1 matches the existing footprint's +X/+Y corner. The legacy footprint's rounded 0.64/−0.63 mm pad coordinates are unchanged. |
| C1717 | Panasonic EEEFK1J470P: 8 mm can diameter, 10.2 mm maximum height, 8.3 mm base and 10.0 mm lead envelope, using the official generator's Panasonic F case definition. Model rotates 180° so the cathode stripe faces pad 2 (+X); pad 1 (−X) is positive. |
| C1727 | Nichicon PCV1E271MCL1GS: CV catalog p1/2, 10 × 12.7 mm size, L=12.6+0.1/−0.4 mm, base B/C=10.3 mm, overall A=11.0 mm, terminal gap E=4.6 mm and nominal 0.95 mm lead width. Model uses 12.7 mm maximum height and nominal XY; cathode faces pad 2 (+X), rotation 180°. |
| U1702 | TI LM51551 DSS0012B, drawing 4218908/A: nominal 2 × 3 mm body, 0.8 mm max height, 6 leads per side at 0.5 mm, 1 × 2.65 mm EP. Stock footprint name says 3x2; its actual copper orientation is 2 mm X by 3 mm Y. Model matches that geometry without rotation. |

Capacitor marking extends 0.01 mm above the specified maximum body height in the
generator; the bounds record includes it. Their plastic base and can details are
simplified. The Toshiba model uses maximum overall height with nominal XY; the
Coilcraft models use maximum XY/height, not every combined terminal tolerance.

Sources: [Panasonic exact part](https://na.industrial.panasonic.com/products/capacitors/aluminum-electrolytic-capacitors/series/88994/model/89545),
[Nichicon CV](https://www.nichicon.co.jp/english/products/pdf/e-cv.pdf),
[TI LM51551](https://www.ti.com/lit/ds/symlink/lm51551.pdf), and source URLs/hashes in
the machine record. Generation used official KiCad Library Tools commit
`4115da4a5f1165c8ddf33d1e29d8f19234b6971d`, CadQuery 2.6.1 / OCP 7.8.1.
Copy the co-located definitions into the matching official generator data folders:
`inductor/SMD`, `package/gullwing`, and `package/no_lead`; append the capacitor
entries to `capacitor/SMD/elec_round_polarized/cq_parameters.yaml` (legacy loader).
Generate the named entries with `python -m generators.generate -g GENERATOR -p
PART -m OUTPUT`; no new generator was written. Only STEP outputs were installed;
existing copper/footprint assignments remain intact.

## Remaining model holds

Every unresolved type has one component. The exact blocker is retained in policy
and checked against the review record. A visually similar package is insufficient
for connector, polarity, pin-1 or thermal-pad review.

| Reference | Blocker |
|---|---|
| D1718 | Exact Diodes SP5 body/terminal underside and pin-1 orientation need a sourced model; a generic three-pin diode would conceal the split terminals. |
| J2002 | Molex 1042240820 hinged/cover geometry and insertion clearance require exact vendor CAD and seating datum; no verified asset obtained. |
| T1701 | Pulse HX4110NL drawing is archived; transformer body, stand-off and lead bend need a matching model; installed stock path is absent. |
| J2001 | Exact Amphenol STEP archived; candidate X rotations align either seating height or contact row, not both. Resolve contact/locating-hole datum against drawing before attachment. |
| J1701 | Amphenol RJE49 drawing archived; no exact CAD obtained. RJ45 substitutes have different panel, shield-tab and LED geometry. |
| U1301 | Realtek drawing archived; installed 6x6 QFN has a different 4.45mm exposed pad. Exact terminal, height and pin-1 datum remain to be modeled. |
| U701 | TI RPA0010A drawing archived. Existing generic no-lead generator does not describe the split VIN fingers and long internal switch/ground terminals. CSE lists a model but did not provide a STEP asset. |
| U2002 | TI RSE0010A drawing archived; two end terminals differ from the eight side terminals. Uniform QFN substitution would misrepresent contacts. |
| U1902 | TI TPS25947 drawing archived; asymmetric long/corner terminals require a matching underside model, not a uniform 10-pin QFN. |
| U1901 | TI RHL0014A drawing archived; asymmetric corner lead placement and thermal-pad profile require an exact terminal definition. |
| U1001 | Full TCS4525 v1.0 p21 gives 1.60-1.66 by 2.00-2.06mm, 0.60mm max height and 0.15-0.23mm ball stand-off, but no ball diameter. Archived v1.1 is only the first page. Do not infer ball diameter from PCB copper. |
| J1201 | No exact matching Amphenol shell/retention-tab CAD obtained; installed model path absent. Mating-face and board-edge datum must be checked. |
| L401 | LPS4018 drawing archived; ferrite drum, base/chamfer and wraparound terminals differ from the modeled XGL molded-body geometry. |
| Y1101 | SiT8008B p11 package drawing archived; existing crystal model generator has a different ceramic/metal stack. Exact PQFN underside and pin-1 treatment remain. |
| U1101 | Stock generator has JEDEC AN 153-ball XY but lacks body stand-off for 3D. Current archived ISSI sheet covers the 100-ball package; exact JCLI 153-ball package dimensions must be archived before generation. |
| J1712 | Molex 87898-0204 exact shroud, latch and mating envelope not verified; a generic 2-pin header would hide connector clearance. |
| Q1705 | FDMS86252 exact Power56/PQFN terminal arrangement and seating geometry need vendor package CAD; generic eight-pin QFN is not sufficient. |
| L1702 | Wurth publishes exact 744272251 STEP (rev1), but automated retrieval returned HTTP 403. Archived 744272222 is wrong MPN and has invalid solids; remains detached. |

## Verification

- Full native ERC: zero violations; 663 components / 823 nets and all assigned-pad identities pass.
- Native schematic/PCB parity: zero issues; 626 stock footprints / 572 HandSolder variants retained.
- All 54 unique attached STEP assets parse as valid shapes. The six new assets also pass solid validity, sourced dimensions, seating-plane and placement/hash checks.
- All 16 PCB edits add model blocks only. No footprint copper, transforms, native links or nets changed.
- Committed staging board: 771 physical DRC findings and 499 unconnected items; no routing or outline. These counts are unchanged. This is not a manufacturing release.

Run `python3 hardware/check.py --output /tmp/sierra-capture`,
`python3 hardware/tools/check_board_sync.py --output /tmp/sierra-board`,
`python3 hardware/tools/check_bga_process.py --output /tmp/sierra-bga.json`,
`python3 hardware/tools/check_model_reviews.py --geometry` and
`python3 hardware/tools/check_step_models.py --output /tmp/sierra-step.json`.
The last two geometry commands require CadQuery. The full appliance checker runs
the process and source/attachment checks without that dependency.

The user's pre-existing outline/UUID save remains uncommitted in the primary
checkout. Model blocks are integrated into that board separately; its content is
backed up before the branch is fast-forwarded. No layout release is implied.
