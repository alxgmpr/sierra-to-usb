# EM9293 Carrier — Netlist (pin → net-label map)

**How to use in EasyEDA:** place each component, then drop a **net label** (not a wire) on each pin with the exact net name below. Same net name = connected across the whole schematic. Passives (§ Bridges) sit *between* two nets — place them and label each end. Pin names match the EasyEDA/LCSC symbol; where a datasheet pin number is known it's shown as `(n)`.

**Reference designators**
| Ref | Part | LCSC |
|---|---|---|
| U1 | CH224K (PD sink) | C970725 |
| U2 | HD3SS3220 (CC + SS mux) | C2155924 |
| U3 | TPS565201 (buck) | C327676 |
| U4 | AP2112K-1.8 (1.8 V LDO) | C176944 |
| U5 | AP2112K-3.3 (3.3 V LDO → mux VCC33) | C51118 |
| J1 | USB-C data | C388660 |
| J2 | USB-C power | C388660 |
| J3 | M.2 Key-B socket (modem) | C590859 |
| J4 | nano-SIM #1 UIM1 (SIM8066) | C3032925 |
| J5 | nano-SIM #2 UIM2 (SIM8066) | C3032925 |
| L1 | 2.2 µH inductor | C2926400 |
| D1 | TPD4EUSB30 (USB3 SS ESD) | C90627 |
| D2 | TPD4E05U06 (USB2/CC ESD) | C81353 |
| D3a/D3b | TPD2E009 (UIM1 SIM ESD, ×2) | C2871371 |
| D6/D7 | TPD2E009 (UIM2 SIM ESD, ×2) | C2871371 |
| D4 | SMAJ13A (J2 VBUS TVS) | C110519 |
| D5 | SMAJ5.0A (J1 VBUS TVS) | C87074 |
| LED1 | green (status) | C12624 |
| LED2 | green (power-good) | C12624 |

**Power-net legend**
| Net | What it is |
|---|---|
| `GND` | ground (global) |
| `VBUS_PD` | J2 VBUS, 5 V→12 V after PD contract → buck input |
| `+3V3` | buck output, 3.28 V → module VCC |
| `+1V8` | 1.8 V (U4) → PCIE_DIS strap only |
| `VBUS_DATA` | J1 VBUS, 5 V from host → U2 VDD5 + U5 input |
| `VCC33_MUX` | U5 output → U2 VCC33 only (kept off main +3V3 for power-on ordering) |
| `SW` | buck switch node (U3 → L1) |

