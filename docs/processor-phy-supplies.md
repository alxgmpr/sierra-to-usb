# Processor PHY supply capture plan

RK3566 guide 2.3.2.3/Figure 2-48 requires ferrite filtering on USB
0.9 V and 1.8 V supplies. It uses 120 Ω at 100 MHz, 0.03 Ω
reference beads, with 1 uF source-side capacitors and separate pin
bypass requirements. Inputs are VDDA_0V9 and VCCA_1V8; filtered
outputs are USB_AVDD_0V9 and USB_AVDD_1V8.

## Exact draft candidate

TDK MPZ1608S121ATAH0 / JLC C114770: 0603, 120 Ω ±25%
at 100 MHz, 2 A, 45 mΩ maximum DC resistance, −55 to +125 °C
including self heating. The official exact-part page reports production
status. Indexed JLC stock was 152,832 on 2026-10-04; not reserved.

Source: https://product.tdk.com/en/search/emc/emc/beads/info?part_no=MPZ1608S121ATAH0

This differs from the reference's 30 mΩ example. At 400 mA, 45 mΩ
gives 18 mV drop and 7.2 mW dissipation at the specified DCR condition.
A 0.9 V source at −5% would leave 0.837 V, above the processor's
0.81 V minimum. Combined thermal resistance, transient drop, upstream
LDO load sharing, bias-dependent impedance and damping remain to
verify. Actual PHY loads must be included with the PLL/other analog loads.
The two beads and source-side capacitors are captured on phy-power.kicad_sch.
USB OTG0/HOST1 balls 1J17 (0.9 V), 1H16 (1.8 V), and 1H18
(3.3 V) now connect to the filtered rails and direct 3V3_MAIN respectively.
C815–C817 provide one 100 nF / 25 V local bypass per ball, following
NanoPi R3S sheet 9. HOST2/3 rails remain open for separate review.

Murata BLM18PG121SN1D was considered but its manufacturer table
shows 0.05 Ω typical and 0.10 Ω maximum. The distributor's 50 mΩ
summary is not sufficient to establish the guaranteed maximum.
Both Murata and TDK raw catalog downloads returned HTTP 403 in
this session; no archived catalog or hash is claimed. The TDK exact-part
page was readable through web search and gives an explicit maximum.

Multi-PHY analog supplies additionally require 0.9 V before 1.8 V
per guide 2.5.9. The USB bead selection does not qualify Multi-PHY
sequencing or the complete processor power tree.
