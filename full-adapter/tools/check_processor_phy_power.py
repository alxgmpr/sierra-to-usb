"""Check USB filter paths, physical supply balls and grounded unused PHYs."""
from pathlib import Path
from xml.etree import ElementTree as ET
import json
import subprocess
import tempfile
import sexpdata as sx

ROOT = Path(__file__).resolve().parents[1]
CLI = '/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli'


def check(root=ROOT):
    with tempfile.TemporaryDirectory(prefix='processor-phy-check-') as directory:
        xml = Path(directory)/'nets.xml'
        subprocess.run([CLI,'sch','export','netlist','--format','kicadxml','-o',str(xml),
                        str(root/'cad/full-adapter.kicad_sch')],check=True,capture_output=True)
        tree = ET.parse(xml)
        nets = {n.get('name'):{(p.get('ref'),p.get('pin')) for p in n.findall('node')}
                for n in tree.findall('.//nets/net')}
        parts = {p.get('ref'):p for p in tree.findall('.//components/comp')}
        assert nets['VDD0V9_USB'] == {('FB550','2'),('C551','1'),('U1','P22'),('U1','R8'),('C543','1'),('C545','1')}
        assert nets['VCC1V8_USB'] == {('FB551','2'),('C553','1'),('U1','P9'),('U1','P23'),('C541','1'),('C544','1')}
        expected = {
            'VCC3V3_S0': [('M23','C540'),('P10','C542')],
            'VDD0V9_ANLG': [('R20','C546'),('R21','C547')],
            'VCC1V8_ANLG': [('R22','C548')],
        }
        for rail,pairs in expected.items():
            for ball,cap in pairs: assert {('U1',ball),(cap,'1')} <= nets[rail]
        assert {('C549','1'),('C550','1'),('FB550','1')} <= nets['VDD0V9_ANLG']
        assert {('C552','1'),('FB551','1')} <= nets['VCC1V8_ANLG']
        for i in range(540,554):
            ref=f'C{i}';part=parts[ref]
            assert (ref,'2') in nets['GND']
            value = '100nF' if i < 548 else '4.7uF' if i < 550 else '1uF'
            assert part.findtext('value') == value,ref
            fields={f.get('name'):f.text for f in part.findall('fields/field')}
            assert fields['MPN'] and fields['LCSC'],ref
        for ref in ['FB550','FB551']:
            part=parts[ref]
            fields={f.get('name'):f.text for f in part.findall('fields/field')}
            assert (fields['MPN'],fields['LCSC'])==('BLM18PG121SN1D','C14709')
            assert part.findtext('footprint')=='full-adapter:Murata_BLM18PG121SN1D_0603'
        grounded=set('M20 M22 U20 U21 U22 V17 V18 W14 W15 W16 W18 Y14 Y15 Y17'.split())
        assert {('U1',p) for p in grounded} <= nets['GND']
        source=json.loads((root/'research/processor-pins.json').read_text())['pins']
        for p in source:
            if p['pin_type'] in {'PI','API'}:
                attached=[nodes for nodes in nets.values() if ('U1',p['ball']) in nodes]
                assert len(attached)==1 and len(attached[0])>1,('uncaptured supply',p['ball'])
        unused_domains={'EDP_TX','PCIE30','HDMI_TX','MIPI_DSI_TX1','MIPI_CSI_RX','MIPI_DSI_TX0/LVDS_TX0'}
        unused = [p['ball'] for p in source if p['power_domain'] in unused_domains and p['pin_type'] not in {'PI','API','G','AG'}]
        present = {p.get('num') for u in parts['U1'].findall('units/unit') for p in u.findall('pins/pin')}
        assert set(unused) <= present, ('unused units absent',set(unused)-present)
        for ball in unused:
            assert all(('U1',ball) not in nodes or nodes=={('U1',ball)} for nodes in nets.values()),ball
        assert len(unused)==63,len(unused)
    def nodes(n,tag):return [x for x in n if isinstance(x,list) and str(x[0])==tag]
    fp=sx.loads((root/'lib/full-adapter.pretty/Murata_BLM18PG121SN1D_0603.kicad_mod').read_text())
    pads=nodes(fp,'pad')
    assert len(pads)==2 and all(nodes(p,'size')[0][1:]==[.65,.7] for p in pads)
    assert {tuple(nodes(p,'at')[0][1:3]) for p in pads}=={(-.675,0),(.675,0)}
    return {'status':'PROCESSOR_PHY_SUPPLY_CAPTURE_CHECKPOINT_NOT_RELEASE','active_PHY_supply_balls':9,
            'grounded_unused_PHY_supply_balls':14,'unused_PHY_signal_balls':63,'local_capacitors':14,
            'all_processor_power_input_balls_present':True,'system_routed':False}


if __name__ == '__main__':
    result=check()
    (ROOT/'research/processor-phy-power-validation.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
