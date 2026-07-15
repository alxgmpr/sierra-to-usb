# Datasheet Verification — Spec §13 Closeout

Closes out `docs/superpowers/specs/2026-07-14-universal-m2-carrier-design.md` §13 items 1–8.
Status legend: **VERIFIED** (checked against primary source, matches spec), **VERIFIED w/ CORRECTION** (checked, spec text needs a fix), **RESOLVED** (decision already made, confirmed consistent), **BLOCKED** (source unavailable, residual risk noted), **DEFERRED** (not a schematic-capture blocker, revisit later).

Primary sources used:
- **EM92XX PTS r7.2**, Doc 41114313, "Product Technical Specification EM929X," June 2026 — `docs/datasheets/41114313 EM92 Product Technical Specification r7.2.pdf`. **AUTHORITATIVE for EM9293/EM929X**, supersedes the "Rev 1" cited in the spec — r7.2 is newer.
- **RM520N Series Hardware Design V1.3** (Quectel) — text at `~/.claude/projects/.../tool-results/rm520n.txt`.
- **EM919x/EM7690 PTS Rev 8** (Semtech/Sierra) — text at `~/.claude/projects/.../tool-results/em919x.txt`.
- **TI TPS23730 datasheet** SLVSER6B (May 2020, rev. Nov 2020) — fetched, extracted locally.
- **TI TPS23730EVM-093 User's Guide** SLUUC91B (May 2020, rev. Aug 2023) — fetched, extracted locally.
- **TI HD3SS3220 datasheet** SLLSES1E (Dec 2015, rev. Jul 2025) — fetched, extracted locally.
- **TI TS3A27518E datasheet** SCDS260F — fetched, extracted locally.
- Quectel RM551E-GL public materials (web search) — no hardware design doc found; see item 4.

---

## Item 1 — EM92xx PTS: USB3 cap figure (35/37) and pin-22 VIH

**Status: VERIFIED — matches spec exactly. One citation correction.**

EM92XX PTS r7.2, **Table 2-3 "USB Interface"** (pin table) and **§2.3.1 "USB Host-side Recommendation," Figure 2-2 "Recommended Schematic for USB Signals"**:

- Pins **29/31 = USB3_TXMa/USB3_TXPa** ("Signal directions are from the module's point of view"): *"No capacitors are required on the host side for the EM929X module's USB3_TXM/USB3_TXP signals."*
- Pins **35/37 = USB3_RXMa/USB3_RXPa**: *"Series capacitors are recommended on the host side for the EM929X module's USB3_RXM/USB3_RXP signals"* — Figure 2-2 shows 220 nF caps on both RX lines, placed "Close to the Host Controller."
- **Exact match** to the EM919x-derived assumption in spec §5 (pins 29/31 module TX, no carrier caps; pins 35/37 module RX, carrier adds 220 nF). No mismatch.

Pin 22 — **Table 2-3** row: `VBUS_SENSE, pin 22, "USB detection"`; **Table 2-1** electrical row: `VBUS_SENSE, PD, Input, High: Min 1.6 V, Max 5.25 V`. **Exact match** to spec's "VIH 1.6–5.25 V" claim (previously only verified from EM919x Rev 8 — now independently confirmed in r7.2, cross-vendor-doc consistent).

**Citation correction (non-substantive):** the spec/brief guessed "EM92xx PTS §3.3.1" for the USB3 figure. The actual r7.2 document numbers this **§2.3.1 / Figure 2-2** (not §3.3.1 — that section number doesn't exist in this doc's ToC). The *fact* is unaffected; only the pointer needs fixing if anyone chases it later.

### Item 1d — VCC pin list

**Status: VERIFIED — confirms spec §4's VCC policy.**

EM92XX PTS r7.2, **§2.2 "Power Supply," Table 2-2 "Power Supply Requirements"**:

> `VCCa (3.3V) — Pins 2, 4, 24b, 38b, 68b, 70, 72, 74 — Voltage range 3.135 / 3.3 / 4.4 V; Ripple voltage max 100 mVpp`
> `GND — Pins 3, 5, 11, 27, 33, 39, 45, 51, 57, 71, 73`

Footnote **b** (quoted verbatim, appears identically as footnote d of Table 2-1):

> *"VCC pins 24, 38, and 68—These pins are optional, and can be left as NC."*

**Conclusion:** this confirms spec §4's cross-vendor VCC policy exactly. The standard set **2, 4, 70, 72, 74** is the mandatory supply path; Sierra itself declares **24/38/68 optional and NC-safe**, so powering only the standard set costs nothing on Sierra (no footnote contradiction — "optional" is explicit, twice). The default-open solder jumpers to 24/38/68 for Sierra-only builds are a pure bonus (extra current sharing), and leaving them open is what protects Quectel cards (24 = VDDIO_1V8 *output*, 38 = WLAN_TX_EN 1.8 V input on RM520N-GL, 68 = RESERVED — per RM520N HW Design V1.3 pin table). No mismatch.

---

## Item 2 — Quectel RC-mode PCIe reference circuit: AC-cap ownership/values; REFCLK/PERST# wiring

**Status: VERIFIED, with a refinement to spec §6's phrasing.**

RM520N HW Design V1.3, **§4.3.3 "Reference Design for PCIe," Figure 21 "PCIe Interface Reference Circuit"** (text-extracted directly from the schematic labels, not OCR):

