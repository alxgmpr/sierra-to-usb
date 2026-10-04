#!/usr/bin/env python3
"""Check appliance restart integration only; not full ERC or completion."""
from pathlib import Path
import subprocess, tempfile, xml.etree.ElementTree as E
root=Path(__file__).resolve().parents[1]
with tempfile.TemporaryDirectory() as tmp:
    path=Path(tmp)/'appliance.xml'
    subprocess.run(['/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli','sch','export','netlist','--format','kicadxml','--output',str(path),str(root/'appliance.kicad_sch')],check=True)
    tree=E.parse(path).getroot()
    net=next(n for n in tree.findall('./nets/net') if n.get('name')=='MCU_PWRON_KICK')
    pins={(n.get('ref'),n.get('pin')) for n in net.findall('node')}
    assert pins=={('U201','43'),('R508','1')},pins
    assert len(tree.findall('./components/comp'))==79
print('PASS: appliance restart GPIO connection and 79-component capture; not full ERC.')
