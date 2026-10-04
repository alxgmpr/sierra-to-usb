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
    nets={n.get('name'):{(v.get('ref'),v.get('pin')) for v in n.findall('node')} for n in tree.findall('./nets/net')}
    assert nets['3V3_MAIN']=={('C602','1'),('C603','1'),('L601','2'),('R601','1'),('U601','5'),('U501','22'),('U501','4'),('C519','1'),('C524','1')},nets['3V3_MAIN']
    recovery=next(p for p in nets.values() if ('U201','4') in p)
    assert not recovery & nets['3V3_MAIN']
    assert ('U601','2') in nets['5V_MAIN'] and ('U501','66') in nets['5V_MAIN']
    assert len(tree.findall('./components/comp'))==86
print('PASS: appliance restart GPIO connection and 86-component capture; not full ERC.')
