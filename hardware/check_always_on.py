#!/usr/bin/env python3
"""Check the actual always-on circuit with native ERC and exact net membership."""
import argparse
import csv
import shutil
import subprocess
from pathlib import Path
import xml.etree.ElementTree as ET

p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--output',type=Path,required=True)
p.add_argument('--kicad-cli',default=shutil.which('kicad-cli') or '/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli')
a=p.parse_args();a.output.mkdir(parents=True,exist_ok=True)
source=Path(__file__).resolve().parent/'recovery.kicad_sch'
def run(*args):subprocess.run([a.kicad_cli,*map(str,args)],check=True)
run('sch','erc','--severity-all','--exit-code-violations','--format','json','--output',a.output/'erc.json',source)
run('sch','export','netlist','--format','kicadxml','--output',a.output/'netlist.xml',source)
r=ET.parse(a.output/'netlist.xml')
nets={n.get('name'):{(x.get('ref'),x.get('pin')) for x in n.findall('node')} for n in r.findall('.//nets/net')}
supply_refs={'U401','L401','C401','C402','R401'}
expected=[{('U401','2'),('U401','3'),('C401','1')},{('U401','9'),('L401','1')},{('L401','2'),('U401','10'),('U401','8'),('C402','1'),('R401','1')},{('U401','7'),('R401','2')},{('U401','1'),('U401','4'),('U401','5'),('U401','6'),('U401','11'),('C401','2'),('C402','2')}]
for group in expected:
 matches=[(name,actual) for name,actual in nets.items() if {node for node in actual if node[0] in supply_refs}==group]
 if len(matches)!=1:raise RuntimeError(f'Expected exact circuit net {group}; actual nets: {nets}')
components=[c for c in r.findall('.//components/comp') if c.get('ref') in supply_refs]
if len(components)!=5:raise RuntimeError(f'Expected 5 components, got {len(components)}')
with (a.output/'bom.csv').open('w',newline='') as f:
 writer=csv.writer(f);writer.writerow(['Reference','Value','Footprint','MPN','Manufacturer','LCSC','Qualification'])
 for c in components:
  fields={x.get('name'):x.text or '' for x in c.findall('./fields/field')}
  if not fields.get('MPN'):raise RuntimeError(f'Missing MPN: {c.get("ref")}')
  writer.writerow([c.get('ref'),c.findtext('value'),c.findtext('footprint'),*(fields.get(x,'') for x in ['MPN','Manufacturer','LCSC','Qualification'])])
run('sch','export','svg','--output',a.output/'svg',source)
run('sch','export','pdf','--output',a.output/'always-on.pdf',source)
print('PASS: native ERC, all five supply circuit nets within integrated hierarchy, 5-component BOM from schematic. Component derating and hardware remain unqualified.')
