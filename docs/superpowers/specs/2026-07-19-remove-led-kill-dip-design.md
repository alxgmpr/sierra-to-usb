# Remove LED-kill gate and DIP switches — design

**Date:** 2026-07-19 · **Status:** approved scope (full removal, freed pins = NC)

## Goal

Simplify the dev-board rev: delete the killable-LED power gate and the 4-position
config DIP switch. Indicator LEDs become hardwired always-on; firmware config
moves to flash (set over USB debug) instead of physical switches. Drops 10
components — including the board's only THT hand-solder switch (SW1) and a
pending edge-placement item (SW2) — and frees 5 RP2040 GPIOs.

## Exact removal list (netlist-verified 2026-07-19, `scratchpad/pre-simplify.net`)

**LED-kill gate (mcu sheet):** SW2 (LED_KILL, PCM12), Q33 (DMG3415U-7 P-FET),
Q35 (2N7002), R82 (100k), R84 (10k).

**DIP bank (mcu sheet):** SW1 (DIP-4, LCSC C99418, HAND), R88/R89/R91/R90
(100k pull-ups on DIP0/1/2/3 respectively).

**Nets deleted:** `DIP0–DIP3`, `LED_EN_CTL`, `/MCU/N_LEDKILL_GATE`,
`/MCU/N_SW2_KILL`, `LED_PWR`.

## Rewiring — LED_PWR consumers → `+3V3`

Q33's source was `+3V3`, so replacing `LED_PWR` with `+3V3` is electrically
identical to the LEDs-on state (minus FET Rds(on)):

| Kept part | Was | Becomes |
|---|---|---|
| R67 → D19 (WWAN LED, m2 sheet) | R67.1 on LED_PWR | R67.1 → +3V3 |
| R120 → D29 (power green, power_input) | R120.1 on LED_PWR | R120.1 → +3V3 |
| R121 → D30 (CH224K PG blue, power_input) | R121.2 on LED_PWR | R121.2 → +3V3 |
| U28 SK6805-EC15 RGB (mcu) | U28.2 (VDD) on LED_PWR | U28.2 → +3V3 |
| C77 100nF (U28 decoupling, mcu) | C77.1 on LED_PWR | C77.1 → +3V3 |

D30's cathode stays on `CH224K_PG` (it indicates PG, not power) — anode-side
rail change only. U28 data line `RGB_DI` (GP14) unaffected.

## Freed GPIOs → no_connect flags

U24 pin 12 (GP9, was LED_EN_CTL) and pins 31/32/34/35 (GP20–23, was DIP0–3).
NC-flagged in schematic; available for a future rev. Not routed to J18.

## Kept — explicitly out of scope

SW3 (BOOTSEL) and SW4 (RUN) are RP2040 essentials, untouched. All LEDs and
their series resistors stay. Board file untouched — footprint removal happens
at the user's next F8 sync (already pending for the J1 SS-pad rebind).

## Gates (same commit)

- `tools/check_nets.py` assertions referencing the deleted nets/parts updated.
- ERC = 0 errors; verify membership changes via netlist export, not geometry.
- Pre-commit hook must pass.

## Firmware impact

GP9 active-low LED kill and GP20–23 DIP reads no longer exist; the task-9
GPIO map is superseded for those pins (firmware plan not yet written, so no
code changes — just this note).

## Coordination

KiCad GUI must be closed (or all sheets saved/clean) before file edits —
stale GUI saves have clobbered sheets 3× on this project.
