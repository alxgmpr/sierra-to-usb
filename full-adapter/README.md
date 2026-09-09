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
power-input balls are now present; signal and boot-control capture remains open.
Other subsystems and the integrated PCB remain unfinished. See [the capture checkpoint](cad/README.md)
for its exported-net checks and six unresolved integration ERC findings. The
[processor escape coupon](studies/README.md) contains real routing and its own
DRC evidence; it is not a system design or release. Full-system ERC, schematic/PCB
parity, DRC, Gerber inspection and 3D clearance verification have **not passed**.

Reproduce the preliminary arithmetic with
`python3 full-adapter/research/engineering_screen.py` from the repository root.
This calculation is not an electrical or layout validation.
