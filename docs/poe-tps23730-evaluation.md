# PoE stage: TPS23730 / PMP22477 evaluation

2026-11-22. **Adopted the same day** with option B (TIDA active bridge kept), parallel grant mode
(R65 left open), D13 dropped, a 470 Ω preload (R1775) and the `ISO_12V` maximum raised to 14 V.
One correction to §1: R58 is the PSR feedback divider's bottom resistor and stays; it is not part
of the setpoint shift. See [hardware/README.md](../hardware/README.md). The text below is the
evaluation as written.
Baseline is `layout/placement` at 1556f20 (843 components, placed, unrouted).
The candidate is TI **TPS23730** (802.3bt Type 3 PD + PWM controller), adapted from
TI reference design **PMP22477** (Class 6, 12 V / 3.8 A, PSR flyback, diode rectifier).

## Recommendation: go-if

Swap to TPS23730/PMP22477 only if all four conditions hold:

1. **The flyback transformer can be bought.** PMP22477 uses LinkCom LDT9055-51R. Its
   listed alternates are Würth 750320319 and Sumida PS21-212. None of the three had a
   DigiKey listing or LCSC (tscircuit index) entry on 2026-11-22. Get a quote and
   samples first. The current Würth 750317065 is not a drop-in (§4).
2. **A preload goes on `ISO_12V_PSU`.** 470 Ω in a 2512 (about 0.3–0.4 W) holds the
   light-load output near 13.4 V instead of 15.7 V. If standby power matters, use an
   active clamp instead (§3).
3. **The `ISO_12V` maximum is raised** from the documented 13.2 V
   ([main-5v-supply.md](main-5v-supply.md)) to 14 V. The alternative is a 270 Ω
   preload, which costs about 0.6 W.
4. **Aux and PoE are not run together on a demoted grant.** Firmware already refuses to
   enable loads on PoE without a 0/1/0 grant. Without the PMP22477 power-limit circuit,
   the PSR droop makes the PoE share uncontrolled whenever aux is also present (§3.4).

If condition 1 fails, the answer is **no-go**. Keep TIDA-050023 and take the cheap
part of this saving now by removing its 12 evaluation-board leftovers (§1).

What the swap buys is modest:

- About 27–34 fewer fitted parts. About 12 of those could be removed today without
  changing the chip.
- About 9% less footprint area.
- No optocoupler or TL431 in the feedback loop.
- About 2 W more measured Class 6 headroom than the planning estimate.

The costs:

- The flyback layout gets redone (997fb5e and cff4aee are discarded).
- The TIDA golden-partition check is rewritten.
- The 802.3 isolation story moves to a new transformer.

## 1. Part count and area

Counted from the native netlist (`kicad-cli sch export netlist`) at 1556f20:

| Sheet | Refs | Fitted | Footprint area* |
|---|---:|---:|---:|
| PoE active input bridge (`poe-input`) | 30 | 26 (D1706–D1709 DNP) | 606 mm² |
| PoE PD / Class 6 (`poe-pd`) | 10 | 10 | 191 mm² |
| Isolated 12 V flyback (`poe-flyback`) | 78 | 77 (R1762 DNP) | 1945 mm² |
| Isolated PoE allocation (`poe-status`) | 12 | 12 | 81 mm² |
| **Total** | **130** | **125** | **2822 mm²** |

\*Per-footprint courtyard bounding box. Where a footprint has no courtyard (the TI
`PoE:` library parts), fab outline plus pads is used. Placed bbox of bridge + PD +
flyback: 80.6 × 72.5 mm ≈ 5840 mm².

The "about 108" figure is the 30 bridge + 78 flyback parts that the golden check
freezes against TIDA-050023. The flyback contains **12 evaluation-board leftovers**:

- J1711 ED555 terminal block
- J1712 Molex header
- D1716 LED
- TP1719–TP1727 Keystone test points

Together they take 153 mm². None is needed on the appliance.

The PMP22477 Rev D BOM (TIDMA49A, 3/5/2024) has **167 fitted parts**. Mapped onto the
appliance:

