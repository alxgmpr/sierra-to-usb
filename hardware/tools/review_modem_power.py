#!/usr/bin/env python3
"""Analytical design corners, not a measured regulator stability/thermal result."""
import argparse, cmath, itertools, json, math
from pathlib import Path
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
vout=.8*(1+36.3/10)
frequencies=[100*10**(i*3/700) for i in range(701)]
corners=[]
# TI SLVS949F section 7.3.17 uses gmps=16; section 7.3.18 uses 12. Evaluate both.
# MLCC range is a sensitivity assumption, NOT a manufacturer guaranteed DC-bias value.
for gm,raw,bulk,rf,esr,load,fs in itertools.product([12,16],[20e-6,40e-6,72.6e-6],[176e-6,264e-6],[0,.045],[0,.015],[.05,1,5],[400e3,550e3]):
 for connected in [False,True]:
  curve=[]
  for f in frequencies:
   s=2j*math.pi*f;zc=1/(1/(1000+1/(s*100e-9))+s*1e-9)
   adm=load/vout+s*raw
   if connected:adm+=1/(rf+esr+1/(s*bulk))
   loop=.0013*zc*gm/adm*.8/vout*cmath.exp(-s/(2*fs))
   curve.append((f,abs(loop),cmath.phase(loop)))
  crossings=[]
  for first,second in zip(curve,curve[1:]):
   if first[1]>=1>second[1]:
    fraction=math.log(first[1])/(math.log(first[1])-math.log(second[1]));fc=first[0]*(second[0]/first[0])**fraction
    phase=first[2]+fraction*(second[2]-first[2]);crossings.append((fc,180+phase*180/math.pi))
  assert len(crossings)==1,(gm,raw,bulk,rf,esr,load,fs,connected,crossings)
  fc,pm=crossings[0];assert pm>45 and fc<fs/10,(fc,pm)
  corners.append({'gm_A_per_V':gm,'raw_uF':raw*1e6,'bulk_uF':bulk*1e6,'efuse_ohm':rf,'bulk_ESR_ohm':esr,'load_A':load,'switch_Hz':fs,'efuse_on':connected,'crossover_Hz':fc,'phase_margin_deg':pm})
def divider(reference,top,bottom,tolerance):
 return [reference[0]*(1+top*(1-tolerance)/(bottom*(1+tolerance))),reference[1]*(1+top*(1+tolerance)/(bottom*(1-tolerance)))]
report={'basis':'TPS54620 SLVS949F sections 7.3.17/18 and 8.2.2.10; simplified current-mode model. Independent component network with eFuse and polymer branch.',
 'limitations':['No slope compensation, parasitic L, capacitor aging, unknown modem capacitance, control-loop mode changes or nonlinear eFuse dynamics.','Raw MLCC 20–72.6uF is a sensitivity assumption; confirm minimum effective bank capacitance from vendor curves and bench.','Nominal transconductance values are not guaranteed process/temperature bounds.','Positive analytical margin does not establish physical stability, burst droop or thermal suitability.'],
 'compensation':{'R_ohm':1000,'C_series_F':100e-9,'C_parallel_F':1e-9},'corner_count':len(corners),
 'worst_phase_corner':min(corners,key=lambda c:c['phase_margin_deg']),
 'crossover_range_Hz':[min(c['crossover_Hz'] for c in corners),max(c['crossover_Hz'] for c in corners)],
 'regulator_V_nominal':vout,'regulator_resistor_reference_corners_V':divider([.792,.808],36.3,10,.001),
 'efuse_OVLO_corners_V_excluding_input_leakage':divider([1.183,1.223],237,100,.01),
 'rail_monitor_falling_corners_V_excluding_25nA_leakage':divider([.405*.98,.405*1.02],330,47,.001),
 'efuse_trip_corners_A_scaled_from_549R_table':[5.4*549/(562*1.001),6.6*549/(562*.999)],
 '5A_efuse_max_drop_V':5*.045,'5A_efuse_max_loss_W':25*.045,
 'connector':'MDT420B01411: 1A/power contact continuous at 25C in still air with <=30C rise. Hot/current-sharing qualification required.',
 'discharge_100R_initial_W':vout*vout/100,'discharge_220uF_nominal_time_to_0V1_s':100*220e-6*math.log(vout/.1),
 'release_holds':['Current EM919x/EM92xx/RM551E controlled guides and model-specific peak/RF accessory budgets','Measure regulator loop with eFuse on/off and all fitted cap banks','Measure VCC at module contacts under RF burst, startup, fault and shutdown','Qualify connector and eFuse thermals; enforce negotiated PoE budget in firmware']}
a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(report,indent=2)+'\n')
print(f"Analytical sensitivity: {len(corners)} corners, minimum margin {report['worst_phase_corner']['phase_margin_deg']:.1f} degrees. Physical verification pending.")
