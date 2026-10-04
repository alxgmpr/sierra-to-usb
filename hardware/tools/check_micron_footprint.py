#!/usr/bin/env python3
"""Audit native ZW ball-center coordinates, not fabrication land-pattern approval."""
from pathlib import Path
import re,csv
root=Path(__file__).resolve().parents[1]
s=(root/'reference/micron-ddr-native-candidate.kicad_mod').read_text()
pads=re.findall(r'\(pad (\S+) smd circle \(at ([\d.-]+) ([\d.-]+) [\d.-]+\) \(size ([\d.-]+) ([\d.-]+)\)',s)
rows='A B C D E F G H J K L M N P R T U V W Y AA AB'.split()
assert len(pads)==200 and len({p[0] for p in pads})==200
expected={r['ball'] for r in csv.DictReader((root/'reference/micron-ddr-native-pin-inventory.csv').open())}
assert {p[0] for p in pads}==expected
for ball,x,y,w,h in pads:
 m=re.fullmatch(r'([A-Z]+)(\d+)',ball);row,col=m[1],int(m[2]);i=rows.index(row)
 # Native footprint is rotated 90 degrees relative to Figure 5 top view.
 ex=(i-10.5)*0.65;ey=(6.5-col)*0.8
 assert abs(float(x)-ex)<=0.006 and abs(float(y)-ey)<=0.006,(ball,x,y,ex,ey)
 assert float(w)==float(h)==0.35
print('PASS: 200 native pad centers match Micron ZW grid within 0.006mm after rotation.')
print('Native copper pads are 0.35mm; manufacturer drawing references 0.4mm SMD pads.')
print('Land pattern remains unqualified: mask/paste, courtyard, Fab outline and assembly review pending.')
