# Decoupling and bulk capacitor review

## Applied 2026-11-22

Section 4 consolidation, plus the rail fixes, gives 48 → 36 capacitor MPNs. Two parts are
deliberately kept:

- C1104 keeps 4.7 uF, because eMMC VDDI needs ≥ 2.2 uF (RK3566 guide 2.1.10).
- C1743, the TIDA-050023 flyback COMP cap, keeps its 5% part.

Rail fixes:

- MODEM_VCC: C2031–C2035, 100 nF → 1 uF 0603.
- ETH_0V95: C1620–C1622, 100 nF → 1 uF 0603.
- VDD_CPU: eight new 1 uF 0402 caps (C847–C854) on the bottom at the CPU balls.
- VDD_LOGIC, VDD_GPU, VDD_NPU: 4, 6 and 6 new 1 uF 0402 caps (C855–C870) at their balls.

Value text and the Voltage Rating, Dielectric, Tolerance and LCSC fields are now normalized for every
instance of the kept MPNs. The RAM bypass plan now holds 1 uF. Its check requires a voltage rating of at
least 3× the rail, replacing the old ≥ 25 V rule.

The 100 nF → 1 uF change on the RK3566, RAM and eMMC bypass caps departs from Rockchip's
reference values (section 6). The model shows it lowers impedance on every BGA rail.

Model on the consolidated netlist (377 caps), worst |Z| in the valid band above 10 MHz:

| Rail | Target | Before | After |
|---|---|---|---|
| VDD_CPU | 17 mΩ | 50.3* | 13.5 |
| MODEM_VCC | 50 mΩ | 256* (4.4 MHz) | 37 (1.4 MHz peak) |
| ETH_0V95 | 71 mΩ | 77.2* | 31.7 |
| VDD_DDR_1V1 | 66 mΩ | 22.6 | 12.5 |
| VDD_DDR_0V6 | 60 mΩ | 16.9 | 10.5 |
| VDD_LOGIC | 36 mΩ | 46.4* | 28.1 (+4× 1 uF 0402, C855–C858) |
| VDD_GPU | 36 mΩ | 69.2* | 28.1 (+6×, C859–C864) |
| VDD_NPU | 45 mΩ | 102* | 32.3 (+6×, C865–C870) |

Counts were chosen from a sweep, for about 20% margin under each target. All 24 added 0402s are
on the bottom side at their rail's balls. Load steps are still assumed (section 6).

## Review of the 023fd93 netlist

Model: [hardware/tools/pdn_model.py](../hardware/tools/pdn_model.py). Export a netlist with
`kicad-cli sch export netlist --format kicadxml`, then run
`uv run --with numpy python hardware/tools/pdn_model.py NETLIST.xml`. Sections 1–6 are the review
of the 023fd93 netlist (349 caps, 48 MPNs).

## 1. Classification (349 caps)

