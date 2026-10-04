#!/usr/bin/env python3
"""Audit native SY8089AAAC pins and prepare an unregistered typed derivative."""
from pathlib import Path
import re,csv
root=Path(__file__).resolve().parents[1]
source=(root/'reference/sy8089-native-candidate.kicad_sym').read_text()
expected={'1':('EN','input'),'2':('GND','power_in'),'3':('LX','power_out'),'4':('IN','power_in'),'5':('FB','input')}
rows=[]
def replace(m):
 old,name,number=m.group(1,2,3)
 assert number in expected and expected[number][0]==name and old=='unspecified'
 kind=expected[number][1];rows.append({'pin':number,'name':name,'electrical_type':kind,'basis':'Silergy AN_SY8089/A Rev 0.9A page 2'})
 return m[0].replace('(pin unspecified ',f'(pin {kind} ',1)
result=re.sub(r'\(pin (\w+) \w+.*?\(name "([^"]+)".*?\(number "([^"]+)"',replace,source,flags=re.S)
assert len(rows)==5 and {r['pin'] for r in rows}==set(expected)
result=re.sub(r'("Footprint"\s+)"[^"]*"',r'\1""',result,count=1)
(root/'reference/sy8089-electrical-review.kicad_sym').write_text(result)
with (root/'reference/sy8089-electrical-review.csv').open('w') as f:
 w=csv.DictWriter(f,fieldnames=rows[0],lineterminator='\n');w.writeheader();w.writerows(rows)
print('PASS: all five native SY8089AAAC pin identities match datasheet; unregistered derivative, no footprint assignment.')
