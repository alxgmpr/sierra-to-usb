#!/usr/bin/env python3
"""Capture audited RAM model as an explicitly incomplete appliance draft."""
from pathlib import Path
import uuid,re
root=Path(__file__).resolve().parents[1]
s=(root/'reference/micron-ddr-grouped-review.kicad_sym').read_text();start=s.index('(symbol ');symbol=s[start:-2];name='MT53E512M32D1ZW_046WT_B';symbol=symbol.replace(f'(symbol "{name}"',f'(symbol "MemoryDraft:{name}"',1)
def uid(k):return str(uuid.uuid5(uuid.NAMESPACE_URL,'sierra-ram-'+k))
def prop(k,v,x,y):return f'(property "{k}" "{v}" (at {x} {y} 0) (effects (font (size 1.27 1.27))))'
items=[]
# Library has no production footprint pending land-pattern qualification.
(root/'MemoryDraft.kicad_sym').write_text((root/'reference/micron-ddr-grouped-review.kicad_sym').read_text())
def wire(a,b,key):
 items.append(f'(wire (pts (xy {a[0]} {a[1]}) (xy {b[0]} {b[1]})) (stroke (width 0) (type default)) (uuid "{uid(key)}"))')
def ground(x,y,key):
 items.append(f'(global_label "GND" (shape passive) (at {x} {y} 0) (effects (font (size 1.27 1.27)) (justify right)) (uuid "{uid(key)}"))')
positions=[(76.2,76.2),(177.8,76.2),(279.4,76.2),(406.4,76.2),(76.2,228.6),(177.8,228.6),(279.4,228.6)]
for unit,(x,y) in enumerate(positions,1):
 h=10.16 if unit in {3,4,5,6} else [22,22,32,20,29,29,14][unit-1]*2.54+5.08
 margin=25.4 if unit==3 else 15.24 if unit==4 else 7.62
 fields=prop('Reference','U901',x,y-h/2-margin)+prop('Value','MT53E512M32D1ZW-046 WT:B',x,y-h/2-margin+2.54)
 for key,value in {'MPN':'MT53E512M32D1ZW-046 WT:B','Manufacturer':'Micron','LCSC':'C5330500','Footprint':'','Qualification':'DRAFT: DDR supplies, bus, WDQS and land pattern unresolved'}.items():
  fields+=f'(property "{key}" "{value}" (at {x} {y} 0) (effects (font (size 1.27 1.27)) (hide yes)))'
 items.append(f'(symbol (lib_id "MemoryDraft:{name}") (at {x} {y} 0) (unit {unit}) (in_bom yes) (on_board yes) (dnp no) (uuid "{uid(str(unit))}") {fields} (instances (project "ram" (path "/{uid("root")}" (reference "U901") (unit {unit})))))')
# Ground pins and permitted unused DNU balls only; no speculative DDR supply/bus wiring.
for unit,(x,y) in enumerate(positions,1):
 body=symbol.split(f'(symbol "{name}_{unit}_1"',1)[1].split(f'(symbol "{name}_{unit+1}_1"',1)[0]
 for px,py,angle,pname,ball in re.findall(r'\(pin \w+ \w+.*?\(at ([\d.-]+) ([\d.-]+) ([\d.-]+)\).*?\(name "([^"]+)".*?\(number "([^"]+)"',body,re.S):
  ax,ay=round(x+float(px),4),round(y-float(py),4)
  if pname=='VSS':
   wire((ax,ay),(ax,y+20.32),'gnd-'+ball)
  elif pname=='VDD1':
   wire((ax,ay),(ax,y-20.32),'vdd1-'+ball)
  elif pname in {'ODT_CA_A','ODT_CA_B'}:
   wire((ax,ay),(ax-7.62,ay),'odt-'+ball)
   ground(ax-7.62,ay,'odt-label-'+ball)
  elif pname=='DNU':
   items.append(f'(no_connect (at {ax} {ay}) (uuid "{uid("nc-"+ball)}"))')
 if unit==3:
  wire((x-39.37,y-20.32),(x-21.59,y-20.32),'vdd1-bank')
  items.append(f'(global_label "VCC_1V8" (shape passive) (at {x-39.37} {y-20.32} 0) (effects (font (size 1.27 1.27)) (justify right)) (uuid "{uid("vdd1-label")}"))')
 if unit in {5,6}:
  wire((x-35.56,y+20.32),(x+35.56,y+20.32),'ground-bank-'+str(unit))
  ground(x-35.56,y+20.32,'ground-label-'+str(unit))
(root/'ram.kicad_sch').write_text(f'(kicad_sch (version 20250114) (generator "eeschema") (uuid "{uid("root")}") (paper "A2") (title_block (title "Micron RAM — DRAFT: supplies and DDR bus incomplete") (date "2026-10-04")) (lib_symbols {symbol}) '+''.join(items)+')')
