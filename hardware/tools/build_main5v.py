#!/usr/bin/env python3
"""Generate the main 5 V regulator control draft; power path remains incomplete."""
from pathlib import Path
import re, uuid
ROOT=Path(__file__).resolve().parents[1]
LIB=Path('/Applications/KiCad/KiCad.app/Contents/SharedSupport/symbols')
NS=uuid.UUID('54134c9d-1c55-4e62-b8a4-63fd630ad347')
def uid(key):return str(uuid.uuid5(NS,key))
def block(text,start):
 depth=0; quoted=False; escape=False
 for i in range(start,len(text)):
  c=text[i]
  if escape:escape=False;continue
  if c=='\\' and quoted:escape=True;continue
  if c=='"':quoted=not quoted
  if not quoted:
   if c=='(':depth+=1
   elif c==')':
    depth-=1
    if depth==0:return text[start:i+1]
 raise ValueError('Unbalanced S expression')
def library(lib,name):
 text=(LIB/(lib+'.kicad_sym')).read_text()
 match=re.search(r'\(symbol "'+re.escape(name)+r'"\s',text)
 assert match,(lib,name)
 s=block(text,match.start())
 assert '(extends ' not in s,'Use a resolved standard symbol'
 return s.replace('(symbol "'+name+'"','(symbol "'+lib+':'+name+'"',1)
used={};items=[];counter=0
font='(effects (font (size 1.27 1.27)))'
def prop(name,value,x,y,hide=False):
 return f'(property "{name}" "{value}" (at {x} {y} 0) (effects (font (size 1.27 1.27))'+(' (hide yes)' if hide else '')+'))'
def add(lib,name,ref,value,x,y,angle=0,fp='',fields=None):
 key=lib+':'+name
 if key not in used:used[key]=library(lib,name)
 s=used[key]
 pins=re.findall(r'\(number "([^"]+)"',s)
 assert len(pins)==len(set(pins)),(ref,pins)
 if ref.startswith('#'):
  properties=prop('Reference',ref,x,y,True)+prop('Value',value,x,y+(3.81 if name=='GND' else -3.81),ref.startswith('#FLG'))
 elif ref.startswith('U'):
  properties=prop('Reference',ref,x,y-15)+prop('Value',value,x,y-12)
 elif ref.startswith('L'):
  properties=prop('Reference',ref,x,y-6.35)+prop('Value',value,x,y-3.81)
 else:
  properties=prop('Reference',ref,x+8.89,y-1.27)+prop('Value',value,x+12.7,y+1.27)
 if ref.startswith('L'):
  properties=re.sub(r'(\(at [^()]+) 0\)',r'\1 90)',properties)
 if ref.startswith('C'):
  properties=prop('Reference',ref,x-10.16,y-1.27)+prop('Value',value,x-10.16,y+1.27)
  properties=properties.replace('(effects (font (size 1.27 1.27)))','(effects (font (size 1.27 1.27)) (justify right))')
 properties+=prop('Footprint',fp,x,y,True)
 for k,v in (fields or {}).items():properties+=prop(k,v,x,y,True)
 items.append(f'(symbol (lib_id "{key}") (at {x} {y} {angle}) (unit 1) (in_bom '+('no' if ref.startswith('#') else 'yes')+') (on_board yes) (dnp no) (uuid "'+uid(ref)+'") '+properties+' '+''.join(f'(pin "{p}" (uuid "{uid(ref+":"+p)}"))' for p in pins)+f' (instances (project "main5v" (path "/{uid("root")}" (reference "{ref}") (unit 1)))))')
 return {num:(float(px),float(py)) for px,py,num in re.findall(r'\(pin .*?\(at ([\d.\-]+) ([\d.\-]+) [\d.\-]+\).*?\(number "([^"]+)"',s,re.S)}
def wire(a,b):
 a=tuple(round(v,4) for v in a);b=tuple(round(v,4) for v in b)
 global counter
 counter+=1
 items.append(f'(wire (pts (xy {a[0]} {a[1]}) (xy {b[0]} {b[1]})) (stroke (width 0) (type default)) (uuid "{uid("wire"+str(counter))}"))')
