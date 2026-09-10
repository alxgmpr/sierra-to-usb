"""Check physical service-control nets and the manufacturer switch lands."""
from pathlib import Path
from xml.etree import ElementTree as ET
import json,subprocess,tempfile
import sexpdata as sx
ROOT=Path(__file__).resolve().parents[1]
CLI='/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli'
def nodes(n,t):return [v for v in n if isinstance(v,list) and str(v[0])==t]
def check(root=ROOT):
    fp=sx.loads((root/'lib/full-adapter.pretty/Alps_SKRPACE010.kicad_mod').read_text())
    pads=nodes(fp,'pad');assert len(pads)==4
    assert {(p[1],*nodes(p,'at')[0][1:3]) for p in pads}=={('1',-2.075,-1.075),('1',2.075,-1.075),('2',-2.075,1.075),('2',2.075,1.075)}
    assert all(nodes(p,'size')[0][1:3]==[1.05,.65] for p in pads)
    with tempfile.TemporaryDirectory() as d:
        path=Path(d)/'nets.xml';subprocess.run([CLI,'sch','export','netlist','--format','kicadxml','-o',str(path),str(root/'cad/full-adapter.kicad_sch')],check=True,capture_output=True)
        tree=ET.parse(path);nets={n.get('name'):{(p.get('ref'),p.get('pin')) for p in n.findall('node')} for n in tree.findall('.//nets/net')}
        def attached(ref,pin):return next(n for n in nets.values() if (ref,pin) in n)
        assert attached('U1','B27')=={('U1','B27'),('SW640','1'),('TP640','1'),('R640','2')}
        assert {('U1','H22'),('R640','1')}<=nets['VCC1V8_ANLG']
        for i,net in [(641,'SYS_RESET_L'),(642,'PMIC_PWRON_L')]:
            assert (f'R{i}','1') in nets[net]
            assert attached(f'SW{i}','1')=={(f'SW{i}','1'),(f'R{i}','2')}
        assert {(f'SW{i}','2') for i in range(640,643)}<=nets['GND']
        parts={p.get('ref'):p for p in tree.findall('.//components/comp')}
        for i in range(640,643):
            p=parts[f'SW{i}'];fields={f.get('name'):f.text for f in p.findall('fields/field')}
            assert (fields['MPN'],fields['LCSC'])==('SKRPACE010','C139797')
        assert parts['R640'].findtext('value')=='10kR 1%'
        for i in [641,642]:assert parts[f'R{i}'].findtext('value')=='100R 1%'
        for p in ['C26','D24','E23','F21','F22','G20','G21']:
            assert all(('U1',p) not in n or n=={('U1',p)} for n in nets.values())
    return dict(status='BUTTON_CAPTURE_NOT_RELEASE',switches=3,physical_lands_checked=4,recovery_pullup_same_as_ADC_supply=True,reset_discharge_peak_mA_at_3V465=3.465/99*1000,hardware_tested=False)
if __name__=='__main__':
    result=check();(ROOT/'research/buttons-validation.json').write_text(json.dumps(result,indent=2)+'\n');print(result)
