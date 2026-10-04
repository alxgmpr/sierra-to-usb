#!/usr/bin/env python3
"""Check captured BUCK1/2 connectivity only; other PMIC circuitry is unfinished."""
from pathlib import Path
import subprocess, tempfile, xml.etree.ElementTree as E
root=Path(__file__).resolve().parents[1]
with tempfile.TemporaryDirectory() as tmp:
 net=Path(tmp)/'pmic.xml'
 subprocess.run(['/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli','sch','export','netlist','--format','kicadxml','--output',str(net),str(root/'pmic.kicad_sch')],check=True)
 tree=E.parse(net).getroot()
 nets={n.attrib['name']:{(v.attrib['ref'],v.attrib['pin']) for v in n.findall('node')} for n in tree.findall('.//nets/net')}
 expected={
 '/5V_MAIN':{('U501','10'),('U501','11'),('C504','1'),('C508','1')},
 '/PMIC_SW1':{('U501','12'),('L501','1')},
 '/PMIC_SW2':{('U501','9'),('L502','1')},
 '/VDD_LOGIC':{('U501','13'),('L501','2'),('C501','1'),('C502','1'),('C503','1')},
 '/VDD_GPU':{('U501','8'),('L502','2'),('C505','1'),('C506','1'),('C507','1')},
 'GND':{(f'C{n}','2') for n in range(501,509)},
 }
 for name,pins in expected.items():assert nets[name]==pins,(name,nets[name],pins)
 comps=tree.findall('.//components/comp');assert len(comps)==11
 for c in comps:
  fields={f.attrib['name']:f.text for f in c.findall('fields/field')}
  assert fields.get('MPN'),c.attrib['ref']
 print('PASS: BUCK1/2 exact six-net membership and 11 MPNs. Remaining PMIC channels and management are incomplete; this is not full ERC or qualification.')
