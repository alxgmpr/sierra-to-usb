#!/usr/bin/env python3
"""Quantify the provisional BGA process window without granting assembly release."""
import argparse
import json
import math
from pathlib import Path
from capture import ROOT, children
from check_footprint_reviews import pads, number


def check(root=ROOT):
    policy = json.loads((root / 'footprint-policy.json').read_text())
    result = {}
    for ref in ['U801', 'U901']:
        identity = policy['assignments'][ref].split(':')[1]
        text = (root / 'Appliance.pretty' / (identity + '.kicad_mod')).read_text()
        lands = pads(text)
        assert 'solder_paste_margin_ratio' not in text, 'Extend aperture calculation for ratios'
        settings = {item.split()[0][1:]: item for item in children(text)}
        def margin(pad, name):
            return (number(pad['text'], name) or
                    number(settings.get(name, ''), name) or (0,))[0]
        assert all(p['shape'] == 'circle' and p['size'][0] == p['size'][1] for p in lands)
        copper = {p['size'][0] for p in lands}
        mask = {p['size'][0] + 2 * margin(p, 'solder_mask_margin')
                for p in lands}
        paste = {p['size'][0] + 2 * margin(p, 'solder_paste_margin')
                 for p in lands}
        assert len(copper) == len(mask) == len(paste) == 1
        assert all('"F.Paste"' in p['text'] and '"F.Mask"' in p['text'] for p in lands)
        c, m, p = copper.pop(), mask.pop(), paste.pop()
        distance = min(math.dist(a['at'][:2], b['at'][:2])
                       for i, a in enumerate(lands) for b in lands[i+1:])
        # Circular aperture: area / wall area = diameter / (4 * foil thickness).
        # These are engineering screening thresholds, not vendor acceptance rules.
        max_thickness = min(p / 3, p / (4 * .66))
        assert ref in policy['land_pattern_release_holds'], (ref, 'Process approval still missing')
        result[ref] = {
            'land_count': len(lands), 'copper_diameter_mm': c,
            'mask_opening_mm': round(m, 6), 'paste_opening_mm': round(p, 6),
            'minimum_center_distance_mm': round(distance, 6),
            'minimum_copper_gap_mm': round(distance-c, 6),
            'minimum_mask_web_mm': round(distance-m, 6),
            'radial_mask_clearance_mm': round((m-c)/2, 6),
            'screening_max_foil_thickness_mm': round(max_thickness, 6),
            'area_ratio_at_100um': round(p / .4, 6),
            'aspect_ratio_at_100um': round(p / .1, 6),
            'released': False,
        }
    return {'scope': 'Geometry and circular-aperture screening only; no process approval',
            'screening_criteria': {'minimum_area_ratio': .66, 'minimum_aspect_ratio': 3},
            'required_evidence': ['Manufacturer or assembler-approved copper and mask design',
                                  'Fabricator mask registration and minimum web capability',
                                  'Assembler stencil thickness, aperture, paste and reflow approval',
                                  'Escape/via strategy and assembly inspection acceptance'],
            'packages': result}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(check(), indent=2) + '\n')
    print('PASS: BGA process windows measured; both assembly holds retained.')
