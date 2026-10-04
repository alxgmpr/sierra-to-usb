#!/usr/bin/env python3
"""Prepare an unregistered, partially typed derivative of the native processor model."""
from pathlib import Path
import csv
import re
import collections

root = Path(__file__).resolve().parents[1]
source = (root / 'reference/rk3566-native-candidate.kicad_sym').read_text()
manufacturer = {r['ball']: r['manufacturer_name'] for r in csv.DictReader((root / 'pinmaps/rk3566.csv').open())}
rows = []
alternate_rows = []
pattern = r'\(pin (\w+) (\w+).*?\(name "([^"]+)".*?\(number "([^"]+)"[^\n]*\n      \)'

def transform(match):
    original_type, shape, native_name, ball = match.groups()
    name = manufacturer[ball]
    primary = native_name
    if native_name.startswith('DDR_VDDQ'):
        primary = native_name.replace('DDR_', 'DDRPHY_', 1)
    elif native_name in {'USB_HOST1_DP', 'USB_HOST1_DM'}:
        primary = native_name.replace('USB_HOST1', 'USB3_HOST1')
    pin_type = original_type
    evidence = 'Unresolved: functional and mux-direction review required'
    if re.fullmatch(r'(?:VSS|AVSS|AVSS1)_\d+', name) or name in {'DDR_AVSS', 'PMUPLL_AVSS', 'SYSPLL_AVSS'}:
        pin_type = 'power_in'
        evidence = 'RK3566 Rev 1.2 Table 2-2 ground groups, pages 30-31'
    elif ('VDD' in name or name.startswith('VCCIO') or name in {'PMUIO1', 'PMUIO2', 'OTP_VCC18'}):
        pin_type = 'power_in'
        evidence = 'RK3566 Rev 1.2 supply groups / recommended operating conditions, pages 31-32 and 53-54'
    elif primary.startswith('GPIO'):
        pin_type = 'bidirectional'
        evidence = 'RK3566 Rev 1.2 GPIO pad capabilities / mux table; not a reset-direction claim'
    rows.append({'ball': ball, 'primary_name': primary, 'manufacturer_name': name,
                 'electrical_type': pin_type, 'evidence': evidence})
    desired_shape = 'line' if pin_type in {'power_in', 'bidirectional'} else shape
    result = match.group(0).replace('(pin ' + original_type + ' ' + shape, '(pin ' + pin_type + ' ' + desired_shape, 1)
    result = result.replace('(name "' + native_name + '"', '(name "' + primary + '"', 1)
    if primary.startswith('GPIO'):
        # GPIO mux entries are complete function names; power names can use slash shorthand.
        alternates = list(dict.fromkeys(n for n in name.split('/') if n not in {primary, '-'}))
        for alternate in alternates:
            alternate_rows.append({'ball': ball, 'function': alternate, 'electrical_type': 'unspecified',
                                   'evidence': 'Manufacturer mux identity verified; direction review pending'})
        result = result[:-1] + ''.join(f'(alternate "{n}" unspecified line)' for n in alternates) + ')'
    return result

review = re.sub(pattern, transform, source, flags=re.S)
assert len(rows) == 565 and len({r['ball'] for r in rows}) == 565
assert {r['ball'] for r in rows} == set(manufacturer)
(root / 'reference/rk3566-electrical-review.kicad_sym').write_text(review)
with (root / 'pinmaps/rk3566-electrical-review.csv').open('w') as handle:
    writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator='\n')
    writer.writeheader()
    writer.writerows(rows)
with (root / 'pinmaps/rk3566-mux-review.csv').open('w') as handle:
    writer = csv.DictWriter(handle, fieldnames=['ball', 'function', 'electrical_type', 'evidence'], lineterminator='\n')
    writer.writeheader()
    writer.writerows(alternate_rows)
print('Prepared unregistered native derivative:', dict(collections.Counter(r['electrical_type'] for r in rows)))
print('GPIO alternate functions preserved:', len(alternate_rows))
print('Remaining unspecified pins are explicit; this is not a qualified processor symbol.')
