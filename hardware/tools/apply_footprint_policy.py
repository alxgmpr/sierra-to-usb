#!/usr/bin/env python3
"""Apply reviewed footprint assignments without regenerating schematic graphics."""
import json
import re
from capture import ROOT, children, quote


def apply():
    policy = json.loads((ROOT / 'footprint-policy.json').read_text())
    assignments = policy['assignments']
    changed = 0
    for path in ROOT.glob('*.kicad_sch'):
        text = path.read_text()
        for symbol in list(children(text)):
            if not re.match(r'^\(symbol\s+\(lib_id\s', symbol):
                continue
            reference = re.search(r'\(property "Reference" "([^"]+)"', symbol)
            if not reference or reference[1] not in assignments:
                continue
            new = re.sub(r'(\(property "Footprint" )"[^"]*"',
                         lambda m: m[1] + '"' + quote(assignments[reference[1]]) + '"', symbol)
            if new != symbol:
                text = text.replace(symbol, new, 1)
                changed += 1
        path.write_text(text)
    print(f'Applied footprint policy to {changed} symbol units; graphics and pins preserved.')


if __name__ == '__main__':
    apply()
