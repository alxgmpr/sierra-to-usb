#!/usr/bin/env python3
"""Generate DDR supply and processor calibration draft from standard symbols."""
from pathlib import Path
import re
import uuid
ROOT=Path(__file__).resolve().parents[1]
LIB=Path('/Applications/KiCad/KiCad.app/Contents/SharedSupport/symbols')
def uid(key):return str(uuid.uuid5(uuid.NAMESPACE_URL,'sierra-ddr-power-'+key))
def block(text,start):
 depth=0;quoted=False;escaped=False
 for i in range(start,len(text)):
  c=text[i]
  if escaped:escaped=False;continue
  if quoted and c=='\\':escaped=True;continue
  if c=='"':quoted=not quoted
  if not quoted:
   depth+=(c=='(')-(c==')')
   if depth==0:return text[start:i+1]
 raise ValueError('Unbalanced expression')
def symbol(name):
 raw=(LIB/'Device.kicad_sym').read_text();s=block(raw,raw.index('(symbol "'+name+'"'))
 return s.replace('(symbol "'+name+'"','(symbol "Device:'+name+'"',1)
def prop(name,value,x,y,hide=False):
 return f'(property "{name}" "{value}" (at {x} {y} 0) (effects (font (size 1.27 1.27))'+(' (hide yes)' if hide else '')+'))'
items=[]
def wire(a,b,key):items.append(f'(wire (pts (xy {a[0]} {a[1]}) (xy {b[0]} {b[1]})) (stroke (width 0) (type default)) (uuid "{uid(key)}"))')
def label(net,p,angle,key):items.append(f'(global_label "{net}" (shape passive) (at {p[0]} {p[1]} {angle}) (effects (font (size 1.27 1.27)) (justify {"right" if angle==0 else "left"})) (uuid "{uid(key)}"))')
def add(name,ref,value,x,y,angle,fp,fields):
 if angle == 90:
  properties=prop('Reference',ref,x,y-8.89)+prop('Value',value,x,y-6.35)
  properties=re.sub(r'(\(at [^()]+) 0\)',r'\1 90)',properties)
 else:
  properties=prop('Reference',ref,x+12.7,y-1.27)+prop('Value',value,x+12.7,y+1.27)
 properties+=prop('Footprint',fp,x,y,True)
 for key,val in fields.items():properties+=prop(key,val,x,y,True)
 items.append(f'(symbol (lib_id "Device:{name}") (at {x} {y} {angle}) (unit 1) (in_bom yes) (on_board yes) (dnp no) (uuid "{uid(ref)}") {properties} '+''.join(f'(pin "{n}" (uuid "{uid(ref+":"+n)}"))' for n in ['1','2'])+f' (instances (project "ddr-power" (path "/{uid("root")}" (reference "{ref}") (unit 1)))))')

add('L_Small','L901','0.47uH',101.6,63.5,90,'Inductor_SMD:L_Coilcraft_XxL4020',{'MPN':'XGL4020-471MEC','Manufacturer':'Coilcraft','LCSC':'C5837785'})
wire((76.2,63.5),(99.06,63.5),'sw');label('PMIC_SW3',(76.2,63.5),0,'sw-label')
wire((104.14,63.5),(241.3,63.5),'output');label('VDD_DDR_1V1',(241.3,63.5),180,'output-label')
for ref,x,value,mpn,lcsc,fp in [('C901',139.7,'22uF','CL32B226KAJNNNE','C309062','C_1210_3225Metric'),('C902',177.8,'10uF','CL31B106KAHNNNE','C14860','C_1206_3216Metric')]:
 add('C_Small',ref,value,x,81.28,0,'Capacitor_SMD:'+fp,{'MPN':mpn,'Manufacturer':'Samsung Electro-Mechanics','LCSC':lcsc,'Voltage Rating':'25V','Qualification':'DDR BUCK3 output; effective capacitance and loop review pending'})
 wire((x,63.5),(x,78.74),ref+'-top');wire((x,83.82),(x,116.84),ref+'-bottom')
