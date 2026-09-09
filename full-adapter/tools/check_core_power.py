"""Independent checks of processor supply groups, bypass and ground connections."""
from pathlib import Path
import json
import subprocess
import tempfile
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
CLI = '/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli'


def check(root=ROOT):
    source = json.loads((root / 'research/processor-pins.json').read_text())
    with tempfile.TemporaryDirectory(prefix='core-power-check-') as directory:
        xml = Path(directory) / 'nets.xml'
        subprocess.run([CLI, 'sch', 'export', 'netlist', '--format', 'kicadxml', '-o', str(xml),
                        str(root / 'cad/full-adapter.kicad_sch')], check=True, capture_output=True)
        tree = ET.parse(xml)
        nets = {n.get('name'): {(p.get('ref'), p.get('pin')) for p in n.findall('node')}
                for n in tree.findall('.//nets/net')}
        parts = {c.get('ref'): c for c in tree.findall('.//components/comp')}
        # Fixed package anchors from manufacturer table, independent of unit sorting.
        groups = {'VDD_CPU': 'J15 K15 K16 K17 K18 L15 L16 L17 L18 M17',
                  'VDD_LOGIC': 'L12 M12 N13 N16 P13 P16 R12 R16 T12 T16',
                  'VDD_GPU': 'R13 T13 U11 U12 U13',
                  'VDD_NPU': 'M19 N19 P18 P19 P20'}
        banks = {'VDD_CPU': (200, ['100nF','4.7uF','22uF','22uF','22uF']),
                 'VDD_LOGIC': (205, ['100nF','4.7uF','1uF','1uF','22uF','22uF','10uF']),
                 'VDD_GPU': (212, ['100nF','4.7uF','22uF','22uF','10uF']),
                 'VDD_NPU': (217, ['100nF','22uF','22uF','10uF'])}
        for rail, balls in groups.items():
            expected = {('U1', ball) for ball in balls.split()}
            start, values = banks[rail]
            for index, value in enumerate(values):
                ref = 'C' + str(start+index)
                expected.add((ref, '1'))
                assert (ref, '2') in nets['GND'], ref
                assert parts[ref].findtext('value') == value, ref
                fields = {f.get('name'): f.text for f in parts[ref].findall('fields/field')}
                assert fields['MPN'] and fields['LCSC'], ref
                assert 'Capacitor_SMD:C_' in parts[ref].findtext('footprint'), ref
            assert nets[rail] == expected, (rail, nets[rail] ^ expected)
        assert nets['VDD_CPU_COM'] == {('U1', 'M15')}
        ground_balls = {p['ball'] for p in source['pins'] if p['pin_type'] in {'G', 'AG'}}
        assert len(ground_balls) == 208
        actual = {pin for ref,pin in nets['GND'] if ref == 'U1'}
        assert actual == ground_balls, actual ^ ground_balls
        assert 'AB24' not in actual, 'TVSS is a temperature reference input, not ground'
    return {'status': 'CORE_POWER_CAPTURE_CHECKPOINT_NOT_RELEASE', 'core_supply_balls': 30,
            'ground_balls': 208, 'bypass_capacitors': 21, 'remote_sense_ball': 'M15',
            'regulators_integrated': False, 'system_routed': False}


if __name__ == '__main__':
    result = check()
    (ROOT / 'research/core-power-validation.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))
