# Integrated full adapter

Status: component and architecture qualification in progress. This directory is
the sole current design location. There is no released schematic, PCB, BOM or
manufacturing package yet. The old boards' validation does not apply here.

Required path: M.2 modem USB3 → Linux host → independent 2.5GbE controller.
RK3568B2 with RK809-5 and an external DDR/storage subsystem is being evaluated
first; MT7981BA/A remains an alternative pending exact variant qualification.

Architecture freeze requires exact device documentation, compatible boot and
memory support, qualified power and Ethernet magnetics, and BGA escape analysis.
