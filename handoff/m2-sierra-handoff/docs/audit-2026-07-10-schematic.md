# Schematic Audit — EM9293 carrier (Netlist export 2026-07-10)

> **STATUS (re-review of export "(2)", 55 components, 2026-07-11):**
> **All 5 criticals RESOLVED** (C1–C5) — board no longer shorts on power-up and the modem's
> power-on / USB-sense / USB2 straps are correct. **HD3SS3220 majors M3 (ENn_CC→GND) and
> M4 (external Rd removed) RESOLVED.** Still open: **M1** (bulk caps — in progress),
> **M2** (double AC caps on USB3 RX — delete C3/C4), and 🟡 minor value bumps.

---

## LAYOUT PREP — SuperSpeed diff-pair polarity/swap plan (2026-07-13)

USB 3.x SS pairs support **automatic polarity inversion** (receiver corrects a swapped +/− at link
training — same as PCIe/SATA/DP). So to uncross a pair, **swap the net labels** (connect P to the
opposite-polarity pin) rather than crossing copper with a via (which hurts SI). Decide the final
polarity at routing — either way trains fine — but the defaults below are the likely-straight choice.

**Never swap:** `USB2_DP`/`USB2_DM` (USB2 has no polarity inversion) and any single-ended line
(`USB1_CC1/2`, etc.).

### Group 1 — Connector ↔ mux (4 pairs): leave as-is
HD3SS3220 RNH is laid out for flow-through; place the mux facing USB1 and these route straight.
Swap an individual pair only if it still crosses after placement.
| Pair | USB1 | Mux (U6) | Net |
|---|---|---|---|
| SSTX1 | A2/A3 | TX1p 17 / TX1n 16 | `SSTX1_P/N` |
| SSRX1 | B11/B10 | RX1p 15 / RX1n 14 | `SSRX1_P/N` |
| SSTX2 | B2/B3 | TX2p 21 / TX2n 20 | `SSTX2_P/N` |
| SSRX2 | A11/A10 | RX2p 19 / RX2n 18 | `SSRX2_P/N` |

### Group 2 — Mux ↔ M.2 (2 pairs): swap candidates (long cross-board runs)
Mux device side is P-then-N (6/7, 9/10); M.2 is N-then-P by pin (29/31, 35/37) → natural order
reversal, so **tentatively pre-swap both** (right column), then confirm at layout.
| Pair | Mux | M.2 | As-drawn | Swapped default |
|---|---|---|---|---|
| Module **TX** | RXp 9 / RXn 10 | 31 TXP / 29 TXM | 9→`USB3_TXP`, 10→`USB3_TXM` | **9→`USB3_TXM`(29), 10→`USB3_TXP`(31)** |
| Module **RX** | TXp 6 / TXn 7 →C20/C21 | 37 RXP / 35 RXM | 6→C20→`USB3_RXP`, 7→C21→`USB3_RXM` | **6→C20→`USB3_RXM`(35), 7→C21→`USB3_RXP`(37)** |

> Swapping the RX pair moves **C20/C21 with it** — each cap stays inline on its own polarity's line.
> To apply in EasyEDA: retype the net label on ONE end only (e.g. the mux pins), not both.

---

## RE-REVIEW 3 — export 2026-07-11 (58 components, full renumber + LCSC parts assigned)

Designators changed again: **U1**=AP2112K-3.3, **U2**=CH224K, **U3**=TPS565201, **U4**=AP2112K-1.8,
**U5**=TPD4EUSB30, **U6**=HD3SS3220. Verified against datasheets via 4 parallel agents
(TPS565201, AP2112K, CH224K, TPD4E05U06/TPD4EUSB30) + cap-vendor checks.

**🔴 Broken path — USB3 SuperSpeed RX disconnected.** The AC-coupling caps got orphaned in the
renumber: `SSRX_P_A`(U6.6)/`SSRX_N_A`(U6.7) dangle, `USB3_RXP/RXM`(CN1.37/35) reach only their ESD.
**Fix:** place **C20 between `SSRX_P_A`↔`USB3_RXP`** and **C21 between `SSRX_N_A`↔`USB3_RXM`** (220nF).
Board enumerates on USB2 without this, but gets NO SuperSpeed → defeats the throughput benchmark.