| PMP22477 block | Fitted | Fate here |
|---|---:|---|
| RJ45 ×2, data transformer T1, Bob-Smith R1–R8 / C1–C6 | 17 | Already in `ethernet-ingress`; not counted |
| Input-power-limit circuit (sheet 3: TLV4376, LM4040, Q1–Q4, U3–U7 FOD817DS, J5–J9, R9–R40, R100, R101, C9–C18, D9) | 56 | Drop (§3.4). U3/U4/U6 duplicate our TPH/TPL/BT optos |
| Setpoint shift (U11, Q5, R57, R58, R62, J14 "PoE SELECT") | 6 | Drop |
| Adapter OR diode D10, adapter/output terminals J11, J13 | 3 | Drop; aux ORing exists on `aux-power` |
| **Power core**: bridge D1–D8, L1–L3, C7/C8, TVS D13, TPS23730 U10, FET Q6, T2, rectifier D11, clamp, bias, output filter, passives | **85** | Keep |

The power core includes seven 0 Ω links (R48, R49, R52, R55, R59, R60, R73), and most
of them can go. The partition comes from the PDF schematic (TIDMA48A). Allow ±3 for
passives near the sheet boundaries.

| Option | Fitted | vs. 125 today | Footprint area |
|---|---:|---:|---:|
| A: PMP22477 core, 8-Schottky bridge, + our 12 status parts, + preload | 91–98 | −27 to −34 (−22 to −27%) | ≈ 2575 mm² (−9%) |
| B: as A, but keep the TIDA active bridge (FDN8601 ×4) | 103–110 | −15 to −22 | ≈ 2690 mm² (−5%) |
| Today minus the 12 eval leftovers (no redesign) | 113 | −12 | 2669 mm² |

Area estimates use this board's own footprint sizes per package. They also use the
LDT9055-51R suggested land pattern, 33.25 × 28.21 mm. That transformer is slightly
*larger* than the placed EFD25 T1702 (32.9 × 27.0 mm), so the transformer dominates
the PoE area and the board outline will not shrink.

Option B costs 12 parts but keeps about 1 W. In PMP22477, the 3.4-point gap between
end-to-end efficiency and efficiency after the bulk cap is about 1.5 W. Of that, about
1.2 W is two Schottky drops at 0.93 A, and about 0.26 W is the 0.3 Ω hotswap. The
active bridge is independent of the PD controller, so it carries over unchanged.

## 2. TPH/TPL/BT and the opto chain

The encoding is unchanged for the case we gate on. On TPS2373 (SLUSCD1C Table 2) and
on TPS23730 (SLVSER6B Table 8-2, SCDIS open), a Class 6 PD on a Type 3/4 PSE reads
**TPH LOW / TPL HIGH / BT LOW**. On our board that is TPH_N/TPL_N/BT_N = 0/1/0.

- **STM32 logic stays the same.** PB10/PB11/PB12 and the enforced 0/1/0 grant need no
  change. Class 5 and Class 6 encode identically on both parts. That does not matter
  here, because the PD requests Class 6 and only gets 4 class events for 51 W.
- **TPH/TPL electrical limits drop.** On TPS2373 these pins are rated to 100 V
  (abs max to RTN). On TPS23730 the recommended range is 0 to VCC and the abs max is
  19 V. Pulling up from TPS23730 VCC (today: POE_VCOUT via R1801/R1802 6.8 kΩ) stays
  inside that. At VCC 12–16 V, IF is 1.5–2.2 mA, under the 3 mA sink limit.
- **BT must move to VB.** TPS23730 BT is recommended 0 to VB (5 V), abs max 6.5 V. With
  the LED and resistor pulled up from VCC, the pin rises to about VCC − 0.9 V when off,
  which exceeds the abs max. Change R1803 to pull up from VB (pin 37) and set it to
  **2.2 kΩ** (IF ≈ 1.6 mA). 6.8 kΩ from 5 V gives only about 0.5 mA, and TLP293(GB)
  needs CTR ≥ 54% there to saturate against the 12 kΩ pull-up. PMP22477 does the same:
  BT opto U6 hangs off 5VREG through 4.99 kΩ, and TPH/TPL hang off VCC through 10 kΩ.
