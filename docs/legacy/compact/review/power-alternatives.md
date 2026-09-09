> Historical evidence from superseded designs. See the [current full adapter](../../../../full-adapter/README.md). Circuit status and artifact paths below refer to the historical checkpoint, not the replacement.

# Power architecture screening - NOT layout release

The existing two-stage candidate is rejected for the required low-line 3A continuous capability. A direct buck is a useful next architecture to develop, but is not yet selected or independently qualified. This worksheet does not prove that the one-port requirement is fundamentally impossible.

Candidate rail 3.3941 V; 3A capability requires 10.182 W. Existing input current lower bound 2.6106 A. Reserve 0.25W upstream for complete CC/mux/logic/protection; this is an allocation, not a component-by-component verified budget. Hot path 56mOhm is an assumption.

| Architecture | Board VBUS | Assumed efficiency | Available modem W | Margin against 3A |
|---|---:|---:|---:|---:|
| existing_two_stage | 5.00 | 0.828 | 10.285 | +0.102 |
| direct_buck_same_current_floor | 5.00 | 0.920 | 11.428 | +1.245 |
| direct_buck_95pct_sensitivity | 5.00 | 0.950 | 11.800 | +1.618 |
| existing_two_stage | 4.75 | 0.828 | 9.744 | -0.438 |
| direct_buck_same_current_floor | 4.75 | 0.920 | 10.827 | +0.645 |
| direct_buck_95pct_sensitivity | 4.75 | 0.950 | 11.180 | +0.998 |
| existing_two_stage | 4.50 | 0.828 | 9.204 | -0.978 |
| direct_buck_same_current_floor | 4.50 | 0.920 | 10.227 | +0.044 |
| direct_buck_95pct_sensitivity | 4.50 | 0.950 | 10.560 | +0.378 |
| existing_two_stage | 4.25 | 0.828 | 8.664 | -1.519 |
| direct_buck_same_current_floor | 4.25 | 0.920 | 9.626 | -0.556 |
| direct_buck_95pct_sensitivity | 4.25 | 0.950 | 9.940 | -0.242 |
| existing_two_stage | 4.00 | 0.828 | 8.123 | -2.059 |
| direct_buck_same_current_floor | 4.00 | 0.920 | 9.026 | -1.157 |
| direct_buck_95pct_sensitivity | 4.00 | 0.950 | 9.320 | -0.862 |

At these conservative assumptions the existing architecture needs 4.953V at the board merely to sustain the 3A load. Cable drop occurs before this boundary. More capacitance changes run time, not this equilibrium.

The direct-buck rows intentionally retain the LTC current floor for comparison; they are not a proposal to bypass the LTC3128 while retaining its current regulation. Its charger loop cannot limit arbitrary external load current. A replacement needs its own total-input current regulation and reverse/inrush protection.

A direct buck with local capacitors would supplement a LIVE source during its control-loop response: i_cap = i_load - i_inductor; dV/dt = -i_cap/C. Unlike a backup-only switchover circuit, no source detach is needed. Such local storage cannot support a long overload. Designing for 3A DC removes the need to invent a 3A burst duration. Exact local C, ESR, compensation, module C and startup remain unresolved.

TPS62816-Q1 cannot directly accept the Quectel recommendation at +20%: two 220uF parts already reach 528uF, above its 470uF total limit before MLCCs or module capacitance. A different regulator with an explicitly reviewed compensation range is needed if retaining that recommendation. LTC3616 is a screened 2.25-5.5V, 6A alternative with external compensation and an available LTspice project; no loop/model run or full selection was completed.

No manufacturer model has been run in this revision. The earlier time-step model remains an analytical approximation. A failed candidate is not released for placement.
