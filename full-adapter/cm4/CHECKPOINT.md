> **Superseded 2026-09-28:** CM4/RK3568 work is preserved as history.
> Do not execute the continuation instructions below. See the current
> [MCU / 2.5GbE PoE appliance requirements](../../REQUIREMENTS.md).

# CM4 implementation checkpoint — 2026-09-10

Saved at the user's request to pause and report status. This is an incomplete
engineering checkpoint, **not a fabrication release or goal completion**.
The latest CAD milestone is `97f1c8f`; the following checkpoint commit contains
this document and regulator research only. Resume from the branch tip and
preserve all subsequent work. The ready-to-paste request is in
[CM4-NEXT-PROMPT.md](../CM4-NEXT-PROMPT.md).

## Read and coordinate before editing

Work in `/Users/alex/sierra-to-usb` on `codex/full-adapter`. Read this checkpoint,
[CM4-HANDOFF.md](../CM4-HANDOFF.md), [CONTINUE.md](../CONTINUE.md), repository
instructions, and the original objective at
`/Users/alex/.codex/attachments/9070579f-f60d-47d5-8fe5-bbe63ea3adf6/pasted-text-1.txt`.
The approved CM4 Lite/native gigabit/isolated PoE architecture supersedes the
original discrete RK3568 and 2.5GbE directions. Prefer the non-wireless 1 GB
CM4001000; saving money matters. Do not substitute CM5 for convenience.

The earlier task `01a088e4-ec23-77c0-a437-6ba4a5e71941` confirmed idle at
`340c622` and yielded write ownership. No other editor was active at this
checkpoint; check again on resumption. Do not touch `/Users/alex/nandapters`,
its router container, or stale shared KiCad GUI projects. Preserve historical
RK3568 CAD, libraries, research and checks. Never reset, push, purchase, reserve
inventory or order fabrication. Make local milestone commits.

## Actual saved implementation

| Milestone | Scope |
| --- | --- |
| `340c622` | Approved architecture handoff; no CM4 CAD at that time |
| `2f316aa` | CM4 Lite core, two physical Hirose sockets, microSD and core controls |
| `2de318b` | Native gigabit magnetics, Cat5e jack, PHY-side ESD and isolated PoE termination |
| `b48844c` | USB-C auxiliary input, PD selection, voltage qualification and source mux |
| `97f1c8f` | Exact modem assembly profiles, M.2 socket and two protected SIM interfaces |

Current project: `cad/cm4-carrier.kicad_pro`, with an 18-page hierarchy and
105 BOM components including 11 DNP profile links. The module is separately
fitted. **There is no integrated CM4 PCB.** Ignored library review fixtures and
the historical processor escape coupon are not this board.

The last CAD milestone passed staged connectivity, component/land and modem
profile assertions, together with the preserved historical checks. Current
ERC has **67 unfinished findings**: 59 isolated pin labels, five undriven pins,
and three undriven power pins; there are no ERC exclusions. These are tracked
integration gaps, not acceptable release results. Partial schematic pages and
new footprint/model fixtures were visually reviewed. Schematic/PCB parity,
carrier DRC, routing, mechanical integration and fabrication review have not
been performed because the carrier PCB does not exist.

Detailed circuit evidence and limitations are in
[CORE-REVIEW.md](research/CORE-REVIEW.md),
[ETHERNET-REVIEW.md](research/ETHERNET-REVIEW.md),
[POWER-INPUT-REVIEW.md](research/POWER-INPUT-REVIEW.md), and
[MODEM-REVIEW.md](research/MODEM-REVIEW.md).

The modem capture has seven explicit profiles: safe unconfigured, EM9190
sub-6 GHz, EM9191, EM929x SIM1, EM929x external SIM2, RM520NGLAA-M20-SGASA
SIM1/internal eSIM, and that exact Quectel variant with external SIM2.
All eleven routing links default DNP. Profile assertions check supply isolation
and conditional SIM2/QTM contacts. EM9190 mmWave QTM hardware is outside the
captured sub-6 profile; RM520NGLAP PCIe-only variants are not interchangeable.
These profile checks do not establish firmware compatibility or powered behavior.

## Resume implementation here

1. Finish and capture modem power/control and the main 5 V supply. Close
   simultaneous load, tolerance, transient, current-limit, startup/shutdown,
   discharge, loop stability and thermal calculations. The regulator candidates
   below are research, not implemented circuits. Preserve modem shutdown
   sequencing and prevent back-power through every control or sense line.
