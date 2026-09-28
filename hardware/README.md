# Independent recovery subsystem — review draft

Open `recovery.kicad_pro` / `recovery.kicad_sch`. Three hierarchical sheets,
27 actual components, no PCB layout. This is **not a complete WAN appliance**.
The packet-path gate in [architecture.md](../docs/architecture.md) remains open.

Implemented:

- STM32G0B1CCT6 in LQFP48, local decoupling, internal clock, SWD recovery header.
- TPS3823-33DBVR independent watchdog/brownout reset, manual reset button and
  physical watchdog service jumper. Fit the RUN shunt for unattended operation.
- BAT54WS reset isolation so the push-pull supervisor does not contend with SWD
  reset. Keep PF2/pin 10 configured as NRST; boot firmware must preserve it.
- Three MMBT3904 open-collector reset/off outputs; 10 kR base and 100 kR
  base-emitter resistors; two default-low power-enable outputs.
- Explicit evaluation boundaries: regulated/current-limited 3.3 V at J101,
  GPIO/service interfaces at J102. J102 is not a modem connector. No firmware.

The G0 is an independent recovery study, **not a selected appliance controller**:
it does not establish modem AT control or multi-gigabit forwarding. The possible
F723 USB-HS control role is separate and remains unqualified. Do not assemble a
second MCU merely because both appear in architecture discussion.

## Validation on 2026-09-28

KiCad CLI 10.99.0: **0 ERC violations at all severities**. Native hierarchical
XML netlist checks pass for diode orientation, watchdog jumper isolation, MCU
NRST, SWD, all three transistor base/collector/emitter networks, enable pull-downs
and essential supply contacts. Three-sheet SVGs were rendered to PNG and visually
reviewed through multiple placement revisions. Native PDF export passes.
These checks establish capture connectivity, not electrical or production approval.

Reproduce without putting generated output in the repository:

```sh
python3 hardware/check.py --output /tmp/sierra-wan-check
```

Use `--kicad-cli /path/to/kicad-cli` if required. The script stops on ERC findings
and exports XML, SVG and PDF for inspection. It does not generate fabrication files.
Do not run Python with `-O`, which disables the connectivity assertions.

## Sources and remaining qualification

- [STM32G0B1 datasheet DS13560](https://www.st.com/resource/en/datasheet/stm32g0b1kc.pdf).
  Capture uses the stock KiCad STM32G0B1CCTx pin identities, without pin swaps.
  Full current manufacturer package-pin/reference-circuit cross-check is still
  pending: the full ST PDF could not be retrieved in this session. Do not treat
  a clean library-based netlist as a completed manufacturer pin audit.
- [TI TPS3823 datasheet](https://www.ti.com/lit/ds/symlink/tps3823.pdf): RESET pin 1,
  GND 2, MR 3, WDI 4, VDD 5; SOT-23-5. Nominal 1.6 s watchdog, 200 ms reset,
  2.93 V threshold. WDI floating disables the watchdog; the fitted RUN jumper
  connects a pulled-down MCU signal so MCU reset does not float it.
- [Diodes BAT54WS](https://www.diodes.com/datasheet/download/BAT54WS.pdf): verify
  supervisor VOL plus diode VF stays below MCU NRST VIL across voltage,
  temperature and reset pull-up currents before release.
- [Nexperia MMBT3904](https://assets.nexperia.com/documents/data-sheet/MMBT3904.pdf):
  base 1, emitter 2, collector 3. Target sink-current allocation is 1 mA;
  verify low voltage against each actual modem/NIC input requirement.

Passives have 0603 footprints; exact MPNs/tolerances and capacitor effective
capacitance are not a released BOM. Headers, RUN shunt and switch need exact
orderable parts and mechanical review. MCU update partition sizing, signed
bootloader, BOR/option bytes, recovery firmware and watchdog startup timing are
not implemented or tested. The RUN jumper must not be omitted in production.

External reset pull-ups must come from the relevant switched target domain;
`MODEM_OFF_N` needs the profile-specific FULL_CARD_POWER_OFF# pull-up. Without
that pull-up, the modem remains off. Neither power switching nor discharge is
implemented. Service UART, HEALTH_IN and POWER_FAULT_N are 3.3 V boundaries;
add appropriate powered-off-safe translation/protection for actual targets.

Not implemented: PoE PD/protection/isolation, final power budget/class, modem
regulator/load switch, socket profiles, SIM, Ethernet controller/magnetics,
USB/PCIe, AT/session control, modem recovery/update transport, complete BOM.
No hardware, throughput, thermal, EMC, isolation or unattended tests have run.

Embedded library-symbol audit: all 18 embedded symbol entries retain the stock
KiCad pin numbers, names and electrical types (inheritance resolved). This checks
symbol fidelity only; it does not replace the outstanding manufacturer pin audit.
