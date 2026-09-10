# Resume the CM4 Lite integrated modem board

## Approved architecture change — 2026-09-10

The user approved **CM4 Lite + native gigabit Ethernet, retaining isolated PoE**
to reduce cost. This supersedes the original RK3568/discrete-memory and 2.5GbE
directions, including the old resume checklist below. Read
[CM4-HANDOFF.md](CM4-HANDOFF.md) first for the revised requirements, research,
implementation starting point and exact unfinished state. Do not continue the
obsolete RTL8125 or discrete processor circuits as the current design.

The user requested this checkpoint and a new-session `/goal` prompt. The CM4
carrier has **not yet been captured or routed**. Preserve the existing RK3568
CAD and checks as historical work; their results do not validate CM4 hardware.
The remainder of this file is the previous RK3568 checkpoint for reference.

## Historical RK3568 continuation (superseded)

Continue `/Users/alex/sierra-to-usb` on `codex/full-adapter`. Read the original
objective at `/Users/alex/.codex/attachments/9070579f-f60d-47d5-8fe5-bbe63ea3adf6/pasted-text-1.txt`
and the repository README, QUALIFICATION, TEST-PLAN, cad/README and research.
The user requested a deliberate checkpoint and a new prompt, not goal completion.
Preserve all prior milestones. Never push, buy or order. Check git status and
coordinate with existing tasks before editing. At checkpoint, other tasks were
idle; do not touch `/Users/alex/nandapters`, its `nandapters-router` container,
or shared KiCad windows with stale projects. Work through files and KiCad CLI.

## Saved implementation

The hierarchy has 29 pages including root: 1 GiB DDR3, RK3568B2 core/PMU/IO/PHY
supplies, RK860-0 CPU regulator, RK809-5 bucks/LDOs/controls/RTC, processor
control/boot straps, 24 MHz crystal, SanDisk SDINBDG4-8G eMMC, console/recovery/buttons,
and RTL8125BG supplies, local bypass,25MHz clock/straps, PCIe data/reference clock,
M1 control isolation and180–420ms startup reset qualification.
All prior symbols remain unchanged; U14FXMA2102L8X, U15SN74LVC1G07DCKR and
U16TPS3808G33DBVR are added with verified manufacturer lands/local models. `check_emmc.py`
checks 153 physical balls/pads and exported eight-bit bus, rails, bypass,
reset and service nets. Both root checkpoint hooks run against staged files.
Sixteen integration ERC findings remain: missing_input_pin 1, missing_bidi_pin 1,
missing_unit 1, power_pin_not_driven 3, isolated modem USB2 endpoint labels 2 and
isolated Ethernet MDI endpoints 8. They are unfinished work, not waivers.
There is no integrated PCB. The only board is a processor escape study with
114 escaped signals and 251 unconnected items. Do not report it as a routed system.

## Resume here

1. Finish Ethernet fast-fault reset and power-cycle re-arm. M1 control isolation
   and normal startup reset are captured in ethernet-control / ethernet-reset.
   U14FXMA2102 bridges WAKE/CLKREQ across S0/ETH rails. U15 open-drain buffer
   combines host PERST with both regulator PG outputs on ETH_RESET_CONDITION_N;
   U16 enforces180–420ms before U11 release. See ethernet-control-qualification.json.
   PG40us deglitch and TPS3808 assertion timing are typical, not500ns guarantees.
   Realtek TFAIL is triggered beyond specified tolerance by>500mV; do not invent
   a tight500ns monitor at the first microvolt outside the operating window.
   Close the fast path, >=50ms off/on interval and discharge. Verify FXMA translated
   LOW at actual loading; its guaranteed VOL test uses0.15V input whereas both
   endpoint VOL specs reach0.4V (typical curve is favorable, not a max guarantee).
   Connect eight MDI endpoints to qualified2.5G four-pair PoE magnetics next.
2. Finish eMMC electrical qualification: JESD84-B51 permits either rail order;
   current slots are compatible. Close ramps, shutdown discharge, IO back-powering
   and current allocation. Source is SanDisk DOC56-34-01508 Rev1.4, URL and pin/page
   anchors in research/emmc-pins.json. Exact
   commercial part is rated −25 to 85 °C despite distributor −40 °C listing.
   Typical currents must not become worst-case budget values. Review the local
   generated ~0.81 mm STEP and footprint; net/pad assertions already pass.
   Enable hardware reset during controlled provisioning (EXT_CSD162 default 0).