- **Timing changes slightly.** TPS2373 asserts the outputs about 24 ms after VC_IN.
  TPS23730 asserts them once DC-DC soft-start completes, and releases them on soft-stop,
  UVLO, inrush or thermal shutdown. Firmware already treats the grant as edge-sensitive
  and debounced, so it needs no change.
- **Adapter decode differs, but we don't use it.** On TPS2373, APD gives TPH low and
  TPL/BT open. On TPS23730, APD or PPD gives TPH and TPL both low, with BT unchanged.
  Our aux input is on the secondary, so APD is tied to RTN and PPD to VSS, and aux-only
  still reads 1/1/1.
- **PoE++ PSEs read 0/1/1.** For a pre-standard PoE++ PSE, TPS23730 sets BT HIGH, so
  firmware rejects it, as it should.

**SCDIS serial mode (SCDIS tied to VSS).** TPH goes high-Z and BT is disabled. TPL
becomes a 625 Hz (550–700 Hz) code:

| TPL in serial mode | Meaning |
|---|---|
| Static HIGH | Class 0–3 |
| Static LOW | Class 4 |
| 25% (24–26%) LOW | Class 5/6, Type 3/4 |
| 50% | PoE++ |
| 75% | Adapter on APD/PPD |

This saves U1801, U1803, R1801, R1803, R1811, R1813, C1801 and C1803: 8 parts, about
38 mm², and two MCU pins. It fails safe: an open opto reads static HIGH and a shorted
opto reads static LOW, and both mean no grant.

The cost is firmware. It needs a timer input capture on PB11 (confirm the STM32G0B1
alternate function) or ≥10 kHz sampling, and must accept only 25% duty across several
periods. C1802 (10 nF with 12 kΩ, 120 µs) rounds the 400 µs pulse; drop it to 1 nF.

Recommendation: keep parallel mode for this spin, and treat serial as a later
cost-down.

## 3. The 15.7 V light-load rise

### 3.1 What PMP22477 measures

TIDT259 §2.3, 48 V input, 25 °C, one board:

| I_OUT | 0 | 5 mA | 10 mA | 25 mA | 50 mA | 100 mA | 250 mA | 1 A | 3.25 A | 3.75 A |
|---|---|---|---|---|---|---|---|---|---|---|
| V_OUT | 15.69 V | 14.88 | 14.23 | 13.52 | 13.04 | 12.70 | 12.46 | 12.24 | 12.05 | 11.98 |

The two-port test (Table 2-4) shows 15.82 V at 0 A. Datasheet §8.3.7.3 only claims
about ±3% regulation for diode rectification "over a wide (< 5% to 100%)" range. Below
5% load the rise is expected behaviour, not a defect. With synchronous rectification
(PSRS open), the claim is ±1.5% over 0–100%.

### 3.2 Our light load

In the grant-wait and standby states, U701 (TPS56837) and U1901 (TPS54620) are
disabled. The 12 V bus then carries only U401 (always-on TPS62177 → STM32, INA226,
LEDs): roughly 3–8 mA at 12 V. Unpreloaded, the bus would sit at **about 14.9 V** for
the whole grant wait, and at up to 15.8 V with no load at all.

### 3.3 Every part on `ISO_12V_PSU` / `ISO_12V_BUS` / `ISO_12V`