| Class | What | Examples |
|---|---|---|
| (a) IC-local decoupling | 0402 under RK3566/LPDDR4X/eMMC; 0603 at RTL8125, logic, MCU, modem | 82x CL05B104KB54PNC, 14x CL05B105KQ5NNNC, 8x CL05A475MP5NRNC, ~45x CL10B104KA8NNNC, 5x CL10A475KA8NQNC (ETH) |
| (b) Rail bulk / regulator in/out | the output banks are part of the loop design | 44x CL32B226KAJNNNE, 26x CL31B106KAHNNNE, 3x CL31B106KBHNNNE, C401 CL31B475KBHNNNE, 6SVPC220MV, PCV1E271, EEE-FK1J470P, PMIC LDO 1 uF banks |
| (c) Value set by the circuit | bootstrap C701/C1901 (TPS56837 §7.2.2.5 / TPS54620: 100 nF), soft start C702/C1908 47 nF, TPS54620 comp C1909/C1910, TPS259474 dV/dt C1911, SY8089 FF C959 100 pF, core FB filters 4x 1 uF, reset/PWRON/VDC RCs 100 nF (RK guide: 100 nF at reset), PMIC VREF/internal 1V8 1 uF, PCIe AC 4x 0201 100 nF (75–200 nF spec), modem USB AC 2x 100 nF, RTL8125 xtal 27 pF (datasheet), SIM 10 pF, RM520 RF bank 220/68/15/9.1/4.7 pF, ETH CT 4x 100 nF, TPS22965 CT 1 nF, PoE bridge 330 pF/1 nF, all TIDA-050023 flyback parts (snubber 100 pF/250 V, 3.3 nF, 3.9 nF C0G, UVLO 220 pF, 22 nF, COMP 47 nF, TL431 47 nF/100 pF, bias 2.2 uF, 1 uF 0805, 10 uF 1210 output), opto filters 10 nF, SARADC 1 nF |
| (d) Safety / isolation | across the PoE/Ethernet barrier | GR442QR73D102KW01L 1 nF/2 kV (Bob Smith), 2x 1812GC472KAT1A 4.7 nF/2 kV (primary-secondary), 4x C1608X7R2A103K 100 V on pair center taps, GRM32ER72A225KA35L 100 V, C0805/C2012 100 V |

## 2. Impedance model

Each capacitor is modelled as a series ESR + L + C(V). The banks come from the
netlist: every cap between a modelled rail and GND.

- **Samsung data (measured):** for CL10B104KA8, CL10B105KA8, CL31B106KAH,
  CL32B226KAJ, CL31B475KBH and CL31B225KBH, the model reads the archived JSON
  directly. It takes the DC-bias curve, ESL from the measured SRF (0.49, 0.43,
  1.03 and 1.08 nH) and ESR at SRF (19, 11, 5.0 and 3.4 mΩ).
- **Assumed parts:** 0402 parts use part L = 0.35 nH. ESR is 30, 12 and 6 mΩ for
  100 nF, 1 uF and 4.7 uF. Retained C for the 1 uF/6.3 V is 0.9 at 1.1 V and 0.8
  at 1.8 V. For the 4.7 uF/10 V X5R it is 0.8 and 0.65. CL31B106KBH is assumed to
  match KAH at 5 V or below and keep 0.5 at 12 V. The polymer is 220 uF, 15 mΩ,
  2 nH.
- **Mounting:** add 0.10 nH for 0402 under the BGA and 0.25 nH for 0603–1210.
  Total L comes to 0.45 nH (0402), 0.7 nH (0603) and 1.3 nH (1206/1210).
- **Constant ESR:** this gives the worst-case Q at anti-resonance. The
  sensitivity run (0402 mounting ×3, ESR ×0.5) is included below.
- **Not modelled:** VRM loop, plane capacitance, spreading inductance, and the
  path through the modem eFuse.
- **Where the model is valid:** from about the regulator crossover (~100 kHz) up
  to f_ceil = Z_t/(2π·L_load). L_load is the assumed ball/via/package loop
  inductance: 50 pH for core rails, 100 pH for DDR, 300 pH for analog and QFN
  loads, and 200–500 pH for connectors. f_ceil is about 50 MHz for VDD_CPU,
  about 100 MHz for DDR and 16–40 MHz for 5V, ETH and modem. Above it, board-cap
  value is irrelevant; on-package and on-die capacitance takes over.

Self-check (asserts): a single cap's |Z| minimum falls at 1/(2π√LC) and equals
ESR. N identical caps give exactly Z/N. The Samsung parse is checked against
nominal C and ESL. A 22 uF ‖ 100 nF pair gives exactly one anti-resonance
between the two SRFs. The netlist count is 349.

Targets: Z_t = V·tol/ΔI. The load steps are **assumed**; the RK356X Power
Consumption Test Report is not in the repo.

