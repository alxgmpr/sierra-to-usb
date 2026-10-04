#!/usr/bin/env python3
"""Map audited RAM identities to RK3566 LPDDR4 functions without lane swaps."""
from pathlib import Path
import csv,re
root=Path(__file__).resolve().parents[1]
soc=list(csv.DictReader((root/'pinmaps/rk3566.csv').open()))
functions={}
for r in soc:
 for f in r['manufacturer_name'].split('/'):
  if f.startswith('LPDDR4_'):
   assert f not in functions
   functions[f]=r['ball']
rows=[]
for r in csv.DictReader((root/'reference/micron-ddr-electrical-review.csv').open()):
 n=r['resolved_name'];f=None
 if re.fullmatch(r'DQ\d+_[AB]',n):f='LPDDR4_'+n
 elif re.fullmatch(r'DMI\d+_[AB]',n):f='LPDDR4_'+n.replace('DMI','DM')
 elif re.fullmatch(r'DQS\d+_[tc]_[AB]',n):f='LPDDR4_'+n.replace('_t_','P_').replace('_c_','N_')
 elif re.fullmatch(r'CA\d+_[AB]',n):f='LPDDR4_'+n.replace('CA','A')
 elif n.startswith('CK_t_'):f='LPDDR4_CLKP_'+n[-1]
 elif n.startswith('CK_c_'):f='LPDDR4_CLKN_'+n[-1]
 elif n.startswith('CKE0_'):f='LPDDR4_'+n
 elif n.startswith('CS0_'):f='LPDDR4_'+n.replace('CS0_','CS0n_')
 elif n=='RESET_n':f='LPDDR4_RESETn'
 if f:
  assert f in functions,(r,f)
  net=f
  if re.fullmatch(r'LPDDR4_(DQS[01][PN]|CLK[PN])_[AB]',f):
   parts=f.split('_');net='DDR_'+parts[-1]+'_'+parts[1]
  rows.append({'net':net,'processor_ball':functions[f],'ram_ball':r['ball'],'ram_function':n})
assert len(rows)==65
assert len({r['processor_ball'] for r in rows})==65
assert len({r['ram_ball'] for r in rows})==65
with (root/'reference/ddr-bus-map.csv').open('w') as f:
 w=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n');w.writeheader();w.writerows(rows)
print('PASS: 65 unique processor/RAM bus endpoints; no data, strobe, channel or CA swaps')