```
Host                                                Module
PCIE_TX_P/M  ──C3/C4 220 nF──  PCIE_RX_P/M (49/47)   [caps near HOST]
PCIE_TX_P/M (43/41) ──C1/C2 220 nF (integrated)──  Host PCIE_RX_P/M
```

> *"AC coupling capacitors C3 and C4 should be placed close to the host on PCB. C1 and C2 have been integrated inside the module, so do not place these two capacitors on your schematic and PCB."*

This is **not vendor-specific** — it is an **M.2 spec requirement**. EM92XX PTS r7.2 §2.4.1 "PCIe Host-side Recommendation" states the identical rule verbatim, citing *"[20] PCI Express M.2™ Specification Revision 4.0, Version 1.1"* as the normative source: *"Series capacitors are required on the host side for the [module's] PCIE_RXM0/PCIE_RXP0 signals... No capacitors are required on the host side for the [module's] PCIE_TXM0/PCIE_TXP0 signals."* Independently confirmed across Quectel and Sierra documents (three sources: RM520N Fig. 21, EM92xx §2.4.1, and the underlying M.2 spec each cites) → **this is a fixed pin-level property of pins 41/43 and 47/49, unaffected by whether the module runs as PCIe endpoint or root complex.**

**Applying this to our RC-mode design (spec §6):**
- Module TX (41/43) → RTL8125BG RX: module already carries 220 nF caps internally. **No carrier caps needed on this leg.**
- RTL8125BG TX → module RX (47/49): **carrier must add 220 nF caps**, placed near whichever device is transmitting on that pair — in RC mode that's **RTL8125BG**, not the module (mirrors "close to the host" in the EP-mode reference, where "host" = the far-end transmitter).

**⚠️ Spec §6 refinement needed:** current text — *"module TX 41/43 → AC caps → RTL8125BG RX"* — is ambiguous/wrong if read as "carrier places caps on this leg." Per the confirmed pin-level rule, **no carrier caps belong on the module-TX/RTL8125-RX leg** (mirrors the USB3 TX pattern already correctly stated elsewhere in spec §5). Only the RTL8125-TX/module-RX leg needs board caps, and they should sit near RTL8125BG. Recommend updating §6 at capture to: *"module TX 41/43 → RTL8125BG RX (no carrier caps — module-internal); RTL8125BG TX → 220 nF caps near RTL8125BG → module RX 47/49."*

**REFCLK/PERST# wiring vs. 5G2PHY practice:** RM520N HW Design footnote 12 (also present in RM520N pin table): *"PERST# behaves as DI in PCIe EP mode, and as OD in PCIe RC mode. CLKREQ# and PEWAKE# behave as OD in PCIe EP mode, and as DI in PCIe RC mode. PCIe EP mode is the default."* **This confirms spec §6's claim exactly**: *"PERST# (50): module OD output in RC mode — pull-up... CLKREQ#(52)/PEWAKE#(54): OD + pull-ups"* — wait, spec says CLKREQ#/PEWAKE# are "OD + pull-ups, RP2040 sense" in RC mode; per this note they become **DI (inputs)** in RC mode, meaning **the carrier (RP2040/pull-ups) must drive them**, not just sense them with pull-ups. **Flag for capture:** in RC mode CLKREQ#/PEWAKE# are module *inputs* — RTL8125BG (or RP2040) needs to drive/service them, not just pull them up for sensing. Re-check RTL8125BG's own CLKREQ#/PEWAKE# pin directions at Task 6 capture to close this loop.

