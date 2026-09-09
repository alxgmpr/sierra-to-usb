> Historical evidence from superseded designs. See the [current full adapter](../full-adapter/README.md). Circuit status and artifact paths below refer to the historical checkpoint, not the replacement.

# Eaton supercapacitor selection

2026-09-04. Provisional component choice for circuit development, not a validated complete power system.

## Preferred prototype bank

Use **two Eaton HV1020-2R7505-R cells in series**. Each is 5 F, 2.7 V, maximum initial ESR 40 milliohms. The pair is nominally **2.5 F, 5.4 V and 80 milliohms**, excluding wiring and switch resistance. Use a midpoint connection for balancing and individual-cell overvoltage protection. Charge below the combined rating; the working setpoint and hot-temperature derating depend on the chosen controller.

DigiKey product number: **283-HV1020-2R7505-R-ND**. Authenticated US/USD Product Search API returned **145 cells directly stocked**, MOQ 1 and **$2.43 each**, or **$4.86 for the pair**, on this review date. Price excludes balancing/charging circuitry, tax and shipping. No order placed.

Eaton specifies each cell at 5.6 A pulse current using a one-second discharge from rated voltage to half rated voltage, and 2.3 A continuous current at 15 C temperature rise. These conditions are not a guaranteed modem hold-up specification. A 3 A bank pulse initially loses 0.24 V across 80 milliohms and dissipates 0.72 W. Required bank current depends on the power-path topology, not directly on modem output current.

At nominal capacitance, an illustrative 4.8 V to 4.0 V bank excursion contains 8.8 J before ESR/converter losses. At -10% capacitance tolerance it contains 7.92 J. This is an energy estimate only: terminal sag, converter minimum voltage and cell imbalance can cause an earlier cutoff. The 5.4 V rating is not a request to boost a laptop port to 5.4 V.

Each upright cell needs a **10.5 mm maximum body diameter, 22.3 mm maximum body height, 5.0 mm lead pitch, and 0.60 mm nominal lead diameter** per Eaton's HV drawing. Formed-lead horizontal mounting could reduce height but must be deliberately dimensioned and supported. Do not treat this pair as a footprint-compatible replacement for the PHV pack.

## Alternatives from the user's export

| Configuration | Nominal bank | Relevant bank ESR | Live component cost | Direct DigiKey stock | Tradeoff |
| --- | --- | --- | --- | --- | --- |
| 2 x HV1020-2R7505-R | 2.5 F / 5.4 V | 80 mOhm, manufacturer initial/DC data | $4.86 | 145 cells | Preferred balance of size, cost and pulse resistance; separate balancing needed. |
| 2 x TVH1220-3R0106-R | 5 F / 6 V | **136 mOhm DC**, 90 mOhm at 1 kHz | $2.60 | 2,393 cells | Cheapest strong candidate; larger 12.5 mm nominal diameter bodies and higher pulse resistance. |
| 2 x TVH1020-3R0705-R | 3.5 F / 6 V | **210 mOhm DC**, 140 mOhm at 1 kHz | $2.32 | 3,980 cells | Smaller than TVH1220 but greater voltage drop. |
| PHV-5R4V255-R | 2.5 F / 5.4 V | 80 mOhm at 100 Hz; Eaton product page also lists DC 80 mOhm | $9.92 | 99 packs | Cheaper packaged alternative if 23 mm upright height fits. |
| PHV-5R4H255-R | 2.5 F / 5.4 V | 80 mOhm at 100 Hz; Eaton product page also lists DC 80 mOhm | $16.73 | 20 packs | Initial pick; factory horizontal package, 23 x 21.3 x 11 mm. |
| PTV-6R0V305-R | 3 F / 6 V | CSV lists 70 mOhm; manufacturer transient data still to audit | $9.03 | 846 packs | Promising packaged alternative with extra voltage headroom; not yet fully verified. |

Prices and direct stock above were checked through the authenticated DigiKey API, not taken solely from the CSV. The initial PHV horizontal search also returned marketplace stock; the table deliberately uses the direct supplier variation. API snapshots without secrets are under `tmp/eaton*-stock.json`.

The lower-priced TVH range is real, but catalog ESR fields are not comparable without their measurement frequency. Eaton's TVH datasheet lists 68 mOhm DC versus 45 mOhm at 1 kHz for TVH1220, and 105 versus 70 mOhm for TVH1020. Two series cells add resistance while halving capacitance. TVH pulse ratings are also conditional on a large voltage excursion; evaluate terminal voltage and heating for the actual modem waveform.

The HSH1020-3R8856-R hybrid in the CSV is inexpensive and has 85 F, but its **DC ESR is 250 mOhm**, versus the exported 120 mOhm at 1 kHz. Eaton gives 0.425 A rated charge/discharge current and a conditional 3.5 A maximum discharge rating. HSH cells have a 2.5 V minimum rated operating voltage and 2.2 V absolute minimum allowed operating voltage. Their large capacitance does not make them a direct substitute for a low-resistance 5 V bank; they need different charging/undervoltage management.

## Power-path requirements carried into capture

USB-C source-current detection/PD -> protected total input-current limit -> managed charger/power path -> modem regulator. The power-path controller must use the capacitor bank to supplement a live but current-limited USB source, and recharge only from unused input capacity. Include cell balancing, individual-cell protection, reverse-current blocking, controlled startup and a modem-off state until the system is ready. Retain local ceramic/polymer decoupling for fast load steps. No final controller selected yet.

## Sources

- User export: `/Users/alex/Downloads/electric_double_layer_capacitors__edlc___supercapacitors.csv` (read only).
- [DigiKey HV1020](https://www.digikey.com/en/products/detail/eaton-electronics-division/HV1020-2R7505-R/3878072).
- [Eaton HV datasheet, specifications page 2 and dimensions page 3](https://www.eaton.com/content/dam/eaton/products/electronic-components/resources/data-sheet/eaton-hv-supercapacitors-cylindrical-cells-data-sheet.pdf).
- [Eaton HV1020 product data](https://www.eaton.com/gb/en-gb/skuPage.HV1020-2R7505-R.html).
- [Eaton TVH datasheet, specifications page 2](https://www.eaton.com/content/dam/eaton/products/electronic-components/resources/data-sheet/eaton-tvh-supercapacitors-cylindrical-cells-high-density-data-sheet-elx1539-en.pdf).
- [Eaton HSH datasheet, specifications page 2](https://www.eaton.com/content/dam/eaton/products/electronic-components/resources/data-sheet/eaton-hsh-supercapacitors-hybrid-high-density-cells-data-sheet-elx1491-en.pdf).
- [Eaton PHV datasheet](https://www.eaton.com/content/dam/eaton/products/electronic-components/resources/data-sheet/eaton-phv-supercapacitors-cylindrical-pack-data-sheet.pdf).
- [Eaton PHV horizontal product data](https://www.eaton.com/fr/fr-fr/skuPage.PHV-5R4H255-R.html).

## 2026-09-04 buffered-power capture update

The initial capacitor-only state is superseded by the candidate power capture documented in [power-design-review.md](power-design-review.md). LTC3128 explicitly supports live-source pulsed loads, but aged/low-input margins fail some test envelopes. The proposed bank setting is 4.06 V, not its 5.4 V summed rating. RM551E requirements and all-modem compatibility remain unverified. This is not a released power system.
