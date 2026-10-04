#!/usr/bin/env python3
"""Check processor draft against native KiCad netlist, not generator internals."""
from pathlib import Path
import csv
import re
import subprocess
import tempfile
import xml.etree.ElementTree as ET
ROOT = Path(__file__).resolve().parents[1]
CLI = '/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli'
with tempfile.TemporaryDirectory() as directory:
    output = Path(directory) / 'processor.xml'
    subprocess.run([CLI,'sch','export','netlist','--format','kicadxml','--output',str(output),str(ROOT/'processor.kicad_sch')], check=True, capture_output=True)
    netlist = ET.parse(output).getroot()
assert {c.attrib['ref'] for c in netlist.findall('./components/comp')} == {'U801','R801','SW801','SW802'}|{f'C{n}' for n in list(range(801,813))+list(range(815,821))}
expected = {r['ball'] for r in csv.DictReader((ROOT/'pinmaps/rk3566-electrical-review.csv').open()) if re.fullmatch(r'(?:VSS|AVSS|AVSS1)_\d+',r['primary_name']) or r['primary_name'] in {'DDR_AVSS','PMUPLL_AVSS','SYSPLL_AVSS'}}
assert len(expected) == 187 and '1M18' not in expected
nets = netlist.findall('./nets/net')
ground = [n for n in nets if n.attrib['name'] == 'GND']
assert len(ground) == 1
actual = {(n.attrib['ref'],n.attrib['pin']) for n in ground[0].findall('node')}
assert actual == {('U801',ball) for ball in expected}|{(f'C{n}','2') for n in list(range(801,813))+list(range(815,821))}|{('SW801','2'),('SW802','2')}
for name, ball in {'PMIC_I2C_SCL':'AJ37','PMIC_I2C_SDA':'AK38','PMIC_SLEEP':'1P19','RK_RESET_N':'AG38','PMIC_INT_N':'1R19'}.items():
    matches = [n for n in nets if n.attrib['name'] == name]
    assert len(matches) == 1
    assert {(n.attrib['ref'],n.attrib['pin']) for n in matches[0].findall('node')} == ({('U801',ball),('SW802','1')} if name == 'RK_RESET_N' else {('U801',ball)})
for component in netlist.findall('./components/comp'):
    ref = component.attrib['ref']
    if ref.startswith('C'):
        fields = {f.attrib['name']:f.text for f in component.findall('./fields/field')}
        assert fields['MPN'] == ('CL10C102JB8NNNC' if ref == 'C820' else 'CL10B105KA8NNNC' if int(ref[1:]) % 2 and int(ref[1:]) <= 809 else 'CL10B104KA8NNNC')
        assert fields['Voltage Rating'] == ('50V' if ref == 'C820' else '25V')
boot=next(n for n in nets if n.attrib['name']=='SARADC_BOOT_KEY')
assert {(n.attrib['ref'],n.attrib['pin']) for n in boot.findall('node')}=={('U801','1D17'),('R801','2'),('C820','1'),('SW801','1')}
res=next(c for c in netlist.findall('./components/comp') if c.attrib['ref']=='R801')
assert {f.attrib['name']:f.text for f in res.findall('./fields/field')}['MPN']=='RC0603FR-0710KL'
for ref in ['SW801','SW802']:
    button=next(c for c in netlist.findall('./components/comp') if c.attrib['ref']==ref)
    assert {f.attrib['name']:f.text for f in button.findall('./fields/field')}['MPN']=='TL3342F160QG'
    assert button.findtext('footprint')=='Button_Switch_SMD:SW_SPST_TL3342'
all_pins = {p.attrib['num'] for p in netlist.findall("./libparts/libpart[@part='RK3566']/pins/pin")}
assert len(all_pins) == 565
print('PASS: one U801, seventeen local bypass capacitors and one input filter, 565 library pins, exactly 187 documented balls on GND; TVSS excluded; PMIC controls and reset ball assignments verified.')
print('Partial capture only: processor supplies and peripherals remain incomplete.')