3. Resolve RK809 VDC RC brownout re-arm: retained charge can defeat automatic
   restart. Add a justified upstream PG/discharge/reset solution. Console and USB
   recovery are captured; recovery VBUS bounds/startup protection are still open.
4. Finish modem exact
   variants, profile isolation, host selection, controls and development IO.
   Qualify isolated PoE transformer and auxiliary USB-C arbitration; finish the
   actual simultaneous worst-case power and thermal budget before choosing class.
5. Finish schematic, then full placement/routing using a documented JLC stackup,
   impedance and BGA escape. Resolve all real ERC/DRC and unrouted nets, verify
   parity and 3D/mechanical clearances, and produce reviewed manufacturing files.
   Do not stop at research, partial capture or a partially routed PCB.

## Tools and layout

Python: `full-adapter/.venv/bin/python`. KiCad CLI:
`/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli` (nightly 10.99).
Generators: `tools/build_core_symbols.py`, `build_ddr_schematic.py`,
`build_emmc.py` under full-adapter. Root `tools/check_current_design.py` validates
staged snapshots; register new CAD/checkers there. Use the KiCad skills.
The root has been expanded to A2/four columns and visually reviewed.
`build/emmc-review.pdf` and its PNGs are regenerable ignored review outputs.
Official library tools live in ignored `tmp/kicad-library-tools`; eMMC model
inputs and vendoring scripts are tracked. Footprint has 153 native 0.24 mm pads
at 0.5 mm pitch, source-checked; model export filename differs from local name.

Open original objective for full requirements and continue autonomously to final
schematic, fully routed PCB, validated fabrication/assembly outputs and test plan.
Make local milestone commits. Bench-dependent characterization may remain stated;
missing CAD, electrical faults and unrouted nets cannot count as completion.

## Earlier checkpoints (superseded where the current status above differs)

JESD84-B51 is archived in reference/jesd84-b51.pdf; hash and source URL are in
emmc-qualification.json. Sections 10.1.2/10.1.3 permit either supply order.
Keep the present slots; still close ramp/discharge and brownout restart behavior.
SanDisk EXT_CSD237=DDh and POWER_CLASS=Dh provide current-class evidence;
Table133 distinguishes RMS/absolute peak limits. Rail allocation and combined
PMIC loads remain open. Do not substitute the 25C typical currents.

Console capture is now implemented as a nineteenth sheet (including root).
See console-qualification.json and check_console.py. U7 uses the processor's
1.8V PMU rail and J620's dedicated adapter-supplied3.3V domain. No connection
joins adapter power to a system supply. Fresh ERC remains six findings.
PMIC restart candidates are recorded in continuation-candidates.json; neither
candidate is selected/captured yet. Continue power/recovery integration next.

Recovery USB/detect sheets now contain J630, U8/U9/U10 and exact passives.
`check_recovery.py` checks connector orientation nets, data-switch pin mapping,
VBUS separation, processor endpoints and RSE pads. Electrical qualification is
NOT complete; see recovery-qualification.json. The two isolated labels are
MODEM_HOST_USB2_P/N for unfinished modem host selection, not ERC exclusions.
Next: finish VBUS bounds and startup gating; capture protected external analog IO. PMIC brownout restart remains unfinished.

Buttons sheet adds SW640 RECOVERY, SW641 RESET and SW642 POWER. All use
Alps SKRPACE010 C139797, exact manufacturer lands and a reviewed nominal3D
model. Recovery R640 is10k to SARADC supply VCC1V8_ANLG; reset/power have
100R series resistors. `check_buttons.py` is in the staged checkpoint checks.
Internal SARADC spare inputs are NC; protected external analog expansion remains
required. Eight ERC findings persist. This is still an unfinished integrated design.

RTL8125BG-CG library contains49 verified pins in4 functional units, a
6x6mm QFN footprint and nominal1mm-height model. It was added to the circuit below.
See rtl8125-qualification.json: exact BG is0..70C ambient,125C junction;
100mA3.3V/650mA0.95V maximum characterized currents. TPS62095 was rejected
for no forced PWM. TPS6281320QWRWYRQ1 C1849536 is a stocked adjustable
3A forced-PWM/soft-start candidate for both rails; qualify and capture next.
Do not lose the >=1MHz PWM constraint of the2024 Realtek reference.

