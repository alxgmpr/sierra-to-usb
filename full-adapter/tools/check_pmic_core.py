"""Physical switching/feedback checks for the three RK809 core bucks."""
from pathlib import Path
from xml.etree import ElementTree as ET
import json
import subprocess
import tempfile

ROOT=Path(__file__).resolve().parents[1]
CLI='/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli'


def check(root=ROOT):
    with tempfile.TemporaryDirectory(prefix='pmic-core-check-') as directory:
        xml=Path(directory)/'nets.xml'
        subprocess.run([CLI,'sch','export','netlist','--format','kicadxml','-o',str(xml),
                        str(root/'cad/full-adapter.kicad_sch')],check=True,capture_output=True)
        tree=ET.parse(xml)
        nets={n.get('name'):{(p.get('ref'),p.get('pin')) for p in n.findall('node')}
              for n in tree.findall('.//nets/net')}
        parts={p.get('ref'):p for p in tree.findall('.//components/comp')}
        for i,(rail,vin,sw,fb) in enumerate([
            ('VDD_LOGIC','11','12','13'),('VDD_GPU','10','9','8'),('VDD_NPU','66','65','64')]):
            l,r,nt=f'L{430+i}',f'R{430+i}',f'NT{430+i}'
            assert next(n for n in nets.values() if ('U5',sw) in n)=={('U5',sw),(l,'1')}
            assert nets[rail+'_FB']=={('U5',fb),(r,'2'),(nt,'2')}
            assert {(l,'2'),(r,'1'),(nt,'1')} <= nets[rail]
            assert ('U5',vin) in nets['VCC3V3_SYS']
            assert parts[nt].find('libsource').get('part')=='NetTie_2'
            assert parts[nt].find("property[@name='exclude_from_bom']") is not None
            assert parts[nt].findtext('footprint')=='NetTie:NetTie-2_SMD_Pad0.5mm'
            for ref,mpn,lcsc in [(l,'SPM5030T-R47M','C501964'),(r,'0402WGF1000TCE','C25076')]:
                fields={p.get('name'):p.text for p in parts[ref].findall('fields/field')}
                assert (fields['MPN'],fields['LCSC'])==(mpn,lcsc)
            assert parts[l].findtext('value')=='0.47uH'
            assert parts[r].findtext('value')=='100R 1%'
            for j in range(6):
                ref=f'C{430+i*10+j}'
                assert (ref,'1') in nets['VCC3V3_SYS' if j<2 else rail]
                assert (ref,'2') in nets['GND']
                fields={p.get('name'):p.text for p in parts[ref].findall('fields/field')}
                if j<5:
                    assert parts[ref].findtext('value')=='22uF'
                    assert (fields['MPN'],fields['LCSC'])==('CL21A226MAYNNNE','C602037')
                else:assert parts[ref].findtext('value')=='100nF'
    return {'status':'PMIC_CORE_CAPTURE_CHECKPOINT_NOT_RELEASE','core_bucks':3,
            'local_capacitors':18,'feedback_resistors':3,'processor_kelvin_ties':3,
            'kelvin_ties_physically_placed':False,'upstream_power_integrated':False}


if __name__=='__main__':
    result=check()
    (ROOT/'research/pmic-core-validation.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
