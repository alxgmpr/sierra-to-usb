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
    en=next(p for name,p in nets.items() if name.endswith('/MAIN3V3_EN'))
    assert en=={('U601','8'),('R603','2'),('R604','1')},en
    assert ('R603','1') in nets['5V_MAIN']
    pg=next(p for name,p in nets.items() if name.endswith('/MAIN3V3_PG_5V'))
    assert pg=={('U601','1'),('U602','2'),('R605','2'),('R606','1')},pg
    assert ('U602','5') in recovery and ('C604','1') in recovery
    assert nets['MAIN3V3_GOOD']=={('U602','4'),('U201','44')},nets['MAIN3V3_GOOD']
    fb=next(p for name,p in nets.items() if name.endswith('/MAIN5V_FB'))
    assert fb=={('U701','2'),('R702','2'),('R703','1')},fb
    mode=next(p for name,p in nets.items() if name.endswith('/MAIN5V_MODE'))
    assert mode=={('U701','10'),('R701','1')},mode
    assert ('R702','1') in nets['5V_MAIN']
    assert {('U701','3'),('U701','9'),('R701','2'),('R703','2')} <= nets['GND']
    sw=next(p for name,p in nets.items() if name.endswith('/MAIN5V_SW'))
    assert sw=={('U701','6'),('C701','2')},sw
    boot=next(p for p in nets.values() if ('U701','7') in p)
    assert boot=={('U701','7'),('C701','1')},boot
    assert len(tree.findall('./components/comp'))==97
print('PASS: appliance restart GPIO connection and 97-component capture; not full ERC.')
