#!/usr/bin/env python3
"""Populate exact resistor fields without changing recovery circuitry or placement."""
from pathlib import Path
import re
ROOT=Path(__file__).resolve().parents[1]
def balanced(text,start):
 depth=0;quoted=False;escaped=False
 for i in range(start,len(text)):
  c=text[i]
  if escaped:escaped=False;continue
  if quoted and c=='\\':escaped=True;continue
  if c=='"':quoted=not quoted
  if not quoted:
   if c=='(':depth+=1
   elif c==')':
    depth-=1
    if depth==0:return i+1
 raise ValueError('Unbalanced expression')
for name in ['supervisor.kicad_sch','controls.kicad_sch']:
 p=ROOT/name;text=p.read_text();changes=[]
 for m in re.finditer(r'\(symbol \(lib_id "Device:R_Small_US"\)',text):
  end=balanced(text,m.start());s=text[m.start():end]
  ref=re.search(r'\(property "Reference" "([^"]+)"',s).group(1)
  value=re.search(r'\(property "Value" "([^"]+)"',s).group(1)
  mpn,lcsc={'10kR':('RC0603FR-0710KL','C98220'),'100kR':('RC0603FR-07100KL','C14675')}[value]
  x,y=re.search(r'\(at ([\d.\-]+) ([\d.\-]+) [\d.\-]+\)',s).groups()
  for field,v in {'MPN':mpn,'Manufacturer':'Yageo','LCSC':lcsc,'Tolerance':'1%','Power Rating':'0.1W','Voltage Rating':'75V','Datasheet':'https://www.yageo.com/upload/media/product/productsearch/datasheet/rchip/PYu-RC_Group_51_RoHS_L_12.pdf'}.items():
   item=f'(property "{field}" "{v}" (at {x} {y} 0) (effects (font (size 1.27 1.27)) (hide yes)))'
   old=re.search(r'\(property "'+re.escape(field)+r'" ',s)
   if old:
    stop=balanced(s,old.start());s=s[:old.start()]+item+s[stop:]
   else:s=s[:-1]+' '+item+')'
  changes.append((m.start(),end,s));print(ref,mpn)
 for start,end,s in reversed(changes):text=text[:start]+s+text[end:]
 p.write_text(text)
