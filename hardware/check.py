#!/usr/bin/env python3
"""Native ERC/export plus critical recovery-net checks; outputs stay outside repo."""
import argparse
import csv
import shutil
import subprocess
from pathlib import Path
import xml.etree.ElementTree as ET

p = argparse.ArgumentParser(description=__doc__)
p.add_argument('--output', type=Path, required=True)
p.add_argument('--kicad-cli', default=shutil.which('kicad-cli') or '/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli')
a = p.parse_args()
a.output.mkdir(parents=True, exist_ok=True)
schematic = Path(__file__).resolve().parent / 'recovery.kicad_sch'
def run(*args):
    subprocess.run([a.kicad_cli, *map(str, args)], check=True)
run('version')
run('sch', 'erc', '--severity-all', '--exit-code-violations', '--format', 'json', '--output', a.output / 'erc.json', schematic)
run('sch', 'export', 'netlist', '--format', 'kicadxml', '--output', a.output / 'netlist.xml', schematic)
r = ET.parse(a.output / 'netlist.xml')
nets = {n.get('name'): {(x.get('ref'), x.get('pin')) for x in n.findall('node')} for n in r.findall('.//nets/net')}
def pins(*items):
    return {tuple(item.split(':')) for item in items}
def exact(name, *items):
    assert nets[name] == pins(*items), (name, nets[name], pins(*items))
exact('/Supervisor/MCU_NRST_N', 'U201:10', 'U202:1', 'R201:2', 'C205:1', 'J201:5')
assert not any(c.get('ref') == 'D201' for c in r.findall('.//components/comp'))
exact('/Supervisor/WDT_INPUT', 'U202:4', 'J202:2')
exact('/Supervisor/WDT_KICK', 'U201:19', 'J202:1', 'R202:1')
exact('/Supervisor/MANUAL_RESET_N', 'U202:3', 'R203:2', 'SW201:1')
exact('/Supervisor/SWDIO', 'U201:35', 'J201:2')
exact('/Supervisor/SWCLK', 'U201:36', 'J201:4')
for i, (name, gpio, header) in enumerate([('MODEM_RESET',15,3), ('MODEM_OFF',16,4), ('ETH_RESET',17,5)]):
    q, rb, rpd = 301+i, 301+2*i, 302+2*i
    exact('/'+name+'_ASSERT', f'U201:{gpio}', f'R{rb}:1')
    exact('/'+name+'_N', f'Q{q}:3', f'J102:{header}')
    exact(f'Net-(Q{q}-B)', f'Q{q}:1', f'R{rb}:2', f'R{rpd}:1')
    assert pins(f'Q{q}:2', f'R{rpd}:2') <= nets['GND']
exact('/MODEM_POWER_EN', 'U201:11', 'R307:1', 'J102:1')
exact('/ETH_POWER_EN', 'U201:12', 'R308:1', 'J102:2')
assert pins('U201:4','U201:5','U201:6','U202:5','J101:1','C201:1','C202:1','C203:1','C204:1') <= nets['+3V3']
assert pins('U201:7','U202:2','J101:2','R307:2','R308:2','R202:2') <= nets['GND']
assert not nets['+3V3'] & nets['GND']
run('sch', 'export', 'svg', '--output', a.output / 'svg', schematic)
run('sch', 'export', 'pdf', '--output', a.output / 'recovery.pdf', schematic)
components = r.findall('.//components/comp')
missing_mpn = []
with (a.output / 'bom.csv').open('w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['Reference', 'Value', 'Footprint', 'MPN', 'Manufacturer', 'Required Mating Part'])
    for comp in components:
        fields = {item.get('name'): item.text or '' for item in comp.findall('./fields/field')}
        if not fields.get('MPN'):
            missing_mpn.append(comp.get('ref'))
        writer.writerow([comp.get('ref'), comp.findtext('value'), comp.findtext('footprint'),
                         fields.get('MPN', ''), fields.get('Manufacturer', ''), fields.get('Required Mating Part', '')])
print(f'BOM MPN coverage: {len(components)-len(missing_mpn)}/{len(components)}; missing: {", ".join(missing_mpn)}')
print(f'PASS: native ERC, critical reset/watchdog/SWD/control connectivity; {len(r.findall(".//components/comp"))} components. Not hardware qualification.')
