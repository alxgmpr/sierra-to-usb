#!/usr/bin/env python3
"""Audit registered PMIC against the saved manufacturer pin-name comparison."""
from pathlib import Path
import csv
import re

ROOT = Path(__file__).resolve().parents[1]
text = (ROOT / 'Recovery.kicad_sym').read_text()
start = text.index('(symbol "RK809-5"')
depth = 0
quoted = False
for end in range(start, len(text)):
    char = text[end]
    if char == '"':
        quoted = not quoted
    if not quoted:
        depth += (char == '(') - (char == ')')
        if depth == 0:
            break
symbol = text[start:end + 1]
pins = re.findall(r'\(pin (\w+) line.*?\(name "([^"]+)".*?\(number "(\d+)"', symbol, re.S)
assert len(pins) == 69
assert {number for _, _, number in pins} == {str(n) for n in range(1, 70)}
assert len(re.findall(r'\(symbol "RK809-5_[1-4]_1"', symbol)) == 4
actual = {number: (name, kind) for kind, name, number in pins}
for row in csv.DictReader((ROOT / 'pinmaps/rk809-cse-audit.csv').open()):
    expected = row['Manufacturer Name']
    if row['Pin'] == '18':
        expected = 'SDO'
    if row['Pin'] == '69':
        expected = 'EPAD'
    assert actual[row['Pin']][0] == expected, (row, actual[row['Pin']])
for number in ['7', '67', '68']:
    assert actual[number][1] == 'open_collector'
assert actual['69'][1] == 'power_in'
assert '(alternate "PDMDATA" input line)' in symbol
assert actual['1'][1] == 'input' and actual['2'][1] == 'bidirectional'
assert {number for number, (_, kind) in actual.items() if kind == 'passive'} == {'36', '37'}
footprint = re.search(r'\(property "Footprint" "([^"]+)"', symbol)[1]
library, name = footprint.split(':')
base = Path('/Applications/KiCad/KiCad.app/Contents/SharedSupport/footprints')
pads = (base / (library + '.pretty') / (name + '.kicad_mod')).read_text()
assert set(re.findall(r'\(pad "(\d+)"', pads)) == set(actual)
print('PASS: 69 unique pins, manufacturer names, 4 units, reset/interrupt/clock types, native alternate, and footprint pad parity. Circuit and assembly not qualified.')