| Rail | V | ΔI | tol | Z_t |
|---|---|---|---|---|
| VDD_CPU | 1.0 V | 3 A | 5% | 17 mΩ |
| LOGIC, GPU | 0.9 V | 1.25 A | 5% | 36 mΩ |
| NPU | 0.9 V | 1 A | 5% | 45 mΩ |
| VDD2 | 1.1 V | 0.5 A | 3% | 66 mΩ |
| VDDQ | 0.6 V | 0.3 A | 3% | 60 mΩ |
| VCC_1V8 | 1.8 V | 0.3 A | 5% | 300 mΩ |
| 3V3_MAIN | 3.3 V | 1 A | 5% | 165 mΩ |
| ETH_0V95 | 0.95 V | 0.4 A | 3% | 71 mΩ |
| MODEM_VCC | 3.7 V | 2 A | 100 mV | 50 mΩ |
| 5V_MAIN | 5 V | 3 A | 3% | 50 mΩ |

### Results: worst |Z| in the valid band (mΩ; * = over target)

| Rail | Z_t | current | all 0402→1 uF | all 0402→100 nF | 10n/100n/1u decade split | notes |
|---|---|---|---|---|---|---|
| VDD_DDR_1V1 | 66 | 22.6 (peak 9.5 MHz) | **14.1** | 38.0 (7.9 MHz) | 15.8 (3 peaks: 4/18/58 MHz) | |
| VDD_DDR_0V6 | 60 | 16.9 (10.1 MHz) | **12.4** | 37.5 | 13.9 | |
| VCC_1V8 | 300 | 22.4 (5.8 MHz) | 17.1 | 61.8 | 23.1 | |
| VDD_LOGIC | 36 | 46.4* (>50 MHz) | 46.7* | 48.6* | 57.8* | 1–10 MHz rises 5.4→11.5 when 3x4.7u→1u (still < Z_t) |
| VDD_GPU | 36 | 69.2* | 69.9* | 68.3* | 155* | |
| VDD_CPU | 17 | **50.3*** (10–53 MHz) | — | — | — | no 0402 at all; +8x 1 uF 0402 → 13.5 |
| VDD_NPU | 45 | 102* (peak 18 MHz) | 104* | — | 159* | +3x 1 uF 0402 → 49 |
| ETH_0V95 | 71 | **77.2*** (12 MHz) | — | — | — | 0603 100n→1u: 31.7; or +2x 1 uF: 26 |
| MODEM_VCC | 50 | **256*** (4.4 MHz) | — | — | — | polymer ESL vs 5x100 nF. 100n→1u: 36.6. Adding 2x22 uF 1210 makes it worse (148) |
| 3V3_MAIN | 165 | 31.8 | 21.7 | | 31.6 | |
| 5V_MAIN | 50 | 15.1 | | | | |

The sensitivity run (0402 mounting ×3, ESR ×0.5) keeps the same ranking. On
VDD2 the current bank reaches 50.7 mΩ, all-1 uF 17.3 mΩ, all-100 nF 71 mΩ (over
target) and the decade split 31 mΩ.

## 3. Verdict on "stacking decades is a myth"

**Mostly right, for capacitors in the same package.** Above its SRF, an MLCC's
impedance is ωL, and L is set by package and mounting, not by value. So a 10 nF
0402 adds no high-frequency benefit over a 1 uF 0402. Swapping every 0402 on
each DDR rail for identical 1 uF parts lowers the worst-case |Z| by 26–45% and
removes the 9.5–10 MHz anti-resonance peak. A deliberate 10n/100n/1u split
creates 2–3 extra peaks and is worse than all-1 uF above 10 MHz (15.2 vs 12.5 mΩ
on VDD2).

**Where the claim is wrong:**

1. "Identical" alone does not help. Making every 0402 a 100 nF is the worst
   case (38 mΩ, peak at 7.9 MHz), because the real gap is between the bulk
   1206/1210 ESL and too little capacitance in the small packages. The rule is:
   identical parts, with the largest C the package allows at the rail voltage.
