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
    with tempfile.TemporaryDirectory(prefix='cpu-circuit-check-') as directory:
        xml = Path(directory) / 'nets.xml'
        subprocess.run([CLI,'sch','export','netlist','--format','kicadxml','-o',str(xml),
                        str(root/'cad/full-adapter.kicad_sch')],check=True,capture_output=True)
        tree = ET.parse(xml)
        nets = {n.get('name'):{(p.get('ref'),p.get('pin')) for p in n.findall('node')}
                for n in tree.findall('.//nets/net')}
        def attached(pin):
            matches=[net for net in nets.values() if pin in net]
            assert len(matches)==1, pin
            return matches[0]
        assert nets['VCC5V_SYS'] == {('U4',p) for p in ['D1','D2','E1','E2']} | {(f'C{i}','1') for i in range(300,304)}
        assert attached(('U4','D3')) == {('U4',p) for p in ['D3','D4','E3','E4']} | {('L300','1')}
        assert attached(('U4','A2')) == {('U4','A2'),('R300','2'),('C304','1')}
        assert nets['VCC3V3_PMU'] == {('R300','1'),('U5','31'),('C407','1')}
        assert nets['PMIC_SLEEP_H'] == {('U4','A1'),('R302','1')}
        assert nets['I2C0_SCL_PMIC'] == {('U4','A3')}
        assert nets['I2C0_SDA_PMIC'] == {('U4','B1')}
        assert nets['VDD_CPU_COM'] == {('U1','M15'),('U4','A4'),('R301','2'),('C305','2')}
        assert {('L300','2'),('R301','1'),('C305','1')} <= nets['VDD_CPU']
        assert nets['VDD_CPU'].isdisjoint(nets['VDD_CPU_COM'])
        for pin in ['B2','B3','C1','C2','C3','C4','B4']:assert ('U4',pin) in nets['GND']
        for i in [300,301,302,303,304,306,307,308,309]:assert (f'C{i}','2') in nets['GND']
        assert ('R302','2') in nets['GND']
        parts={p.get('ref'):p for p in tree.findall('.//components/comp')}
        for ref,value in {'L300':'0.35uH','R300':'51kR 1%','R301':'100R 1%','R302':'100kR 1%','C304':'100nF','C305':'1uF',**{f'C{i}':'22uF' for i in [300,301,302,303,306,307,308,309]}}.items():
            assert parts[ref].findtext('value')==value,ref
            fields={f.get('name'):f.text for f in parts[ref].findall('fields/field')}
            if value=='22uF':assert (fields['MPN'],fields['LCSC'])==('CL21A226MAYNNNE','C602037')
            if ref=='L300':assert (fields['MPN'],fields['LCSC'])==('SPM5030T-R35M','C695608')
        inductor=sx.loads((root/'lib/full-adapter.pretty/L_TDK_SPM5030.kicad_mod').read_text())
        pads=children(inductor,'pad');assert len(pads)==2
        for p in pads:
            assert one(p,'at')[1:3]==([-2.1,0] if p[1]=='1' else [2.1,0])
            assert one(p,'size')[1:]==[1.5,2.2]
    return {'status': 'CPU_REGULATOR_CAPTURE_CHECKPOINT_NOT_RELEASE', 'physical_pins': 20,
            'native_stack_export_verified': True, 'land_diameter_mm': .15,
            'footprint_sha256': hashlib.sha256(fp_path.read_bytes()).hexdigest(),
            'power_circuit_integrated': True, 'upstream_rails_integrated': False,
            'assembly_process_qualified': False}


if __name__ == '__main__':
    result = check()
    (ROOT / 'research/cpu-regulator-validation.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))
