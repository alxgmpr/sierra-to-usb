#!/usr/bin/env python3
"""Generate the reviewed always-on supply draft from unmodified KiCad symbols."""
from pathlib import Path
import re, uuid
ROOT=Path(__file__).resolve().parents[1]
LIB=Path('/Applications/KiCad/KiCad.app/Contents/SharedSupport/symbols')
NS=uuid.UUID('cd5e0145-4c4e-44dd-b916-d857aacfc85c')
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
 items.append(f'(symbol (lib_id "{key}") (at {x} {y} {angle}) (unit 1) (in_bom '+('no' if ref.startswith('#') else 'yes')+') (on_board yes) (dnp no) (uuid "'+uid(ref)+'") '+properties+' '+''.join(f'(pin "{p}" (uuid "{uid(ref+":"+p)}"))' for p in pins)+f' (instances (project "pmic" (path "/{uid("root")}" (reference "{ref}") (unit 1)))))')
 return {num:(float(px),float(py)) for px,py,num in re.findall(r'\(pin .*?\(at ([\d.\-]+) ([\d.\-]+) [\d.\-]+\).*?\(number "([^"]+)"',s,re.S)}
def wire(a,b):
 a=tuple(round(v,4) for v in a);b=tuple(round(v,4) for v in b)
 global counter
 counter+=1
 items.append(f'(wire (pts (xy {a[0]} {a[1]}) (xy {b[0]} {b[1]})) (stroke (width 0) (type default)) (uuid "{uid("wire"+str(counter))}"))')
def junction(p):items.append(f'(junction (at {p[0]} {p[1]}) (diameter 0) (color 0 0 0 0) (uuid "{uid("junction"+str(p))}"))')
def label(name,p):items.append(f'(label "{name}" (at {p[0]} {p[1]} 0) (effects (font (size 1.27 1.27)) (justify left bottom)) (uuid "{uid("label"+name+str(p))}"))')
def power(name,p,ref):add('power',name,ref,name,*p)
def note(text,p,size=1.27):items.append(f'(text "{text}" (at {p[0]} {p[1]} 0) (effects (font (size {size} {size})) (justify left)) (uuid "{uid(text)}"))')
def pinlabel(number,name):
 px,py=pins[number]; a=(101.6+px,76.2-py);b=(a[0]+(-7.62 if px<0 else 7.62),a[1]);wire(a,b);power('+3V3',b,'#PWR413') if name=='+3V3' else label(name,b)

# Native full four-unit PMIC; unresolved pins deliberately remain unconnected.
raw=(ROOT/'Recovery.kicad_sym').read_text()
s=block(raw,raw.index('(symbol "RK809-5"')).replace('(symbol "RK809-5"','(symbol "Recovery:RK809-5"',1)
used['Recovery:RK809-5']=s
fp=re.search(r'\(property "Footprint" "([^"]+)"',s)[1]
units={}
for unit,x,y in [(1,101.6,81.28),(2,101.6,165.1),(3,101.6,248.92),(4,279.4,215.9)]:
 u=block(s,s.index(f'(symbol "RK809-5_{unit}_1"'))
 pins={n:(round(x+float(px),4),round(y-float(py),4)) for px,py,n in re.findall(r'\(pin .*?\(at ([\d.\-]+) ([\d.\-]+) [\d.\-]+\).*?\(number "([^"]+)"',u,re.S)}
 units[unit]=pins
 fields=prop('Reference','U501',x-25.4,y-30.48)+prop('Value','RK809-5',x-25.4,y-27.94)+prop('Footprint',fp,x,y,True)+prop('MPN','RK809-5',x,y,True)+prop('Manufacturer','Rockchip',x,y,True)+prop('LCSC','C2939628',x,y,True)
 items.append(f'(symbol (lib_id "Recovery:RK809-5") (at {x} {y} 0) (unit {unit}) (in_bom yes) (on_board yes) (dnp no) (uuid "{uid("U501:"+str(unit))}") '+fields+' '+''.join(f'(pin "{n}" (uuid "{uid("U501:"+n)}"))' for n in pins)+f' (instances (project "pmic" (path "/{uid("root")}" (reference "U501") (unit {unit})))))')
