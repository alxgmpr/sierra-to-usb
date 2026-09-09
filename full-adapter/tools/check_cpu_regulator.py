"""Check all RK860 balls, native stack expansion, and generated land geometry."""
from pathlib import Path
import hashlib
import json
import subprocess
import tempfile
from xml.etree import ElementTree as ET
import sexpdata as sx

ROOT = Path(__file__).resolve().parents[1]
CLI = '/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli'


def children(node, tag):
    return [item for item in node if isinstance(item, list) and str(item[0]) == tag]


def one(node, tag):
    return children(node, tag)[0]


def check(root=ROOT):
    source = json.loads((root / 'research/cpu-regulator-pins.json').read_text())
    expected = {p['ball']: p for p in source['pins']}
    lib = sx.loads((root / 'lib/full-adapter.kicad_sym').read_text())
    symbol = next(s for s in children(lib, 'symbol') if s[1] == 'RK860-0')
    pins = [p for unit in children(symbol, 'symbol') for p in children(unit, 'pin')]
    physical = {}
    labels = []
    wires = []
    for index, pin in enumerate(pins):
        number = one(pin, 'number')[1]
        numbers = number[1:-1].split(',') if number.startswith('[') else [number]
        name = one(pin, 'name')[1]
        for ball in numbers:
            assert ball not in physical, ball
            assert (name, str(pin[1])) == (expected[ball]['name'], expected[ball]['type']), ball
            physical[ball] = name
        x, y, angle = one(pin, 'at')[1:]
        assert angle in (0, 180)
        assert abs(x / 2.54 - round(x / 2.54)) < 1e-6
        assert abs(y / 2.54 - round(y / 2.54)) < 1e-6
        x, y = round(100+x, 6), round(100-y, 6)
        ex = round(x + (-5.08 if angle == 0 else 5.08), 6)
        wires.append(f'(wire (pts (xy {x} {y}) (xy {ex} {y})) (stroke (width 0) (type default)))')
        labels.append(f'(label "{name}" (at {ex} {y} 0) (effects (font (size 1.27 1.27)) (justify left bottom)))')
    assert set(physical) == set(expected) and len(physical) == 20
    fp_name = source['footprint'].split(':')[1]
    fp_path = root / 'lib/full-adapter.pretty' / (fp_name + '.kicad_mod')
    fp = sx.loads(fp_path.read_text())
    pads = children(fp, 'pad')
    assert len(pads) == 20 and {p[1] for p in pads} == set(expected)
    for pad in pads:
        ball = expected[pad[1]]
        assert one(pad, 'at')[1:3] == [ball['x_mm'], ball['y_mm']], ball
        assert one(pad, 'size')[1:] == [.15, .15], ball
        assert str(pad[2]) == 'smd' and str(pad[3]) == 'circle'
        assert set(one(pad, 'layers')[1:]) == {'F.Cu', 'F.Paste', 'F.Mask'}
    assert one(fp, 'solder_mask_margin')[1] == .05
    model = root / 'lib/full-adapter.3dshapes' / (fp_name + '.step')
    assert model.is_file()
    assert one(fp, 'model')[1] == '${KIPRJMOD}/../lib/full-adapter.3dshapes/' + model.name
    # Fresh KiCad export verifies that a native alphanumeric stack really expands
    # to distinct PCB pins. The test drawing stays outside the design hierarchy.
    symbol[1] = 'probe:RK860-0'
    with tempfile.TemporaryDirectory(prefix='rk860-check-') as directory:
        sch = Path(directory) / 'probe.kicad_sch'
        xml = Path(directory) / 'probe.xml'
        sch.write_text('(kicad_sch (version 20250114) (generator "probe") (paper "A4") '
                       '(lib_symbols ' + sx.dumps(symbol) + ') ' + '\n'.join(wires + labels) +
                       '(symbol (lib_id "probe:RK860-0") (at 100 100 0) (unit 1) '
                       '(in_bom yes) (on_board yes) (property "Reference" "U1" (at 100 70 0) '
                       '(effects (font (size 1.27 1.27)))) (property "Value" "RK860-0" '
                       '(at 100 72.54 0) (effects (font (size 1.27 1.27))))))')
        subprocess.run([CLI, 'sch', 'export', 'netlist', '--format', 'kicadxml', '-o', str(xml), str(sch)],
                       check=True, capture_output=True, text=True)
        nets = ET.parse(xml).findall('.//nets/net')
        actual = {}
        for net in nets:
            for pin in net.findall('node'):
                assert pin.attrib['ref'] == 'U1'
                actual[pin.attrib['pin']] = net.attrib['name'].split('/')[-1]
        assert actual == physical, (actual, physical)
    return {'status': 'CPU_REGULATOR_LIBRARY_CHECKPOINT_NOT_RELEASE', 'physical_pins': 20,
            'native_stack_export_verified': True, 'land_diameter_mm': .15,
            'footprint_sha256': hashlib.sha256(fp_path.read_bytes()).hexdigest(),
            'power_circuit_integrated': False, 'assembly_process_qualified': False}


if __name__ == '__main__':
    result = check()
    (ROOT / 'research/cpu-regulator-validation.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))
