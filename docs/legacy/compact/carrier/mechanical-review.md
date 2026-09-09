> Historical evidence from superseded designs. See the [current full adapter](../../../../full-adapter/README.md). Circuit status and artifact paths below refer to the historical checkpoint, not the replacement.

# Placement mechanical definition — 2026-09-07

This is an unrouted, serviceable prototype layout, not a fabrication release. Coordinates below are millimetres from the left edge / SMA launch-line datum, viewed from the component side. PCB +Y runs downward. The board is 110 × 114 mm overall (Y−7…107), with a110 × 100 mm central body, finished thickness 1.50 ±0.05 mm. Four layers are proposed. The 1.55 mm upper tolerance stays below Amphenol132289's 1.57 mm maximum; obtain fabricator acceptance of the custom stack before routing widths are frozen.

## Fixed interfaces

| Feature | Definition |
|---|---|
| USB-C J101 | Centre X55; footprint Y94.10; housing mouth nominal Y99.72, 0.28 mm inside edge. Reserve a 16 mm wide plug approach beyond Y100. |
| RF1…4 + GPS | SMA edge-launch axes X15,35,55,75,95 at Y0, projecting toward negative Y. 20 mm pitch; 9.52 mm maximum body width leaves10.48 mm between adjacent body envelopes. Reserve16 mm diameter wrench/coupling access, and at least25 mm external axial cable access. |
| Carrier MHF4 | J601/603/605/607/609 at X15/35/55/75/95,Y12. Keep diameter7.6 mm tool access around each; remove external antennas before servicing if needed. |
| Module socket | J201 locating-hole midpoint55,76, rotated180°. Module extends toward negative Y; exact AmphenolMDT420B01411, not the rejected LOTES socket. |
| Module support | H5 centre55,25.75, NPTH2.2 mm. Derived from1.75 mm internal card-stop setback and52 mm card length, not from connector body edge. Verify full insertion against the first socket/module assembly before ordering boards. |
| Nano-SIM | J203 centre8.5,80, rotated270°; card approach from left edge. Reserve25 mm external access; replace only with modem powered off. |
| Profile assembly | J202 pin1 at78,95, body32.72×8.59×9.91 mm;20-contact fixed3M profile assembly, with22 mm total vertical service envelope. Route ribbon out beyond the bottom edge. Keep25 mm free for its folded/spliced tail. |
| Controls | POWER centre100,36; RUN100,50; RESET100,64; RF OFF100,75. Accessible from the open component side without a carrier-mounted cooler frame. |
| Board attachment | H1(4,−3), H2(106,−3), H3(4,103), H4(106,103), NPTH2.7 mm. Symmetric corner ears have4 mm outer radii and1 mm neck fillets. Use an insulating base/support; bottom screw-head clearance is required. |

The board intentionally trades minimum area for connector access, coax bend space. Mechanical anchors and controls are locked. Unlock only after updating this definition, the placement source and the drawings together.

## Module support and adhesive cooling

AmphenolCMDT420X0X411 RevA section view gives a2.89 mm slot centre. With nominal0.80 mm M.2 PCB thickness, its underside is2.49 mm above the carrier. The current Wurth2.5 mm SMT support candidate was rejected because its ±0.1 mm height plus solder-paste thickness does not establish this stack.

HN01 is a **custom machined brass support**, OD5.0 mm, bore2.2 mm, finished height2.49±0.02 mm, parallel faces within0.02 mm and deburred. An M2×8 pan-head machine screw, OD5 mm washer and M2 nut retain the module through H5. Fit without bending the module; verify screw engagement and any required support-height adjustment on first article. The support is not counted as an electrical ground connection.

The Sierra Rev8 envelope is30.45 mm maximum width including burr,52.30 mm maximum length,0.88 mm maximum PCB thickness and1.50 mm maximum upper component height. The RM520N-GL V1.0 drawing p72 specifies30×52 mm (general±0.15 mm),0.80±0.05 mm PCB and1.50 mm maximum upper component height. Both are single-sided in the audited drawings. Reserve module XY39.775…70.225 by25.60…77.90; no tall components occupy it. Actual shield flatness and thermal landing area must be inspected for the exact purchased modules.

Cooling is a small adhesive heatsink selected and attached during assembly. No exact part, position, thermal tape geometry or cooling envelope is modeled. The previous Fischer 50×50×25 mm sink, retention frame, four posts, associated screws/washers and H6–H9 mounting holes are removed. The previous sink/tape thermal calculation no longer applies. H5 and its M.2 support/screw remain necessary for module retention.

## Coax and routing access

Use four Taoglas CAB.01072 cellular harnesses and an optional fifth for a dedicated module GNSS port. Keep cables free of the adhesive heatsink and avoid loading their connectors. No cooler underside clearance is assumed.

Reserve at least15 mm bend radius as a conservative engineering layout target; no manufacturer cable-specific minimum radius was obtained. It is not a certified cable rating. First-article harness dressing must demonstrate that all four100 mm assemblies fit both module variants with that target and accessible disconnect tools. If actual plug orientation or required length fails, revise the cable assembly and mechanical drawing before fabrication. Do not force a cable to fit the nominal outline. RF cable loss and return loss remain bench gates over the applicable bands.

## Placement DRC basis

All161 schematic components are placed. Six board-only mechanical holes are intentional. No tracks, vias or copper fills exist. References reside on F.Fab for a legible assembly drawing; physical silkscreen retains user controls and interfaces.

Normal copper clearance is0.15 mm, power0.20 mm, board edge0.30 mm, finished hole-to-hole allowance0.14 mm. The last value accommodates the audited USB connector's close locating/shield holes and requires fabrication acceptance. LTC3310S internal manufacturer lands use a local0.15 mm clearance rule (minimum actual approximately0.176 mm). Its external routing retains normal power clearance.

Only the Amphenol132289 footprint's edge-clearance check is ignored: its drawing deliberately places the centre copper land exactly at the board edge. Other edge clearances remain checked. I-PEX's manufacturer-defined continuous solder-mask window is explicitly allowed to bridge its own centre/ground apertures; the copper remains separate and checked. No blanket unrouted/clearance waivers are used. The final report must retain counts of expected unconnected items separately.

Final connector review: XKB XKNANO-113 A0 specifies0.75mm locating holes; the carrier copy now follows that drawing, with a conservative top-copper exclusion under internal contacts. HRO TYPE-C-31-M-04 drawing2014-05-29 references a1.0mm PCB: validate its short-tail soldering/fixture process on the requested1.50mm carrier before assembly. No supplier acceptance is implied.

## Alternate module length and detailed models

H10 at(55,35.75), NPTH2.2 mm, supports3042 cards such as EM160R. Move the single removable support/screw from H5 to H10 for a42 mm card; never fit both supports beneath a52 mm card. The default rendered assembly is3052. EM160R electrical pin mapping, profile wiring, mounting-ground requirements and USB operation remain unqualified; the new hole is mechanical accommodation only.

See [model-sources.md](model-sources.md) for the reconstructed IDC, M.2, card and support geometry. Card and hardware are nominal renderings, not purchased-part fit certifications.
