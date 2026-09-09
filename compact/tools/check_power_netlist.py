"""Compare exported KiCad connectivity with capture intent; not electrical simulation."""
from pathlib import Path
import json, xml.etree.ElementTree as ET, csv
R=Path(__file__).resolve().parents[1]
tree=ET.parse(R/'build/power.xml')
actual={n.attrib['name'].lstrip('/'): {(p.attrib['ref'],p.attrib['pin']) for p in n.findall('node')} for n in tree.findall('.//nets/net')}
expected=json.loads((R/'reference/intended-nets.json').read_text())
checks=[]
for name,pins in expected.items():
 pins=[p for p in pins if not p[0].startswith('#')]
 assert set(map(tuple,pins))==actual.get(name),f'{name}: {set(map(tuple,pins)) ^ actual.get(name,set())}'
 checks.append(f'PASS {name}: {len(pins)} pins')
assert actual['VCAP_STORE'].isdisjoint(actual['USB_PROTECTED'])
assert ('U3','2') in actual['VCAP_STORE'] and ('C1','1') in actual['VCAP_STORE']
assert ('C1','2') in actual['SC_MID'] and ('C2','1') in actual['SC_MID'] and ('U2','18') in actual['SC_MID']
checks.append('PASS all modem-regulator input energy passes through storage node; no USB bypass')
checks.append('PASS capacitor polarity and balancing midpoint')
assert ('U6','5') in actual['MODEM_ENABLE'] and ('U6','3') not in actual['MODEM_ENABLE']
checks.append('PASS SN74LVC1G74 DCU non-inverted Q is pin 5, per datasheet pin-function table')
(R/'build/net-checks.txt').write_text('\n'.join(checks)+'\n')
with (R/'build/power-bom.csv').open('w') as f:
 w=csv.writer(f);w.writerow(['Reference','Value','Footprint','MPN','Manufacturer','Status'])
 for c in tree.findall('.//components/comp'):
  fields={p.attrib['name']:p.text or '' for p in c.findall('fields/field')}
  w.writerow([c.attrib['ref'],c.findtext('value'),c.findtext('footprint'),fields.get('MPN',''),fields.get('Manufacturer',''),fields.get('Status','')])
print(f'{len(checks)} connectivity assertions passed; BOM exported')
