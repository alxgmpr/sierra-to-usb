"""Check fixed RK3568 PMU/PLL ball assignments and local bypass independently."""
from pathlib import Path
from xml.etree import ElementTree as ET
import json
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
CLI = '/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli'


def check(root=ROOT):
    with tempfile.TemporaryDirectory(prefix='processor-pmu-check-') as directory:
        xml = Path(directory)/'nets.xml'
        subprocess.run([CLI,'sch','export','netlist','--format','kicadxml','-o',str(xml),
                        str(root/'cad/full-adapter.kicad_sch')],check=True,capture_output=True)
        tree = ET.parse(xml)
        nets = {n.get('name'):{(p.get('ref'),p.get('pin')) for p in n.findall('node')}
                for n in tree.findall('.//nets/net')}
        parts = {p.get('ref'):p for p in tree.findall('.//components/comp')}
        anchors = {'V21':'VDD0V9_PMU', 'Y21':'VCC1V8_PMU', 'P11':'VDD0V9_ANLG',
                   'N10':'VCC1V8_ANLG', 'V19':'VDD0V9_PMU', 'Y20':'VCC3V3_PMU', 'W19':'VCC1V8_PMU'}
        for ball,rail in anchors.items():
            assert ('U1',ball) in nets[rail],(ball,rail)
            assert [name for name,nodes in nets.items() if ('U1',ball) in nodes] == [rail]
        cap_rails = ['VDD0V9_PMU']*2 + ['VCC1V8_PMU']*2 + ['VDD0V9_ANLG']*2 + ['VCC1V8_ANLG']*2 + ['VDD0V9_PMU']*2 + ['VCC3V3_PMU','VCC1V8_PMU']
        for i,rail in enumerate(cap_rails):
            ref = f'C{500+i}'
            assert (ref,'1') in nets[rail] and (ref,'2') in nets['GND'],ref
            expected = '1uF' if i < 10 and i % 2 == 0 else '100nF'
            assert parts[ref].findtext('value') == expected,ref
            assert parts[ref].findtext('footprint') == 'Capacitor_SMD:C_0402_1005Metric',ref
            fields = {f.get('name'):f.text for f in parts[ref].findall('fields/field')}
            assert fields['MPN'] and fields['LCSC'],ref
            if expected == '1uF': assert (fields['MPN'],fields['LCSC']) == ('CL05A105KA5NQNC','C52923')
        library = json.loads((root/'research/core-symbols.json').read_text())['RK3568B2']
        balls = [p['ball'] for u in library for p in u['pins']]
        assert len(balls) == len(set(balls)) == 636
        assert {p['ball'] for p in library[13]['pins']} == set(anchors)
        assert library[16]['title'] == 'Core supplies'
    return {'status':'PROCESSOR_PMU_CAPTURE_CHECKPOINT_NOT_RELEASE','supply_balls':7,
            'local_bypass_capacitors':12,'pmu_0v9_peak_mA':60,'ldo3_rating_mA':100,
            'remaining_processor_supplies_integrated':True,'system_routed':False}


if __name__ == '__main__':
    result = check()
    (ROOT/'research/processor-pmu-validation.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
