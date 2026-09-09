> Historical evidence from superseded designs. See the [current full adapter](../../../../full-adapter/README.md). Circuit status and artifact paths below refer to the historical checkpoint, not the replacement.

# Active detailed assembly models — 2026-09-07

These four models are reconstructed CAD from manufacturer drawings, not manufacturer-supplied STEP files. All surfaces are opaque. `detailed_models.py` generates colored STEP and tessellated VRML; `board.py` assigns them explicitly. The source library's older bounding boxes remain archived in the model register but are not used for J201/J202/MECH1/H5.

| Board item | Model | Dimensional source and representation |
|---|---|---|
| J202, 3M N2520-6002-RB | IDC_3M_N2520_Detailed | 3M drawing78-5100-0770-7 RevU, local `../reference/3m-2500.pdf`, sheet2. 32.72×8.59×9.91 mm body,2.54 mm pin pitch,0.64 mm square pins,2.84 mm solder tails. Open shroud, central polarization notch and20 contacts. Minor molding features simplified. |
| J201, Amphenol MDT420B01411 | M2_MDT420_Detailed | Amphenol CMDT420X0X411 RevA, local `../reference/amphenol-mdt420.pdf`. 22 mm body width,4.2 mm height,2.89 mm slot center, B key,67 contacts, anchors and locating pegs. Contact springs use simplified solid segments; verify mating insertion on hardware. |
| H5, optional relocation to H10 | M2_support_assembly | Existing HN01 custom brass spacer: OD5, bore2.2, height2.49 mm. Includes a simplified M2 screw, washer and nut. No modeled threads; nut exterior is simplified circular. It is not a McMaster part or substitute BOM selection. Actual screw engagement and support-height tolerance require fit checking. |
| MECH1 | RM520N_GL_Detailed | Quectel RM520N-GL Hardware Design V1.0 figure35, local `../reference/rm520n.pdf` and `../reference/rm520-outline.png`. 30×52×0.8 mm PCB, mounting notch, B-key fingers, shield and drawing-based connector positions. Shield seams/contact details and label are representative; text is a visualization annotation with no invented regulatory/serial markings. Not a universal model of every RM5xx or Sierra variant. |

Exact CAD search: the [Amphenol product page](https://www.amphenol-cs.com/product/mdt420b01411.html) exposed the official `smdt420b0x411_a.zip` link, but its download returned an access challenge. The [DigiKey N2520 model listing](https://www.digikey.com/en/models/755179) and RM520N Ultra Librarian listing did not yield accessible exact CAD. No manufacturer CAD is claimed from these listings.

The [Quectel EM160R-GL product page](https://www.quectel.com/product/lte-a-em160r-gl/) specifies a30×42 mm module. H10 provides the corresponding support position,10 mm closer to the socket than H5. Fit one support only. This revision does not establish EM160R electrical compatibility: exact variant pinout, profile wiring, grounding and usable USB host interface require a separate audit. Do not infer universal RM5xx support from shared dimensions.

Five SMA models remain the exact-part KiCad Amphenol132289 STEP. U301 retains the reconstructed TI RPW0010A package. The large cooler and orange service-volume placeholder are absent; adhesive cooling and coax cables are unmodeled.

Validation: independent STEP readback verifies bounds and valid BReps for all four detailed models. Top/isometric assembly views are visually checked. This does not constitute tolerance-stack, thread-engagement, exact solid-interference or thermal certification.