Cap value: 220 nF is inside the PCIe base-spec AC-coupling range (176–265 nF); the commonly-seen "100 nF" typical-app value in generic PCIe reference designs is *below* PCIe base-spec minimum — 220 nF (matching both vendors' own reference figures) is the correct choice, not a mid-range guess. Spec §6's "~100–220 nF" hedge should be tightened to **220 nF** at capture.

No RTL8125BG-specific reference schematic with AC-cap values could be located publicly (Realtek doesn't publish full reference schematics openly); the RTL8125BG side of the RX-leg caps should be confirmed against its datasheet/reference design at Task 6 capture, but 220 nF is a safe, spec-conformant default independent of that confirmation.

---

## Item 3 — Sierra pin 26/23/67 exact definitions in EM92xx PTS

**Status: VERIFIED.**

EM92XX PTS r7.2, **Table 2-1 "Host Interface (75-pin) Connections — Module View"**:

| Pin | Signal name | Type | Description | Active state / levels |
|---|---|---|---|---|
| 23 | `WAKE_ON_WAN_N` | OC | Wake Host | Output, Low 0–0.15 V |
| 26 | `GPS_DISABLE_N` | PU | Wireless disable (GNSS radio) | Input, High 1.1–4.4 V / Low ≤0.4 V |
| 67 | `RESET_N` | PU | Reset module | Input, Low active, −0.3 to 0.5 V |

Matches spec §7.1 table for pins 23 (`WAKE_ON_WAN#`) and 67 (`RESET#`, optional). **Pin 26 is not in spec's strap table at all** (spec's table lists pins 6/20/22/8/67/10/23 only) — this is fine, pin 26 (GPS_DISABLE_N on Sierra / W_DISABLE2# on RM520N per earlier verification) isn't wired to the RP2040 control plane in the current design and doesn't need to be. No contradiction — just confirming there's no missing strap-table row.

---

## Item 4 — RM551E-GL pinout spot-check (pins 6/8/20/22/24/38/68)

**Status: BLOCKED — no public RM551E-GL hardware design document exists.**

Searched: Quectel forums, Quectel.com, sixfab.com, cartft.com, wifiwithus.com, e2e.ti.com, GitHub (`xBryan101/RM551E-GL`, `iamromulan/RM551E-GL`, `iamromulan/cellular-modem-wiki`). Findings:
- Only a **"5G Specification V1.0.0 Preliminary" PowerPoint-derived marketing PDF** is public (`Quectel_RM551E-GL_5G_Specification_V1.0.0_Preliminary_20240201.pdf`) — confirmed via local `pdftotext`: it contains block-diagram/antenna images and marketing bullet points, **no pin table**.
- Community wiki (`iamromulan/cellular-modem-wiki`) has no pinout table for this module either.
- Forum discussion threads describe RM551E-GL as still in **engineering-sample stage** as of the search date — hardware design doc is likely NDA-gated.

**Residual risk:** per spec's own fallback plan, RM520N-GL pin assumptions (verified: pins 6/8/20/22/24/38/68 per RM520N HW Design V1.3, cross-checked earlier in this session) stand in for the Quectel family. RM551E-GL uses a newer Qualcomm X75 chipset (vs. RM520N's X62) — **CONFIG pin semantics or reserved-pin repurposing could differ** between generations; this is unverified. **Action for capture:** treat RM551E-specific pins as provisional; re-verify against the real hardware design doc (or against the physical card, since the design brief mentions "user's reference card") before finalizing any RM551E-specific strap/jumper decisions, or accept RM520N-derived behavior as the documented assumption with this flag attached.

---

## Item 5 — HD3SS3220 UFP wiring against datasheet

**Status: VERIFIED.**

TI HD3SS3220 datasheet SLLSES1E, **§4 "Pin Configuration and Functions"** (RNH 30-pin VQFN):

| Pin | Name | No. | Strap for our design | Datasheet text |
|---|---|---|---|---|
| PORT | 4 | Tri-level input | **GND (L → UFP)** | *"L - UFP (Pull-down or tie to GND if UFP mode is desired)"* |
| VBUS_DET | 5 | Analog input | **900 kΩ from VBUS_DATA** | *"5-28V VBUS input voltage... One 900K external resistor required between system VBUS and VBUS_DET pin."* §5 Electrical Characteristics: `R(VBUS)` min/typ/max = **880/900/910 kΩ**. |
| ENn_MUX | 12 | Digital input | **GND (L → normal operation)** | *"L - Normal operation, and H - Shutdown."* |
| ADDR | 22 | Tri-level input | **NC → GPIO mode (I2C disabled)** | *"NC - GPIO mode (I2C is disabled)"* (H=I2C addr 0x67, L=I2C addr 0x47) |

All four strap assumptions in spec §5 (`PORT=GND, VBUS_DET 900k, ENn_MUX=GND, ADDR=NC`) are **confirmed exactly**, including the 900 kΩ tolerance band (880–910 kΩ, so a standard 900 kΩ 1% resistor is correct).

**SS pin mapping table (for Task 7's mux net table):**

| Function | Pins | Side |
|---|---|---|
| TX1p/TX1n, RX1p/RX1n | 17/16, 15/14 | Type-C Port, orientation/CC1 channel (connector-side pair A) |
| TX2p/TX2n, RX2p/RX2n | 21/20, 19/18 | Type-C Port, orientation/CC2 channel (connector-side pair B) |
| TXp/TXn, RXp/RXn | 6/7, 9/10 | **Host/Device (fixed, muxed output)** — this is the module-side pair in our design |

The device automatically selects connector pair A or B based on CC1/CC2 detection and presents it on the fixed Host/Device pins. In our architecture (§5: "USB-C #1 SS pairs → TPD4EUSB30 (connector side) → HD3SS3220 → TPD4EUSB30 (module side) → M.2"), the Type-C Port pins (14–21) go to the connector-side TPD4EUSB30, and the Host/Device pins (6,7,9,10) go to the module-side TPD4EUSB30 → M.2 pins 35/37/29/31.

---

## Item 6 — TPS23730 / EVM-093 verbatim decision — Class-4 resistor set

**Status: RESOLVED (topology decision stands) — ⚠️ CONTRADICTION FOUND in the Class-4 claim, needs a capture-time decision.**

Spec §13.6 says: *"~~TPS23730 vs TPS2373-4~~ RESOLVED 2026-07-14: TPS23730 per TI EVM-093 verbatim (active-clamp forward, opto, Würth 750313355); confirm Class-4 resistor set at capture."* Spec §4/§12 both state **"Class 4 (25.5 W)"** for the design.

**Transformer/opto part numbers confirmed exactly** — TPS23730EVM-093 BOM (SLUUC91B, §4 Bill of Materials): `T2 = Würth Elektronik 750313355` (matches spec exactly), `U2 = TCMT1107 (Vishay)` optocoupler, `U1 = TPS23730RMT`, active-clamp forward topology per §1 ("TPS23730EVM-093 is targeted for a 12-V active clamp forward high efficiency 50-W solution"). **No mismatch here.**

**⚠️ Loud flag — Classification mismatch:** TPS23730EVM-093 User's Guide, **Table 2-1 "TPS23730EVM-093 Electrical and Performance Specifications"**, row `Classification` = **6**, not 4. Output spec in the same table: `Output Current, 37V≤Vin≤57V = 5 A` at `12 V` → this is a **Class 6 (40–51 W)** design point, not Class 4 (25.5 W). TPS23730 datasheet (SLVSER6B) §9.2.1.1.5 confirms the EVM's own worked "high-power design" example: *"For a high-power design, choose Class 6 where RCLSA = 32 Ω and RCLSB = 130 Ω."* The BOM's `R47 = 31.6 Ω` (closest E96 1% value to the Class-6 CLSA nominal of 32 Ω) is consistent with this; the CLSB designator/value could not be confirmed from BOM text alone (schematic pages are images, resolution too low to read the tiny reference designators near U1's CLSA/CLSB pins — attempted, inconclusive) — the Classification=6 electrical spec table (Table 2-1) is the authoritative statement regardless.

**Table 8-1 "Class Resistor Selection" (TPS23730 datasheet), Class 4 row:** `Min/Max power at PD = 12.95/25.5 W`, `2–3 classification cycles`, `RCLSA = 32 Ω`, `RCLSB = 32 Ω`.

**This is a real conflict, not a paperwork issue:** "copied verbatim from TI EVM-093" (Class 6, 51 W, 5 A @ 12 V) and "Class 4 (25.5 W)" cannot both be true simultaneously. Options for capture:
1. **Keep EVM-093 verbatim including Class 6** — this is a **standards move, not a wattage relabel**. Class 6 is an **IEEE 802.3bt Type 3** classification (TPS23730 datasheet SLVSER6B §8.4.1 "PoE Overview": *"devices with higher power and enhanced classification is referred to as Type 3 (Class 5, 6) or 4 (Class 7, 8) devices"*; Class 4 is the ceiling of 802.3at/Type 2). Adopting it abandons the spec's **802.3at decision-of-record** (§2 "802.3at isolated PoE power", §4 "TPS23730 802.3at PD"): full 51 W is only granted by an **802.3bt Type 3 PSE**, it requires **4-event classification** (Table 8-1: Class 6 = 4 class cycles, RCLSA = 32 Ω / RCLSB = 130 Ω), and on the plain 802.3at Type 2 switches the spec targets, the PSE power-demotes the board to Class 4/25.5 W anyway (datasheet §8.4.5 "Hardware Classification": *"A Type 2 PSE will treat a Class 5 to 8 device like a Class 4 device, allotting 25.5W if it chooses to power the PD"*). If chosen, spec §2/§4/§12/§13.6 and the bring-up plan (§14.2 "class negotiation on an 802.3at switch") must all be rewritten for 802.3bt.
2. **Deviate from EVM-093 on CLSA/CLSB only** — change to Class 4's `RCLSA = RCLSB = 32 Ω` (both resistors, per TPS23730 datasheet Table 8-1 — not the EVM's 32 Ω/130 Ω), keep the rest of the topology (transformer, opto, PWM controller, magnetics) unchanged. This **stays 802.3at** (Class 4 = Type 2, 2–3 class events, 25.5 W), matching the spec's explicit "Class 4 (25.5 W)"/"802.3at" decision-of-record, but is technically no longer "verbatim."