2. You still need a mix of packages. Bulk (1210, ~1.3 nH) carries the
   capacitance and low-ESL 0402s carry the count. Every peak found on this
   board is a bulk-ESL against small-cap-C resonance (DDR, ETH, NPU, GPU) or a
   polymer against 100 nF resonance (modem), not a decade-value effect.
3. Value still matters below SRF. On VDD_LOGIC, dropping 3x4.7 uF to 1 uF
   doubles |Z| at 1–10 MHz, though it stays under target.
4. Paralleling or series-stacking a common part to make odd values only makes
   sense for class (c) parts that tolerate it. No class (a) or (b) value on this
   board needs it.

## 4. Consolidation (48 → 34 MPNs firm, 33 conditional)

All swaps below keep the same footprint unless noted, so no layout change is needed.

| From | → To | Qty | Reason / check |
|---|---|---|---|
| CL05B104KB54PNC 100 nF 0402 | CL05B105KQ5NNNC 1 uF 0402 X7R 6.3 V | 82 | Same ESL with 10x the capacitance; the model shows it is lower or equal everywhere it matters. Rails are ≤1.8 V except 4 positions on 3V3_MAIN/VCC3V3_PMU (C811, C812, C817, C1434): 1.9x voltage margin and about 40% bias loss, acceptable for decoupling. Adds ~19 uF to the SY8089/BUCK3 output banks; both are internally compensated with a "≥22 uF" minimum. Check JLC basic status and price. |
| CL05A475MP5NRNC 4.7 uF 0402 X5R | CL05B105KQ5NNNC | 8 | Within target on LOGIC/GPU/DDR. It is also X7R rather than X5R, which suits the heat under the BGA. EMMC_VDDI (C1104): the ISSI datasheet gives no value, so confirm JEDEC/vendor CREG limits; keep 4.7 uF if 1 uF is outside them. |
| CL31B106KAHNNNE 10 uF/25 V 1206 | CL31B106KBHNNNE 10 uF/50 V 1206 | 26 | Pure duplicate. C1905/C1906 on ISO_12V are 25 V parts at 12 V (Samsung: −66%, about 3.4 uF), so moving them to 50 V fixes that. Regulator output banks (BUCK3 C902, BUCK4 C542, SY8089 C958/C1507) keep the same nominal value. Obtain Samsung's KBH bias/ESR curve to confirm it is ≥ KAH at ≤5 V. |
| CL31B475KBHNNNE 4.7 uF/50 V (C401) | CL31B106KBHNNNE | 1 | TPS62177 input cap; more capacitance is fine. About 5 uF at 12 V is expected, versus 3.4 uF now. |
| 06033D104KAT2A (C1718), 06033C104JAT2A (C1739) | CL10B104KA8NNNC | 2 | Same 25 V 0603, and X7R is at least as good as the X5R part. C1739 goes from 5% to 10% on a VCIN bypass, which is harmless. |
| 06033C473JAT2A (C1743 COMP), C1608X7R1H473K080AA (C1745 TL431) | CL10B473KB8NNNC | 2 | C1745 is spec-identical. C1743 tolerance goes from 5% to 10%, so re-check the flyback loop margin. |
| CL10B103KB8NNNC, GRM188R61H103KA01D | C1608X7R2A103K 10 nF/100 V | 5 | The 100 V part is already needed on the pair center taps. DC bias is negligible at 10 nF. |
| CL10B102KB8NNNC | C1608X7R2A102K 1 nF/100 V | 2 | Same as above. |
| GRM1885C1H101JA01D | CL10C101JB8NNNC | 2 | Identical spec: C0G, 50 V, 5%. |
| C0603C221J5GACTU | CL10C221JB8NNNC | 1 | Identical spec: C0G, 50 V, 5%. |
| C0805C104K1RACTU | C2012X7R2A104K125AA | 1 | Identical spec: 100 V X7R 0805. |
| (cond.) CL05C102JB5NNNC SARADC 1 nF 0402 (C820) | C1608X7R2A102K | 1 | Changes the footprint to 0603. Only do this if the part is not under the BGA. |

