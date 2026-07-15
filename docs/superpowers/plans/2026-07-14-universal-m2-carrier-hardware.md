# Universal 5G M.2 Carrier — Hardware Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Produce an orderable KiCad 10 design (schematic, 4-layer PCB, JLC fab outputs) of the universal Sierra/Quectel M.2 carrier per `docs/superpowers/specs/2026-07-14-universal-m2-carrier-design.md`.

**Architecture:** Hierarchical KiCad schematic (one sheet per subsystem) captured against a test-first netlist checker; then 4-layer layout with per-class impedance rules; then kicad-cli fab outputs split into JLC-assembled vs hand-soldered BOM lines.

**Tech Stack:** KiCad 10 (`/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli`), Python via `uv` for the net checker, git (local commits only — never push).

## Global Constraints

- Spec is the source of truth: `docs/superpowers/specs/2026-07-14-universal-m2-carrier-design.md`. On conflict, stop and flag — don't improvise.
- **Module-safety rules (never violate):** M.2 pin 20 must never be able to exceed 2.10 V (pull-up to +1V8 only, open-drain FET only). Pin 22 is fed ONLY by the VBUS_DATA divider (~1.75 V) or the Q5 force-FET from +1V8 — never direct 5 V. M.2 VCC = pins 2/4/70/72/74 only; pins 24/38/68 connect to +3V3 only through default-open solder jumpers JP1/JP2/JP3.
- Blank-MCU default = Sierra forced-USB: every strap/select passive default must hold without firmware (pin 6 high, pin 20 high@1.8 V, USB2 mux→data port, SIM mux→physical slot 2, LED rail on).
- Hand-solder rules: 0603 minimum passives; leaded packages preferred where a choice exists; exposed-pad parts that are hand-soldered get via-stitched thermal pads.
- JLC-assembled BOM lines must carry an LCSC part number property; hand-soldered lines may be any distributor.
- Python only via `uv run` (never raw python/pip).
- Commit locally at the end of every task; never push.
- `kicad-cli` alias used below: `KCLI="/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli"`.
- ERC gate = 0 errors. Warnings are allowed only if logged with justification in `docs/erc-waivers.md`.

## File Structure

```
sierra-to-usb.kicad_pro / .kicad_pcb            # existing project (root)
sierra-to-usb.kicad_sch                          # root sheet: hierarchy + title block only
sheets/power_input.kicad_sch                     # CH224K PD, PoE PD+flyback, OR → +12V
sheets/power_rails.kicad_sch                     # buck, LDOs, INA226 ×2, ADC dividers
sheets/m2.kicad_sch                              # M.2 socket, VCC/jumpers, bulk, straps+FETs
sheets/usb3_data.kicad_sch                       # J1, HD3SS3220, SS ESD, 220nF caps
sheets/usb2_debug.kicad_sch                      # TS3USB221 USB2 mux, J3 debug port, ESD
sheets/mcu.kicad_sch                             # RP2040, flash, xtal, SWD, DIP, RGB, LED-kill, temps, Qwiic, fan
sheets/ethernet.kicad_sch                        # RTL8125BG, magjack, EEPROM, 25MHz
sheets/sim.kicad_sch                             # SIM1, SIM2, eSIM, TS3A27518E, SIM ESD
sheets/rf.kicad_sch                              # 5× MHF4 → SMA
tools/check_nets.py                              # netlist assertion checker (test harness)
tools/netchecks.txt                              # accumulated pin→net assertions
docs/sourcing.md                                 # Task 1 output: pinned part numbers
docs/verification.md                             # Task 2 output: spec §13 closeout
docs/erc-waivers.md                              # justified ERC warnings
docs/ordering.md                                 # Task 20 output: JLC order checklist
```

**Reference designator map (use exactly these):** CN1 M.2 socket · J1 USB-C data · J2 USB-C PD · J3 USB-C debug · J4 RJ45 magjack · J5–J9 MHF4 (ANT0,ANT1,ANT2,ANT3,GNSS) · J10–J14 SMA (same order) · J15 Qwiic · J16 SWD · J17 fan · J18 spare GPIO · SIM1/SIM2 nano-SIM · U1 HD3SS3220 · U2 CH224K · U3 TPS565201 · U4 AP2112K-3.3 (U1 local) · U5 AP2112K-1.8 · U6 RP2040 · U7 W25Q128JVS · U8 TS3USB221 · U9 RTL8125BG · U10 TPS23730 (or Task-1 substitute) · U11 TS3A27518E · U12 eSIM MFF2 · U13 INA226 (12V) · U14 INA226 (3V3 module feed) · U15/U16 TMP112 · U17 AP2112K-3.3 (MCU) · U18 SK6805 RGB · U19 ideal-diode OR (Task-1 pick) · Q1 pin6-FET · Q2 pin20-FET · Q3 pin8-FET · Q4 pin67-FET · Q5 VBUS_SENSE-force-FET · Q6 LED-kill FET · Q7 fan FET (all 2N7002) · D1/D2 TPD4EUSB30 (connector side) · D3 TPD4EUSB30 (module side) · D4 TPD4E05U06 (J1 CC+D±) · D5 TPD4E05U06 (J3) · D6 SMAJ13A · D7 SMAJ58A · BR1/BR2 PoE bridges · D10/D11 TPD4S009 (SIM) · Y1 12 MHz · Y2 25 MHz · SW1 DIP-4 · SW2 LED slide · SW3 BOOTSEL · SW4 RESET · JP1/JP2/JP3 solder jumpers (M.2 pins 24/38/68 → +3V3) · T1 PoE transformer (Würth 750313355, EVM-093) · TP* test points.