| Part | Net | Limit | At 15.8 V | Source |
|---|---|---|---|---|
| U1901 TPS54620 (modem buck) PVIN/VIN | ISO_12V | **17 V recommended**, 20 V abs | Inside, **1.2 V margin**; release transients at light load not characterised | TPS54620 SLVS949, §6.3 / §6.1 |
| U701 TPS56837 (main 5 V) VIN | ISO_12V | 28 V recommended, 32 V abs | OK | TPS56837 §5.3 / §5.1 |
| U401 TPS62177 (always-on) VIN | ISO_12V | 28 V recommended, 30 V abs | OK | tps62175.pdf, Recommended Operating Conditions |
| U2101/U2102 LM74700-Q1 | AUX / PSU → BUS | 3.2–65 V operating | OK | LM74700-Q1 datasheet |
| Q2101/Q2102 CSD17577Q5A | same | V_DS 30 V | OK; Q2101 blocks ≤ 15.8 V reverse when aux is absent | CSD17577Q5A |
| U2103 INA226 IN+/IN−/VBUS | BUS / ISO_12V | 0–36 V common-mode and bus | OK | INA226 |
| C1905, C1906, C401, C703, C704 (10 µF CL31B106KBHNNNE) | ISO_12V | 50 V | OK. Samsung DC-bias data in repo: −66% at 12 V, −74% at 15 V | `reference/cl31b106kahnnn-characteristics.json` (same dielectric/size) |
| C2104, C2105 (10 µF, 50 V) | ISO_12V_BUS | 50 V | OK | — |
| C1907, C705, C2103 (100 nF, 25 V) | ISO_12V / PSU | 25 V | OK (63%) | — |
| D2101 SMBJ12CA | AUX_12V_IN only | — | Not on the PSU side; the LM74700 blocks reverse | — |
| PMP22477 output caps (8 × 22 µF 25 V 1210, 220 µF 25 V Al) | PSU | 25 V | OK | TIDMA49A |
| Documented `ISO_12V` maximum | — | **13.2 V** | **Violated** (14.9 V standby) | [main-5v-supply.md](main-5v-supply.md) |

Nothing exceeds a rating. The TPS54620 has only 1.2 V margin with an unknown overshoot
and spread (one board, 25 °C), and the 13.2 V design assumption is broken. Both need
the fix.

### 3.4 Interaction with the aux ORing (`aux-power`)

Today's TL431 loop keeps the PSU flat at 12.0 V. A higher aux simply carries the bus,
and the PSU idles at 12.0 V.

With PSR, the PSU curve falls monotonically with load, about 0.2 V/A between 0.5 and
3.75 A. That gives *stable droop sharing*, which TI tests as "two-port power sharing"
in TIDT259 Table 2-4. For an aux voltage between 12.0 and 15.7 V, the PSU settles at
the current where its curve meets V_aux:

- About 0.15–0.2 A at the 12.6 V aux maximum.
- Almost all of the load at 12.0 V.

This is not hunting, but the PoE share is uncontrolled. PMP22477's 56-part power-limit
circuit exists so that share never exceeds the granted Type 1/2/3 power. Without it:

- Firmware must never bypass the grant gate on aux while PoE is present with a grant
  other than 0/1/0, or must disable loads above that grant.
- Add this to the firmware rule in [hardware/README.md](../hardware/README.md).

### 3.5 Fix

| Fix | Parts | Light-load V | Loss at 3.3 A | Idle loss | Verdict |
|---|---:|---|---|---|---|
| **470 Ω, 1 W, 2512 on `ISO_12V_PSU`** (before Q2102) | +1 | ≈ 13.4 V (28 mA on the curve) | 0.31 W | 0.38 W | **Recommended.** TPS54620 gets 3.6 V margin. Raise the documented maximum to 14 V |
| 270 Ω, 1 W, 2512 | +1 | ≈ 13.05 V (48 mA) | 0.53 W | 0.63 W | Use if the 13.2 V figure must stand |
| TL431 + pass transistor + 100 Ω series resistor, clamping at 13.0 V | +5 | ≤ 13.0 V | 0 above ~50 mA load | ≤ 0.65 W | Use if the 0.3 W at full load matters |
| Synchronous rectifier (e.g. UCC24612 + FET), PSRS open | +5–7 | ±1.5%, 0–100% (datasheet claim) | Saves most of the D11 conduction loss (estimated 1–1.5 W at 3.3 A) | 0 | Root-cause fix, but leaves the tested reference design |

The preload sits on the PSU side, so it also keeps VCC alive from the bias winding. The
datasheet describes light-load VCC droop for diode-rectified flybacks in §8.3.7.1.

## 4. Transformer, efficiency, stock, lifecycle

**Transformer.** PSR needs a bias winding tightly coupled to the secondary. The
±3% claim holds "with a correctly designed power transformer". LDT9055-51R (LinkCom
datasheet RevA):

- 55 µH ±7% primary, 0.6 µH max leakage
- Np:Ns = 2.33:1 and Np:Naux = 2.33:1 (aux 12 V / 20 mA)
- 34–57 V input, 250 kHz, 12 V / 4 A output
- Hipot 1500 Vac for 2 s
- Body 26.0 × 31.5 mm, 14.5 mm maximum height
- −40 to +125 °C

