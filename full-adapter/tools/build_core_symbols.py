"""Build auditable multi-unit symbols from reviewed manufacturer pin maps.

No pin is omitted, duplicated, or silently remapped. Unused processor
interfaces remain visible in separate units so their treatment is reviewable.
"""
from collections import Counter, OrderedDict
from pathlib import Path
import json
import math
import copy
import re
import sexpdata as sx

ROOT = Path(__file__).resolve().parents[1]
LIB = ROOT / 'lib/full-adapter.kicad_sym'
Q = lambda s: json.dumps(str(s), ensure_ascii=False)


def effects(size=1.27):
    return f'(effects (font (size {size} {size})))'


def display_name(name):
    if name.endswith('_N') and not name.startswith(('PCIE', 'USB', 'MULTI')):
        return '~{' + name[:-2] + '}'
    if name in {'DDR3_RASn', 'DDR3_CASn', 'DDR3_WEn', 'DDR3_RESETn', 'DDR3_CS0n', 'DDR3_CS1n'}:
        return '~{' + name[:-1] + '}'
    return name


def natural(value):
    return [int(s) if s.isdigit() else s for s in re.split(r'(\d+)', value)]


def make_symbol(name, footprint, datasheet, manufacturer, lcsc, description, units, keywords='processor DDR3 memory', footprint_filter=None):
    props = [('Reference', 'U'), ('Value', name), ('Footprint', footprint),
             ('Datasheet', datasheet), ('Description', description),
             ('Manufacturer', manufacturer), ('MPN', name), ('LCSC', lcsc),
             ('ki_keywords', keywords), ('ki_fp_filters', footprint_filter or ('FBGA*7.5x13mm*P0.8mm*' if name.startswith('H5') else 'RK3568B2*19x19mm*P0.65mm*'))]
    output = [f'(symbol {Q(name)} (pin_names (offset 0.508)) (in_bom yes) (on_board yes)']
    for i, (k, v) in enumerate(props):
        output.append(f'(property {Q(k)} {Q(v)} (at 0 {80-i*2.54} 0) {effects()}' + (' (hide yes)' if i > 1 else '') + ')')
    manifest = []
    for u, (title, pins) in enumerate(units.items(), 1):
        sides = {s: [] for s in 'LRTB'}
        for pin in pins:
            sides[pin.get('side', 'L' if pin['type'] == 'input' else 'R')].append(pin)
        def pin_gap(pin):
            # Native stacks print their numbers on separate lines above the pin.
            return 2.54 * math.ceil((len(pin.get('physical_pins', [pin['ball']])) + 1) / 2)
        n = max(sum(pin_gap(p) for p in sides['L']) / 2.54,
                sum(pin_gap(p) for p in sides['R']) / 2.54, 1)
        width = max(30.48, 2.54 * (max(len(sides['T']), len(sides['B'])) + 2))
        # Long power-domain names need room; keep units within an A3 page.
        width = max(width, 2.54 * (max((len(p['name']) for p in pins), default=10) // 2 + 2))
        width = max(width, 1.27 * (max((len(p['name']) for p in sides['L']), default=0) + max((len(p['name']) for p in sides['R']), default=0)) + 7.62, len(title)*.8+5.08)
        height = max(40.64 if sides['T'] and (sides['B'] or sides['L'] or sides['R']) else 15.24, (n + 3) * 2.54,
                     2 * max((len(p['name']) * .8 for p in sides['T'] + sides['B']), default=0) + 15.24)
        height = math.ceil(height / 5.08) * 5.08
        width = math.ceil(width / 5.08) * 5.08
        top, bottom = height / 2, -height / 2
        output.append(f'(symbol {Q(name + "_" + str(u) + "_1")}')
        output.append(f'(rectangle (start {-width/2} {top}) (end {width/2} {bottom}) (stroke (width 0.254) (type default)) (fill (type background)))')
        title_y = 0 if sides['T'] or sides['B'] else top-2.54
        output.append(f'(text {Q(title)} (at 0 {title_y} 0) {effects()})')
        ps = []
        for side, group in sides.items():
            cursor_y = (-2.54 if sides['T'] or sides['B'] else top - 2.54)
            for index, p in enumerate(group):
                if side in 'LR':
                    x = -width/2 - 2.54 if side == 'L' else width/2 + 2.54
                    cursor_y -= pin_gap(p)
                    y = cursor_y
                    angle = 0 if side == 'L' else 180
                else:
                    x = (index - len(group)//2) * 2.54
                    y = top + 2.54 if side == 'T' else bottom - 2.54
                    angle = 270 if side == 'T' else 90
                length = 0 if p['type'] == 'no_connect' else 2.54
                if p['type'] == 'no_connect':
                    x -= 2.54
                hidden = ' (hide yes)' if p['type'] == 'no_connect' else ''
                x, y = round(x, 6), round(y, 6)
                output.append(f'(pin {p["type"]} line (at {x} {y} {angle}) (length {length}){hidden} (name {Q(display_name(p["name"]))} {effects()}) (number {Q(p["ball"])} {effects()})')
                for alt in p.get('alternates', []):
                    if alt != p['name']:
                        output.append(f'(alternate {Q(display_name(alt))} {p["type"]} line)')
                output.append(')')
                ps.append(dict(p, at=[x, y, angle]))
        output.append(')')
        manifest.append({'unit': u, 'title': title, 'width': width, 'height': height, 'pins': ps})
    output.append(')')
    return '\n'.join(output), manifest


def memory():
    source = json.loads((ROOT / 'research/memory-pins.json').read_text())
    units = OrderedDict((s, []) for s in ['DDR3 command and data', 'DDR3 supplies'])
    for p in sorted(source['pins'], key=lambda p: natural(p['function'])):
        name = p['name']
        typ = p['electrical_type']
        unit = 'DDR3 supplies' if typ in {'power_in', 'no_connect'} or name in {'VREFCA', 'VREFDQ', 'ZQ'} else 'DDR3 command and data'
        side = ('T' if name in {'VDD', 'VDDQ'} else 'B' if name in {'VSS', 'VSSQ'} else
                'R' if typ in {'bidirectional', 'no_connect'} or name in {'DMU', 'DML'} else 'L')
        alternates = []
        if name in {'A10/AP', 'A12/BC_N'}:
            name, alternate = name.split('/')
            alternates = [alternate]
        units[unit].append({'ball': p['ball'], 'name': name, 'type': typ, 'side': side, 'alternates': alternates})
    return make_symbol(source['mpn'], source['footprint'],
                       'https://onwaytech.com/static/upload/datasheet/H5TQ4G63EFR.pdf',
                       source['manufacturer'], source['lcsc'], '4Gb DDR3-1866, 256M x16, 1.5V, FBGA96 7.5x13mm', units)


def processor():
    source = json.loads((ROOT / 'research/processor-pins.json').read_text())
    units = OrderedDict()
    for label in ['DDR3 command', 'DDR3 byte 0', 'DDR3 byte 1', 'DDR3 byte 2', 'DDR3 byte 3', 'DDR ECC unused', 'DDR3 supplies']:
        units[label] = []
    type_map = {'G':'power_in', 'AG':'power_in', 'PI':'power_in', 'API':'power_in',
                'PO':'power_out', 'O':'output', 'AO':'output', 'CO':'output',
                'I':'input', 'AI':'input', 'CI':'input', 'A':'passive',
                'I/O':'bidirectional', 'AI/O':'bidirectional'}
    ground_count = 0
    for p in source['pins']:
        original = p['canonical_name']
        name = p.get('ddr3_function', original.split('/')[0])
        typ = type_map[p['pin_type']]
        if typ == 'power_in':
            name = original
        domain = p['power_domain'] or 'General'
        side = 'L' if typ == 'input' else 'R'
        if p['pin_type'] in {'G', 'AG'}:
            title = 'Ground balls ' + str(ground_count // 26 + 1)
            ground_count += 1
            side = 'B'
        elif domain in {'DDRPHY_VDDQ', 'DDRPHY_VDDQL'}:
            title, side = 'DDR3 supplies', 'T'
        elif name.startswith('DDR3_'):
            m = re.fullmatch(r'DDR3_DQ(\d+)', name)
            lane = int(m[1]) // 8 if m else None
            m = re.fullmatch(r'DDR3_D(?:M|QS)(\d)[PN]?', name)
            if m:
                lane = int(m[1])
            title = 'DDR3 command' if lane is None else 'DDR3 byte ' + str(lane)
        elif name in {'DDR_RZQ', 'DDR_VREFOUT'}:
            title = 'DDR3 supplies'
        elif name.startswith('DDR_ECC'):
            title = 'DDR ECC unused'
        elif typ == 'power_in':
            title, side = 'Core supplies' if domain.startswith('VDD_') else 'Analog and IO supplies', 'L'
        else:
            title = domain.replace('\n', '')
        units.setdefault(title, []).append({'ball': p['ball'], 'name': name, 'type': typ, 'side': side,
            'alternates': [] if typ == 'power_in' else list(dict.fromkeys(v for v in original.split('/') if v not in {'-', name}))})
    assert sum(map(len, units.values())) == 636
    # Stable physical order for supplies; numerical order for byte and CA pins.
    for title, pins in units.items():
        if title.startswith('DDR3'):
            pins.sort(key=lambda p: natural(p['name']))
        elif title == 'Core supplies':
            order = {'CPU': 0, 'LOGIC': 1, 'GPU': 2, 'NPU': 3}
            pins.sort(key=lambda p: (order[p['name'].split('_')[1]], natural(p['name'])))
            for pin in pins:
                if pin['name'] == 'VDD_CPU_COM':
                    # HW Guide §2.2.2.4: remote sense tap, not an external supply feed.
                    pin['type'] = 'passive'
    return make_symbol('RK3568B2', 'full-adapter:RK3568B2_FCCSP636_19x19mm_P0.65mm',
                       'https://rockchip.fr/RK3568B2%20datasheet%20V2.3.pdf?download=1',
                       'Rockchip', 'C3345225', 'Quad Cortex-A55 Linux processor; exact B2 FCCSP636 pin population', units)


def cpu_regulator():
    source = json.loads((ROOT / 'research/cpu-regulator-pins.json').read_text())
    groups = OrderedDict()
    for pin in source['pins']:
        groups.setdefault(pin['name'], []).append(pin)
    pins = []
    for name in ['VIN', 'EN', 'VSEL', 'SCL', 'SDA', 'LX', 'VOUT', 'GND', 'AGND']:
        group = groups[name]
        numbers = [p['ball'] for p in group]
        pins.append({'ball': numbers[0] if len(numbers) == 1 else '[' + ','.join(numbers) + ']',
                     'physical_pins': numbers, 'name': name, 'type': group[0]['type'],
                     'side': 'R' if name in {'LX', 'VOUT', 'GND', 'AGND'} else 'L'})
    return make_symbol(source['mpn'], source['footprint'], source['source']['url'],
                       source['manufacturer'], source['lcsc'],
                       '6A I2C buck regulator, 0x40, 1.0V startup, WLCSP20',
                       {'CPU voltage regulator': pins}, keywords='buck regulator I2C CPU power',
                       footprint_filter='RK860*WLCSP20*P0.4mm*')


def main():
    syms, manifest = [], {}
    for name, fn in [('H5TQ4G63EFR-RDC', memory), ('RK3568B2', processor), ('RK860-0', cpu_regulator)]:
        symbol, units = fn()
        syms.append(symbol)
        manifest[name] = units
        all_pins = [number for u in units for p in u['pins'] for number in p.get('physical_pins', [p['ball']])]
        assert len(all_pins) == len(set(all_pins))
        print(name, len(all_pins), 'pins in', len(units), 'units')
    std = sx.loads(Path('/Applications/KiCad/KiCad.app/Contents/SharedSupport/symbols/power.kicad_sym').read_text())
    vdd = next(v for v in std if isinstance(v, list) and str(v[0]) == 'symbol' and v[1] == 'VDD')
    for rail in ('VCC_DDR', 'VDD_CPU', 'VDD_LOGIC', 'VDD_GPU', 'VDD_NPU'):
        power = copy.deepcopy(vdd)
        def rename(node):
            for i, v in enumerate(node):
                if isinstance(v, list): rename(v)
                elif isinstance(v, str) and (v == 'VDD' or v.startswith('VDD_')): node[i] = v.replace('VDD', rail, 1)
        rename(power)
        syms.append(sx.dumps(power))
    LIB.write_text('(kicad_symbol_lib (version 20251024) (generator "full_adapter_core_symbols")\n' + '\n'.join(syms) + '\n)\n')
    sx.loads(LIB.read_text())
    (ROOT / 'research/core-symbols.json').write_text(json.dumps(manifest, indent=2) + '\n')


if __name__ == '__main__':
    main()
