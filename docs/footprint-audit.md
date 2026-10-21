# Footprint, model and native synchronization audit

Current follow-up: [2026-10-21 six-footprint review](footprint-review-2026-10-21.md).
Four drawing geometry holds are closed; U801/U901 retain land/mask/paste process
holds. TPS56837 geometry, BGA centers and model heights are corrected.
The October 7 results below are historical, including their six-hold count.

## Historical audit — 2026-10-07

2026-10-07, KiCad 10.99.0. The pre-audit project was sweep-committed before edits.
The canonical project is `hardware/appliance.kicad_pro`, with 30 sheets,
663 components, 823 nets and 663 PCB footprints. The PCB is a footprint staging
board with no tracks, vias, zones or board outline; placement and routing remain
open.

## Verified result

- All-severity schematic ERC: **0 violations, no exclusions**.
- Native **Update PCB from Schematic**: **0 errors, 0 warnings, no changes**.
- Native **Update Schematic from PCB**: **0 errors, 0 warnings, no changes**.
- Normal UUID matching was used after repairing the multi-unit RK3566 and RAM
  links. Reference relinking is off in both final checks. Forward replacement,
  orphan deletion and field replacement/removal are enabled; reverse references,
  footprints, values, net names, attributes and other fields are enabled.
- Native CLI schematic parity: **0 issues**. All component fields, DNP flags,
  pad identities, native symbol UUID links and multi-unit metadata are checked.
- **626 default-library footprints**, including **572 stock HandSolder variants**.
  Package sizes and exact MPNs are retained. Fine-pitch ICs and BGAs still require
  appropriate assembly equipment; an enlarged passive pad does not change that.
- **626 components have resolved models**. All **48 distinct attached STEP assets**
  parse with valid shapes. Three bare test pads need no model. **34 components / 24
  footprint types** have explicit model holds, listed below.

[Native forward report](../hardware/review/2026-10-07/footprint-audit/schematic-to-pcb.txt),
[round-trip options and source hashes](../hardware/review/2026-10-07/footprint-audit/native-roundtrip.json),
[board audit](../hardware/review/2026-10-07/footprint-audit/board-sync-report.json),
[STEP shape/bounds report](../hardware/review/2026-10-07/footprint-audit/step-model-report.json)
and [footprint plots](../hardware/review/2026-10-07/footprint-audit/svg/)
retain the evidence. The empty native reverse report means no proposed changes.

## Selection and geometry corrections

Stock KiCad packages replace generic/imported passives, applicable SOT-23 parts,
SMA/SMB diodes, the Ethernet crystal, USON protection arrays, DHVQFN USB muxes,
TPS2373/TPS2372 power packages and the TPS22965 WSON. The eMMC uses the stock
11.5 × 13 mm LFBGA-153 footprint with the audited ball identifiers. The existing
TCS4525 WLCSP and RTL8125 package remain local because their exact ball names or
exposed-pad dimensions do not match the closest stock alternative.

| Reference / part | Assigned engineering land pattern and review boundary |
|---|---|
| U801 RK3566 | Official grid-array generator, all 565 original audited ball centers, 15.5 × 14.4 mm body, 0.22 mm copper pads. Mixed pitch retained. Generated nominal envelope model; copper/mask/stencil and package tolerances need assembly review. |
| U901 Micron MT53E256M32D2DS-046 WT:B | Official grid-array generator, all 200 audited balls, 14.5 × 10 mm ZW body. 0.45 mm copper, 0.40 mm mask opening, 0.40 mm paste opening per engineering SMD interpretation of the archived Micron guidance. The final stencil process remains a release hold. |
| T1701 Pulse HX4110NLT | 24 pads, 1.27 mm pitch, 0.75 × 1.65 mm lands at y = ±4.51 mm. Top row is 24…13, bottom row 1…12 from left to right. 16.51 × 9.14 mm nominal outline follows the Pulse drawing; no verified model attached. |
| J1701 Amphenol RJE491881401 | Manufacturer top-view pin order: 8/6/4/2 at y = 0 and 7/5/3/1 at y = 1.78 mm, left to right. 0.90 mm signal drills; shell slots 1.0 × 2.6 mm at x = ±7.95, y = 5.05 mm. Pin-1 silk/fab markers follow the reflected pad map. Final housing/board-edge clearance needs mechanical review. |
| J2001 Amphenol MDT420B01411 | B-key: 67 electrical contacts, pins 12–19 and 76 absent. Odd lands 0.30 × 1.50 mm at y = −5.25; even lands 0.30 × 1.55 mm at y = +2.275. Retention lands and asymmetric 1.1/1.6 mm NPTHs follow drawing Rev A. Exact STEP is archived, but model seating/row datums need reconciliation before attachment. |
| U701 TPS56837 RPA0010A | Same-package TPS56A37RPAR import corrected to ten electrical identities: VIN fingers 11/12/13 become pin 8. The independent TPS56837 symbol is retained. Imported lands differ from the TI nominal drawing by up to 0.02 mm; right fingers are 0.56 mm (the original 0.60 mm comparison was incorrect; see the October 21 review). Stencil/assembly review remains open; no model attached. |

