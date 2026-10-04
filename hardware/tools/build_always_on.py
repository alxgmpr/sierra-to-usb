#!/usr/bin/env python3
"""Generate the reviewed always-on supply draft from unmodified KiCad symbols."""
from pathlib import Path
import re, uuid
ROOT=Path(__file__).resolve().parents[1]
LIB=Path('/Applications/KiCad/KiCad.app/Contents/SharedSupport/symbols')
NS=uuid.UUID('b876305a-05e0-4abd-901c-37fc6c579d52')
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
 items.append(f'(symbol (lib_id "{key}") (at {x} {y} {angle}) (unit 1) (in_bom '+('no' if ref.startswith('#') else 'yes')+') (on_board yes) (dnp no) (uuid "'+uid(ref)+'") '+properties+' '+''.join(f'(pin "{p}" (uuid "{uid(ref+":"+p)}"))' for p in pins)+f' (instances (project "always-on" (path "/{uid("root")}" (reference "{ref}") (unit 1)))))')
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
pins=add('Regulator_Switching','TPS62177DQC','U401','TPS62177DQCR',101.6,76.2,fp='Package_SON:WSON-10-1EP_2x3mm_P0.5mm_EP0.84x2.4mm_ThermalVias',fields={'MPN':'TPS62177DQCR','Manufacturer':'Texas Instruments','LCSC':'C91241','Datasheet':'https://www.ti.com/lit/ds/symlink/tps62175.pdf'})
# Convert standard symbol coordinates to schematic coordinates and audit the TI pin table.
assert set(pins)==set(map(str,range(1,12))),pins
for n in ['1','4','6','11']:
 px,py=pins[n];a=(round(101.6+px,4),round(76.2-py,4));b=(a[0],96.52);wire(a,b)
