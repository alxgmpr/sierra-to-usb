"""Check physical oscillator topology, analog reference and crystal lands."""
from pathlib import Path
from xml.etree import ElementTree as ET
import hashlib
import json
import subprocess
import tempfile
import sexpdata as sx

ROOT=Path(__file__).resolve().parents[1]
CLI='/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli'
def nodes(n,tag):return [x for x in n if isinstance(x,list) and str(x[0])==tag]


def check(root=ROOT):
    with tempfile.TemporaryDirectory(prefix='processor-clock-check-') as directory:
        xml=Path(directory)/'nets.xml'
        subprocess.run([CLI,'sch','export','netlist','--format','kicadxml','-o',str(xml),
                        str(root/'cad/full-adapter.kicad_sch')],check=True,capture_output=True)
        tree=ET.parse(xml)
        nets={n.get('name'):{(p.get('ref'),p.get('pin')) for p in n.findall('node')}
              for n in tree.findall('.//nets/net')}
        def local(name):
            found=[v for n,v in nets.items() if n.endswith('/'+name)]
            assert len(found)==1,(name,found)
            return found[0]
        assert local('SOC_XIN24M')=={('U1','AF28'),('R570','1'),('Y570','1'),('C570','1')}
        assert local('SOC_XOUT24M')=={('U1','AF27'),('R570','2'),('R571','1')}
        assert local('SOC_XTAL_OUT')=={('R571','2'),('Y570','3'),('C571','1')}
        assert {('U1','AB24'),('Y570','2'),('Y570','4'),('C570','2'),('C571','2')} <= nets['GND']
        parts={c.get('ref'):c for c in tree.findall('.//components/comp')}
        expected={'Y570':('24MHz / 12pF','TXM24M0004322FBCDO00T','C362340'),
                  'R570':('1MR 1%','0402WGF1004TCE','C26083'),
                  'R571':('22R 1%','0402WGF220JTCE','C25092'),
                  'C570':('20pF C0G','0402CG200J500NT','C1554'),
                  'C571':('20pF C0G','0402CG200J500NT','C1554')}
        for ref,(value,mpn,lcsc) in expected.items():
            fields={f.get('name'):f.text for f in parts[ref].findall('fields/field')}
            assert (parts[ref].findtext('value'),fields['MPN'],fields['LCSC'])==(value,mpn,lcsc),ref
        assert parts['Y570'].findtext('footprint')=='full-adapter:Yajingxin_TXM_3225_24MHz'
    fp=sx.loads((root/'lib/full-adapter.pretty/Yajingxin_TXM_3225_24MHz.kicad_mod').read_text())
    pads={p[1]:p for p in nodes(fp,'pad')}
    assert set(pads)=={'1','2','3','4'}
    for number,xy in {'1':[-1.1,.85],'2':[1.1,.85],'3':[1.1,-.85],'4':[-1.1,-.85]}.items():
        assert nodes(pads[number],'at')[0][1:3]==xy
        assert nodes(pads[number],'size')[0][1:3]==[1.4,1.2]
    source=json.loads((root/'research/processor-crystal-footprint-source.json').read_text())
    assert source['datasheet_sha256']==hashlib.sha256((root/'reference/yjx-txm24m0004322fbcd.pdf').read_bytes()).hexdigest()
    return {'status':'PROCESSOR_CLOCK_CAPTURE_CHECKPOINT_NOT_RELEASE',
            'crystal_frequency_MHz':24,'crystal_ESR_max_ohm':30,'load_caps_pF':[20,20],
            'assumed_combined_stray_pF':2,'grounded_TVSS_ball':'AB24',
            'frequency_startup_drive_verified_on_hardware':False,'system_routed':False}


if __name__=='__main__':
    result=check()
    (ROOT/'research/processor-clock-validation.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
