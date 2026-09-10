# Integrated full adapter

Status: **implementation incomplete; not suitable for fabrication**. This directory is
the sole current design location. There is no released schematic, PCB, BOM or
manufacturing package yet. The old boards' validation does not apply here.

Required path: M.2 modem USB3 → Linux host → independent 2.5GbE controller.
RK3568B2 with RK809-5 and an external DDR/storage subsystem is being evaluated
first; MT7981BA/A remains an alternative pending exact variant qualification.

Architecture freeze requires exact device documentation, compatible boot and
memory support, qualified power and Ethernet magnetics, and BGA escape analysis.

See [qualification findings and outstanding work](QUALIFICATION.md), the
[proposed bring-up and manufacturing test plan](TEST-PLAN.md), and
[machine-readable screening results](research/engineering-screen.json).
The current hierarchy starts at [cad/full-adapter.kicad_sch](cad/full-adapter.kicad_sch).
Its two DDR pages capture the selected 1 GiB subsystem, including voltage
references, calibration, clock termination and local bypass. A third page
captures the four processor core supply groups, bypass and all 208 ground balls.
A fourth page captures the RK860-0 CPU regulator, defaults and remote sense.
A fifth page captures the nine RK809-5 LDO outputs and their local bypass.
A sixth page captures the DDR buck with hardware 1.5008 V selection.
A seventh captures the LOGIC/GPU/NPU bucks and Kelvin feedback ties; an eighth
captures BUCK5 and the two switched 3.3 V supplies. The ninth currently
contains PMIC control, reset, RTC, auto-start RC and unused-audio terminations.
Four further pages capture processor PMU/PLL, peripheral IO and USB/combo-PHY
supplies, plus explicit unused display/camera/PCIe3 terminations. All processor
power-input balls are now present. A further processor-control page connects the
PMIC bus, reset, interrupt and sleep signals and defines the hardware boot straps.
The processor-clock page adds the 24 MHz crystal network and grounded TVSS
reference. Two eMMC pages add SDINBDG4-8G storage, eight-bit wiring, reset,
local bypass and recovery/test pads. Storage sequencing and worst-case load
qualification remain open. The external console is now captured with a fixed-direction TXU0202 and a
separately adapter-powered3.3V port. Remaining signal capture is open.
Other subsystems and the integrated PCB remain unfinished. See [the capture checkpoint](cad/README.md)
for its exported-net checks and six unresolved integration ERC findings. The
[processor escape coupon](studies/README.md) contains real routing and its own
DRC evidence; it is not a system design or release. Full-system ERC, schematic/PCB
parity, DRC, Gerber inspection and 3D clearance verification have **not passed**.

Reproduce the preliminary arithmetic with
`python3 full-adapter/research/engineering_screen.py` from the repository root.
This calculation is not an electrical or layout validation.

Recovery USB capture is on `recovery-usb` and `recovery-detect` (22 sheets total).
It includes a dedicated USB-C service port, power-off-specified data switch,
USB data ESD and a separate VBUS translator. Eight integration ERC findings
remain; recovery electrical qualification and the full PCB remain unfinished.

Physical RECOVERY, RESET and POWER buttons are captured on `buttons`;
manufacturer switch lands, nominal3D geometry and connectivity were reviewed.