**🟠 Floating caps to wire.** **C16, C17 (10µF)** unwired → connect to `+3V3`/`GND`
(buck agent confirms total ceramic ≈64µF nominal / ~46µF derated is inside TI's 20–68µF D-CAP2 window).

**🟠 Wrong bulk-cap TYPE.** C12/C15 = **C2831775** is a 470µF **25V through-hole aluminum electrolytic**
(D8×12mm radial, ESR ~400mΩ) — NOT an SMD polymer. Issues: JLC PCBA is SMT-first (THT may not
auto-assemble), and 400mΩ ESR is poor for fast modem bursts. Switch to SMD polymer (e.g. **C2161524**
470µF 6.3V, ~9mΩ) or confirm JLC THT. **One 470µF is plenty — drop the second.**

**🟡 Minor.**
- **Delete C22 (10nF)** — floating; TPS565201 (D-CAP2) needs NO feedforward cap (DNP on TI EVM).
- **Add a local 1µF (X5R) at U4 VIN** (AP2112K-1.8, `+3V3`) if the U1 output cap isn't adjacent — good practice.
- **Input caps** 2×10µF/25V X5R 0603 derate to ~9µF effective at 12V (just under TI's ">10µF"); optional 3rd 10µF or a 22µF/25V.
- **R1 (1kΩ, CH224K VDD feed from VBUS_PD):** at 12V dissipates ~75mW on a 0603 (100mW rating) — consider 2kΩ to run cooler. Works as-is.
- **Inductor** 2.2µH: Isat margin only ~18% (Ipeak ≈5.1A vs 6A). OK for bench; watch heating (46mΩ DCR ≈0.74W).

**✅ Datasheet-verified PASS (this export):**
- Buck: Vref 0.760V + 33.2k/10k = TI's exact 3.3V divider; boot 100nF; 2×10µF+100nF input; 2×22µF output in-range; no feedforward; 500kHz.
- LDOs (AP2112K ×2): stable with 1µF ceramic in/out (the "10µF min" claim is a myth for this part); EN=VIN ok; 5V input within 6V max.
- CH224K: VDD is a **3.6V-max shunt reg** correctly fed via 1kΩ series from VBUS_PD (self-powered ✓); CFG1 24k→12V ✓; VBUS-sense 10k series ✓; 1µF decouple ✓; CFG2/3 + DP/DM floating ✓.
- Cap voltages: 10µF=25V (12V-rail OK), 22µF=10V (3.3V OK), 1µF/220nF/10nF=50V ✓.
- ESD arrays U5/D7: 4 ch on pins 1/2/4/5, GND 3/8, **pins 6/7/9/10 true NC** — wiring correct.
- All 15 resistors correct; TVS D5/D6 orientation correct; all 5 original criticals still holding; ENn_CC→GND & no external Rd still holding.

**Net:** one real broken path (USB3 RX), two caps to wire, one to delete, and a bulk-cap-type swap. No power-rail hazards.

---

Source: `Netlist_Schematic1_2026-07-10 (1).enet` (61 components). Checked every net's
membership, every R/C value, and all critical straps against the EM92XX PTS Rev 1
(Doc 41114313) and the part datasheets. Designators below are **your schematic's**
(U4 = 3.3 V LDO, U5 = 1.8 V LDO, U6 = TPD4EUSB30, CN1 = M.2, USB1 = data, USB2 = power).

Legend: 🔴 critical (won't work / self-damage) · 🟠 major (function/reliability) · 🟡 minor.
Resolution tags: ✅ RESOLVED · ⏳ OPEN.

---

## 🔴 CRITICAL — fix before ordering

### ✅ C1. D4 & D5 TVS diodes are reversed → dead short on both power rails  — RESOLVED (D4 K→VBUS_PD, D5 C→VBUS_DATA)
As netlisted, the **anode** sits on the live rail and the **cathode** on GND:
- D4 (SMAJ13A): pin2/A → `VBUS_PD`, pin1/K → `GND`
- D5 (SMAJ5.0A): pin2/A → `VBUS_DATA`, pin1/K → `GND`

A unidirectional TVS must sit **reverse-biased**: banded **cathode → the rail**, anode → GND.
As drawn each diode forward-conducts at ~0.7 V and shorts its rail the instant power is applied.
**Fix:** flip both — cathode(band) to `VBUS_PD`/`VBUS_DATA`, anode to `GND`.

### ✅ C2. CH224K nets split `_244` vs `_224` → PD sink dead  — RESOLVED (all merged to `_224`)
U1's own pins are labeled `*_244`; the passives around it are `*_224`. They never connect.
Rename the four **device-side** nets `_244 → _224`:
| Pin | Now | → |
|---|---|---|
| U1.1 VDD | `VDD_244` | `VDD_224` (joins R11 feed + R14) |
| U1.8 VBUS | `VBUS_SNS_244` | `VBUS_SNS_224` (joins R12) |
| U1.9 CFG1 | `CFG1_244` | `CFG1_224` (joins R13 = 24 k → 12 V) |
| U1.10 PG | `PG_244` | `PG_224` (joins R14) |

C18 is on the same VDD net, so it follows the rename. **Without this:** CH224K has no VDD
(R11's feed from VBUS_PD never reaches it), CFG1 floats (no 12 V request — stays 5 V),
VBUS-sense floats → no PD negotiation at all.

### ✅ C3. VBUS_SENSE (M.2 pin 22) mislabeled `VCC51_MUX` → USB never turns on  — RESOLVED (CN1.22 = VBUS_SENSE)
CN1.22 is on an orphan net `VCC51_MUX`; the real `VBUS_SENSE` net has only R20.
**Fix:** rename CN1.22 → `VBUS_SENSE`. PTS §3.3: *"The USB interface does not activate
until VBUS_SENSE is connected."*

### ✅ C4. Module USB 2.0 D+/D− not wired to the USB-C data port → no enumeration  — RESOLVED (CN1.7/9 = USB2_DP/DM)
CN1.7 = `USB_D+` and CN1.9 = `USB_D-` are orphan nets; the connector/ESD side uses
`USB2_DP`/`USB2_DM`. **Fix:**
- CN1.7 `USB_D+` → `USB2_DP` (joins D1, USB1.A6/B6)
- CN1.9 `USB_D-` → `USB2_DM` (joins D1, USB1.A7/B7)

USB 2.0 is the base enumeration path — the modem won't come up on SS alone.

### ✅ C5. Full_Card_Power_Off_N (pin 6) pulled to a floating net → module never powers on  — RESOLVED (R19 → +3V3)
R19 (100 k) ties CN1.6 to net `NET_PWR_ON`, which connects to nothing else.
**Fix:** rename R19's far pin `NET_PWR_ON` → `+3V3`. Then pin 6 —100 k— +3V3 = always-on
(PTS: 75–100 k to VCC rail ✓). This is the exact pin that left it dead in the 5G2PHY.

---

## 🟠 MAJOR — function / reliability

### ⏳ M1. No bulk capacitance anywhere — buck won't be stable, can't feed modem peaks  — OPEN (in progress)
Every cap is ≤ 470 nF (all 0603). A TPS565201 (≤4 A) and a modem drawing ~3 A peaks need real bulk:
- **Buck input** (`VBUS_PD`): C9/C10 = 100 nF → change to **≥10 µF each** (e.g. 2×10 µF 25 V + a 22 µF).
- **Buck output / `+3V3`**: C11/C12/C16 total ~540 nF → need **≥2×22 µF ceramic + the 470 µF polymer bulk**
  (BOM part C2161524). The polymer bulk is currently **absent entirely**.

These parts can't be 0603 — the 470 µF polymer and 22 µF need larger footprints. Biggest single gap.

### ⏳ M2. Double AC caps on module RX + mismatched values  — OPEN (delete C3/C4)
PTS §3.3.1: series caps go on the module **RX** pair only (none on TX) — one set.
You have two in series: C3(100 nF)/C4(220 nF) at the M.2 pins **and** C19/C20(220 nF) at the mux —
and C3≠C4 on the same pair. **Fix:** delete C3/C4; relabel CN1.35 → `USB3_RXM`, CN1.37 → `USB3_RXP`
(direct); keep C19/C20 (matched 220 nF) as the single AC cap. Module TX correctly has no caps ✓.

### ✅ M3. HD3SS3220 ENn_CC RC wired in series — CC controller not enabled  — RESOLVED (U2.29 → GND, R1/C2 removed)
Path is ENn_CC —R1— node —C2— GND, so nothing pulls ENn_CC low at DC (C2 blocks it).
Datasheet (pin 29): *"Enable signal for CC controller. Enable is active low."* Input, no internal
pull — it **must be driven/tied low** or the whole CC block (and mux) stays disabled.
**Fix:** tie U2.29 (ENn_CC) directly to `GND` (drop R1/C2).

### ✅ M4. External Rd on CC lines BREAKS attach detection — remove all four  — RESOLVED (R3/R4/R15/R16 removed)
CC1 = R3(5.1k)∥R15(5.1k) = 2.55 k; CC2 = R4∥R16 = 2.55 k. **This was upgraded from "verify" to
confirmed after reading HD3SS3220 datasheet (Rev E):**
> §7: *"HD3SS3220 constantly presents Rd (pull-down resistors) on both CC pins."*
> Electrical table `R(CC_D)` = 4.6 / **5.1** / 5.6 kΩ (UFP mode).

The chip already presents 5.1 k Rd internally and detects a DFP by measuring the CC voltage the
source's Rp current develops across it. Adding external 5.1 k halves Rd to 2.55 k: a default-current
source (80 µA) then develops only ~0.20 V, **below the chip's 0.25 V `V(UFP_CC_USB)` detect floor**
→ reads as unattached, mux never enables. **Fix:** delete R3, R4, R15, R16 entirely. The CC nets
then correctly = chip CC pin + connector CC pin + ESD only.
(The earlier netlist doc told you to add Rd — that was my error; corrected in the netlist doc §6.)

---

## 🟡 MINOR
- SIM VCC decoupling low: C5/C7 = 470 nF, C6/C8 = 10 nF (intended 4.7 µF + 0.1 µF). SIM current is tiny; bump if room.
- C13 (`VBUS_DATA`, feeds LDO + mux) = 100 nF → add a 1 µF.
- C14/C17 (`VCC33_MUX`) = 100 nF/10 nF → a 1 µF is nicer.

---

## ✅ Confirmed CORRECT
- All M.2 power/GND (8× +3V3, 11× GND) present.
- +1V8 → PCIE_DIS (pin 20) USB-select strap ✓ ; C15 decoupled.
- Both LDOs: U4 (VBUS_DATA→VCC33_MUX), U5 (+3V3→+1V8) ✓.
- SS mux mapping: SSTX1/2, SSRX1/2 ↔ mux ↔ module TX(29/31)/RX(35/37) ✓.
- Both LEDs correct polarity (LED1 cathode→WWAN_LED_N sink; LED2 cathode→GND).
- Both SIMs: VCC/RST/CLK/DATA/GND, ESD (D2/D3, D6/D7), data pull-ups (R6/R7) ✓; VPP NC ✓.
- Values right: FB divider 33.2k/10k → 3.28 V ✓; CFG1 24k → 12 V ✓; VBUS_DET 910 k ✓;
  buck EN 1 M ✓; pin-6 100 k ✓ (once net fixed); boot cap C1 100 nF ✓.

---

### Fix order (fastest path to a working board)
1. Flip D4, D5 (C1). ✅
2. Net renames — all one-click relabels: `_244→_224` ×4 (C2), CN1.22→VBUS_SENSE (C3),
   CN1.7/9→USB2_DP/DM (C4), R19 far end→+3V3 (C5), CN1.35/37→USB3_RXM/RXP + delete C3/C4 (M2). ✅ (M2 pending)
3. Tie ENn_CC→GND (M3); delete CC Rd R3/R4/R15/R16 (M4 — datasheet-confirmed, they break attach). ✅
4. Bulk caps (M1) — see cap-pass table below.

---

## Cap pass (M1 + M2) — install list

Verified LCSC parts (checked on LCSC 2026-07-11):
| Value | LCSC | Spec | Footprint |
|---|---|---|---|
| 10 µF | **C15850** | 25 V X5R | 0805 |
| 22 µF | **C45783** | 25 V X5R | 0805 |
| 470 µF | **C2161524** | 6.3 V polymer (3.3 V rail only!) | D8 can (Ø8 mm) |
| 1 µF | **C29936** | 25 V X7R | 0603 |
| 100 nF | **C307331** | 50 V X7R | 0603 |
| 4.7 µF | **C19666** | 16 V X5R (3.3 V/SIM only) | 0603 |

> 25 V 0805 X5R loses ~half its value under 12 V DC bias — that's why the input uses 2×10 µF, not 1.

**Step 0 — M2, delete the double AC caps.** Delete **C3, C4**; relabel **CN1.35 → `USB3_RXM`**,
**CN1.37 → `USB3_RXP`**. Keeps C19/C20 (220 nF) as the single AC-coupling pair. TX stays uncoupled ✓.

**Step 1 — buck INPUT (`VBUS_PD`).** C10 100 nF → **10 µF (C15850)**; ADD **C21 = 10 µF (C15850)**.
Keep C9 = 100 nF (HF). Result: 2×10 µF + 100 nF.

**Step 2 — buck OUTPUT at U3 (`+3V3`).** C11 220 nF → **22 µF (C45783)**; C12 220 nF → **22 µF (C45783)**.
Keep C16 = 100 nF (HF).

**Step 3 — module VCC bulk at M.2 (`+3V3`).** ADD **C22 = 470 µF (C2161524)** near CN1;
ADD **C23, C24 = 10 µF (C15850)** spread across the 8 VCC pins; ADD **C25, C26 = 100 nF (C307331)** at VCC cluster.

**Step 4 — LDO stability (REQUIRED, not optional).**
- C13 100 nF → **1 µF (C29936)** — U4 input (`VBUS_DATA`).
- C14 100 nF → **1 µF (C29936)** — U4 output (`VCC33_MUX`). AP2112K needs ≥1 µF out.
- C15 100 nF → **1 µF (C29936)** — U5 output (`+1V8`). Same.
- C17 (10 nF, `VCC33_MUX`): leave or → 100 nF.

**Step 5 — minor (optional).** C18 100 nF → 1 µF (CH224K VDD); SIM C5/C7 → 1 µF, C6/C8 → 100 nF.

**Step 6 — before ordering.** Every generic `CAP_0603`/`Res_0603` still has NO LCSC part assigned —
assign real parts (100 nF→C307331, 1 µF→C29936, etc.) or JLC PCBA will flag them.

Optional stability aid: if the 3.3 V rail rings on load steps, add a 47 pF feedforward cap across R8 (FB top).
