#!/usr/bin/env python3
"""Read every unique attached STEP model, validate its shapes and record bounds.

Requires CadQuery. This detects missing or invalid assets, not mating clearances
or manufacturer tolerances. Package and orientation review remain separate.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import cadquery as cq
from capture import ROOT, children


def audit(output):
    policy = json.loads((ROOT / 'footprint-policy.json').read_text())
    stock = Path(policy['default_library_root']).parent / '3dmodels'
    models = {}
    for fp in children((ROOT / 'appliance.kicad_pcb').read_text()):
        if not fp.startswith('(footprint '):
            continue
        ref = re.search(r'\(property "Reference" "([^"]+)"', fp)[1]
        for model in re.findall(r'\(model "([^"]+)"', fp):
            path = re.sub(r'\$\{KICAD\d+_3DMODEL_DIR\}', str(stock), model)
            path = Path(path.replace('${KIPRJMOD}', str(ROOT)))
            models.setdefault(path, []).append(ref)
    report = []
    for path, refs in models.items():
        shape = cq.importers.importStep(str(path)).val()
        assert shape.isValid(), (path, refs, 'Invalid STEP geometry')
        bounds = shape.BoundingBox()
        report.append({
            'model': str(path).replace(str(ROOT), '${KIPRJMOD}')
                     .replace(str(stock), '${KICAD10_3DMODEL_DIR}'),
            'references': refs,
            'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
            'valid_STEP_shape': True,
            'bounding_box_mm': {axis + '_' + end: getattr(bounds, axis + end)
                                for axis in 'xyz' for end in ['min', 'max']}
        })
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps({
        'scope': 'STEP parsing, shape validity and bounds; package-envelope identification does not qualify assembly tolerances or mating clearances',
        'models': report
    }, indent=2) + '\n')
    print(f'PASS: {len(models)} unique attached STEP models contain valid shapes.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    audit(parser.parse_args().output)