for ref,y,value,mpn,lcsc in [('R901',78.74,'47kR','RC0603FR-0747KL','C105579'),('R902',104.14,'120kR','RC0603FR-07120KL','C114607')]:
 add('R_Small_US',ref,value,215.9,y,0,'Resistor_SMD:R_0603_1608Metric',{'MPN':mpn,'Manufacturer':'Yageo','LCSC':lcsc,'Tolerance':'1%','Power Rating':'0.1W'})
wire((215.9,63.5),(215.9,76.2),'r-top');wire((215.9,81.28),(215.9,101.6),'r-mid');label('DDR_FB',(215.9,91.44),0,'fb-label')
wire((215.9,106.68),(215.9,116.84),'r-ground');wire((139.7,116.84),(215.9,116.84),'ground-bank');label('GND',(139.7,116.84),0,'ground-label')
add('C_Small','C903','10uF',63.5,142.24,0,'Capacitor_SMD:C_1206_3216Metric',{'MPN':'CL31B106KAHNNNE','Manufacturer':'Samsung Electro-Mechanics','LCSC':'C14860','Voltage Rating':'25V','Qualification':'Place at RK809 VCC3 pin 24'})
wire((63.5,139.7),(63.5,129.54),'input');label('5V_MAIN',(63.5,129.54),0,'input-label');wire((63.5,144.78),(63.5,152.4),'input-ground');label('GND',(63.5,152.4),0,'input-ground-label')
add('R_Small_US','R904','120R',190.5,152.4,90,'Resistor_SMD:R_0603_1608Metric',{'MPN':'RC0603FR-07120RL','Manufacturer':'Yageo','LCSC':'C114640','Tolerance':'1%','Power Rating':'0.1W','Voltage Rating':'75V','Qualification':'Processor RZQ pull-up for LPDDR4/LPDDR4X; NanoPi R3S sheet 6'})
wire((160.02,152.4),(187.96,152.4),'soc-zq');label('DDR_SOC_RZQ',(160.02,152.4),0,'soc-zq-label')
wire((193.04,152.4),(218.44,152.4),'soc-zq-supply');label('VDD_DDR_1V1',(218.44,152.4),180,'soc-zq-supply-label')
native=(ROOT/'reference/sy8089-electrical-review.kicad_sym').read_text()
ic=block(native,native.index('(symbol "SY8089AAAC"')).replace('(symbol "SY8089AAAC"','(symbol "DdrPowerDraft:SY8089AAAC"',1)
(ROOT/'DdrPowerDraft.kicad_sym').write_text(native)
properties=prop('Reference','U902',91.44,208.28)+prop('Value','SY8089AAAC',91.44,210.82)
for k,v in {'MPN':'SY8089AAAC','Manufacturer':'Silergy','LCSC':'C78988','Footprint':'Package_TO_SOT_SMD:SOT-23-5','Qualification':'Reference LPDDR4X supply; load, loop and sequencing require bench verification'}.items():properties+=prop(k,v,91.44,218.44,True)
items.append(f'(symbol (lib_id "DdrPowerDraft:SY8089AAAC") (at 91.44 218.44 0) (unit 1) (in_bom yes) (on_board yes) (dnp no) (uuid "{uid("U902")}") {properties} (instances (project "ddr-power" (path "/{uid("root")}" (reference "U902") (unit 1)))))')
for net,a,b in [('DDR_VDDQ_EN',(81.28,215.9),(68.58,215.9)),('GND',(81.28,218.44),(68.58,218.44)),('DDR_VDDQ_SW',(81.28,220.98),(68.58,220.98)),('DDR_VDDQ_FB',(101.6,215.9),(114.3,215.9))]:
 wire(a,b,net+'-u902');label(net,b,0 if b[0]<90 else 180,net+'-u902-label')