2. Finish USB-C protection and isolated PoE. The TPS2121 has a 24 V absolute
   maximum; an ordinary 22 V TVS with a 30+ V clamp is insufficient. Its present
   nominal 4.5 A current limit does not enforce a 3 A USB-C contract. Qualify
   actual input-capacitor effective capacitance, PD/hotplug behavior, source
   changes, reverse leakage and hardware load limits. Capture the PoE bridges,
   qualified isolated converter and class-detection gating. Select class from
   the completed simultaneous worst-case budget, including conversion losses.
3. Resolve the USB3 controller's hardware and firmware qualification, then
   capture PCIe, clocks, rails, reset, USB3 and USB2 modem paths. Native CM4 USB2
   alone is insufficient. Continue independent circuits while documentation
   access remains outstanding; do not treat the candidate as already qualified.
4. Complete GPIO/UART/SPI/I2C/Qwiic, useful analog inputs, debug/recovery,
   independent modem controls, antenna interfaces, mounting and cooling.
   Correct the microSD supply protection: its current 1 A switch limit exceeds
   the CM4's 600 mA 3.3 V output rating. Qualify an appropriate lower limit and
   the combined auxiliary rail load. Review the SD connector land/model.
5. Complete the readable hierarchy and electrical review; resolve real ERC
   faults. Build the actual integrated PCB, choose a documented JLC stackup and
   impedance rules, verify footprints, place and fully route it. Finish parity,
   DRC, connectivity/profile assertions, all unrouted nets and 3D/mechanical
   review. Generate and review exact BOM and placement, Gerbers/drills,
   assembly information, schematic PDF and board renders. Finish programming,
   recovery, manufacturing tests and the complete cost estimate. Bench tests
   may remain explicitly pending; missing CAD and electrical faults may not.

## Regulator research saved after the last CAD milestone

Catalog records are in [regulator-candidates.json](research/regulator-candidates.json);
manufacturer URLs and cached-file hashes are in
[regulator-sources.json](research/regulator-sources.json). **No regulator or
eFuse schematic/footprint was added by this research.**

The working modem-supply proposal is TPS54560DDAR (`C31966`), an externally
compensated asynchronous buck, producing approximately 3.864 V at MODEM_RAW
(38.3 kohm/10 kohm divider), followed by TPS259470LRPWR (`C3662793`) for active
current limiting, reverse blocking, adjustable OVLO and independent enable.
Put the modem bulk capacitance after the eFuse so its ramp controls capacitor
charging; buck feedback is before the eFuse. This topology still needs full
electrical and thermal qualification. The 470L latches after a thermal fault;
it does not immediately latch on every overcurrent event.

Candidate support parts: Sunlord MWSA1004S-6R8MT (`C408485`), Diodes
B560C-13-F (`C85100`), Murata GRM32ER71H106KA12L (`C77102`) 10 uF/50 V X7R,
and two JIERR MA6.3V1000M6X10 (`C54321568`) 1000 uF/6.3 V polymer capacitors.
The JIERR manufacturer table lists 14 milliohm ESR and 4.1 A ripple at 100 kHz,
but lands/reflow/derating remain unreviewed. Its download returned HTTP 403;
an alternate manufacturer-document mirror is recorded in the source JSON.
The cached Sunlord PDF is scanned and needs visual page review. Obtain and
review the exact catch-diode datasheet and MLCC DC-bias/temperature data.

Reject Ruilong `8102LAM0812E2RR00O` (`C723059`) as an SMD choice: the maker's
ordering code identifies a radial/bagged component despite the catalog SMD
label. Lelon OVZ102M0JTR-0812 (`C250085`) is a possible alternative bulk
capacitor, not a qualified substitute.

TPS54560's published small-signal model permits an explicit compensation
analysis. Include pre-eFuse capacitance, eFuse resistance and post-eFuse bulk,
load/ESR/tolerance corners, and off/on profiles. Its internal ramp is about
1024 switching cycles; do not connect large bulk directly and assume startup
will work. A 200 kohm RT resistor proposes approximately 500 kHz. Proposed
eFuse UV/OV dividers and a roughly 20 ms ramp remain uncalculated drafts.
Candidate current-limit resistor 976 ohm RT0603BRD07976RL (`C861607`) is
sourced; a proposed parallel 1.45 kohm Sierra profile resistor was not sourced
or qualified. Check guaranteed limits, not just the nominal 3334/R relation.