The six rows remain explicit land-pattern release holds. Assigning them closes
native synchronization; it does not silently qualify their assembly processes.

RTL8125's four imported thermal through-hole pads now share exposed-pad number
49/GND and have no paste on their holes. The PowerDI-5 uses a stock-derived land
pattern with its three native electrical identities: anodes 1/2, cathode 3.
Imported malformed legacy courtyard arcs were migrated by KiCad. The final DRC
has zero malformed courtyards, copper shorts, mask bridges, unresolved text
variables or library-footprint mismatches.

## Models and provenance

Thirteen embedded TI reference STEP files were recovered into `PoE.3dshapes`.
Their hashes and original CAD source are retained in
`hardware/reference/imported-model-sources.json`. The WE-SL5 asset named
`744272222.stp` contains invalid solids and differs from the selected 744272251
MPN. It is archived but detached. Other retained TI models and the local recovery
header envelopes are reference/equivalent geometry, not vendor-exact clearance
certification.

The renamed stock TPS22965 model was resolved to the same-size WSON-8 envelope.
The missing stock DHVQFN model was generated from the exact upstream KiCad
definition and stored locally. RK3566 and Micron models use the co-located BGA
parameters. Attached model paths resolve without `kicad-embed://` or temporary
paths. A valid STEP shape establishes readable geometry, not exact MPN identity,
connector mating clearance or board-level interference freedom.

Manufacturer drawing URLs, revisions and hashes are in
`hardware/reference/footprint-audit-sources.json`; the original source registry
remains in `hardware/reference/sources.json`. The newer archived ISSI TF-family
PDF covers a different 100-ball option; the selected 153-ball IS21TF16G-JCLI was
retained against the previously audited native map and older manufacturer
package information. No different memory part was silently substituted.

