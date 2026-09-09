"""Reviewable corner arithmetic, not a switching model or a bench result."""
from pathlib import Path
import itertools
import json

OUT = Path(__file__).resolve().parents[1] / 'carrier/build'

# Component limits are deliberately separated from design allocations below.
# REF3312 initial 0.15%, TC 30 ppm/C over 100 C; add 0.05% ageing allowance.
ref_error = .0015 + .003 + .0005
# Divider resistors: 0.1%, 25 ppm/C, 100 C from room temperature.
divider_error = .001 + .0025
# CSM2512 0.1%, 15 ppm/C; add its specified 0.2% load-life test change.
shunt_error = .001 + .0015 + .002
gain_error = .002 + .0007
# INA input: 15 uV offset + 8 uV drift + PSRR/common-mode allowance.
input_offset = 35e-6
opamp_offset = 60e-6 # 15uV initial + supply/temperature/lifetime allowance; latter is conditional

limits = []
for sr,st,sb,ss,sg,so,sa in itertools.product((-1,1), repeat=7):
    vref = 1.25 * (1 + sr*ref_error)
    rt = 41200 * (1 + st*divider_error)
    rb = 56200 * (1 + sb*divider_error)
    threshold = vref * rb / (rt+rb) + sa*opamp_offset
    gain = 25 * (1 + sg*gain_error)
    shunt = .010 * (1 + ss*shunt_error)
    limits.append((threshold/gain + so*input_offset)/shunt)
imin,imax = min(limits), max(limits)

# LTC3310S full-temperature reference 495..505 mV; divider 0.1% + 10ppm/C x 100C.
rtop=56200+402  # R401 Panasonic10ppm + R411 Yageo25ppm, each0.1%.
rtop_error=.001+100*(56200*10e-6+402*25e-6)/rtop
vmin = .495 * (1+rtop*(1-rtop_error)/(10000*1.002)) - 20e-9*rtop
vmax = .505 * (1+rtop*(1+rtop_error)/(10000*.998)) + 20e-9*rtop
rows = []
for vin in (4.0,4.25,4.5,4.75,5.0):
    path_r = .045 + .010*(1+shunt_error) + .005
    available = vin*imin - imin**2*path_r
    # These are explicit engineering allocations, NOT guaranteed IC maxima.
    auxiliary_w = .12
    buck_loss_w = .55
    load_w = vmax*3
    margin = available - auxiliary_w - buck_loss_w - load_w
    rows.append(dict(vbus_V=vin,regulated_load_W=load_w,
        path_loss_W=imin**2*path_r,auxiliary_allocation_W=auxiliary_w,
        buck_loss_allocation_W=buck_loss_w,margin_W=margin,
        dropout_headroom_V=vin-imin*path_r-vmax))

