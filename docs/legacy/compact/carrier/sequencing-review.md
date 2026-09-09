> Historical evidence from superseded designs. See the [current full adapter](../../../../full-adapter/README.md). Circuit status and artifact paths below refer to the historical checkpoint, not the replacement.

# Hardware sequencing review — development

The carrier uses separate POWER and RUN slide switches. Both may remain on across reconnect, in which case startup repeats automatically. There is no MCU and no software bypass of the source/profile authorization. Invalid profile or loss of the 3 A advertisement removes buck enable even when both switches are on.

## Startup and brownout

`BUCK_ENABLE = USB_3A_OK & PROFILE_OK & POWER_REQUEST`. U503 monitors VCC at the regulator output bank, upstream of socket contact drops and holds DRIVE_ALLOWED low until the rail is above its positive threshold for the capacitor-programmed interval. U504 then enables the local 1.8 V strap/FCPO supply. U506 requires both DRIVE_ALLOWED and RUN_REQUEST, then adds a second delay before releasing FCPO and enabling USB2/USB3.

TPS389033 has nominal thresholds 3.17 V falling and 3.189 V rising, with ±1% published accuracy. The nominal 3.33 V buck corner calculation yields 3.2844–3.3759 V at the regulator output. Both supervisors' SENSE and ground references must be taken at the output bank, upstream of the module socket contact drop. Even with 20 mV negative steady ripple this point remains above the 3.2209 V maximum rising threshold. The supervisor qualifies the regulator rail; it does not measure voltage on the far side of the M.2 contacts. The separate 80 mV supply-and-return distribution allocation and 50 mV transient allocation yield a module-pin minimum of 3.1544 V. Validate that voltage directly at the module, including contact sharing and temperature. A loss of the regulator rail forces shutdown; arbitrary module-side contact faults are not detected by this circuit.

For the effective capacitance bounds currently written on the schematic, C503=214.5–429 nF and C508=1.43–2.86 µF. Using the TPS3890 limits of 0.90–1.35 µA charging current and 1.17–1.29 V comparator threshold gives C503 delay 0.186–0.615 s and C508 delay 1.239–4.099 s, plus the small IC propagation delay. These bounds are **conditional on the selected capacitors meeting the effective bias/temperature/aging limits** in passive-review.md. The first delay exceeds Sierra's 100 ms guard before externally supplied logic voltages. The second delay lets the Sierra straps settle before FCPO release and prevents an immediate RUN restart after a normal STOP. Verify the minimum MR pulse and CT discharge behavior with contact bounce; do not infer a guaranteed complete shutdown from a momentary switch glitch.

Q501 clamps FCPO to ground until RUN_ALLOWED. A 10 kΩ pull-up supplies the released level from the delayed 1.8 V rail. Q502 only pulls RESET down; the modem owns its released voltage. DMG1012T has specified on-resistance at 1.8/2.5 V gate drive; its top-view gate/source/drain positions were checked against DS31783 Rev8-2. Carrier footprint pad convention is 1=G, 2=S, 3=D.

## Normal shutdown

- **RM520N-GL V1.0:** send `AT+CFUN=0`, wait for `OK`, then move RUN to STOP. Leave POWER on for at least 900 ms and confirm shutdown before turning POWER off or unplugging. The board cannot infer completion of the host command.
- **EM9190 Rev8:** after the modem has booted, move RUN to STOP. Wait for PLA_S2# to go low (documented maximum 8 s), then remove power. TP509 exposes this status only through the Sierra profile bridge 17–18. Quectel's reserved pin 28 stays isolated.
- Loss of USB authorization, an invalid profile, supply fault or unplug overrides graceful shutdown. Firmware/data integrity under abrupt loss remains a bench/firmware qualification item.

The profile connector has expanded to 20 contacts. Sierra bridges 1–2, 3–4, 5–6, 7–8, 9–10, 11–12, 15–16 and 17–18. Quectel bridges only 13–14 and 15–16. Contacts19/20 remain unused. Exact keyed mating hardware and harness construction are defined in profile-assembly.md; first-article retention and partial-insertion behavior remain validation items. Change module and profile only with USB disconnected.

## Reset and RF disable

LTC6993HS6-3 is the falling-edge, non-retriggering version. DIV code6 sets N=262144 and positive output polarity. RSET=95.3 kΩ gives 499.65 ms nominal; confirm final timing-resistor tolerance/drift against the current RevF timing limits before release. Holding the button does not prolong the pulse. This reset is a recovery action, not the normal shutdown procedure. RF DISABLE grounds pin8 only and adds no pull-up.

## Evidence and remaining tests

Sources: [TI TPS3890 SLVSD65A](https://www.ti.com/lit/ds/symlink/tps3890.pdf), [ADI LTC6993 RevF](https://www.analog.com/media/en/technical-documentation/data-sheets/ltc6993-6993-1-6993-2-6993-3-6993-4.pdf), [Diodes DMG1012T](https://www.diodes.com/datasheet/download/DMG1012T.pdf), Sierra 41113174 Rev8 USB startup/shutdown diagrams and Quectel RM520N-GL Hardware Design V1.0 power-off section (local source register).

Exported numeric-pin tests cover the captured topology. No physical timing, rail-fault, contact-bounce, off-state leakage, reset-width or vendor shutdown test has been run. Check both switch positions at cold attach, all profile codes, a floating/unprogrammed CC GPIO, source-current downgrade, slow ramps and fast detach. Scope VCC, 1.8 V, FCPO, USB_MUX_OFF and RESET simultaneously.
