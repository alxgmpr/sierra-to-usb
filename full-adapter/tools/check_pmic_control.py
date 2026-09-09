"""Check explicit unused-codec connections without claiming RTC completion."""
from pathlib import Path
from xml.etree import ElementTree as ET
import json
import subprocess
import tempfile

ROOT=Path(__file__).resolve().parents[1]
CLI='/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli'


def check(root=ROOT):
    with tempfile.TemporaryDirectory(prefix='pmic-control-check-') as directory:
        xml=Path(directory)/'nets.xml'
        subprocess.run([CLI,'sch','export','netlist','--format','kicadxml','-o',str(xml),
                        str(root/'cad/full-adapter.kicad_sch')],check=True,capture_output=True)
        tree=ET.parse(xml)
        nets={n.get('name'):{(p.get('ref'),p.get('pin')) for p in n.findall('node')}
              for n in tree.findall('.//nets/net')}
        for pin in ['14','15','16','17','19','40']:assert ('U5',pin) in nets['GND']
        for pin in ['18','32','34','35','36','37','38','39','41','42','43']:
            node=('U5',pin)
            assert all(node not in n or n=={node} for n in nets.values()),pin
        for pin,ref in [('44','C480'),('48','C481')]:
            assert next(n for n in nets.values() if ('U5',pin) in n)=={('U5',pin),(ref,'1')}
        assert ('U5','33') in nets['VCC3V3_SYS'] and ('C482','1') in nets['VCC3V3_SYS']
        parts={p.get('ref'):p for p in tree.findall('.//components/comp')}
        for ref in ['C480','C481','C482']:
            assert (ref,'2') in nets['GND']
            fields={f.get('name'):f.text for f in parts[ref].findall('fields/field')}
            assert parts[ref].findtext('value')==('10uF' if ref=='C482' else '1uF')
            assert fields['LCSC']==('C19702' if ref=='C482' else 'C52923')
    return {'status':'PMIC_UNUSED_AUDIO_CHECKPOINT_NOT_RELEASE','grounded_audio_pins':6,
            'unused_open_pins':11,'internal_supply_bypass_caps':2,'control_and_RTC_integrated':False}


if __name__=='__main__':
    result=check()
    (ROOT/'research/pmic-control-validation.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
