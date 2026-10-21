#!/usr/bin/env python3
"""Check native PCB parity and report the separate physical-layout release gates."""
import argparse
from collections import Counter
import json
from pathlib import Path
import re
import subprocess
import xml.etree.ElementTree as ET
from capture import ROOT, children
from check_appliance_capture import CLI


def audit(output):
    output.mkdir(parents=True, exist_ok=True)
    subprocess.run([CLI, 'pcb', 'drc', '--severity-all', '--schematic-parity',
                    '--format', 'json', '--output', str(output / 'drc.json'),
                    str(ROOT / 'appliance.kicad_pcb')], check=True, capture_output=True)
    drc = json.loads((output / 'drc.json').read_text())
    assert not drc['schematic_parity'], drc['schematic_parity']
    subprocess.run([CLI, 'sch', 'export', 'netlist', '--format', 'kicadxml',
                    '--output', str(output / 'appliance.xml'),
                    str(ROOT / 'appliance.kicad_sch')], check=True, capture_output=True)
    components = {c.get('ref'): c for c in ET.parse(output / 'appliance.xml').getroot()
                  .findall('./components/comp')}
    policy = json.loads((ROOT / 'footprint-policy.json').read_text())
    models_root = Path(policy['default_library_root']).parent / '3dmodels'
    footprints = {}
    modelled = 0
    missing_models = []
    for fp in children((ROOT / 'appliance.kicad_pcb').read_text()):
        if not fp.startswith('(footprint '):
            continue
        ref = re.search(r'\(property "Reference" "([^"]+)"', fp)[1]
        assert ref not in footprints, ref
        identity = re.match(r'\(footprint "([^"]+)"', fp)[1]
        footprints[ref] = identity
        component = components[ref]
        attrs = next((x for x in children(fp) if x.startswith('(attr ')), '')
        flags = attrs[6:-1].split() if attrs else []
        for flag in ['dnp', 'exclude_from_bom', 'exclude_from_pos_files']:
            assert (flag in flags) == (component.find(f'property[@name="{flag}"]') is not None), (ref, flag)
        native_path = re.search(r'\(path "([^"]+)"', fp)[1]
        sheet, stamp = native_path.rsplit('/', 1)
        assert sheet == component.find('sheetpath').get('tstamps').rstrip('/'), (ref, native_path)
        assert stamp in component.findtext('tstamps').split(), (ref, 'Invalid native symbol link', native_path)
        if len(component.findtext('tstamps').split()) > 1:
            assert any(x.startswith('(units') for x in children(fp)), (ref, 'Missing native units')
        models = re.findall(r'\(model "([^"]+)"', fp)
        for model in models:
            path = re.sub(r'\$\{KICAD\d+_3DMODEL_DIR\}', str(models_root), model)
            path = path.replace('${KIPRJMOD}', str(ROOT))
            assert Path(path).is_file(), (ref, 'Missing attached model', model)
        if models:
            modelled += 1
        elif not identity.startswith('TestPoint:'):
            missing_models.append(ref)
            assert identity in policy['model_release_holds'], (ref, 'Undocumented missing model')
    assert footprints == policy['assignments'], 'PCB footprint policy drift'
    counts = Counter(v['type'] for v in drc['violations'])
    for kind in ['shorting_items', 'malformed_courtyard', 'unresolved_variable',
                 'lib_footprint_mismatch', 'solder_mask_bridge']:
        assert not counts[kind], (kind, counts[kind])
    report = {
        'date': '2026-10-21', 'PCB_footprints': len(footprints),
        'schematic_parity_issues': 0,
        'default_library_footprints': sum(not v.startswith(('Appliance:', 'Recovery:', 'PoE:'))
                                          for v in footprints.values()),
        'hand_solder_footprints': sum('handsolder' in v.lower() for v in footprints.values()),
        'components_with_resolved_models': modelled,
        'model_release_hold_components': sorted(missing_models),
        'physical_DRC_violations': dict(sorted(counts.items())),
        'unconnected_items': len(drc['unconnected_items']),
        'manufacturing_ready': not drc['violations'] and not drc['unconnected_items']
                               and not policy['land_pattern_release_holds'],
        'scope': 'Native component, field, attribute and net synchronization. Full DRC is reported without exclusions; zero parity does not establish manufacturing readiness.'
    }
    (output / 'board-sync-report.json').write_text(json.dumps(report, indent=2) + '\n')
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    report = audit(parser.parse_args().output)
    print(f"PASS: {report['PCB_footprints']} footprints, zero native schematic parity issues; all attached model paths resolve.")
    print(f"Layout remains unreleased: {sum(report['physical_DRC_violations'].values())} physical DRC violations, {report['unconnected_items']} unconnected items.")
