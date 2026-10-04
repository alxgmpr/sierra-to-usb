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
assert {c.attrib['ref'] for c in netlist.findall('./components/comp')} == {'U801','R801','SW801','SW802','Q801','R802','R803','Q802','R804','R805'}|{f'C{n}' for n in list(range(801,813))+list(range(815,825))}
expected = {r['ball'] for r in csv.DictReader((ROOT/'pinmaps/rk3566-electrical-review.csv').open()) if re.fullmatch(r'(?:VSS|AVSS|AVSS1)_\d+',r['primary_name']) or r['primary_name'] in {'DDR_AVSS','PMUPLL_AVSS','SYSPLL_AVSS'}}
assert len(expected) == 187 and '1M18' not in expected
nets = netlist.findall('./nets/net')
ground = [n for n in nets if n.attrib['name'] == 'GND']
assert len(ground) == 1
actual = {(n.attrib['ref'],n.attrib['pin']) for n in ground[0].findall('node')}
assert actual == {('U801',ball) for ball in expected}|{(f'C{n}','2') for n in list(range(801,813))+list(range(815,825))}|{('SW801','2'),('SW802','2'),('Q801','2'),('R803','2'),('Q802','2'),('R805','2')}
for name, ball in {'PMIC_I2C_SCL':'AJ37','PMIC_I2C_SDA':'AK38','PMIC_SLEEP':'1P19','RK_RESET_N':'AG38','PMIC_INT_N':'1R19','DDR_SOC_RZQ':'1F3'}.items():
    matches = [n for n in nets if n.attrib['name'] == name]
    assert len(matches) == 1
    assert {(n.attrib['ref'],n.attrib['pin']) for n in matches[0].findall('node')} == ({('U801',ball),('SW802','1'),('Q801','3')} if name == 'RK_RESET_N' else {('U801',ball)})
for component in netlist.findall('./components/comp'):
    ref = component.attrib['ref']
    if ref.startswith('C'):
        fields = {f.attrib['name']:f.text for f in component.findall('./fields/field')}
        assert fields['MPN'] == ('CL32B226KAJNNNE' if ref in {'C822','C824'} else 'CL31B106KAHNNNE' if ref == 'C823' else 'CL10C102JB8NNNC' if ref == 'C820' else 'CL10B105KA8NNNC' if int(ref[1:]) % 2 and int(ref[1:]) <= 809 else 'CL10B104KA8NNNC')
        assert fields['Voltage Rating'] == ('50V' if ref == 'C820' else '25V')
boot=next(n for n in nets if n.attrib['name']=='SARADC_BOOT_KEY')
assert {(n.attrib['ref'],n.attrib['pin']) for n in boot.findall('node')}=={('U801','1D17'),('R801','2'),('C820','1'),('SW801','1'),('Q802','3')}
res=next(c for c in netlist.findall('./components/comp') if c.attrib['ref']=='R801')
assert {f.attrib['name']:f.text for f in res.findall('./fields/field')}['MPN']=='RC0603FR-0710KL'
for ref in ['SW801','SW802']:
    button=next(c for c in netlist.findall('./components/comp') if c.attrib['ref']==ref)
    assert {f.attrib['name']:f.text for f in button.findall('./fields/field')}['MPN']=='TL3342F160QG'
    assert button.findtext('footprint')=='Button_Switch_SMD:SW_SPST_TL3342'
parts={c.attrib['ref']:c for c in netlist.findall('./components/comp')}
for ref,mpn in {'Q801':'MMBT3904,215','R802':'RC0603FR-0710KL','R803':'RC0603FR-07100KL','Q802':'MMBT3904,215','R804':'RC0603FR-0710KL','R805':'RC0603FR-07100KL'}.items():
    assert {f.attrib['name']:f.text for f in parts[ref].findall('./fields/field')}['MPN']==mpn
base=next(n for n in nets if any(v.attrib['ref']=='Q801' and v.attrib['pin']=='1' for v in n.findall('node')))
assert {(v.attrib['ref'],v.attrib['pin']) for v in base.findall('node')}=={('Q801','1'),('R802','2'),('R803','1')}
recovery_base=next(n for n in nets if any(v.attrib['ref']=='Q802' and v.attrib['pin']=='1' for v in n.findall('node')))
assert {(v.attrib['ref'],v.attrib['pin']) for v in recovery_base.findall('node')}=={('Q802','1'),('R804','2'),('R805','1')}
identities=re.findall(r'\(uuid "([^\"]+)"\)',(ROOT/'processor.kicad_sch').read_text())
assert len(identities)==len(set(identities)), 'Duplicate schematic identity'
npu=next(n for n in nets if n.attrib['name']=='VDD_NPU')
assert {(n.attrib['ref'],n.attrib['pin']) for n in npu.findall('node')}=={('U801',b) for b in ['1G15','1H14','1H15','1J14','1J15']}|{(f'C{n}','1') for n in range(821,825)}
for ref,footprint in {'C821':'Capacitor_SMD:C_0603_1608Metric','C822':'Capacitor_SMD:C_1210_3225Metric','C823':'Capacitor_SMD:C_1206_3216Metric','C824':'Capacitor_SMD:C_1210_3225Metric'}.items():
    assert parts[ref].findtext('footprint')==footprint
all_pins = {p.attrib['num'] for p in netlist.findall("./libparts/libpart[@part='RK3566']/pins/pin")}
assert len(all_pins) == 565
print('PASS: one U801, twenty-one local bypass capacitors and one input filter, 565 library pins, exactly 187 documented balls on GND; TVSS excluded; PMIC controls and reset ball assignments verified.')
print('Partial capture only: processor supplies and peripherals remain incomplete.')

# Single-rank LPDDR4X: rank-1 and ODT control outputs are unused.
unused={'1H3','1A2','1A4','1A5','1C2','1C3','A3','A10','E2'}
for ball in unused:
    assert not any(len(n.findall('node'))>1 and any(v.get('ref')=='U801' and v.get('pin')==ball for v in n.findall('node')) for n in nets),ball
text=(ROOT/'processor.kicad_sch').read_text()
markers={(round(float(x),4),round(float(y),4)) for x,y in re.findall(r'\(no_connect \(at ([\d.-]+) ([\d.-]+)\)',text)}
model=(ROOT/'reference/rk3566-electrical-review.kicad_sym').read_text()
expected_markers={(round(279.4+float(x),4),round(139.7-float(y),4)) for x,y,ball in re.findall(r'\(pin \w+ \w+.*?\(at ([\d.-]+) ([\d.-]+) [\d.-]+\).*?\(number "([^"]+)"',model,re.S) if ball in unused}
assert len(expected_markers)==9 and markers==expected_markers
print('PASS: nine unused DDR outputs explicitly no-connect for single-rank LPDDR4X.')
