#!/usr/bin/env python3
"""Capture all native RK3566 units as an explicitly incomplete standalone draft."""
from pathlib import Path
import re
import uuid
ROOT = Path(__file__).resolve().parents[1]
def uid(key):
    return str(uuid.uuid5(uuid.NAMESPACE_URL, 'sierra-processor-' + key))
def block(text, start):
    depth = 0
    quoted = escape = False
    for i in range(start, len(text)):
        c = text[i]
        if escape:
            escape = False
            continue
        if quoted and c == '\\':
            escape = True
            continue
        if c == '"':
            quoted = not quoted
        if not quoted:
            depth += (c == '(') - (c == ')')
            if depth == 0:
                return text[start:i+1]
    raise ValueError('Unbalanced expression')
def prop(name, value, x, y, hidden=False):
    return f'(property "{name}" "{value}" (at {x} {y} 0) (effects (font (size 1.27 1.27))' + (' (hide yes)' if hidden else '') + '))'
source = (ROOT / 'reference/rk3566-electrical-review.kicad_sym').read_text()
symbol = block(source, source.index('(symbol "RK3566"')).replace('(symbol "RK3566"', '(symbol "ProcessorDraft:RK3566"', 1)
# No production footprint assignment until land-pattern review is complete.
symbol = re.sub(r'("Footprint"\s+)"[^"]*"', r'\1""', symbol, count=1)
(ROOT / 'ProcessorDraft.kicad_sym').write_text('(kicad_symbol_lib (version 20211014) (generator eeschema) ' + symbol.replace('(symbol "ProcessorDraft:RK3566"','(symbol "RK3566"',1) + ')\n')
items = []
ground_balls = set()
control_nets = {'AJ37':'PMIC_I2C_SCL','AK38':'PMIC_I2C_SDA','1P19':'PMIC_SLEEP','AG38':'RK_RESET_N','1R19':'PMIC_INT_N','1D17':'SARADC_BOOT_KEY'}
connected_controls = set()
rail_balls = {}
for unit, x, y in [(1,76.2,76.2),(2,177.8,177.8),(3,279.4,139.7),(4,431.8,76.2),(5,76.2,304.8),(6,279.4,304.8),(7,444.5,228.6),(8,444.5,330.2)]:
    body = block(symbol, symbol.index(f'(symbol "RK3566_{unit}_1"'))
    top = float(re.search(r'\(start [-\d.]+ ([-\d.]+)\)', body)[1])
    pins = re.findall(r'\(number "([^"]+)"', body)
    for px, py, angle, name, number in re.findall(r'\(pin \w+ \w+.*?\(at ([-\d.]+) ([-\d.]+) ([-\d.]+)\).*?\(name "([^"]+)".*?\(number "([^"]+)"', body, re.S):
        analog = {'OTP_VCC18':'VCCA_1V8','SARADC_AVDD_1V8':'VCCA_1V8','USB_AVDD1_0V9':'USB_AVDD_0V9','USB_AVDD1_1V8':'USB_AVDD_1V8','USB_AVDD1_3V3':'3V3_MAIN','PMU_VDD_LOGIC_0V9':'VDDA0V9_PMU','PMUPLL_AVDD_0V9':'VDDA0V9_PMU','PMUPLL_AVDD_1V8':'VCCA1V8_PMU','SYSPLL_AVDD_0V9':'VDDA_0V9','SYSPLL_AVDD_1V8':'VCCA_1V8'}
        rail = analog.get(name) or ('VDD_LOGIC' if name.startswith('VDD_LOGIC_') else 'VDD_GPU' if name.startswith('VDD_GPU_') else 'VCC3V3_PMU' if name in {'PMUIO1','PMUIO2'} else None)
        if rail:
            rail_balls[number] = rail
        control = control_nets.get(number) or rail
        if control:
            if number in control_nets:
                connected_controls.add(number)
            ax, ay = round(x + float(px),4), round(y - float(py),4)
            left = float(px) < 0
            bx = round(ax + (-12.7 if left else 12.7),4)
            items.append(f'(wire (pts (xy {ax} {ay}) (xy {bx} {ay})) (stroke (width 0) (type default)) (uuid "{uid("control-wire-"+number)}"))')
            items.append(f'(global_label "{control}" (shape passive) (at {bx} {ay} {0 if left else 180}) (effects (font (size 1.27 1.27)) (justify {"right" if left else "left"})) (uuid "{uid("control-label-"+number)}"))')
        if not (re.fullmatch(r'(?:VSS|AVSS|AVSS1)_\d+', name) or name in {'DDR_AVSS','PMUPLL_AVSS','SYSPLL_AVSS'}):
            continue
        ground_balls.add(number)
        ax, ay = round(x + float(px),4), round(y - float(py),4)
        left = float(px) < 0
        bx = round(ax + (-7.62 if left else 7.62),4)
        items.append(f'(wire (pts (xy {ax} {ay}) (xy {bx} {ay})) (stroke (width 0) (type default)) (uuid "{uid("ground-wire-"+number)}"))')
        items.append(f'(global_label "GND" (shape passive) (at {bx} {ay} {0 if left else 180}) (effects (font (size 1.27 1.27)) (justify {"right" if left else "left"})) (uuid "{uid("ground-label-"+number)}"))')
    fields = prop('Reference','U801',x,y-top-7.62) + prop('Value','RK3566',x,y-top-5.08)
    for key,value in {'Footprint':'','MPN':'RK3566','Manufacturer':'Rockchip','LCSC':'C2943786','Qualification':'DRAFT: supplies, peripherals, TVSS and land pattern unresolved'}.items():
        fields += prop(key,value,x,y,True)
    items.append(f'(symbol (lib_id "ProcessorDraft:RK3566") (at {x} {y} 0) (unit {unit}) (in_bom yes) (on_board yes) (dnp no) (uuid "{uid(str(unit))}") {fields} ' + ''.join(f'(pin "{n}" (uuid "{uid("pin-"+n)}"))' for n in pins) + f' (instances (project "processor" (path "/{uid("root")}" (reference "U801") (unit {unit})))))')