def terminal(n,net,direction):
 a=units[1][str(n)];b=(round(a[0]+direction*7.62,4),a[1]);wire(a,b);label(net,b)
 # Left-side label text must extend away from the body.
 if direction<0:items[-1]=items[-1].replace('(justify left bottom)','(justify right bottom)')
for n,net,d in [(10,'5V_MAIN',0),(11,'5V_MAIN',0),(9,'PMIC_SW2',1),(12,'PMIC_SW1',1),(8,'VDD_GPU_SENSE',-1),(13,'VDD_LOGIC_SENSE',-1)]:
 if d:terminal(n,net,d)
 else:
  a=units[1][str(n)];b=(a[0],40.64);wire(a,b)
wire((88.9,40.64),(93.98,40.64));label("5V_MAIN",(88.9,40.64))
capfields={'MPN':'CL32B226KAJNNNE','Manufacturer':'Samsung Electro-Mechanics','LCSC':'C309062','Qualification':'Effective-capacitance review and load stability pending'}
for channel,y,out,sense,cref in [(1,63.5,'VDD_LOGIC','VDD_LOGIC_SENSE',501),(2,129.54,'VDD_GPU','VDD_GPU_SENSE',505)]:
 add('Device','L_Small',f'L50{channel}','0.47uH',238.76,y,90,fp='Inductor_SMD:L_Coilcraft_XxL4020',fields={'MPN':'XGL4020-471MEC','Manufacturer':'Coilcraft','LCSC':'C5837785'})
 wire((223.52,y),(236.22,y));label(f'PMIC_SW{channel}',(223.52,y))
 wire((241.3,y),(327.66,y));label(out,(327.66,y))
 for j,x in enumerate([266.7,297.18,327.66]):
  add('Device','C_Small',f'C{cref+j}','22uF / 25V',x,y+12.7,fp='Capacitor_SMD:C_1210_3225Metric',fields=capfields)
  wire((x,y),(x,y+10.16));wire((x,y+15.24),(x,y+22.86));junction((x,y))
 wire((266.7,y+22.86),(327.66,y+22.86));junction((297.18,y+22.86));power('GND',(297.18,y+22.86),f'#PWR50{channel}')
 # Dedicated routed sense connects electrically at bank; physical Kelvin route to load required.
 wire((327.66,y),(353.06,y));wire((353.06,y),(353.06,y+22.86));label(sense,(353.06,y+22.86))
 add('Device','C_Small',f'C{cref+3}','22uF / 25V',185.42,y+12.7,fp='Capacitor_SMD:C_1210_3225Metric',fields=capfields)
 wire((185.42,y+10.16),(185.42,y));label('5V_MAIN',(185.42,y));wire((185.42,y+15.24),(185.42,y+22.86));power('GND',(185.42,y+22.86),f'#PWR51{channel}')
 note(f'BUCK{channel}: 0.9V startup / 2.5A rated; 3 x 22uF output bank',(175.26,y-12.7))
note('PMIC capture in progress — BUCK1 / BUCK2',(35.56,22.86),2.54)
note('DRAFT: other rails and management/audio pins are deliberately unwired.\\nNo complete ERC or appliance BOM claim. Do not use for fabrication.\\nFeedback sense must route to processor load; verify ground return and placement.',(175.26,172.72))
text='(kicad_sch (version 20250114) (generator eeschema) (uuid "'+uid('root')+'") (paper "A3") (title_block (title "PMIC capture draft") (date "2026-10-03") (rev "0.1-draft")) (lib_symbols '+'\n'.join(used.values())+')\n'+'\n'.join(items)+'\n(sheet_instances (path "/" (page "1"))))\n'
(ROOT/'pmic.kicad_sch').write_text(text)
print('Generated PMIC draft; all 69 pins retained, unfinished pins intentionally visible.')
