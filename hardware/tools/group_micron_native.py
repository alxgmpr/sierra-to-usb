#!/usr/bin/env python3
"""Group audited native RAM pins; candidate remains outside production library."""
from pathlib import Path
import csv,re
root=Path(__file__).resolve().parents[1]
rows=list(csv.DictReader((root/'reference/micron-ddr-electrical-review.csv').open()))
groups=[[],[],[],[],[],[],[]]
for r in rows:
 n=r['resolved_name'];t=r['electrical_type']
 if n.endswith('_A'):g=0
 elif n.endswith('_B'):g=1
 elif n in {'VDD1','VDD2'}:g=2
 elif n=='VDDQ':g=3
 elif n=='VSS':g=4 if len(groups[4])<29 else 5
 else:g=6
 groups[g].append(r)
name='MT53E512M32D1ZW_046WT_B'
symbol=f'(symbol "{name}" (in_bom yes) (on_board yes) (property "Reference" "U" (at 0 0 0) (effects (font (size 1.27 1.27)))) (property "Value" "MT53E512M32D1ZW-046 WT:B" (at 0 0 0) (effects (font (size 1.27 1.27)))) (property "Footprint" "" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))'
for unit,group in enumerate(groups,1):
 left=[r for r in group if r['electrical_type']!='bidirectional'];right=[r for r in group if r['electrical_type']=='bidirectional']
 h=max(len(left),len(right))*2.54+5.08
 symbol+=f'(symbol "{name}_{unit}_1" (rectangle (start -15.24 {h/2}) (end 15.24 {-h/2}) (stroke (width 0) (type default)) (fill (type background)))'
 for side,rs in [('left',left),('right',right)]:
  for i,r in enumerate(rs):
   x=-20.32 if side=='left' else 20.32;angle=0 if side=='left' else 180;y=h/2-5.08-2.54*i
   hide=' hide' if r['electrical_type']=='no_connect' else ''
   symbol+=f'(pin {r["electrical_type"]} line (at {x} {y} {angle}) (length 5.08){hide} (name "{r["resolved_name"]}" (effects (font (size 1.27 1.27)))) (number "{r["ball"]}" (effects (font (size 1.27 1.27)))))'
 symbol+=')'
symbol+=')'
expected={(r['ball'],r['resolved_name'],r['electrical_type']) for r in rows}
pins=re.findall(r'\(pin (\w+) \w+.*?\(name "([^"]+)".*?\(number "([^"]+)"',symbol,re.S)
assert len(pins)==200 and {(b,n,t) for t,n,b in pins}==expected
(root/'reference/micron-ddr-grouped-review.kicad_sym').write_text('(kicad_symbol_lib (version 20231120) (generator eeschema) '+symbol+')\n')
print('PASS: seven grouped review units preserve all 200 ball identities, names and types')
print('Unit sizes:',[len(g) for g in groups])
