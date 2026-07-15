# ERC Waivers

Tracks intentionally-accepted ERC warnings (with justification), sheet by sheet,
as the hierarchy is populated. Task 3 baseline was 0 errors / 0 warnings on an
empty scaffold. Task 4 (power_input, after the EVM-093 transcription fix pass)
is the first sheet with real content; `$KCLI sch erc sierra-to-usb.kicad_sch`
now reports **0 errors / 259 warnings**, all four categories below, all on this
sheet.

Task 5 (power_rails: buck + LDOs + INA226 telemetry + ADC dividers) adds 87
more warnings, all in the same three pre-existing categories (no new
category) — `$KCLI sch erc sierra-to-usb.kicad_sch` now reports
**0 errors / 346 warnings**. Two ERC *errors* surfaced during development and
were fixed by design changes (not waived): `pin_to_pin` "Power output and
Power output are connected" (a redundant `PWR_FLAG` was placed on `+1V8` and
`+3V3_MCU`, both of which already have a legitimate driver — U5/U17's `VOUT`
pins are `power_out` type on the stock AP2112K base symbol; removed the
redundant flags) and `power_pin_not_driven` on `U17.VIN` (the diode-OR node
`N_OR17` had no driver at all — added a `PWR_FLAG` there, the same fix
pattern as the pre-existing `+12V_BUCK`/`+3V3`/`+3V3_MOD` flags). A third,
`pin_not_driven` on `U13.SCL` (I2C bus not yet mastered by anything, since
the mcu sheet is a future task), was resolved the same way: a `PWR_FLAG` on
`I2C_SCL` satisfies ERC's "Input pin not driven by any Output pins" check
(a `PWR_FLAG` pin is `power_out` type, which the check accepts as a driver
for a plain signal net, not only for power nets) without fabricating a
phantom I2C master.

| Date | Warning | Justification |
| ---- | ------- | -------------- |
| 2026-07-14 | `isolated_pin_label` ×5 — global labels `POE_VA+`, `POE_VA-`, `POE_VB+`, `POE_VB-` (BR1/BR2 AC inputs) and `+3V3` (R4 pull-up) each connect to only one pin | The four PoE center-tap labels are this sheet's *export* of the PoE pairs — the matching consumer (J4 magjack on `sheets/ethernet.kicad_sch`) is wired in Task 10; until then a single-pin global label is correct. `+3V3` is referenced here only as CH224K PG's pull-up rail; it is *deliberately* a plain global label (not a power symbol, no PWR_FLAG) because the rail is produced on the power_rails sheet (later task) and the Task-4 review (MINOR 9) forbids this sheet asserting it driven. Both warnings clear when the producing/consuming sheets land. |
| 2026-07-14 | `footprint_link_issues` ×95 — every placed symbol's `Footprint` field points at a library not yet present in `fp-lib-table` | Footprint/library binding is explicitly a Task 14 activity per the plan. The `Footprint` string on each symbol records the *intended* package (per EVM-093 BOM / datasheets) so Task 14 has the real target; only the fp-lib-table registration is deferred. Count rose from 50 to 95 with the EVM-093 fix pass (sync-rect stage, snubbers, full compensation network, input filter added). |
| 2026-07-14 | `lib_symbol_mismatch` ×1 — `TCMT1107` cached copy in this sheet's `lib_symbols` differs from the stock `Isolator` library on disk | The stock symbol uses KiCad's `extends` inheritance (`TCMT1107`→`TCMT1100`); the generator flattens it into a standalone cache entry so the schematic is self-contained. Electrically identical (same pin numbers/positions/types), differs only structurally — cosmetic. (The Task-4 `SMAJ13A`/`SMAJ58A` flattening waivers are gone: the fix pass replaced them with project-library unidirectional TVS symbols with explicit pin-1-cathode polarity, per review MINOR 8.) |
| 2026-07-14 | `endpoint_off_grid` ×158 — pin/label/power-symbol endpoints not on KiCad's default edit grid | This sheet is script-authored: every label/power-symbol anchor sits at the *exact* absolute coordinate of the pin it connects to, rather than snapped to the editor's visual grid. Electrically correct (verified via `check_nets.py` and a full generator-intent-vs-exported-netlist diff of all 317 pin assignments) but cosmetically off-grid; a GUI re-snap pass would silence this without changing connectivity and is not required for the ERC error gate. |
| 2026-07-14 | (Task 5, power_rails) `endpoint_off_grid` ×59 | Same cause as the power_input row above — this sheet uses the identical script-authored, label-at-exact-pin-coordinate generator idiom (see task-5-report.md). |
| 2026-07-14 | (Task 5, power_rails) `footprint_link_issues` ×26 — every placed symbol's `Footprint` field points at a library not yet present in `fp-lib-table` | Same as the power_input row above: footprint/library binding is Task 14. `Footprint` strings record the intended package per `docs/sourcing.md` (MSOP-10 for INA226AIDGSR, TSOT-23-6 for TPS565201DDCR, SOT-23-5 for both AP2112K LDOs) so Task 14 has the real target. |
| 2026-07-14 | (Task 5, power_rails) `lib_symbol_mismatch` ×2 — `AP2112K-1.8` and `AP2112K-3.3` cached copies differ from the stock `Regulator_Linear` library on disk | Same cause and same resolution as the Task-4 `TCMT1107` row above: both stock symbols use KiCad's `extends` inheritance (`AP2112K-1.8`/`AP2112K-3.3` → `AP2204K-1.5`); the generator flattens each into a standalone cache entry (own Reference/Value/Footprint/Datasheet/Description properties, but the base symbol's graphics and pins) so the schematic is self-contained. Electrically identical (same pin numbers/positions/types — VIN(1)/GND(2)/EN(3)/NC(4)/VOUT(5)), differs only structurally — cosmetic. |