def junction(p):items.append(f'(junction (at {p[0]} {p[1]}) (diameter 0) (color 0 0 0 0) (uuid "{uid("junction"+str(p))}"))')
def label(name,p):
 if name in {'5V_MAIN','ISO_12V','MCU_MAIN5V_EN','MAIN5V_GOOD'}:
  items.append(f'(global_label "{name}" (shape passive) (at {p[0]} {p[1]} 0) (effects (font (size 1.27 1.27)) (justify left)) (uuid "{uid("global"+name+str(p))}"))');return
 items.append(f'(label "{name}" (at {p[0]} {p[1]} 0) (effects (font (size 1.27 1.27)) (justify left bottom)) (uuid "{uid("label"+name+str(p))}"))')
def power(name,p,ref):add('power',name,ref,name,*p)
def note(text,p,size=1.27):items.append(f'(text "{text}" (at {p[0]} {p[1]} 0) (effects (font (size {size} {size})) (justify left)) (uuid "{uid(text)}"))')

raw=(ROOT/'Recovery.kicad_sym').read_text()
used['Recovery:TPS56837RPAR']=block(raw,raw.index('(symbol "TPS56837RPAR"')).replace('(symbol "TPS56837RPAR"','(symbol "Recovery:TPS56837RPAR"',1)
add('Recovery','TPS56837RPAR','U701','TPS56837RPAR',101.6,76.2,fields={'MPN':'TPS56837RPAR','Manufacturer':'Texas Instruments','LCSC':'C22428366','Qualification':'Footprint pending review; incomplete power path'})
items[-1]=items[-1].replace('(at 101.6 61.2 0)','(at 88.9 53.34 0)').replace('(at 101.6 64.2 0)','(at 88.9 56.388 0)')
# MODE resistor directly below the control pin.
wire((88.9,81.28),(66.04,81.28));wire((66.04,81.28),(66.04,101.6))
add('Device','R_Small_US','R701','30.1kR',66.04,104.14,fp='Resistor_SMD:R_0603_1608Metric',fields={'MPN':'RC0603FR-0730K1L','Manufacturer':'Yageo','LCSC':'C137745','Tolerance':'1%'})
wire((66.04,106.68),(66.04,114.3));power('GND',(66.04,114.3),'#PWR701')
label('MAIN5V_MODE',(66.04,81.28))
# Feedback divider shares its node with the FB pin using a named local connection.
wire((88.9,76.2),(78.74,76.2));label('MAIN5V_FB',(78.74,76.2));items[-1]=items[-1].replace('justify left bottom','justify right bottom')
for ref,value,mpn,lcsc,y in [('R702','73.2kR','RT0603BRD0773K2L','C861548',58.42),('R703','10kR','RT0603BRD0710KL','C95204',83.82)]:
 add('Device','R_Small_US',ref,value,200.66,y,fp='Resistor_SMD:R_0603_1608Metric',fields={'MPN':mpn,'Manufacturer':'Yageo','LCSC':lcsc,'Tolerance':'0.1%','TCR':'25ppm/K'})
wire((200.66,55.88),(200.66,45.72));label('5V_MAIN',(200.66,45.72))
wire((200.66,60.96),(200.66,81.28));label('MAIN5V_FB',(200.66,73.66))
wire((200.66,86.36),(200.66,96.52));power('GND',(200.66,96.52),'#PWR702')
# AGND and PGND share the electrical return; physical connection follows TI layout guidance.
wire((99.06,88.9),(99.06,99.06));wire((104.14,88.9),(104.14,99.06));wire((99.06,99.06),(104.14,99.06));power('GND',(101.6,99.06),'#PWR703');junction((101.6,99.06))
# Bootstrap capacitor: differential voltage is BOOT-SW, not the rail-to-ground voltage.
add('Device','C_Small','C701','100nF / 25V',139.7,58.42,fp='Capacitor_SMD:C_0603_1608Metric',fields={'MPN':'CL10B104KA8NNNC','Manufacturer':'Samsung Electro-Mechanics','LCSC':'C1590','Dielectric':'X7R','Qualification':'Place immediately between BOOT and SW'})
wire((104.14,63.5),(104.14,45.72));wire((104.14,45.72),(139.7,45.72));wire((139.7,45.72),(139.7,55.88))
wire((139.7,60.96),(139.7,71.12));wire((114.3,71.12),(139.7,71.12));label('MAIN5V_SW',(139.7,71.12))
# Adjustable soft-start capacitor follows the TI reference's 47 nF value.
add('Device','C_Small','C702','47nF / 50V',139.7,104.14,fp='Capacitor_SMD:C_0603_1608Metric',fields={'MPN':'CL10B473KB8NNNC','Manufacturer':'Samsung Electro-Mechanics','LCSC':'C1622','Dielectric':'X7R','Tolerance':'10%','Qualification':'4.7ms typical startup; full timing bounds unqualified'})
wire((114.3,81.28),(139.7,81.28));wire((139.7,81.28),(139.7,101.6));wire((139.7,106.68),(139.7,114.3));power('GND',(139.7,114.3),'#PWR704')
# Input bypass bank: isolated rail only; never raw PoE.
wire((99.06,63.5),(99.06,40.64));label('ISO_12V',(99.06,40.64))
for ref,x in [('C703',210.82),('C704',236.22),('C705',261.62)]:
 bulk=ref!='C705'
 add('Device','C_Small',ref,'10uF / 50V' if bulk else '100nF / 25V',x,104.14,fp='Capacitor_SMD:C_1206_3216Metric' if bulk else 'Capacitor_SMD:C_0603_1608Metric',fields={'MPN':'CL31B106KBHNNNE' if bulk else 'CL10B104KA8NNNC','Manufacturer':'Samsung Electro-Mechanics','LCSC':'C89632' if bulk else 'C1590','Dielectric':'X7R','Qualification':'Input ripple and effective-capacitance qualification pending'})
 wire((x,101.6),(x,91.44));wire((x,106.68),(x,116.84))