**Recommendation:** since spec text commits repeatedly and specifically to "Class 4 (25.5 W)" / "802.3at" language (not just as an incidental mention), the 3.6 A/3.3V ≈ 12 W main load doesn't need 51 W, and option 1 would ripple into the standards baseline and test plan, **option 2 is the minimal, lowest-risk change** — flag for the person doing Task 4 (power section capture) to explicitly choose and update the spec/BOM CLSA/CLSB resistors to 32 Ω/32 Ω, not blindly copy the EVM BOM's classification resistors.

---

## Item 7 — eSIM DET polarity per vendor; TS3A27518E channel count

**Status: VERIFIED — no blocker, one informational flag.**

TI TS3A27518E datasheet SCDS260F, §8 "Detailed Description": *"The TS3A27518E is a bidirectional, 6-channel, 1:2 multiplexer-demultiplexer... Two digital signals control the 6 channels of the switch; one digital control for each set of three single-pole, [double-throw switches]."* It is a **generic** 6-channel analog mux (marketed for SDIO/qSPI card expansion) — **no dedicated card-detect logic or DET-specific pin exists on this part**; any DET signal routed through it is treated as an ordinary analog/digital channel like VCC/RST/CLK/DATA. **6 channels ≥ 5 UIM2 signals** (VDD, RST, CLK, DATA, and DET if muxed too) → channel count is sufficient with 1 spare, confirming spec §13.7's "channel count covers VCC/RST/CLK/IO/DET" claim.

**DET polarity, cross-vendor:**
- **Sierra** (EM92XX PTS r7.2, Table 2-1, pin 40 `UIM2_PRES` and pin 66 `SIM1_DETECT`, footnote e): *"0 V—SIM not present / Open circuit—SIM present"* — i.e., **grounded = absent, floating (internally pulled up) = present**. Footnote e also notes: *"Active logic state is configurable."*
- **Quectel** (RM520N HW Design, §4.1.2 "USIM Hot-Plug"): `USIM1_DET`/`USIM2_DET` are **pulled LOW by default** and internally pulled up to 1.8 V only when hot-plug is software-enabled (`AT+QSIMDET=<enable>,<insert_level>`, `insert_level` 0=low-level-means-inserted / 1=high-level-means-inserted, configurable). §4.1.3 "Normally Closed (U)SIM Card Connector": *"USIM_DET pin is shorted to ground when there is no card inserted"* for NC-type sockets — same **grounded = absent, floating/high = present** convention as Sierra, when `insert_level=1` is configured and a normally-closed socket is used.

