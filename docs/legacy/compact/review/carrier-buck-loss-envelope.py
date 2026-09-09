"""Constituent loss allocation and headroom; deliberately not a guaranteed efficiency."""
from pathlib import Path
import json,math
P=Path(__file__).resolve().parents[1]/'carrier/build'
power=json.loads((P/'replacement-power-budget.json').read_text())
rows=[]
for entry in power['rows']:
    vin=entry['vbus_V']-entry['path_loss_W']/power['input_limit_min_A']
    vout=power['rail_max_V'];load=3.02
    # 2x the data-sheet25C typical16/4.5mOhm: an analysis allocation,
    # not a manufacturer production bound. Include copper temp coefficient.
    rp,rn=.032,.009
    rl=.0046*(1+.00393*100)
    duty=(vout+load*(rn+rl))/(vin-load*(rp-rn))
    frequency_min=1.8e6;inductance_min=.47e-6*.8
    ripple=max(0,(vin-vout-load*rp)*duty/(frequency_min*inductance_min))
    irms2=load**2+ripple**2/12
    switches=irms2*(duty*rp+(1-duty)*rn)
    winding=irms2*rl
    remaining=.55-switches-winding
    rows.append({'vbus_V':entry['vbus_V'],'buck_input_V':vin,'load_with_carrier_reserve_A':load,
        'duty_estimate':duty,'inductor_ripple_A':ripple,'inductor_peak_A':load+ripple/2,
        'switch_conduction_allocation_W':switches,'winding_loss_W':winding,
        'remaining_for_core_switching_gate_drive_and_IC_W':remaining,
        'dropout_margin_at_100_percent_V':vin-vout-load*(rp+rl),
        'passes_allocation_arithmetic':0<duty<1 and remaining>0})
report={'status':'Conditional constituent loss envelope, not simulation or measured efficiency',
 'source_switch_RDS':'LTC3310S RevF p4:16mOhm top and4.5mOhm bottom, typical only at25C.',
 'switch_resistance_multiplier':2,'multiplier_status':'Engineering allowance, not a guaranteed hot/process maximum.',
 'inductor_source':'Coilcraft XEL4030-471 drawing:4.6mOhm maxDCR25C,20% inductance tolerance; copper TC used to125C.',
 'remaining_loss_rule':'Combined measured core, switching, gate-drive and IC operating losses must fit residual; no assumed edge time or fabricated vendor efficiency.',
 'thermal_rule':'Measure die viaSSTT and surrounding component/socket temperatures on routed hardware. Datasheet42C/W requires its test-board copper; it is not a verified board thermal model.',
 'rows':rows}
(P/'buck-loss-envelope.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(rows,indent=2))