The current T1702 (Würth 750317065, EFD25, 30 µH) is wound for the LM5155 design and is
not interchangeable. Before release:

- Confirm the isolation rating against 802.3 / IEC 62368-1. The 2 s hipot is a
  production test, not a type rating.
- Confirm the 14.5 mm height fits the enclosure.

Sourcing: no DigiKey result for LDT9055-51R, 750320319 or PS21-212 (2026-11-22), and
no distributor stock found. This is the gating item. Ask TI E2E and Würth about
orderability. Another option is a catalog PoE flyback with an aux winding (for example
the Coilcraft POE-series), checked with TI's TPS23730 design calculator. That option is
not evaluated here.

**Efficiency at 3.3 A** (TIDT259 §2.3, 48 V, 3.25 A row):

- 87.7% end-to-end, including the diode bridge and hotswap: P_in 44.65 W for 39.15 W
  out.
- 91.1% measured from the bulk cap.

The planning envelope in [power-and-cost.md](power-and-cost.md) assumes 85% isolated
efficiency plus 1 W, which gives 47.50 W at the PD. With the PMP22477 figure:

`35.57 / 0.90 / 0.877 = 45.07 W` at the PD. That leaves 5.9 W headroom under 51 W,
against 3.5 W today, and about 7 W with option B's active bridge.

At 3.75 A, PMP22477 draws 51.4 W, which is over the Class 6 limit. That is why TI adds
the power limiter. Our 3.3 A allocation does not reach it.

TIDA-050023 efficiency is not in the repo, so a like-for-like delta is not given.

**Stock and lifecycle** (2026-11-22, not reservations). DigiKey figures are from cached
regional pages. LCSC figures are from the tscircuit JLC parts index
(`jlcsearch.tscircuit.com/api/search`), which mirrors the LCSC catalogue with some lag.

| Part | Status | DigiKey | LCSC (tscircuit index) |
|---|---|---|---|
| TPS23730RMTR | TI: **ACTIVE** | 13280037: ~5,000–6,000, $4.41 (1) → $2.41 (3k reel), 18-week factory lead | C3189530: no stock listed, $4.23 (an earlier cached LCSC page showed 10–42 pcs) |
| TPS2373-3RGWR (incumbent PD) | — | not checked | C2860885: **4 pcs**, $3.71 |
| LM51551QDSSRQ1 (incumbent flyback) | — | not checked | C2860796: **2 pcs**, $1.52 |
| TLP293(GB-TPL,E) (grant optos, kept) | — | — | C77656: 39,845, $0.16 |
| FDMS86252 (primary FET, both designs) | already on BOM | not checked | Exact part not indexed; only FDMS86252L (logic-level variant, C606108, 2,313) |
| CSD17577Q5A / LM74700QDBVRQ1 (aux ORing, unchanged) | — | — | C475504: 757, $0.52 / C2941042: 8,790, $1.06 |
| LDT9055-51R / 750320319 / PS21-212 (PMP22477 T2) | unknown | not found | not indexed |
| Würth 750317065 (incumbent T1702), FSV1060V, SBRT20U60, B2100 | — | not checked | not indexed |

At LCSC, the incumbent TPS2373-3 + LM51551-Q1 pair is no better stocked than
TPS23730, so JLC stock does not favour either design. Both need a pre-order or
consigned parts. The flyback transformer is a non-LCSC part in both designs.

## 5. What must be re-verified

**Checks** — line numbers refer to [check_appliance_capture.py](../hardware/tools/check_appliance_capture.py):

- L33: component count `843`.
- L39: `counts['U1701']=21`. TPS23730 is a 45-pin VQFN plus thermal pad.
- L91–93: the U1701 pin map.
  - POE_VCIN, POE_VCOUT, POE_UVLO and POE_AMPS_CTL do not exist on TPS23730. Its
    pins are RTN 7–9, VSS 27–28, VDD 23, DEN 24, CLSA 21, CLSB 20, REF 17, VCC 42,
    VB 37 and others.
  - R1723 becomes 25.5 kΩ (pin table) instead of CRCW060324K9FKEA.
  - CLSA/CLSB change from 63.4/249 Ω to 32/130 Ω (Table 8-1; PMP22477 uses
    31.6/130 Ω).