**Net naming (use exactly these):** rails `VBUS_PD, VBUS_DATA, VBUS_DBG, +12V, +12V_POE, +3V3, +3V3_MUX, +3V3_MCU, +1V8, +3V3_MOD` (post-INA226 module feed) · straps `FCPO_N, PCIE_DIS, VBUS_SENSE, W_DISABLE1_N, MODEM_RESET_N` · senses `WWAN_LED_N, WAKE_N` · USB3 connector side `SS_CON_TX1_P/N, SS_CON_TX2_P/N, SS_CON_RX1_P/N, SS_CON_RX2_P/N` · mux↔module `SS_MOD_TX_P/N` (mux out, pre-cap), `SS_MOD_TX_C_P/N` (post-cap → CN1 35/37), `SS_MOD_RX_P/N` (CN1 29/31 → mux) · USB2 `USB2_CON_DP/DM` (J1→D4→U8), `USB2_MOD_DP/DM` (U8→CN1 7/9), `USB2_MCU_DP/DM` (U8→U6 PIO-USB) · debug `USB_DBG_DP/DM` · PCIe `PCIE_MTX_P/N` (CN1 41/43, pre-cap), `PCIE_MTX_C_P/N` (post-cap → U9 RX), `PCIE_MRX_P/N` (CN1 47/49), `PCIE_MRX_C_P/N` (U9 TX pre-cap side), `PCIE_REFCLK_P/N, PERST_N, CLKREQ_N, PEWAKE_N` · MDI `MDI0_P/N … MDI3_P/N` · SIM `UIM1_VDD/RST/CLK/IO/DET`, `UIM2_VDD/RST/CLK/IO/DET` (CN1 side), `UIM2S_*` (physical SIM2 branch), `UIM2E_*` (eSIM branch) · control `I2C_SDA, I2C_SCL, MUX_USB2_SEL, SIM_SEL, RTL_RST_N, LED_EN, DIP0–DIP3, RGB_DI, FAN_PWM` · ADC `VMON_12V, VMON_3V3, VMON_1V8` · PoE primary `POE_VA+, POE_VA-, POE_VB+, POE_VB-, POE_VDD54, POE_RTN` (isolated domain).

---

### Task 0: Net-check test harness

**Files:**
- Create: `tools/check_nets.py`, `tools/netchecks.txt`
- Test: the script self-tests against the current (nearly empty) schematic

**Interfaces:**
- Produces: `uv run tools/check_nets.py` — exits 0 iff every assertion in `tools/netchecks.txt` holds against a fresh netlist export. Assertion syntax (one per line, `#` comments):
  - `CN1.20 = PCIE_DIS` (component pin *number* on net)
  - `U2.pinfn:CFG1 = CH224K_CFG1` (match by pin *function name* from the symbol)
  - `NET PCIE_DIS PINS>=3` (net exists with minimum pin count)

- [ ] **Step 1: Write the checker (this is the failing-test infrastructure for every later task)**

