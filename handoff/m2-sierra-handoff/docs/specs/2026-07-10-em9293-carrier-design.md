# EM9293 Forced-USB Test Carrier — Design Spec

**Date:** 2026-07-10
**Status:** Approved design, pending spec review
**Source of truth:** Sierra Wireless *EM92XX Product Technical Specification*, Rev 1 (Oct 2023), Doc# 41114313 (covers EM9291/EM9293). All pin numbers and voltage limits below are cited from Table 3-1 and §3.2–3.10 of that document.

## 1. Purpose

A single-purpose bench carrier board that holds a Sierra Wireless **EM9293** 5G module in **forced USB 3.2 SuperSpeed** mode, so it can be brought up on any host (including a Mac) and benchmarked against a Quectel RM551E reference. This board exists because the EM9293 defaults to PCIe and requires host-driven enable/interface-select signals that a Quectel-oriented carrier (e.g. the 5G2PHY) does not provide — so the module never powers on there.

### Root cause this board addresses (verified)
- `Full_Card_Power_Off_N` (**pin 6**) is internally pulled **down** and **must be pulled high to power the module on** (high = 1.35–4.4 V). A Quectel-oriented board does not drive it → module stays off → no LED, no USB, no enumeration.
- `PCIE_DIS` (**pin 20**) selects the host interface: **high (1.8 V) = USB**, float/low = PCIe. Interfaces are mutually exclusive and latched at boot.
- USB does not start until `VBUS_SENSE` (**pin 22**) is present.

## 2. Scope / non-goals

- **In scope:** forced-USB SuperSpeed data path, PD-sourced power, nano-SIM, status + power LEDs, on-module antennas.
- **Out of scope:** PCIe path, Ethernet PHY, enclosure, mmWave, GNSS-specific features, second SIM (UIM2), antenna tuner control.
- **Removed after verification:** a UART debug header — **the EM9293 M.2 connector exposes no UART**; AT/NMEA/diagnostic access is via USB CDC-ACM ports after enumeration.

## 3. Architecture (block diagram)

```
[USB-C #1: DATA]                                  ┌─────────────────────────────┐
   ├─ CC1/CC2 ── 5.1kΩ Rd (declare UFP/device)    │   EM9293  (M.2 3052 Key-B)  │
   ├─ VBUS (5V) ─────────────────► pin 22 VBUS_SENSE (5V-tolerant, direct)      │
   ├─ SS pairs ─► [SS 2:1 orientation MUX] ─► pins 29/31 TX (direct)            │
   │                                └────────► pins 35/37 RX (220nF series)     │
   └─ D+/D- ───────────────────────► pins 7/9 (USB2)                            │
                                                   │                            │
[USB-C #2: PD] ─► [PD sink 9–12V] ─► [Buck 3.3V/4A] ─► VCC pins 2/4/24/38/68/70/72/74
                                          │        │  pin 6  Full_Card_Power_Off_N ◄─ 75–100kΩ to VCC (enable)
                                          ├─[1.8V LDO] ─► pin 20 PCIE_DIS (force USB; ≤2.10V!)
                                          └─ PG LED    pin 10 WWAN_LED_N ─► green status LED
                                                       UIM1 pins ─► nano-SIM socket
```

## 4. Subsystems

### 4.1 Power (highest-risk subsystem)
- **PD sink** on USB-C #2: **CH224K** PD decoy (LCSC C970725, ESSOP-10, no programming). `CFG1 → 24 kΩ to GND` requests **12 V**; VDD from J2 VBUS via 1 kΩ (+1 µF); VBUS-sense via 10 kΩ; CFG2/CFG3/DP = NC; PG = open-drain (optional PD-OK LED). J2 VBUS (5 V→12 V after contract) feeds the buck input directly — no load switch. Sourced from a USB-C PD wall charger.
- **Buck converter:** **TPS565201** (4.5–17 V in, 5 A, VFB 0.760 V), 12 V → **3.28 V** (R1=33.2 kΩ / R2=10.0 kΩ), L=2.2 µH, Cin 2×10 µF/25 V, Cout 2×22 µF/10 V. Ripple ≤100 mVpp. **EN via 1 MΩ from VBUS_PD** (turn-on ≈8 V) so the buck only starts after the CH224K negotiates 12 V — the module never boots on the weak 5 V pre-PD rail.
- **Bulk capacitance at the M.2 VCC pins:** **2×470 µF/6.3 V polymer + 6×10 µF ceramic + 0.1 µF/VCC pin**, placed at the connector, to absorb 5G TX current transients (the brownout failure mode).
- **1.8 V LDO:** small (~150 mA) off 3.3 V; supplies the `PCIE_DIS` strap (high-impedance load). Independent of the module so it is stable at boot.
- **Power-good LED** on the 3.3 V rail.

