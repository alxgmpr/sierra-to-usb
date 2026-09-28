# Sierra / Quectel 2.5GbE PoE modem appliance

The project restarted on 2026-09-28 to reduce cost. **CM4 is retired.**
The current requirements and architecture gates are in [REQUIREMENTS.md](REQUIREMENTS.md).
The replacement is in architecture qualification; no replacement CAD or selected
MCU/data path exists yet. It is not ready for fabrication.

The user-facing goal is a cellular WAN appliance: with a supported modem,
antennas and provisioned SIM installed, plug in one PoE Ethernet cable and obtain
a WAN connection without an external USB host or routine manual intervention.

## Preserved work

- [CM4 checkpoint](full-adapter/cm4/CHECKPOINT.md): superseded, incomplete design.
- [Earlier full-adapter work](full-adapter/README.md): historical CM4/RK3568 research.
- [Legacy evidence](docs/legacy/README.md) and reusable libraries.
- Original carrier checkpoint: `4353916`; last CM4 checkpoint: `c81dc27`.

All previous branch work was fast-forwarded into the primary local branch,
renamed from `main` to `master`. Historical results do not validate the restart.
No commits have been pushed as part of this restart.
