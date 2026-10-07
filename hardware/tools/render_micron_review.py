#!/usr/bin/env python3
"""Create temporary RAM review sheet, outside the appliance hierarchy."""
from pathlib import Path
import uuid,re
root=Path(__file__).resolve().parents[1]
s=(root/'reference/micron-ddr-grouped-review.kicad_sym').read_text();start=s.index('(symbol ');symbol=s[start:-2];name='MT53E512M32D1ZW_046WT_B';symbol=symbol.replace(f'(symbol "{name}"',f'(symbol "Review:{name}"',1)
def uid(k):return str(uuid.uuid5(uuid.NAMESPACE_URL,'sierra-ram-review-'+k))
def prop(k,v,x,y):return f'(property "{k}" "{v}" (at {x} {y} 0) (effects (font (size 1.27 1.27))))'
items=[]
positions=[(76.2,76.2),(177.8,76.2),(279.4,76.2),(406.4,76.2),(76.2,228.6),(177.8,228.6),(279.4,228.6)]
for unit,(x,y) in enumerate(positions,1):
 h=10.16 if unit in {3,4,5,6} else [22,22,32,20,29,29,14][unit-1]*2.54+5.08
 margin=15.24 if unit in {3,4} else 7.62
 fields=prop('Reference','U901',x,y-h/2-margin)+prop('Value','Micron RAM review',x,y-h/2-margin+2.54)
 items.append(f'(symbol (lib_id "Review:{name}") (at {x} {y} 0) (unit {unit}) (in_bom yes) (on_board yes) (dnp no) (uuid "{uid(str(unit))}") {fields} (instances (project "ram-review" (path "/{uid("root")}" (reference "U901") (unit {unit})))))')
Path('/tmp/ram-review.kicad_sch').write_text(f'(kicad_sch (version 20250114) (generator "eeschema") (uuid "{uid("root")}") (paper "A2") (lib_symbols {symbol}) '+''.join(items)+')')