```python
#!/usr/bin/env python3
"""Assert pin->net connectivity against a KiCad netlist export.

Usage: uv run tools/check_nets.py [--sch sierra-to-usb.kicad_sch] [--checks tools/netchecks.txt]
Exit 0 = all assertions pass. Prints each failure.
"""
import argparse, re, subprocess, sys, tempfile, xml.etree.ElementTree as ET
from pathlib import Path

KCLI = "/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli"

def export_netlist(sch: Path) -> ET.Element:
    with tempfile.NamedTemporaryFile(suffix=".xml", delete=False) as f:
        out = Path(f.name)
    subprocess.run([KCLI, "sch", "export", "netlist", "--format", "kicadxml",
                    "-o", str(out), str(sch)], check=True, capture_output=True)
    return ET.parse(out).getroot()

def build_index(root: ET.Element):
    """pin_by_num[(ref, pinnum)] -> net ; pin_by_fn[(ref, pinfunction)] -> set(nets) ; net_pins[net] -> count"""
    by_num, by_fn, net_pins = {}, {}, {}
    for net in root.iter("net"):
        # hierarchical nets export as "/sheet_path/NAME" — match on the leaf name
        name = net.get("name").split("/")[-1]
        for node in net.iter("node"):
            ref, pin = node.get("ref"), node.get("pin")
            by_num[(ref, pin)] = name
            fn = node.get("pinfunction")
            if fn:
                by_fn.setdefault((ref, fn.upper()), set()).add(name)
            net_pins[name] = net_pins.get(name, 0) + 1
    return by_num, by_fn, net_pins

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sch", default="sierra-to-usb.kicad_sch")
    ap.add_argument("--checks", default="tools/netchecks.txt")
    args = ap.parse_args()
    by_num, by_fn, net_pins = build_index(export_netlist(Path(args.sch)))
    failures = 0
    for lineno, raw in enumerate(Path(args.checks).read_text().splitlines(), 1):
        line = raw.split("#")[0].strip()
        if not line:
            continue
        m = re.fullmatch(r"NET\s+(\S+)\s+PINS>=(\d+)", line)
        if m:
            net, need = m.group(1), int(m.group(2))
            if net_pins.get(net, 0) < need:
                print(f"FAIL L{lineno}: net {net} has {net_pins.get(net,0)} pins, need >={need}")
                failures += 1
            continue
        m = re.fullmatch(r"(\S+?)\.(pinfn:)?(\S+)\s*=\s*(\S+)", line)
        if not m:
            print(f"FAIL L{lineno}: unparseable: {raw}")
            failures += 1
            continue
        ref, isfn, pin, want = m.group(1), m.group(2), m.group(3), m.group(4)
        if isfn:
            got = by_fn.get((ref, pin.upper()), set())
            ok = want in got
            gotstr = ",".join(sorted(got)) or "<unconnected>"
        else:
            gotnet = by_num.get((ref, pin))
            ok = gotnet == want
            gotstr = gotnet or "<unconnected>"
        if not ok:
            print(f"FAIL L{lineno}: {ref}.{pin} on '{gotstr}', want '{want}'")
            failures += 1
    print(f"{failures} failure(s)" if failures else "all checks pass")
    sys.exit(1 if failures else 0)

if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Seed `tools/netchecks.txt` with one assertion the current schematic already satisfies and one it doesn't** — the existing sch has a `Connector:USB_C_Receptacle` and `Interface_USB:CH224K`; write `NET GND PINS>=2` (should pass) and `CN1.20 = PCIE_DIS` (should fail).
- [ ] **Step 3: Run `uv run tools/check_nets.py`** — Expected: exactly `FAIL ...: CN1.20 ...` then `1 failure(s)`, exit 1. (Proves both the pass and fail paths.)
- [ ] **Step 4: Delete the deliberately-failing line, rerun** — Expected: `all checks pass`, exit 0.
- [ ] **Step 5: Commit** — `git add tools/ && git commit -m "tooling: netlist assertion checker"`

### Task 1: Sourcing verification (gate parts)

**Files:**
- Create: `docs/sourcing.md`

**Interfaces:**
- Produces: pinned MPN + distributor + stock count + unit price for every row below; a **decision** for the two open part choices (PoE controller; ideal-diode OR). Later tasks consume these MPNs for symbol/footprint selection and BOM fields.

- [ ] **Step 1:** Search LCSC (JLC-assembled parts MUST be LCSC): RP2040, W25Q128JVSIQ, RTL8125BG(-CG), HD3SS3220RNHR, TS3USB221 (DRC/RSE pkg), TS3A27518E (or TSSOP alternative TS3A27518EPWR), MFF2 eUICC (ST4SIM-200M or equal), MHF4 SMT receptacle, JST-SH-4 (Qwiic), M.2 Key-B 75-pin socket H=4.2 + standoff. Record stock/price in a table in `docs/sourcing.md`.
- [ ] **Step 2:** Search any distributor (hand-soldered): 2.5G+PoE magjack (start: LINK-PP LP-designated 2.5G ICMs with bt-rated CTs), PoE flyback transformer for TPS23730 (start: Würth 750318131-class per TI EVM; else Coilcraft/UMEC), CH224K, TPS565201, TPS23730, AP2112K-3.3/-1.8, INA226, TMP112, SK6805-EC15 (3V3-logic RGB), TPD4EUSB30, TPD4E05U06, TPD4S009, SMAJ13A/SMAJ58A, MB10S bridges, 2N7002, USB-C receptacles (hand-solderable, e.g., HRO TYPE-C-31-M-12 class), nano-SIM push-push, SMA edge jacks, DIP-4, slide switch, 470 µF 6.3 V polymer, 2.2 µH ≥5.6 A Isat inductor, ideal-diode OR (candidates: LM5050-1 + FET ×2, or dual SM74611-class; must pass 12 V/3 A).
- [ ] **Step 3:** **Decisions recorded in docs/sourcing.md:** (a) TPS23730 vs TPS2373-4+separate controller — pick by transformer availability; (b) ideal-diode OR implementation. If the 2.5G+PoE magjack is unobtainable, STOP and flag (fallback = separate 2.5G transformer + PoE-tap RJ45, needs user sign-off).
- [ ] **Step 4:** Commit — `git add docs/sourcing.md && git commit -m "docs: pinned sourcing for gate parts + decisions"`

### Task 2: Datasheet verification closeout (spec §13)

**Files:**
- Create: `docs/verification.md`

**Interfaces:**
- Produces: closed/blocked status for spec §13 items 1–8 with citations (doc, rev, table/figure). Tasks 4–12 consume the confirmed pin facts.

- [ ] **Step 1:** Ask the user to drop the EM92XX PTS PDF (Doc 41114313) into `docs/datasheets/`. Verify from it: USB3 caps on 35/37 only (§3.3.1 figure), pin-22 VIH range, pins 23/26/67 definitions, VCC pin list. Record in `docs/verification.md`. If the user can't locate it, mark item BLOCKED and proceed (EM919x facts already verified stand for the family; flag residual risk).
- [ ] **Step 2:** Fetch Quectel RM520N HW design (already at `~/.claude/.../tool-results/rm520n.txt` from brainstorming; re-fetch if absent) — record: PCIe AC-cap ownership/values from the RC-mode reference circuit; REFCLK/PERST# connection diagram. Also RM551E hardware design (Quectel site/search) — spot-check pins 6/8/20/22/24/38/68 match RM520N assumptions.
- [ ] **Step 3:** HD3SS3220 datasheet (TI): confirm standalone-UFP strap set used in spec §5 (PORT=GND, VBUS_DET 900 k, ENn_MUX=GND, ADDR=NC) and SS pin mapping for the mux net table in Task 7. TPS23730 datasheet: confirm 802.3at Class-4 resistor set for Task 4.
- [ ] **Step 4:** Commit — `git add docs/verification.md docs/datasheets && git commit -m "docs: close out spec §13 datasheet verifications"`

### Task 3: Root sheet + hierarchy + net classes

**Files:**
- Modify: `sierra-to-usb.kicad_sch` (strip the placeholder parts already there — they'll be re-captured properly in their sheets), `sierra-to-usb.kicad_pro`
- Create: all 9 empty `sheets/*.kicad_sch`, `docs/erc-waivers.md` (empty table)

- [ ] **Step 1:** In the root schematic delete the existing loose symbols (M.2, USB-Cs, CH224K, R/C/TVS — they predate the spec). Create the 9 hierarchical sheet instances named exactly as File Structure lists.
- [ ] **Step 2:** In `sierra-to-usb.kicad_pro` define net classes (used later by layout; declared now so nets inherit on capture): `DIFF_USB_90` (SS_*, USB2_*, USB_DBG_*), `DIFF_PCIE_85` (PCIE_M*, PCIE_REFCLK*), `DIFF_MDI_100` (MDI*), `RF_50` (ANT*, GNSS), `POE_PRI` (POE_*), `POWER` (+12V*, VBUS_*, +3V3*, +1V8).
- [ ] **Step 3:** `$KCLI sch erc sierra-to-usb.kicad_sch -o /tmp/erc.rpt; cat /tmp/erc.rpt` — Expected: 0 errors (empty sheets are fine).
- [ ] **Step 4:** Commit — `git add -A && git commit -m "sch: hierarchy scaffold + net classes"`

### Task 4: Sheet power_input (PD + PoE + OR)

**Files:**
- Modify: `sheets/power_input.kicad_sch`, append `tools/netchecks.txt`

**Interfaces:**
- Produces nets: `+12V` (ORed output), `VBUS_PD`, `POE_*` primary domain, `CH224K_PG` (open-drain status → LED sheet/mcu), `POE_STATUS`.
- Consumes: J4 magjack center-tap pins live on the ethernet sheet — CTs exported as hierarchical labels `POE_VA+/-, POE_VB+/-` here, wired to J4 in Task 10.

- [ ] **Step 1: Add failing checks** (append to `tools/netchecks.txt`):

```
# power_input
J2.pinfn:VBUS = VBUS_PD
U2.pinfn:CFG1 = CH224K_CFG1
D6.1 = VBUS_PD
BR1.pinfn:+ = POE_VDD54
U10.pinfn:VDD = POE_VDD54
U19.pinfn:OUT = +12V
NET +12V PINS>=3
NET POE_RTN PINS>=4
```

- [ ] **Step 2:** `uv run tools/check_nets.py` — Expected: FAIL on every new line.
- [ ] **Step 3: Wire the sheet** per this table (CH224K per its datasheet application circuit as already redone by the user; TPS23730 copied verbatim from TI EVM-093 (active-clamp forward + opto, Würth 750313355) per 2026-07-14 user decision — supersedes 'no-opto flyback'; resistor values from Task 2 step 3):

| Block | Connections |
|---|---|
| J2 (PD port) | VBUS→`VBUS_PD`; CC1/CC2→U2 CC1/CC2; D±/SS = NC flags; shield→GND via 1 MΩ‖1 nF |
| U2 CH224K | VDD←`VBUS_PD` via 1 kΩ + 1 µF; VBUS-sense per datasheet; CFG1→24 kΩ→GND (`CH224K_CFG1`, 12 V request); PG→`CH224K_PG` (open-drain, 10 k pull to +3V3) |
| D6 SMAJ13A | `VBUS_PD`→GND |
| PoE front | `POE_VA±`,`POE_VB±` → BR1/BR2 → `POE_VDD54`/`POE_RTN`; D7 SMAJ58A across; 25.5 kΩ detection + Class-4 classification RCLSA=RCLSB=32 Ω (TPS23730 DS Table 8-1 — deliberate deviation from EVM-093's Class-6 values) |
| U10+T1 flyback | primary on `POE_VDD54/POE_RTN` (isolated domain), secondary → `+12V_POE`/GND per datasheet typical application (no-opto FB) |
| U19 ideal-diode OR | inputs `VBUS_PD` and `+12V_POE` → output `+12V` |

- [ ] **Step 4:** `uv run tools/check_nets.py` — Expected: `all checks pass`. Then ERC → 0 errors (waive+log "isolated POE_RTN not connected to GND" if flagged).
- [ ] **Step 5:** Commit — `git add -A && git commit -m "sch: power input (CH224K PD + 802.3at PoE flyback + 12V OR)"`

### Task 5: Sheet power_rails (buck, LDOs, INA226, monitors)

**Files:**
- Modify: `sheets/power_rails.kicad_sch`, append `tools/netchecks.txt`

**Interfaces:**
- Produces: `+3V3` (system), `+3V3_MOD` (post-U14 module feed), `+1V8`, `+3V3_MCU`, `VMON_12V/3V3/1V8`, I2C addresses: U13=0x40, U14=0x41 (A0/A1 strapping shown below).

- [ ] **Step 1: Add failing checks:**

```
# power_rails
U3.pinfn:VIN = +12V
U3.pinfn:EN = BUCK_EN
U13.pinfn:IN+ = +12V
U5.pinfn:VOUT = +1V8
U14.pinfn:IN+ = +3V3
U14.pinfn:IN- = +3V3_MOD
U17.pinfn:VOUT = +3V3_MCU
NET VMON_12V PINS>=2
```

- [ ] **Step 2:** Run checker — Expected: FAIL on all new lines.
- [ ] **Step 3: Wire:** U13 INA226 shunt (2 mΩ) in series on `+12V` **before** U3. U3 TPS565201 per datasheet: FB divider 33.2 k/10 k → 3.28 V, L=2.2 µH (Task-1 ≥5.6 A part), Cin 2×10 µF/25 V, Cout 2×22 µF; `BUCK_EN` ← 1 MΩ from `+12V` + 100 k to GND (starts ≥~8 V). U14 INA226 (2 mΩ) between `+3V3` and `+3V3_MOD`. U5 AP2112K-1.8 from `+3V3`. U17 AP2112K-3.3 from Schottky-OR (2× B5819W) of `VBUS_DBG` and `+3V3` → `+3V3_MCU`. ADC dividers: `+12V`→100 k/10 k→`VMON_12V`; `+3V3`→100 k/100 k→`VMON_3V3`; `+1V8`→100 k/100 k→`VMON_1V8`. INA226 A0/A1: U13 GND/GND (0x40), U14 VS/GND (0x41); both on `I2C_SDA/SCL`.
- [ ] **Step 4:** Checker passes; ERC 0 errors.
- [ ] **Step 5:** Commit — `git add -A && git commit -m "sch: power rails (buck + LDOs + INA226 telemetry + ADC dividers)"`

### Task 6: Sheet m2 (socket, VCC policy, straps)

**Files:**
- Modify: `sheets/m2.kicad_sch`, append `tools/netchecks.txt`

**Interfaces:**
- Produces: every CN1 pin net per the table below; strap control inputs `FCPO_CTL, PCIE_DIS_CTL, WDIS_CTL, MRST_CTL, VBUSSNS_CTL` (FET gates, consumed by mcu sheet); senses `WWAN_LED_N, WAKE_N`.

- [ ] **Step 1: Add failing checks** (safety-critical subset — full table wired in step 3):

```
# m2 — module-safety assertions (Global Constraints)
CN1.2 = +3V3_MOD
CN1.4 = +3V3_MOD
CN1.70 = +3V3_MOD
CN1.72 = +3V3_MOD
CN1.74 = +3V3_MOD
CN1.24 = M2_VCC_JP1     # jumpered, NOT +3V3_MOD directly
CN1.38 = M2_VCC_JP2
CN1.68 = M2_VCC_JP3
CN1.6 = FCPO_N
CN1.20 = PCIE_DIS
CN1.22 = VBUS_SENSE
CN1.8 = W_DISABLE1_N
CN1.67 = MODEM_RESET_N
CN1.10 = WWAN_LED_N
CN1.23 = WAKE_N
NET PCIE_DIS PINS>=3
Q2.pinfn:D = PCIE_DIS
```

- [ ] **Step 2:** Run checker — FAIL on all.
- [ ] **Step 3: Wire CN1** (`Connector:Bus_M.2_Socket_B` or Task-1 vendor symbol): GND pins 3/5/11/27/33/39/45/51/57/71/73 → GND. VCC per checks (JP1–3 solder jumpers to `+3V3_MOD`). Bulk at socket: 3×470 µF poly (≈1.5 mF per EM92xx r7.2) + 6×10 µF + 0.1 µF per VCC pin. Straps: `FCPO_N` 100 k→+3V3, Q1 drain, gate=`FCPO_CTL` 100 k pulldown; `PCIE_DIS` 10 k→**+1V8**, Q2, gate=`PCIE_DIS_CTL`; `W_DISABLE1_N` 10 k→+1V8, Q3, `WDIS_CTL`; `MODEM_RESET_N` 10 k→+1V8, Q4, `MRST_CTL`; `VBUS_SENSE` ← divider `VBUS_DATA`→33 k→node→18 k→GND (≈1.76 V) plus Q5 as high-side pull from +1V8 via 1 k (gate `VBUSSNS_CTL`); `WWAN_LED_N` → LED(+3V3, 1 k, on LED_EN rail) and to mcu sense; `WAKE_N` 100 k→+1V8, to mcu. USB3/USB2/PCIe/UIM pins get hierarchical labels only (wired by sheets 7/8/10/11). SS net names are host-perspective per the Global net table (`SS_MOD_RX_*` = what the host/mux receives = CN1 29/31 module TX; `SS_MOD_TX_C_*` = post-cap host TX into module RX = CN1 35/37): CN1.29=`SS_MOD_RX_N`, CN1.31=`SS_MOD_RX_P`, CN1.35=`SS_MOD_TX_C_N`, CN1.37=`SS_MOD_TX_C_P`, CN1.7=`USB2_MOD_DP`, CN1.9=`USB2_MOD_DM`, CN1.41=`PCIE_MTX_N`, CN1.43=`PCIE_MTX_P`, CN1.47=`PCIE_MRX_N`, CN1.49=`PCIE_MRX_P`, CN1.53=`PCIE_REFCLK_N`, CN1.55=`PCIE_REFCLK_P`, CN1.50=`PERST_N` (10 k→+1V8), CN1.52=`CLKREQ_N` (10 k→+1V8), CN1.54=`PEWAKE_N` (10 k→+1V8), UIM1: 30=`UIM1_RST`,32=`UIM1_CLK`,34=`UIM1_IO`,36=`UIM1_VDD`,66=`UIM1_DET`; UIM2: 40=`UIM2_DET`,42=`UIM2_IO`,44=`UIM2_CLK`,46=`UIM2_RST`,48=`UIM2_VDD`. CONFIG 1/21/69/75 + remaining reserved pins → NC flags. Test points on all straps.
- [ ] **Step 4:** Add these checks too, rerun until pass:

```
CN1.29 = SS_MOD_RX_N
CN1.31 = SS_MOD_RX_P
CN1.35 = SS_MOD_TX_C_N
CN1.37 = SS_MOD_TX_C_P
CN1.41 = PCIE_MTX_N
CN1.55 = PCIE_REFCLK_P
CN1.48 = UIM2_VDD
```

- [ ] **Step 5:** ERC 0 errors; Commit — `git add -A && git commit -m "sch: M.2 socket, vendor-safe VCC policy, strap plane"`

### Task 7: Sheet usb3_data (J1 + HD3SS3220 + caps + ESD)

**Files:**
- Modify: `sheets/usb3_data.kicad_sch`, append `tools/netchecks.txt`

**Interfaces:**
- Consumes: `SS_MOD_RX_P/N`, `SS_MOD_TX_C_P/N`, `USB2_CON_DP/DM` (to usb2_debug), `VBUS_DATA`.
- Produces: fully wired data port; `VBUS_DATA` rail.

- [ ] **Step 1: Failing checks:**

```
# usb3_data — cap placement is THE verified-twice item: caps feed 35/37 ONLY
NET SS_MOD_TX_C_P PINS>=2      # post-cap net exists (C→CN1.37)
NET SS_MOD_RX_P PINS>=2        # module TX to mux — NO caps: net goes straight D3→U1
J1.pinfn:VBUS = VBUS_DATA
U1.pinfn:VBUS_DET = HD_VBUSDET
U4.pinfn:VOUT = +3V3_MUX
```

- [ ] **Step 2:** Run — FAIL.
- [ ] **Step 3: Wire:** J1 SSTX1/SSRX1/SSTX2/SSRX2 → D1/D2 (flow-through) → U1 connector-side per HD3SS3220 datasheet mapping (Task 2 step 3). U1 module side (CORRECTED 2026-07-14 — HD3SS3220 TX/RX pins are named from the LOCAL controller's perspective = the module, per SLLSES1E Fig 7-3): U1 RXp/RXn (9/10) → 220 nF ×2 → `SS_MOD_TX_C_P/N` (→CN1 35/37, via module-side ESD flow-through); U1 TXp/TXn (6/7) ← `SS_MOD_RX_P/N` (CN1 29/31, via ESD, **no caps**). Original text had the roles swapped — link-dead both directions. U1 straps: PORT=GND, ENn_MUX=GND, ADDR=NC, VBUS_DET←`VBUS_DATA` via 900 kΩ (`HD_VBUSDET`), VDD5←`VBUS_DATA`, VCC33←`+3V3_MUX` from U4 (input `VBUS_DATA`). J1 D± both rows → D4 → `USB2_CON_DP/DM` hierarchical labels; CC1/CC2 → U1 CC pins through D4 channels. J1 VBUS → `VBUS_DATA`; SMAJ5.0A across it (add refdes D8 — update refdes map comment inline).
- [ ] **Step 4:** Checker passes; ERC 0; Commit `git add -A && git commit -m "sch: USB3 data port + HD3SS3220 + correct 35/37 AC caps"`

### Task 8: Sheet usb2_debug (TS3USB221 mux + debug port)

**Files:**
- Modify: `sheets/usb2_debug.kicad_sch`, append `tools/netchecks.txt`

**Interfaces:**
- Consumes: `USB2_CON_DP/DM`, `USB2_MOD_DP/DM` (CN1 7/9), `USB2_MCU_DP/DM` (mcu sheet), `MUX_USB2_SEL`.

- [ ] **Step 1: Failing checks:**

```
# usb2_debug
U8.pinfn:D+ = USB2_MOD_DP
U8.pinfn:S = MUX_USB2_SEL
J3.pinfn:VBUS = VBUS_DBG
NET USB_DBG_DP PINS>=2
NET MUX_USB2_SEL PINS>=3
```

- [ ] **Step 2:** Run — FAIL.
- [ ] **Step 3: Wire:** U8 common D± → `USB2_MOD_DP/DM`; port A (default) → `USB2_CON_DP/DM`; port B → `USB2_MCU_DP/DM`; SEL=`MUX_USB2_SEL` with 100 k pulldown selecting A (blank-MCU default = data port; verify A/low polarity against TS3USB221 datasheet — if A=high, pull up instead and note in sheet). U8 VCC=+3V3. J3: VBUS→`VBUS_DBG`, D±→D5→`USB_DBG_DP/DM`, CC1/CC2→5.1 kΩ→GND each, SS pins NC.
- [ ] **Step 4:** Pass; ERC 0; Commit `git add -A && git commit -m "sch: USB2 mux + debug port"`

### Task 9: Sheet mcu (RP2040 core + control plane)

**Files:**
- Modify: `sheets/mcu.kicad_sch`, append `tools/netchecks.txt`

**Interfaces:**
- Consumes every `*_CTL`, sense, `MUX_USB2_SEL`, `SIM_SEL`, `RTL_RST_N`, `I2C_*`, `VMON_*`, `USB2_MCU_DP/DM`, `USB_DBG_DP/DM`, `LED_EN`.
- Produces: the committed GPIO map below (firmware plan consumes it verbatim).

**GPIO map (spec §7.2, 26/30):** GP0/1 I2C_SDA/SCL · GP2/3 PIO-USB `USB2_MCU_DP/DM` (adjacent, required by pico-pio-usb) · GP4 FCPO_CTL · GP5 PCIE_DIS_CTL · GP6 WDIS_CTL · GP7 MRST_CTL · GP8 VBUSSNS_CTL · GP9 LED_EN_CTL · GP10 MUX_USB2_SEL · GP11 SIM_SEL · GP12 RTL_RST_N · GP13 UIM2_DET_CTL · GP14 RGB_DI · GP15 FAN_PWM · GP16 WWAN_LED_N (in) · GP17 WAKE_N (in) · GP18 PERST_N (in) · GP19 CLKREQ_N (in) · GP20–23 DIP0–3 · GP24/25/spares → J18 · GP26 VMON_12V · GP27 VMON_3V3 · GP28 VMON_1V8 · GP29 spare-ADC→J18.

- [ ] **Step 1: Failing checks:**

```
# mcu
U6.pinfn:USB_DP = USB_DBG_DP
U6.pinfn:GPIO4 = FCPO_CTL
U6.pinfn:GPIO5 = PCIE_DIS_CTL
U6.pinfn:GPIO26_ADC0 = VMON_12V
U7.pinfn:DO(IO1) = QSPI_SD1
SW1.1 = DIP0
Q6.pinfn:G = LED_EN
NET RGB_DI PINS>=2
NET I2C_SDA PINS>=6
```

(If the KiCad `MCU_RaspberryPi:RP2040` symbol names pins differently, adjust the `pinfn:` strings to the symbol's names — the assertion intent is fixed.)

- [ ] **Step 2:** Run — FAIL.
- [ ] **Step 3: Wire:** RP2040 minimal set per Raspberry Pi *Hardware design with RP2040* reference: U7 W25Q128 on QSPI, Y1 12 MHz + 27 pF ×2, 1V1 from internal reg (VREG_VOUT→DVDD, 1 µF), all IOVDD/USB_VDD→`+3V3_MCU`, 100 nF per supply pin, RUN→SW4 (to GND) + 10 k→+3V3_MCU, QSPI_SS→SW3 (BOOTSEL to GND). USB_DP/DM→`USB_DBG_DP/DM` via 27 Ω series. GPIO per map. LED-kill: Q6 gate=`LED_EN`, driven by SW2 slide (to +3V3_MCU) in series-OR with GP9 open-drain pull-down (SW2 on = 10 k pull-up high; GP9 low overrides); Q6 drain = common cathode rail `LED_RET` for ALL indicator LEDs (power_input PG/PoE LEDs reference `LED_RET` — go back and hook their cathodes if wired to GND). U15 TMP112 (0x48) placed-near-CN1 note; U16 (0x49) near U3/U10; J15 Qwiic (GND/+3V3/SDA/SCL); I2C 4.7 k pull-ups ×2; U18 SK6805 on `RGB_DI`+`+3V3_MCU`; J16 SWD (SWCLK/SWDIO/GND); J17 fan: +12V, Q7 low-side, gate `FAN_PWM`, flyback diode; J18 spare header (GP24, GP25, GP29, +3V3_MCU, GND); SW1 DIP-4 → `DIP0–3` with 100 k pull-ups (closed = low).
- [ ] **Step 4:** Pass; ERC 0; Commit `git add -A && git commit -m "sch: RP2040 control plane + GPIO map"`

### Task 10: Sheet ethernet (RTL8125BG + magjack)

**Files:**
- Modify: `sheets/ethernet.kicad_sch`, append `tools/netchecks.txt`

**Interfaces:**
- Consumes: `PCIE_MTX_P/N` (module TX), `PCIE_MRX_P/N`, `PCIE_REFCLK_P/N`, `PERST_N`, `CLKREQ_N`, `PEWAKE_N`, `RTL_RST_N`; produces `POE_VA±/VB±` to power_input, `MDI0–3`.

- [ ] **Step 1: Failing checks:**

```
# ethernet — PCIe cap ownership per Task 2 findings
NET PCIE_MTX_C_P PINS>=2      # module TX reaches U9 RX through caps
NET PCIE_MRX_C_P PINS>=2      # U9 TX through caps toward module RX
U9.pinfn:PERST# = PERST_N
NET MDI0_P PINS>=2
J4.pinfn:CT_A = POE_VA+
Y2.1 = RTL_XTAL1
```

(`pinfn` strings per the Task-1 symbol; adjust names, keep intent.)

- [ ] **Step 2:** Run — FAIL.
- [ ] **Step 3: Wire:** `PCIE_MTX_P/N` → 220 nF ×2 (or Task-2 value) → `PCIE_MTX_C_P/N` → U9 PERp/n0 (RX). U9 PETp/n0 (TX) → `PCIE_MRX_C_P/N` → caps → `PCIE_MRX_P/N` (→CN1 47/49) — cap ownership/side per Task 2's RC-mode reference; if Quectel's figure shows caps only on one side, follow it exactly and update these check names in place. REFCLK pair → U9 REFCLK in (+ any termination per RTL8125 datasheet). `PERST_N`→U9 reset in (and already pulled 1.8 V on m2 sheet — **check RTL8125 VIH at 1.8 V; if it needs 3.3 V logic, insert the 2N7002+pull-up level stage and note it**). U9 support: Y2 25 MHz + load caps, 93C46 EEPROM (U20 — extend refdes map), ISOLATEB/reset ← `RTL_RST_N`, LED0/1 → J4 LED pins (NOT on LED_RET), MDI0–3 100 Ω pairs → J4, magjack CTs → `POE_VA+/-`, `POE_VB+/-` hierarchical labels, 75 Ω Bob-Smith RC on J4 shield per magjack datasheet. All U9 power pins ← `+3V3` with datasheet decoupling.
- [ ] **Step 4:** Pass; ERC 0; Commit `git add -A && git commit -m "sch: RTL8125BG + 2.5G PoE magjack"`

### Task 11: Sheet sim (dual SIM + eSIM mux)

**Files:**
- Modify: `sheets/sim.kicad_sch`, append `tools/netchecks.txt`

**Interfaces:**
- Consumes: `UIM1_*`, `UIM2_*` from m2; `SIM_SEL`, `UIM2_DET_CTL` from mcu.

- [ ] **Step 1: Failing checks:**

```
# sim
SIM1.pinfn:VCC = UIM1_VDD
U11.pinfn:COM1 = UIM2_VDD
NET UIM2S_VDD PINS>=2
NET UIM2E_VDD PINS>=2
U12.pinfn:VCC = UIM2E_VDD
NET SIM_SEL PINS>=3
```

- [ ] **Step 2:** Run — FAIL.
- [ ] **Step 3: Wire:** SIM1 direct: `UIM1_VDD/RST/CLK/IO/DET` + D10 TPD4S009 + 22 pF per line + 100 nF on VDD. U11 TS3A27518E: COM side = `UIM2_VDD/RST/CLK/IO` (+DET channel); NO side = `UIM2S_*` → SIM2 socket (+D11 ESD + 22 pF); NC side = `UIM2E_*` → U12 MFF2 pads (VCC/RST/CLK/IO per MFF2 pinout, C1..C7); SEL=`SIM_SEL` 100 k pulldown = physical slot (verify polarity against TS3A27518E datasheet; flip pull if needed). `UIM2_DET`: through mux channel from slot-2 switch, plus Q8 2N7002 (extend refdes map) gate=`UIM2_DET_CTL` to assert "present" when eSIM active — confirm DET polarity per CN1 socket + both vendors (Task 2; Quectel USIM2_DET is active-high presence on RM520N).
- [ ] **Step 4:** Pass; ERC 0; Commit `git add -A && git commit -m "sch: dual SIM + eSIM slot-2 override mux"`

### Task 12: Sheet rf (MHF4 → SMA ×5)

**Files:**
- Modify: `sheets/rf.kicad_sch`, append `tools/netchecks.txt`

- [ ] **Step 1: Failing checks:**

```
# rf
J5.1 = ANT0
J10.1 = ANT0
J9.1 = GNSS
J14.1 = GNSS
NET ANT3 PINS>=2
```

- [ ] **Step 2:** Run — FAIL.
- [ ] **Step 3: Wire:** J5→J10 (`ANT0`), J6→J11 (`ANT1`), J7→J12 (`ANT2`), J8→J13 (`ANT3`), J9→J14 (`GNSS`); all shields→GND. Nets in class `RF_50`.
- [ ] **Step 4:** Pass; ERC 0; Commit `git add -A && git commit -m "sch: 5x MHF4-to-SMA RF breakouts"`

### Task 13: Full-schematic audit

**Files:**
- Modify: any sheet needing fixes; `docs/erc-waivers.md`

- [ ] **Step 1:** `uv run tools/check_nets.py` — Expected: `all checks pass` (full accumulated file, ~70 assertions).
- [ ] **Step 2:** `$KCLI sch erc sierra-to-usb.kicad_sch -o /tmp/erc.rpt` — 0 errors; every warning either fixed or logged in `docs/erc-waivers.md` with justification.
- [ ] **Step 3:** Export flat netlist (`$KCLI sch export netlist -o /tmp/full.net sierra-to-usb.kicad_sch`) and manually walk spec §7.1's table + §4's VCC policy against it one row at a time. Walk the Global Constraints safety list explicitly. Record "audited <date>" in `docs/verification.md`.
- [ ] **Step 4:** Commit — `git add -A && git commit -m "sch: full audit pass (netchecks + ERC + spec walk)"`

### Task 14: Footprints + BOM fields

**Files:**
- Modify: all sheets (symbol properties)

- [ ] **Step 1:** Assign footprints per `docs/sourcing.md` MPNs. Hand-solder rule check: no passive smaller than 0603; any hand-soldered EP part flagged for via-stitched pad (note in Value field suffix `[EP-VIA]` for Task 15 to consume).
- [ ] **Step 2:** Add properties to every symbol: `LCSC` (JLC-assembled lines), `Assembly` = `JLC` or `HAND`, `MPN`, `Distributor`. JLC set exactly: U6, U7?, U9, U1, U8?, U11?, U12, J5–J9, J15, CN1 (U7/U8/U11 = JLC only if QFN per Task 1; TSSOP → HAND).
- [ ] **Step 3:** `$KCLI sch export bom sierra-to-usb.kicad_sch --fields "Reference,Value,MPN,LCSC,Assembly,Footprint" -o /tmp/bom.csv` — inspect: zero rows with `Assembly=JLC` and empty `LCSC`; `grep -c 'JLC,' /tmp/bom.csv` matches the count from step 2.
- [ ] **Step 4:** Commit — `git add -A && git commit -m "sch: footprints + assembly-split BOM fields"`

### Task 15: Board setup

**Files:**
- Modify: `sierra-to-usb.kicad_pcb`, `sierra-to-usb.kicad_pro`

- [ ] **Step 1:** Stackup: JLC7628 4-layer 1.6 mm (L1 sig / L2 GND / L3 pwr / L4 sig). Enter JLC impedance-calculator geometries as custom rules: `DIFF_USB_90` w/gap, `DIFF_PCIE_85`, `DIFF_MDI_100`, `RF_50` CPWG width/clearance (record the four geometry numbers in a text note on a Comments layer + `docs/ordering.md` draft).
- [ ] **Step 2:** Board outline 100×80 mm; 4× M3 holes at corners (3.2 mm, 5 mm from edges); DRC custom rule: PoE primary zone keepout/clearance ≥2.5 mm to secondary (rule area named `POE_PRI_MOAT`).
- [ ] **Step 3:** Update from schematic (`Tools → Update PCB` or `$KCLI` equivalents); confirm all footprints import, 0 lost nets.
- [ ] **Step 4:** `$KCLI pcb drc sierra-to-usb.kicad_pcb -o /tmp/drc.rpt` — expected: only "unrouted" violations at this stage.
- [ ] **Step 5:** Commit — `git add -A && git commit -m "pcb: stackup, outline, impedance rules, moat"`

### Task 16: Placement

**Files:**
- Modify: `sierra-to-usb.kicad_pcb`

- [ ] **Step 1:** Floorplan per spec §11: north edge J1,J2,J3,J4; south edge J10–J14 (SMA) with J5–J9 MHF4 just inboard; CN1 center with SIM1/SIM2/U12 adjacent east; U9+Y2 between CN1 and J4; U1 between J1 and CN1 (SS runs short/equal); U6 cluster (U7,Y1,SW1–4,J16,J18,U18) west; power train (U2,U19,U3,L,U13/U14) near J2; PoE island (BR1/2,U10,T1,D7) beside J4 inside the moat; U15 touching CN1 courtyard, U16 by U3; bulk caps hugging CN1 VCC pins; JP1–3 near CN1 pin 24/38/68 side; test points along accessible rows.
- [ ] **Step 2:** All JLC-assembled parts on ONE side (top); verify with a screenshot render (`$KCLI pcb render --side top -o /tmp/top.png sierra-to-usb.kicad_pcb` and `--side bottom`).
- [ ] **Step 3:** Commit — `git add -A && git commit -m "pcb: placement floorplan"`

### Task 17: Routing — power + PoE

- [ ] **Step 1:** Route `POE_VA±/VB±`→bridges→U10/T1 inside the moat; verify moat DRC rule triggers if a secondary trace enters (deliberately draw one, expect DRC violation, delete it — this is the rule's failing-test).
- [ ] **Step 2:** Route +12V (2 mm min), +3V3/+3V3_MOD (3 mm or pour), INA226 shunts kelvin-connected; L3 power islands drawn (+3V3 / +12V / +1V8); stitch GND vias.
- [ ] **Step 3:** DRC: no new violations besides remaining unrouted; Commit `git add -A && git commit -m "pcb: power routing + PoE moat verified"`

### Task 18: Routing — high-speed + RF

- [ ] **Step 1:** SS pairs J1↔U1↔CN1 (90 Ω, L1 only, over solid L2, caps/ESD flow-through, intra-pair skew <0.15 mm); USB2 pairs incl. mux branches (90 Ω); PCIe pairs + REFCLK (85 Ω, skew <0.1 mm); MDI (100 Ω) U9↔J4.
- [ ] **Step 2:** RF: 5× CPWG runs J5–J9 → J10–J14 (Task-15 geometry), via fences both sides ~1 mm pitch, no crossings under/over switching nodes.
- [ ] **Step 3:** Run KiCad length/skew report for each pair class; record numbers in `docs/verification.md`. DRC clean except remaining slow nets. Commit `git add -A && git commit -m "pcb: high-speed + RF routing with skew report"`

### Task 19: Routing cleanup + final DRC

- [ ] **Step 1:** Route all remaining slow nets (straps, I2C, DIP, LEDs, SIM) — L4 preferred; GND pours L1/L4 stitched.
- [ ] **Step 2:** `$KCLI pcb drc --severity-error --exit-code-violations sierra-to-usb.kicad_pcb -o /tmp/drc.rpt` — Expected exit 0. Zero unrouted, zero errors; silk pass (refdes legible, strap/TP labels, DIP legend, "SIERRA↔QUECTEL universal carrier" title, JP1–3 warning text "Sierra only — see spec §4").
- [ ] **Step 3:** Final spec walk: re-run every Global Constraint against the finished board visually + netcheck rerun. Commit `git add -A && git commit -m "pcb: complete routing, DRC clean"`

### Task 20: Fab outputs + order pack

**Files:**
- Create: `fab/` outputs, `docs/ordering.md`

- [ ] **Step 1:** Export: `$KCLI pcb export gerbers -o fab/gerbers/ sierra-to-usb.kicad_pcb && $KCLI pcb export drill -o fab/gerbers/ sierra-to-usb.kicad_pcb && zip -j fab/sierra-to-usb-gerbers.zip fab/gerbers/*`
- [ ] **Step 2:** JLC CPL for assembled lines: `$KCLI pcb export pos --format csv --units mm --side front -o fab/cpl-all.csv sierra-to-usb.kicad_pcb`, then filter to `Assembly=JLC` refs (uv one-liner joining /tmp/bom.csv) → `fab/jlc-cpl.csv`; BOM split → `fab/jlc-bom.csv` (LCSC column) and `fab/hand-bom.csv` (MPN+distributor).
- [ ] **Step 3:** Write `docs/ordering.md`: JLC order options (4-layer JLC7628, ENIG, impedance control YES + the four geometry specs, stencil top, selective assembly w/ jlc-bom+cpl), plus the hand-solder kit shopping list per distributor, plus first-power bring-up steps (spec §14 order).
- [ ] **Step 4:** Commit — `git add -A && git commit -m "fab: gerbers, split BOM/CPL, ordering guide"`

---

## Self-Review (performed at write time)

**Spec coverage:** §4 power→Tasks 4/5; §5 USB3→7/8; §6 PCIe→10; §7 control→6/9; §8 SIM→11; §9 RF→12; §10 LEDs→4/9 (LED_RET rail noted in Task 9 step 3); §11 fab→15–20; §13 verifications→Task 2; §14 bring-up→ordering.md. Firmware (§7.3 behavior) deliberately out — separate plan.
**Placeholders:** part-number gaps are Task 1 *deliverables*, not TBDs; two datasheet-dependent polarities (U8 SEL, U11 SEL, UIM2_DET) carry explicit verify-and-flip instructions.
**Consistency:** net names in Tasks 6–12 all come from the Global net table; SS naming rule is host-perspective (`SS_MOD_RX_*` = CN1 29/31 module TX, `SS_MOD_TX_C_*` = CN1 35/37 module RX), consistent across the net table, Task 6, and Task 7 checks.
