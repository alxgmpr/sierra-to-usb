#!/usr/bin/env python3
"""Generate reviewed USB analog supply filter draft from standard symbols."""
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
items.append(f'(text "BUCK3: 1.5A rated, external FB reset mode, startup slot 3.\\nNominal 1.113V; ripple, load, thermal and shutdown qualification pending." (at 35.56 25.4 0) (effects (font (size 1.27 1.27)) (justify left)) (uuid "{uid("note")}"))')
(ROOT/'ddr-power.kicad_sch').write_text(f'(kicad_sch (version 20250114) (generator eeschema) (uuid "{uid("root")}") (paper "A4") (title_block (title "DDR BUCK3 supply — DRAFT") (date "2026-10-04")) (lib_symbols '+symbol('L_Small')+symbol('C_Small')+symbol('R_Small_US')+') '+' '.join(items)+')')
