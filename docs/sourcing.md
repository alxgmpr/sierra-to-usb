# Sourcing — pinned gate parts (Task 1)

**Date checked:** 2026-07-14. All stock/price figures are snapshots (LCSC live pages / jlcsearch API mirror / DigiKey product pages fetched that day) — **re-verify at order time**, especially anything flagged low-stock. LCSC "C" numbers below were read from real LCSC listings, not inferred. Price class: `$` <0.50, `$$` 0.50–2, `$$$` 2–10 per unit at qty 1.

**Gate result: NOT blocked.** A 2.5G+PoE magjack is obtainable (Bel 2250504-1, live stock seen at DigiKey — §2 row 1), so the STOP condition in the plan does not trigger.

## 1. JLC-assembled parts (MUST be LCSC)

| Part / function | MPN | Package | Distributor | LCSC # | Price class | Stock note (2026-07-14) |
|---|---|---|---|---|---|---|
| MCU | Raspberry Pi RP2040 | LQFN-56 (7×7) | LCSC | C2040 | $$ ($0.99@1 / $0.76@100) | 12,622 — confirmed live page. Don't confuse with RP2040-Zero *module* (C5350143). |
| QSPI flash | Winbond W25Q128JVSIQ | SOIC-8 208mil | LCSC | C97521 | $$$ ($2.64@1) | 23,976. Flagged as JLC **Basic** part via jlcsearch — reconfirm basic/extended in JLCPCB library at order. Cheaper extended listing C113767 (~$1.18, ~5.1k stock). |
| 2.5GbE NIC | Realtek RTL8125BG-CG | **QFN-48-EP (6×6)** | LCSC | C3013605 | $$$ ($4.44@1 / $2.93@100) | 4,662. Confirm KiCad footprint against QFN-48. |
| USB3 SS mux | TI HD3SS3220RNHR | WQFN-30-EP (2.5×4.5) | LCSC | C165155 | $$ ($1.89@1) | 2,387 — moderate stock, recheck at order. |
| USB2 2:1 mux | TI TS3USB221DRCR | VSON-10-EP (3×3) | LCSC | C324071 | $$ ($0.75@1) | 3,622. Alternates on LCSC: TS3USB221ARSER UQFN-10 1.5×2 (C128396, 5,855, $0.26); TS3USB221RSER (C130085, 2,117); TS3USB221ERSER (C129313, 3,292). **Pick DRC (VSON-10) for JLC assembly; RSE 1.5×2 UQFN is tiny but also fine for JLC.** |
| SIM 6-ch 2:1 mux | TI TS3A27518EPWR | **TSSOP-24** (not TSSOP-16 — brief's assumption corrected) | LCSC | C443721 | $$ ($0.90@1) | 6,272. QFN option: TS3A27518ERTWR WQFN-24-EP 4×4 (C2651937, 1,509, ~$0.71). TSSOP-24 → HAND-solder per plan Task 14 rule; QFN → JLC. |
| MFF2 eUICC eSIM | ST4SIM-200M | MFF2 (DFN-8) | **NOT ON LCSC** | — | — | **No LCSC listing exists for ST4SIM-200M** (confirmed by multiple searches). MFF2 alternatives found on LCSC are both **out of stock**: Hologram SIM-ST-MFF2 (C22416518), Truphone SIM-S-IO3-MFF2-2 (C5122390, DFN-8 5×6). ⚠️ **Action:** source ST4SIM-200M via Mouser/DigiKey/ST and hand-solder it (MFF2 = 8-pad DFN, iron-solderable), or use JLC parts consignment. Reclassify this line from JLC-assembled → HAND. Stock unverified — check at order time. |
| MHF4 SMT receptacle ×5 | TE CONMHF4-SMD-G-T | SMD MHF4 jack | LCSC | C18221168 | $$ ($0.89@1) | 1,580 (live page; API mirror disagreed — page taken as authoritative). Only true-MHF4 listing on LCSC. Fallback if it dries up: Hirose U.FL-R-SMT-1(80) (C88374, 293k stock, ~$0.10) — **only** if antenna jumpers are re-specced to U.FL; U.FL ≠ MHF4 mechanically. |
| Qwiic JST-SH-4 | JST BM04B-SRSS-TB(LF)(SN) | SMT top-entry, 1 mm | LCSC | C160390 | $ ($0.21@1) | 23,522. Standard Qwiic/STEMMA-QT connector. |
| M.2 Key-B socket | LOTES APCI0105-P001A | SMD 0.5 mm, M.2 B-key, **67P** | LCSC | C841658 | $$ ($0.70@1) | **127 in stock — thin; recheck/buy early.** Note: every real B-key socket is sold as **67-pin** (75 edge-pad spec minus 8 pads at the B notch) — the plan's "75-pin" wording describes the module edge, not the socket. **4.2 mm mating height not stated in LCSC parametrics — pull the LOTES datasheet before footprint commit.** Backups: UMAX 91302-42-067R2B (C879639, 269), Foxconn AS0BC21-S30BB-7H (C2761344, 60). |
| M.2 standoff + screw | Sinhoo SMTSO2530CTJ | SMT M2.5, 3 mm H | LCSC | C2915631 | $ ($0.08@5) | 5,260. Generic SMT standoff, not M.2-specific — verify height matches socket stack (H4.2 socket → 4.2 mm nominal card height; 3 mm standoff suits single-sided-bottom cards — check module thickness). |

## 2. Hand-soldered parts (any distributor; LCSC preferred)

| Part / function | MPN | Package | Distributor | LCSC # | Price class | Stock note (2026-07-14) |
|---|---|---|---|---|---|---|
| **2.5G+PoE magjack (GATE)** | **Bel 2250504-1** | RJ45 ICM, 2.5GBASE-T, 100 W 4-pair PoE (≥802.3bt) | **DigiKey** | — | $$$ ($9.88@1) | **57 in stock — live number seen on DigiKey page.** Bel press release confirms single-port 2.5GBASE-T/100 W part. Family siblings 0826-1X1T-HS-F / -KH-F / 2250506-1 were 0-stock. Second source: LINK-PP **LPJTP95282-8CNL** (2.5G, PoE++/bt, tab-up) ~$4.98 on LINK-PP's own store (l-p.com, "15.2K sold") — not found on LCSC or an independent distributor; stock unverified — check at order time. |
| **PoE flyback/forward transformer (GATE)** | **Würth 750313355** (WE-PoE++, SMT, 1500 Vrms) | SMT_XFRMR_29MM08_23MM1 | **DigiKey** | — | $$$ ($7.19@1, $5.23@1.1k) | **1,074 in stock, Active — fetched live from DigiKey.** This is T2 of TI's TPS23730EVM-093 (12 V / 5 A). TI BOM lists alternate: **Linkcom LDT8627-50R**. See Decision (a) for topology note. |
| PD sink controller | WCH CH224K | **ESSOP-10** (not SOP-8 — verify footprint) | LCSC | C970725 | $ ($0.49@1) | 14,053 — live page. |
| 12 V→3.3 V buck | TI TPS565201DDCR | TSOT-23-6 | LCSC | C327676 | $ ($0.13@1) | 8,893. |
| LDO 3.3 V ×2 | Diodes AP2112K-3.3TRG1 | SOT-25 | LCSC | C51118 | $ ($0.13@1) | 41,270. |
| LDO 1.8 V | Diodes AP2112K-1.8TRG1 | SOT-25 | LCSC | C176944 | $ ($0.15@1) | 12,170. |
| Current monitor ×2 | TI INA226AIDGSR | MSOP-10 | LCSC | C49851 | $$ ($0.60@1) | 42,750. |
| Temp sensor ×2 | TI TMP112AIDRLR | SOT-563 | LCSC | C28927 | $ ($0.23@1) | 26,572. |
| RGB LED | OPSCO SK6805-EC15 | 1.5×1.5 SMD-4P | LCSC | C2890035 | $ ($0.09@1) | 80,300 — live page. ⚠️ Datasheet Vdd min is 3.7 V; 3.3 V operation is standard practice (Adafruit ships this chip as 3.3–5 V) but technically below datasheet floor — noted for design docs. |
| USB3 ESD ×3 | TI TPD4EUSB30DQAR | DFN-2510-10 | LCSC | C558427 | $ ($0.05@1) | 11,595. |
| USB2/LV ESD | TI TPD4E05U06DQAR | USON-10 (1×2.5) | LCSC | C138714 | $ ($0.06@1) | 107,192. |
| CC/SIM ESD ×2 | TI TPD4S009DBVR | SOT-23-6 | LCSC | C88032 | $ ($0.08@1) | 4,687. |
| TVS 13 V | SMAJ13A | DO-214AC (SMA) | LCSC | C19077533 | $ | 43,157 (JLC-preferred listing). |
| TVS 58 V | SMAJ58A | DO-214AC (SMA) | LCSC | C19077554 | $ | 11,842 (JLC-preferred listing). |
| PoE bridge ×2 | MB10S | MBS SMD | LCSC | C2488 | $ ($0.02) | 230,909 — JLC basic, lowest-risk. |
| N-FET ×~8 | 2N7002 | SOT-23 | LCSC | C8545 | $ ($0.01) | 1.84 M — JLC basic. |
| USB-C receptacle ×3 | HRO (Korean Hroparts) TYPE-C-31-M-12 | 16-pin mid-mount, hybrid SMD/TH tabs | LCSC | C165948 | $ ($0.17@1) | 115k+. **16-pin = USB2+PD only, no SS pins.** Fine for J2 (PD) and J3 (debug). ⚠️ **J1 (data) carries USB3 SuperSpeed — it needs a 24-pin receptacle.** Pin a 24-pin part (e.g. HRO TYPE-C-31-M-17 class / GCT USB4085) at capture time; stock unverified — check at order time. |
| Nano-SIM push-push ×2 | JXTCONN CSIM-H137-7P | SMD push-push, 1.37 mm H | LCSC | C42420236 | $ ($0.25) | **605 — thin; fine for qty 2, recheck at order.** Backup: CSIM-113-7P (C42420249, 675). |
| SMA edge jack ×5 | BWSMA-KE-Z001 | TH board-edge SMA | LCSC | C496549 | $ ($0.36@1) | 94,740. |
| DIP-4 switch | DSWB04LHGET | THT 2.54 mm | LCSC | C99418 | $ ($0.17) | 43,189. |
| Slide switch | SK12D07VG4 (THT) / MSK12C02 (SMT) | 8.7×4.4 / 8×2.8 | LCSC | C393937 / C431540 | $ | 49,718 / 98,963. |
| 470 µF 6.3 V polymer ×2 | Panasonic 6TPE470MI | 7343 SP-Cap | LCSC | C402828 | $$ ($1.45@1) | 8,795 — live page; 18 mΩ ESR confirmed. |
| 2.2 µH ≥5.6 A inductor | Sunlord **SWPA8040S2R2MT** (or NT) | 8×8×4 shielded | LCSC | C36415 (MT) / C504645 (NT) | $ ($0.09) | MT 959 / NT 22 in stock. **Datasheet-verified: Isat 7.10 A max-rating / Irms 5.15 A max-rating (5.60 A typ)** — clears the ≥5.6 A Isat requirement with margin (the 6045 size the plan warns about is indeed undersized). Order MT variant; low-ish stock, buy early. |
| Ideal-diode OR ctrl ×2 | TI **LM5050MKX-1/NOPB** | TSOT-23-6 | DigiKey | — | $$$ ($2.21@1) | **16,526 in stock (DigiKey, live).** Note: the plain LM5050MK-1/NOPB SKU showed 0 stock/16-wk lead — order the MKX (tape/reel cut) SKU. |
| OR-path N-FET ×2 | STD30NF03LT (ST) or NTD20N03L27 (onsemi) or DMC3032LSD (Diodes) | DPAK / SO-8 | DigiKey/Mouser | — | $ | 30 V, low-Rds, ≫3 A — all comfortably rated. Stock unverified — check at order time; any 30 V+ / <20 mΩ N-FET in DPAK/SO-8 works here. |
| PoE PD+DC/DC controller | TI **TPS23730RMTR** | VQFN-45 (7×5) | DigiKey | — | $$$ ($4.95@1) | **3,569 in stock (DigiKey, live).** See Decision (a). (Rejected alt TPS2373-4RGWR also real: 1,729 in stock, $3.40.) |

## 3. Decisions

### (a) PoE controller: **TPS23730** (TPS23730RMTR) — chosen over TPS2373-4 + separate PWM controller

Driven by transformer availability, exactly as the plan requires: the TI-specified 12 V transformer for the TPS23730's own EVM (TPS23730EVM-093, 12 V / 5 A) is Würth **750313355**, a live catalog part with **1,074 units in stock at DigiKey** at check time, and TI's EVM BOM even names a drop-in alternate (Linkcom LDT8627-50R) — so the integrated-controller route has a proven, purchasable magnetics path with a published schematic/BOM to copy at Class-appropriate power. The TPS2373-4 route would need the *same class* of 54 V→12 V isolated transformer plus an additional PWM controller IC and its support parts, i.e. it only adds BOM lines without easing the one genuinely scarce component; it would only win if no TPS23730-matched transformer were stocked, which is not the case. **Topology note for Task 4:** the stocked 12 V TI designs (EVM-093, PMP23253, PMP23365) are **active-clamp forward with opto feedback** (EVM BOM includes TCMT1107 + TL431), not the "no-opto flyback" the spec §4 sketches; TI's true no-opto 12 V flyback (PMP22477, 12 V/3.8 A) uses a transformer that is *not* a catalog part (matching TI E2E "trouble sourcing" threads). Recommendation carried to schematic capture: follow **EVM-093 verbatim** (add the opto + TL431 — 3 cheap parts) rather than chase a custom flyback transformer; this is a deviation from the spec's "no-opto" wording and is flagged per Global Constraints rather than improvised silently.

### (b) Ideal-diode OR: **2× LM5050-1 (LM5050MKX-1/NOPB) + 2× discrete N-FET** — chosen over SM74611-class

LM5050-1 is a purpose-built high-side ideal-diode OR-ing controller: two of them (one per 12 V source, PD and PoE) each driving a cheap 30 V low-Rds N-FET give true diode-emulation OR-ing at 12 V/3 A with millivolt-class drop, and the controller is deeply stocked (16,526 at DigiKey) in a hand-solderable TSOT-23-6, with commodity DPAK/SO-8 FETs that have dozens of substitutes. The alternatives lose on the facts found: **SM74611** is actually a TI (not Diodes Inc) single-channel *photovoltaic bypass* smart diode in TO-263 — it would still take two devices, costs more (~$5.95 each), and its solar-bypass duty profile isn't intended for continuous supply OR-ing; **LM66200** (true dual, integrated FETs) tops out at 5.5 V — rules itself out at 12 V; **TPS2120/TPS2121** power muxes cover 22 V/4.5 A in one chip but are seamless *switchover muxes* rather than diode-ORs and ship in DSBGA (YFP) — not hand-solderable, violating the assembly split; **LTC4227** (genuine dual ideal-diode controller, one package + 2 FETs) is the closest single-IC competitor but live stock was not confirmed during research. If a one-package solution is later preferred, re-check LTC4227 stock; the default remains 2× LM5050-1 + 2× FET.

## 4. Carry-forward flags (consumed by Tasks 2/6/7/11/14)

1. **eSIM (U12):** ST4SIM-200M is not on LCSC → moves from JLC-assembled to hand-soldered (MFF2 pads are iron-friendly) or JLC consignment; source from Mouser/DigiKey/ST, stock unverified.
2. **M.2 socket:** real B-key sockets are 67-pin (spec's "75-pin" counts module edge pads); LOTES C841658 stock is thin (127) and its 4.2 mm height needs datasheet confirmation before Task 14 footprint lock.
3. **TS3A27518E** is TSSOP-24 or WQFN-24 — plan's TSSOP-16 note is wrong; choose QFN→JLC or TSSOP→hand at Task 14.
4. **CH224K is ESSOP-10**, not SOP-8 — footprint check at Task 14.
5. **USB-C J1 (data)** needs a 24-pin (full USB3) receptacle — the pinned TYPE-C-31-M-12 is 16-pin and only suits J2/J3.
6. **SK6805-EC15 at 3.3 V** is below its 3.7 V datasheet floor (works in practice; note in design docs).
7. Low-stock watch list: Bel magjack (57), Würth 750313355 (1,074), MHF4 (1,580), M.2 socket (127), nano-SIM (605), SWPA8040S2R2MT (959), HD3SS3220 (2,387) — order early or re-verify at BOM lock.
8. LINK-PP LPJTP95282-8CNL (magjack second source) needs verification through an independent distributor before relying on it.