| References | Footprint type | Model hold |
|---|---|---|
| D1718 | `Appliance:Diodes_PowerDI-5_3Pin_Derived` | Referenced model is absent from the installed stock libraries; no unverified substitute attached |
| J2002 | `Appliance:SIM-SMD_1042240820` | No verified mechanical model attached |
| U1801, U1802, U1803 | `Appliance:SOP-4_L4.4-W2.8-P1.27-LS7.0-BR` | No verified mechanical model attached |
| T1701 | `Appliance:Sierra_HX4110NL_2x12_P1.27mm` | Referenced model is absent from the installed stock libraries; no unverified substitute attached |
| J2001 | `Appliance:Sierra_MDT420B01411_2x38-1MP_P0.5mm` | Exact manufacturer STEP archived; seating plane and pin-row datum conflict require reconciliation before attachment |
| J1701 | `Appliance:Sierra_RJE491881401_1x08-1MP_P1.02mm` | Referenced model is absent from the installed stock libraries; no unverified substitute attached |
| U1301 | `Appliance:TQFN-48_L6.0-W6.0-P0.40-BL-EP4.5` | No verified mechanical model attached |
| U701 | `Appliance:Texas_RPA0010A_TPS56837` | No verified mechanical model attached |
| U2002 | `Appliance:UQFN-10_L2.0-W1.5-P0.50-BL` | No verified mechanical model attached |
| U1902 | `Appliance:VQFN-10_L2.0-W2.0-P0.45-TL` | No verified mechanical model attached |
| U1901 | `Appliance:VQFN-14_L3.5-W3.5-P0.50-TL-EP_TPS54622RHLT` | No verified mechanical model attached |
| U1001 | `Appliance:WLCSP-20_L2.0-W1.6-R5-C4-P0.40-TL` | No verified mechanical model attached |
| J1201 | `Connector_USB:USB_Micro-B_Amphenol_10103594-0001LF_Horizontal` | Referenced model is absent from the installed stock libraries; no unverified substitute attached |
| L401 | `Inductor_SMD:L_Coilcraft_LPS4018` | Referenced model is absent from the installed stock libraries; no unverified substitute attached |
| L501, L502, L504, L505, L901, L902, L1001, L1501, L1707 | `Inductor_SMD:L_Coilcraft_XxL4020` | Referenced model is absent from the installed stock libraries; no unverified substitute attached |
| L601 | `Inductor_SMD:L_Coilcraft_XxL4030` | Referenced model is absent from the installed stock libraries; no unverified substitute attached |
| Y1101 | `Oscillator:Oscillator_SMD_SiT_PQFN-4Pin_3.2x2.5mm` | Referenced model is absent from the installed stock libraries; no unverified substitute attached |
| U1101 | `Package_BGA:LFBGA-153_11.5x13mm_Layout14x14_P0.5mm` | Referenced model is absent from the installed stock libraries; no unverified substitute attached |
| U1702 | `Package_SON:WSON-12-1EP_3x2mm_P0.5mm_EP1x2.65` | Referenced model is absent from the installed stock libraries; no unverified substitute attached |
| J1712 | `PoE:TI_Molex_87898-0204` | No verified mechanical model attached |
| C1727 | `PoE:TI_PCV_1000x1270` | No verified mechanical model attached |
| C1717 | `PoE:TI_SM_RADIAL_F` | No verified mechanical model attached |
| Q1705 | `PoE:TI_TRANS_Fairchild_PQFN08A` | No verified mechanical model attached |
| L1702 | `PoE:TI_WE-SL5` | TI embedded 744272222 STEP has invalid solids and is a different MPN from 744272251; retain archived source but do not attach |

## Physical PCB gates

All-severity physical DRC still reports **791 violations and 499 unconnected
items**: 354 clearance, 199 silk overlap, 199 silk over copper, 19 overlapping
courtyards, 19 drill-range failures and 1 missing outline. These are retained
without exclusions or weakened rules. Hand-solder pad expansion exposes more
clearance issues in the staging arrangement; meaningful placement, fabrication
rules and routing are the next work. The board is not fabrication-ready.

## Reproduce

```sh
python3 hardware/check.py --output /tmp/sierra-capture-check
python3 hardware/tools/check_board_sync.py --output /tmp/sierra-board-check
python3 hardware/tools/check_step_models.py --output /tmp/sierra-step-check.json
```

The last command requires CadQuery. Assertions must remain enabled. For ordinary
editing use KiCad's native update dialogs. `sync_board.py` preserves native links
and refuses a routed board; it is an initial-capture refresh helper.

Generated package parameters and CSVs live beside `Appliance.pretty`. To reproduce
the five new generated footprints, use KiCad Library Tools commit
`4115da4a5f1165c8ddf33d1e29d8f19234b6971d` from the
[official repository](https://gitlab.com/kicad/libraries/kicad-library-tools).
Copy `sierra-bga.yaml` and its two CSVs into `data/package/grid_array`, and
`sierra-connectors.yaml` into `data/connector/generator`. Run its official
`generators.generate` with `-g package/grid_array connector/generator -p 'Sierra*'
-f <staging> -m <staging>`, then run
`hardware/tools/import_generated_footprints.py <staging>`. This applies the
explicit transformer numbering, RJ45 reflection/slots and M.2 odd-row length
corrections. Review outputs and update the PCB natively. No new generic footprint
generator was introduced.
