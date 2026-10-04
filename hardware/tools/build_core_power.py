#!/usr/bin/env python3
"""Capture logic/GPU local bypass values from NanoPi R3S reference sheet 5."""
from pathlib import Path
import uuid

ROOT = Path(__file__).resolve().parents[1]
LIB = Path('/Applications/KiCad/KiCad.app/Contents/SharedSupport/symbols')

def uid(key):
    return str(uuid.uuid5(uuid.NAMESPACE_URL, 'sierra-core-power-' + key))

def block(text, start):
    depth = 0
    quoted = escaped = False
    for i in range(start, len(text)):
        c = text[i]
        if escaped:
            escaped = False
            continue
        if quoted and c == '\\':
            escaped = True
            continue
        if c == '"':
            quoted = not quoted
        if not quoted:
            depth += (c == '(') - (c == ')')
            if depth == 0:
                return text[start:i+1]
    raise ValueError('Unbalanced symbol')

def symbol(lib, name):
    raw = (LIB / (lib + '.kicad_sym')).read_text()
    return block(raw, raw.index('(symbol "' + name + '"')).replace(
        '(symbol "' + name + '"', '(symbol "' + lib + ':' + name + '"', 1)

def prop(name, value, x, y, hidden=False):
    return f'(property "{name}" "{value}" (at {x} {y} 0) (effects (font (size 1.27 1.27))' + (' (hide yes)' if hidden else '') + '))'

items = []
def wire(a, b, key):
    items.append(f'(wire (pts (xy {a[0]} {a[1]}) (xy {b[0]} {b[1]})) (stroke (width 0) (type default)) (uuid "{uid(key)}"))')

parts = {
    '100nF': ('CL10B104KA8NNNC', 'C1590', '0603_1608Metric', 'X7R'),
    '4.7uF': ('CL10A475KA8NQNC', 'C69335', '0603_1608Metric', 'X5R'),
    '10uF': ('CL31B106KAHNNNE', 'C14860', '1206_3216Metric', 'X7R'),
    '22uF': ('CL32B226KAJNNNE', 'C309062', '1210_3225Metric', 'X7R'),
}
for bank, net, y, values, under_count, first_ref in [
    (0, 'VDD_LOGIC', 66.04, ['100nF','4.7uF','4.7uF','4.7uF','22uF','10uF','22uF'], 4, 825),
    (1, 'VDD_GPU', 132.08, ['100nF','4.7uF','22uF','10uF','22uF'], 2, 832),
]:
    xs = [60.96 + 25.4*i for i in range(len(values))]
    for i, (x, value) in enumerate(zip(xs, values)):
        ref = f'C{first_ref+i}'
        mpn, lcsc, package, dielectric = parts[value]
        properties = prop('Reference', ref, x+7.62, y-1.27) + prop('Value', value, x+7.62, y+1.27)
        fields = {'MPN':mpn, 'Manufacturer':'Samsung Electro-Mechanics', 'LCSC':lcsc,
                  'Footprint':'Capacitor_SMD:C_'+package, 'Voltage Rating':'25V',
                  'Dielectric':dielectric, 'Tolerance':'10%',
                  'Placement Intent':'under processor package' if i < under_count else 'close to processor package',
                  'Qualification':'Reference nominal value; bias, aging, impedance, placement and regulator stability pending'}
        for name, field in fields.items():
            properties += prop(name, field, x, y, True)
        items.append(f'(symbol (lib_id "Device:C_Small") (at {x} {y} 0) (unit 1) (in_bom yes) (on_board yes) (dnp no) (uuid "{uid(ref)}") {properties} ' + ''.join(f'(pin "{p}" (uuid "{uid(ref+":"+p)}"))' for p in ['1','2']) + f' (instances (project "core-power" (path "/{uid("root")}" (reference "{ref}") (unit 1)))))')
        wire((x,y-2.54),(x,y-10.16),ref+'-top')
        wire((x,y+2.54),(x,y+10.16),ref+'-bottom')
    for i in range(len(xs)-1):
        for side, yy in [('top',y-10.16),('bottom',y+10.16)]:
            wire((xs[i],yy),(xs[i+1],yy),f'{bank}-{side}-{i}')
    for x in xs[1:-1]:
        for yy in [y-10.16,y+10.16]:
            items.append(f'(junction (at {x} {yy}) (diameter 0) (color 0 0 0 0) (uuid "{uid(str(bank)+str(x)+str(yy))}"))')
    items.append(f'(global_label "{net}" (shape passive) (at {xs[0]} {y-10.16} 0) (effects (font (size 1.27 1.27)) (justify right)) (uuid "{uid(net)}"))')
    x, gy = xs[0], y+10.16
    wire((x,gy),(x,gy+5.08),net+'-ground-wire')
    properties = prop('Reference',f'#PWR80{bank}',x,gy+5.08,True)+prop('Value','GND',x,gy+8.89)
    items.append(f'(symbol (lib_id "power:GND") (at {x} {gy+5.08} 0) (unit 1) (in_bom no) (on_board yes) (dnp no) (uuid "{uid(net+"-ground")}") {properties} (pin "1" (uuid "{uid(net+"-ground-pin")}")) (instances (project "core-power" (path "/{uid("root")}" (reference "#PWR80{bank}") (unit 1)))))')
    items.append(f'(text "{net}: local bypass; first {under_count} capacitors under package, remaining capacitors nearby." (at 35.56 {y-22.86} 0) (effects (font (size 1.27 1.27)) (justify left)) (uuid "{uid(net+"-note")}"))')
items.append(f'(text "DRAFT CORE BYPASS: NanoPi R3S LTS 2411 sheet 5 nominal values.\nEffective capacitance, layout feasibility, PDN impedance and regulator stability remain to verify." (at 25.4 20.32 0) (effects (font (size 1.27 1.27)) (justify left)) (uuid "{uid("note")}"))')
root = uid('root')
(ROOT/'core-power.kicad_sch').write_text(f'(kicad_sch (version 20250114) (generator eeschema) (uuid "{root}") (paper "A4") (title_block (title "Processor logic and GPU local bypass — DRAFT") (date "2026-10-04")) (lib_symbols {symbol("Device","C_Small")} {symbol("power","GND")}) ' + ' '.join(items) + ' (sheet_instances (path "/" (page "1"))))\n')
print('Generated twelve processor-local logic/GPU bypass capacitors.')
