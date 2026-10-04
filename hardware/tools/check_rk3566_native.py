#!/usr/bin/env python3
"""Audit the unregistered native processor candidate against the extracted ball table."""
from pathlib import Path
import collections
import csv
import re

root = Path(__file__).resolve().parents[1]
source = (root / 'reference/rk3566-native-candidate.kicad_sym').read_text()
pins = re.findall(r'\(pin (\w+) \w+.*?\(name "([^"]+)".*?\(number "([^"]+)"', source, re.S)
manufacturer = {r['ball']: r['manufacturer_name'] for r in csv.DictReader((root / 'pinmaps/rk3566.csv').open())}
assert len(pins) == 565
assert len({number for _, _, number in pins}) == 565
assert {number for _, _, number in pins} == set(manufacturer)
rows = list(csv.DictReader((root / 'pinmaps/rk3566-native-audit.csv').open()))
assert len(rows) == 565
saved = {r['ball']: r for r in rows}
assert len(saved) == 565
for pin_type, name, number in pins:
    expected = manufacturer[number]
    status = ('exact' if name == expected else
              'native_name_is_one_manufacturer_function' if name in expected.split('/') else
              'unresolved_name_difference')
    assert saved[number] == {'ball': number, 'native_name': name,
                             'manufacturer_name': expected, 'native_type': pin_type,
                             'name_status': status}
print('PASS: native candidate has exactly 565 manufacturer ball identifiers.')
print(dict(collections.Counter(r['name_status'] for r in rows)))
print('Candidate only: all electrical types unspecified; no functional or footprint qualification.')