add('C_Small','C955','10uF',139.7,223.52,0,'Capacitor_SMD:C_1206_3216Metric',{'MPN':'CL31B106KAHNNNE','Manufacturer':'Samsung Electro-Mechanics','LCSC':'C14860','Voltage Rating':'25V','Qualification':'U902 input bypass; place at IN/GND'})
wire((101.6,220.98),(139.7,220.98),'u902-input-cap')
wire((139.7,220.98),(139.7,203.2),'u902-input-source');label('3V3_MAIN',(139.7,203.2),180,'u902-input-label')
wire((139.7,226.06),(139.7,238.76),'u902-cap-ground');label('GND',(139.7,238.76),180,'u902-cap-ground-label')
# Reference enable RC, plus application-note default-off pull-down.
add('R_Small_US','R907','20kR',228.6,218.44,90,'Resistor_SMD:R_0603_1608Metric',{'MPN':'RC0603FR-0720KL','Manufacturer':'Yageo','LCSC':'C105575','Tolerance':'1%','Power Rating':'0.1W','Voltage Rating':'75V'})
wire((205.74,218.44),(226.06,218.44),'vddq-en-source');label('VCC_1V8',(205.74,218.44),0,'vddq-en-source-label')
wire((231.14,218.44),(292.1,218.44),'vddq-en-common');label('DDR_VDDQ_EN',(292.1,218.44),180,'vddq-en-common-label')
add('C_Small','C960','100nF',254,231.14,0,'Capacitor_SMD:C_0603_1608Metric',{'MPN':'CL10B104KA8NNNC','Manufacturer':'Samsung Electro-Mechanics','LCSC':'C1590','Voltage Rating':'25V','Dielectric':'X7R','Tolerance':'10%'})
add('R_Small_US','R908','1MR',292.1,231.14,0,'Resistor_SMD:R_0603_1608Metric',{'MPN':'RC0603FR-071ML','Manufacturer':'Yageo','LCSC':'C105578','Tolerance':'1%','Power Rating':'0.1W','Voltage Rating':'75V','Qualification':'Default-off pull-down; leakage and shutdown timing qualification pending'})
for x,key in [(254,'C960'),(292.1,'R908')]:
 wire((x,218.44),(x,228.6),key+'-top');wire((x,233.68),(x,243.84),key+'-bottom')
wire((254,243.84),(292.1,243.84),'vddq-en-ground');label('GND',(254,243.84),0,'vddq-en-ground-label')
# NanoPi LPDDR4X feedback values; retain documented reference exception.
for ref,y,value,mpn,lcsc in [('R905',81.28,'2kR','RC0603FR-072KL','C105576'),('R906',104.14,'100kR','RC0603FR-07100KL','C14675')]:
 add('R_Small_US',ref,value,330.2,y,0,'Resistor_SMD:R_0603_1608Metric',{'MPN':mpn,'Manufacturer':'Yageo','LCSC':lcsc,'Tolerance':'1%','Power Rating':'0.1W','Voltage Rating':'75V','Qualification':'NanoPi reference divider; 2kR exception to general datasheet guidance recorded'})
add('C_Small','C959','100pF',368.3,81.28,0,'Capacitor_SMD:C_0603_1608Metric',{'MPN':'CL10C101JB8NNNC','Manufacturer':'Samsung Electro-Mechanics','LCSC':'C14858','Voltage Rating':'50V','Dielectric':'C0G','Tolerance':'5%','Qualification':'Reference feed-forward capacitor; loop/transient qualification pending'})
wire((330.2,63.5),(368.3,63.5),'vddq-divider-output');label('VDD_DDR_0V6',(330.2,63.5),0,'vddq-divider-output-label')
for x,ref in [(330.2,'R905'),(368.3,'C959')]:
 wire((x,63.5),(x,78.74),ref+'-top');wire((x,83.82),(x,91.44),ref+'-bottom')
