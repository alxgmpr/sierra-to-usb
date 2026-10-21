#!/usr/bin/env python3
"""Enforce exact-module documentation gates alongside electrical stuffing checks."""
import argparse
import json
from pathlib import Path

from capture import ROOT


def check(root=ROOT):
    review = json.loads((root / 'reference/modem-documentation-review.json').read_text())
    profiles = json.loads((root / 'reference/modem-assembly-profiles.json').read_text())
    expected = {'EM9190', 'EM9293', 'RM520N-GL', 'RM551E-GL'}
    assert {p['model'] for p in profiles} == expected and len(profiles) == 4
    assert set(review['models']) == expected
    for profile in profiles:
        evidence = review['models'][profile['model']]
        assert profile['documentation_review'] == 'modem-documentation-review.json'
        assert evidence['hardware_guide']['status'] in ['login_required', 'not_located']
        # No reviewed current production pin/timing comparison or measured tuple exists.
        assert not evidence['current_guide_reviewed']
        assert evidence['exact_order_code'] is None
        assert evidence['hardware_revision'] is None
        assert evidence['bench_evidence'] is None
        assert not profile['released'], (profile['model'], 'Unqualified profile released')
        if profile['vendor'] == 'Quectel':
            assert set(profile['VCC_contacts']) == {'2', '4', '70', '72', '74'}
            assert profile['populate_optional'] == []
        else:
            assert set(profile['VCC_contacts']) == {'2', '4', '24', '38', '68', '70', '72', '74'}
    excluded = review['models']['RM520N-GL']['excluded_order_codes']
    assert 'RM520NGLAP-M20-HP' in excluded
    assert all(review['required_tuple_fields'].count(name) == 1 for name in [
        'order_code', 'hardware_revision', 'firmware', 'carrier_PRI', 'SIM_APN',
        'USB_VID_PID_composition', 'host_kernel_driver', 'image_hash', 'bench_results'])
    return {'reviewed': review['reviewed'], 'profiles': sorted(expected),
            'released': 0, 'current_production_guides_reviewed': 0,
            'scope': 'Documentation access and exact-SKU release gates; not module support proof'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    result = check()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + '\n')
    print('PASS: four exact-module documentation gates; no profiles released.')