Task 6 (m2: M.2 socket, vendor-safe VCC policy, strap plane) adds 118 more
warnings, all in the same four pre-existing categories (no new category) —
`$KCLI sch erc sierra-to-usb.kicad_sch` now reports **0 errors / 464
warnings**. Breakdown: `endpoint_off_grid` 217→299 (+82), `footprint_link_issues`
121→139 (+18), `isolated_pin_label` 5→23 (+18), `lib_symbol_mismatch` 3→3
(+0 — the flattened `2N7002` did not trigger a new mismatch, unlike Task 5's
`AP2112K` flattening, because kicad-cli's own `extends`-resolution of the
stock `2N7002` happens to produce the identical structure my flattener does).

Seven ERC *errors* surfaced during development and were fixed by design
changes (not waived): `pin_not_driven` on 7 CN1 pins whose stock-symbol pin
*type* is literally "input" (`PCIE_MTX_N/P`, `SS_MOD_RX_N/P`,
`UIM1_RST/CLK/VDD`) with no other schematic component providing an
Output-type pin on those nets — the real driver for all of these is the
pluggable module itself (invisible to ERC's connectivity model, since a
connector symbol has no "the module drives this" pin). Fixed the same way as
Task 5's `I2C_SCL` forward-reference: a `PWR_FLAG` colocated with a matching
`global_label`. **Root cause of an intermediate false "still broken" state,
recorded for future reference:** the fix did not work the first time it was
applied — ERC kept reporting both `pin_not_driven` *and* a new
`label_dangling` on the same 7 nets — because the generator embedded
`power:GND` in this sheet's own `lib_symbols` cache but forgot to do the same
for `power:PWR_FLAG`, silently falling back to the *system* library table's
copy for pin geometry. That fallback copy apparently isn't recognized as
"touching" a coincident label by kicad-cli's ERC the way an embedded-cache
copy is (empirically confirmed: adding the missing cache entry, with no other
change, took both error types to zero). Every symbol used on a sheet needs
its own `lib_symbols` cache entry, not just the ones whose *pins* the
generator programmatically decorates — this project's established idiom
(Tasks 4/5) already did this correctly for `power:GND`; Task 6 initially
missed it for `power:PWR_FLAG` specifically.