wire((330.2,91.44),(368.3,91.44),'vddq-divider-fb');label('DDR_VDDQ_FB',(368.3,91.44),180,'vddq-divider-fb-label')
wire((330.2,91.44),(330.2,101.6),'vddq-divider-lower-top');wire((330.2,106.68),(330.2,116.84),'vddq-divider-ground');label('GND',(330.2,116.84),0,'vddq-divider-ground-label')
# Keep the reference's 2.2uH value, with a lower-DCR, higher-current part.
add('L_Small','L902','2.2uH',203.2,147.32,90,'Inductor_SMD:L_Coilcraft_XxL4020',{'MPN':'XGL4020-222MEC','Manufacturer':'Coilcraft','Inductance Tolerance':'20%','DCR Maximum':'21.5mOhm','Saturation Current 10% Drop':'2.7A','Thermal Current 20C Rise':'6.7A','Qualification':'SY8089AAAC rail limited by regulator; verify current and loop'})
wire((182.88,147.32),(200.66,147.32),'vddq-switch-filter');label('DDR_VDDQ_SW',(182.88,147.32),0,'vddq-switch-filter-label')
wire((205.74,147.32),(304.8,147.32),'vddq-output-filter');label('VDD_DDR_0V6',(304.8,147.32),180,'vddq-output-filter-label')
for ref,x,value,mpn,lcsc,fp in [('C956',228.6,'22uF','CL32B226KAJNNNE','C309062','C_1210_3225Metric'),('C957',266.7,'22uF','CL32B226KAJNNNE','C309062','C_1210_3225Metric'),('C958',304.8,'10uF','CL31B106KAHNNNE','C14860','C_1206_3216Metric')]:
 add('C_Small',ref,value,x,162.56,0,'Capacitor_SMD:'+fp,{'MPN':mpn,'Manufacturer':'Samsung Electro-Mechanics','LCSC':lcsc,'Voltage Rating':'25V','Dielectric':'X7R','Qualification':'VDDQ regulator output bank; NanoPi sheet 7 nominal values'})
 wire((x,147.32),(x,160.02),ref+'-top');wire((x,165.1),(x,177.8),ref+'-bottom')
wire((228.6,177.8),(304.8,177.8),'vddq-filter-ground');label('GND',(228.6,177.8),0,'vddq-filter-ground-label')
items.append(f'(text "LPDDR4X 0.612V nominal: 2.2uH, 22uF + 22uF + 10uF output.\\nPlace FB sense at load; verify load, ripple, loop and rail order on hardware." (at 35.56 193.04 0) (effects (font (size 1.27 1.27)) (justify left)) (uuid "{uid("u902-note")}"))')
items.append(f'(text "BUCK3: 1.5A rated, external FB reset mode, startup slot 3.\\nNominal 1.113V; ripple, load, thermal and shutdown qualification pending." (at 35.56 25.4 0) (effects (font (size 1.27 1.27)) (justify left)) (uuid "{uid("note")}"))')
from capture import Sheet,stock
flags=Sheet('ddr-power','')
for ref,net,x,y,source in [('#FLG901','VDD_DDR_1V1',241.3,63.5,'RK809 SW3 through L901'),('#FLG902','VDD_DDR_0V6',304.8,147.32,'SY8089 LX through L902')]:
 flags.flag(ref,net,x,y,source)
items.extend(flags.items)
flag_symbol=stock('power','PWR_FLAG').replace('(symbol "PWR_FLAG"','(symbol "power:PWR_FLAG"',1)
(ROOT/'ddr-power.kicad_sch').write_text(f'(kicad_sch (version 20250114) (generator eeschema) (uuid "{uid("root")}") (paper "A3") (title_block (title "DDR and VDDQ supplies — engineering capture") (date "2026-10-07")) (lib_symbols '+symbol('L_Small')+symbol('C_Small')+symbol('R_Small_US')+ic+flag_symbol+') '+' '.join(items)+')')
