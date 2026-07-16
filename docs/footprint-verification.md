# Footprint verification matrix (Task 14b)

Gate: `uv run tools/check_3d.py` — every footprint in use must (a) carry a `(model …)`
entry that resolves on disk or be allowlisted in the gate with a reason, and (b) have a
row here whose **Source** is one of `JLC-verified` / `mfr-drawing` / `KiCad-stock` /
`approximation` (the last only for gate-listed re-flags).

Source tags:
- **JLC-verified** — geometry taken from (or verified equal to) the LCSC/EasyEDA footprint
  for the sourced LCSC part, i.e. the land pattern JLCPCB physically assembles against.
- **mfr-drawing** — verified/rebuilt against the manufacturer's own drawing/datasheet.
- **KiCad-stock** — shipped with KiCad 10.0.4 official libraries; used as-is.
- **approximation** — still unobtainable; explicitly re-flagged in `tools/check_3d.py`.

Former Task-14 order-gate approximations (docs/sourcing.md §5): **M.2 LOTES socket,
Würth 750313355 transformer, Bel 2250504-1 magjack, TE MHF4** — all four are now
verified (see their rows). The nano-SIM socket (which was already a disclosed
cross-vendor substitution, not one of the four) remains the only `approximation`.

3D models live in `lib/sierra-to-usb.3dshapes/` and are referenced via
`${KIPRJMOD}/lib/sierra-to-usb.3dshapes/…`. "Envelope box" models are correctly
dimensioned extruded outlines for height/clearance checking, not detailed bodies.