### 4.2 Enable + interface-select straps
| Signal | Pin | Connection | Note |
|---|---|---|---|
| `Full_Card_Power_Off_N` | 6 | 75–100 kΩ pull-up to **VCC** | High=1.35–4.4 V. Rises with VCC → enables after power-good. Optional RC/PG-gated delay for margin (host must not drive signals <100 ms after power-on start). |
| `PCIE_DIS` | 20 | Tie to **1.8 V** rail | **Max 2.10 V — never VCC.** High=USB. |
| `VBUS_SENSE` | 22 | USB-C #1 VBUS (5 V) **direct** (series R + ESD) | High=2.0–5.25 V. No divider. |
| `W_DISABLE_N` | 8 | NC (float high) | Internally pulled up; radio on. |
| `GPS_DISABLE_N` | 26 | NC (float high) | GNSS on. |
| `RESET_N` | 67 | NC | Internally biased. **Never drive high (damage risk).** |
| `WAKE_ON_WAN_N` / `DPR` / `PLA_S2_N` | 23 / 25 / 28 | NC (test points optional) | `PLA_S2_N` optionally monitored for clean shutdown. |
| `CONFIG_0/1/2/3` | 21/69/75/1 | Leave as module straps | Do not repurpose (21/69 tied to GND by module). |

### 4.3 USB 3.x SuperSpeed data path (USB-C #1)
- USB-C receptacle as a **UFP/device: 5.1 kΩ Rd on CC1 and CC2.**
- **CC + orientation + SS mux (single chip):** **HD3SS3220** (LCSC C2155924, VQFN-30) as a standalone UFP — `PORT=GND`, `ADDR=NC`, `ENn_MUX=GND`, `ENn_CC=GND via RC`, `DIR=200 kΩ pull-up`, `VBUS_DET ← J1 VBUS via 900 kΩ`. Powers `VDD5 ← J1 VBUS (5 V)` and `VCC33 ← local 3.3 V LDO off VDD5` (satisfies the VDD5-before-VCC33 ordering rule). Integrates CC logic, orientation detect, and the SS 2:1 mux — replaces a separate CC controller + redriver. Handles both plug orientations. (Approved decision.)
- **SuperSpeed routing, 90 Ω differential, impedance-controlled:**
  - Module TX `USB3_TXM/TXP` (pins 29/31) → host RX, **direct** (no caps).
  - Module RX `USB3_RXM/RXP` (pins 35/37) → host TX, **220 nF series AC-coupling caps** near the connector (per Fig 3-1).
- **USB 2.0** `USB_D+/USB_D-` (pins 7/9) routed, 90 Ω differential, for enumeration/fallback. (Note: USB 2.0-only is not officially supported by the module; it exists here alongside SuperSpeed.)
- **ESD protection** on all exposed USB lines and VBUS.

### 4.4 SIM (UIM1 / primary)
Nano-SIM socket (GCT SIM8066, push-push) wired to: `UIM1_RESET` (30), `UIM1_CLK` (32), `UIM1_DATA` (34), `UIM1_PWR` (36). **No card-detect switch** → tie `SIM1_DETECT` (66) open = "SIM present" (bench rig needs no hot-swap detect; modem reports absence via AT). Per §3.5.1:
- Socket <10 cm from module; keep CLK/DATA short, avoid long parallel runs.
- `UIM1_PWR` decoupling **4.7 µF + 0.1 µF** at the socket.
- Optional 15–30 kΩ pull-ups on DATA/PWR; optional 47 pF/51 Ω on CLK; optional ESD array (user-exposed).
- Supports 1.8 V/3 V SIMs (auto).

