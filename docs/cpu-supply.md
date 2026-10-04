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

## Reference TCS4525 investigated

The manufacturer's current TCS4525 page links to Ver.1.1 May 26,2020,
but that download is only a one-page product summary. It advertises
6 A, 0.6–1.4 V programming in 6.25 mV steps, and WCSP-20. It does
not provide a pin table, full electrical limits or register reset values.
Archived directly from the manufacturer; PDF metadata title EUP3265
is not evidence of pin compatibility or an approved substitute.

A mirrored manufacturer-authored Ver.1.0 May 26,2015 full datasheet
is archived separately and clearly marked as older. Its reset-default
section specifies VOUT_VSEL0 = 1.025 V and VOUT_VSEL1 = 1.15 V,
with PWM/PFM auto mode for VSEL0 and forced PWM for VSEL1. This
explains how the reference design can obtain 1.025 V without first
programming I2C; selecting VSEL0 is essential. However this older
document identifies the regulator as 5 A. Do not treat its electrical
limits or pin table as a complete verified specification for the current
6 A version without manufacturer revision reconciliation.

Direct catalog lookup C7501359 identifies TCS4525_WT, WCSP20,
5 A and zero indexed stock, despite exact-MPN lookup returning no
result. No procurement decision is made from this stale/indexed stock.

The upstream Linux fan53555 driver at the same pinned revision
explicitly matches tcs,tcs4525, accepts chip ID 12 and sets a 600000 uV
minimum with 6250 uV steps. Driver source is archived with original
SPDX license. Target bootloader/kernel configuration remains unverified.

The reference part now has stronger boot-voltage evidence than the TI
alternative, but a complete current 6 A datasheet and exact orderable
availability are still required before symbol/circuit selection. Neither
source discrepancy nor missing stock justifies reducing CPU rail scope.

Sources: https://www.tctek.cn/en/product/tcs4525/ and its linked
https://www.tctek.cn/wp-content/uploads/2025/03/TCS4525_Ver.1.1_compressed.pdf;
older manufacturer-authored PDF mirrored at
https://datasheet4u.com/pdf/1549392/TCS4525.pdf.

## Pinned CPU and GPU operating points

Archived upstream rk3566.dtsi at the same immutable Linux revision as
our regulator drivers. CPU targets are 0.85V at 408/600/816MHz, 0.90V
at 1104MHz, 1.025V at 1416MHz, 1.10V at 1608MHz and 1.15V at
1800MHz. The source specifies 1.15V maximum in each CPU voltage
triplet. A 1.05V startup candidate is inside the low-frequency triplets,
but this is software operating-point evidence rather than a manufacturer
boot limit or proof of the actual BootROM/DDR-loader CPU clock.
We still need the selected boot chain's pre-regulator initialization state.

GPU targets are 0.85V at 200/300/400MHz, 0.90V at 600MHz, 0.95V
at 700MHz and 1.00V at 800MHz. Therefore captured RK809 BUCK2's
0.90V startup setting does not qualify an 800MHz GPU operating point.
Firmware/kernel must configure voltage before increasing frequency and
lower frequency before decreasing voltage. Final regulator device-tree
bindings, enabled OPPs and bootloader ordering remain implementation work;
no high-frequency operation is claimed from the startup rail capture.

Evidence: hardware/reference/linux-rk3566-opp.dtsi, with original license
and source hash recorded in hardware/reference/sources.json.
