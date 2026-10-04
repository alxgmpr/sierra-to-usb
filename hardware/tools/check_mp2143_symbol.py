#!/usr/bin/env python3
"""Check native MP2143 pin fidelity and footprint pad parity."""
from pathlib import Path
import csv,re
root=Path(__file__).resolve().parents[1]
s=(root/'Recovery.kicad_sym').read_text().split('(symbol "MP2143DJ-LF-Z"',1)[1].split('(symbol "TPS56837RPAR"',1)[0]
pins=re.findall(r'\(pin (\w+) line.*?\(name "([^\"]+)".*?\(number "([^\"]+)"',s,re.S)
expected={(r['Electrical type'],r['Name'],r['Pin']) for r in csv.DictReader((root/'pinmaps/mp2143.csv').open())}
assert len(pins)==8 and set(pins)==expected,pins
fp=Path('/Applications/KiCad/KiCad.app/Contents/SharedSupport/footprints/Package_TO_SOT_SMD.pretty/TSOT-23-8.kicad_mod').read_text()
assert set(re.findall(r'\(pad "([^\"]+)"',fp))=={str(i) for i in range(1,9)}
print('PASS: MP2143 eight unique pin names/types and footprint pad numbers; dimensional qualification separate.')
