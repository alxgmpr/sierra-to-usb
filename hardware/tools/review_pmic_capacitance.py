#!/usr/bin/env python3
"""Reproducible estimates from typical Samsung bias data; no corner guarantee."""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]
data=json.loads((ROOT/'reference/cl32b226kajnnn-characteristics.json').read_text())
graph=next(g for g in data if g['graphType']=='DCBias')
curve=next(c for p in graph['selectPartsList'] if p['degC']==25 for c in p['chartList'] if c['asixYOption']=='DeltaC')
points=sorted((float(p['x']),float(p['y'])) for p in curve['data'])
def loss(voltage):
 for (x0,y0),(x1,y1) in zip(points,points[1:]):
  if x0<=voltage<=x1:return y0+(y1-y0)*(voltage-x0)/(x1-x0)
 raise ValueError(voltage)
def estimate(count,voltage):
 # Do not credit positive typical capacitance change as guaranteed margin.
 return count*22*min(1,1+loss(voltage)/100)*.9*.85
output=[]
for name,count,voltage,target in [('BUCK1/2 startup',3,.9,30),('BUCK1/2 highest programmable output',3,2.4,30),('BUCK1/2 input at 5.5 V',1,5.5,10),('BUCK5 startup',3,1.8,33),('BUCK5 highest programmable output',3,3.6,33)]:
 effective=estimate(count,voltage)
 output.append({'case':name,'count':count,'voltage_V':voltage,'typical_bias_change_percent':round(loss(voltage),4),'estimated_uF_before_aging':round(effective,4),'comparison_uF':target,'remaining_loss_fraction_before_comparison':round(1-target/effective,4)})
assert output[1]['estimated_uF_before_aging']>30
assert output[2]['estimated_uF_before_aging']>10
print(json.dumps({'part':'CL32B226KAJNNNE','assumptions':'Typical 25 C bias curve, -10% initial and -15% temperature; no positive-bias credit; aging excluded; not guaranteed combined-corner or loop-stability evidence','cases':output},indent=2))