**No contradiction** — both vendors are compatible with grounded=absent/floating=present, but Quectel's is a software-configurable AT setting while Sierra's is fixed-but-"configurable" per an undocumented mechanism. **Flag for capture/bring-up:** (1) confirm the chosen nano-SIM socket is normally-closed type before wiring DET through the mux; (2) set `AT+QSIMDET` insert_level=1 on Quectel cards at bring-up; (3) informational — EM92XX PTS footnote f warns *"EM929X modules SKUs with 3V UIM2 support enabled are not compatible with host platforms that support mmWave — use of these modules will lead to damage on host-side mmWave components."* Moot today since mmWave is explicitly out of scope (spec §2), but flagged in case a 3V-UIM2 EM929X SKU is ever paired with a future mmWave-capable carrier revision.

---

## Item 8 — JLC impedance calculator geometries for all four diff classes + RF CPWG

**Status: DEFERRED — not a schematic-capture blocker.**

This item concerns PCB stackup trace geometry (JLC7628 4-layer, 90 Ω USB/USB2, 85 Ω PCIe, 100 Ω MDI, 50 Ω CPWG), which is a **Task 11 (PCB/fabrication) concern**, not a schematic-capture (Tasks 4–12 net-level) concern — no net-level fact here affects component selection or pin connectivity. The task brief's own step list (steps 1–4) does not include this item among the "new research" targets, consistent with treating it as out of scope for Task 2. **Action:** revisit at Task 11 using JLCPCB's impedance calculator against the finalized JLC7628 stackup (copper weight, dielectric thickness per layer) once the board is laid out enough to know actual trace/reference-plane geometry.

---

## Additional finding beyond the original 8 items

**⚠️ New datum — VCC bulk capacitance may be undersized relative to Sierra's own recommendation.** EM92XX PTS r7.2, **Table 2-2 "Power Supply Requirements"**, footnote a: *"A **1.5 mF supercapacitor** connected to VCC is strongly recommended to mitigate the module's peak current."* (1.5 mF = 1500 µF.) Spec §4's current bulk-cap plan is *"2× 470 µF polymer + 6× 10 µF ceramic + 0.1 µF per VCC pin"* = 940 µF polymer + 60 µF ceramic ≈ **1000 µF total**, and none of it is a supercapacitor (different technology — supercaps have much higher energy density per volume and different ESR/transient behavior than polymer electrolytics). This directly relates to spec §4's own note that this bulk cap is for *"brownout mitigation — the documented failure mode."* **Flag for Task 4 (power capture):** either size up the bulk cap bank toward 1.5 mF, add an actual supercapacitor in parallel, or explicitly document why the polymer-cap-only approach is judged sufficient (e.g., PD/PoE source impedance is different from the failure mode Sierra is guarding against) before finalizing the power section.

---

## Self-review

- Every VERIFIED claim above traces to a specific table/figure/section number in a primary-source document that was actually opened and grepped/read (not inferred from memory) — EM92XX PTS r7.2 (local PDF, `pdftotext -layout`), RM520N HW Design V1.3 (pre-extracted text, confirmed still relevant), TPS23730/TPS23730EVM-093/HD3SS3220/TS3A27518E TI datasheets (freshly fetched, extracted locally since WebFetch's own summarizer failed to parse embedded-font PDFs — verified via local `pdftotext` instead of trusting the WebFetch tool's mangled response).
- Two real contradictions were found and are flagged loudly, not smoothed over: (1) item 6 — EVM-093 "verbatim" ships as Class 6 (51 W), not Class 4 (25.5 W) as spec text states; (2) the "Additional finding" — Sierra's own 1.5 mF supercap recommendation exceeds the currently planned bulk-cap bank by ~50%.
- One further nuance flagged under item 2: spec's phrasing for RC-mode PCIe caps could be read as requiring carrier caps on the module-TX leg, which the confirmed pin-level M.2 rule contradicts (caps belong only on the RX leg, near the transmitter).
- Item 4 (RM551E) is honestly reported BLOCKED after a real search effort (not rubber-stamped) — no hardware design doc is publicly available for this still-engineering-sample module.
- Item 8 is explicitly scoped out as non-blocking for schematic capture rather than silently skipped.
- The TPS23730EVM-093 schematic pages were viewed as rendered images to try to pin down the CLSA/CLSB resistor designators precisely; resolution was insufficient to read the tiny reference designators with certainty, so that specific sub-claim (which BOM line is CLSB) is reported as "inconclusive" rather than guessed.

---

# Task 13 audit — full-schematic spec-against-netlist walk

**Audited 2026-07-15.** Method: single flat netlist export (`kicad-cli sch export
netlist --format kicadxml`) as ground truth; every row below derived from that
export (component/pin/net dumps), plus one full `kicad-cli sch erc` run and
`uv run tools/check_nets.py`. Approved amendments (task briefs/reports 4–12)
supersede spec text where they differ; only NEW drift is flagged. Full detail
in `.superpowers/sdd/task-13-report.md`.

## Check table