Ethernet supplies are now captured on two pages: U12/U13 TPS6281320QWRWYRQ1,
L650/L660 SPM5030T-R47M. U12 is enabled by VCC3V3_S0 and supplies VCC3V3_ETH
(3.318V nominal). U13 takes that rail and produces VDD0V95_ETH (0.950V).
ETH_CORE_ENABLE has a47k pulldown and is now driven by U11 pin6 POW_EXT_SWR.
Both regulators force PWM at2.25MHz and use10nF C0G soft start; five22uF local
output capacitors each account for DC-bias/temperature loss and design allowance.
Manufacturer RWY0009 copper/stencil lands and maximum package-envelope STEP are
added. check_ethernet_power.py checks exported nets, pins/pads and sizing corners
and runs in staged checkpoint hooks. See ethernet-power-qualification.json for
limits and remaining tests. PG is not a tight voltage-valid monitor; hardware
reset delay and brownout sequencing remain unfinished.

## Current Ethernet controller capture

All49 U11 pins are present on three new pages. `check_ethernet_controller.py`
checks rail membership,15 local bypass capacitors, pin15-only PLL filter,
25MHz crystal/case pins, mandatory HIGH straps, no-EEPROM LOW straps, RSET,
all six RK3568 PCIe balls and four transmit coupling capacitors. R679 holds
PERSTB LOW until qualified hardware release is implemented. WAKE/CLKREQ have
Ethernet-domain pull-ups but no host connection yet. Eight MDI endpoints remain
open for the qualified magnetics; do not waive these ERC findings.

Y670 is exact YXC X322525MOB4SI C9006. Use the worse distributor temperature/ESR
bounds where they differ from the manufacturer sheet;17ppm remains for load/PCB
error within Realtek's total50ppm first-year budget. Tune20pF loads and CKXTAL2
series damping on hardware. No EEPROM/flash is fitted: provision a stable unique
local MAC before network-UP; Linux random fallback is not production identity.
See ethernet-controller-qualification.json for limits and open boot-image work.

Figure16 resolves Table35 TPERSTB-RTD: >=10ms between successive PERSTB rising
edges, not a10ms analog rise time. The separate >=100ms stable-power delay and
>=100us clock-stable/assertion constraints still need hardware implementation.
Fresh live stock is in ethernet-controller-live-stock.json. The27-page review
is build/ethernet-controller-review.pdf; root and all three new pages, crystal
and bead copper/model views were inspected. There is still no integrated PCB.

## Current Ethernet control capture

U1unit31 uses AD1PERST / AD7WAKE / AG6CLKREQ on VCCIO5; remaining27pins are NC.
U14 A0/B0 is WAKE, A1/B1 is bidirectional CLKREQ, OE follows S0 as manufacturer
note4 allows. Unlike TXS0102, it permits crossing/equal VCCA/VCCB. R700/R7011.5k
keep HIGH drop below0.324V with the16k minimum reset pulldown; use functional M1
mux and disable internal pulls in firmware. R70247k holds host PERST LOW.

U15 input tolerates the powered host with Ethernet off. Its output, U12PG/U13PG,
R653/R663 and TP651/TP661 now share one condition net (the old separate PG names
are removed). U16SENSE/VDD use ETH3.3, CT viaR703100k selects300ms typical,
180–420ms guaranteed delay. R70410k releases PERST with originalR67947k down;
worst HIGH2.659V. Fast-fault timing remains open. Current Linux source toggles
reset GPIO low, enablesLTSSM, delays then drives high; final DTS polarity,
clock/ASPM and discovery with420ms added delay must be verified in the image.

`check_ethernet_control.py` checks19newIC physical pins, three M1 balls, all control
nets, rail separation, resistor corners and three manufacturer footprints. It is
registered in both staged hooks. Reviewed working PDF:build/ethernet-control-review.pdf,
29pages (control22,reset29,PG14,PCIe15,root1). Footprint copper/model review lives
in ignored build/ethernet-control-* files and is not the system PCB. KLC exceptions
are retained assembly fields, visibleU15NC, exact onsemi rectangular lands and
project-relative models. No new ERC exclusions;16integration findings remain.