wire((96.52,96.52),(104.14,96.52))
for x in [99.06,101.6]:junction((x,96.52))
power('GND',(101.6,96.52),'#PWR401')
# VIN and EN tied to isolated input. Never tie SLEEP to the 12 V input.
wire((63.5,63.5),(83.82,63.5));wire((83.82,63.5),(83.82,71.12))
wire((83.82,68.58),(91.44,68.58));wire((83.82,71.12),(91.44,71.12));junction((83.82,68.58))
wire((91.44,76.2),(73.66,76.2));power('+3V3',(73.66,76.2),'#PWR413')
wire((91.44,81.28),(76.2,81.28));wire((76.2,81.28),(76.2,91.44));label('AON_POWER_GOOD',(76.2,91.44))
px,py=pins['5'];a=(101.6+px,76.2-py);wire(a,(a[0]+5.08,a[1]));power('GND',(a[0]+5.08,a[1]),'#PWR405')
px,py=pins['9'];sw=(round(101.6+px,4),round(76.2-py,4))
# L_Small rotated so pin 1 is on the left; output sense is after the inductor.
add('Device','L_Small','L401','10uH',139.7,sw[1],90,fp='Inductor_SMD:L_Coilcraft_LPS4018',fields={'MPN':'LPS4018-103MRC','Manufacturer':'Coilcraft','LCSC':'C6127589','Datasheet':'https://www.coilcraft.com/getmedia/31b05c96-4c4c-4498-8dbb-fe092de76bad/lps4018.pdf'})
wire(sw,(137.16,sw[1]));wire((142.24,sw[1]),(165.1,sw[1]));power('+3V3',(165.1,sw[1]),'#PWR409')
px,py=pins['10'];vos=(101.6+px,76.2-py);wire(vos,(165.1,vos[1]));wire((165.1,vos[1]),(165.1,sw[1]));junction((165.1,sw[1]))
add('Device','C_Small','C401','4.7uF / 50V',63.5,76.2,fp='Capacitor_SMD:C_1206_3216Metric',fields={'MPN':'CL31B475KBHNNNE','Manufacturer':'Samsung Electro-Mechanics','LCSC':'C51205','Qualification':'DC-bias curve pending'})
wire((63.5,73.66),(63.5,63.5));label('ISO_12V',(63.5,63.5));wire((63.5,78.74),(63.5,86.36));power('GND',(63.5,86.36),'#PWR410')
add('Device','C_Small','C402','22uF / 25V',185.42,76.2,fp='Capacitor_SMD:C_1210_3225Metric',fields={'MPN':'CL32B226KAJNNNE','Manufacturer':'Samsung Electro-Mechanics','LCSC':'C309062','Qualification':'DC-bias curve pending; provisional selection'})
wire((185.42,73.66),(185.42,sw[1]));wire((165.1,sw[1]),(185.42,sw[1]));wire((185.42,78.74),(185.42,86.36));power('GND',(185.42,86.36),'#PWR411')
add('Device','C_Small','C403','22uF / 25V',200.66,99.06,fp='Capacitor_SMD:C_1210_3225Metric',fields={'MPN':'CL32B226KAJNNNE','Manufacturer':'Samsung Electro-Mechanics','LCSC':'C309062','Qualification':'Parallel output bank; combined corner/stability validation pending'})
wire((200.66,96.52),(200.66,sw[1]));wire((185.42,sw[1]),(200.66,sw[1]));junction((185.42,sw[1]));wire((200.66,101.6),(200.66,114.3));power('GND',(200.66,114.3),'#PWR414')
add('Device','R_Small_US','R401','100kR',63.5,109.22,fp='Resistor_SMD:R_0603_1608Metric',fields={'MPN':'RC0603FR-07100KL','Manufacturer':'Yageo','LCSC':'C14675','Tolerance':'1%','Power Rating':'0.1W'})
wire((63.5,106.68),(63.5,101.6));power('+3V3',(63.5,101.6),'#PWR412');wire((63.5,111.76),(63.5,116.84));label('AON_POWER_GOOD',(63.5,116.84))
# Flags describe external isolated input and buck output, not raw PoE.
add('power','PWR_FLAG','#FLG401','PWR_FLAG',63.5,63.5)
add('power','PWR_FLAG','#FLG402','PWR_FLAG',63.5,86.36)
add('power','PWR_FLAG','#FLG403','PWR_FLAG',185.42,sw[1])
note('Independent supervisor supply', (40.64,30.48),2.54)
note('DRAFT: isolated 12V input; 3.3V / 0.5A output. No connection to raw PoE.\\nEN tied to input; SLEEP tied to 3.3V for normal operation.\\nAlways on while the isolated input is present; downstream cuts must not gate this rail.',(40.64,137.16))
note('TI SLVSB35C, Figure 8 / Tables 2-3. 10uH + 2x22uF nominal.\\nCapacitor DC bias, complete rail load and layout review remain open.\\nRoute VOS as Kelvin sense after L401; join AGND / PGND / exposed pad locally.',(40.64,160.02))
items.insert(0,'(rectangle (start 35.56 40.64) (end 208.28 124.46) (stroke (width 0.254) (type default)) (fill (type none)) (uuid "'+uid('box')+'"))')
text='(kicad_sch (version 20250114) (generator eeschema) (uuid "'+uid('root')+'") (paper "A4") (title_block (title "Always-on supervisor supply") (date "2026-10-03") (rev "0.1-draft")) (lib_symbols '+'\n'.join(used.values())+')\n'+'\n'.join(items)+'\n(sheet_instances (path "/" (page "1"))))\n'
text=text.replace('(label "AON_POWER_GOOD" (at 76.2 91.44 0)', '(hierarchical_label "AON_POWER_GOOD" (shape output) (at 76.2 91.44 0)')
# Retain both standalone and integrated recovery annotation contexts.
recovery_root='37b14702-5d54-5543-b96e-899c36eac351'
recovery_sheet=str(uuid.uuid5(uuid.NAMESPACE_URL,'sierra-recovery-always-on-sheet'))
pattern=r'\(instances (\(project "always-on" \(path "[^"]+" \(reference "([^"]+)"\) \(unit 1\)\)\))\)'
text=re.sub(pattern,lambda m:f'(instances {m[1]} (project "recovery" (path "/{recovery_root}/{recovery_sheet}" (reference "{m[2]}") (unit 1))))',text)
(ROOT/'always-on.kicad_sch').write_text(text)
print('Generated',ROOT/'always-on.kicad_sch')
