# External RK3566 CPU supply — selection open

The NanoPi R3S LTS reference identifies an external 6 A CPU supply,
1.025 V startup, RK809 enable slot 2A. Sheet 15 uses TCS4525,
I2C0_SDA_PMIC/I2C0_SCL_PMIC and PMIC_SLEEP_H. Therefore the CPU
supply design must address runtime voltage control as well as boot sequencing.
A fixed resistor-programmed buck alone does not establish equivalent operation.
Do not silently remove voltage scaling to choose an easier circuit.

TI TPS628691ARQYR is a candidate: 2.4–5.5 V input, 6 A output,
0.4–1.675 V programmable range and 5 mV steps. Archived TI SLVSFS3B,
July 2021, describes resistor-selected startup and I2C address. 1.025 V is
representable after programming, but the startup table offers 1.00 V (133k,
address 0x43) or 1.05 V (162k, address 0x44), not 1.025 V. Neither boot
choice is qualified yet. No exact JLC catalog result was found for this
suffix; manufacturer ordering and assembly availability remain unresolved.

Required before selection/capture:

- RK3566 boot voltage limits and exact CPU operating-point requirements;
  select a startup voltage that permits CPU initialization before I2C programming.
- Verify orderable suffix, VSET/VID variant and package pinout. The PG variants
  have different startup behavior and must not be substituted blindly.
- Confirm bootloader and kernel regulator support for the exact device/address,
  runtime ramp rate and voltage transitions; a reference circuit is not software proof.
- Connect the CPU rail enable to reviewed RK809 EXT_EN sequencing, not directly
  to main 5 V if that changes the CPU startup slot.
- Budget the complete CPU input and output banks, including processor decoupling;
  verify current-limit margin, capacitor/inductor corners and shutdown/discharge.

TPS62816-Q1 and TPS62867 are useful 6 A analog-feedback comparisons but are
not frozen as substitutes for the reference's digitally controlled CPU supply.
No CPU regulator symbol or circuit has been added.

Sources: archived NanoPi R3S LTS sheets 3 and 15;
https://www.ti.com/lit/ds/symlink/tps62868.pdf, Sections 5 and 8.3;
https://www.ti.com/product/TPS62869.

## Upstream driver and voltage-limit evidence

Fetched Linux driver and binding using gh CLI at immutable revision
7704c4c5bb127673b4f0ead839919db573559e38; archived original SPDX
licensed sources and SHA-256 provenance. Driver explicitly matches
"ti,tps62869" and implements 400000 uV minimum, 5000 uV steps,
256 selectors, VOUT1 register 0x01 and software enable in register 0x03.
Thus 1.025 V maps to selector 125 (0x7D) for the 1A variant.
Device-tree binding requires a regulators child with SW node.
The driver specifies 1000 uV/us ramp delay and 3000 us enable time.
This is upstream source support, not evidence that the eventual bootloader
or selected kernel includes/configures the driver or initializes the rail.

Rockchip RK3566 hardware guide Section 2.2.2.3 explicitly calls for an
external CPU DC/DC supporting dynamic frequency/voltage scaling, keeping
reference decoupling and routing a separate feedback trace from the processor.
It calls for ripple within 60 mV and refers peak current to the separate
RK356X Power Consumption Test Report, which has not been obtained.

RK3566 datasheet V1.2 Table 3-2 lists CPU recommended voltage minimum
0.81 V, typical 0.9 V and maximum NA. Table 3-1 lists 1.2 V absolute
maximum. This does not establish 1.05 V as a qualified boot voltage;
absolute maximum must not be used as a recommended operating limit.
The available evidence closes upstream driver support and exact voltage
representation, but leaves pre-I2C startup, OPP limits and peak loading open.
