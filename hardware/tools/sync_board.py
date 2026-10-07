#!/usr/bin/env python3
"""Refresh footprint geometry/fields/nets in the canonical unrouted appliance board.

Existing footprint identities and transforms are preserved. Refuses routed boards:
use KiCad's native update dialog once routing has started.
"""
import argparse
import json
import re
import shutil
import subprocess
import uuid
import xml.etree.ElementTree as ET
from pathlib import Path
from capture import ROOT, children, quote
from check_appliance_capture import CLI


def uid(ref, key):
    return str(uuid.uuid5(uuid.NAMESPACE_URL, 'sierra-board-' + ref + '-' + key))


def tag(item):
    return re.match(r'\(([^\s()]+)', item)[1]


def property_text(ref, name, value):
    return (f'(property "{quote(name)}" "{quote(value)}" (at 0 0 0) '
            f'(layer "F.Fab") (hide yes) (uuid "{uid(ref, name)}") '
            '(effects (font (size 1 1) (thickness 0.15))))')


def synchronize(output):
    output.mkdir(parents=True, exist_ok=True)
    board_path = ROOT / 'appliance.kicad_pcb'
    board = board_path.read_text()
    assert not re.search(r'\((segment|arc|via|zone)\b', board), 'Routed board: use native update.'
    shutil.copy2(board_path, output / 'appliance-before-sync.kicad_pcb')
    subprocess.run([CLI, 'sch', 'export', 'netlist', '--format', 'kicadxml',
                    '--output', str(output / 'appliance.xml'), str(ROOT / 'appliance.kicad_sch')], check=True)
    tree = ET.parse(output / 'appliance.xml').getroot()
    components = {c.get('ref'): c for c in tree.findall('./components/comp')}
    nets = {(n.get('ref'), n.get('pin')): (net.get('name'), n.attrib)
            for net in tree.findall('./nets/net') for n in net.findall('node')}
    policy = json.loads((ROOT / 'footprint-policy.json').read_text())
    existing = {}
    for item in children(board):
        if tag(item) == 'footprint':
            ref = re.search(r'\(property "Reference" "([^"]+)"', item)[1]
            assert ref not in existing, ref
            existing[ref] = item
    assert set(existing) <= set(components), 'PCB-only components need explicit review.'
    footprints = []
    missing = []
    new_count = 0
    for ref, comp in components.items():
        fp = comp.findtext('footprint')
        if not fp:
            missing.append(ref)
            continue
        library, name = fp.split(':')
        base = ROOT if library in ['Appliance', 'Recovery', 'PoE'] else Path(policy['default_library_root'])
        source = (base / (library + '.pretty') / (name + '.kicad_mod')).read_text()
        old = existing.get(ref, '')
        old_items = list(children(old)) if old else []
        transform = next((x for x in old_items if tag(x) == 'transform'), None)
        if transform is None:
            transform = f'(transform (translate {400 + 50 * new_count} 300) (rotate 0) (scale 1 1))'
            new_count += 1
        rotation = policy.get('board_rotation', {}).get(ref)
        if rotation is not None:
            transform = re.sub(r'\(rotate [^()]+\)', f'(rotate {rotation})', transform)
        old_id = next((x for x in old_items if tag(x) == 'uuid'), f'(uuid "{uid(ref, "footprint")}")')
        props = {f.get('name'): f.text or '' for f in comp.findall('./fields/field')
                 if f.get('name') != 'Footprint'}
        props.update(Reference=ref, Value=comp.findtext('value', ''),
                     Datasheet=comp.findtext('datasheet', ''))
        props.setdefault('Description', '')
        output_items = ['(layer "F.Cu")', old_id, transform]
        properties_written = set()
        pad_indices = {}
        for item in children(source):
            kind = tag(item)
            if kind in ['version', 'generator', 'generator_version', 'layer', 'uuid', 'tedit', 'at']:
                continue
            item = re.sub(r'\s*\(uuid "[^"]+"\)', '', item)
            if kind == 'model':
                model = re.match(r'\(model "([^"]+)"', item)[1]
                overrides = policy.get('model_overrides', {})
                if model in overrides:
                    if overrides[model] is None:
                        continue
                    item = item.replace(model, overrides[model])
            if kind == 'property':
                name_match = re.match(r'\(property "([^"]+)"', item)
                if name_match is None:
                    continue
                field = name_match[1]
                if field in ['Reference', 'Value']:
                    item = re.sub(r'^(\(property "[^"]+" )"[^"]*"',
                                  lambda m: m[1] + '"' + quote(props[field]) + '"', item)
                    item = item[:-1] + f' (uuid "{uid(ref, field)}"))'
                    if field == 'Value' and '(hide yes)' not in item:
                        item = item[:-1] + ' (hide yes))'
                    output_items.append(item)
                    properties_written.add(field)
                continue
            if kind == 'attr':
                attrs = item[6:-1].split()
                attrs = [v for v in attrs if v not in ['dnp', 'exclude_from_bom', 'exclude_from_pos_files']]
                if comp.find('property[@name="dnp"]') is not None:
                    attrs.append('dnp')
                if comp.find('property[@name="exclude_from_bom"]') is not None:
                    attrs.append('exclude_from_bom')
                if comp.find('property[@name="exclude_from_pos_files"]') is not None:
                    attrs.append('exclude_from_pos_files')
                item = '(attr ' + ' '.join(attrs) + ')'
            if kind == 'pad':
                number = re.match(r'\(pad (?:"([^"]*)"|([^\s()]+))', item)
                number = number[1] if number[1] is not None else number[2]
                index = pad_indices.get(number, 0)
                pad_indices[number] = index + 1
                item = re.sub(r'\s*\((net|pinfunction|pintype) [^()]*\)', '', item)
                if number:
                    net, attrs = nets[(ref, number)]
                    if net.startswith('unconnected-'):
                        net = net.replace('/', '{slash}')
                    item = item[:-1] + f' (net "{quote(net)}")'
                    for field in ['pinfunction', 'pintype']:
                        if attrs.get(field):
                            item += f' ({field} "{quote(attrs[field])}")'
                    item += ')'
                item = item[:-1] + f' (uuid "{uid(ref, "pad-" + number + "-" + str(index))}"))'
            output_items.append(item)
        for field, value in props.items():
            if field not in properties_written:
                output_items.append(property_text(ref, field, value))
        # KiCad stores these library filters as an unquoted internal property.
        # Dropping them makes an otherwise identical native update propose edits.
        output_items.extend(x for x in old_items if x.startswith('(property ki_fp_filters '))
        for name in ['path', 'sheetname', 'sheetfile', 'units']:
            prior = next((x for x in old_items if tag(x) == name), None)
            if prior:
                output_items.append(prior)
            elif name == 'path':
                stamps = comp.findtext('tstamps').split()
                assert len(stamps) == 1, (
                    ref, 'Add multi-unit symbols through KiCad Update PCB to establish native links.')
                sheet = comp.find('sheetpath').get('tstamps').rstrip('/')
                output_items.append(f'(path "{sheet}/{stamps[0]}")')
        footprints.append('(footprint "' + fp + '"\n' + '\n'.join(output_items) + '\n)')
    other = [x for x in children(board) if tag(x) != 'footprint']
    board_path.write_text('(kicad_pcb\n' + '\n'.join(other + footprints) + '\n)\n')
    print(f'Synchronized {len(footprints)} footprints; unassigned: {missing}')


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output', type=Path, required=True)
    args = p.parse_args()
    synchronize(args.output)