**Direction key** (from the *device's own* perspective): **I** = input, **O** = output, **B** = bidirectional, **P** = power/ground, **OD** = open-drain output.

---

## 1. Power — CH224K PD sink (U1) + J2

**U1 CH224K** (ESSOP-10)
| Pin | Net | Dir | Note |
|---|---|---|---|
| GND (1) | `GND` | P | |
| VDD (2) | `VDD_224` | P-in | internal reg, fed from `VBUS_PD` via 1 kΩ |
| CFG2 (3) | *NC* | I | leave open (single-resistor mode) |
| CFG3 (4) | *NC* | I | leave open (single-resistor mode) |
| DP (5) | *NC* | B | legacy QC/BC1.2 D+ — **unused in PD-only** |
| DM (if on symbol) | *NC* | B | legacy QC/BC1.2 D− — **unused in PD-only** |
| CC2 (6) | `J2_CC2` | B | PD negotiation |
| CC1 (7) | `J2_CC1` | B | PD negotiation |
| VBUS (8) | `VBUS_SNS_224` | I | VBUS sense, via 10 kΩ from `VBUS_PD` |
| CFG1 (9) | `CFG1_224` | I | 24 kΩ→GND selects **12 V** |
| PG (10) | `PG_224` | OD | power-good, active-low (opt. LED) |

**J2 USB-C (power)** — `U262-241N-4BV64`, real symbol pins
| Pin(s) | Symbol name | Net | Dir |
|---|---|---|---|
| A4, A9, B4, B9 | VBUS | `VBUS_PD` | P-in |
| A1, A12, B1, B12, + shield 1-4 | GND | `GND` | P |
| A5 | CC1 | `J2_CC1` | B |
| B5 | CC2 | `J2_CC2` | B |
| A2/A3/B2/B3/A10/A11/B10/B11 | SSTX/SSRX | *NC* | — |
| A6/A7/B6/B7 | DP1/DN1/DP2/DN2 | *NC* | — |
| A8, B8 | SBU1/2 | *NC* | — |

*(Power-only port: only VBUS/CC/GND wired.)*

---

## 2. Power — buck TPS565201 (U3) + L1 + rails

**U3 TPS565201** (SOT-23-6, by pin name)
| Pin | Net |
|---|---|
| VIN | `VBUS_PD` |
| GND | `GND` |
| EN | `EN_BUCK` |
| SW | `SW` |
| FB | `FB_BUCK` |
| VBST/BST (if present) | boot cap to `SW` (see Bridges) |

**L1 2.2 µH:** `SW` ↔ `+3V3`

**U4 AP2112K-1.8** (SOT-23-5, by name)
| Pin | Net |
|---|---|
| VIN | `+3V3` |
| EN | `+3V3` (tie on = always enabled) |
| GND | `GND` |
| VOUT | `+1V8` |
| NC | *NC* |

**U5 AP2112K-3.3** (SOT-23-5, by name)
| Pin | Net |
|---|---|
| VIN | `VBUS_DATA` |
| EN | `VBUS_DATA` (tie on) |
| GND | `GND` |
| VOUT | `VCC33_MUX` |
| NC | *NC* |

**LED2 power-good:** `+3V3` → 330 Ω → LED2(anode→cathode) → `GND`

---

## 3. USB-C data + CC/mux — HD3SS3220 (U2) + J1

**U2 HD3SS3220** (WQFN-30)
| Pin | Net | Pin | Net |
|---|---|---|---|
| CC2 (1) | `J1_CC2` | TX2n (20) | `SSTX2_N` |
| CC1 (2) | `J1_CC1` | TX2p (21) | `SSTX2_P` |
| CURRENT_MODE (3) | *NC* | ADDR (22) | *NC* |
| PORT (4) | `GND` (UFP) | INT_N/OUT3 (23) | *NC* |
| VBUS_DET (5) | `VBUS_DET` | VCONN_FAULT_N (24) | *NC* |
| TXp (6) | `SSRX_P_A` | SDA/OUT1 (25) | *NC* |
| TXn (7) | `SSRX_N_A` | SCL/OUT2 (26) | *NC* |
| VCC33 (8) | `VCC33_MUX` | ID (27) | *NC* |
| RXp (9) | `USB3_TXP` | GND (28) | `GND` |
| RXn (10) | `USB3_TXM` | ENn_CC (29) | `GND` (via RC, see Bridges) |
| DIR (11) | `DIR` | VDD5 (30) | `VBUS_DATA` |
| ENn_MUX (12) | `GND` | EP / thermal pad | `GND` |
| GND (13) | `GND` | | |
| RX1n (14) | `SSRX1_N` | RX2n (18) | `SSRX2_N` |
| RX1p (15) | `SSRX1_P` | RX2p (19) | `SSRX2_P` |
| TX1n (16) | `SSTX1_N` | | |
| TX1p (17) | `SSTX1_P` | | |

**Directions (U2):** CC1/CC2, all TX/RX (6/7/9/10, 14–21) = **B** (analog SS passthrough); VBUS_DET, PORT, ENn_MUX, ENn_CC, ADDR, CURRENT_MODE = **I**; DIR, VCONN_FAULT_N, ID, INT_N, SDA, SCL = **O/OD**; VCC33, VDD5 = **P-in**.

> **Verify at capture:** device-side TX/RX and P/N assignment (pins 6/7/9/10 → module) against the TI HD3SS3220 EVM — a P/N or TX↔RX swap here is the classic USB-C bring-up bug.

**J1 USB-C (data)** — `U262-241N-4BV64`, real symbol pins (from your schematic)
| Pin | Symbol name | Net | Dir | Description |
|---|---|---|---|---|
| A1 | GND | `GND` | P | |
| A2 | SSTXP1 | `SSTX1_P` | B | SuperSpeed lane-1 TX pair + (→ mux TX1) |
| A3 | SSTXN1 | `SSTX1_N` | B | SuperSpeed lane-1 TX pair − |
| A4 | VBUS | `VBUS_DATA` | P-in | host 5 V (also powers U2 VDD5 + U5) |
| A5 | CC1 | `J1_CC1` | B | to U2.CC1 + ESD only — **no external Rd** (HD3SS3220 presents Rd internally) |
| A6 | DP1 | `USB2_DP` | B | USB 2.0 D+ — tie with B6 |
| A7 | DN1 | `USB2_DM` | B | USB 2.0 D− — tie with B7 |
| A8 | SBU1 | *NC* | — | sideband, unused |
| A9 | VBUS | `VBUS_DATA` | P-in | |
| A10 | SSRXN2 | `SSRX2_N` | B | SS lane-2 RX pair − (→ mux RX2) |
| A11 | SSRXP2 | `SSRX2_P` | B | SS lane-2 RX pair + |
| A12 | GND | `GND` | P | |
| B1 | GND | `GND` | P | |
| B2 | SSTXP2 | `SSTX2_P` | B | SS lane-2 TX pair + (→ mux TX2) |
| B3 | SSTXN2 | `SSTX2_N` | B | SS lane-2 TX pair − |
| B4 | VBUS | `VBUS_DATA` | P-in | |
| B5 | CC2 | `J1_CC2` | B | to U2.CC2 + ESD only — **no external Rd** (HD3SS3220 presents Rd internally) |
| B6 | DP2 | `USB2_DP` | B | tie with A6 |
| B7 | DN2 | `USB2_DM` | B | tie with A7 |
| B8 | SBU2 | *NC* | — | |
| B9 | VBUS | `VBUS_DATA` | P-in | |
| B10 | SSRXN1 | `SSRX1_N` | B | SS lane-1 RX pair − (→ mux RX1) |
| B11 | SSRXP1 | `SSRX1_P` | B | SS lane-1 RX pair + |
| B12 | GND | `GND` | P | |
| 1,2,3,4 | shield/mount | `GND` | P | connector shell |

**How the SS nets reach the mux (U2, connector side):** `SSTX1_±`→TX1(17/16), `SSRX1_±`→RX1(15/14), `SSTX2_±`→TX2(21/20), `SSRX2_±`→RX2(19/18). The mux then routes the *active* orientation's pair to the module.

---

## 4. Modem — M.2 socket (J3)

**Power/GND**
| Module pins | Net |
|---|---|
| 2, 4, 24, 38, 68, 70, 72, 74 | `+3V3` |
| 3, 5, 11, 27, 33, 39, 45, 51, 57, 71, 73 | `GND` |

**Straps / control** (dir = module's view)
| Pin | Signal | Net | Dir |
|---|---|---|---|
| 6 | Full_Card_Power_Off_N | `NET_PWR_ON` | I (drive high = on) |
| 20 | PCIE_DIS | `+1V8` | I (high = USB) |
| 22 | VBUS_SENSE | `VBUS_SENSE` | I (USB detect) |
| 10 | WWAN_LED_N | `WWAN_LED_N` | OD (LED sink) |
| 8, 26, 67 | W_DISABLE_N / GPS_DISABLE_N / RESET_N | *NC (float)* | I (internally biased) |
| 23, 25, 28 | WAKE_ON_WAN_N / DPR / PLA_S2_N | *NC* | O / I / O |
| 1, 21, 69, 75 | CONFIG_0..3 | *NC (module straps)* | O |

**USB (module side)** (dir = module's view)
| Pin | Net | Dir | Description |
|---|---|---|---|
| 7 USB_D+ | `USB2_DP` | B | USB 2.0 D+ (enumeration/fallback) |
| 9 USB_D− | `USB2_DM` | B | USB 2.0 D− |
| 29 USB3_TXM | `USB3_TXM` | O | module SuperSpeed TX − → mux RXn(10) |
| 31 USB3_TXP | `USB3_TXP` | O | module SuperSpeed TX + → mux RXp(9) |
| 35 USB3_RXM | `USB3_RXM` | I | module SuperSpeed RX − ← mux TXn(7) via 220 nF |
| 37 USB3_RXP | `USB3_RXP` | I | module SuperSpeed RX + ← mux TXp(6) via 220 nF |

**SIM (module side, UIM1)** (dir = module's view)
| Pin | Net | Dir |
|---|---|---|
| 30 UIM1_RESET | `UIM1_RST` | O |
| 32 UIM1_CLK | `UIM1_CLK` | O |
| 34 UIM1_DATA | `UIM1_DATA` | B |
| 36 UIM1_PWR | `UIM1_PWR` | P-out (module powers SIM) |
| 66 SIM1_DETECT | *NC (open = "present")* | I |

**SIM #2 (module side, UIM2)** — verified EM92XX PTS Rev 1, Tables 3-1 & 3-6 (dir = module's view)
| Pin | Net | Dir | Note |
|---|---|---|---|
| 46 UIM2_RESET_N | `UIM2_RST` | O | active-low reset |
| 44 UIM2_CLK | `UIM2_CLK` | O | serial clock |
| 42 UIM2_DATA | `UIM2_DATA` | B | bidirectional I/O |
| 48 UIM2_PWR | `UIM2_PWR` | P-out | **module powers SIM — 1.8 V only** (1.75–1.85 V; no 3 V mode) |
| 40 UIM2_PRES | *NC (open = "present")* | I | internal PU; 0 V = absent, open = present. Left open (no card-detect on SIM8066), symmetric with pin 66 |

> **UIM2 caveats (from PTS):** (1) UIM2_PWR is 1.8 V-only — old 3 V-only SIMs won't work in slot 2 (nearly all modern SIMs are 1.8 V-capable). (2) On eSIM-equipped SKUs, UIM2 is **muxed with the internal eSIM** — only one of {external UIM2, eSIM} is active at a time, set by config/software. Bench-test fine; not a fully independent path.

**LED1 status:** `+3V3` → 1 kΩ → LED1(anode→cathode) → `WWAN_LED_N` (module sinks it, active-low)

---

## 5. SIM socket #1 (J4, GCT SIM8066 — UIM1)

| SIM contact | Net |
|---|---|
| C1 VCC | `UIM1_PWR` |
| C2 RST | `UIM1_RST` |
| C3 CLK | `UIM1_CLK` |
| C5 GND | `GND` |
| C6 VPP | *NC* — legacy programming voltage, unused on modern UICCs; module has no VPP output |
| C7 I/O | `UIM1_DATA` |
| shell/shield | `GND` |

(No card-detect switch on this socket — module pin 66 left open.)

## 5b. SIM socket #2 (J5, GCT SIM8066 — UIM2)

| SIM contact | Net |
|---|---|
| C1 VCC | `UIM2_PWR` |
| C2 RST | `UIM2_RST` |
| C3 CLK | `UIM2_CLK` |
| C5 GND | `GND` |
| C6 VPP | *NC* — legacy programming voltage, unused; module has no VPP output |
| C7 I/O | `UIM2_DATA` |
| shell/shield | `GND` |

(No card-detect switch — module pin 40 UIM2_PRES left open = "present". Same 6-pin nano-SIM footprint as J4.)

---

## 6. Bridges (passives between two nets) — place + label both ends

**Power / buck**
| Ref | Value | Net A | Net B |
|---|---|---|---|
| R1 | 33.2 kΩ | `+3V3` | `FB_BUCK` |
| R2 | 10.0 kΩ | `FB_BUCK` | `GND` |
| R3 | 1 MΩ | `VBUS_PD` | `EN_BUCK` |
| C1,C2 | 10 µF 25 V | `VBUS_PD` | `GND` |
| C3,C4 | 22 µF | `+3V3` | `GND` |
| Cb | 0.1 µF | `VBST` | `SW` | *(only if U3 symbol has a VBST pin — per datasheet)* |
| Cbulk1,2 | 470 µF 6.3 V | `+3V3` | `GND` |
| C_3v3[] | 6× 10 µF + 0.1 µF/VCC-pin | `+3V3` | `GND` |

**CH224K**
| Ref | Value | Net A | Net B |
|---|---|---|---|
| R4 | 1 kΩ | `VBUS_PD` | `VDD_224` |
| C5 | 1 µF | `VDD_224` | `GND` |
| R5 | 10 kΩ | `VBUS_PD` | `VBUS_SNS_224` |
| R6 | 24 kΩ | `CFG1_224` | `GND` |
| R7 | 10 kΩ | `PG_224` | `VDD_224` |

**LDO decoupling**
| Ref | Value | Net A | Net B |
|---|---|---|---|
| C6 | 1 µF | `+3V3` | `GND` (U4 in) |
| C7 | 1 µF | `+1V8` | `GND` (U4 out) |
| C8 | 1 µF | `VBUS_DATA` | `GND` (U5 in) |
| C9 | 1 µF | `VCC33_MUX` | `GND` (U5 out) |
| C10 | 0.1 µF | `VCC33_MUX` | `GND` (U2 decouple) |

**USB-C / mux**
| Ref | Value | Net A | Net B |
|---|---|---|---|
| ~~R8~~ | ~~5.1 kΩ~~ | — | **DO NOT FIT.** HD3SS3220 "constantly presents Rd (5.1 kΩ) on both CC pins" internally (datasheet Rev E, §7). External Rd on `J1_CC1` halves it → attach detection fails. CC1 = mux CC1 + connector CC1 + ESD only. |
| ~~R9~~ | ~~5.1 kΩ~~ | — | **DO NOT FIT** (same reason, `J1_CC2`). |
| R10 | 200 kΩ | `DIR` | `VBUS_DATA` (pull-up) |
| R11 | 910 kΩ | `VBUS_DATA` | `VBUS_DET` |
| Rec/Cec | 100 kΩ + 0.1 µF | `ENn_CC` RC delay: 0.1 µF `ENn_CC`↔`GND`, 100 kΩ `ENn_CC`↔`GND` (or tie `ENn_CC` straight to `GND`) |
| Cac1 | 220 nF | `SSRX_P_A` | `USB3_RXP` (AC-couple module RX+) |
| Cac2 | 220 nF | `SSRX_N_A` | `USB3_RXM` (AC-couple module RX−) |

**Module straps / LED**
| Ref | Value | Net A | Net B |
|---|---|---|---|
| R12 | 100 kΩ | `NET_PWR_ON` | `+3V3` (pull pin 6 high = enable) |
| R13 | 33 Ω | `VBUS_DATA` | `VBUS_SENSE` (series to pin 22) |
| R14 | 1 kΩ | `+3V3` | LED1 anode |
| R15 | 330 Ω | `+3V3` | LED2 anode |

**SIM**
| Ref | Value | Net A | Net B |
|---|---|---|---|
| C11 | 4.7 µF | `UIM1_PWR` | `GND` |
| C12 | 0.1 µF | `UIM1_PWR` | `GND` |
| R16 | 22 kΩ | `UIM1_DATA` | `UIM1_PWR` (pull-up, opt) |
| R17 | 22 kΩ | `UIM1_PWR` | `+3V3`? — omit; UIM1_PWR is module-driven. (skip R17) |
| C13 | 4.7 µF | `UIM2_PWR` | `GND` |
| C14 | 0.1 µF | `UIM2_PWR` | `GND` |
| R18 | 22 kΩ | `UIM2_DATA` | `UIM2_PWR` (pull-up, opt — pulls to 1.8 V) |

**TVS / ESD** (cathode→signal, anode→GND for TVS; ESD arrays: tap listed nets + GND)
| Ref | On nets |
|---|---|
| D4 SMAJ13A | `VBUS_PD` → `GND` |
| D5 SMAJ5.0A | `VBUS_DATA` → `GND` |
| D2 TPD4E05U06 | channels on `USB2_DP`, `USB2_DM`, `J1_CC1`, `J1_CC2`; GND→`GND` (place at J1) |
| D1 TPD4EUSB30 | channels on `USB3_TXP`, `USB3_TXM`, `USB3_RXP`, `USB3_RXM`; GND→`GND` |
| D3a TPD2E009 | `UIM1_DATA`, `UIM1_CLK`; GND→`GND` |
| D3b TPD2E009 | `UIM1_RST` (+spare); GND→`GND` |
| D6 TPD2E009 | `UIM2_DATA`, `UIM2_CLK`; GND→`GND` |
| D7 TPD2E009 | `UIM2_RST` (+spare); GND→`GND` |

### Polarity / orientation (only these parts care — get them right)
| Ref | Polarized? | Orientation |
|---|---|---|
| Cbulk1, Cbulk2 (470 µF polymer) | **YES** | **`+` → `+3V3`**, **`−` (stripe) → `GND`**. Reversed = vents/pops. |
| LED1 (status) | **YES** | anode → 1 kΩ (`+3V3` side), **cathode → `WWAN_LED_N`** (module sinks it) |
| LED2 (power-good) | **YES** | anode → 330 Ω (`+3V3` side), **cathode → `GND`** |
| D4 SMAJ13A | **YES** (unidir) | **cathode (band) → `VBUS_PD`**, anode → `GND` |
| D5 SMAJ5.0A | **YES** (unidir) | **cathode (band) → `VBUS_DATA`**, anode → `GND` |
| D1/D2/D3 ESD arrays | pin-keyed | I/O pins on the signal nets, **GND pin → `GND`** (clamps are bidirectional; just honor the GND pin) |
| all resistors, all MLCC ceramics (10 µF/22 µF/1 µF/0.1 µF/4.7 µF/220 nF/47 pF), boot cap Cb | **NO** | non-polarized — either way is fine |

> Rule of thumb: the **polymer bulk caps, the two LEDs, and the two SMAJ TVS** are the only "install-backwards-and-it-fails" parts. Everything else in §6 is orientation-free.

---

## 7. Net-completeness check (key nets → every member)

- **`+1V8`**: U4.VOUT, J3.20 (PCIE_DIS), C7. *(nothing else — it's a strap rail)*
- **`NET_PWR_ON`**: J3.6, R12(→+3V3). *(2 members)*
- **`VBUS_SENSE`**: J3.22, R13(→VBUS_DATA). *(2)*
- **`VCC33_MUX`**: U5.VOUT, U2.VCC33(8), C9, C10. *(isolated from +3V3 — correct)*
- **`SSRX_P_A`/`SSRX_N_A`**: only U2.TXp/TXn(6/7) + Cac1/Cac2. Module RX side (`USB3_RXP/RXM`) only touches Cac + J3.37/35.
- **`EN_BUCK`**: U3.EN, R3(→VBUS_PD) only (internal 245 k pulldown does the rest).
- **`UIM2_PWR`**: J3.48, J5.C1, C13, C14, R18(→UIM2_DATA). *(module-driven 1.8 V rail — do NOT tie to +3V3 or +1V8)*
- **`UIM2_DATA`**: J3.42, J5.C7, D6, R18. **`UIM2_CLK`**: J3.44, J5.C3, D6. **`UIM2_RST`**: J3.46, J5.C2, D7. *(each SIM net = M.2 pin + socket contact + ESD channel, mirrors UIM1)*

> **Three verify-at-capture items:** (1) U3 buck pin names + whether it needs the VBST boot cap (per symbol/datasheet); (2) U2 device-side TX/RX P/N vs the HD3SS3220 EVM; (3) AP2112K EN/VIN/VOUT pin positions per the symbol (tie EN→VIN).
