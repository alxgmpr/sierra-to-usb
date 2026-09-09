"""Provisional geometry calculation for the explicit custom1.50mm stack."""
from pathlib import Path
import math,json
P=Path(__file__).resolve().parent
h=.18;t=.035;er=3.61;gap=.15
def z0(w,h=h):return 87/math.sqrt(er+1.41)*math.log(5.98*h/(.8*w+t))
def zd(w,h=h):return 2*z0(w,h)*(1-.48*math.exp(-.96*gap/h))
def solve(fn,target):
 a,b=.05,1.0
 for _ in range(80):
  m=(a+b)/2
  if fn(m)>target:a=m
  else:b=m
 return (a+b)/2
rf=solve(z0,50);usb=solve(zd,90)
r={'status':'Custom stack request; not a published/accepted fabrication stack. Widths are provisional.',
 'fabricator_candidate':'PCBWay advanced/custom fabrication; no contact, quote or order',
 'capability_source':'https://www.pcbway.com/advanced-pcb-capabilities.html',
 'fabricator_gate':'Published board thickness tolerance is±7% for1.0..2.5mm, which does NOT satisfy1.50±0.05. A special accepted stack or revised assembly is required. Do not use the stock service unchanged.',
 'finished_mm':1.5,'required_finished_tolerance_mm':.05,'SMA_maximum_mm':1.57,
 'layers_mm':{'F.Mask':.015,'F.Cu':.035,'prepreg1':.18,'In1.Cu':.018,'core':1.004,'In2.Cu':.018,'prepreg2':.18,'B.Cu':.035,'B.Mask':.015},
 'laminate_request':'FR408HR, construction/Dk must be confirmed by fabricator',
 'assumed_Dk':er,'outer_reference_height_mm':h,'outer_copper_mm':t,
 'model':'IPC-style closed-form microstrip approximation; no mask/roughness/etch/launch modeling',
 'RF50_width_mm':rf,'USB90_width_mm':usb,'USB_gap_mm':gap,
 'USB_h_sensitivity':[{'h_mm':v,'Zdiff_ohm':zd(usb,v)} for v in [.16,.18,.20]],
 'note':'Use vendor field solver and controlled-impedance coupon. Do not treat arithmetic as routed SI validation.'}
(P/'build/stackup-and-impedance.json').write_text(json.dumps(r,indent=2)+'\n')
print('Provisional RF width',rf,'USB width/gap',usb,gap)