| # | Check | Result | Evidence (from flat netlist) |
|---|-------|--------|------------------------------|
| 1a | §7.1 pin 6 FCPO_N: 100 k→3V3 default-ON, OD FET | **PASS** | `FCPO_N` = {CN1.6, Q1.D, R51.2(100k→`+3V3`), TP1}; Q1.G=`FCPO_CTL`+R52 100k→GND |
| 1b | §7.1 pin 20 PCIE_DIS: 10 k→1V8 only, OD FET | **PASS** | `PCIE_DIS` = {CN1.20, Q2.D, R53.2(10k→`+1V8`), TP2}; no member can exceed 1.8 V (Q2 2N7002 OD to GND; TP passive) |
| 1c | §7.1 pin 22 VBUS_SENSE: divider + 1V8 force path | **PASS** | `VBUS_SENSE` = {CN1.22, R59.2(33k 1%←`VBUS_DATA`), R60.1(18k 1%→GND) ⇒ 5 V×18/51≈1.76 V, R61.2(330Ω←Q32.D), TP5}; force = Q5 2N7002 (G=`VBUSSNS_CTL`/GP8) pulls Q32(DMG3415U, S=`+1V8`) gate low vs R68 100k→`+1V8` — per approved amendment; no 5 V path exists |
| 1d | §7.1 pin 8 W_DISABLE1#: 10 k→1V8, OD FET | **PASS** | `W_DISABLE1_N` = {CN1.8, Q3.D, R55.2(10k→`+1V8`), TP3} |
| 1e | §7.1 pin 67 RESET#: pull-up, OD FET | **PASS** | `MODEM_RESET_N` = {CN1.67, Q4.D, R57.2(10k→`+1V8`), TP4} |
| 1f | §7.1 pin 10 WWAN_LED#: LED + sense | **PASS** | `WWAN_LED_N` = {CN1.10, D19.K, U24.GPIO16}; D19.A→R67 1k→`LED_PWR` (kill rail) |
| 1g | §7.1 pin 23 WAKE#: pull-up + sense | **PASS** | `WAKE_N` = {CN1.23, R63.2(100k→`+1V8`), TP6, U24.GPIO17} (but see FINDING F2 on sense levels) |
| 2a | §4 VCC = pins 2/4/70/72/74 only on `+3V3_MOD` | **PASS** | `+3V3_MOD` CN1 members exactly {2,4,70,72,74}; no other CN1 pin on any 3V3 rail |
| 2b | §4 pins 24/38/68 via default-open jumpers only | **PASS** | CN1.24=`M2_VCC_JP1`={CN1.24,JP1.1}; CN1.38=`M2_VCC_JP2`={CN1.38,JP2.1}; CN1.68=`M2_VCC_JP3`={CN1.68,JP3.1}; JP1-3 pin B all →`+3V3_MOD` (jumper strictly in series, 2-pin nets) |
| 2c | §4 bulk at M.2 VCC (amended 3×470 µF) | **PASS** | C44-C46 470uF + C47-C52 10uF ×6 + C53-C57 0.1uF ×5, all on `+3V3_MOD` |
| 2d | Blank-MCU defaults (all strap/select pulls) | **PASS** | gate/select pulls: R52/R54/R56/R58/R62 100k→GND (all strap FETs off ⇒ pin6 high, pin20 high@1.8 V, pin8 high, pin67 high); R72 100k→GND on `MUX_USB2_SEL` (S=L⇒1D=data port, polarity verified Task 8); R116 100k→GND on `SIM_SEL` (IN=L⇒NC=physical slot 2); R119 100k→GND on `UIM2_DET_CTL` (Q39 off); R84 10k→`+3V3_MCU` on `LED_EN_CTL` ⇒ Q35 on ⇒ Q33 gate low ⇒ LEDs ON; R102 10k→GND on `RTL_RST_N` (RTL8125 isolated); R87 100k→GND on `FAN_PWM` (fan off) |
| 3a | §3 USB3 chain J1→U1→CN1, caps on 35/37 leg only | **PASS** | J1 SS pairs→D20/D21(flow-through)→U1.14-21 (conn side); U1.9/10(RX)→C58/C59 220nF→`SS_MOD_TX_C_P/N`→D22→CN1.37/35; CN1.31/29→`SS_MOD_RX_P/N`→D22→U1.6/7(TX), **no caps** — matches approved role-corrected amendment |
| 3b | §3 USB2 chain, default = data | **PASS** | J1.A6/B6+A7/B7→`USB2_CON_DP/DM`→D23→U8.1/2(1D); U8.8/7(D)→CN1.7/9; U8.3/4(2D)→U24.GPIO2/3 (PIO-USB); R72 default selects 1D |
| 3c | §3 PCIe chain cap ownership | **PASS** | CN1.41/43(`PCIE_MTX_N/P`)→U9.42/41 HSIN/HSIP direct (no carrier caps — module-internal); U9.38/39 HSOP/HSON→C83/C84 220nF→CN1.49/47; REFCLK CN1.55/53→U9.44/45; PERST/CLKREQ/PEWAKE via Q36/Q37/Q38 BSS138 (G=`+1V8`) to `N_*_3V3` w/ R93-95→`+3V3_ETH` per approved amendment |
| 3d | §3 PoE chain | **PASS** | J8 VC12/VC36/VC45/VC78→BR1/BR2→`POE_VDD54`/`POE_VSS` (D7 SMAJ58A); U10 TPS23730 (RCLSA=R7=32Ω, RCLSB=R8=32Ω→`POE_VSS`, Class 4 per amendment); `POE_VSS`≠`POE_RTN` split present; T1 750313355 primary `POE_VDD54_F`/`N_SW`, secondary→sync rect (Q22/Q23, S=GND ⇒ secondary GND = board GND)→L1→`+12V_POE`→U21 LM5050→`+12V`←U19 LM5050←`VBUS_PD`; D16 PoE LED on `+12V_POE` (unkillable, accepted) |
| 3e | §3 SIM chain | **PASS** | UIM1: CN1.30/32/34/36/66→D27 TPD4S009+22pF→SIM1. UIM2: CN1.40-48→U29 TS3A27518E COM1-5; NC throws=`UIM2S_*`→D28+SIM2 (physical slot 2 = default); NO throws=`UIM2E_*`→U30 eSIM; `UIM2E_DET`={U29.NO5} float-only (present-by-float, no DET pull-ups anywhere: R114/R115/R118 absent); Q39.D on `UIM2_DET` = force-absent; U29 ch6 NC/NO grounded |
| 3f | INA226 insertions (amendment) | **PASS** | U13: IN+=`+12V`, IN−/VBUS=`+12V_BUCK` across R39 2 mΩ; U14: IN+=`+3V3`, IN−/VBUS=`+3V3_MOD` across R44 2 mΩ; both on `I2C_SDA/SCL` w/ U24.GPIO0/1, R80/R81 pulls, U26/U27 TMP112, J5 Qwiic |
| 4 | Cross-sheet net integrity (global labels) | **PASS** | all 85 distinct global labels have ≥2 members in the flat netlist; only single-pin net project-wide = `UIM2E_DET` (documented intended-float waiver, `NET UIM2E_DET PINS>=1` locked in netchecks); 92 `unconnected-*` stubs all NC-flagged (0 ERC pin_not_connected) |
| 5 | ERC | **PASS** | 0 errors / 788 warnings; category breakdown 622 endpoint_off_grid + 144 footprint_link_issues + 9 lib_symbol_mismatch + 1 isolated_pin_label + 2 multiple_net_names + 10 pin_to_pin — matches `docs/erc-waivers.md` Task-12 accounting exactly, no stale waiver rows found |
| 6 | `uv run tools/check_nets.py` | **PASS** | `all checks pass` (690-line accumulated file), exit 0 |
| 7 | Refdes uniqueness + annotation | **PASS** | 357 unique refs, 0 duplicates in flat netlist; netlist export emits no annotation warnings (3 consecutive runs) |
| 8 | BOM sanity | **PASS** (w/ Task-14 scope count) | every one of 357 symbols has a non-empty Value; footprint status for Task 14: 3 symbols with **empty** Footprint field (J2, J3, J8) + 144 symbols whose Footprint string doesn't resolve against a registered library (ERC footprint_link_issues item list) ⇒ **147 symbols** in Task 14 binding scope; remaining 210 resolve against stock libs |

