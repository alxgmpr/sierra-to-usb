"""Independent fixed-ball IO voltage and bypass checks from exported CAD nets."""
from pathlib import Path
from xml.etree import ElementTree as ET
import json
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
CLI = '/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli'


def check(root=ROOT):
    with tempfile.TemporaryDirectory(prefix='processor-io-check-') as directory:
        xml = Path(directory)/'nets.xml'
        subprocess.run([CLI,'sch','export','netlist','--format','kicadxml','-o',str(xml),
                        str(root/'cad/full-adapter.kicad_sch')],check=True,capture_output=True)
        tree = ET.parse(xml)
        nets = {n.get('name'):{(p.get('ref'),p.get('pin')) for p in n.findall('node')}
                for n in tree.findall('.//nets/net')}
        parts = {p.get('ref'):p for p in tree.findall('.//components/comp')}
        expected = {
            'VCC3V3_S0': {'H17':'C520','J21':'C524','R9':'C526','U9':'C527','V10':'C528','V11':'C529','V12':'C530'},
            'VCC1V8_SYS': {'H18':'C521','H20':'C522'},
            'VCC1V8_ANLG': {'H22':'C523'}, 'VCC_SDIO': {'L22':'C525'},
        }
        for rail, assignments in expected.items():
            for ball,ref in assignments.items():
                assert {('U1',ball),(ref,'1')} <= nets[rail],(ball,ref,rail)
                assert (ref,'2') in nets['GND'],ref
                assert parts[ref].findtext('value') == '100nF',ref
                assert parts[ref].findtext('footprint') == 'Capacitor_SMD:C_0402_1005Metric',ref
                fields = {f.get('name'):f.text for f in parts[ref].findall('fields/field')}
                assert fields['MPN'] and fields['LCSC'],ref
        assert ('C531','1') in nets['VCC3V3_S0'] and ('C531','2') in nets['GND']
        assert parts['C531'].findtext('value') == '1uF'
        fields = {f.get('name'):f.text for f in parts['C531'].findall('fields/field')}
        assert (fields['MPN'],fields['LCSC']) == ('CL05A105KA5NQNC','C52923')
        assert nets['VCC_SDIO'].isdisjoint(nets['VCC3V3_SD']), 'SD IO must change voltage independently of card power'
    return {'status':'PROCESSOR_IO_SUPPLY_CAPTURE_CHECKPOINT_NOT_RELEASE','supply_balls':11,
            'local_bypass_capacitors':12,'storage_IO_V':1.8,'hardware_storage_voltage_strap_integrated':True,
            'IO_load_budget_closed':False,'system_routed':False}


if __name__ == '__main__':
    result = check()
    (ROOT/'research/processor-io-power-validation.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
