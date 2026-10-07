#!/usr/bin/env python3
"""Install the project's official-generator outputs and explicit pin-map corrections.

Input is a staging directory produced by KiCad Library Tools, not the PCB. Review
the outputs before using KiCad's native Update PCB dialog. No routed board edits.
"""
import argparse
import re
import shutil
from pathlib import Path
from capture import ROOT, children


def install(generated):
    library = ROOT / 'Appliance.pretty'
    for name in ['Sierra_RK3566_BGA565', 'Sierra_Micron_ZW_TFBGA200']:
        source = generated / 'Package_BGA.pretty' / (name + '.kicad_mod')
        text = source.read_text().replace(
            '${KICAD10_3DMODEL_DIR}/Package_BGA.3dshapes/',
            '${KIPRJMOD}/Appliance.3dshapes/')
        (library / source.name).write_text(text)
        shutil.copy2(generated / 'Package_BGA.3dshapes' / (name + '.step'),
                     ROOT / 'Appliance.3dshapes' / (name + '.step'))
    for name in ['Sierra_HX4110NL_2x12_P1.27mm',
                 'Sierra_RJE491881401_1x08-1MP_P1.02mm',
                 'Sierra_MDT420B01411_2x38-1MP_P0.5mm']:
        source = generated / 'Connector_Appliance.pretty' / (name + '.kicad_mod')
        result = []
        for item in children(source.read_text()):
            if item.startswith('(model '):
                continue  # No verified connector model is attached.
            if 'RJE49' in name:
                # Mirror pads AND the pin-1 silk/fab markers. The manufacturer's
                # top-view pin sequence is opposite the generic generator's.
                item = re.sub(r'(\((?:at|start|end|mid|center) )(-?[0-9.]+)',
                              lambda m: m[1] + str(-float(m[2])), item)
                if item.startswith('(pad "SH"'):
                    item = re.sub(r'\(drill 1\)', '(drill oval 1 2.6)', item)
            if item.startswith('(pad '):
                match = re.match(r'\(pad "([0-9]+)"', item)
                number = int(match[1]) if match else None
                if 'HX4110' in name and number and number > 12:
                    item = item.replace(f'(pad "{number}"', f'(pad "{37-number}"', 1)
                if 'MDT420' in name and number and number % 2:
                    item = item.replace('(size 0.3 1.55)', '(size 0.3 1.5)')
            result.append(item)
        (library / source.name).write_text(
            '(footprint "' + name + '"\n' + '\n'.join(result) + '\n)\n')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('generated', type=Path)
    install(parser.parse_args().generated)