| Footprint | Source | Verification method | 3D model | Refs | LCSC | Changes (Task 14b) |
|---|---|---|---|---|---|---|
| `Button_Switch_SMD:SW_SPDT_PCM12` | KiCad-stock | KiCad 10.0.4 official library, exact package/part match | stock model resolves | SW2 | C221841 | — |
| `Button_Switch_SMD:SW_SPST_B3U-1000P` | KiCad-stock | KiCad 10.0.4 official library, exact package/part match | stock model resolves | SW3, SW4 | — | — |
| `Button_Switch_THT:SW_DIP_SPSTx04_Piano_10.8x11.72mm_W7.62mm_P2.54mm` | KiCad-stock | KiCad 10.0.4 official library, exact package/part match | stock model resolves | SW1 | C99418 | — |
| `Capacitor_SMD:CP_Elec_10x10.5` | KiCad-stock | KiCad 10.0.4 official library, exact package/part match | stock model resolves | C28 | — | — |
| `Capacitor_SMD:CP_Elec_10x12.6` | KiCad-stock | KiCad 10.0.4 official library, exact package/part match | stock model resolves | C4 | — | — |
| `Capacitor_SMD:CP_Elec_6.3x5.8` | KiCad-stock | KiCad 10.0.4 official library, exact package/part match | stock model resolves | C25 | — | — |
| `Capacitor_SMD:CP_Elec_6.3x7.7` | KiCad-stock | KiCad 10.0.4 official library, exact package/part match | stock model resolves | C44, C45, C46 | — | — |
| `Capacitor_SMD:C_0603_1608Metric` | KiCad-stock | KiCad 10.0.4 official library, exact package/part match | stock model resolves | C1, C2, C11 +83 | — | — |
| `Capacitor_SMD:C_0805_2012Metric` | KiCad-stock | KiCad 10.0.4 official library, exact package/part match | stock model resolves | C8, C10, C15 +11 | — | — |
| `Capacitor_SMD:C_1206_3216Metric` | KiCad-stock | KiCad 10.0.4 official library, exact package/part match | stock model resolves | C3, C9, C17 +3 | — | — |
| `Capacitor_SMD:C_1210_3225Metric` | KiCad-stock | KiCad 10.0.4 official library, exact package/part match | stock model resolves | C5, C6, C7 +6 | — | — |
| `Capacitor_SMD:C_1808_4520Metric` | KiCad-stock | KiCad 10.0.4 official library, exact package/part match | stock model resolves | C19 | — | — |
| `Connector_JST:JST_SH_SM04B-SRSS-TB_1x04-1MP_P1.00mm_Horizontal` | KiCad-stock | KiCad 10.0.4 official library, exact package/part match | stock model resolves | J5 | C160390 | — |
| `Connector_PinHeader_2.54mm:PinHeader_1x02_P2.54mm_Vertical` | KiCad-stock | KiCad 10.0.4 official library, exact package/part match | stock model resolves | J6 | — | — |
| `Connector_PinHeader_2.54mm:PinHeader_1x03_P2.54mm_Vertical` | KiCad-stock | KiCad 10.0.4 official library, exact package/part match | stock model resolves | J4 | — | — |
| `Connector_PinHeader_2.54mm:PinHeader_1x04_P2.54mm_Vertical` | KiCad-stock | KiCad 10.0.4 official library, exact package/part match | stock model resolves | J7 | — | — |
| `Crystal:Crystal_SMD_3225-4Pin_3.2x2.5mm` | KiCad-stock | KiCad 10.0.4 official library, exact package/part match | stock model resolves | Y1, Y2 | — | — |
| `Diode_SMD:D_SMA` | KiCad-stock | KiCad 10.0.4 official library, exact package/part match | stock model resolves | D12, D13 | — | — |
| `Diode_SMD:D_SMB` | KiCad-stock | KiCad 10.0.4 official library, exact package/part match | stock model resolves | D6, D7, D24 | C19077533, C19077554, C98802 | — |
| `Diode_SMD:D_SOD-123` | KiCad-stock | KiCad 10.0.4 official library, exact package/part match | stock model resolves | D1, D2, D3 +5 | — | — |
| `Diode_SMD:D_SOD-323` | KiCad-stock | KiCad 10.0.4 official library, exact package/part match | stock model resolves | D17, D18, D26 | — | — |
| `Inductor_SMD:L_0603_1608Metric` | KiCad-stock | KiCad 10.0.4 official library, exact package/part match | stock model resolves | FB1 | C88984 | — |
| `Inductor_SMD:L_1210_3225Metric` | KiCad-stock | KiCad 10.0.4 official library, exact package/part match | stock model resolves | L5, L6 | — | — |
| `Inductor_SMD:L_6.3x6.3_H3` | KiCad-stock | KiCad 10.0.4 official library, exact package/part match | allowlisted: official model not shipped in KiCad 10 3dmodels package | L3 | C2042369 | — |
| `Inductor_SMD:L_Bourns-SRN8040_8x8.15mm` | KiCad-stock | KiCad 10.0.4 official library, exact package/part match | allowlisted: official model not shipped in KiCad 10 3dmodels package | L4 | C36415 | — |
| `Jumper:SolderJumper-2_P1.3mm_Open_RoundedPad1.0x1.5mm` | KiCad-stock | KiCad 10.0.4 official library, exact package/part match | allowlisted: copper-only feature, no body | JP1, JP2, JP3 | — | — |
| `LED_SMD:LED_0603_1608Metric` | KiCad-stock | KiCad 10.0.4 official library, exact package/part match | stock model resolves | D10, D16, D19 +2 | — | — |
| `Package_DFN_QFN:PQFN-8-EP_6x5mm_P1.27mm_Generic` | KiCad-stock | KiCad 10.0.4 official library, exact package/part match | stock model resolves | Q20 | — | — |
| `Package_DFN_QFN:QFN-48-1EP_6x6mm_P0.4mm_EP4.3x4.3mm` | KiCad-stock | KiCad 10.0.4 official library, exact package/part match | allowlisted: official model not shipped in KiCad 10 3dmodels package | U9 | C3013605 | — |
| `Package_DFN_QFN:QFN-56-1EP_7x7mm_P0.4mm_EP3.2x3.2mm` | KiCad-stock | KiCad 10.0.4 official library, exact package/part match | stock model resolves | U24 | C2040 | — |
| `Package_DFN_QFN:Texas_RNH0030A_WQFN-30-1EP_2.5x4.5mm_P0.4mm_EP1.2x3.2mm` | KiCad-stock | KiCad 10.0.4 official library, exact package/part match | allowlisted: official model not shipped in KiCad 10 3dmodels package | U1 | C165155 | — |
| `Package_SO:MSOP-10_3x3mm_P0.5mm` | KiCad-stock | KiCad 10.0.4 official library, exact package/part match | stock model resolves | U13, U14 | C49851 | — |
| `Package_SO:SOIC-8_3.9x4.9mm_P1.27mm` | KiCad-stock | KiCad 10.0.4 official library, exact package/part match | stock model resolves | U11 | — | — |
| `Package_SO:SOIC-8_5.3x5.3mm_P1.27mm` | KiCad-stock | KiCad 10.0.4 official library, exact package/part match | stock model resolves | U25 | C97521 | — |
| `Package_SO:SOP-4_4.4x2.6mm_P1.27mm` | KiCad-stock | KiCad 10.0.4 official library, exact package/part match | stock model resolves | U20 | — | — |
| `Package_SO:SSOP-10-1EP_3.9x4.9mm_P1mm_EP2.1x3.3mm` | KiCad-stock | KiCad 10.0.4 official library, exact package/part match | stock model resolves | U2 | C970725 | — |
| `Package_SO:TSSOP-24_4.4x7.8mm_P0.65mm` | KiCad-stock | KiCad 10.0.4 official library, exact package/part match | stock model resolves | U29 | C443721 | — |
| `Package_SON:Texas_S-PVSON-N10` | KiCad-stock | KiCad 10.0.4 official library, exact package/part match | stock model resolves | U8 | C324071 | — |
| `Package_SON:USON-10_2.5x1.0mm_P0.5mm` | KiCad-stock | KiCad 10.0.4 official library, exact package/part match | stock model resolves | D20, D21, D22 +2 | C138714, C558427 | — |
| `Package_TO_SOT_SMD:SOT-23` | KiCad-stock | KiCad 10.0.4 official library, exact package/part match | stock model resolves | D15, Q1, Q2 +12 | C8490, C8545, C96616 | — |
| `Package_TO_SOT_SMD:SOT-23-5` | KiCad-stock | KiCad 10.0.4 official library, exact package/part match | stock model resolves | U4, U5, U12 +2 | C141836, C176944, C51118 | — |
| `Package_TO_SOT_SMD:SOT-23-6` | KiCad-stock | KiCad 10.0.4 official library, exact package/part match | stock model resolves | D27, D28, U3 +2 | C327676, C88032 | — |
| `Package_TO_SOT_SMD:SOT-563` | KiCad-stock | KiCad 10.0.4 official library, exact package/part match | stock model resolves | U26, U27 | C28927 | — |
| `Package_TO_SOT_SMD:SOT-583-8` | KiCad-stock | KiCad 10.0.4 official library, exact package/part match | stock model resolves | U15 | C5219272 | — |
| `Package_TO_SOT_SMD:SOT-89-3` | KiCad-stock | KiCad 10.0.4 official library, exact package/part match | stock model resolves | Q24, Q25 | — | — |
| `Package_TO_SOT_SMD:TDSON-8-1` | KiCad-stock | KiCad 10.0.4 official library, exact package/part match | stock model resolves | Q22, Q23 | — | — |
| `Package_TO_SOT_SMD:TO-252-2` | KiCad-stock | KiCad 10.0.4 official library, exact package/part match | stock model resolves | Q30, Q31 | — | — |
| `Resistor_SMD:R_0603_1608Metric` | KiCad-stock | KiCad 10.0.4 official library, exact package/part match | stock model resolves | R1, R2, R3 +100 | C126359 | — |
| `Resistor_SMD:R_0805_2012Metric` | KiCad-stock | KiCad 10.0.4 official library, exact package/part match | stock model resolves | R7, R8, R24 | — | — |
| `Resistor_SMD:R_1206_3216Metric` | KiCad-stock | KiCad 10.0.4 official library, exact package/part match | stock model resolves | R20, R21, R22 +2 | — | — |
| `Resistor_SMD:R_2512_6332Metric` | KiCad-stock | KiCad 10.0.4 official library, exact package/part match | stock model resolves | R25, R26, R27 | — | — |
| `TestPoint:TestPoint_Pad_D1.5mm` | KiCad-stock | KiCad 10.0.4 official library, exact package/part match | allowlisted: copper-only feature, no body | TP1, TP2, TP3 +7 | — | — |
| `sierra-to-usb:Bel_2250504-1` | mfr-drawing | Task 14b: vector-extracted the SUGGESTED PCB FOOTPRINT view of TRP/Bel drawing C=2250504 Rev1 (dr-mag-2250504-1.pdf) and cross-checked 8 printed dims (2.032/1.016 pitch, 11.18 VC span, 8.13/6.59 VC rows, 12.7 peg span, 16.13 shield span, 3.18, 8.17) — all exact; pin numbers read off an enlarged crop of the drawing | envelope box 16.8×21.8×13.7 (no mfr STEP published openly) | J8 | — | **REBUILT.** Old approximation had VC pins at x=±3.09 (real ±5.588), VC row sep 1.27 (real 1.543), pegs 3.78 mm too far from signal rows, shield slots 1.4 mm off, and the pin 1–6 row wrongly gapped at center with pins 1–3 shifted +2.032 |
| `sierra-to-usb:DIP-4_SMD_GullWing_FOD817` | mfr-drawing | Task 14b: pin grid (2.54 pitch, ±1.27 rows, ±4.9 pad centers) cross-checked against EasyEDA C2912100 (EL817S, same commodity SMD gull-wing DIP-4 package) — positions agree; our pads are shorter/conservative (1.2×0.7 vs 2.6×1.42). Hand-assembled FOD817DS | EasyEDA EL817S step+wrl (same package family) | U23 | — | 3D model attached; geometry kept |
| `sierra-to-usb:D_MBS-4` | JLC-verified | Task 14b: easyeda2kicad pull of LCSC C2488 (MB10S, JLC-assembled) adopted verbatim | EasyEDA step+wrl | BR1, BR2 | C2488 | **REPLACED.** Old footprint used 3.5 mm pitch / 7.5 mm lead span with 1.0×2.15 pads; JLC-verified part is 2.4 mm pitch / 6.2 mm span with 2.0×1.1 pads — old one would not fit the assembled part |
| `sierra-to-usb:FDMC2523P` | JLC-verified | Task 14b: easyeda2kicad pull of LCSC C890927 (FDMC2523P, Power33-8) adopted; pads renamed 1→S, 2→G, 3→S, 4→S, 5-8→D, EP 9→D to keep Device:Q_PMOS symbol binding | EasyEDA step+wrl | Q21 | — | **REPLACED.** Old approximation put the 8 pins on left/right columns at x=±1.40 (real part: top/bottom rows at y=±1.50) and omitted the 2.55×1.9 exposed DRAIN tab entirely |
| `sierra-to-usb:LED_SK6805-EC15_1.5x1.5mm` | JLC-verified | Task 14b: easyeda2kicad pull of LCSC C2890035 compared — pad positions agree within 0.06 mm, sizes 0.5 vs 0.55 (immaterial); kept ours | EasyEDA step+wrl | U28 | C2890035 | 3D model attached; geometry kept (JLC agrees) |
| `sierra-to-usb:L_Wurth_WE-HCI_744325550` | mfr-drawing | Task 14b: re-verified against Würth datasheet 744325550 rev 004.001 Recommended Land Pattern: pads 4.0×3.85, centers ±3.825 (3.8 gap) — exact match | envelope box 10.1×10.1×4.7 (Würth STEP not machine-retrievable) | L2 | — | 3D envelope attached; geometry confirmed exact |
| `sierra-to-usb:L_Wurth_WE-HCI_74435571500` | mfr-drawing | Task 14b: re-verified against Würth datasheet 74435571500 rev 004.001 Recommended Land Pattern: pads 6.0×6.0, centers ±6.65 (7.3 gap) — exact match | envelope box 18.2×18.3×8.9 (Würth STEP not machine-retrievable) | L1 | — | 3D envelope attached; geometry confirmed exact |
| `sierra-to-usb:M.2_Key-B-SMD_Socket_LOTES_APCI0105-P001A` | JLC-verified | Task 14b: easyeda2kicad pull of LCSC C841658 (LOTES APCI0105-P001A, JLC-assembled) adopted verbatim — this is the land pattern JLC builds against. No KiCad-stock host-socket footprint exists to cross-reference (Connector_PCBEdge only has module card-edge patterns) | EasyEDA step+wrl (full socket body) | CN1 | C841658 | **REPLACED — this was the user-reported mask defect.** Old approximation placed both contact rows on the SAME side, 0.8 mm apart (rows at y=−1.85/−1.05 with 1.1 mm tall pads ⇒ copper/mask overlap between rows — the visibly wrong solder mask), pads 0.25×1.1 vs real 0.30×1.55, pin order X-mirrored, rows really sit at y=±3.77 (7.54 mm apart, one row each side of the connector), and the 2 mechanical tabs (pads 76/77) + 2 locating-peg holes were missing |
| `sierra-to-usb:MHF4_TE_CONMHF4-SMD-G-T` | JLC-verified | Task 14b: easyeda2kicad pull of LCSC C18221168 (the sourced MPN) adopted; GND pads renamed 2/3/4→2 to keep Conn_Coaxial symbol binding. Old approximation agreed within 0.08 mm — the flagged top-tab width (0.6) was confirmed correct | EasyEDA step+wrl | J9, J11, J13 +2 | C18221168 | **REPLACED** (near-identical geometry, now JLC-exact; approximation flag cleared) |
| `sierra-to-usb:NanoSIM_XKB_XKNANO-113` | JLC-verified | Task 14c RE-PICK: JXTCONN CSIM-H137-7P (LCSC C42420236) had no retrievable EasyEDA CAD (404 at every check, Task 14b included) and an unconfirmed CD-switch polarity (docs/sourcing.md Sec.5 Note 3). Replaced with XKB Industrial Precision XKNANO-113 (LCSC C381071): easyeda2kicad --full pull SUCCEEDED (symbol+footprint+3D model all present), and XKB's own drawing (Dwg No. XKNANO-113) documents the CD circuit explicitly (NORMAL=SHORT-to-GND, CARD INSERTED=OPEN) — confirms this project's "grounded=absent" DET convention, closing the CD-polarity order gate with a real citation instead of an assumption. 7 small SMD signal pads (VCC/RST/CLK/CD/GND/VPP/IO) + 4 large SMD shell tabs (merged to one pad number 8, MHF4-GND-tab convention) + 2 unnamed 0.9mm NPTH pegs (excluded from pad-coverage checks, no signal) | EasyEDA step+wrl | SIM1, SIM2 | C381071 | **REPLACED — supersedes the JXTCONN approximation row outright** (part re-picked, not just re-footprinted). Old `NanoSIM_JXTCONN_CSIM-H137-7P` footprint/symbol/3D files left in `lib/` as historical record but no longer referenced by any symbol in the design. |
| `sierra-to-usb:SMA_EdgeMount_BWSMA-KE-Z001` | mfr-drawing | Task 14b: easyeda2kicad pull of LCSC C496549 compared — hole positions agree within 0.014 mm (5.08 grid), drills ours Ø1.4 vs EasyEDA 1.35/1.5 (all pass the Ø1.4-pin datasheet callout); kept ours (BAT Wireless drawing + KiCad stock BWSMA-KWE cross-check, now 3-way agreement) | EasyEDA step+wrl | J10, J12, J14 +2 | C496549 | 3D model attached; geometry kept |
| `sierra-to-usb:TPS23730_RMTR` | mfr-drawing | Task 14b: adopted EasyEDA footprint of TPS23731RMTR C3189532 (identical TI RMT0045A package) and verified dimension-by-dimension against TI's RMT0045A outline/board-layout in the TPS23730 datasheet (8 checks incl. the 0.8 mm double-gaps at pins 9/10 and 29/30, dual EP 3.7×2.1 & 2.9×2.15) | EasyEDA step+wrl (TPS23731 body, same package) | U10 | — | **REPLACED.** Old approximation had the per-side pin distribution wrong (guessed 10/12/10/13; real 13/9/13/10) and guessed EP geometry — pins would have landed in wrong positions |
| `sierra-to-usb:Transformer_SMT_WE750313355` | mfr-drawing | Task 14b: rebuilt from Würth datasheet 750313355 rev 004.001 Recommended Land Pattern (pads 3.05×1.27, 3.00 pitch, columns 26.52 apart, 1–6 left / 12–7 right) | envelope box 21.8×16.6×11.43 (Würth STP link requires their portal) | T1 | — | **REBUILT.** Old approximation had pins on top/bottom edges at 5.06 mm pitch with 19.0 mm row separation — wrong axis, wrong pitch (real 3.00), wrong span (real 26.52); would not fit the physical part |
| `sierra-to-usb:USB_C_Receptacle_HRO_TYPE-C-31-M-04` | JLC-verified | Task 14b: easyeda2kicad pull of LCSC C129018 adopted; shield pads renamed 0→SH to keep symbol binding | EasyEDA step+wrl | J1, J2, J3 | C129018 | **REPLACED.** The physical M-04 is a HYBRID receptacle: A-row 12 SMD pads (0.3×0.9 at y=−3.11) but B-row is 12 THROUGH-HOLE pins (Ø0.4 drills, staggered rows y=−1.19/−1.89, B1→B12 right-to-left) plus 4 THT oval shield legs and 2 NPTH pegs. Old approximation modeled it as an all-SMD JAE-style 24-pad pattern — it could not physically accept the part. **Task 14c:** J2/J3 re-picked from the 16-pin M-12 onto this same M-04 footprint/symbol (schematic-only edit; see docs/sourcing.md). **J2/J3's PCB footprints are now stale** (still placed as the old `Connector_USB:USB_C_Receptacle_HRO_TYPE-C-31-M-12` in `sierra-to-usb.kicad_pcb`, deliberately untouched by this text-only schematic edit) — before layout/fab, open the project in the KiCad GUI and run Tools → Update PCB from Schematic (F8) to re-bind J2/J3 to this footprint, then re-place/re-route their now-different (larger, hybrid SMD+THT) pads. |
| `sierra-to-usb:VFDFPN8_MFF2` | mfr-drawing | Task 14b: pin grid (1.27 pitch, rows ±2.8, central EP) cross-checked against EasyEDA C5122390 (Truphone MFF2, same DFN-8 5×6 package) — positions exact within 0.004 mm; ours kept (MFF2 packaging-spec numbering). Hand-assembled ST4SIM-200M | EasyEDA DFN-8 step+wrl (rotated 90°) | U30 | — | 3D model attached; geometry kept (grid confirmed exact) |
