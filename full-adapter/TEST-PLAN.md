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

### RTL8125BG bring-up and identity

- Complete the hardware reset and host-control isolation circuit before attempting
  link bring-up. R679 currently holds PERSTB low. Measure both Ethernet rails,
  pin6/U13 EN, ISOLATEB, PERSTB and REFCLK together. Require at least100ms of valid
  power and100us of stable clock before PERST release, at least100us reset pulses,
  at least10ms between release edges, and at least50ms off/on spacing. Repeat
  brownouts and shutdown with both supply orders and asynchronous clock activity.
- Measure 3.14–3.46V and0.92–0.98V at U11 under full traffic, including DC drop,
  ripple and transients. Probe pin15's filtered branch for ringing and startup
  overshoot. Check the regulator's capacitive load, discharge and PWM operation
  after final placement; generic capacitor estimates are not production minima.
- Tune Y670's load and CKXTAL2 damping without loading the oscillator with a
  conventional probe. Verify startup, maximum100uW crystal drive and total
  frequency error within±50ppm including first-year aging. The current component
  budget leaves17ppm for load/PCB error. Keep exact BG ambient within0–70C.
- No EEPROM/flash is fitted. Verify exact-silicon default enumeration and record
  PCI IDs, revision, kernel, device tree and rtl8125b-2 firmware hashes. Provision
  a unique locally administered unicast MAC per board and apply it before network-UP.
  Record the address and board serial in the fixture ledger, reject duplicates,
  and verify persistence after reboot and firmware update. Random driver fallback
  is a bring-up aid, not acceptable production identity. Do not burn RTL OTP.
- Test both PCIe directions and sustained simultaneous USB/modem/Ethernet traffic.
  Check negotiated PCIe speed/width, AER counters, throughput, loss, thermals and
  recovery after reset. Add qualified magnetics and all four MDI pairs before
  these tests; isolated schematic endpoints cannot be treated as passed hardware.

### RK809 control measurements

- Verify I2C0 is pulled to 1.8 V and PMUIO2 is configured to that same domain;
  INT and reset use the 3.3 V PMU domain. Check low levels and edge times at
  both RK809 and RK860 during simultaneous activity.
- Measure VCC3V3_SYS, VDC, PMIC outputs and SYS_RESET_L together. Verify the
  VDC trigger follows valid PMIC input power and the specified qualification
  interval. Before release, finish the upstream power-good/restart circuit;
  an RC cold-start delay alone does not establish brownout recovery.
- Sweep power interruptions and supply ramps through the final supported
  ranges, including interruptions too short to discharge C487. Require an
  automatic valid restart or the deliberately specified latched-off state;
  no partially powered processor or modem state is acceptable.
- Measure RTC startup margin and crystal drive with a suitable low-loading
  method, keeping normal drive within Epson's 0.01–0.5 uW operating range.
  Verify 32.768 kHz tuning over temperature, including actual stray loading;
  22 pF capacitors alone do not establish the 12.5 pF crystal load.

### Processor analog and IO supply measurements

- Check all processor supply balls against the selected IO voltage map before
  programming. Confirm FLASH_VOL_SEL is physically HIGH for 1.8 V VCCIO2;
  SD-IO voltage must track its regulator while SD card power stays at 3.3 V.
- Measure PLL and combo-PHY 0.9 V ripple below 20 mV and 1.8 V ripple below
  50 mV at the device bypass pads. USB2-PHY limits are 25 mV, 50 mV and
  200 mV at 0.9 V, 1.8 V and 3.3 V respectively. Measure hot DC drop and
  transient response across both USB filter beads; their room-temperature
  DCR and nominal capacitance do not establish a hot operating guarantee.
- Bound PMUIO and peripheral IO loads, including pull-ups and exposed pins.
  Include those loads, PMIC self-consumption and buck losses in the thermal
  calculation; the current 0.76425 W analog-LDO subtotal is incomplete.
- Verify the 14 unused display/camera/PCIe3 supply balls remain at GND and
  the corresponding DTS nodes are disabled. Boot and recovery must work with
  those PHYs unpowered. Check active USB3/PCIe2 operation simultaneously.

### Processor oscillator

- Measure Y570 frequency after assembly and tune C570/C571 from their initial
  20 pF values. The 2 pF combined parasitic assumption must be checked against
  the final layout. Use a low-capacitance probe or buffered clock observation;
  a conventional passive probe can stop or detune the oscillator.
- Check cold/hot startup at minimum and maximum allowed oscillator supply,
  including repeated power cycling. Measure crystal drive and keep it at or
  below the conservative 100 µW limit; retain Rockchip's 22 Ω series resistor
  and 1 MΩ feedback unless a documented characterization justifies a change.
- Verify grounding of case pads 2/4 and U1 AB24 TVSS. Verify firmware uses the
  internal PVTM low-speed clock with external CLK32K_IN disconnected.

### Fixture records

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

## eMMC checkpoint follow-up

Verify storage supply order, discharge and IO behavior on both startup and
brownout after completing the source review. During controlled provisioning,
check 3.3 V and 1.8 V rise times against 35 ms and 25 ms limits respectively.
Require both supplies valid before commands. For unconditional power-cycle
recovery, hold VCCQ below 0.5 V for more than 1 ms; VCC alone is not monitored
in sleep. Record actual EXT_CSD power-class fields before selecting bus speed.
The present rail order is permitted by JESD84-B51 sections 10.1.2/10.1.3.
During controlled provisioning,
enable EXT_CSD RST_n_FUNCTION=1: the manufacturer's default disables the
hardware reset pin. Verify reset, boot, HS200 timing and sustained read/write
under concurrent system load and temperature. Do not provision permanent
write protection, RPMB keys or partition settings without the final procedure.
The D0/GND service pads follow Rockchip's power-on MaskROM procedure; release
the short after USB enumeration. Normal recovery controls and USB connector
are not yet captured. Keep VSF1–4 pads isolated from application circuits.

## Console fixture connection

J620: 1=GND, 2=board TX -> adapter RX, 3=board RX <- adapter TX,
4=adapter 3.3V output (>=5mA available). Do not connect an adapter power output
to a system rail. Use 3.3V TTL, not RS-232. The initial target is1.5Mbaud 8N1;
confirm the programmed bootloader's baud rate and <=50pF total line loading.
Verify idle high with either endpoint unpowered, repeated cable insertion,
continuous bidirectional traffic and board power cycling. Measure off-state
leakage into VCC1V8_PMU; U7's published Ioff is2uA maximum per port through85C
under its stated zero-supply test conditions. Qualify partial-ramp behavior
separately. System ESD testing remains part of the final interface validation.

Recovery-port qualification: resolve dedicated VBUSDET HIGH/LOW/leakage bounds
and S0/PHY partial-supply behavior before release. On hardware, exercise host
attached before power, attached after power, unplug, shutdown, brownout and
reset; measure both rails for injection, detector voltage and USB enumeration.
Verify both USB-C orientations, Loader/MaskROM operation and USB2 eye quality.
Use independent board power; this connector must not source the system rail.

Verify all three service buttons: normal boot with RECOVERY released; Loader
with RECOVERY held through startup/reset and released after USB recognition;
RESET asserted until release without rail shutdown; POWER short/long presses
using explicitly recorded RK809 debounce, shutdown and restart settings.
Verify released ADC level tracks VCC1V8_ANLG and no service input injects power.
