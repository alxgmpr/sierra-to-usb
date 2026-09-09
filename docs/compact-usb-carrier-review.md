> Historical evidence from superseded designs. See the [current full adapter](../full-adapter/README.md). Circuit status and artifact paths below refer to the historical checkpoint, not the replacement.

# Compact EM9190 / Quectel USB carrier

2026-09-04. Initial architecture and reuse review; not a released schematic or fabrication design.

## User clarification: one cable to a MacBook

The user specified Quectel RM520N and RM551E alongside EM9190, with a preference for one USB-C connection directly to an M1 Pro MacBook Pro running the latest macOS. This supersedes the two-port candidate below as the preferred architecture. Regional modem suffixes and the exact macOS release remain to be recorded for compatibility testing.

Apple identifies this MacBook generation as having Thunderbolt 4 ports. Proceed with one USB-C data/power port and a 5 V / 3 A input design target, checking available current at attachment before enabling the modem. This is a source-power budget, not yet proof that RM551E worst-case demand fits. Reference: [Apple 2021 MacBook Pro specifications](https://support.apple.com/en-bh/111902).

Design for operation from 5 V input with correctly detected/negotiated source current; do not require the old design's 12 V input. PD cannot obtain a voltage or current the laptop does not offer. Intel specifies 15 W minimum accessory power for Thunderbolt 4/5 computer ports; the actual MacBook port and attachment behavior still need verification. A 5 V, 3 A source is a plausible design target, not an established guarantee for the user's unspecified MacBook.

RM520N-GL Hardware Design V1.0 section 3.3.1 requires at least 3 A continuous capability at the modem supply. For illustration, 3.3 V x 3 A / 90% conversion efficiency = 11 W input before other board loads and cable losses. That suggests a 15 W input can be viable, but is not a full transient/thermal budget. RM551E maximum demand remains unverified; do not extend this calculation into a compatibility claim for it.

Mac operation also requires a supported USB network function and connection-management path for each module/firmware combination. Successful USB enumeration alone does not establish working cellular networking. Validate this with existing adapter hardware before freezing the new carrier, including ECM or another macOS-compatible mode where the particular firmware supports it. An MCU that only controls straps does not translate an unsupported USB modem protocol.

References: [Intel Thunderbolt comparison](https://www.intel.com/content/www/us/en/architecture-and-technology/thunderbolt/overview.html), [TI laptop PD source-capability explanation](https://e2e.ti.com/support/power-management-group/power-management/f/power-management-forum/1543719/tps25730evm-laptop-type-c-pd-port-interface-to-tps25730evm), [Quectel RM520N MacBook support discussion](https://forums.quectel.com/t/rm520n-gl-with-m-2-usb-adapter-using-with-macbook-pro/30204).

## Recommendation

### User-supplied 3 A continuous / 4 A peak figures

Checked the supplied RM50xQ Series Hardware Design V1.3: section 3.3.1, printed page 32, specifies at least 3 A continuous and 4 A peak supply capability. This is a supply-sizing requirement for RM50xQ, not a documented maximum consumption or verified RM551E requirement. The other supplied device.report link contains a Quectel product catalogue despite its EG800K page title.

At an assumed 3.3 V modem rail, 3 A is 9.9 W and 4 A is 13.2 W. Illustrative converter input demands are 11.0 W / 14.67 W at 90% efficiency, or 10.42 W / 13.89 W at 95%, before auxiliary loads and cable/protection losses. Thus 15 W is plausible but has little worst-case peak margin. At 4.75 V converter input and 90% efficiency, the 4 A output case alone draws approximately 3.09 A input, exceeding a 3 A source allocation. A 3.7 V rail would require 14.8 W output at 4 A before conversion losses.

Keep the one-port architecture, but select the buck for at least the verified peak load plus component/current-limit margin (a 5-6 A class part is a candidate, not a completed selection). Verify efficiency at minimum input voltage, full load and temperature; include auxiliary power, cable resistance and inrush. Size local energy storage from actual pulse duration and allowed droop: C >= deficit_current * pulse_duration / allowed_droop, with ESR and converter response also checked. Capacitors cannot cover sustained insufficient source power. Do not freeze RM551E power compatibility without its applicable hardware specification or equivalent measured evidence.

Source: [Quectel-authored RM50xQ Hardware Design V1.3, supplied Scribd copy](https://www.scribd.com/document/909631816/Quectel-RM50xQ-Series-Hardware-Design-V1-3).

### Peak buffering direction

The user suggested bulk capacitance or another energy-buffering approach. Start with a fast synchronous buck plus local low-ESR bulk/ceramic capacitance. Treat this as a candidate requiring load-step and transmit-current measurements, not a guarantee that capacitors solve the power budget.

For illustration, if capacitors must supply a 1 A deficit and only 0.1 V droop is allocated to capacitive discharge, ideal capacitance is 1,000 uF for 100 us, 10,000 uF for 1 ms, and 100,000 uF (0.1 F) for 10 ms. ESR drop, capacitance tolerance, DC bias, rail tolerance, trace drop and converter response reduce the available margin. These examples assume the full stated deficit persists for the duration; actual source and converter contributions must be measured.

For longer peaks, consider a separately current-limited, higher-voltage reservoir charged from the 5 V input, with a controlled discharge converter/power path feeding the modem rail. Ideal usable energy is 0.5*C*(V_high^2-V_low^2); include discharge conversion loss and recharge demand. This permits more voltage swing than bulk directly on the modem rail but adds area, losses and control complexity. Reserve it as a fallback after measuring the waveform. Neither approach can compensate indefinitely for average input demand exceeding the available USB power.

Place substantial capacitance behind controlled inrush/precharge; verify cable insertion, reservoir recharge, repeated peaks, overload behavior and USB current limits. A large capacitor directly across the receptacle is not the proposed implementation.

Reuse selected schematic circuits and project libraries from this repository, with a new compact PCB layout. The existing design is a much larger USB / Ethernet / PoE carrier with 369 footprints. Removing those extra functions changes the power tree, placement and routing enough to justify a fresh layout. Preserve the existing project as the reference.

The user's current requirements are USB-C data, USB-C PD power, an M.2 modem socket, convenient coax-to-edge-SMA breakouts, and support for EM9190 plus specified Quectel models. Prior project documents contain historical choices, not new approvals for this reduced design.

## Verified findings

- EM919x PTS 41113174 Rev 5, section 3.7, printed pages 38-39: PCIE_DIS selects USB when driven to 1.8 V at boot. A change requires reset/power cycle. This is M.2 pin 20. The module also needs its normal power-on controls; this strap alone is insufficient.
- The supplied EM91 DevKit guide 41113875 Rev 2, section 5.1, printed page 23, requires VBUS_SENSE to indicate USB presence; the schematic on page 36 maps it to pin 22. Do not connect negotiated PD voltage directly to this pin.
- The supplied guide section 8.1, printed page 29, has FOUR MHF4-to-SMA paths: AUX, MIMO2, MIMO1 and MAIN, covering sub-6/LTE/3G/GNSS. The existing project's fifth dedicated GNSS path is not required to mirror this EM91 arrangement. These paths do not implement EM9190 mmWave antenna hardware.
- Quectel RM520N-GL Hardware Design V1.0, printed pages 20-23, marks pins 20 and 22 RESERVED and directs reserved/unused pins to remain unconnected. Existing Sierra pull-ups/dividers must therefore be disconnectable at the modem pins. Pulling a pin low with an open-drain MCU output is not disconnection.
- Current TI documentation identifies HD3SS3220 as supporting up to 10 Gbps. The old symbol description calling it Gen1 is incomplete. Reuse is conditional on the selected USB-C architecture and signal-integrity review; no tested 10 Gbps performance is implied.

Source versions matter: Sierra currently lists EM919x PTS version 11. The accessible Rev 5 and supplied DevKit Rev 2 establish the above behavior, but final capture needs the applicable current module specification and the exact Quectel hardware design. The existing EM929X PDF is not a substitute for EM9190-specific verification.

## Circuit reuse map

| Existing sheet | Compact design treatment |
| --- | --- |
| `sheets/usb3_data.kicad_sch` | Reuse as a candidate for separate data/power ports; audit USB-C footprint, both cable orientations, ESD loading, AC coupling and mux power states. A shared PD/data port needs a coordinated CC/PD controller and orientation arrangement. |
| `sheets/power_input.kicad_sch` | Rework around PD only. Remove PoE and source ORing if no longer needed. Select supported PDOs and a rated protected input path. Do not assume every source supplies the old 12 V request. |
| `sheets/power_rails.kicad_sch` | Reuse regulator ideas after recalculating modem load, transient droop, startup/inrush, UVLO and thermal behavior. Provide a modem supply within both selected modules' limits and a separate 1.8 V control rail. |
| `sheets/m2.kicad_sch` | Reuse socket and verified shared USB pins; redesign vendor-specific pin isolation, boot sequencing and host-presence detection. Recheck every populated pin against both exact modules. |
| `sheets/sim.kicad_sch` | One physical nano-SIM is the proposed minimum; dual SIM/eSIM is optional pending user preference. Preserve module-supplied SIM voltage and required ESD/protection. |
| `sheets/rf.kicad_sch` | Reuse four MHF4-to-SMA paths for EM9190. Confirm footprint drawings, exact mating cable family, SMA board thickness and operating frequency. Label generic ANT1-4 with a vendor mapping table. |
| `sheets/mcu.kicad_sch` | Optional control subsystem for reset, power cycle and profile management. Remove AT-command USB-host multiplexing unless specifically needed. Hardware profile selection should permit initial bring-up without firmware. |
| `sheets/usb2_debug.kicad_sch` | Retain only if required for MCU configuration; otherwise use a compact programming header. |
| `sheets/ethernet.kicad_sch` | Omit from the proposed compact USB-only variant. |

## Proposed electrical architecture

Two-port candidate, pending user port preference:

```text
USB-C DATA -> ESD + orientation mux -> M.2 USB3 + USB2
            host VBUS detector    -> isolated Sierra VBUS_SENSE path
USB-C PD   -> PD sink + protection -> buck -> modem VCC
                                         -> logic rails
Hardware profile / optional MCU  -> isolated straps, reset, power enable
Nano-SIM                         -> M.2 SIM1
4 x edge SMA <-> 50-ohm PCB path <-> MHF4 <-> cable <-> modem
```

For a one-port implementation, the host must supply enough power. Its USB-C connector alone does not establish a suitable PD contract. Coordinate PD negotiation, current limiting, orientation selection, host-presence detection and converter startup in that design. Do not place two independent CC owners on the same receptacle. Support of 5 V fallback must be based on the advertised current and measured power budget, not assumed.

Start with a manually selected Sierra / Quectel hardware profile. On Sierra, connect the 1.8 V boot strap and a conditioned host-presence signal. On Quectel, physically disconnect these paths when its pin table requires NC. A removable profile jumper arrangement is the simplest prototype; programmable operation needs switches with appropriate powered-off isolation and voltage ratings, with the modem held off until configuration is valid. Firmware cannot repair conflicting hardwired pin assignments. Do not depend on automatic USB identification to choose the electrical profile before the modem can enumerate.

Leave Sierra's extra supply connections 24/38/68 unpopulated until verified against the applicable EM9190 and Quectel pin tables. Never use software alone to select supply connections onto potential signal/output pins. Check power-off leakage and back-power paths from the host cable and MCU into the modem.

A four-layer board is the initial layout candidate: uninterrupted ground reference under USB and RF, controlled 90-ohm USB differential and 50-ohm RF routing using the fabricator's stackup. Reserve module mounting/grounding, heatsink clearance, short RF paths and SMA mechanical support before setting final dimensions. Port placement and four SMA bodies will set a practical size floor. No trace widths or final outline are frozen yet.

## Baseline checks actually run

- KiCad CLI successfully exports the existing hierarchical schematic netlist.
- `python3 tools/check_nets.py`: all existing assertions pass. These assertions verify recorded connectivity, not cross-vendor electrical correctness.
- Current schematic ERC: 0 errors, 496 warnings. Categories: 129 library mismatches, 352 off-grid endpoints, 1 isolated-pin label, 3 unconnected-wire endpoints, 2 multiple-net-name findings, 8 pin-to-pin warnings and 1 same-local/global-label warning. Existing project exclusions/check settings apply.
- Current PCB DRC: CLI reports 626 violations and separately 499 unconnected items. These are baseline results, not introduced changes or proof that every finding is an electrical fault.
- Reports: `tmp/baseline-erc.rpt` and `tmp/baseline-drc.rpt`. No schematic or PCB copper was changed during this review.

## Decisions needed before variant capture

1. Exact Quectel model(s), including regional suffix. Prior notes mention RM551E-GL but do not contain its verified hardware pin table; do not inherit RM520N compatibility as proof.
2. One shared USB-C PD/data port versus separate data and PD power ports.

After those decisions: capture the reduced hierarchy, verify pin-by-pin net connectivity and power sequencing, check footprint drawings, then place and route the new PCB. Bring-up must measure the empty-socket rails and profile pins first, then test enumeration in both cable orientations, power interruption/reconnection, and sustained transmit load with thermal monitoring. Fabrication readiness requires resolved relevant ERC/DRC findings and completed routing.

## Primary sources

- Supplied file: `/Users/alex/Downloads/41113875 EM91 Series Development Kit User Guide r2.pdf`, sections 5.1 and 8.1, schematic page 36.
- [Sierra EM919x PTS current download page](https://source.sierrawireless.com/resources/airprime/minicard/airprime_em919x-7690_product_technical_specification/).
- [Sierra EM919x PTS Rev 5, manufacturer forum attachment](https://cdck-file-uploads-us1.s3.dualstack.us-west-2.amazonaws.com/flex025/uploads/sierrawireless/original/2X/1/1bd7a25d38d0c99ff10fe2000bcd4a6c2ee9dafa.pdf).
- [Quectel RM520N-GL hardware design, manufacturer forum attachment](https://forums.quectel.com/uploads/short-url/1zkjPRnxF5BZ2woox386baCZx4g.pdf).
- [TI HD3SS3220](https://www.ti.com/product/HD3SS3220).
- [I-PEX MHF4 catalog](https://www.i-pex.com/sites/default/files/downloads/pdf/CATALOG_MHF_4_E.pdf).

## 2026-09-04 buffered-power capture update

The initial capacitor-only state is superseded by the candidate power capture documented in [power-design-review.md](power-design-review.md). LTC3128 explicitly supports live-source pulsed loads, but aged/low-input margins fail some test envelopes. The proposed bank setting is 4.06 V, not its 5.4 V summed rating. RM551E requirements and all-modem compatibility remain unverified. This is not a released power system.
