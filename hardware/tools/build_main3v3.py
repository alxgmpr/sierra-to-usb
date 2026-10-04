#!/usr/bin/env python3
"""Generate the reviewed always-on supply draft from unmodified KiCad symbols."""
from pathlib import Path
import re, uuid
ROOT=Path(__file__).resolve().parents[1]
LIB=Path('/Applications/KiCad/KiCad.app/Contents/SharedSupport/symbols')
NS=uuid.UUID('d93a1f6c-985a-4f01-8a3e-c4e66e488ac0')
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
 items.append(f'(symbol (lib_id "{key}") (at {x} {y} {angle}) (unit 1) (in_bom '+('no' if ref.startswith('#') else 'yes')+') (on_board yes) (dnp no) (uuid "'+uid(ref)+'") '+properties+' '+''.join(f'(pin "{p}" (uuid "{uid(ref+":"+p)}"))' for p in pins)+f' (instances (project "main3v3" (path "/{uid("root")}" (reference "{ref}") (unit 1)))))')
 return {num:(float(px),float(py)) for px,py,num in re.findall(r'\(pin .*?\(at ([\d.\-]+) ([\d.\-]+) [\d.\-]+\).*?\(number "([^"]+)"',s,re.S)}
def wire(a,b):
 a=tuple(round(v,4) for v in a);b=tuple(round(v,4) for v in b)
 global counter
 counter+=1
 items.append(f'(wire (pts (xy {a[0]} {a[1]}) (xy {b[0]} {b[1]})) (stroke (width 0) (type default)) (uuid "{uid("wire"+str(counter))}"))')
def junction(p):items.append(f'(junction (at {p[0]} {p[1]}) (diameter 0) (color 0 0 0 0) (uuid "{uid("junction"+str(p))}"))')
def label(name,p):
 if name in {'5V_MAIN','3V3_MAIN','MAIN3V3_GOOD'}:
  items.append(f'(global_label "{name}" (shape passive) (at {p[0]} {p[1]} 0) (effects (font (size 1.27 1.27)) (justify left)) (uuid "{uid("global"+name+str(p))}"))');return
 items.append(f'(label "{name}" (at {p[0]} {p[1]} 0) (effects (font (size 1.27 1.27)) (justify left bottom)) (uuid "{uid("label"+name+str(p))}"))')
def power(name,p,ref):add('power',name,ref,name,*p)
def note(text,p,size=1.27):items.append(f'(text "{text}" (at {p[0]} {p[1]} 0) (effects (font (size {size} {size})) (justify left)) (uuid "{uid(text)}"))')
def pinlabel(number,name):
 px,py=pins[number]; a=(101.6+px,76.2-py);b=(a[0]+(-7.62 if px<0 else 7.62),a[1]);wire(a,b);power('+3V3',b,'#PWR413') if name=='+3V3' else label(name,b)


raw=(ROOT/'Recovery.kicad_sym').read_text()
used['Recovery:MP2143DJ-LF-Z']=block(raw,raw.index('(symbol "MP2143DJ-LF-Z"')).replace('(symbol "MP2143DJ-LF-Z"','(symbol "Recovery:MP2143DJ-LF-Z"',1)
add('Recovery','MP2143DJ-LF-Z','U601','MP2143DJ-LF-Z',101.6,76.2,fp='Package_TO_SOT_SMD:TSOT-23-8',fields={'MPN':'MP2143DJ-LF-Z','Manufacturer':'Monolithic Power Systems','LCSC':'C43427'})
wire((101.6,66.04),(101.6,50.8));label('5V_MAIN',(101.6,50.8))
wire((91.44,73.66),(78.74,73.66));label('MAIN3V3_EN',(78.74,73.66));items[-1]=items[-1].replace('justify left bottom','justify right bottom')
wire((111.76,78.74),(124.46,78.74));label('MAIN3V3_PG_5V',(124.46,78.74))
for x in [99.06,104.14]:wire((x,86.36),(x,93.98))
wire((99.06,93.98),(104.14,93.98));power('GND',(101.6,93.98),'#PWR601')
add('Device','L','L601','1uH',139.7,73.66,angle=90,fp='Inductor_SMD:L_Coilcraft_XxL4030',fields={'MPN':'XGL4030-102MEC','Manufacturer':'Coilcraft','LCSC':'C6336766','Qualification':'Footprint dimensions and hot saturation pending'})
wire((111.76,73.66),(135.89,73.66));wire((143.51,73.66),(175.26,73.66));label('3V3_MAIN',(175.26,73.66))
wire((91.44,78.74),(83.82,78.74));label('3V3_MAIN',(83.82,78.74));items[-1]=items[-1].replace('(at 83.82 78.74 0)','(at 83.82 78.74 180)').replace('justify left','justify right')
cap={'MPN':'CL32B226KAJNNNE','Manufacturer':'Samsung Electro-Mechanics','LCSC':'C309062','Qualification':'Bank sizing and loop stability pending'}
for ref,x,y,net in [('C601',55.88,63.5,'5V_MAIN'),('C602',175.26,91.44,'3V3_MAIN'),('C603',200.66,91.44,'3V3_MAIN')]:
 add('Device','C_Small',ref,'22uF / 25V',x,y,fp='Capacitor_SMD:C_1210_3225Metric',fields=cap)
 wire((x,y-2.54),(x,y-10.16));label(net,(x,y-10.16));wire((x,y+2.54),(x,y+10.16));power('GND',(x,y+10.16),'#PWR62'+ref[1:])