result = {
    'status':'CONDITIONAL analytical envelope; loss, component and loop gates OPEN',
    'input_limit_min_A':imin,'input_limit_max_A':imax,
    'upstream_current_reserve_A':.010,
    'total_max_steady_current_A':imax+.010,
    'rail_min_V':vmin,'rail_max_V':vmax,
    'allocated_carrier_drop_V':.080,'allocated_negative_ripple_V':.050,'maximum_negative_steady_ripple_for_supervisor_V':.020,
    'module_min_after_allocations_V':vmin-.080-.050,
    'connector_drop_basis':{'contact_initial_max_ohm':.055,'contact_endurance_change_ohm':.020,'Quectel_supply_contacts':5,'ground_contacts_excluding_solder_tabs':11,'at_3A_V':3*.075*(1/5+1/11),'pcb_supply_plus_return_allowance_V':.010,'note':'Equalized distribution required; check individual pin current and socket temperature. 80mV allocation includes both contact paths and PCB.'},
    'component_temperature_span_from_25C_C':100,
    'rows':rows,
    'startup':{
        'LTC3310S_CSS_nominal_F':1e-6,
        'CSS_effective_factor_min':.65,'CSS_effective_factor_max':1.30,'charge_current_min_A':7e-6,'charge_current_max_A':13e-6,
        'soft_start_min_s':.65e-6*.495/13e-6,
        'soft_start_max_s':1.30e-6*.505/7e-6,
        'total_output_capacitance_design_ceiling_F':.0022,
        'maximum_capacitor_charge_current_A':.0022*vmax/(.65e-6*.495/13e-6),
        'module_load_rule':'Hold FCPO low and USB isolated until rail stable and >100ms startup guard elapsed',
    },
    'storage':{
        'MPN':'T530D227M006ATE005','count':4,
        'polymer_capacitance_nominal_F':880e-6,
        'polymer_capacitance_initial_min_F':704e-6,
        'polymer_capacitance_after_endurance_min_F':563.2e-6,
        'temperature_capacitance_factor_allocation':.90,
        'polymer_capacitance_analysis_min_F':506.88e-6,
        'bank_ESR_initial_max_ohm':.00125,
        'bank_ESR_after_endurance_max_ohm':.0025,
        'temperature_ESR_factor_allocation':2.0,
        'bank_ESR_analysis_max_ohm':.005,
        'temperature_factors_status':'Engineering allowances; confirm with manufacturer curves and measurements. Endurance limits are conditional qualification tests.',
        'step_stress_A':3,
        'charge_deficit_for_50mV_after_ESR_C':506.88e-6*(.050-3*.005),
        'full_3A_deficit_time_for_50mV_s':506.88e-6*(.050-3*.005)/3,
        'note':'Time is a ZERO incremental-converter-current envelope, not a modem burst duration. Integrate actual load minus converter current.',
        'ripple_current_initial_limit_each_45C_A':7.1,
        'ripple_current_limit_each_105_to_125C_A':7.1*.25,
        'maximum_operating_voltage_at_125C_V':6.3*2/3,
        'maximum_output_capacitor_plus_module_budget_F':.0022,
        'maximum_polymer_bank_with_initial_and_endurance_positive_tolerance_F':880e-6*1.2*1.1,
        'bleeder_ohm':330,'bleeder_max_power_W':vmax**2/(330*.99),
        'discharge_2p2mF_to_0p1V_s':.0022*330*1.01*__import__('math').log(vmax/.1),
        'discharge_rule':'POWER off / detach, verify TP505 <0.1V before changing modules or profile. 10s nominal service wait is not a substitute for measurement.',
    },
    'recharge':{
        'rail_recharge_after_50mV_drop_J':.5*506.88e-6*(vmax**2-(vmax-.05)**2),
        'lowest_line_conditional_surplus_W':rows[0]['margin_W'],
        'minimum_recharge_time_after_50mV_at_full_DC_load_s':(.5*506.88e-6*(vmax**2-(vmax-.05)**2))/rows[0]['margin_W'],
        'repeated_event_rule':'Average deficit energy per period must remain below the available surplus; capacitance cannot cover sustained overload. Duration/frequency must come from measured module activity.',
    },
    'loop_model':{'file':'loop-sensitivity.json','selected_R403_ohm':100000,'selected_C408_F':4.7e-9,
        'scope':'Exploratory averaged small-signal model; typical IC gains and assumed inner pole; no nonlinear current-limit handoff or switching model.'},
    'unverified':[
        'The 0.55W buck loss allocation must be demonstrated at 4V and hot corners; typical RDS is not a guaranteed maximum.',
        '0.12W auxiliary allocation includes the34.9mW bleeder; itemized bound is in auxiliary-budget.json and retains explicitly identified unverified hot-current allowances.',
        'Exact capacitor C/ESR/bias/temperature, total module capacitance and shunt package qualification.',
        'Both loops, anti-windup recovery, startup, saturation and current-limit overshoot require simulation and bench verification.',
        'Reference long-term allowance is an assumption; lifetime specifications are conditional tests, not arbitrary field-life guarantees.',
        'No instantaneous 3A ceiling is claimed; switching current and loop delay require USB-source transient validation.',
    ],
}
OUT.mkdir(exist_ok=True)
(OUT/'replacement-power-budget.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
