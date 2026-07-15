# ERC Waivers

Tracks intentionally-accepted ERC warnings (with justification), sheet by sheet,
as the hierarchy is populated. Task 3 baseline was 0 errors / 0 warnings on an
empty scaffold. Task 4 (power_input, after the EVM-093 transcription fix pass)
is the first sheet with real content; `$KCLI sch erc sierra-to-usb.kicad_sch`
now reports **0 errors / 259 warnings**, all four categories below, all on this
sheet.

| Date | Warning | Justification |
| ---- | ------- | -------------- |
| 2026-07-14 | `isolated_pin_label` ×5 — global labels `POE_VA+`, `POE_VA-`, `POE_VB+`, `POE_VB-` (BR1/BR2 AC inputs) and `+3V3` (R4 pull-up) each connect to only one pin | The four PoE center-tap labels are this sheet's *export* of the PoE pairs — the matching consumer (J4 magjack on `sheets/ethernet.kicad_sch`) is wired in Task 10; until then a single-pin global label is correct. `+3V3` is referenced here only as CH224K PG's pull-up rail; it is *deliberately* a plain global label (not a power symbol, no PWR_FLAG) because the rail is produced on the power_rails sheet (later task) and the Task-4 review (MINOR 9) forbids this sheet asserting it driven. Both warnings clear when the producing/consuming sheets land. |
| 2026-07-14 | `footprint_link_issues` ×95 — every placed symbol's `Footprint` field points at a library not yet present in `fp-lib-table` | Footprint/library binding is explicitly a Task 14 activity per the plan. The `Footprint` string on each symbol records the *intended* package (per EVM-093 BOM / datasheets) so Task 14 has the real target; only the fp-lib-table registration is deferred. Count rose from 50 to 95 with the EVM-093 fix pass (sync-rect stage, snubbers, full compensation network, input filter added). |
| 2026-07-14 | `lib_symbol_mismatch` ×1 — `TCMT1107` cached copy in this sheet's `lib_symbols` differs from the stock `Isolator` library on disk | The stock symbol uses KiCad's `extends` inheritance (`TCMT1107`→`TCMT1100`); the generator flattens it into a standalone cache entry so the schematic is self-contained. Electrically identical (same pin numbers/positions/types), differs only structurally — cosmetic. (The Task-4 `SMAJ13A`/`SMAJ58A` flattening waivers are gone: the fix pass replaced them with project-library unidirectional TVS symbols with explicit pin-1-cathode polarity, per review MINOR 8.) |
| 2026-07-14 | `endpoint_off_grid` ×158 — pin/label/power-symbol endpoints not on KiCad's default edit grid | This sheet is script-authored: every label/power-symbol anchor sits at the *exact* absolute coordinate of the pin it connects to, rather than snapped to the editor's visual grid. Electrically correct (verified via `check_nets.py` and a full generator-intent-vs-exported-netlist diff of all 317 pin assignments) but cosmetically off-grid; a GUI re-snap pass would silence this without changing connectivity and is not required for the ERC error gate. |
