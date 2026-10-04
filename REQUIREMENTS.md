# Appliance restart — 2026-09-28

This decision supersedes the CM4/RK3568 architecture and their continuation
instructions. Cost reduction is the reason for restarting. No CM4 or CM5.
Use an MCU-based architecture; RP2350 and STM32 are candidates, not selections.

## Required product behavior

- Support Sierra/Semtech EM919x and Quectel RM5x modem families. Qualify exact
  SKUs, firmware, pin profiles and interfaces; family names are not proof of
  interchangeability. Do not silently narrow support to one vendor.
- Provide a 2.5GBASE-T Ethernet port with standards-based isolated PoE input.
  Select PoE type/class only after establishing the complete peak power budget.
- Operate reliably as an unattended appliance. A provisioned SIM, suitable
  antennas and supported modem are installation prerequisites; normal use is
  one powered Ethernet cable and automatic cellular WAN service to the attached
  router or host. No external USB host is required.
- Use a highly reliable MCU implementation, with deterministic startup,
  brownout recovery, independent watchdog, bounded reconnect/retry behavior,
  controlled modem power/reset, and recoverable firmware updates.
- Minimize complete assembled cost, including power, magnetics, networking
  silicon, memory, connectors and assembly. No numerical cost target is set yet.

## Architecture gates before schematic capture

1. Prove the modem-to-Ethernet packet path for both modem families using exact
   manufacturer interface and firmware evidence. Determine who hosts USB/PCIe,
   establishes the cellular session, forwards packets and supplies DHCP/IP
   configuration. Do not assume modems can host an Ethernet controller merely
   because both expose PCIe, or that an Ethernet PHY provides a MAC/router.
2. Separate MCU supervision from the high-speed data path if needed. RP2350's
   native USB 1.1 full-speed path is limited to 12 Mb/s and cannot provide a
   high-throughput 5G bridge. An external controller still requires a viable
   host bus, protocol implementation and measured performance. STM32 is a
   family: qualify a specific part and its actual USB/Ethernet/bus capabilities.
3. Establish required sustained WAN throughput separately from 2.5GbE link
   negotiation. Do not quietly accept a slow forwarding path behind a fast port.
4. Resolve bridge/IP-passthrough versus routed/NAT operation and automatic
   APN/SIM provisioning behavior, including recovery after cellular loss.
5. Compare complete cost and software support before selecting components.
   If an MCU-only data path cannot meet the requirements, document the conflict
   and viable alternatives before changing the user's architecture direction.
6. Demonstrate cold boot, modem detection, session setup, Ethernet WAN service,
   power interruption recovery and sustained traffic on evaluation hardware
   before investing in a new integrated PCB.

## Initial source evidence

Checked 2026-09-28:

- Raspberry Pi RP2350 product specifications list one USB 1.1 host/device
  controller and PHY: https://www.raspberrypi.com/products/rp2350/
- RP2350 datasheet: https://datasheets.raspberrypi.com/rp2350/rp2350-datasheet.pdf
- Quectel RM520N product documentation is a starting point, not qualification
  of every RM5x variant: https://www.quectel.com/product/5g-rm520n-series/

## Repository scope

Work on `master`. The active tree contains only the restart documentation.
Previous CAD, libraries, research, continuation prompts, generated outputs and
checks were removed. Recover historical material from Git only when needed for
an explicitly scoped reference; do not restore old architecture instructions.
The final pre-restart hardware checkpoint is `c81dc27`.
No new hardware is implemented or qualified by this requirements reset.
Publishing, procurement and fabrication are not part of this change.

## Session clarification — 2026-09-28

- MCU-only is a hard constraint; do not add an external Linux/application
  processor to make the packet path work.
- Target is multi-gigabit WAN forwarding, not merely a 2.5GbE link.
- Requested model list: RM520N-GL, RM551E-GL, EM9190, and EM9293 (confirmed
  correction of the initial EM9193 identifier). Firmware revisions and carrier
  profiles remain unspecified.
- 0603 signal passives, appropriately larger power parts, and an LQFP STM32
  package are acceptable.
- Investigate whether a switch helps, but do not treat a PCIe switch as a root
  complex, an Ethernet switch as a modem host, or either as modem firmware.

Current research and independent recovery-circuit capture are indexed in README.
They do not close the packet-path feasibility gate or qualify an appliance.

The user subsequently confirmed: **retain all four models; hold integration**.
Do not narrow to Quectel-only. Complete-appliance capture remains on hold until
manufacturer evidence closes the packet-path gate. Independent recovery circuitry
is a review milestone, not authorization to integrate an unsupported interface.

## Subsequent alternatives review

The user reopened Linux packet processors for consideration, specifically asking
for sourceable, manufacturable Rockchip options. This authorizes comparison, not
a final part selection or restoration of retired designs. All four modem models
remain in scope. See `docs/rockchip-options.md`; integrated CAD remains on hold.

## Linux packet processor direction — 2026-09-29

The user has now directed qualification of a Rockchip Linux processor. **RK3566
is the selected processor candidate for evaluation**, paired with a PCIe
RTL8125BG-CG 2.5GbE controller and the independent STM32 recovery subsystem.
This supersedes the MCU-only constraint for the packet path. The MCU remains
responsible for independent supervision and recovery. All four requested modems
remain in scope. See [rockchip-qualification.md](docs/rockchip-qualification.md).

The processor's documented simultaneous USB3-host and PCIe-root-complex
interfaces qualify the topology for schematic planning. They do not establish
measured multi-gigabit WAN forwarding, exact modem compatibility, a released
memory/PMIC/storage BOM, PoE class, or safe universal M.2 socket. Detailed
integrated capture remains gated by those exact electrical and software choices.

## Complete schematic capture — 2026-10-03

The user authorized completing the full appliance schematic and exact parts
selection before PCB layout. This supersedes the earlier hold on detailed CAD
capture. Keep RK3566, independent STM32 supervision, isolated PoE and 2.5GbE,
and all four modem models in scope. Use manufacturer reference-design packages
for new power circuits; 0603 remains the signal-passive preference.

Capture is an engineering draft until pin/rail/BOM/mechanical checks close.
Bench throughput and recovery evidence remain release conditions; capture does
not claim those tests have passed. Do not replace missing manufacturer pinouts
with assumed compatibility. Profile-specific modem implementations are allowed
without dropping any requested model. Current progress and acceptance criteria
are in `docs/schematic-completion.md`.
