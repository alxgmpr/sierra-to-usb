# Universal 5G M.2 Carrier — Design Spec

**Date:** 2026-07-14
**Status:** Approved section-by-section in brainstorming; pending user spec review
**Supersedes:** `handoff/m2-sierra-handoff/docs/specs/2026-07-10-em9293-carrier-design.md` (EM9293-only, USB-only, EasyEDA)
**Tooling:** KiCad 10 (`sierra-to-usb.kicad_pro` in this repo), JLCPCB 4-layer PCB + selective SMT assembly, remainder hand-soldered.

## 1. Purpose

A universal M.2 Key-B carrier for 5G WWAN modules that supports two operating modes:

1. **USB device mode** — the module presents USB 3.x SuperSpeed to a host PC. Required path for **Sierra/Semtech EM919x/EM929x** (which default to PCIe and need strap intervention — the original project goal), also works for Quectel RM-series.
2. **2.5GbE PHY mode** — the module runs its PCIe controller as **root complex** and directly drives an onboard **RTL8125BG** 2.5GbE NIC (5G2PHY-style standalone ethernet modem). **Quectel RM-series only**: verified (2026-07-14) that Sierra EM919x/EM929x firmware has no RC mode and no ethernet driver — the EM9 AT reference (41113480 Rev 11, Jan 2025) contains no equivalent of Quectel's `AT+QCFG="pcie/mode",1` / `AT+QETH="eth_driver","r8125",1`. The PCIe/RTL8125 hardware is identical either way; capability is purely module firmware.

An onboard **RP2040** provides dynamic strap control, vendor profiles, AT-command automation, and debug telemetry. Board is for personal use ("overkill welcome"), not for sale.

### Verified target-module facts
- Sierra EM919x/EM929x default to **PCIe** and never enumerate USB unless: pin 6 `Full_Card_Power_Off_N` high (internally 100k pulled down), pin 20 `PCIE_DIS` at **1.8 V** (abs max 2.10 V), pin 22 `VBUS_SENSE` high (**VIH 1.6–5.25 V** per EM919x PTS 41113174 Rev 8 Table 3-1).
- Quectel RM-series default to **USB**; PHY mode enabled by AT commands (see §7.4).
- Design is verified against: EM919x PTS (Rev 8), EM92XX PTS (Rev 1, Doc 41114313 — cross-check items flagged below), RM520N Hardware Design (V1.3), EM9 AT Reference (Rev 11).

## 2. Scope

**In scope:** forced-USB SuperSpeed path; PCIe→RTL8125BG 2.5GbE path; USB-C PD power; 802.3at isolated PoE power; RP2040 control plane (straps, DIP profiles, AT access via USB2 mux, telemetry); dual nano-SIM + MFF2 eSIM with slot-2 override; 5× MHF4→SMA RF breakouts; status LEDs with hardware kill; temp + current telemetry.

**Out of scope:** mmWave, enclosure design (mounting holes + edge-connector layout are in scope), Sierra PHY mode (firmware-impossible today), isolation-certified compliance testing.

## 3. Architecture

```
                                ┌──────────────────────────────────────────────┐
USB-C #1 DATA ── HD3SS3220 ─────┤ SS: 220nF → pins 35/37 (module RX)           │
  (UFP, Rd, SS orientation mux) │     pins 29/31 (module TX, caps in module)   │
  D± ── TS3USB221 USB2 mux ─────┤ USB2: pins 7/9                               │
             │A (default)       │                                              │
             │B                 │        M.2 Key-B socket (3042/3052)          │
RP2040 PIO-USB host ────────────┘        Sierra EM919x/EM929x, Quectel RM5xx   │
                                │                                              │
USB-C #2 PD ── CH224K@12V ──┐   │ PCIe lane 0 (Quectel RC mode):               │
                            ├─OR┤   41/43 modTX → caps → RTL8125BG ── magjack ── RJ45 2.5GbE
RJ45 PoE CTs ── bridges ──  │   │   47/49 modRX ← caps ← RTL8125BG        │
  TPS23730 iso fwd (EVM-093)┘   │   53/55 REFCLK (mod→PHY), 50 PERST# (OD out),│
        12V node → TPS565201 ───┤   52 CLKREQ#, 54 PEWAKE# (OD, pull-ups)      │
        → 3V3 (module, RTL8125) │                                              │
        → AP2112K-1.8 (straps)  │ UIM1 ── nano-SIM 1                           │
                                │ UIM2 ── TS3A27518E mux ── nano-SIM 2 / eSIM  │
USB-C #3 DEBUG ── RP2040 native │                                              │
  USB (CDC console + UF2)       │ Straps/senses ── RP2040 (see §7)             │
                                └──────────────────────────────────────────────┘
```

