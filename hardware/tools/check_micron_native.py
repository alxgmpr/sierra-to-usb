#!/usr/bin/env python3
"""Check native RAM model consistency; does not certify manufacturer pin mapping."""
from pathlib import Path
import csv, re
root = Path(__file__).resolve().parents[1]
symbol = (root/'reference/micron-ddr-native-candidate.kicad_sym').read_text()
footprint = (root/'reference/micron-ddr-native-candidate.kicad_mod').read_text()
pins = re.findall(r'\(pin (\w+) \w+.*?\(name "([^"]+)".*?\(number "([^"]+)"', symbol, re.S)
pads = re.findall(r'\(pad (\S+) smd', footprint)
assert len(pins) == len(pads) == 200
assert len({p[2] for p in pins}) == len(set(pads)) == 200
assert {p[2] for p in pins} == set(pads)
rows = list(csv.DictReader((root/'reference/micron-ddr-native-pin-inventory.csv').open()))
assert len(rows) == 200
assert {(r['native_type'], r['native_name'], r['ball']) for r in rows} == set(pins)
assert all(t == 'unspecified' for t, _, _ in pins)
print('PASS: 200 unique symbol pins and footprint pads; inventory matches conversion.')
print('Unregistered candidate only: manufacturer mapping, electrical types and land pattern unqualified.')
