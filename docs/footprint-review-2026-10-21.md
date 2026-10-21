# Six-footprint drawing review — 2026-10-21

Four engineering land-pattern review holds are closed against the archived
manufacturer drawings. U801 and U901 retain explicit PCB land/mask/paste process
holds. None of this releases the board for manufacture. Placement, routing,
fabricator rules, assembly approval, connector/enclosure clearances and physical
qualification remain open.

The machine-readable [review](../hardware/reference/footprint-reviews-2026-10-21.json)
records source revisions/hashes and the disposition of every part. The independent
[dimensional checker](../hardware/tools/check_footprint_reviews.py) compares native
footprints against drawing-derived coordinates rather than generated CSV output.
The full appliance checker now runs that check and the modem documentation gate.

| Ref | Drawing review and corrections | Disposition |
|---|---|---|
| U701 TPS56837RPAR | TI TPS5683x Rev B, drawing 4224047/A, PDF pp31–33. Centered the imported geometry by +0.01 mm in X; added R0.05 corners, explicit 0.07 mm mask clearance and separate paste-only apertures for SW pin 6 and PGND pin 9. Ten electrical identities, including four overlapping VIN pad sections numbered 8, retained. | Drawing geometry hold closed; stencil example assumes 0.1 mm thickness. Assembly process still needs approval. |
| U801 RK3566 | Rev1.2 Figs2-5/6. All 565 identities and both grids checked: 343 inner balls at 0.65 mm, 222 outer balls at 0.4 mm. Removed hundredth-mm source rounding and its inner-grid offset; pad centers now follow the exact centered grids. Official KiCad generator used. | **Hold retained:** 0.22 mm copper/mask and full-area paste are provisional. The package's 0.22–0.32 mm ball diameter is not a PCB land recommendation. Obtain a fabrication/assembly-approved land, mask and stencil design before escape routing. |
| U901 MT53E256M32D2DS-046 WT:B | Micron ZW Rev I, Figs5/9, PDF pp22/28. All 200 identities and rotated 0.65 × 0.8 mm grid checked; rounded centers replaced with exact values, e.g. A1 = (−6.825, +4.4). Official generator used. | **Hold retained:** existing 0.45 mm copper / 0.40 mm mask and paste openings are an engineering choice. Fig9's “post-reflow on Ø0.4 SMD ball pads” qualifies package measurement conditions; it does not independently approve this PCB land/stencil. |
| T1701 HX4110NLT | Pulse Rev A, pp1–3. 24 lands, 1.27 mm pitch, 0.75 × 1.65 mm pads, rows at ±4.51 mm, numbering 1…12 below / 24…13 above. T suffix is tape/reel, per p1. Existing geometry retained. Inch dimensions control; the bracketed metric dimensions are rounded. | Drawing geometry hold closed. No verified 3D model; PHY/magnetics performance and board isolation/clearance still require system review. The archived sheet alone is not proof of 2.5GbE operation. |
| J1701 RJE491881401 | Amphenol P-RJE49-188-1X01 Rev A. Checked top-view pin order 8/6/4/2 then 7/5/3/1, 0.90 mm signal drills and shell slots 1.00 × 2.60 mm at x=±7.95, y=5.05. The 4.38/3.27/5.05 mm dimensions resolve the datums. Existing geometry retained. | Drawing geometry hold closed. No verified 3D model; board edge, panel cutout, finished-hole tolerances and wave-solder process remain board/assembly obligations. |
| J2001 MDT420B01411 | Amphenol CMDT420X0X411 Rev A pp1–2. Checked all 67 contacts, omitted B-key positions 12–19 and 76, 0.5 mm same-row pitch, odd/even lands at y=−5.25/+2.275, unequal 1.50/1.55 mm lengths, retention lands and 1.1/1.6 mm locating holes. Existing geometry retained. | Drawing geometry hold closed. The exact archived STEP remains **detached**: its native axis/seating/row datums have not been reconciled together. Modem support, retention at the far end, insertion sweep and temperature/current derating remain open. |

## TPS56837 corrections to the earlier review

The earlier RPA table incorrectly treated the three right VIN fingers as 0.60 mm
long at x=1.40. TI explicitly specifies **0.56 mm at x=1.42**. The seven 0.60 mm
lands are the four left lands, two lower small lands and upper MODE land. The
import already had the correct finger lengths; its common −0.01 mm X displacement
is now removed. The silkscreen reference was moved outside the copper and the fabrication
reference reduced to fit the body. No electrical symbol or circuit connection
was changed.

The new paste-only apertures follow p33: pin 6 has two 0.25 × 0.75 mm openings
centered at y=0.375/1.325; pin 9 has two 0.40 × 0.95 mm openings at
y=−1.225/−0.075. Copper remains continuous. Paste apertures are unnumbered and
on F.Paste only. This implements the manufacturer's example, not a production
stencil qualification or a claim that every assembly process should use it.

## Models and source freshness

The official generator at commit `4115da4a5f1165c8ddf33d1e29d8f19234b6971d`
regenerated both BGA footprints and models using the co-located YAML/CSVs.
Their XY body dimensions remain nominal. Height now uses the package maximum:
RK3566 0.889 mm and Micron ZW 1.05 mm, instead of 0.794/0.95 mm nominal.
The generator's small marking geometry is included in the STEP bounds. These
are still envelope models, not vendor-exact models or full tolerance envelopes.

TI and Pulse downloads on October 21 are byte-identical to the archived PDFs.
Amphenol CDN downloads returned HTTP 403; those comparisons use the previously
archived Rev A drawings, with hashes retained. The Micron-authored document is
an archived distributor copy, not a newly obtained controlled revision. These
freshness limits remain part of the review and must survive a manufacturing handoff.

The existing missing-model holds remain. In particular, the M.2 STEP's native
bounding box is X ±10.95, Y 1.93…6.63, Z −3.95…4.45 mm. Reading this shape does
not resolve the PCB solder plane and both contact rows. No guessed transform
was attached to make the viewer appear complete.

## Verification

```sh
python3 hardware/tools/check_footprint_reviews.py --output /tmp/sierra-footprints.json
python3 hardware/tools/check_modem_documentation.py --output /tmp/sierra-modems.json
python3 hardware/check.py --output /tmp/sierra-capture
python3 hardware/tools/check_board_sync.py --output /tmp/sierra-board
python3 hardware/tools/check_step_models.py --output /tmp/sierra-models.json
```

The STEP check requires CadQuery; generation used the official tool's pinned
CadQuery 2.6.1 environment. Review evidence and native SVG exports are under
`hardware/review/2026-10-21/`. The committed staging board has no routing or
outline; DRC is reported without exclusions. The user's pre-existing outline
edit is preserved separately in the primary checkout and is not a manufactured
board outline release.