### 4.5 Status / LED
- **Green status LED** driven by `WWAN_LED_N` (pin 10, open-collector, sinks ≤10 mA): LED + series resistor from VCC to pin 10. Gives the boot/registration blink patterns.
- Power-good LED per §4.1.

### 4.6 Antennas (no board RF)
- RF connectors are **on the module** (MHF/U.FL) — 4 antenna pigtails out. The datasheet requires **all four antennas enabled for commercial/normal operation**; populate all four for valid throughput testing.

### 4.7 Thermal
- The module runs hot under sustained TX. Provide a **heatsink / thermal pad** against the module shield; expect throttling on long throughput runs without it (§ Thermal Considerations).

### 4.8 Mechanical / fab
- **M.2 Type 3052-S3, Key-B** socket (Socket 2, Config #6: PCIe/USB3/Port Config 2) + standoff at the **52 mm** position.
- **4-layer, controlled-impedance PCB** (required for SuperSpeed), ~50×70 mm.
- Assembled via **JLCPCB PCBA** (fine-pitch M.2 connector + QFN PD/buck/mux are impractical by hand).

## 5. Bring-up & success criteria

1. Apply PD power → **power-good LED on**, 3.3 V measured at VCC pins.
2. Module enables (pin 6 high) → **green status LED** blinks; module boots.
3. Connect USB-C data → module enumerates on host as Sierra USB device (**`/dev/cu.usbmodem*`** on macOS / `ttyUSB*` on Linux), multiple CDC-ACM ports incl. AT.
4. `AT!ENTERCND="A710"`, `AT!GSTATUS?`, `AT!USBCOMP?` respond over the AT port (no SIM required).
5. Insert SIM → registers on network.
6. Throughput run vs the RM551E reference.

## 6. Open items / risks

- **PD source availability:** requires a real PD wall charger for 9–12 V (host ports may not source it). Barrel fallback was intentionally *not* included per design decision (two USB-C ports). Revisit if PD charger is inconvenient.
- **Buck/PD part selection** and **SS mux part** are class-level; exact parts finalized at schematic capture.
- **Enable sequencing:** static pull-up on pin 6 is datasheet-endorsed for always-on; add PG-gated/RC delay only if bring-up shows a power-on-timing issue (>100 ms rule).
- **1.8 V rail timing:** LDO must be stable before/with the module so `PCIE_DIS` reads high at boot; verify LDO enable/soft-start ordering vs VCC.

## 7. Bill of materials (LCSC part numbers)

C-numbers verified against LCSC/JLCPCB (2026-07); confirm live stock in EasyEDA at capture. **B**=JLC Basic (no extended-part fee), **E**=Extended.

### Actives
| Function | Part | Pkg | LCSC # | B/E |
|---|---|---|---|---|
| PD sink (12 V decoy) | WCH CH224K | ESSOP-10 | **C970725** | E |
| CC + orientation + SS mux | TI HD3SS3220 | VQFN-30 | **C2155924** | E |
| Buck 3.28 V/4 A | TI TPS565201DDCR | SOT-23-6 | **C327676** | E |
| 1.8 V LDO (strap rail, in 3.3 V) | Diodes AP2112K-1.8TRG1 | SOT-23-5 | **C176944** | E |
| 3.3 V LDO (HD3SS3220 VCC33, in ~5 V) | Diodes AP2112K-3.3TRG1 | SOT-23-5 | **C51118** | E |

### Connectors
| Function | Part | Pkg | LCSC # | Note |
|---|---|---|---|---|
| M.2 Key-B 67P socket | TE 2199230-3 | SMD, **4.2 mmH** | **C590859** | 4.2 mm → **standoff = 4.2 mm**. JLC in-house `C9900163443` = cheaper assembly alt (height unpublished). |
| USB-C recept ×2 (24-pin SS) | XKB U262-241N-4BV64 | SMD 24P | **C388660** | one part, J1 (full SS) + J2 (VBUS/CC/GND only). NOT the 16-pin `…4BVC11` lookalike. |
| Nano-SIM (4FF) push-push | GCT SIM8066-6-1-14-01-A | SMD | **C3032925** | **no card-detect** → tie `SIM1_DETECT` (pin 66) to "present" (leave open); bench rig needs no hot-swap detect. |

### Protection (ESD / TVS)
| Function | Part | LCSC # | Note |
|---|---|---|---|
| USB3 SS ESD (0.5 pF) | TI TPD4EUSB30DQAR | **C90627** | on J1 SS pairs (clone `C558427`) |
| USB2 + CC ESD | TI TPD4E05U06QDQARQ1 | **C81353** | J1 D±/CC (std-grade clone `C2827646`) |
| SIM ESD ×2 | TI TPD2E009DBZR | **C2871371** | UIM1 DATA/CLK/RST |
| VBUS TVS — J2 (12 V) | Diodes SMAJ13A | **C110519** | 13 V standoff, SMA |
| VBUS TVS — J1 (5 V) | Diodes SMAJ5.0A | **C87074** | 5 V standoff, SMA |

### Magnetics + capacitors
| Function | Value | Pkg | LCSC # | B/E |
|---|---|---|---|---|
| Buck inductor | 2.2 µH, 6 A Isat, 46 mΩ | 4020 | **C2926400** (YHNR4020-2R2M) — verified in stock | E. Works; higher DCR (~0.7 W). For lower loss, filter LCSC Power Inductors 2.2 µH / Isat ≥6 A / DCR <30 mΩ and pick an in-stock 6045. |
| Bulk ×2 | 470 µF 6.3 V polymer, 9 mΩ | D8 | **C2161524** | E |
| Buck Cout ×2 | 22 µF 25 V X5R | 0805 | **C45783** | B |
| Buck Cin + bulk ceramic | 10 µF 25 V X5R | 0805 | **C15850** | B |
| Decoupling | 1 µF 25 V X7R | 0603 | **C29936** | E (X5R basic `C15849`) |
| Per-pin decoupling | 0.1 µF 50 V X7R | 0402 | **C307331** | B (NOT `C1525`=16 V) |
| SIM PWR | 4.7 µF 16 V X5R | 0603 | **C19666** | B |
| USB3 AC-coupling ×2 | 220 nF 16 V X7R | 0402 | **C16772** | B |
| SIM CLK filter (opt) | 47 pF 50 V C0G | 0402 | **C1567** | B |

### Resistors (0402) + LEDs
| Function | Value | LCSC # | B/E |
|---|---|---|---|
| Buck FB top | 33.2 kΩ 1% | **C226998** | E |
| Buck FB bottom / pulldowns | 10.0 kΩ 1% | **C25744** | B |
| CH224K CFG1 (→12 V) | 24 kΩ 1% | **C138026** | E |
| Buck EN | 1 MΩ 1% | **C26083** | B |
| USB-C CC Rd (×2 on J1) | 5.1 kΩ 1% | **C25905** | B |
| HD3SS3220 DIR pull-up | 200 kΩ 1% | **C25764** | B |
| VBUS_DET divider | 910 kΩ 1% | **C25800** | E |
| Full_Card_Power_Off pull-up | 100 kΩ 1% | **C25741** | B |
| Series / LED / VDD | 1 kΩ 1% | **C11702** | B |
| VBUS_SENSE series | 33 Ω | **C25105** | B |
| SIM pull-ups | 22 kΩ 1% | **C25768** | B |
| SIM CLK series (opt) | 51 Ω | **C137960** | E |
| PG-LED series | 330 Ω 1% | **C25104** | B |
| Green LED ×2 (status + PG) | 0603 green | **C12624** | E |

Most ceramics/resistors are JLC **Basic** (no extended fee). Extended parts with no Basic equivalent: ICs, connectors, inductor, polymer caps, ESD/TVS, and the 33.2 k/24 k/910 k/51 Ω resistors + green LED (E96/high-value or discontinued-basic).

## 8. References

- Sierra Wireless EM92XX Product Technical Specification, Rev 1, Doc# 41114313 (Table 3-1 pin map; §3.2 power; §3.3 USB; §3.5 SIM; §3.6 control signals; §3.7 PCIE_DIS).
- Sierra Wireless EM9 Series AT Command Reference, Doc# 41113480 (AT!ENTERCND, AT!USBCOMP, etc.).
