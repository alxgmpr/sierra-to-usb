"""Exploratory averaged small-signal model; NOT an ADI model or bench validation.
Uses datasheet typical gm/ITH gain; parameter sweeps are engineering sensitivities.
No switching ripple, slope compensation, pulse skipping, clamps or diode handoff.
"""
from pathlib import Path
import json,itertools
import numpy as np
from scipy import signal
P=Path(__file__).resolve().parents[1]/'carrier/build'

def mul(a,b):return (np.polymul(a[0],b[0]),np.polymul(a[1],b[1]))
def response(rc,cc,cout,esr,gscale,kscale):
    # Laplace variable is per microsecond for numerical conditioning.
    cf=15e-12;ra=56602;rb=10000;cff=15e-12
    zc=([rc*cc*1e6,1],[rc*cc*cf*1e12,(cc+cf)*1e6,0])
    zo=([esr*cout*1e6,1],[cout*1e6,0]) # incremental current-source load: no resistive damping
    inner=([18*kscale],[1/(2*np.pi*200e3)*1e6,1])
    fb=([rb/(ra+rb)*ra*cff*1e6,rb/(ra+rb)],[ra*rb/(ra+rb)*cff*1e6,1])
    loop=mul(mul(mul(zc,inner),zo),fb)
    loop=(np.asarray(loop[0])*400e-6*gscale,loop[1])
    f=np.logspace(1,6,5000);w=2*np.pi*f*1e-6
    _,h=signal.freqresp(signal.TransferFunction(*loop),w=w)
    mag=20*np.log10(abs(h));phase=np.unwrap(np.angle(h))*180/np.pi
    indices=np.where((mag[:-1]>=0)&(mag[1:]<0))[0]
    margins=[180+np.interp(0,[mag[i+1],mag[i]],[phase[i+1],phase[i]]) for i in indices]
    freqs=[float(f[i]) for i in indices]
    closed=(np.polymul(zo[0],loop[1]),np.polymul(zo[1],np.polyadd(loop[1],loop[0])))
    # Algebra includes common s factors. Cancel exact trailing zeros to avoid artificial origin poles.
    while closed[0][-1]==0 and closed[1][-1]==0:
        closed=(closed[0][:-1],closed[1][:-1])
    sys=signal.TransferFunction(*closed)
    poles=np.roots(closed[1]);stable=bool(np.all(poles.real<0))
    t=np.linspace(0,1500,3001)
    _,v=signal.step(sys,T=t)
    return dict(rc_ohm=rc,cc_F=cc,cout_F=cout,esr_ohm=esr,gm_scale=gscale,ith_gain_scale=kscale,
        stable_in_model=stable,crossover_Hz=freqs,phase_margin_deg=[float(x) for x in margins],
        step_3A_peak_droop_V=float(3*np.max(v)),step_3A_peak_rebound_V=float(-3*np.min(v)))

rows=[]
for rc,cc in [(22000,22e-9),(68000,6.8e-9),(100000,4.7e-9),(120000,3.9e-9)]:
    for cap,esr,gm,k in itertools.product([506.88e-6,1.1e-3,2.2e-3],[.0025,.005],[.75,1,1.25],[.75,1,1.25]):
        rows.append(response(rc,cc,cap,esr,gm,k))
summary=[]
for rc in sorted({r['rc_ohm'] for r in rows}):
    group=[r for r in rows if r['rc_ohm']==rc]
    summary.append({'rc_ohm':rc,'cc_F':group[0]['cc_F'],'stable_in_all_model_cases':all(r['stable_in_model'] for r in group),
        'minimum_phase_margin_deg':min(v for r in group for v in r['phase_margin_deg']),
        'maximum_step_3A_droop_V':max(r['step_3A_peak_droop_V'] for r in group),
        'maximum_step_3A_rebound_V':max(r['step_3A_peak_rebound_V'] for r in group)})
report={'scope':__doc__,'source':'LTC3310S RevF p3 typical gm400uS / ITH gain18A/V, p18 compensation guidance',
 'assumptions':['gm and ITH gain +/-25% are sensitivity ranges, NOT guaranteed bounds.',
 '200kHz inner current-loop pole is an assumed approximation, NOT a documented IC pole.',
 'Current-source load has no resistive damping; 3A ideal step is an engineering stimulus, NOT a modem burst specification.',
 'No current-limit handoff, source impedance, transport delay, buck saturation or switch-level behavior is represented.'],
 'summary':summary,'cases':rows}
P.mkdir(exist_ok=True);(P/'loop-sensitivity.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(summary,indent=2))
