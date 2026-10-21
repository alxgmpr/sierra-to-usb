# Block diagram and BOM qualification status

Updated 2026-10-21: the [full engineering schematic](../hardware/appliance.kicad_sch)
has 30 sheets / 663 components / 823 nets and zero full ERC violations. See the
[current capture and release holds](schematic-completion.md) and
[engineering BOM inventory](../hardware/review/2026-10-07/bom.csv).
All major circuit blocks are captured. Two BGA land/process reviews, remaining model
holds, current controlled modem guides, exact software tuples and physical validation
remain open. See [six-footprint disposition](footprint-review-2026-10-21.md) and
[modem documentation blockers](modem-documentation.md).
All 663 PCB footprints are assigned, including 572 stock hand-solder choices.
Current CLI parity is clean; the October 7 native bidirectional update checks
are retained. The board is still unrouted and unreleased. See the [footprint/model audit](footprint-audit.md). No modem or
forwarding/recovery tuple is qualified.

The dated feasibility and recovery-only BOM tables below are historical context,
not the current capture inventory. Current native files and the completion page
supersede descriptions of absent circuit blocks.

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
| U202 | 1 | TPS3828-33DBVR / SOT-23-5 | Exact part entered; reset timing and watchdog startup must be verified at limits and on hardware. |
| Q301–Q303 | 3 | Nexperia MMBT3904,215 / SOT-23 | Exact part entered; actual target sink voltage/current and powered-off interface review pending. Datasheet field now points to Nexperia. |
| C201, C202, C204, C205 | 4 | CL10B104KA8NNNC / 100 nF, 25 V X7R, 0603 | Exact MPN captured; typical bias data archived; temperature/aging qualification pending. |
| C203 | 1 | CL31B106KAHNNNE / 10 µF, 25 V X7R, 1206 | Enlarged for capacitance margin; typical combined estimate 6.48 µF at 3.6 V with tolerance/temperature allowance; aging pending. |
| R201–R203, R301, R303, R305 | 6 | RC0603FR-0710KL / 10 kR, 1%, 0.1 W, 0603 | Exact MPN captured; transistor-drive limits pending. |
| R302, R304, R306–R308 | 5 | RC0603FR-07100KL / 100 kR, 1%, 0.1 W, 0603 | Exact MPN captured; leakage and default-off margins pending. |
| J101, J202 | 2 | 2-pin 2.54 mm headers | 61300211121 captured; J202 requires 60900213421 RUN shunt; local 1.10 mm drill footprint checked. |
| J201 | 1 | 6-pin 2.54 mm SWD header | 61300611121 captured with checked local drill variant; access/mechanical review pending. |
| J102 | 1 | 10-pin 2.54 mm control boundary | 61301011121 captured with checked local drill variant; production target interface remains unqualified. |
| SW201 | 1 | Reset button / TL3342 footprint | TL3342F160QG captured; Rev J pad geometry and common-contact grouping match footprint. |

Total: **26 fitted schematic components**, excluding power symbols and the
required J202 mating shunt. The netlist supplies the component inventory; exact
manufacturer part numbers are now entered for all 26 components. Electrical
qualification and full-appliance integration remain incomplete. See
[schematic-completion.md](schematic-completion.md) for current audit evidence.
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
