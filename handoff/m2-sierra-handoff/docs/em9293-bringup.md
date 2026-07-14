---
name: em9293-bringup
description: "Sierra/Semtech EM9293 5G M.2 module bring-up — defaults to PCIe, needs pin-20/22 mod for USB; NOT compatible with the Quectel 5G2PHY"
metadata: 
  node_type: memory
  type: project
  originSessionId: c59117de-c274-4d85-b416-6ea1a38995cd
---

Sierra Wireless / Semtech **EM9293** 5G Sub-6 M.2 module (Snapdragon X62 class). Bring-up notes from 2026-07-09 session (tried in a 5g2phy, failed).

**Root problem: EM9293 defaults to PCIe mode.** The whole EM919x/EM929x family boots PCIe. To force USB enumeration, two M.2 B-key pins must be driven:
- **Pin 20 = PCIE_DIS / PCIEorUSB_SELECT → tie to 1.8V** (selects USB over PCIe)
- **Pin 22 = VBUS_SENSE → hold high** (enables USB PHY)
If not driven, module presents NOTHING on USB (no enumeration under any VID — not Sierra 0x1199, not Qualcomm QDL 0x05c6), status LED stays dark, UART silent. All confirmed observed.

**The [[5g2phy-rm551e-setup]] board is a DEAD END for the EM9293.** 5G2PHY is Quectel-targeted (RM520N/RM500Q/RM551). Quectel defaults to USB and doesn't use the Sierra pin-20 select, so the board never ties pin 20 to 1.8V → EM9293 stays in PCIe → invisible, no green LED. No reports of any Sierra module working in a 5G2PHY.

**Working USB carriers:** Sierra/Semtech EM919x/EM929x Dev Kit (PN **5304831**, confirmed works for EM9291/EM9293). OR a modded M.2-USB adapter (resistor voltage-divider pulling pin 20 to ~1.8V + pin 22 high). Generic/eBay and even stock Waveshare "USB TO M.2 B KEY" adapters FAIL — they don't drive pin 20/22.

**No SIM needed for bring-up/AT diagnostics.** Once it enumerates on USB, Sierra AT: `AT!ENTERCND="A710"` unlocks `!` cmds; `AT!GSTATUS?`, `AT!USBCOMP?`/`=` for USB composition, `AT!RESET`. On macOS Sierra presents standard CDC-ACM → `/dev/cu.usbmodem*` (unlike the RM551E's class-255 ports).

Mac USB probe: `ioreg -rc IOUSBHostDevice -w 0 | grep idVendor` (Sierra=4505/0x1199, Qualcomm-QDL=1478/0x05c6, Quectel=11419/0x2c7c).

**PROJECT (2026-07-10): building a forced-USB carrier PCB** so the EM9293 can be brought up + benchmarked vs the RM551E. Spec: `docs/superpowers/specs/2026-07-10-em9293-carrier-design.md`; build plan: `docs/superpowers/plans/2026-07-10-em9293-carrier.md` (both under /Users/alex/rbm33g-openwrt, NOT a git repo yet). **EasyEDA Pro** (switched from KiCad — whole BOM is LCSC parts, so vetted footprints + one-click JLC PCBA), JLCPCB PCBA, 4-layer.
Decisions: forced-USB (not PCIe), USB3 SuperSpeed, dual USB-C (data + PD), USB-C orientation mux, features = SIM+LEDs (NO UART — none on M.2 connector; AT is over USB CDC-ACM).
Verified from EM92XX PTS Rev1 (Doc 41114313, local PDF): VCC 3.0A peak/2.8A cont; pin6 Full_Card_Power_Off_N internally pulled-DOWN, MUST pull high to boot (this is why it's dead in the 5G2PHY); pin20 PCIE_DIS→1.8V=USB (max 2.10V, never 3.3V); pin22 VBUS_SENSE 5V-tolerant (wire host VBUS direct); USB3 TX 29/31, RX 35/37 (220nF on RX only); UIM1 SIM pins 30/32/34/36/66; WWAN_LED_N pin10.
Finalized parts: **CH224K** (LCSC C970725) PD decoy, CFG1→24kΩ=12V, VBUS→buck direct no load switch. **HD3SS3220** (LCSC C2155924) standalone-UFP CC+orientation+SS mux: PORT=GND, ADDR=NC, ENn_MUX=GND, VBUS_DET←900kΩ, VDD5←J1 VBUS, VCC33←local LDO off VDD5. Buck ~TPS54560 12V→3.3V/4A.
