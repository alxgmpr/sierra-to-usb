#!/usr/bin/env python3
"""Capture all native RK3566 units as an explicitly incomplete standalone draft."""
from pathlib import Path
import re
import uuid
ROOT = Path(__file__).resolve().parents[1]
def uid(key):
    return str(uuid.uuid5(uuid.NAMESPACE_URL, 'sierra-processor-' + key))
def block(text, start):
    depth = 0
    quoted = escape = False
    for i in range(start, len(text)):
        c = text[i]
        if escape:
            escape = False
            continue
        if quoted and c == '\\':
            escape = True
            continue
        if c == '"':
            quoted = not quoted
        if not quoted:
            depth += (c == '(') - (c == ')')
            if depth == 0:
                return text[start:i+1]
    raise ValueError('Unbalanced expression')
def prop(name, value, x, y, hidden=False):
    return f'(property "{name}" "{value}" (at {x} {y} 0) (effects (font (size 1.27 1.27))' + (' (hide yes)' if hidden else '') + '))'
source = (ROOT / 'reference/rk3566-electrical-review.kicad_sym').read_text()
symbol = block(source, source.index('(symbol "RK3566"')).replace('(symbol "RK3566"', '(symbol "ProcessorDraft:RK3566"', 1)
# No production footprint assignment until land-pattern review is complete.
symbol = re.sub(r'("Footprint"\s+)"[^"]*"', r'\1""', symbol, count=1)
(ROOT / 'ProcessorDraft.kicad_sym').write_text('(kicad_symbol_lib (version 20211014) (generator eeschema) ' + symbol.replace('(symbol "ProcessorDraft:RK3566"','(symbol "RK3566"',1) + ')\n')
items = []
ground_balls = set()
control_nets = {'AJ37':'PMIC_I2C_SCL','AK38':'PMIC_I2C_SDA','1P19':'PMIC_SLEEP','AG38':'RK_RESET_N'}
connected_controls = set()
rail_balls = {}
for unit, x, y in [(1,76.2,76.2),(2,177.8,177.8),(3,279.4,139.7),(4,431.8,76.2),(5,76.2,304.8),(6,279.4,304.8),(7,444.5,228.6),(8,444.5,330.2)]:
    body = block(symbol, symbol.index(f'(symbol "RK3566_{unit}_1"'))
    top = float(re.search(r'\(start [-\d.]+ ([-\d.]+)\)', body)[1])
    pins = re.findall(r'\(number "([^"]+)"', body)
    for px, py, angle, name, number in re.findall(r'\(pin \w+ \w+.*?\(at ([-\d.]+) ([-\d.]+) ([-\d.]+)\).*?\(name "([^"]+)".*?\(number "([^"]+)"', body, re.S):
        rail = ('VDD_LOGIC' if name.startswith('VDD_LOGIC_') or name == 'PMU_VDD_LOGIC_0V9' else 'VDD_GPU' if name.startswith('VDD_GPU_') else 'VCC3V3_PMU' if name in {'PMUIO1','PMUIO2'} else None)
        if rail:
            rail_balls[number] = rail
        control = control_nets.get(number) or rail
        if control:
            if number in control_nets:
                connected_controls.add(number)
            ax, ay = round(x + float(px),4), round(y - float(py),4)
            left = float(px) < 0
            bx = round(ax + (-12.7 if left else 12.7),4)
            items.append(f'(wire (pts (xy {ax} {ay}) (xy {bx} {ay})) (stroke (width 0) (type default)) (uuid "{uid("control-wire-"+number)}"))')
            items.append(f'(global_label "{control}" (shape passive) (at {bx} {ay} {0 if left else 180}) (effects (font (size 1.27 1.27)) (justify {"right" if left else "left"})) (uuid "{uid("control-label-"+number)}"))')
        if not (re.fullmatch(r'(?:VSS|AVSS|AVSS1)_\d+', name) or name in {'DDR_AVSS','PMUPLL_AVSS','SYSPLL_AVSS'}):
            continue
        ground_balls.add(number)
        ax, ay = round(x + float(px),4), round(y - float(py),4)
        left = float(px) < 0
        bx = round(ax + (-7.62 if left else 7.62),4)
        items.append(f'(wire (pts (xy {ax} {ay}) (xy {bx} {ay})) (stroke (width 0) (type default)) (uuid "{uid("ground-wire-"+number)}"))')
        items.append(f'(global_label "GND" (shape passive) (at {bx} {ay} {0 if left else 180}) (effects (font (size 1.27 1.27)) (justify {"right" if left else "left"})) (uuid "{uid("ground-label-"+number)}"))')
    fields = prop('Reference','U801',x,y-top-7.62) + prop('Value','RK3566',x,y-top-5.08)
    for key,value in {'Footprint':'','MPN':'RK3566','Manufacturer':'Rockchip','LCSC':'C2943786','Qualification':'DRAFT: supplies, peripherals, TVSS and land pattern unresolved'}.items():
        fields += prop(key,value,x,y,True)
    items.append(f'(symbol (lib_id "ProcessorDraft:RK3566") (at {x} {y} 0) (unit {unit}) (in_bom yes) (on_board yes) (dnp no) (uuid "{uid(str(unit))}") {fields} ' + ''.join(f'(pin "{n}" (uuid "{uid("pin-"+n)}"))' for n in pins) + f' (instances (project "processor" (path "/{uid("root")}" (reference "U801") (unit {unit})))))')
items.append(f'(text "INCOMPLETE PROCESSOR CAPTURE: all 565 balls present; documented grounds, logic/GPU and PMU supplies connected; circuitry incomplete.\\nPMIC controls: AJ37=I2C0 SCL, AK38=I2C0 SDA, 1P19=PMIC_SLEEP.\\n19 alternate roles and TVSS unresolved. No production footprint assigned.\\nIntegrated draft: CPU, DDR, analog/IO supplies and peripheral circuitry remain open." (at 25.4 20.32 0) (effects (font (size 1.27 1.27)) (justify left)) (uuid "{uid("note")}"))')
(ROOT / 'processor.kicad_sch').write_text(f'(kicad_sch (version 20250114) (generator eeschema) (uuid "{uid("root")}") (paper "A2") (title_block (title "RK3566 processor — INCOMPLETE") (date "2026-10-04")) (lib_symbols {symbol}) ' + ' '.join(items) + ' (sheet_instances (path "/" (page "1"))))\n')
assert len(rail_balls) == 17
assert connected_controls == set(control_nets)
assert len(ground_balls) == 187 and '1M18' not in ground_balls
print('Generated standalone eight-unit processor draft, U801; 187 documented ground balls connected.')
