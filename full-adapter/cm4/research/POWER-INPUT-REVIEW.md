# Auxiliary input capture — 2026-09-10

The current CM4 hierarchy has 12 pages and 69 physical components. Four new
pages capture 36 components for USB-C power, CC protection, voltage qualification
and input arbitration. The project has 50 unfinished ERC findings and no carrier
PCB. This is a static capture milestone; the open items below prevent release.

## Selected circuit

J150 is GCT USB4105-GF-A-120, rated 5 A collectively on VBUS. This is a power-only
port; its data and SBU contacts are unconnected. U150 is exactly HUSB238_002DD:
VSET open and 22.6 kohm ISET request 20 V / 3 A. Manufacturer Table 8 says this
variant asserts GATE during POR and tries the next PDO on a mismatch. GATE alone
therefore cannot indicate adequate power. The RDO algorithm rejects source
PDOs below the requested current and searches downward in voltage. A 45 W
20 V / 2.25 A adapter normally falls back to 15 V / 3 A, which U153 rejects.
Use a supply offering 20 V / 3 A and a compliant 3 A cable. No SOP' emulation
or I2C override is used. An 18 V source at its upper tolerance may enter the
window; the final budget must therefore cover the lowest qualified voltage.

U151 TPD6S300RUKR protects CC against 20 V shorts and IEC ESD. Port-side CCs
also connect to the matching RPD_G pins for dead-battery attachment. HUSB238
provides permanent sink Rd, including when unpowered. TI's 3.5 ms maximum
power-up reconnection is below the 10 ms Type-C detach interval. Unused U151
channels and pins 16/17 are grounded; unused J150 data contacts remain open.
The VBIAS bypass is the exact 100 nF / 50 V X7R part TI recommends.

U152 TLV70433 powers protection and logic from AUX only. D150 BAT54CLT1G has
anode 1 at VBUS, anode 2 at AUX_3V3 and common cathode 3 at the LDO input.
One diode isolates the input reservoir on unplug; the other implements the
OUT-to-IN bypass recommended in TLV704 section 8.2.2.3. The LDO output has no
external powered load. Verify the residual diode drop and reverse current during
cold/hot unplug; do not rely on an unprotected LDO body diode. D150 is sized for
housekeeping current, not an independently short-circuit-qualified power output.

Q150 DMP2035U supplies the fault node while HUSB GATE is low. Pin 2 is source;
pin 3 is drain. The 10 kohm gate-source resistor turns it off when GATE opens;
1 kohm limits GATE transient current. U151 FLT and both U153 outputs can sink
the node through 4.7 kohm. U154 SN74LVC1G14 inverts it to the active-high mux
disable input. This Schmitt input tolerates the slow gate transitions. At a
3.0 V housekeeping floor, conservative resistance/leakage bounds leave the
valid node above 2.833 V. Fault sink current is below 0.782 mA and LOW is at
most 0.4 V. The review bounds thresholds using the 3 V and 4.5 V table rows;
it does not present an interpolated nominal threshold as a specified limit.
Verify PMOS off leakage and logic margin over the board's qualified temperature
range, including the LDO's legacy/new die variants.

## Voltage window and arbitration

U153 uses 0.1%, 25 ppm/K resistors. Independent calculations include reference
limits, input leakage and a 100 K resistor temperature excursion from 25 C:

| Transition | Minimum | Maximum |
| --- | ---: | ---: |
| UV permits input, rising | 18.198 V | 18.845 V |
| UV disconnects, falling | 17.785 V | 18.659 V |
| OV disconnects, rising | 21.222 V | 21.966 V |
| OV permits input, falling | 20.739 V | 21.749 V |

Normal 20 V +/-5% stays inside the initial acceptance window. OV disconnect
occurs below the mux's 22 V recommended input ceiling. These are static trip
levels; comparator delay does not clamp a fast input surge.

U160 TPS2121 uses AUX on IN1 and the pending isolated 12 V PD output on IN2.
Separate 49.9 kohm / 10 kohm dividers select the higher qualified input. Its
back-to-back switches prevent steady backfeed into either absent source;
the specified reverse leakage is finite, and a removal transient needs testing.
Unused ST is grounded exactly as its datasheet directs. Both OUT pads are
connected. The 22.1 kohm limit is nominally 4.5 A; the IC's 4–5 A range becomes
about 3.92–5.10 A with a conservative 2% resistor bound. This does not enforce
the USB-C 3 A contract; normal load and fault-source limits still need closure.
The 1 uF SS capacitor gives about 0.09 V/ms initial rise. Downstream converter
UVLO, bus capacitance, switchover droop and thermal layout remain to be sized.

## Land and drawing review

- GCT B4: 12 physical contact lands carry 16 numbered contacts, with four
  shield slots and two 0.65 mm locating holes. PCB edge is local y=+3.675 mm.
  The -120 variant's maximum 1.35 mm stake depth is represented in its model.
- TPD6S300 RUK0020B: 20 lands are 0.6 x 0.2 mm, pitch 0.4 mm, opposing
  centre distance 2.8 mm; EP is 1.7 mm square. The installed KiCad land was
  0.7 mm long and was corrected to the device datasheet's page 33 drawing.
- TPS2121 RUX: 12 pads, no EP. Pins 1/2/7/8 use 1.05 x 0.4 mm power lands;
  the eight end lands use 0.2 x 0.6 mm. Pad 1 and pad 8 both carry output.
- HUSB238 DFN: manufacturer package dimensions plus an IPC-derived pattern:
  0.75 x 0.25 mm lands at 0.5 mm pitch, EP 1.8 x 2.5 mm. Four paste windows
  cover 65.5% of the EP. The manufacturer supplies package dimensions rather
  than a recommended PCB land. Final stencil review must include this choice.

Schematic pages and footprint SVGs were rendered and reviewed; reference-label
overlap and title-block encroachment were corrected. The four STEP models load
as valid solids. IC models are conservative body envelopes. The ignored review
fixture is clearly marked as library QA and contains no carrier circuitry.

`check_power_input.py` independently asserts exported pin connectivity, separate
rails, exact MPNs, NC/ground policy, divider limits and land dimensions.
`check_core.py` invokes it, and the staged root check includes all four pages.
No ERC exclusions were introduced. The six non-isolated ERC findings are CM4
5 V, three PCIe inputs, PoE 12 V and PoE class disable; 44 global endpoints remain
isolated while the rest of the board is captured.

## Open integration work

Complete the simultaneous modem/CM4/USB3/storage/fan/development-IO budget before
finalizing the PoE class. Ag59612-LPB Class 6 is a candidate, not a final power
qualification. Capture its bridges and class interlock, all rail converters,
modem controls and the rest of the interfaces.

The TPS2121's 24 V absolute maximum needs coordinated input transient protection.
A generic 22 V TVS whose clamp exceeds 30 V is insufficient. Close cable
reconnection/PD-reset overshoot, input capacitance compliance, bulk-capacitor
DC-bias/aging derating, source fault limits and full-load dissipation before
calling this power path electrically complete. Bench tests cover real hot-plug,
ESD, PD interoperability, thermal rise and source-change behavior; missing
protection or unrouted nets are not bench-only exceptions.

`power-input-captured-cost.json` totals only the 36 captured parts: **$4.5268 per
board at quantities for ten boards**, using explicit price breaks where supplied.
The accompanying catalog includes unused candidates, which are not counted.
This excludes PCB, assembly, wastage, freight, tax and every uncaptured subsystem.
It is neither a complete-board estimate nor an actual JLC quote.
