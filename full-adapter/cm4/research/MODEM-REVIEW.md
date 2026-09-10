# Modem and SIM capture — 2026-09-10

Six new schematic sheets capture the common modem socket, explicit assembly
profiles and two protected nano-SIM sockets. The complete CM4 hierarchy now has
18 pages and 105 components, including 11 profile links marked DNP. There is
no integrated PCB. ERC has 59 isolated endpoints, five undriven signal inputs
and three undriven power inputs. These are unfinished circuits, not exclusions.

## Profiles and current contacts

The exact socket is Amphenol MDT420B01411, B key, 67 contacts, 1 A per power
contact. The manufacturer specifies the 1 A rating at 25 C still air with a
30 C maximum rise under EIA-364-70 method 2. This is not a blanket 1 A allowance
at every board ambient. Final qualification must check connector temperature,
current sharing, contact resistance and regulator protection. The exact socket
has no captured JLC or distributor stock/price; procurement is unresolved.
The 0.5 A/contact JAE SM3ZS067U410ABR1000 is insufficient for an unqualified
3 A continuous load through five Quectel power contacts. TE 2199230-4 is key E,
not B, and must not be substituted despite its attractive catalog availability.

`modem-profiles.json` is the assembly authority for this capture. Every profile
is checked using a connectivity graph of fitted links, separately from KiCad's
unconditional netlist. All links default absent; the unconfigured profile must
keep modem power disabled. Change profile only with every source removed and
the modem supply discharged.

| Profile | Fit links | Boundary |
| --- | --- | --- |
| EM9190 sub-6 / EM9191 | R200–R205 | EM9190 QTM mmWave support is not implemented |
| EM9291/9293/9291P/9293P, SIM1 | R200–R205 | Exact SKU and current power class still matter |
| EM929x external SIM2 | R200–R205 and R220–R224 | External SIM2 and 3 V capability depend on SKU |
| RM520NGLAA-M20-SGASA, SIM1/internal eSIM | None | GLAP PCIe-only variants are excluded |
| RM520NGLAA external SIM2 | R220–R224 | Only an exact SKU configured for external SIM2 |

R200–R202 add Sierra power contacts 24/38/68. These are mandatory for EM919x
and fitted for EM929x current sharing. Quectel uses pin 24 as its 1.8 V output,
pin 38 as WLAN_TX_EN and pin 68 as reserved, so all three links stay absent.
R203 applies the Sierra 1.8 V PCIe-disable strap; R204 carries USB VBUS sense;
R205 returns Sierra power-loss acknowledgement. Those three pins are reserved
on the selected Quectel modem. All eleven links use Yageo RC0603JR-070RL,
specified 1 A rated/2 A maximum and less than 50 mΩ; their thermal derating and
extra branch resistance must be included in final power/contact analysis.

SIM2 contacts 40/42/44/46/48 carry EM9190 QTM antenna outputs, including a
1.904 V supply. All five physical links are absent for EM9190 and EM9191.
Pin 65 remains unconnected in every profile: EM929x's 2 mA tuner output is not
a general logic supply. No generic M.2 PCIe connector pinout has been assumed.

The six USB data contacts have explicit module-side directions. Modem TX is
29−/31+ and RX is 35−/37+; USB2 is 9−/7+. Modem TX AC capacitors are internal;
host TX capacitors belong at the PCIe-to-USB3 controller. Native CM4 USB2 is
reserved for recovery. The actual USB3 host and power/control drivers remain
to be captured and qualified.

## SIM implementation and physical lands

Both XUNPU SMN-303-ARP7 sockets are powered only by the modem. They use 22 Ω
series resistors, 18 kΩ ±1% data pull-ups, 10 pF C0G signal bypass and 100 nF
supply bypass. The full pull-up tolerance fits Sierra's 15–30 kΩ and Quectel's
10–20 kΩ recommendations. TPD4EUSB30 protects reset, clock, data and detect;
TPD1E05U06 protects each SIM supply. The SIM2 power flag represents the module's
pin 48 through fitted R224; with R224 absent, that socket is unused/unpowered.

The card switch is closed to ground when absent and opens when inserted.
Quectel requires the matching detect configuration (`AT+QSIMDET=1,1`); verify
Sierra polarity with the selected firmware. Keep SIM paths below 100 mm and
parallel clock/data runs below 20 mm, with a ground guard. Bench validation
must include both supported SIM voltages, insertion/removal, clock quality and
rise time. Layout has not yet established any of those geometry constraints.

The ARP7 variant has no locating posts; its manufacturer drawing specifies
−25 to +85 C, despite a wider distributor temperature listing. Its seven contact
lands are 0.8 × 1.14 mm; four shield lands are 0.7 × 2.1 mm. The moving-contact
interior is an F.Cu keepout, and the ejection side has a 10 mm finger-access
outline. Stencil thickness is 0.12 mm. A filled SIM2 option must retain access.

Amphenol's drawing was inspected at its land and orientation details. The M.2
footprint origin is midway between 1.1/1.6 mm locating holes at x=−10/+10 mm.
Odd lands are y=−5.275 mm, even lands y=+2.275 mm, each 0.30 × 1.55 mm.
Pin 1 is x=−9.25 mm; pin 2 is x=−9 mm. Contacts 12–19 are absent at the key.
Two 1.2 × 2.75 mm board-lock lands connect to ground. Standoff height, module
outline, screw position and RF connector/cooling clearance still need system
mechanical integration. The socket STEP is a conservative occupied envelope.

TI DPY0002A uses two 0.30 × 0.50 mm NSMD-option lands at 0.70 mm pitch: IO1,
GND2. The three local footprints and STEP solids were rendered and inspected.
The ignored library fixture is explicitly labelled and is not the carrier PCB.
Schematic title-block encroachment, labels and off-grid wires were corrected.

## Source limits and remaining work

The captured source versions are Sierra EM919x 41113174 Rev8, Semtech EM929x
41114313 Rev7.1 and Quectel RM520N-GL Hardware Design V1.0. Source URLs and hashes
are in `modem-sources.json`. EM929x Rev7.2 and the latest Quectel guide are
sign-in restricted; their changes need reconciliation before release.

EM9190/EM9191 specified 3.3 V peak/continuous currents are 3.0/2.3 A and
2.7/2.0 A respectively. EM929x specifies 2.8 A continuous and 3 A PC2 or 5 A
PC1.5 peaks. The old Quectel guide specifies at least 3 A supply capability
but gives no universal continuous maximum. Do not turn typical consumption
into a guaranteed budget ceiling. The final regulated rail, bulk capacitors,
rise time, independent shutdown, RF controls and simultaneous power budget
remain required electrical work.

The common priced parts on these six sheets total **$1.8992 per board** for
quantities needed by ten boards, excluding J200. Each fitted profile link adds
$0.003. `modem-captured-cost.json` retains explicit price tiers and omissions.
This excludes the modem, regulators, controller, other circuits, PCB, assembly,
consignment and delivery. No actual fabrication/assembly quote was obtained.