for ref,value,mpn,lcsc,y in [('R601','200kR','RT0603BRD07200KL','C728585',127),('R602','44.2kR','RT0603BRD0744K2L','C861410',142.24)]:
 add('Device','R_Small_US',ref,value,139.7,y,fp='Resistor_SMD:R_0603_1608Metric',fields={'MPN':mpn,'Manufacturer':'Yageo','LCSC':lcsc,'Tolerance':'0.1%','TCR':'25ppm/C'})
wire((139.7,124.46),(139.7,116.84));label('3V3_MAIN',(139.7,116.84))
wire((139.7,129.54),(139.7,139.7));label('MAIN3V3_FB',(139.7,134.62))
wire((91.44,76.2),(83.82,76.2));label('MAIN3V3_FB',(83.82,76.2));items[-1]=items[-1].replace('justify left bottom','justify right bottom')
wire((139.7,144.78),(139.7,152.4));power('GND',(139.7,152.4),'#PWR610')
# Reference enable divider: rail follows upstream 5 V without a PMIC dependency.
for ref,value,mpn,lcsc,y in [('R603','20kR','RC0603FR-0720KL','C105575',127),('R604','10kR','RC0603FR-0710KL','C98220',142.24)]:
 add('Device','R_Small_US',ref,value,210.82,y,fp='Resistor_SMD:R_0603_1608Metric',fields={'MPN':mpn,'Manufacturer':'Yageo','LCSC':lcsc,'Tolerance':'1%'})
wire((210.82,124.46),(210.82,116.84));label('5V_MAIN',(210.82,116.84))
wire((210.82,129.54),(210.82,139.7));label('MAIN3V3_EN',(210.82,134.62))
wire((210.82,144.78),(210.82,152.4));power('GND',(210.82,152.4),'#PWR611')
# 5 V tolerant Schmitt input, powered by the independent recovery supply.
add('74xGxx','74LVC1G17','U602','SN74LVC1G17DBVR',210.82,45.72,fp='Package_TO_SOT_SMD:SOT-23-5',fields={'MPN':'SN74LVC1G17DBVR','Manufacturer':'Texas Instruments','LCSC':'C7836'})
items[-1]=items[-1].replace('(at 185.42 30.72 0)','(at 210.82 22.86 0)').replace('(at 185.42 33.72 0)','(at 210.82 25.4 0)')
wire((198.12,45.72),(185.42,45.72));label('MAIN3V3_PG_5V',(185.42,45.72));items[-1]=items[-1].replace('justify left bottom','justify right bottom')
wire((220.98,45.72),(233.68,45.72));label('MAIN3V3_GOOD',(233.68,45.72))
power('+3V3',(205.74,35.56),'#PWR612');power('GND',(205.74,55.88),'#PWR613')
add('Device','C_Small','C604','100nF / 25V',254,66.04,fp='Capacitor_SMD:C_0603_1608Metric',fields={'MPN':'CL10B104KA8NNNC','Manufacturer':'Samsung Electro-Mechanics','LCSC':'C1590'})
power('+3V3',(254,63.5),'#PWR614');power('GND',(254,68.58),'#PWR615')
for ref,value,mpn,lcsc,y in [('R605','10kR','RC0603FR-0710KL','C98220',127),('R606','100kR','RC0603FR-07100KL','C14675',142.24)]:
 add('Device','R_Small_US',ref,value,254,y,fp='Resistor_SMD:R_0603_1608Metric',fields={'MPN':mpn,'Manufacturer':'Yageo','LCSC':lcsc,'Tolerance':'1%'})
wire((254,124.46),(254,116.84));label('5V_MAIN',(254,116.84))
wire((254,129.54),(254,139.7));label('MAIN3V3_PG_5V',(254,134.62))
wire((254,144.78),(254,152.4));power('GND',(254,152.4),'#PWR616')
note('DRAFT: Upstream 5V sequencing, PG translation, capacitance and thermal margins unfinished.',(35.56,172.72))
(ROOT/'main3v3.kicad_sch').write_text('(kicad_sch (version 20250114) (generator eeschema) (uuid "'+uid('root')+'") (paper "A4") (lib_symbols '+''.join(used.values())+') '+''.join(items)+')\n')
print('Generated main 3.3V draft')
