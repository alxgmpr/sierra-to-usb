"""Physical-ball assertions for eMMC library, rails and eight-bit host mapping."""
from pathlib import Path
from xml.etree import ElementTree as ET
import json
import subprocess
import tempfile
import sexpdata as sx

ROOT=Path(__file__).resolve().parents[1]
CLI='/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli'
def nodes(n,tag):return [x for x in n if isinstance(x,list) and str(x[0])==tag]


def check(root=ROOT):
    source=json.loads((root/'research/emmc-pins.json').read_text())
    expected={p['ball']:p for p in source['pins']}
    assert len(expected)==153
    lib=sx.loads((root/'lib/full-adapter.kicad_sym').read_text())
    symbol=next(s for s in nodes(lib,'symbol') if s[1]=='SDINBDG4-8G')
    actual={}
    for u in nodes(symbol,'symbol'):
        for p in nodes(u,'pin'):
            number=nodes(p,'number')[0][1]
            balls=number[1:-1].split(',') if number.startswith('[') else [number]
            for ball in balls:
                assert ball not in actual
                actual[ball]=(nodes(p,'name')[0][1],str(p[1]))
    assert actual=={b:(p['name'],p['type']) for b,p in expected.items()}
    fp=sx.loads((root/'lib/full-adapter.pretty/SanDisk_SDINBDG4_BGA153_11.5x13mm_P0.5mm.kicad_mod').read_text())
    pads={p[1]:p for p in nodes(fp,'pad')}
    assert set(pads)==set(expected)
    for b,p in pads.items():
        assert nodes(p,'at')[0][1:3]==expected[b]['xy_mm']
        assert nodes(p,'size')[0][1:3]==[.24,.24]
    with tempfile.TemporaryDirectory(prefix='emmc-check-') as directory:
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
        # Independent manufacturer anchors, not generated from the intent map.
        host=['A24','C21','B24','D21','A25','E21','E22','B25']
        device=['A3','A4','A5','B2','B3','B4','B5','B6']
        for i,(h,d) in enumerate(zip(host,device)):
            want={('U1',h),('U6',d),(f'R{610+i}','2')}
            if i==0:want.add(('TP600','1'))
            assert local(f'EMMC_D{i}')==want,i
        assert local('EMMC_CMD')=={('U1','B22'),('U6','M5'),('R618','2')}
        assert local('EMMC_RESET_L')=={('U1','F20'),('U6','K5'),('R619','2')}
        assert local('SOC_EMMC_CLK')=={('U1','A23'),('R600','1')}
        assert local('EMMC_CLK')=={('U6','M6'),('R600','2')}
        assert local('EMMC_DS_RAW')=={('U6','H5'),('R601','1')}
        assert local('EMMC_DS')=={('U1','A26'),('R601','2'),('R602','1')}
        assert ('R602','2') in nets['GND']
        assert {b for r,b in nets['VCC3V3_S0'] if r=='U6'}=={'E6','F5','J10','K9'}
        assert {b for r,b in nets['VCC1V8_SYS'] if r=='U6'}=={'C6','M4','N4','P3','P5'}
        assert {b for r,b in nets['GND'] if r=='U6'}=={'A6','E7','G5','H10','J5','K8','C4','N2','N5','P4','P6'}
        assert ('U1','H18') in nets['VCC1V8_SYS']
        assert nets['FLASH_VOL_SEL']=={('U1','AG25'),('R560','2')}
        for ref in range(610,620):assert (f'R{ref}','1') in nets['VCC1V8_SYS']
        for ref in range(600,612):
            assert (f'C{ref}','2') in nets['GND']
            if ref<611:assert (f'C{ref}','1') in nets['VCC3V3_S0' if ref<605 else 'VCC1V8_SYS']
        containing=lambda node:[v for v in nets.values() if node in v]
        assert containing(('U6','C2'))==[{('U6','C2'),('C611','1')}]
        for i,ball in enumerate(['E9','E10','F10','K10']):
            assert containing(('U6',ball))==[{('U6',ball),(f'TP{610+i}','1')}]
        for ref in ['TP601','TP614']:assert (ref,'1') in nets['GND']
        for ball,p in expected.items():
            if p['name']=='NC':assert all(len(v)==1 for v in containing(('U6',ball)))
        parts={c.get('ref'):c for c in tree.findall('.//components/comp')}
        fields={f.get('name'):f.text for f in parts['U6'].findall('fields/field')}
        assert (fields['MPN'],fields['LCSC'])==('SDINBDG4-8G','C577444')
        for ref,value in {'R600':'22R 1%','R601':'0R','R602':'47kR 1%',
                          'C600':'22uF','C605':'22uF','C611':'1uF',
                          **{f'R{i}':'10kR 1%' for i in range(610,620)}}.items():
            assert parts[ref].findtext('value')==value,ref
        for ref in ['TP600','TP601','TP610','TP611','TP612','TP613','TP614']:
            assert parts[ref].findtext('footprint')=='TestPoint:TestPoint_Pad_D1.0mm'
            assert parts[ref].find("property[@name='exclude_from_bom']") is not None
    return {'status':'EMMC_CAPTURE_CHECKPOINT_NOT_RELEASE','physical_balls':153,
            'data_bits':8,'supply_balls':9,'ground_balls':11,'unused_balls':116,
            'bypass_capacitors':12,'vendor_test_pads':4,'recovery_pad_pair':True,
            'hardware_reset_connected':True,'power_budget_closed':False,
            'boot_and_signal_integrity_verified_on_hardware':False,'system_routed':False}


if __name__=='__main__':
    result=check()
    (ROOT/'research/emmc-validation.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
