#!/usr/bin/env python3
"""Generate reviewed USB analog supply filter draft from standard symbols."""
from pathlib import Path
import re
import uuid
ROOT=Path(__file__).resolve().parents[1]
LIB=Path('/Applications/KiCad/KiCad.app/Contents/SharedSupport/symbols')
def uid(key):return str(uuid.uuid5(uuid.NAMESPACE_URL,'sierra-phy-power-'+key))
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
 items.append(f'(symbol (lib_id "Device:{name}") (at {x} {y} {angle}) (unit 1) (in_bom yes) (on_board yes) (dnp no) (uuid "{uid(ref)}") {properties} '+''.join(f'(pin "{n}" (uuid "{uid(ref+":"+n)}"))' for n in ['1','2'])+f' (instances (project "phy-power" (path "/{uid("root")}" (reference "{ref}") (unit 1)))))')
for fb,cap,source,dest,y in [('FB801','C813','VDDA_0V9','USB_AVDD_0V9',63.5),('FB802','C814','VCCA_1V8','USB_AVDD_1V8',127)]:
 add('FerriteBead_Small',fb,'120R @ 100MHz',139.7,y,90,'Inductor_SMD:L_0603_1608Metric',{'MPN':'MPZ1608S121ATAH0','Manufacturer':'TDK','LCSC':'C114770','DCR Maximum':'45mOhm','Current Rating':'2A','Qualification':'Draft USB filter; thermal voltage drop and bias impedance pending'})
 add('C_Small',cap,'1uF / 25V',101.6,y+20.32,0,'Capacitor_SMD:C_0603_1608Metric',{'MPN':'CL10B105KA8NNNC','Manufacturer':'Samsung Electro-Mechanics','LCSC':'C29936','Qualification':'Source-side bypass per RK3566 guide Figure 2-48'})
 wire((76.2,y),(101.6,y),fb+'-source1');wire((101.6,y),(137.16,y),fb+'-source2');label(source,(76.2,y),0,fb+'-source-label')
 wire((101.6,y),(101.6,y+17.78),cap+'-top')
 items.append(f'(junction (at 101.6 {y}) (diameter 0) (color 0 0 0 0) (uuid "{uid(cap+"-junction")}"))')
 wire((142.24,y),(190.5,y),fb+'-out');label(dest,(190.5,y),180,fb+'-out-label')
 wire((101.6,y+22.86),(101.6,y+30.48),cap+'-bottom');label('GND',(101.6,y+30.48),0,cap+'-ground')
items.append(f'(text "USB ANALOG FILTERS: local pin bypass and processor loads are captured.\\n45mOhm maximum DCR differs from 30mOhm reference example.\\nRail headroom, thermal limits and bead/capacitor damping remain to verify." (at 35.56 25.4 0) (effects (font (size 1.27 1.27)) (justify left)) (uuid "{uid("note")}"))')
(ROOT/'phy-power.kicad_sch').write_text(f'(kicad_sch (version 20250114) (generator eeschema) (uuid "{uid("root")}") (paper "A4") (title_block (title "USB PHY analog filters — engineering capture") (date "2026-10-07")) (lib_symbols '+symbol('FerriteBead_Small')+symbol('C_Small')+') '+' '.join(items)+' (sheet_instances (path "/" (page "1"))))\n')
print('Generated two USB supply beads and two source-side bypass capacitors.')
