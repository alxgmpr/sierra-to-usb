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
There is no new schematic or routed board: ERC, schematic/PCB parity, DRC,
Gerber inspection and 3D clearance verification have **not been run**.

Reproduce the preliminary arithmetic with
`python3 full-adapter/research/engineering_screen.py` from the repository root.
This calculation is not an electrical or layout validation.