# Four processor-local PLL banks; distinct from PMIC output capacitance.
cap_source = Path('/Applications/KiCad/KiCad.app/Contents/SharedSupport/symbols/Device.kicad_sym').read_text()
cap = block(cap_source, cap_source.index('(symbol "C_Small"')).replace('(symbol "C_Small"','(symbol "Device:C_Small"',1)
def wire(a,b,key):
    items.append(f'(wire (pts (xy {a[0]} {a[1]}) (xy {b[0]} {b[1]})) (stroke (width 0) (type default)) (uuid "{uid(key)}"))')
def label(net,x,y,key):
    items.append(f'(global_label "{net}" (shape passive) (at {x} {y} 0) (effects (font (size 1.27 1.27)) (justify right)) (uuid "{uid(key)}"))')
for bank,net,x,y in [(0,'VDDA0V9_PMU',50.8,152.4),(1,'VCCA1V8_PMU',50.8,213.36),(2,'VDDA_0V9',304.8,223.52),(3,'VCCA_1V8',406.4,147.32),(4,'VDDA0V9_PMU',50.8,370.84),(5,'VCC3V3_PMU',304.8,375.92),(6,'USB_AVDD_0V9',355.6,284.48),(7,'USB_AVDD_1V8',406.4,284.48),(8,'3V3_MAIN',482.6,284.48),(9,'VCCA_1V8',381,375.92),(10,'VCCA_1V8',431.8,375.92)]:
    offsets = [(0,'1uF','CL10B105KA8NNNC','C29936'),(1,'100nF','CL10B104KA8NNNC','C1590')]
    if bank >= 6:
        offsets = [(0,'100nF','CL10B104KA8NNNC','C1590')]
    for offset,value,mpn,lcsc in offsets:
        if bank == 5:
            value,mpn,lcsc = '100nF','CL10B104KA8NNNC','C1590'
        placement = ('PMU logic bypass at 1N16' if bank == 4 else ('PMUIO1 bypass at 1P16' if offset == 0 else 'PMUIO2 bypass at 1N15') if bank == 5 else 'PLL local bypass per RK3566 guide Figures 2-17/18; place at corresponding supply ball')
        if 6 <= bank <= 8:
            placement = 'USB OTG0/HOST1 local bypass at ' + {6:'1J17',7:'1H16',8:'1H18'}[bank] + '; NanoPi R3S sheet 9'
        if bank >= 9:
            placement = ('SARADC bypass at 1D16' if bank == 9 else 'OTP bypass at 1D15') + '; RK3566 guide Figure 2-49; place close to ball'
        ref = f'C{815+bank-6}' if bank >= 6 else f'C{801+2*bank+offset}'
        cx = x+30.48*offset
        fields = prop('Reference',ref,cx+6.35,y-1.27)+prop('Value',value,cx+6.35,y+1.27)
        for key,val in {'Footprint':'Capacitor_SMD:C_0603_1608Metric','MPN':mpn,'Manufacturer':'Samsung Electro-Mechanics','LCSC':lcsc,'Voltage Rating':'25V','Qualification':placement}.items():
            fields += prop(key,val,cx,y,True)
        items.append(f'(symbol (lib_id "Device:C_Small") (at {cx} {y} 0) (unit 1) (in_bom yes) (on_board yes) (dnp no) (uuid "{uid(ref)}") {fields} '+''.join(f'(pin "{n}" (uuid "{uid(ref+":"+n)}"))' for n in ['1','2'])+f' (instances (project "processor" (path "/{uid("root")}" (reference "{ref}") (unit 1)))))')
        wire((cx,y-2.54),(cx,y-10.16),ref+'-top')
        wire((cx,y+2.54),(cx,y+10.16),ref+'-bottom')
    if bank < 6:
        wire((x,y-10.16),(x+30.48,y-10.16),net+str(bank)+'-top')
        wire((x,y+10.16),(x+30.48,y+10.16),net+str(bank)+'-bottom')
    label(net,x,y-10.16,net+str(bank)+'-label')
    label('GND',x,y+10.16,net+str(bank)+'-ground')
