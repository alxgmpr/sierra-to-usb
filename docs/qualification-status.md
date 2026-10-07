# Block diagram and BOM qualification status

Checked 2026-09-29 against the active three-sheet KiCad recovery schematic and
the architecture requirements. **The block diagram is a feasibility map, not a
qualified full-appliance circuit. The 27-component recovery BOM is a capture
inventory, not a released procurement BOM.** No modem, PoE, NIC, power tree or
packet processor is present in KiCad.

## Block diagram decision gates

| Block / interface | Established | Needed to close the gate |
|---|---|---|
| Recovery MCU, watchdog, reset and enable outputs | Captured in `hardware/recovery.kicad_sch`; native ERC and critical-net assertions pass. | Exact target-domain electrical levels, reset pull-ups, powered-off safety, firmware timing and bench fault injection. |
| Quectel modem to RTL8125 packet path | Manufacturer material makes modem PCIe root-complex offload a candidate; no requested model/firmware/NIC tuple is qualified. | RM520N-GL and RM551E-GL production hardware guides, approved firmware, NIC driver, data-call/NAT/DHCP/recovery behavior and traffic test. |
| Sierra modem to Ethernet | Older manufacturer PTS identifies EM9190/EM9293 as USB devices / PCIe endpoints. RK3566 supplies a documented USB3 host. | Exact firmware/composition and Linux driver route, then bench traffic and recovery for each model. |
| Common Linux host | RK3566 is now selected for evaluation. Its separate USB3 host and PCIe RC close the interface topology gate; see [rockchip-qualification.md](rockchip-qualification.md). | Exact RAM/PMIC/storage/NIC reference circuit, software image, measured multi-gigabit forwarding and all four modem tuples. |
| PoE and isolated power | Functional domains are mapped in `packet-path.svg`. | Peak power for every installed modem configuration, PD class, exact PD/converter/bridges/magnetics, isolation/EMC and thermal evidence. |
| Universal M.2 socket | **Unsafe to capture as one common VCC plane:** Sierra contacts 24/38/68 conflict with RM520N-GL assignments. | Separate profile-specific hardware or reviewed default-disconnected selection; RM551E-GL current pin table; all power, reset and SIM pin reviews. |

The product-level packet path remains open for the required set of four modems.
Do not treat a 2.5GbE link, an ERC pass or the estimated power envelope as
throughput, interoperability or production qualification. The source and exact
model distinctions are in [architecture.md](architecture.md),
[rockchip-options.md](rockchip-options.md) and [power-and-cost.md](power-and-cost.md).

## KiCad recovery BOM, grouped from the native XML netlist

| References | Qty | Captured value / package | Qualification gap |
|---|---:|---|---|
| U201 | 1 | STM32G0B1CCT6 / LQFP48 | Exact part entered; current manufacturer pin/reference-circuit audit, option bytes and firmware/recovery tests pending. |
| U202 | 1 | TPS3823-33DBVR / SOT-23-5 | Exact part entered; reset timing and watchdog startup must be verified at limits and on hardware. |
| D201 | 1 | BAT54WS-7-F / SOD-323 | Exact part entered; supervisor-low plus diode-forward drop versus MCU NRST-low threshold pending. |
| Q301–Q303 | 3 | Nexperia MMBT3904,215 / SOT-23 | Exact part entered; actual target sink voltage/current and powered-off interface review pending. Datasheet field now points to Nexperia. |
| C201, C202, C204, C205 | 4 | 100 nF / 0603 | No MPN. Select X7R voltage rating and check effective capacitance at 3.3 V and temperature. |
| C203 | 1 | 4.7 µF / 0603 | No MPN. Effective capacitance under DC bias and package feasibility require a manufacturer curve; enlarge if needed. |
| R201–R203, R301, R303, R305 | 6 | 10 kR / 0603 | No MPN, tolerance or power rating; check reset and transistor-drive limits. |
| R302, R304, R306–R308 | 5 | 100 kR / 0603 | No MPN, tolerance or power rating; check leakage and default-off margins. |
| J101, J202 | 2 | 2-pin 2.54 mm headers | No exact orderable header or mating shunt; J202 requires a fitted RUN shunt in service. |
| J201 | 1 | 6-pin 2.54 mm SWD header | No exact orderable part, mating connector or access/mechanical check. |
| J102 | 1 | 10-pin 2.54 mm control boundary | Evaluation connector only; no production target interface is qualified. |
| SW201 | 1 | Reset button / TL3342 footprint | No exact switch MPN or footprint/datasheet match. |

Total: **27 fitted schematic components**, excluding power symbols and the
required J202 mating shunt. The netlist supplies the component inventory; exact
manufacturer part numbers must be entered in the schematic before release.
Prices, stock and assembly feasibility require a fresh quote after the design
architecture and exact MPNs are frozen. No purchasing approval is implied.

## Evidence and validation boundary

`python3 hardware/check.py --output /tmp/sierra-wan-check-20260929` passed on
2026-09-29 with KiCad CLI 10.99.0: zero ERC violations, native XML netlist
connectivity assertions, and SVG/PDF export. This validates schematic capture
connectivity only. Manufacturer references for currently captured ICs:
[ST STM32G0B1 datasheet](https://www.st.com/resource/en/datasheet/stm32g0b1ne.pdf),
[TI TPS3823](https://www.ti.com/product/TPS3823),
[Nexperia MMBT3904](https://www.nexperia.com/product/MMBT3904), and
[Diodes BAT54WS](https://www.diodes.com/datasheet/download/BAT54WS.pdf).
