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
items = []
for unit, x, y in [(1,76.2,76.2),(2,177.8,177.8),(3,279.4,139.7),(4,431.8,76.2),(5,76.2,304.8),(6,279.4,304.8),(7,444.5,228.6),(8,444.5,330.2)]:
    body = block(symbol, symbol.index(f'(symbol "RK3566_{unit}_1"'))
    top = float(re.search(r'\(start [-\d.]+ ([-\d.]+)\)', body)[1])
    pins = re.findall(r'\(number "([^"]+)"', body)
    fields = prop('Reference','U801',x,y-top-7.62) + prop('Value','RK3566',x,y-top-5.08)
    for key,value in {'Footprint':'','MPN':'RK3566','Manufacturer':'Rockchip','LCSC':'C2943786','Qualification':'DRAFT: supplies, peripherals, TVSS and land pattern unresolved'}.items():
        fields += prop(key,value,x,y,True)
    items.append(f'(symbol (lib_id "ProcessorDraft:RK3566") (at {x} {y} 0) (unit {unit}) (in_bom yes) (on_board yes) (dnp no) (uuid "{uid(str(unit))}") {fields} ' + ''.join(f'(pin "{n}" (uuid "{uid("pin-"+n)}"))' for n in pins) + f' (instances (project "processor" (path "/{uid("root")}" (reference "U801") (unit {unit})))))')
items.append(f'(text "INCOMPLETE PROCESSOR CAPTURE: all 565 balls present; connections remain open.\\n19 alternate roles and TVSS unresolved. No production footprint assigned.\\nThis standalone draft is not yet connected to appliance power or recovery." (at 25.4 20.32 0) (effects (font (size 1.27 1.27)) (justify left)) (uuid "{uid("note")}"))')
(ROOT / 'processor.kicad_sch').write_text(f'(kicad_sch (version 20250114) (generator eeschema) (uuid "{uid("root")}") (paper "A2") (title_block (title "RK3566 processor — INCOMPLETE") (date "2026-10-04")) (lib_symbols {symbol}) ' + ' '.join(items) + ' (sheet_instances (path "/" (page "1"))))\n')
print('Generated standalone eight-unit processor draft, U801; no circuit connections claimed.')
