"""Independent exported-net checks for the DDR capture checkpoint, not release."""
from collections import Counter
from pathlib import Path
import json
import re
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET
import sexpdata as sx

KICAD='/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli'


def children(n, tag):return [v for v in n if isinstance(v,list) and str(v[0])==tag]
def one(n,tag):return children(n,tag)[0]


def check(root, output=None):
    root=Path(root)
    source=json.loads((root/'research/processor-pins.json').read_text())
    memory=json.loads((root/'research/memory-pins.json').read_text())
    cpu_by_function={p.get('ddr3_function',p['canonical_name']):p['ball'] for p in source['pins']}
    mem_by_function={p['function']:p['ball'] for p in memory['pins'] if p['name'] not in {'VDD','VDDQ','VSS','VSSQ','NC'}}
    library=sx.loads((root/'lib/full-adapter.kicad_sym').read_text())
    for model, pins in [('RK3568B2',source['pins']),('H5TQ4G63EFR-RDC',memory['pins'])]:
        sym=next(s for s in children(library,'symbol') if s[1]==model)
        sy_pins=[p for u in children(sym,'symbol') for p in children(u,'pin')]
        actual=[one(p,'number')[1] for p in sy_pins]
        assert len(actual)==len(set(actual))==len(pins)
        assert set(actual)=={p['ball'] for p in pins}
        source_by_ball={p['ball']:p for p in pins}
        for p in sy_pins:
            original=source_by_ball[one(p,'number')[1]]
            if model=='RK3568B2':
                expected=original.get('ddr3_function',original['canonical_name'] if original['pin_type'] in {'G','AG','PI','API'} else original['canonical_name'].split('/')[0])
            else:
                expected=original['name'].split('/')[0]
            if expected.endswith('_N') and not expected.startswith(('PCIE','USB','MULTI')): expected='~{'+expected[:-2]+'}'
            if expected in {'DDR3_RASn','DDR3_CASn','DDR3_WEn','DDR3_RESETn','DDR3_CS0n','DDR3_CS1n'}:expected='~{'+expected[:-1]+'}'
            assert one(p,'name')[1]==expected,(model,original['ball'],one(p,'name')[1],expected)
        footprint=next(p[2] for p in children(sym,'property') if p[1]=='Footprint')
        fp=sx.loads((root/'lib/full-adapter.pretty'/ (footprint.split(':')[1]+'.kicad_mod')).read_text())
        pads={p[1]:p for p in children(fp,'pad')}
        assert set(pads)==set(actual)
        for p in pins:assert one(pads[p['ball']],'at')[1:3]==p['xy_mm']
    with tempfile.TemporaryDirectory(prefix='ddr-check-') as t:
        xml=Path(t)/'nets.xml'; erc=Path(t)/'erc.json'
        sch=root/'cad/full-adapter.kicad_sch'
        subprocess.run([KICAD,'sch','export','netlist',str(sch),'--format','kicadxml','-o',str(xml)],check=True,stdout=subprocess.DEVNULL)
        tree=ET.parse(xml)
        nets={n.get('name'):{(v.get('ref'),v.get('pin')) for v in n.findall('node')} for n in tree.findall('.//nets/net')}
        def net(suffix):
            matches=[(k,v) for k,v in nets.items() if k.rsplit('/',1)[-1]==suffix]
            assert len(matches)==1,(suffix,matches)
            return matches[0][1]
        def exact(name, expected):assert net(name)==set(expected),(name,net(name)^set(expected))
        def equal_pin_net(*pins):
            matches=[v for v in nets.values() if pins[0] in v]
            assert len(matches)==1 and matches[0]==set(pins),(pins,matches)
        for bit in range(32):
            exact(f'DDR3_DQ{bit}', [('U1',cpu_by_function[f'DDR3_DQ{bit}']),('U2' if bit<16 else 'U3',mem_by_function[f'DQ{bit%16}'])])
        for byte in range(4):
            ref='U2' if byte<2 else 'U3'; half='L' if byte%2==0 else 'U'
            exact(f'DDR3_DM{byte}', [('U1',cpu_by_function[f'DDR3_DM{byte}']),(ref,mem_by_function['DM'+half])])
            for polarity in ['P','N']:
                exact(f'DDR3_DQS{byte}_{polarity}', [('U1',cpu_by_function[f'DDR3_DQS{byte}{polarity}']),(ref,mem_by_function[f'DQS{half}_{polarity}'])])
        ca={**{f'A{i}':f'A{i}' for i in range(15)},**{f'BA{i}':f'BA{i}' for i in range(3)},'CKE':'CKE','CS0n':'CS_N','ODT0':'ODT','RASn':'RAS_N','CASn':'CAS_N','WEn':'WE_N','RESETn':'RESET_N'}
        ca['A10']='A10/AP';ca['A12']='A12/BC_N'
        for cpu,ram in ca.items():
            name='DDR3_'+cpu.replace('n','_N')
            expected=[('U1',cpu_by_function['DDR3_'+cpu]),('U2',mem_by_function[ram]),('U3',mem_by_function[ram])]
            if cpu=='RESETn':expected += [('C102','1'),('C103','1')]
            exact(name,expected)
        # Fixed physical anchors supplement the generated maps.
        exact('DDR3_DQ17',[('U1','A9'),('U3','F7')])
        exact('DDR3_DQS0_P',[('U1','G1'),('U2','F3')])
        exact('DDR3_DQS2_N',[('U1','B11'),('U3','G3')])
        exact('DDR3_CLK_P',[('U1','B4'),('U2','J7'),('U3','J7'),('R101','1')])
        exact('DDR3_CLK_N',[('U1','A4'),('U2','K7'),('U3','K7'),('R102','1')])
        equal_pin_net(('R101','2'),('R102','2'),('C101','1'))
        equal_pin_net(('U1','H7'),('R103','1'))
        equal_pin_net(('U2','L8'),('R106','1'))
        equal_pin_net(('U3','L8'),('R107','1'))
        exact('DDR_VREFCA',[('R104','2'),('R105','1'),('C112','1'),('C114','1'),('U2','M8'),('U3','M8')])
        exact('DDR_VREFDQ',[('U1','P8'),('U2','H1'),('U3','H1'),('C110','2'),('C111','1'),('C113','1'),('C115','1')])
        power=net('VCC_DDR');ground=net('GND');assert power.isdisjoint(ground)
        for ref in ['U2','U3']:
            for p in memory['pins']:
                pin=(ref,p['ball'])
                if p['name'] in {'VDD','VDDQ'}:assert pin in power
                elif p['name'] in {'VSS','VSSQ'}:assert pin in ground
                elif p['name']=='NC':assert all(pin not in ns or len(ns)==1 for ns in nets.values())
        for p in source['pins']:
            if p['power_domain'] in {'DDRPHY_VDDQ','DDRPHY_VDDQL'}:assert ('U1',p['ball']) in power
        for ref in ['R103','R105','R106','R107','C101','C102','C103','C111','C112','C113','C114','C115']:
            assert (ref,'2') in ground,ref
        assert ('C110','1') in power and ('R104','1') in power
        for n in range(120,173):assert ('C'+str(n),'1') in power and ('C'+str(n),'2') in ground
        components={c.get('ref'):c for c in tree.findall('.//components/comp')}
        for ref,val in {'R101':'49.9R 1%','R102':'49.9R 1%','R103':'120R 1%','R104':'1kR 1%','R105':'1kR 1%','R106':'240R 1%','R107':'240R 1%','C101':'100pF C0G'}.items():
            assert components[ref].findtext('value')==val
        for ref,c in components.items():
            if ref in {'TP560','TP561','TP562','TP600','TP601','TP610','TP611','TP612','TP613','TP614'}:
                assert c.find('libsource').get('part')=='TestPoint'
                assert c.findtext('footprint')=='TestPoint:TestPoint_Pad_D1.0mm'
                assert c.find("property[@name='exclude_from_bom']") is not None
                continue
            if ref in {'NT430','NT431','NT432'}:
                assert c.find('libsource').get('part')=='NetTie_2'
                assert c.find("property[@name='exclude_from_bom']") is not None
                continue
            fields={f.get('name'):f.text for f in c.findall('fields/field')}
            assert fields.get('MPN') and fields.get('LCSC'),ref
        # No waived integration findings: these are the exact open work at this
        # checkpoint, and release still requires their resolution.
        subprocess.run([KICAD,'sch','erc',str(sch),'--format','json','-o',str(erc)],check=True,stdout=subprocess.DEVNULL)
        erc_data=json.loads(erc.read_text())
        counts=Counter(v['type'] for s in erc_data['sheets'] for v in s['violations'])
        # CPU and DDR are driven through L300/L420 (documented power flags).
        # All processor supply balls are present. Upstream rails and remaining
        # functional units await capture; regulator I2C now connects to U1.
        expected={'missing_input_pin':1,'missing_bidi_pin':1,'missing_unit':1,'power_pin_not_driven':3,'isolated_pin_label':2}
        assert counts==expected,counts
        isolated=[v for sh in erc_data["sheets"] for v in sh["violations"] if v["type"]=="isolated_pin_label"]
        assert {v["items"][0]["description"] for v in isolated}=={"Global Label 'MODEM_HOST_USB2_P'", "Global Label 'MODEM_HOST_USB2_N'"}
        summary={'status':'DDR_CAPTURE_CHECKPOINT_NOT_RELEASE','library_pins_checked':732,'dq_nets':32,'dqs_pairs':4,'dm_nets':4,'shared_ca_nets':len(ca),'clock_rc':'2 x 49.9R 1%, common 100pF C0G to ground','erc_open_integration_findings':dict(counts),'system_routed':False}
        if output:
            Path(output).write_text(json.dumps(summary,indent=2)+'\n')
        print(json.dumps(summary,indent=2))
        return summary


if __name__=='__main__':
    check(Path(sys.argv[1]) if len(sys.argv)>1 else Path(__file__).resolve().parents[1], sys.argv[2] if len(sys.argv)>2 else None)
