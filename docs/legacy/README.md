# Superseded design evidence

The current design effort is [full-adapter](../../full-adapter/README.md).
Everything under this directory is historical evidence, not an active board.
The original full-board specification and verification corrections remain in
`docs/superpowers` and `docs/verification.md`; the older handoff reviews remain
in `handoff/m2-sierra-handoff/docs`.

The complete old source trees, including the compact generators and their
generation guards, are recoverable from local checkpoint `4353916`. Board and
schematic files, generators and obsolete exports have been removed from the
active tree. Links in historical reports to those artifacts refer to that
checkpoint. Links to `build/` reports now correspond to the neighboring
`historical-build-evidence/` directories; generated binary exports are retired.

Reusable compact footprints, symbols, models, datasheets, sourcing snapshots,
pin audits and mechanical/electrical reviews are retained under `compact/`.
Vendor PDFs and extracted text remain local and ignored, preserving the earlier
repository's non-redistribution convention. Existing root libraries remain in
`lib/`. Neither library is automatically approved for use in the new board.

The checkpoint credential scanner flagged public DigiKey ordering numbers in
the distributor snapshot. Redundant `DigiKeyProductNumber` fields were omitted
from the committed copy; MPN and sourcing information remain. The original
snapshot is retained locally in ignored `tmp/distributor-stock-original.json`.

The old local pre-commit hook calls `tools/check_nets.py` and
`tools/check_netclasses.py`. Those entry points now check retirement integrity
and explicitly report that no replacement electrical validation has run.
Their old circuit assertions are preserved in the checkpoint. New circuit
validation must be installed before the replacement schematic is committed;
the retirement checks refuse to accept new CAD files as electrically checked.
