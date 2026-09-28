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
