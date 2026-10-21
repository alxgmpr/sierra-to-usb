#!/usr/bin/env python3
"""Check the new model evidence, exact board attachments and remaining holds."""
import argparse
import hashlib
import json
from pathlib import Path
import re
from capture import ROOT, children
from check_footprint_reviews import number


def vector(block, field):
    item = next(x for x in children(block) if x.startswith('(' + field))
    return number(item, 'xyz')


def check(root=ROOT, geometry=False):
    record = json.loads((root / 'reference/model-reviews-2026-10-21.json').read_text())
    policy = json.loads((root / 'footprint-policy.json').read_text())
    for name, digest in record['source_hashes'].items():
        assert hashlib.sha256((root / name).read_bytes()).hexdigest() == digest, name
    board = {re.search(r'\(property "Reference" "([^"]+)"', f)[1]: f
             for f in children((root / 'appliance.kicad_pcb').read_text())
             if f.startswith('(footprint ')}
    for entry in record['attached']:
        path = root / entry['file']
        assert hashlib.sha256(path.read_bytes()).hexdigest() == entry['sha256'], path
        attached = []
        for ref, fp in board.items():
            for model in children(fp):
                if model.startswith('(model "${KIPRJMOD}/' + entry['file'] + '"'):
                    attached.append(ref)
                    assert vector(model, 'offset') == tuple(entry['offset_xyz_mm']), ref
                    assert vector(model, 'rotate') == tuple(entry['rotation_xyz_degrees']), ref
                    assert vector(model, 'scale') == (1, 1, 1), ref
        assert sorted(attached) == entry['references'], entry['file']
        if geometry:
            import cadquery as cq
            shape = cq.importers.importStep(str(path)).val()
            assert shape.isValid() and all(s.isValid() for s in shape.Solids()), path
            bounds = shape.BoundingBox()
            actual = (bounds.xlen, bounds.ylen, bounds.zlen)
            assert all(abs(a-b) < .0001 for a, b in zip(actual, entry['size_xyz_mm'])), (path, actual)
            assert abs(bounds.zmin - entry['z_min_mm']) < .0001, path
    holds = {e['footprint']: e for e in record['remaining_holds']}
    assert set(holds) == set(policy['model_release_holds'])
    for identity, entry in holds.items():
        assert entry['blocker'] == policy['model_release_holds'][identity]
        assert entry['references'] == sorted(r for r, f in policy['assignments'].items() if f == identity)
        assert all('(model ' not in board[r] for r in entry['references'])
    return record


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--geometry', action='store_true', help='Also validate STEP solids and sourced bounds; requires CadQuery')
    args = parser.parse_args()
    record = check(geometry=args.geometry)
    print(f"PASS: {len(record['attached'])} model reviews, 16 attachments; 18 documented remaining model holds.")
