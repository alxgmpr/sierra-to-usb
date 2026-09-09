# Proposed programming, bring-up and manufacturing tests

This is a plan for a future implemented board, not a record of passed tests.
Connector designators, fixture net names, pin voltages, test limits and firmware
images must be assigned from the final verified schematic. No test firmware or
production image has been produced.

## Required recovery provisions

Provide a documented Linux debug UART with its actual I/O voltage, hardware
reset and a physical Rockchip Maskrom/recovery control. Expose the correct USB
OTG device path for Rockchip recovery without ever joining it to another host.
Reserve programming access to the selected boot storage. Record exact DDR
training binary, loader, U-Boot, kernel, device tree and image hashes; verify
redistribution licenses and exact DDR/storage support before a factory release.

If RP2350B is fitted, provide SWD, reset and ROM boot access on an independent
power domain. Establish hardware ownership and safe inactive states for every
shared control before Linux or supervisor firmware executes. MCU reset and
unprogrammed flash must leave the modem profile invalid and modem power off.

## First-board bring-up sequence

1. Inspect assembly, X-ray the processor, DDR and other hidden joints, and
   measure resistance to ground on each rail before power. Start with the modem
   absent and accessory loads disconnected.
2. Use a current-limited auxiliary supply. Scope rail startup/shutdown, overshoot,
   reset release and PMIC sequence against exact device limits. Check reset,
   recovery and brownout behavior repeatedly before fitting the modem.
3. Load recovery software; train memory at the chosen conservative frequency.
   Run sustained memory and storage read/write verification across temperature
   and supply corners, then repeat with simultaneous CPU, USB and PCIe traffic.
4. Check every profile contact with a breakout fixture and modem absent. Verify
   no supplemental VCC or control pull-up reaches reserved/output contacts of
   each supported module. Invalid settings must prevent power. Measure power-off
   leakage/backfeed and discharge before permitting a physical module change.
5. Test modem start, orderly shutdown, emergency off, reset and radio-disable
   using exact model/firmware combinations. Measure transmit transients at the
   M.2 contacts, not only at the regulator. Check SIM behavior and antenna/cooling
   mechanics for each approved module length and connector height.
6. Validate USB host selection with both hosts attached, power sequencing in both
   orders, cable removal, reset and unpowered endpoints. Confirm break-before-make
   operation and absence of VBUS contention or signal back-powering.
7. Measure 2.5GbE link establishment and sustained bidirectional traffic through
   Linux and the modem, using appropriate RF conditions and a known capable
   peer. Record USB retries, PCIe errors, packet loss, thermals and throttling.
   Nominal link rates alone are not acceptance evidence.
8. Qualify PoE with the selected IEEE class, required pair sets, polarity cases,
   PSEs and worst cable loss. Verify detection/classification, inrush, maintain
   power signature, overload behavior, isolation and hot operation. Test USB-C
   negotiation, source handover and reverse-current blocking at full load.
9. Load GPIO, Qwiic, analog, fan and other accessory interfaces to their actual
   hardware-enforced limits. Check hot/cold thermal soak with maximum permitted
   modem, CPU, Ethernet and accessory demand. Test ESD/EMC and safety/isolation
   against the intended product requirements using suitable lab equipment.

## Production fixture and release records

The fixture should contact ground, input and isolated rails, PMIC outputs,
modem supply/control signals, supervisor SWD and Linux console/recovery without
bridging the PoE isolation barrier. Use an M.2 fixture to verify profile pin
mapping before fitting a valuable modem. Test rail voltages, off-state leakage,
programming, DDR/storage, Ethernet loopback or peer traffic, USB3 enumeration,
SIM, GPIO and user controls. Add calibrated current measurement and test software
that saves board serial, firmware hashes, measured results and failure reason.

Before release, replace all generic procedures with design-specific limits and
fixture connections. Archive ERC/parity/DRC and connectivity assertions, reviewed
layer and 3D renders, approved JLC stackup/impedances, BOM/placement consistency,
assembly drawings, programming images, qualification results and manufacturing
test logs. No unrouted nets or real electrical faults may be waived.
