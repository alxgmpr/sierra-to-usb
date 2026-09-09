"""Check RK809 physical control/RTC nodes and explicit unused-codec pins."""
from pathlib import Path
from xml.etree import ElementTree as ET
import json
import subprocess
import tempfile
import sexpdata as sx

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
        def attached(ref,pin):return next(n for n in nets.values() if (ref,pin) in n)
        for pin in ['47','69','56','62','63']:assert ('U5',pin) in nets['GND']
        for pin in ['60','68']:
            assert all(('U5',pin) not in n or n=={('U5',pin)} for n in nets.values())
        assert attached('U5','1')=={('U5','1'),('R490','2')}
        assert attached('U5','2')=={('U5','2'),('R491','2')}
        assert attached('U5','46')=={('U5','46'),('C484','1')}
        assert attached('U5','61')=={('U5','61'),('R496','2'),('R497','1'),('C487','1')}
        assert nets['PMIC_PWRON_L']=={('U5','52'),('C485','1')}
        assert nets['SYS_RESET_L']=={('U5','67'),('R494','2'),('C486','1'),('U1','AH27'),('R561','2'),('C560','1')}
        assert nets['PMIC_INT_L']=={('U5','7'),('R495','2'),('U1','AA22')}
        assert {('U5','45'),('C483','1'),('R496','1')} <= nets['VCC3V3_SYS']
        assert ('R497','2') in nets['GND']
        for ref in ['C483','C484','C485','C486','C487','C488','C489']:assert (ref,'2') in nets['GND']
        xin=attached('U5','50');xout=attached('U5','51')
        assert {('U5','50'),('C488','1')} < xin and {('U5','51'),('C489','1')} < xout
        assert len(xin)==len(xout)==3 and xin.isdisjoint(xout)
        assert {p for ref,p in xin|xout if ref=='Y490'}=={'1','2'}
        expected={
            'R490':('22R 1%','C25092'),'R491':('22R 1%','C25092'),
            'R492':('2.2kR 1%','C25879'),'R493':('2.2kR 1%','C25879'),
            'R494':('10kR 1%','C25744'),'R495':('10kR 1%','C25744'),
            'R496':('100kR 1%','C25741'),'R497':('56kR 1%','C25796'),
            'C483':('1uF','C52923'),'C484':('1uF','C52923'),'C487':('1uF','C52923'),
            'C488':('22pF','C1555'),'C489':('22pF','C1555')}
        for ref,(value,lcsc) in expected.items():
            f={x.get('name'):x.text for x in parts[ref].findall('fields/field')}
            assert (parts[ref].findtext('value'),f['LCSC'])==(value,lcsc)
        for ref in ['C485','C486']:assert parts[ref].findtext('value')=='100nF'
        f={x.get('name'):x.text for x in parts['Y490'].findall('fields/field')}
        assert (f['MPN'],f['LCSC'])==('FC-135R 32.7680KA-A3','C6554955')
        assert parts['Y490'].findtext('footprint')=='full-adapter:Epson_FC-135R_3.2x1.5mm'
        assert {p.get('num') for u in parts['U5'].findall('units/unit') for p in u.findall('pins/pin')}=={str(i) for i in range(1,70)}
        for ref in ['C480','C481','C482']:
            assert (ref,'2') in nets['GND']
            fields={f.get('name'):f.text for f in parts[ref].findall('fields/field')}
            assert parts[ref].findtext('value')==('10uF' if ref=='C482' else '1uF')
            assert fields['LCSC']==('C19702' if ref=='C482' else 'C52923')
    def nodes(n,t):return [x for x in n if isinstance(x,list) and str(x[0])==t]
    fp=sx.loads((root/'lib/full-adapter.pretty/Epson_FC-135R_3.2x1.5mm.kicad_mod').read_text())
    pads=nodes(fp,'pad');assert len(pads)==2
    assert {tuple(nodes(p,'at')[0][1:3]) for p in pads}=={(-1.25,0),(1.25,0)}
    assert all(nodes(p,'size')[0][1:]==[1,1.8] for p in pads)
    zone=nodes(fp,'zone')[0]
    pts=nodes(nodes(zone,'polygon')[0],'pts')[0][1:]
    assert {tuple(p[1:]) for p in pts}=={(-.75,-.9),(.75,-.9),(.75,.9),(-.75,.9)}
    keepout=nodes(zone,'keepout')[0]
    assert all(str(nodes(keepout,t)[0][1])=='not_allowed' for t in ['tracks','vias','pads','copperpour'])
    return {'status':'PMIC_CONTROL_CAPTURE_CHECKPOINT_NOT_RELEASE','pmic_physical_pins_present':69,
            'grounded_audio_pins':6,'unused_audio_open_pins':11,'internal_supply_bypass_caps':2,
            'control_and_RTC_integrated':True,'processor_control_connections_integrated':True,
            'oscillator_and_startup_physically_qualified':False}


if __name__=='__main__':
    result=check()
    (ROOT/'research/pmic-control-validation.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
