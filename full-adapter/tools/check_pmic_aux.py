"""Verify BUCK5 and both switches preserve distinct voltage/ownership nets."""
from pathlib import Path
from xml.etree import ElementTree as ET
import json
import subprocess
import tempfile

ROOT=Path(__file__).resolve().parents[1]
CLI='/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli'


def check(root=ROOT):
    with tempfile.TemporaryDirectory(prefix='pmic-aux-check-') as directory:
        xml=Path(directory)/'nets.xml'
        subprocess.run([CLI,'sch','export','netlist','--format','kicadxml','-o',str(xml),
                        str(root/'cad/full-adapter.kicad_sch')],check=True,capture_output=True)
        tree=ET.parse(xml)
        nets={n.get('name'):{(p.get('ref'),p.get('pin')) for p in n.findall('node')}
              for n in tree.findall('.//nets/net')}
        parts={p.get('ref'):p for p in tree.findall('.//components/comp')}
        assert next(n for n in nets.values() if ('U5','53') in n)=={('U5','53'),('L460','1')}
        assert nets['VCC1V8_SYS']=={('U5','59'),('L460','2'),('C462','1'),('C463','1'),('C464','1'),
                                   ('U1','H18'),('U1','H20'),('C521','1'),('C522','1')} | {('U6',b) for b in ['C6','M4','N4','P3','P5']} | {(f'C{i}','1') for i in range(605,611)} | {(f'R{i}','1') for i in range(610,620)}
        assert nets['VCC3V3_S0']=={('U5','55'),('C465','1'),('U1','H17'),('U1','J21'),('U1','R9'),
                                  ('U1','U9'),('U1','V10'),('U1','V11'),('U1','V12'),
                                  ('C520','1'),('C524','1'),('C526','1'),('C527','1'),('C528','1'),('C529','1'),('C530','1'),('C531','1'),
                                  ('U1','M23'),('U1','P10'),('C540','1'),('C542','1')} | {('U6',b) for b in ['E6','F5','J10','K9']} | {(f'C{i}','1') for i in range(600,605)} | {('U8','10'),('U9','7'),('C631','1'),('C633','1'),('U12','8'),('R652','1')} | {('U14','1'),('U14','5'),('C700','1'),('R700','1'),('R701','1')}
        assert nets['VCC3V3_SD']=={('U5','58'),('C467','1')}
        assert {('U5','54'),('U5','57'),('C460','1'),('C461','1'),('C466','1')} <= nets['VCC3V3_SYS']
        for i in range(460,468):
            ref=f'C{i}';p=parts[ref]
            assert (ref,'2') in nets['GND']
            fields={f.get('name'):f.text for f in p.findall('fields/field')}
            expected=('22uF','CL21A226MAYNNNE','C602037') if i<465 else ('1uF','CL05A105KA5NQNC','C52923')
            assert (p.findtext('value'),fields['MPN'],fields['LCSC'])==expected
        p=parts['L460'];fields={f.get('name'):f.text for f in p.findall('fields/field')}
        assert (p.findtext('value'),fields['MPN'],fields['LCSC'])==('0.47uH','SPM5030T-R47M','C501964')
    return {'status':'PMIC_AUX_CAPTURE_CHECKPOINT_NOT_RELEASE','buck5_startup_V':1.8,
            'switch1_input_V':3.3,'switch2_input_V':3.3,'local_capacitors':8,
            'processor_IO_and_OTP_supplies_integrated':True,
            'remaining_peripheral_loads_integrated':False,'upstream_power_integrated':False}


if __name__=='__main__':
    result=check()
    (ROOT/'research/pmic-aux-validation.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
