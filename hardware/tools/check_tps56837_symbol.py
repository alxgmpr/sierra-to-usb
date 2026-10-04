#!/usr/bin/env python3
"""Verify main regulator native pin names/types; footprint intentionally pending."""
from pathlib import Path
import re,csv
root=Path(__file__).resolve().parents[1]
s=(root/'Recovery.kicad_sym').read_text().split('(symbol "TPS56837RPAR"',1)[1]
pins=re.findall(r'\(pin (\w+) line.*?\(name "([^\"]+)".*?\(number "([^\"]+)"',s,re.S)
expected={(r['Electrical type'],r['Name'],r['Pin']) for r in csv.DictReader((root/'pinmaps/tps56837.csv').open())}
assert len(pins)==10 and set(pins)==expected,pins
assert '(property "Footprint" ""' in s
print('PASS TPS56837 ten unique pin names and reviewed electrical types; footprint pending.')