Three USB-C ports: **#1 data** (SS + USB2 + CC via HD3SS3220), **#2 power** (PD sink, CC only), **#3 debug** (RP2040 native USB, USB2 only, 5.1k Rd on CC). One port = one CC owner; no second PD trigger on the data port (would conflict with HD3SS3220 CC/orientation logic).

## 4. Power

- **PD input:** USB-C #2 → CH224K (CFG1 24 kΩ → request 12 V; VDD via 1 kΩ + 1 µF; PG open-drain → LED). SMAJ13A TVS on VBUS_PD.
- **PoE input:** RJ45 magjack center taps (all 4 pairs) → 2× diode bridges → SMAJ58A TVS → **TPS23730 802.3at PD + isolated active-clamp forward converter, copied verbatim from TI EVM-093** (opto feedback, Würth 750313355 transformer — the stocked, proven 12 V reference; supersedes the earlier "no-opto flyback" sketch per 2026-07-14 sourcing decision), Class 4 (25.5 W — classification resistors RCLSA=RCLSB=32 Ω per TPS23730 DS Table 8-1, the ONE deliberate deviation from the EVM-093 BOM, which ships Class 6/802.3bt; user decision 2026-07-14), 54 V → 12 V. Secondary GND = board GND; primary side moated per creepage rules.
- **ORing:** PD 12 V and PoE 12 V through ideal-diode OR → **12V node**.
- **Main buck:** TPS565201, 12 V → 3.3 V. EN via 1 MΩ from the 12V node (starts ≥~8 V, i.e., only after a PD contract or PoE class — module never boots on pre-negotiation 5 V). Inductor: 2.2 µH with **Isat ≥ 5.6 A** (upgrade from SWPA6045S2R2MT's 4.4 A — budget below).
- **Load budget:** module 3.0 A peak / 2.8 A cont (EM9293; EM9191 2.7 A) + RTL8125BG ~0.5 A + RP2040 & misc ~0.1 A ≈ **3.6 A peak** on 3V3.
- **Bulk at M.2 VCC:** 3× 470 µF polymer (≈1.5 mF, per EM92xx PTS r7.2 recommendation; user decision 2026-07-14) + 6× 10 µF ceramic + 0.1 µF per VCC pin (brownout mitigation — the documented failure mode).
- **1.8 V:** AP2112K-1.8 off 3V3; feeds strap pull-ups only.
- **RP2040 power:** dedicated AP2112K-3.3 fed by Schottky-OR of debug-port VBUS and main 3V3 — console alive with either source.
- **HD3SS3220 local 3V3:** AP2112K-3.3 off VBUS_DATA (mux alive whenever a data cable is present, per original reviewed design).
- **M.2 VCC pins — cross-vendor safety (critical):** power **only pins 2, 4, 70, 72, 74** (the standard set; 0.6 A/pin at 3.0 A peak — same loading as any laptop slot). Sierra's extra VCC pins **24, 38, 68 are landmines on Quectel** (24 = VDDIO_1V8 *output* on RM520N-GL; 38 = WLAN_TX_EN, a **1.8 V input**, on -GL; 68 = RESERVED). Each gets a **default-open solder jumper** to VCC for Sierra-only builds.

## 5. USB3 data path

- **TX/RX map (verified from EM919x PTS Fig. 3-2 + RM520N table; both vendors agree):** pins **29/31 = module TX** (220 nF inside the module — **no carrier caps**), pins **35/37 = module RX** (**carrier adds 220 nF series caps**, placed near the mux). ⚠️ The 07-14 handoff §6 had this backwards and its "fix #1" would have broken the working as-built EasyEDA arrangement. Re-verify EM92xx PTS Fig. equivalent at capture (expected identical; EM92xx §3.3.1 wording matches).
- Note: the host PC AC-couples its own TX on its motherboard, so host-TX→module-RX carries two caps in series (~110 nF effective) through our passive mux — within USB3 spec coupling range and per module-vendor host guidance.
- **Path:** USB-C #1 SS pairs → TPD4EUSB30 (flow-through, connector side) → HD3SS3220 2:1 mux (PORT=GND standalone-UFP, presents Rd, auto orientation; VBUS_DET via 900 k; VDD5 from VBUS_DATA; VCC33 local LDO) → TPD4EUSB30 (module side) → M.2.
- **USB2:** A6+B6 → D+, A7+B7 → D− at the receptacle → TPD4E05U06 ESD → **TS3USB221 2:1 mux** → M.2 pins 7/9. Mux position A (hardware default pull): data port. Position B (RP2040): RP2040 PIO-USB host (§7.3). No crossover jumpers (handoff issue #4 is designed out).
- **Debug port:** USB-C #3 → RP2040 USB (FS device). 5.1 kΩ Rd both CC pins, ESD array, no SS pins.

## 6. PCIe → RTL8125BG (Quectel PHY mode)

- Lane: module TX 41/43 → AC caps → RTL8125BG RX; RTL8125BG TX → AC caps → module RX 47/49. Cap values/placement per Quectel RC-mode reference + RTL8125BG reference design (verify at capture; ~100–220 nF).
- REFCLK 53/55: **module-driven** in RC mode → RTL8125 REFCLK in. PERST# (50): module **OD output** in RC mode — pull-up, routed to RTL8125 reset in + RP2040 sense. CLKREQ# (52) / PEWAKE# (54): OD + pull-ups, RP2040 sense.
- RTL8125BG: single 3.3 V supply (internal regs) *(correction 2026-07-15: single-supply is true only of the RTL8125B**GS** variant, which is not obtainable — no LCSC/authorized-distributor listing. The pinned RTL8125B**G**-CG requires an external 0.95 V core rail; the schematic provides it via a TLV62569 buck enabled by POW_EXT_SWR pin 6, and per Realtek's reference the NIC's 3.3 V must come from a ≥1 MHz forced-PWM switcher — a dedicated +3V3_ETH TPS62933F rail, not the ~580 kHz Eco-mode main rail)*, 25 MHz crystal, 93C46 EEPROM footprint (optional MAC/config), board-edge link/act LED on U9 LED3, fed from +3V3_ETH (correction 2026-07-15: the sourced Bel 2250504-1 magjack has no integrated LEDs; LED dies with its own domain), MDI 4 pairs (100 Ω diff) → magjack.
- RP2040 holds RTL8125 in reset/isolate in Sierra profile (block is dark when a Sierra card is installed).
- Net classes: PCIe **85 Ω diff**; MDI **100 Ω diff** (distinct from USB's 90 Ω).

## 7. RP2040 control plane

### 7.1 Straps and senses (cross-vendor verified)

All strap outputs are **2N7002 open-drain pull-downs against passive pull-ups** — the RP2040 physically cannot overdrive a rail. Blank/held-in-reset MCU = all defaults = **Sierra forced-USB mode works with zero firmware**.

| M.2 pin | Sierra | Quectel RM520N | Passive default | RP2040 |
|---|---|---|---|---|
| 6 | Full_Card_Power_Off_N | FULL_CARD_POWER_OFF# (same) | 100 k → 3V3 (ON) | FET low = off/power-cycle |
| 20 | PCIE_DIS (max 2.10 V!) | RESERVED (-GL) / PCM_CLK 1.8 V (-EU) | 10 k → **1V8** (USB) | FET low = PCIe (Quectel) |
| 22 | VBUS_SENSE (VIH 1.6–5.25 V) | RESERVED (-GL) / PCM_DIN **1.8 V input** (-EU) | **divider from VBUS_DATA → ~1.75 V** (tracks cable, 1.8 V-domain-safe) | FET forces high (for PIO-USB host sessions) |
| 8 | W_DISABLE1# | W_DISABLE1# (int. 100 k → 1.8 V) | 10 k → 1V8 (radio on) | FET low = airplane |
| 67 | RESET# (optional) | RESET# | pull-up | FET low = reset |
| 10 | WWAN_LED# | LED_WWAN# | LED to 3V3 | sense input |
| 23 | WAKE_ON_WAN# | WAKE_ON_WAN# | pull-up | sense input |

⚠️ Pin-22 divider: never restore the old 33 Ω direct-5 V feed — it damages RM520N-EU (PCM_DIN, 1.8 V). Never pull pin 20 above 2.10 V (Sierra abs max) — the FET topology enforces this.

### 7.2 Peripherals
- **4-pos DIP switch** (direct GPIO, read at boot): 2 bits profile (Sierra-USB / Quectel-USB / Quectel-PHY / auto-detect), 2 bits script flags.
- **I2C bus:** 2× temp sensors (TMP112/LM75-class: one at M.2, one at power stage), 2× **INA226** (12V input; modem 3V3 feed), Qwiic/STEMMA-QT connector.
- **ADC:** VBUS_PD, 3V3, 1V8 dividers.
- **RGB LED** — single-wire addressable (SK6805/WS2812-class, 3V3-logic variant, 1 GPIO) — firmware state. **LED kill:** all indicator LEDs return via a common low-side FET; slide switch gates it (default on) AND RP2040 can pull it off; magjack link LEDs excluded.
- **SIM mux select** + UIM2_DET drive (§8). RTL8125 reset. USB2 mux select. PIO-USB D+/D− (2 GPIO).
- SWD header, BOOTSEL + RESET buttons. GPIO budget: 26/30 committed (6 strap/kill FETs, 4 senses, RTL reset, USB2-mux sel, 2 PIO-USB, SIM-mux sel, UIM2_DET, 2 I2C, 3 ADC, 4 DIP, 1 RGB); remaining ~4 to a spare header (UART-capable pins preferred).

### 7.3 AT-command access (USB2 mux + PIO-USB host)
No M.2 UART exists on either vendor — AT is USB CDC-ACM only. RP2040 flips TS3USB221 to position B, forces VBUS_SENSE high, and enumerates the module as a **full-speed PIO-USB host** (pico-pio-usb; HS devices fall back to FS; AT traffic is tiny). Native USB stays the debug console.

Enables: band-lock/block script slots (DIP/console-selected, fired at boot); **Quectel PHY self-provisioning** (§7.4 sequence — no PC needed, improves on 5G2PHY); auto vendor detect (USB VID 0x1199/0x2c7c → set straps → power-cycle via pin 6); health polling (`AT!GSTATUS?`/`AT+QTEMP`); AT-driven SIM switching and eSIM LPA (`!CUSTOM "SIMLPA"` / `AT+QESIM`).

### 7.4 Quectel PHY-mode provisioning sequence (reference)
`AT+QCFG="data_interface",1,0` · `AT+QCFG="pcie/mode",1` (RC) · `AT+QETH="eth_driver","r8125",1` · `AT+QMAPWAC=1` — then reboot (pin 6 cycle).

## 8. SIM subsystem
- **UIM1** (pins 30/32/34/36, det 66; 1.8/3 V) → nano-SIM slot 1. **UIM2** (pins 40–48; Sierra 1.8 V-only) → **TS3A27518E 6-ch 2:1 mux** → nano-SIM slot 2 **or MFF2 eSIM** (ST4SIM-200M-class; 1.8/3 V class B/C). Select line pulled to "physical slot 2" (blank-firmware = normal dual-SIM board); RP2040/DIP flips to eSIM; RP2040 drives UIM2_DET "present" when eSIM active.
- Pin maps verified identical across vendors (incl. USIM2_VDD 48, USIM2_DET 40).
- TVS/ESD (TPD4S009-class) + 22 pF filtering at each socket, close to the M.2 connector.

## 9. RF breakouts
5× SMT MHF4 receptacle → 50 Ω CPWG (via-fenced, short) → edge SMA jack; labeled ANT0–ANT3 + GNSS. Card connects via MHF4 plug-to-plug jumpers. Covers 4×4 sub-6 MIMO + dedicated GNSS (EM919x); unused ports harmless on cards with shared GNSS.

## 10. LEDs and telemetry
Hardwired (on kill rail): 12V-node, PoE-active (TPS23730 status), modem WWAN_LED#, PD-good (CH224K PG). RGB = firmware state. Console commands: `temps`, `power` (INA226 live amps — brownout/throughput diagnosis), `straps`, `leds off`, `profile`, `at <cmd>`.

## 11. PCB / fabrication
- **JLC7628 4-layer** (~1.6 mm): L1 sig / L2 solid GND / L3 pwr islands / L4 slow signals. Controlled impedance: 90 Ω (USB SS + USB2), 85 Ω (PCIe), 100 Ω (MDI), 50 Ω CPWG (RF). Intra-pair length match. PoE primary moat per flyback creepage. RF edge opposite power/switching. ENIG.
- **Board:** ~100×80 mm class; USB-C ×3 + RJ45 one edge, SMA ×5 opposite; SIMs accessible; 4× M3 holes; test points on all rails, straps, USB2, PERST#/CLKREQ#; footprint-only 12 V fan header (PWM FET).
- **Assembly split:** JLC selective SMT for leadless/fine-pitch only — RP2040, RTL8125BG, HD3SS3220, muxes if QFN, eSIM MFF2, MHF4 receptacles, Qwiic JST-SH, M.2 socket. **Everything else hand-soldered**: 0603 min passives, leaded packages preferred, via-stitched thermal pads for iron-from-backside EP soldering, hand parts on accessible edges/side, JLC stencil ordered regardless.
- **BOM rule:** JLC-assembled lines must be LCSC-catalog; hand-placed parts may come from any distributor.
- **Sourcing checks before capture** (soft gates — hand-soldering allows any distributor): 2.5G+PoE magjack (LINK-PP), PoE flyback transformer, eUICC chip, MHF4 receptacles.

## 12. Key parts
M.2 socket Key-B (75-position/67-pin) + standoff · **RP2040** + W25Q128 + 12 MHz · **RTL8125BG** · **HD3SS3220RNH** · **TS3USB221** · **CH224K** · **TPS565201** · **TPS23730** + Würth 750313355 transformer (EVM-093 active-clamp forward) · **AP2112K-3.3 ×2 / -1.8** · **TS3A27518E** · MFF2 eUICC · **INA226 ×2** · TMP112 ×2 · TPD4EUSB30 ×3 · TPD4E05U06 · TPD4S009 ×2 · SMAJ13A / SMAJ58A · 2N7002 ×~7 · 2.5G PoE magjack · MHF4 ×5 · SMA ×5 · nano-SIM ×2 · USB-C ×3 · 4-pos DIP · slide switch · Qwiic JST-SH.

## 13. Verification items carried into implementation
1. EM92xx PTS: confirm USB3 fig. matches EM919x (caps on 35/37 only) and pin-22 VIH — user has the PDF locally.
2. Quectel RC-mode PCIe reference circuit: AC-cap ownership/values; REFCLK/PERST# wiring vs 5G2PHY practice.
3. Sierra pin 26/23/67 exact definitions in EM92xx PTS (Quectel side verified).
4. RM551E pinout spot-check (user's reference card) against the RM520N assumptions.
5. HD3SS3220 UFP wiring against datasheet (carried from reviewed design, re-verify in KiCad).
6. ~~TPS23730 vs TPS2373-4~~ RESOLVED 2026-07-14: TPS23730 per TI EVM-093 verbatim (active-clamp forward, opto, Würth 750313355); confirm Class-4 resistor set at capture.
7. eSIM DET polarity per vendor; TS3A27518E channel count covers VCC/RST/CLK/IO/DET.
8. JLC impedance calculator geometries for all four diff classes + RF CPWG on JLC7628.

## 14. Testing / bring-up plan (summary)
1. Power-only smoke: PD 12 V contract, rails, no module.
2. PoE: class negotiation on an 802.3at switch, isolation check, ORing behavior.
3. RP2040: UF2, console, strap toggling observed at test points.
4. Sierra card: blank-firmware USB enumeration on macOS (`ioreg` VID 0x1199), CDC-ACM AT, throughput vs RM551E reference.
5. Quectel card: USB profile first; then RP2040 self-provision PHY mode → 2.5GbE link → throughput.
6. Telemetry validation: INA226 vs bench meter during 5G TX; temp trend under load.
