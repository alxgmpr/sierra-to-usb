"""Verify recovery capture, while retaining explicit electrical release gaps."""
from pathlib import Path
from xml.etree import ElementTree as ET
import json,subprocess,tempfile
import sexpdata as sx
ROOT=Path(__file__).resolve().parents[1]
CLI='/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli'
def nodes(n,t):return [v for v in n if isinstance(v,list) and str(v[0])==t]
def check(root=ROOT):
    lib=sx.loads((root/'lib/full-adapter.kicad_sym').read_text())
    sym=next(v for v in nodes(lib,'symbol') if v[1]=='TS3USB221ARSER')
    pins={nodes(p,'number')[0][1]:nodes(p,'name')[0][1] for u in nodes(sym,'symbol') for p in nodes(u,'pin')}
    assert pins=={'1':'1D+','2':'1D-','3':'2D+','4':'2D-','5':'GND','6':'~{OE}','7':'D-','8':'D+','9':'S','10':'VCC'}
    fp=sx.loads((root/'lib/full-adapter.pretty/TI_TS3USB221A_RSE0010A.kicad_mod').read_text())
    pads={p[1]:p for p in nodes(fp,'pad')};assert set(pads)==set(pins)
    for number,p in pads.items():
        i=int(number);expected=([0,-.9] if i==10 else [0,.9]) if i in [5,10] else ([-.675,-.75+(i-1)*.5] if i<5 else [.675,.75-(i-6)*.5])
        assert nodes(p,'at')[0][1:3]==expected
        assert nodes(p,'size')[0][1:3]==([.3,.6] if i in [5,10] else [.55,.25 if i in [1,4,6,9] else .2])
    with tempfile.TemporaryDirectory() as d:
        path=Path(d)/'nets.xml'
        subprocess.run([CLI,'sch','export','netlist','--format','kicadxml','-o',str(path),str(root/'cad/full-adapter.kicad_sch')],check=True,capture_output=True)
        tree=ET.parse(path);nets={n.get('name'):{(p.get('ref'),p.get('pin')) for p in n.findall('node')} for n in tree.findall('.//nets/net')}
        def net(name):
            found=[v for k,v in nets.items() if k==name or k.endswith('/'+name)];assert len(found)==1,(name,found);return found[0]
        assert net('RECOVERY_CABLE_P')=={('J630','A6'),('J630','B6'),('U8','1'),('U10','1')}
        assert net('RECOVERY_CABLE_N')=={('J630','A7'),('J630','B7'),('U8','2'),('U10','2')}
        for letter,up,rp,ball in [('P','8','R632','P27'),('N','7','R633','P28')]:
            assert net('RECOVERY_SWITCH_'+letter)=={('U8',up),(rp,'1')}
            assert net('SOC_RECOVERY_'+letter)=={('U1',ball),(rp,'2')}
        assert net('RECOVERY_VBUSDET')=={('U1','M24'),('R634','2'),('R635','1'),('C634','1')}
        assert next(v for v in nets.values() if ('U9','8') in v)=={('U9','8'),('R634','1')}
        assert net('VCC_RECOVERY5V')=={('J630',p) for p in ['A4','A9','B4','B9']}|{('C630','1'),('C632','1'),('U9','3'),('U9','5'),('U9','6')}
        assert {('U8','10'),('U9','7'),('C631','1'),('C633','1')}<=net('VCC3V3_S0')
        assert {('U8','5'),('U8','6'),('U8','9'),('U9','1'),('U9','2'),('U10','3'),('R635','2')}<=net('GND')
        for p,r in [('A5','R630'),('B5','R631')]:
            assert next(v for v in nets.values() if ('J630',p) in v)=={('J630',p),(r,'1')}
            assert (r,'2') in net('GND')
        # Open integration endpoints are asserted, not ERC exclusions.
        assert net('MODEM_HOST_USB2_P')=={('U1','P24')}
        assert net('MODEM_HOST_USB2_N')=={('U1','P25')}
        for fpname,ref in [('GCT_USB4105_120','J630'),('TI_TPD2EUSB30_DRT0003A','U10')]:
            f=sx.loads((root/f'lib/full-adapter.pretty/{fpname}.kicad_mod').read_text())
            assert {p[1] for p in nodes(f,'pad') if p[1]}==({f'{b}{i}' for b in 'AB' for i in [1,4,5,6,7,8,9,12]}|{'SH'} if ref=='J630' else {'1','2','3'})
    return dict(status='RECOVERY_CAPTURE_NOT_RELEASE',data_path_checked=True,host_supply_separate=True,modem_endpoints_unfinished=2,electrical_qualification_complete=False,hardware_tested=False)
if __name__=='__main__':
    result=check();(ROOT/'research/recovery-validation.json').write_text(json.dumps(result,indent=2)+'\n');print(result)