wire((210.82,91.44),(261.62,91.44));junction((236.22,91.44));wire((236.22,91.44),(236.22,83.82));label('ISO_12V',(236.22,83.82))
wire((210.82,116.84),(261.62,116.84));junction((236.22,116.84));power('GND',(236.22,116.84),'#PWR705')
# Recovery MCU controls EN; external pulldown holds EN low with the GPIO high impedance.
add('Device','R_Small_US','R704','1kR',66.04,68.58,angle=90,fp='Resistor_SMD:R_0603_1608Metric',fields={'MPN':'RC0603FR-071KL','Manufacturer':'Yageo','LCSC':'C22548','Tolerance':'1%'})
items[-1]=re.sub(r'(\(property "Reference" "R704" \(at )[^)]*',r'\g<1>66.04 60.96 90',items[-1])
items[-1]=re.sub(r'(\(property "Value" "1kR" \(at )[^)]*',r'\g<1>66.04 63.5 90',items[-1])
wire((63.5,68.58),(53.34,68.58));label('MCU_MAIN5V_EN',(53.34,68.58));items[-1]=items[-1].replace('(at 53.34 68.58 0)','(at 53.34 68.58 180)').replace('justify left','justify right')
wire((68.58,68.58),(76.2,68.58));wire((76.2,68.58),(76.2,71.12));wire((76.2,71.12),(88.9,71.12));wire((76.2,71.12),(40.64,71.12));junction((76.2,71.12))
add('Device','R_Small_US','R705','10kR',40.64,104.14,fp='Resistor_SMD:R_0603_1608Metric',fields={'MPN':'RC0603FR-0710KL','Manufacturer':'Yageo','LCSC':'C98220','Tolerance':'1%'})
wire((40.64,71.12),(40.64,101.6));wire((40.64,106.68),(40.64,114.3));power('GND',(40.64,114.3),'#PWR706')
# PG is open drain; use the independent recovery supply for the MCU-safe pullup.
add('Device','R_Small_US','R706','10kR',154.94,73.66,fp='Resistor_SMD:R_0603_1608Metric',fields={'MPN':'RC0603FR-0710KL','Manufacturer':'Yageo','LCSC':'C98220','Tolerance':'1%'})
wire((154.94,71.12),(154.94,63.5));power('+3V3',(154.94,63.5),'#PWR707')
wire((114.3,76.2),(154.94,76.2));wire((154.94,76.2),(154.94,81.28));label('MAIN5V_GOOD',(154.94,81.28));junction((154.94,76.2))
note('MAIN 5 V CONTROL DRAFT — INCOMPLETE',(35.56,25.4),1.524)
note('MODE: 500 kHz; high valley current limit option. Feedback: 4.992 V nominal.',(35.56,132.08))
note('Missing: inductor and output bank.',(35.56,139.7))
note('No 5 V power source exists on this sheet yet. Regulator footprint awaits review.',(35.56,147.32))
(ROOT/'main5v.kicad_sch').write_text('(kicad_sch (version 20250114) (generator eeschema) (uuid "'+uid('root')+'") (paper "A4") (lib_symbols '+''.join(used.values())+') '+''.join(items)+')\n')
print('Generated main 5 V control draft with twelve exact-MPN components.')