| Date | Warning | Justification |
| ---- | ------- | -------------- |
| 2026-07-14 | (Task 6, m2) `isolated_pin_label` ×15 — global labels `PCIE_MRX_P/N`, `USB2_MOD_DP/DM`, `UIM1_DET`, `UIM1_IO`, `PCIE_REFCLK_P/N`, `UIM2_DET/IO/CLK/RST/VDD`, `WWAN_LED_N`, `LED_RET` each connect to only one pin on this sheet | **Row edited by Task 7 per its brief's explicit instruction** (was ×18, listed `SS_MOD_TX_C_P/N` and `VBUS_DATA` too — both now removed from this row, count reduced 18→15, since Task 7's `sheets/usb3_data.kicad_sch` supplies the second touch point for all three: `SS_MOD_TX_C_P/N` via C58/C59 + D22 + the module-side global labels, `VBUS_DATA` via J1/D24/U4/R69/U1.VDD5). Remaining 15 are still-open documented forward references: the matching consumer/producer lands on a future sheet (usb2_debug/Task 8, mcu/Task 9, ethernet/Task 10, sim/Task 11) per the plan's own sheet-dependency order. Clears once each producing/consuming sheet lands, same pattern as Task 4/5's forward-reference waivers. |
| 2026-07-14 | (Task 6, m2) `footprint_link_issues` ×18 — `CN1` (`Connector_M.2`), `JP1-3` (`Jumper`), `TP1-9` (`TestPoint`), `D19` (`LED_SMD`), bulk caps (`CP_Elec_6.3x7.7`) point at libraries not yet in `fp-lib-table` | Same as the Task 4/5 rows above: footprint/library binding is Task 14. `Footprint` strings record the intended package (`Connector_M.2:M.2_Key-B-SMD` for CN1 per the LOTES APCI0105-P001A datasheet, `docs/sourcing.md` row 20) so Task 14 has the real target. |
| 2026-07-14 | (Task 6, m2) `endpoint_off_grid` ×82 | Same cause as the Task 4/5 rows above — this sheet uses the identical script-authored, label-at-exact-pin-coordinate generator idiom. |

## Task 6 review Fix pass (2026-07-14)

Fixing the 5 findings from the Task 6 (m2) review (VBUS_SENSE P-FET force-path
rebuild, R59/R60 1% tolerance, WWAN LED rewired through the module's status
pin, C44-C57 footprint prefixes, task-6-report.md refdes table correction)
changes `$KCLI sch erc sierra-to-usb.kicad_sch` from **0 errors / 464
warnings** to **0 errors / 452 warnings** (`endpoint_off_grid` 299→302,
`footprint_link_issues` 139→125, `isolated_pin_label` 23→22,
`lib_symbol_mismatch` 3→3 — no new category). Net delta: 16 warnings resolved,
4 new, both fully accounted for below.

**Resolved (16):**
- `footprint_link_issues` ×14 — C44-C57's `Footprint` fields were bare
  names with no library prefix (`CP_Elec_6.3x7.7`, `C_0805_2012Metric`,
  `C_0402_1005Metric` — not even a valid `Library:Footprint` lib_id, unlike
  the rest of this sheet's parts). Fix 4 added the `Capacitor_SMD:` prefix
  to all 14, verified against the real `.kicad_mod` files in KiCad 10's
  stock `Capacitor_SMD.pretty`. `Capacitor_SMD` is a standard footprint
  library already present in this machine's global `fp-lib-table` (unlike
  `Connector_M.2`/`Jumper`/`TestPoint`/`LED_SMD`, which is why CN1/JP1-3/
  TP1-9/D19 still show `footprint_link_issues` below — same as the
  pre-existing Task 6 row, that part is genuinely Task 14 work), so this
  resolves cleanly rather than needing a waiver.