- L94–96: the TPH/TPL/BT loop. Add an assertion that the BT LED resistor ties to VB.
- L125: the `ISO_12V_PSU` membership set (C1727, J1711, L1708, R1753, TP1719).
- L146–157: the TIDA golden-partition proof.
  - The flyback golden goes.
  - PMP22477 exists only as Altium/PDF, so there is no native partition source. A
    hand-entered netlist would have to replace it.
  - The input golden survives only with option B.
- Footprint/pad-parity block, `footprint-policy.json` (U1701 L474, T1702 L540, and
  every new ref), `check_footprint_reviews`, `check_model_reviews` and
  `check_step_models`. New packages: RMT0045A VQFN-45, TO-277A, LDT9055 land,
  Panasonic radial G, 744273501.
- Full ERC with zero violations.

**Generators and layout:**

- `build_poe.py`, `build_poe_pd.py`, `build_poe_status.py` (net renames). Per the
  native-edit rule, patch natively; don't regenerate.
- [place_board.py](../hardware/tools/place_board.py) L139 `prim_nets` regex, and the
  primary/secondary creepage partition.
- `sync_board.py` and `check_board_sync.py`.
- Flyback placement from 997fb5e and cff4aee is redone.
- `reference/tida-import/`, `imported-model-sources.json`.
- [supervisor-appliance-assignment.csv](../hardware/pinmaps/supervisor-appliance-assignment.csv)
  rows 6–8 cite TPS2373. Add the PB11 timer alternate function if serial mode is
  adopted.

**Docs:**

- [power-and-cost.md](power-and-cost.md): the 85% assumption, the Class 6 headroom and
  the TPS2373 links.
- [schematic-completion.md](schematic-completion.md): the TIDA-050023 retained-parts
  claim.
- [hardware/README.md](../hardware/README.md): `ISO_12V_PSU`, the aux/grant firmware
  rule (§3.4) and the release holds.
- [main-5v-supply.md](main-5v-supply.md): the 13.2 V maximum.
- [decoupling-review.md](decoupling-review.md): C1743/C1745 TIDA references and the
  flyback output caps.
- [footprint-audit.md](footprint-audit.md): the TPS2373 package.
- [qualification-status.md](qualification-status.md): the PoE row.
- [architecture.md](architecture.md): the bridge description.

**Bench work the swap adds:**

- Light-load and no-load V_OUT over −40 to +85 °C, with and without the preload.
- Load release from 3.3 A to the standby load, measured at the TPS54620 VIN.
- Grant timing and debounce on a real Type 3 PSE.
- Droop sharing with aux at 12.0 and 12.6 V.
- Isolation and hipot of the chosen transformer.

## Sources

- TPS23730 datasheet, SLVSER6B (Nov 2020): <https://www.ti.com/lit/ds/symlink/tps23730.pdf>. Product page (ACTIVE): <https://www.ti.com/product/TPS23730>
- PMP22477: <https://www.ti.com/tool/PMP22477>. Test report TIDT259 (Mar 2022): <https://www.ti.com/lit/pdf/tidt259>. Schematic TIDMA48A and BOM TIDMA49A (Rev D, 3/5/2024): <https://www.ti.com/lit/pdf/tidma48a>, <https://www.ti.com/lit/pdf/tidma49a>
- LinkCom LDT9055-51R spec (via TI E2E): <https://e2e.ti.com/cfs-file/__key/communityserver-discussions-components-files/196/LDT9055_2D00_51R.pdf>
- TPS2373 SLUSCD1C, TPS54620, TPS56837, TPS62175/7: local copies in `hardware/reference/`
- Stock: DigiKey TPS23730RMTR <https://www.digikey.com/en/products/detail/texas-instruments/TPS23730RMTR/13280037>. LCSC C3189530 <https://lcsc.com/product-detail/Power-Over-Ethernet-PoE-Controllers_Texas-Instruments-TPS23730RMTR_C3189530.html>. tscircuit JLC parts index: <https://jlcsearch.tscircuit.com/api/search?q=C3189530>