## FINDINGS (electrical — reported, deliberately NOT fixed here)

- **F1 (CRITICAL — power): U3 TPS565201 can never be enabled as drawn.**
  Datasheet (TI, `tps565201.pdf` §6.5 Electrical Characteristics): VENH (EN
  high-level input voltage) **min 1.6 V**; REN (internal EN pull-down)
  **120–400 kΩ**. As built (`BUCK_EN` = {R40.2, R41.1, U3.EN}; R40 = 1.00 MΩ
  from `+12V`, R41 = 100 kΩ to GND): VEN(12 V) = 12 × (100k‖REN)/(1M + 100k‖REN)
  = **0.66–0.90 V** — below VENH under all tolerances (worst case ≤ VENL 0.8 V,
  i.e. guaranteed OFF). `+3V3` (hence `+3V3_MOD`, `+1V8`, module, everything)
  never starts. Origin is the plan/Task-5 brief's own "1 MΩ + 100 k (starts
  ≥~8 V)" arithmetic, which assumed neither the 1.6 V VENH nor the internal
  REN; spec §4's "EN via 1 MΩ from the 12V node (starts ≥~8 V)" is equally
  unachievable (even with R41 removed, worst-case REN=120k gives 1.29 V at
  12 V). Needs a redesigned EN network (e.g. ~100k/39k ⇒ 2.7–3.1 V at 12 V,
  start ≈6–7 V) chosen against the desired UVLO point.
- **F2 (MEDIUM — sense levels): GP17/GP18/GP19 read 1.8 V-domain highs on a
  3.3 V-IOVDD RP2040.** `WAKE_N`, `PERST_N`, `CLKREQ_N` are pulled to `+1V8`
  (R63 100k, R64/R65 10k) and sensed directly by U24 GPIO17/18/19; RP2040
  VIH = 0.65×IOVDD ≈ 2.1 V at 3.3 V, so a 1.8 V high is in the undefined
  region. Task 10 confirmed this exact problem for the RTL8125 side and
  level-shifted it (Q36-38) but the RP2040 side stayed on the 1.8 V nets.
  Enabling RP2040 internal pull-ups (~50k to 3.3 V) rescues `WAKE_N` (100k
  external ⇒ ~2.8 V) but not PERST/CLKREQ (10k external ⇒ ~2.0-2.1 V,
  marginal at best, and back-biases the 1.8 V rail slightly). Options: sense
  the existing 3.3 V-side nets `N_PERST_3V3`/`N_CLKREQ_3V3` instead (already
  have R93/R94 pull-ups, though to `+3V3_ETH` which is down in Sierra
  profile), add two more BSS138 stages, or document firmware/margin
  acceptance. (GP16/`WWAN_LED_N` is NOT affected — no external pull; the
  internal-pull-up mitigation note is already on-sheet per Task 9.)
