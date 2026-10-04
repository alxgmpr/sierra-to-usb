# Complete appliance schematic — in progress

Authorized 2026-10-03. Work branch: `codex/complete-appliance-schematic`.
The original dirty checkout was copied to the isolated worktree without changing
its files. Prior recovery circuitry is retained. No procurement or fabrication.

## Scope and completion evidence

| Required block | Current authoritative state | Required before schematic completion |
|---|---|---|
| Recovery MCU, watchdog, SWD and reset outputs | Existing 27-component, three-sheet capture; native ERC/connectivity passes again on 2026-10-03 | Exact passive/connector/switch MPNs; manufacturer MCU pin audit; reset voltage margin; target-domain interface integration |
| Independent always-on supply | `hardware/always-on.kicad_sch`, 5 components, TPS62177DQCR, LPS4018-103MRC; native ERC and all five circuit-net checks pass | Capacitor effective capacitance; rail load; power fault integration; connect into final appliance hierarchy |
| RK3566 / DDR / PMIC | Archived NanoPi R3S LTS 2411 reference schematic | Exact supported RAM and DDR training route; PMIC silicon/suffix and rail sequence; all package balls checked; native capture with complete decoupling and clocks |
| Boot storage and recovery | Signed A/B and recovery requirements exist; storage not selected | Capacity budget, exact eMMC, SD/USB recovery circuit and boot strap audit |
| 2.5GbE | RTL8125BG-CG remains candidate | Exact pin/reference circuit, clocks/rails/reset/PCIe coupling and 2.5G PoE-rated magnetics; symbol and footprint checks |
| Isolated PoE | Archived TI TIDA-050023 schematic and BOM as candidate reference | Whole-appliance peak and startup budget, exact class, transformer/protection/feedback/MPS/allocation integration; isolation boundary audit |
| Modem power | Requirements only | Voltage/current envelope per model, switch/eFuse/ramp/discharge, default-off controls and fault sensing |
| EM9190 / EM9293 sockets and SIM | Older manufacturer PTS research; contacts 24/38/68 conflict with Quectel | Current controlled pin tables, complete per-model profile and power/control/SIM/USB3 capture |
| RM520N-GL / RM551E-GL sockets and SIM | RM520 guide exists; current RM551 production guide still missing | Current controlled hardware guides and per-model pin/voltage/control/SIM/USB3 capture |
| Full hierarchy and BOM | Not yet present | One integrated appliance root; exact MPN/manufacturer/footprint for every fitted component; BOM exported from native netlist |
| Visual and electrical review | Always-on draft rendered and corrected; recovery tests rerun | All sheets and circuit crops inspected, native ERC and complete critical-net assertions, manufacturer pin fidelity, footprint pad parity |

No PCB file exists. Do not start placement until the integrated schematic and
exact parts meet the criteria above. Physical throughput, thermal/EMC/isolation,
power interruption and unattended recovery remain separate qualification work.

## Always-on circuit decisions

Input is the **isolated nominal 12 V intermediate rail**, not raw PoE.
TPS62177 has 4.75–28 V operating input and fixed 3.3 V / 0.5 A output.
EN is connected to the isolated input; SLEEP to output for normal operation.
FB and NC are grounded as recommended; exposed pad, AGND and PGND connect to
local ground. VOS senses after the 10 uH inductor. PG has a 100 kR pull-up
and is not yet wired to the MCU. No downstream power enable gates this supply.

TI SLVSB35C Table 2 recommends the nominal 10 uH / 22 uF combination, assuming
approximately 20 percent component variation. The two capacitor MPNs are
**provisional until DC-bias curves establish effective capacitance**:
CL31B225KBHNNNE (2.2 uF, 50 V, X7R, 1206) and CL32B226KAJNNNE (22 uF,
25 V, X7R, 1210). Manufacturer pages identify both as mass-production products.
The originally researched Murata input capacitor was rejected after an obsolete
lifecycle indication; it is not captured.

Coilcraft LPS4018-103MRC is the current packaging variant of a TI-listed family.
Manufacturer data: 10 uH ±20 percent, 0.2 ohm maximum DCR, saturation current
1.1/1.2/1.3 A at 10/20/30 percent inductance drop; RMS 0.9/1.25 A at 20/40 C
rise. Do not use the catalog's 1.3 A number as a no-drop rating. Worst-case
switch current limit can reach 1.2 A. Transient margin and inductance at that
current still require review; this is a draft selection, not a released BOM.

Sources:
- [TI TPS6217x datasheet](https://www.ti.com/lit/ds/symlink/tps62175.pdf), pin table and application section.
- [Coilcraft LPS4018 datasheet](https://www.coilcraft.com/getmedia/31b05c96-4c4c-4498-8dbb-fe092de76bad/lps4018.pdf).
- [Samsung input capacitor](https://product.samsungsem.com/mlcc/CL31B225KBHNNN.do).
- [Samsung output capacitor](https://product.samsungsem.com/mlcc/CL32B226KAJNNN.do).
- [FriendlyElec NanoPi R3S LTS reference](https://wiki.friendlyelec.com/wiki/images/f/fd/NanoPi_R3S_LTS_2411_SCH.pdf).
- [TI TIDA-050023](https://www.ti.com/tool/TIDA-050023). Its reference Ethernet magnetics must not be inherited as a 2.5G-qualified part.

Archived PDFs and SHA-256 provenance live in `hardware/reference/sources.json`.
Catalog stock observed via PCBParts on 2026-10-03 is not reserved inventory or a
production quote. The schematic is the BOM source; do not edit exported BOMs.

## Reproduce current checks

```sh
python3 hardware/check.py --output /tmp/sierra-recovery-check
python3 hardware/check_always_on.py --output /tmp/sierra-aon-check
```

The always-on checker validates native ERC, exact membership of every circuit
net and five-component inventory, then exports SVG/PDF and BOM. It does not
verify DC bias, load margin, system integration or physical operation.
`hardware/tools/build_always_on.py` reconstructs only the new always-on draft;
it does not touch the preserved recovery sheets. Do not rerun it over manual
edits without preserving those edits first.
