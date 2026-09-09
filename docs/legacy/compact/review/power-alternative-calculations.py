"""Review worksheet: explicit hypothetical efficiency envelopes, not part qualification."""
from pathlib import Path
import json
out=Path(__file__).parent
vm=.6*(1+47.5/10.2)
load=3*vm
# Existing LTC3128 current floor, including 0.1% programming resistance.
ii=(11/4.02)*.955/1.001
# Entire auxiliary allocation stays a reservation until complete circuitry exists.
aux_w=.25
rows=[]
for v in [5,4.75,4.5,4.25,4.0]:
 for name,i,r,eta in [('existing_two_stage',ii,.056,.90*.92),('direct_buck_same_current_floor',ii,.056,.92),('direct_buck_95pct_sensitivity',ii,.056,.95)]:
  available=((v-i*r)*i-aux_w)*eta
  rows.append(dict(topology=name,vbus_at_board_V=v,input_A=i,path_ohm=r,efficiency_assumed=eta,auxiliary_input_W=aux_w,modem_W=available,demand_W=load,margin_W=available-load))
req=((load/(.90*.92)+aux_w)/ii)+ii*.056
report={'classification':'Screening only. Efficiencies and hot path resistance are assumptions. No selected or qualified replacement circuit.','modem_voltage_V':vm,'three_amp_capability_W':load,'existing_two_stage_required_board_V':req,'rows':rows,'duration_policy':'No module pulse duration inferred. Require 3A continuous capability for the replacement, so 3A burst duration is not a storage-sizing assumption. Sub-100us transients still require loop/local-capacitor qualification.','capacitor_conflict':{'quectel_recommended_nominal_uF':440,'at_plus20pct_uF':528,'tps62816_max_total_uF':470,'excess_before_MLCC_and_modem_uF':58}}
(out/'power-alternatives.json').write_text(json.dumps(report,indent=2)+'\n')
lines=['# Power architecture screening - NOT layout release','','The existing two-stage candidate is rejected for the required low-line 3A continuous capability. A direct buck is a useful next architecture to develop, but is not yet selected or independently qualified. This worksheet does not prove that the one-port requirement is fundamentally impossible.','',f'Candidate rail {vm:.4f} V; 3A capability requires {load:.3f} W. Existing input current lower bound {ii:.4f} A. Reserve 0.25W upstream for complete CC/mux/logic/protection; this is an allocation, not a component-by-component verified budget. Hot path 56mOhm is an assumption.','', '| Architecture | Board VBUS | Assumed efficiency | Available modem W | Margin against 3A |','|---|---:|---:|---:|---:|']
for r in rows:lines.append(f"| {r['topology']} | {r['vbus_at_board_V']:.2f} | {r['efficiency_assumed']:.3f} | {r['modem_W']:.3f} | {r['margin_W']:+.3f} |")
lines += ['',f'At these conservative assumptions the existing architecture needs {req:.3f}V at the board merely to sustain the 3A load. Cable drop occurs before this boundary. More capacitance changes run time, not this equilibrium.','', 'The direct-buck rows intentionally retain the LTC current floor for comparison; they are not a proposal to bypass the LTC3128 while retaining its current regulation. Its charger loop cannot limit arbitrary external load current. A replacement needs its own total-input current regulation and reverse/inrush protection.','', 'A direct buck with local capacitors would supplement a LIVE source during its control-loop response: i_cap = i_load - i_inductor; dV/dt = -i_cap/C. Unlike a backup-only switchover circuit, no source detach is needed. Such local storage cannot support a long overload. Designing for 3A DC removes the need to invent a 3A burst duration. Exact local C, ESR, compensation, module C and startup remain unresolved.','', 'TPS62816-Q1 cannot directly accept the Quectel recommendation at +20%: two 220uF parts already reach 528uF, above its 470uF total limit before MLCCs or module capacitance. A different regulator with an explicitly reviewed compensation range is needed if retaining that recommendation. LTC3616 is a screened 2.25-5.5V, 6A alternative with external compensation and an available LTspice project; no loop/model run or full selection was completed.','', 'No manufacturer model has been run in this revision. The earlier time-step model remains an analytical approximation. A failed candidate is not released for placement.']
(out/'power-alternatives.md').write_text('\n'.join(lines)+'\n')
print(f'Existing candidate minimum board voltage for 3A capability under assumptions: {req:.3f} V')
