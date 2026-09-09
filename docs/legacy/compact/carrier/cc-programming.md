> Historical evidence from superseded designs. See the [current full adapter](../../../../full-adapter/README.md). Circuit status and artifact paths below refer to the historical checkpoint, not the replacement.

# CC configuration and programming — development

U101 is STUSB4500LQTR, the 5 V Type-C controller. It does not negotiate PD. The address straps select I²C address **0x28**. A board with factory-default NVM must not enable the modem: its GPIO SINK_POWER function goes low for a 3 A source, which inhibits the final authorization AND gate.

Required application settings, from DS13102 Rev6 Table13:

| Parameter | Required value | Reason |
|---|---:|---|
| GPIO_CFG | `10b` / DEBUG | GPIO low excludes debug accessory; high permits normal attachment |
| SHIFT_VBUS_HIGH_LIMIT | `1010b` / 10% | Retain 5.75 V nominal CC overvoltage limit; eFuse has the tighter board protection |
| VBUS_DISCH_TIME_TO_0V | `1001b` / 9 | Retain default discharge timer |
| VBUS_DISCH_DISABLE | `0b` | Enable receptacle-side discharge through R101 |

The ST VBUS disconnect threshold is 3.2–3.4 V under its specified test condition. The 4.0 V carrier-input boundary therefore does not inherently conflict with that threshold. VSYS uses AUX_3V3. No second Rd/CC controller is present.

J102: pin1 GND, pin2 target AUX_3V3 reference, pin3 SCL, pin4 SDA. Use an open-drain 3.3 V I²C programmer with common ground. Pin2 is **not** an external power input. Power the carrier through USB-C with POWER and RUN off and no modem installed for first programming. Do not back-power either the board or a programmer through SDA/SCL or the target-voltage reference.

Use an STUSB4500L-compatible version of the ST GUI to export the configuration, then the ST NVM utility or its documented library to program it. [ST's NVM utility announcement](https://community.st.com/interface-and-connectivity-ics-52/stusb-nvm-readwriteutility-v1-01-27318) explicitly lists STUSB4500L and requires a STM32 Nucleo USB-to-I²C bridge. The announcement title says v1.01 while its attachment label says v1-00: record the actual downloaded tool version. Do not transplant a complete STUSB4500 PD image into this part.

1. Read and archive the device's original NVM and device markings.
2. Export the four settings above with the L-compatible GUI. Preserve all unrelated/reserved bytes from the correct device configuration.
3. Write once; read back and compare the full image. Archive the image, tool version and SHA-256.
4. Power-cycle and wait at least 30 ms for NVM loading before register reads. Re-read the configuration after the power cycle.
5. Verify factory/default, normal default-current, 1.5 A, 3 A, debug accessory and detach cases with a CC analyzer. Only normal 3 A attachment may produce USB_3A_OK.
6. Confirm 4.0 V operation, both orientations, slow attach, source-current downgrade and error recovery while scoping BUCK_ENABLE. The delayed RUN logic must never release from a transient authorization glitch.

The exact **L** programming reference PM0265 Rev1 (February2020) and STSW-STUSB007 example were obtained from [the device-specific example repository](https://github.com/usb-c/STUSB4500L). The example includes a 40-byte NVM array, but does not identify those bytes as this carrier's required DEBUG configuration. It is retained as reference only. Device ID alone does not distinguish STUSB4500 from STUSB4500L.

**Open:** the GUI-generated carrier image, verified reserved-byte preservation, programmer setup and all physical readback/fault tests. No image has been flashed and no arbitrary binary image is claimed qualified.