# Defined normal-boot level and local SARADC VIN0 input filter.
resistor = block(cap_source, cap_source.index('(symbol "R_Small_US"')).replace('(symbol "R_Small_US"','(symbol "Device:R_Small_US"',1)
for name,ref,value,x,y,fp,fields in [
 ('R_Small_US','R801','10kR',350.52,320.04,'Resistor_SMD:R_0603_1608Metric',{'MPN':'RC0603FR-0710KL','Manufacturer':'Yageo','LCSC':'C98220','Tolerance':'1%','Power Rating':'0.1W'}),
 ('C_Small','C820','1nF',350.52,345.44,'Capacitor_SMD:C_0603_1608Metric',{'MPN':'CL10C102JB8NNNC','Manufacturer':'Samsung Electro-Mechanics','LCSC':'C163508','Tolerance':'5%','Voltage Rating':'50V','Dielectric':'C0G'})]:
 fields.update({'Footprint':fp,'Qualification':'SARADC VIN0 normal-boot pull-up and input filter; RK3566 guide Figure 2-49'})
 properties=prop('Reference',ref,x+7.62,y-1.27)+prop('Value',value,x+7.62,y+1.27)
 for key,val in fields.items():properties+=prop(key,val,x,y,True)
 items.append(f'(symbol (lib_id "Device:{name}") (at {x} {y} 0) (unit 1) (in_bom yes) (on_board yes) (dnp no) (uuid "{uid(ref)}") {properties} '+''.join(f'(pin "{n}" (uuid "{uid(ref+":"+n)}"))' for n in ['1','2'])+f' (instances (project "processor" (path "/{uid("root")}" (reference "{ref}") (unit 1)))))')
wire((350.52,317.5),(350.52,309.88),'boot-pullup-top')
label('VCCA_1V8',350.52,309.88,'boot-pullup-supply')
wire((350.52,322.58),(350.52,332.74),'boot-pullup-bottom')
wire((350.52,332.74),(350.52,342.9),'boot-filter-top')
wire((350.52,332.74),(365.76,332.74),'boot-node-label-wire')
items.append(f'(global_label "SARADC_BOOT_KEY" (shape passive) (at 365.76 332.74 180) (effects (font (size 1.27 1.27)) (justify left)) (uuid "{uid("boot-node-label")}"))')
items.append(f'(junction (at 350.52 332.74) (diameter 0) (color 0 0 0 0) (uuid "{uid("boot-node-junction")}"))')
wire((350.52,347.98),(350.52,355.6),'boot-filter-ground')
label('GND',350.52,355.6,'boot-filter-ground-label')
items.append(f'(text "INCOMPLETE PROCESSOR CAPTURE: all 565 balls present; documented grounds, logic/GPU and PMU supplies connected; circuitry incomplete.\\nPMIC controls: AJ37=I2C0 SCL, AK38=I2C0 SDA, 1P19=PMIC_SLEEP.\\n19 alternate roles and TVSS unresolved. No production footprint assigned.\\nIntegrated draft: CPU, DDR, analog/IO supplies and peripheral circuitry remain open." (at 25.4 20.32 0) (effects (font (size 1.27 1.27)) (justify left)) (uuid "{uid("note")}"))')
(ROOT / 'processor.kicad_sch').write_text(f'(kicad_sch (version 20250114) (generator eeschema) (uuid "{uid("root")}") (paper "A2") (title_block (title "RK3566 processor — INCOMPLETE") (date "2026-10-04")) (lib_symbols {symbol} {cap} {resistor}) ' + ' '.join(items) + ' (sheet_instances (path "/" (page "1"))))\n')
assert len(rail_balls) == 26
assert connected_controls == set(control_nets)
assert len(ground_balls) == 187 and '1M18' not in ground_balls
print('Generated standalone eight-unit processor draft, U801; 187 documented ground balls connected.')