Optional, not recommended without a TIDA-050023 re-check: EMK107BB7225KA-T →
CL10A475KA8NQNC (LM51551 VCC/BIAS range is 1–4.7 uF), and GRM21BR71E105KA99L →
CL10B105KA8NNNC (0805→0603, larger bias loss at 12 V). Either brings the count to 31.

**Must not change:** everything in class (c) and (d) above. Also keep:

- Regulator output banks:
  - TPS56837 (5V_MAIN, ~177 uF nominal; Murata-based table, 1–10 parts)
  - MP2143
  - TPS62177 (10 uH / 22–200 uF table)
  - TPS54620
  - RK809 BUCK1/2 (>30 uF effective, per the RK guide)
  - TCS4525
- The modem 220 uF polymer.
- The flyback 270 uF and 10 uF 1210 output.
- The 47 uF PoE input.

Changes that do not reduce the line count but improve impedance:

- MODEM_VCC: 5x 100 nF → 1 uF 0603, or add 4x 1 uF. This cuts the 4.4 MHz peak
  from 256 to about 40 mΩ.
- RTL8125 rails: 100 nF → 1 uF 0603. ETH_0V95 drops from 77 to 32 mΩ.

Not modelled: the 4.7 uF 0603 parts on the ETH_ANALOG rails form LC filters
with beads, so keep them.

## 5. Field and text inconsistencies (same MPN)

- **CL32B226KAJNNNE:** 24 entries read "22uF / 25V" with an empty Voltage
  Rating field; 20 read "22uF" with the field set to 25V.
- **CL10B105KA8NNNC:** 19 read "1uF / 25V" and 7 read "1uF". The Voltage
  Rating field is empty on all 26.
- **CL10B104KA8NNNC:** values are split between "100nF / 25V" and "100nF", and
  the Voltage Rating field is empty on 8.
- **CL31B106KAHNNNE:** one entry reads "10uF / 25V".
- **CL10B473KB8NNNC:** one entry reads "47nF / 50V", with its voltage field empty.
- **Dielectric field:** missing on part of CL05B104KB54PNC (34 of 82),
  CL05A475MP5NRNC (1), CL10B102KB8NNNC (1) and CL31B106KAHNNNE (15).
- **4.7 uF part on the logic/GPU banks:** docs/schematic-completion.md §1657
  names CL10A475KA8NQNC 0603, but the netlist has CL05A475MP5NRNC 0402.

## 6. Open risks

- **VDD_CPU** has no local 0402 decoupling: only 5x 22 uF 1210 and 2x 4.7 uF 0603.
  It is about 3x over the assumed target above roughly 15 MHz. The RK guide says
  not to remove reference-schematic capacitors, so compare against NanoPi R3S
  sheet 3 or 15. VDD_GPU and VDD_NPU (1 small cap each) are also over target
  above about 20 MHz.
- **Load steps are assumed.** The RK356X Power Consumption Test Report and
  modem burst data are needed to fix Z_t.
- **Vendor guidance:** Rockchip asks for its reference values to be kept
  ("1 uF + 100 nF per PLL supply", values per the reference schematic). Changing
  100 nF to 1 uF is better physically but deviates from the reference; get
  agreement before doing it.
- **Model limits:**
  - The 0402 and KBH data are assumptions, not measurements.
  - ESR is held constant, so the peaks shown are upper bounds.
  - No spreading or plane model, and no VRM. Below about 100 kHz the regulator
    loop dominates, which is why VCCA_1V8 and VDDA_0V9 show high values at
    100 kHz.
  - MODEM_VCC leaves out the eFuse path to the 3x 22 uF upstream bank.
- **Isolation caps:** 1812GC472KAT1A is a 2 kV MLCC, not a Y-rated safety part.
  Confirm against the isolation and safety requirement.