LM61460AANRJRR (`C2864505`) remains a possible main 5 V regulator. Its TI
PSpice library is encrypted and is not ngspice-readable; do not decrypt it.
The TI calculator XLSM was downloaded/extracted only, not evaluated. The
TPS56637 datasheet's supported output-filter range does not justify attaching
1.5 mF directly. TPS566238's 18 V input limit excludes the 20 V auxiliary
input. Do not promote any catalog candidate to a selected BOM part without
the needed qualification.

## External dependencies and unresolved engineering bounds

- Renesas uPD720202K8-711-BAA-A (`C3025201`) is the low-cost USB3 candidate;
  current hardware documentation and firmware access require manufacturer
  sign-in. An earlier request for the user to sign in is unanswered. The
  cached 2013 Rev. 5 datasheet is not the current hardware manual. Linux uses
  `renesas_usb_fw.mem` through xhci-pci-renesas; firmware acquisition, license,
  exact revision, initramfs availability and cold/warm/recovery boot behavior
  remain unqualified. A forum boot report is not this board's validation.
  The -701 ROM option needs its own programming/configuration qualification.
  Publicly documented TUSB7320 is a more expensive alternative, also requiring
  errata/Linux review; do not switch merely to avoid documenting the tradeoff.
- EM929x Rev. 7.1 and Quectel RM520N-GL V1.0 are cached. Reconciliation against
  gated current revisions (EM929x 7.2 and Quectel 1.4) remains outstanding.
  Verify exact purchased SKU/firmware and external-SIM2 behavior. EM919x Rev. 8
  is cached; use the source maps for exact pin and timing evidence.
- Amphenol MDT420B01411 is the selected 1 A/contact M.2 connector, but no exact
  stock/price was captured. Its current rating is a specified test condition,
  not proof of hot-enclosure capacity. A 0.5 A/contact substitute gives only
  2.5 A through Quectel's five power contacts and is not acceptable by default.
- Silver Ag59612-LPB is a Class 6/Type 3 candidate, not captured or finally
  selected. Its recommended continuous output is 48 W, whereas Class 6's
  51 W at the PD is before bridge/conversion losses. Typical efficiency is not
  a guaranteed budget bound. Qualify primary bridges, module thermal limits,
  class gating, isolation boundaries and output bulk. Do not claim a final
  PoE class before closing the board budget.
- CM4's quoted 1.4 A consumption is typical. Six Hirose 0.3 A power contacts
  give a conservative 1.8 A contact allocation, and external 3.3 V/1.8 V
  loads consume module-input power too. Close the actual guaranteed operating
  envelope and thermal/contact assumptions; an arbitrary low limit that
  causes brownouts is not a solution. Modem peaks include EM929x PC1.5 at
  5 A; source/profile/current-duration evidence must remain explicit.

Documentation/procurement access is an external dependency. Missing regulator
calculations, protection, controls, CAD and routing are unfinished engineering
work and must not be called external blockers.

## Cost and reproducibility

Captured partial auxiliary-input cost is $4.5268 per board at component
quantities for ten boards. Priced common modem/SIM capture is $1.8992, excluding
the unpriced M.2 socket; each fitted profile link adds $0.003. These are partial
captured totals, not complete carrier BOMs or JLC quotes. Regulator catalog
records are candidates only. Refresh availability at final selection and price
the module, modem, storage, all carrier parts, manual assembly, PCB and PCBA;
separate captured totals, allowances and actual quotes. No fabrication or
assembly quote has been obtained for a completed CM4 board.

Python is `full-adapter/.venv/bin/python`; KiCad CLI is
`/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli` (10.99 nightly).
Generators and assertions are in `cm4/tools/`; `check_core.py` invokes the
Ethernet, input-power and modem checks. Run from the repository root:

```sh
full-adapter/.venv/bin/python full-adapter/cm4/tools/check_core.py
```

Root staged hooks run `tools/check_nets.py` and `tools/check_netclasses.py`,
including `tools/check_current_design.py`; retain their staged-snapshot
validation and update explicit new-CAD registration as implementation grows.
The last CAD commit passed both hooks. Expected partial ERC counts are tracked
by the checker; they must shrink as integration is completed, not be waived.
`research/core-validation.json` is an earlier core milestone, not today's
complete validation report. Downloaded references and review exports live in
ignored `full-adapter/reference/cm4/` and `full-adapter/cm4/build/` respectively.
Their source manifests are tracked; ignored local copies are not a portable
release. Use the relevant KiCad skills before each capture/layout/export stage.
