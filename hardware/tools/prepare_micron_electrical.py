#!/usr/bin/env python3
"""Prepare an unregistered native RAM derivative from audited pin identities."""
from pathlib import Path
import re,csv,collections
root=Path(__file__).resolve().parents[1]
source=(root/'reference/micron-ddr-native-candidate.kicad_sym').read_text()
audit=list(csv.DictReader((root/'reference/micron-ddr-native-ball-audit.csv').open()))
assert len(audit)==200 and len({r['ball'] for r in audit})==200
byball={r['ball']:r for r in audit}; changes=[]
def replace(m):
 old,name,ball=m.group(1,2,3);r=byball[ball]
 assert r['native_name']==name and old=='unspecified'
 resolved=r['manufacturer_name']
 if resolved=='NC': kind='no_connect'
 elif resolved=='DNU' or resolved=='ZQ0': kind='passive'
 elif resolved in {'VDD1','VDD2','VDDQ','VSS'}:kind='power_in'
 elif re.fullmatch(r'(DQ\d+|DQS\d+_[tc]|DMI\d+)_[AB]',resolved):kind='bidirectional'
 elif re.fullmatch(r'(CK_[tc]|CKE0|CS0|CA\d+|ODT_CA)_[AB]',resolved) or resolved=='RESET_n':kind='input'
 else:raise AssertionError((ball,resolved))
 changes.append({'ball':ball,'native_name':name,'resolved_name':resolved,'electrical_type':kind,'basis':'Micron Rev I Figure 5 and Table 5'})
 return m.group(0).replace('(pin unspecified ',f'(pin {kind} ',1).replace(f'(name "{name}"',f'(name "{resolved}"',1)
pattern=r'\(pin (\w+) \w+.*?\(name "([^"]+)".*?\(number "([^"]+)"'
result=re.sub(pattern,replace,source,flags=re.S)
assert len(changes)==200
(root/'reference/micron-ddr-electrical-review.kicad_sym').write_text(result)
with (root/'reference/micron-ddr-electrical-review.csv').open('w') as f:
 w=csv.DictWriter(f,fieldnames=list(changes[0]),lineterminator='\n');w.writeheader();w.writerows(changes)
print(collections.Counter(r['electrical_type'] for r in changes))
print('Prepared unregistered review derivative; no schematic or production footprint added.')
