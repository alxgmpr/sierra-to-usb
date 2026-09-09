"""Energy-envelope calculations, NOT a switching/control-loop simulation.
Efficiency, path resistance, taper law and load waveforms are explicit assumptions.
Actual RF current waveform, efficiency and temperature require measurement.
"""
from pathlib import Path
import json,math,csv
ROOT=Path(__file__).resolve().parents[1]
VM=.6*(1+47.5/10.2)
IIN=11/4.02
VSET=.58*7
VUV=.405*(1+787/100)

def limits(reflo,refhi,rt,rb,tol=.001):
 return [reflo*(1+rt*(1-tol)/(rb*(1+tol))),refhi*(1+rt*(1+tol)/(rb*(1-tol)))]
uv=limits(.405*.98,.405*1.02,787,100)
vc=limits(.565,.590,600,100)
# SENSE input current +/-25 nA through 787k raises worst threshold uncertainty by 19.675 mV.
uv[0]-=25e-9*787e3;uv[1]+=25e-9*787e3
cases=[dict(name='nominal',vin=5.0,rfuse=.028,ilim=IIN,eta_chg=.93,eta_buck=.95,C=2.5,ESR=.08,vset=VSET,uv=VUV),dict(name='low_line_aged',vin=4.5,rfuse=.056,ilim=IIN*.955/1.001,eta_chg=.90,eta_buck=.92,C=2.5*.9*.7,ESR=.16,vset=vc[0],uv=uv[1]),dict(name='poor_cable_aged',vin=4.25,rfuse=.056,ilim=IIN*.955/1.001,eta_chg=.90,eta_buck=.92,C=2.5*.9*.7,ESR=.16,vset=vc[0],uv=uv[1])]

def source(c,v):
 # Conservative linear approximation of datasheet's last-5% current taper.
 factor=min(1,max(.2,.2+16*(1-v/c['vset'])))
 i=c['ilim']*factor
 return (c['vin']-i*c['rfuse'])*i*c['eta_chg']

def equilibrium(c,load):
 demand=load*VM/c['eta_buck']+.02
 lo,hi=c['uv'],c['vset']
 if source(c,lo)<demand:return None
 for _ in range(60):
  mid=(lo+hi)/2
  if source(c,mid)>demand:lo=mid
  else:hi=mid
 return (lo+hi)/2

def burst(c,base,peak,duration,period=2.0,count=10):
 v=equilibrium(c,base)
 if v is None:return {'baseline_sustainable':False}
 v_initial=v;vmin=v;max_i=0;esr_energy=0;dt=.0001;t=0;recovered=None;deficit_j=0;first_end=None
 while t < count*period:
  high=(t%period)<duration
  load=peak if high else base
  p_load=VM*load/c['eta_buck']+.02
  # Solve terminal voltage = stored capacitor voltage - ESR*Icap.
  lo=v/2;hi=max(v+1,c['vset']+1)
  def residual(vt):return vt*vt-v*vt+c['ESR']*(p_load-source(c,vt))
  if residual(lo)>0:return {'baseline_sustainable':True,'trip_s':round(t,5),'reason':'ESR power limit'}
  for _ in range(32):
   mid=(lo+hi)/2
   if residual(mid)>0:hi=mid
   else:lo=mid
  vt=(lo+hi)/2
  p_def=p_load-source(c,vt)
  icap=(v-vt)/c['ESR']
  max_i=max(max_i,abs(icap));vmin=min(vmin,vt);esr_energy+=icap*icap*c['ESR']*dt
  if vt<c['uv']:return {'baseline_sustainable':True,'trip_s':round(t,5),'initial_v':v_initial,'minimum_terminal_v':vmin,'max_bank_current_A':max_i,'reason':'UV latch clears'}
  v-=icap*dt/c['C'];v=min(v,c['vset']);t+=dt
  if t<=duration:deficit_j+=max(0,p_def)*dt
  if first_end is None and t>=duration:first_end=v
  if t>duration and recovered is None and v>=v_initial-.001:recovered=t-duration
 return {'baseline_sustainable':True,'trip_s':None,'initial_v':v_initial,'minimum_terminal_v':vmin,'final_stored_v':v,'max_bank_current_A':max_i,'bank_esr_loss_J':esr_energy,'first_pulse_deficit_J':deficit_j,'recharge_to_within_1mV_s':recovered,'pulse_end_stored_v':first_end}

def startup(c):
 # Piecewise energy approximation: constant 4 A capacitor current ceiling, then input power,
 # then taper. The 4 A is the datasheet minimum linear limit, NOT a precision charge limit.
 v=0;t=0;loss=0;dt=.0001
 while v<.99*c['vset'] and t<120:
  i=min(4,source(c,max(v,.05))/max(v,.05))
  loss+=i*i*c['ESR']*dt;v+=i*dt/c['C'];t+=dt
 return {'to_99pct_seconds':t,'bank_esr_heat_J':loss,'energy_J':.5*c['C']*v*v}
summary={'classification':'engineering envelope model; not bench or switching simulation','modem_voltage':VM,'input_limit_nominal':IIN,'input_limit_upper_assumption':IIN*1.045/.999+.05,'bank_setpoint':VSET,'bank_regulation_range':vc,'uv_nominal':VUV,'uv_range_including_sense_bias':uv,'output_cap_min_F':2*150e-6*.8+3*22e-6*.8*.5,'output_cap_max_F':2*150e-6*1.2+3*22e-6*1.2,'assumptions':cases,'cases':[]}
for c in cases:
 d={'case':c['name'],'available_modem_W_full_input':((c['vin']-c['ilim']*c['rfuse'])*c['ilim']*c['eta_chg']-.02)*c['eta_buck'],'startup':startup(c),'results':[]}
 for base,peak,duration in [(2.3,3,.1),(2.3,3,.5),(2.3,4,.1),(2.3,5,.1),(3,4,.1)]:
  d['results'].append({'base_A':base,'peak_A':peak,'pulse_s':duration,'period_s':2,'count':10,**burst(c,base,peak,duration)})
 summary['cases'].append(d)
(ROOT/'build/power-budget.json').write_text(json.dumps(summary,indent=2))
lines=['# Buffered power envelope results','','Analytical time-step model only. Taper is an approximation; efficiency and path resistance are assumed, not measured.','','| Case | Available modem W | Startup to 99% (s) |','|---|---:|---:|']
for c in summary['cases']:lines.append(f"| {c['case']} | {c['available_modem_W_full_input']:.2f} | {c['startup']['to_99pct_seconds']:.2f} |")
lines+=['','| Case | Base / peak A | Pulse ms | Result for ten bursts at 2 s intervals |','|---|---:|---:|---|']
for c in summary['cases']:
 for r in c['results']:
  result='FAIL: baseline exceeds source budget' if not r['baseline_sustainable'] else (f"UV trip at {r['trip_s']:.4f} s" if r.get('trip_s') is not None else f"No trip in model; minimum {r['minimum_terminal_v']:.3f} V")
  lines.append(f"| {c['case']} | {r['base_A']} / {r['peak_A']} | {r['pulse_s']*1000:g} | {result} |")
(ROOT/'build/power-budget.md').write_text('\n'.join(lines)+'\n')
print('\n'.join(lines))