- **F3 (MINOR — functional gap vs spec §4/§10): no PD-good LED and no
  12V-node LED exist anywhere.** Spec §10 lists four hardwired indicators;
  only WWAN (D19) and PoE-active (D16) were captured. `CH224K_PG` is a
  dead-end net = {U2.10, R4 10k→`+3V3`} — pulled up but read by nothing and
  lighting nothing (the Task-4 brief itself specified only the pull-up).
  Decide: add the two LEDs on `LED_PWR`, route PG to a spare GPIO (J7 has
  GP24/GP25), or amend spec §10.

## Spec text updates needed (approved amendments the spec doesn't reflect — no NEW drift)

1. §4 "EN via 1 MΩ from the 12V node (starts ≥~8 V)" — arithmetically impossible against TPS565201 VENH/REN (see F1); rewrite once F1's fix is chosen.
2. §6 "PERST# … RP2040 sense. CLKREQ#(52)/PEWAKE#(54): OD + pull-ups, RP2040 sense" — per the approved Task-9 GPIO map, PEWAKE# has **no** RP2040 GPIO (pull-up + BSS138 to U9 LANWAKEB only); only PERST (GP18) and CLKREQ (GP19) are sensed.
3. §6 "module TX 41/43 → AC caps → RTL8125BG RX" — already flagged by Item 2 above; as-built (correctly) has no carrier caps on that leg; caps (C83/C84, 220 nF) sit on the RTL8125-TX→module-RX leg only.
4. §5/§12/§7.2 residual refdes/net names (U6→U24 RP2040, U7→U25 flash, Q6 LED-kill→Q33/Q35, `LED_EN`→`LED_EN_CTL`, magjack J4→J8, RF J5-J14→J9-J18, TPS565201-era "580 kHz Eco" note vs §6's own +3V3_ETH correction) — all covered by approved amendments; a consolidation pass on the spec would help Task 14+.
5. §10 hardwired-LED list — pending the F3 decision.

## Task 13 fix-pass re-verification (2026-07-15, post-3b3ee19)

Independent closure check from a fresh flat netlist export (membership diff
old→new shows **only** the declared fix scope: R40/R41 value-only, GP17/18/19
retargets, Q40/R122, D29/R120, D30/R121 — zero collateral changes; all 28
audit rows above re-confirmed; 363 unique refs/0 dups; check_nets all-pass;
ERC 0 errors / 800 warnings matching erc-waivers.md's fix-pass accounting
category-for-category; single-pin set still exactly {`UIM2E_DET`}).

- **F1 CLOSED (with one documented residual).** Four-corner arithmetic
  independently recomputed and confirmed: ratio(REN=120k)=0.19141 ⇒
  VEN(11 V)=2.105 V (+31.6% over VENH 1.6 V), crossover 8.36 V;
  ratio(REN=400k)=0.19953 ⇒ VEN(5.5 V)=1.097 V, VEN(5 V)=0.998 V. The
  2-resistor impossibility proof also checks out (required gain
  1.76/0.72=2.44× vs divider cap 11/5.5=2.00×, further reduced by REN
  loading). **Residual (accepted-risk wording correction):** the fix
  report's claim that 1.097 V is "exactly the UVLO-latch stays-off region"
  overstates the guarantee — 0.8–1.6 V is the *indeterminate* band; the
  datasheet bounds a part's rising threshold only as ≤1.6 V (and ≥~VENL
  0.8 V), so a worst-case part may enable at a node voltage as low as
  ≈4.0 V, i.e. **"no false start on 5–5.5 V VBUS" is typical-expected but
  not datasheet-guaranteed** (and provably cannot be with any 2-R divider
  on this pin). Consequence if it happens: pre-contract boot attempt →
  USB source current-limit/brownout loop — benign, no module-safety
  interaction (strap domains unaffected). Guaranteeing it would need a
  precision UVLO/comparator on EN; accepted as residual risk for this
  personal-use board.
- **F2 CLOSED.** `N_PERST_3V3`={Q36.D, R93.1, U24.GPIO18, U9.PERSTB},
  `N_CLKREQ_3V3`={Q37.D, R94.1, U24.GPIO19, U9.CLKREQB}, `WAKE_3V3`=
  {Q40.D, R122.1, U24.GPIO17}; Q40 mirrors Q36-38 exactly (G=`+1V8`,
  S=`WAKE_N`, D=`WAKE_3V3`); R93/R94 4.7k→`+3V3_ETH` (rail is
  always-on when +12V is up — U15 EN comes from the R112/R113 divider off
  `+12V`, so the pull-ups are powered in every profile), R122 4.7k→`+3V3`.
  1.8 V-side nets unchanged. All highs now ≥VIH.
- **F3 CLOSED.** D29(green)/R120 1k: `LED_PWR`→R120→D29→GND ≈1.1 mA —
  fine; indicates "12 V negotiated" transitively via the F1-gated `+3V3`,
  killable per spec. D30(blue)/R121 1k: `LED_PWR`→R121→D30→`CH224K_PG`
  (open-drain active-low, LED use per WCH datasheet). R4 10k pull-up
  coexistence is sane: PG released ⇒ node 3.3 V ⇒ 0 V across D30 branch
  (clean off); PG low ⇒ D30 current ≈(3.3−Vf_blue≈2.6−VOL)/1k ≈ **0.6 mA**
  + R4's 0.33 mA ⇒ ~1 mA total PG sink, well within an OD pin.
  *Observation (non-blocking):* 0.6 mA is dim for a blue LED — consider
  470-680 Ω for R121 or a green part at Task-14 BOM lock.

**Task 13 gate verdict: APPROVED** (Task-14 footprint scope updates to
**151** symbols: 148 footprint_link_issues refs + J2/J3/J8 empty fields).
