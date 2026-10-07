#!/usr/bin/env python3
"""Check existing EasyEDA candidate coordinates; does not generate a footprint."""
from pathlib import Path
import csv
import re

root = Path(__file__).resolve().parents[1]
source = (root / 'reference/rk3566-native-candidate.kicad_mod').read_text()
pads = re.findall(r'\(pad (\S+) smd circle \(at ([-\d.]+) ([-\d.]+).*?\(size ([\d.]+) ([\d.]+)\)', source)
balls = {r['ball'] for r in csv.DictReader((root / 'pinmaps/rk3566.csv').open())}
assert len(pads) == len({p[0] for p in pads}) == 565
assert {p[0] for p in pads} == balls
inner_rows = 'A B C D E F G H J K L M N P R T U V'.split()
outer_rows = 'A B C D E F G H J K L M N P R T U V W Y AA AB AC AD AE AF AG AH AJ AK AL AM AN AP AR'.split()
counts = {True: 0, False: 0}
for number, x, y, width, height in pads:
    inner, row, column = re.fullmatch(r'(1?)([A-Z]+)(\d+)', number).groups()
    inner = bool(inner)
    rows = inner_rows if inner else outer_rows
    columns, pitch = (20, 0.65) if inner else (38, 0.4)
    expected_x = (int(column) - 1 - (columns - 1) / 2) * pitch
    expected_y = (rows.index(row) - (len(rows) - 1) / 2) * pitch
    # EasyEDA export rounds to hundredths and has a 0.005 mm inner-array offset.
    assert abs(float(x) - expected_x) <= 0.011, (number, x, expected_x)
    assert abs(float(y) - expected_y) <= 0.011, (number, y, expected_y)
    assert float(width) == float(height) == 0.22
    counts[inner] += 1
assert counts == {True: 343, False: 222}
print('PASS: 565 exact ball identifiers; 343 inner 0.65 mm and 222 outer 0.4 mm coordinates.')
print('Top-view orientation matches Rev 1.2 Fig 2-6; outer extent matches Fig 2-5 D1/E1.')
print('Not land-pattern qualification: 0.22 mm lands, mask/paste, fab/courtyard and 3D remain unapproved.')
