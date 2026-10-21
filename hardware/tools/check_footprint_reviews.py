#!/usr/bin/env python3
"""Check the six drawing reviews independently of the footprint generators.

Dimensions are in mm, from the archived drawing pages cited in the review.
This verifies the drawing comparison, not an assembler's process approval.
"""
import argparse
from collections import Counter
import csv
import hashlib
import json
from pathlib import Path
import re

from capture import ROOT, children


def number(item, field):
    match = re.search(r'\(' + field + r' ([^()]*)\)', item)
    return tuple(float(v) for v in match[1].split()) if match else ()


def pads(text):
    result = []
    for item in children(text):
        if not item.startswith('(pad '):
            continue
        match = re.match(r'\(pad "([^"]*)" (\S+) (\S+)', item)
        result.append({'pin': match[1], 'kind': match[2], 'shape': match[3],
                       'at': number(item, 'at'), 'size': number(item, 'size'),
                       'text': item})
    return result


def close(actual, expected, tolerance=0.00001):
    assert len(actual) == len(expected) and all(
        abs(a - b) <= tolerance for a, b in zip(actual, expected)), (actual, expected)


def check(root=ROOT):
    policy = json.loads((root / 'footprint-policy.json').read_text())
    report = {}
    data = {}
    for ref in ['U701', 'U801', 'U901', 'T1701', 'J1701', 'J2001']:
        name = policy['assignments'][ref].split(':')[1]
        path = root / 'Appliance.pretty' / (name + '.kicad_mod')
        data[ref] = pads(path.read_text())
        report[ref] = {'footprint': name, 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}

    # TI 4224047/A, board layout p32. Seven 0.60mm lands; three VIN fingers
    # are explicitly 0.56mm long at x=1.42, not 0.60mm at x=1.40.
    expected = {str(i + 1): (-1.4, -.75 + .5 * i, .6, .25) for i in range(4)}
    expected.update({'5': (-.93, 1.4, .25, .6), '6': (.37, .85, .25, 1.7),
                     '7': (.87, 1.4, .25, .6), '9': (-.21, -.65, .4, 2.1),
                     '10': (-.93, -1.4, .25, .6)})
    copper = [p for p in data['U701'] if p['pin']]
    assert len(copper) == 13
    assert Counter(p['pin'] for p in copper) == Counter(list(expected) + ['8'] * 4)
    assert {p['at'][1] for p in copper if p['pin'] == '8' and p['size'] == (.25, .56)} == {-.75, -.25, .25}
    for pad in copper:
        x, y = pad['at'][:2]
        w, h = pad['size']
        if len(pad['at']) == 3 and pad['at'][2] == 90:
            w, h = h, w
        if pad['pin'] == '8':
            if w == .4:
                close((x, y, w, h), (.95, -.65, .4, 2.1))
            else:
                close((x, w, h), (1.42, .56, .25))
                assert y in [-.75, -.25, .25]
        else:
            close((x, y, w, h), expected[pad['pin']])
        close(number(pad['text'], 'solder_mask_margin'), (.07,))
        close(number(pad['text'], 'roundrect_rratio'), (.05 / min(w, h),))
        assert ('"F.Paste"' in pad['text']) == (pad['pin'] not in ['6', '9'])
    apertures = [p for p in data['U701'] if not p['pin']]
    assert len(apertures) == 4
    actual = sorted(tuple(p['at'][:2]) + p['size'] for p in apertures)
    expected_paste = sorted([(.37, .375, .25, .75), (.37, 1.325, .25, .75),
                             (-.21, -1.225, .4, .95), (-.21, -.075, .4, .95)])
    for a, b in zip(actual, expected_paste):
        close(a, b)
    assert all('(layers "F.Paste")' in p['text'] for p in apertures)
    report['U701']['review'] = 'TI copper, NSMD and split 0.1mm-stencil example checked'

    # Rockchip Rev1.2 Fig2-5/6: independent inner/outer coordinate formulae.
    outer = 'A B C D E F G H J K L M N P R T U V W Y AA AB AC AD AE AF AG AH AJ AK AL AM AN AP AR'.split()
    inner = 'A B C D E F G H J K L M N P R T U V'.split()
    rk_ids = {r['ball'] for r in csv.DictReader((root / 'pinmaps/rk3566.csv').open())}
    assert len(data['U801']) == 565 and {p['pin'] for p in data['U801']} == rk_ids
    for pad in data['U801']:
        group, row, col = re.fullmatch(r'(1?)([A-Z]+)(\d+)', pad['pin']).groups()
        rows, cols, pitch = (inner, 20, .65) if group else (outer, 38, .4)
        close(pad['at'][:2], ((int(col) - 1 - (cols - 1) / 2) * pitch,
                              (rows.index(row) - (len(rows) - 1) / 2) * pitch))
        close(pad['size'], (.22, .22))
    report['U801']['review'] = '565 exact ball centers; 0.22mm PCB copper/mask/paste still provisional'

    # Micron RevI Fig5/9, rotated 90 degrees: no hundredth-mm source rounding.
    rows = 'A B C D E F G H J K L M N P R T U V W Y AA AB'.split()
    ram_ids = {r['ball'] for r in csv.DictReader((root / 'reference/micron-ddr-native-pin-inventory.csv').open())}
    assert len(data['U901']) == 200 and {p['pin'] for p in data['U901']} == ram_ids
    for pad in data['U901']:
        row, col = re.fullmatch(r'([A-Z]+)(\d+)', pad['pin']).groups()
        close(pad['at'][:2], ((rows.index(row) - 10.5) * .65, (6.5 - int(col)) * .8))
        close(pad['size'], (.45, .45))
        close(number(pad['text'], 'solder_mask_margin'), (-.025,))
    report['U901']['review'] = '200 exact ball centers; 0.45/0.40mm PCB copper/mask and stencil still provisional'

    # Pulse RevA p3: inch dimensions are controlling, bracketed mm rounded.
    assert len(data['T1701']) == 24
    for pad in data['T1701']:
        n = int(pad['pin'])
        close(pad['at'][:2], (((n - 1) if n <= 12 else (24 - n)) * 1.27 - 6.985,
                              4.51 if n <= 12 else -4.51))
        close(pad['size'], (.75, 1.65))
    report['T1701']['review'] = '24 lands, pitch, row separation and top-view numbering checked'

    # Amphenol RJE49 RevA: dimensions 4.38, 3.27, 5.05 establish row/slot datums.
    assert len(data['J1701']) == 10
    for pad in data['J1701']:
        if pad['pin'] == 'SH':
            assert abs(pad['at'][0]) == 7.95 and pad['at'][1] == 5.05
            assert '(drill oval 1 2.6)' in pad['text']
        else:
            n = int(pad['pin'])
            close(pad['at'][:2], (3.57 - (n - 1) * 1.02, 1.78 if n % 2 else 0))
            close(number(pad['text'], 'drill'), (.9,))
    report['J1701']['review'] = '8 signal drills and 2 shell slots match drawing top view'

    # CMDT420X0X411 RevA p2, recommended PCB, origin midpoint of locating holes.
    electrical = [p for p in data['J2001'] if p['pin']]
    assert len(electrical) == 67
    assert {int(p['pin']) for p in electrical} == set(range(1, 76)) - set(range(12, 20))
    for pad in electrical:
        n = int(pad['pin'])
        close(pad['at'][:2], (-9.25 + (n - 1) * .25, -5.25 if n % 2 else 2.275))
        close(pad['size'], (.3, 1.5 if n % 2 else 1.55))
    mechanical = sorted((p['at'][:2], p['size'], p['kind']) for p in data['J2001'] if not p['pin'])
    assert mechanical == [((-10.35, -4.9), (1.2, 2.75), 'smd'),
                          ((-10., 0.), (1.1, 1.1), 'np_thru_hole'),
                          ((10., 0.), (1.6, 1.6), 'np_thru_hole'),
                          ((10.35, -4.9), (1.2, 2.75), 'smd')]
    report['J2001']['review'] = '67 contacts, B-key gap, retention lands and asymmetric NPTHs checked; model remains detached'
    assert policy['land_pattern_release_holds'] == ['U801', 'U901']
    record = json.loads((root / 'reference/footprint-reviews-2026-10-21.json').read_text())
    assert set(record['reviews']) == set(report)
    for ref, item in report.items():
        assert record['reviews'][ref]['sha256'] == item['sha256'], (ref, 'Review evidence is stale')
        assert record['reviews'][ref]['land_pattern_released'] == (ref not in policy['land_pattern_release_holds'])
    for name, source in record['sources'].items():
        assert hashlib.sha256((root / 'reference' / name).read_bytes()).hexdigest() == source['sha256'], name
    return {'scope': 'Drawing geometry review; not manufacturing or physical qualification',
            'reviews': report, 'land_pattern_release_holds': policy['land_pattern_release_holds']}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    result = check()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + '\n')
    print('PASS: six drawing comparisons; two BGA land-pattern/process holds remain.')