- `isolated_pin_label` ×2 — `WWAN_LED_N` and `LED_RET`. Fix 3 gives
  `WWAN_LED_N` a second same-sheet touch point (D19's cathode, alongside
  the pre-existing CN1.10), so it's no longer isolated on this sheet.
  `LED_RET` is deleted outright (D19's cathode no longer references it) —
  removed, not a forward reference anymore, so the old Task 6 waiver row's
  mention of `LED_RET` is superseded by this section for that one label
  (the row itself is left unedited per the "no existing assertion/waiver
  text is silently rewritten" convention — this section is the correction).

**New (4) — same categories/root causes as the existing Task 6 waiver rows
above, not a new waiver category:**
- `endpoint_off_grid` ×3 — `#PWR91` (new GND on Q5's source), `Q32` pin 1
  (gate), `R68` pin 1. Same cause as the existing Task 6 `endpoint_off_grid`
  row: this sheet places labels/power symbols at the exact absolute pin
  coordinate of the component they connect to rather than snapping to the
  editor grid. Verified electrically correct via `uv run
  tools/check_nets.py` (all Fix 1 pin-function assertions pass) and the
  `kicad-cli sch export netlist` pin-to-net dump.
- `isolated_pin_label` ×1 — global label `LED_PWR` (R67's new supply-side
  pin) connects to only one pin on this sheet. This is a deliberate,
  documented forward reference: Task 9 (mcu) drives `LED_PWR` from `+3V3`
  through the WWAN kill switch, per Fix 3. Same pattern as the pre-existing
  Task 6 forward-reference waivers (`WWAN_LED_N` originally, `VBUS_DATA`,
  etc.) — clears once Task 9 lands.

No new `footprint_link_issues` or `lib_symbol_mismatch` from the new parts:
`Q32` (`sierra-to-usb:DMG3415U`, footprint `Package_TO_SOT_SMD:SOT-23`) and
`R68` (`Device:R_Small`, footprint `Resistor_SMD:R_0603_1608Metric`) both
reuse footprint libraries already used elsewhere on this sheet (Q1-Q5,
R59-R67) that resolve via the global `fp-lib-table` without a project-local
entry. The new `sierra-to-usb:DMG3415U` project-library symbol's cached copy
in `sheets/m2.kicad_sch`'s `lib_symbols` was built to be structurally
identical to the `lib/sierra-to-usb.kicad_sym` master (same property
node shapes, no stray `pin_names` override) specifically to avoid adding a
5th `lib_symbol_mismatch` entry — confirmed 3→3, unchanged.

| Date | Warning | Justification |
| ---- | ------- | -------------- |
| 2026-07-14 | (Fix pass) `endpoint_off_grid` ×3 — `#PWR91` Pin 1, `Q32` Pin 1 `[G]`, `R68` Pin 1 | Same script-authored, label/symbol-at-exact-pin-coordinate idiom as every other `endpoint_off_grid` row on this sheet. Connectivity verified via `check_nets.py` and a `kicad-cli sch export netlist` pin dump, not just ERC. |
| 2026-07-14 | (Fix pass) `isolated_pin_label` ×1 — global label `LED_PWR` (R67 pin 2) connects to only one pin on this sheet | Documented forward reference: Task 9 (mcu) drives `LED_PWR` from `+3V3` through the WWAN kill switch (Fix 3). Same pattern as this sheet's other Task 6 forward-reference waivers; clears when Task 9 lands. |

## Task 7 (usb3_data: J1 + HD3SS3220 mux + AC caps + ESD)

`$KCLI sch erc sierra-to-usb.kicad_sch` goes from Task-6-fix-pass's **0
errors / 452 warnings** to **0 errors / 490 warnings** (+38). Breakdown:
`endpoint_off_grid` 302→337 (+35), `footprint_link_issues` 125→127 (+2),
`isolated_pin_label` 22→19 (−3, see the edited Task 6 row above),
`lib_symbol_mismatch` 3→5 (+2), and one **new category**: `pin_to_pin` (+2).
Two ERC *errors* surfaced during development and were fixed by design (not
waived) — see below.

**Errors found and fixed (not waived):**
1. `label_dangling` ×2 on `U1` (HD3SS3220 mux) pins `VDD5`/`EN` (net
   `VBUS_DATA`) and `VOUT` (net `+3V3_MUX`) — root cause: the sheet's
   `lib_symbols` cache embedded `Regulator_Linear:AP2112K-3.3` via a plain
   rename of the stock symbol text, but the stock `AP2112K-3.3` symbol is
   itself `(extends "AP2204K-1.5")` — renaming without flattening left an
   empty shell with no pins in the cache, so kicad-cli silently fell back to
   resolving the base symbol elsewhere, and that fallback pin geometry
   didn't register as "touching" the coincident global label/local label —
   the **exact same failure mode** already root-caused in the Task 6 section
   above for `power:PWR_FLAG` (there: a missing cache entry causing a
   system-library fallback; here: an unflattened `extends` cache entry
   causing the same kind of fallback). Fixed by flattening `AP2112K-3.3`
   the same way Task 5 already documented doing for `AP2112K-1.8`/`-3.3` on
   `power_rails.kicad_sch` (merge the `AP2204K-1.5` base's graphics/pin
   sub-units, renamed, with `AP2112K-3.3`'s own top-level properties) —
   confirmed by re-running ERC (both errors cleared, no other change).
2. `power_pin_not_driven` ×1 on `U1.VDD5` (`power_in` type, net
   `VBUS_DATA`) — `J1`'s VBUS pins are typed `passive` (matching the stock
   `USB_C_Receptacle_USB2.0_16P` convention used by `J2`), which doesn't
   satisfy ERC's driver requirement for a `power_in` pin the way it does for
   a plain `input` pin. Fixed the same way as this project's pre-existing
   `+12V_BUCK`/`+3V3`/`+3V3_MOD`/`I2C_SCL` forward-reference `PWR_FLAG`s
   (Tasks 4/5/6): added a `power:PWR_FLAG` colocated with `D24`'s cathode
   pin (already on `VBUS_DATA`), asserting "this net is genuinely driven
   from off-board (through J1), trust me" — confirmed by re-running ERC.

| Date | Warning | Justification |
| ---- | ------- | -------------- |
| 2026-07-14 | (Task 7) `footprint_link_issues` ×2 — `D24` (`sierra-to-usb:SMAJ5.0A`, `Diode_SMB:D_SMB`) and `U1` (`sierra-to-usb:HD3SS3220`, `Package_DFN_QFN:HD3SS3220_RNH0030A`) | `D24` matches the pre-existing `SMAJ13A`/`SMAJ58A` pattern exactly (`Diode_SMB` isn't a registered library on this machine — same as `D6`/`D7`). `U1`'s WQFN-30 (RNH) package has no matching stock footprint file; `Package_DFN_QFN` itself is registered but `HD3SS3220_RNH0030A` doesn't exist in it. Both record the intended package per `docs/sourcing.md` (LCSC C165155, WQFN-30-EP 2.5×4.5) for Task 14 to bind. Everything else new on this sheet (J1 → `Connector_USB:USB_C_Receptacle_HRO_TYPE-C-31-M-17`, D20-D23 → `Package_SON:USON-10_2.5x1.0mm_P0.5mm`, U4 → `Package_TO_SOT_SMD:SOT-23-5`, new R/C → `Resistor_SMD:R_0603_1608Metric`/`Capacitor_SMD:C_0603_1608Metric`) resolved cleanly against libraries already registered on this machine — no waiver needed for those. |
| 2026-07-14 | (Task 7) `lib_symbol_mismatch` ×2 — `TPD4E05U06DQA` (`D23`) and a second `AP2112K-3.3` instance (`U4`) cached copies differ from the stock `Power_Protection`/`Regulator_Linear` libraries on disk | Same cause and resolution as every other row in this category: both stock symbols use `extends` (`TPD4E05U06DQA`→`TPD4EUSB30`, `AP2112K-3.3`→`AP2204K-1.5`); the generator flattens each into a standalone cache entry (own properties, base symbol's graphics/pins) so the schematic is self-contained. Electrically identical, differs only structurally — cosmetic. |
| 2026-07-14 | (Task 7) `endpoint_off_grid` ×35 | Same script-authored, label/symbol-at-exact-pin-coordinate idiom as every other row in this category. Connectivity verified via `uv run tools/check_nets.py` (all pass) and a `kicad-cli sch export netlist --format kicadxml` pin-to-net dump (SS-pair mapping table in `task-7-report.md`), not just ERC. |
| 2026-07-14 | (Task 7) `pin_to_pin` ×2 (**new category**) — "Pins of type Bidirectional and Power output are connected": `U1` pins `RXP`/`RXN` (net `SS_MOD_RX_P`/`SS_MOD_RX_N`) tied to `#FLG19`, a `power:PWR_FLAG` on `sheets/m2.kicad_sch` | This `PWR_FLAG` was added in Task 6 specifically because `CN1.29`/`CN1.31` are `input`-typed pins with no visible driver *on the m2 sheet alone* (the module itself is invisible to ERC's connectivity model). Task 7 now supplies a real `bidirectional`-type driver on the same global net (`U1.RXP`/`RXN`, `D22`'s flow-through ESD pins) — the flag is now redundant (same situation Task 5 resolved by *removing* the equivalent redundant `+1V8`/`+3V3_MCU` flags), but removing it means editing `sheets/m2.kicad_sch`, which is outside this task's declared file scope (`sheets/usb3_data.kicad_sch` + `tools/netchecks.txt` only, per the brief). Flagged as a carry-forward cleanup for whichever task next touches `m2.kicad_sch`, not fixed here. Not an error — informational pin-type-mix warning only. |
