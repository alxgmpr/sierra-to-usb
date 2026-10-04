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
for unit,x,y in [(1,101.6,81.28),(2,101.6,165.1),(3,101.6,248.92),(4,238.76,248.92)]:
 u=block(s,s.index(f'(symbol "RK809-5_{unit}_1"'))
 pins={n:(round(x+float(px),4),round(y-float(py),4)) for px,py,n in re.findall(r'\(pin .*?\(at ([\d.\-]+) ([\d.\-]+) [\d.\-]+\).*?\(number "([^"]+)"',u,re.S)}
 units[unit]=pins
 fields=prop('Reference','U501',x-25.4,y-30.48)+prop('Value','RK809-5',x-25.4,y-27.94)+prop('Footprint',fp,x,y,True)+prop('MPN','RK809-5',x,y,True)+prop('Manufacturer','Rockchip',x,y,True)+prop('LCSC','C2939628',x,y,True)
 items.append(f'(symbol (lib_id "Recovery:RK809-5") (at {x} {y} 0) (unit {unit}) (in_bom yes) (on_board yes) (dnp no) (uuid "{uid("U501:"+str(unit))}") '+fields+' '+''.join(f'(pin "{n}" (uuid "{uid("U501:"+n)}"))' for n in pins)+f' (instances (project "pmic" (path "/{uid("root")}" (reference "U501") (unit {unit})))))')
def terminal(n,net,direction):
 a=units[1][str(n)];b=(round(a[0]+direction*7.62,4),a[1]);wire(a,b);label(net,b)
 # Left-side label text must extend away from the body.
 if direction<0:items[-1]=items[-1].replace('(justify left bottom)','(justify right bottom)')
for n,net,d in [(10,'5V_MAIN',0),(11,'5V_MAIN',0),(9,'PMIC_SW2',1),(12,'PMIC_SW1',1),(8,'VDD_GPU_SENSE',-1),(13,'VDD_LOGIC_SENSE',-1),(53,'PMIC_SW5',1),(59,'VCC_1V8_SENSE',-1)]:
 if d:terminal(n,net,d)
 else:
  a=units[1][str(n)];b=(a[0],40.64);wire(a,b)
wire((88.9,40.64),(93.98,40.64));label("5V_MAIN",(88.9,40.64))
a=units[1]['54'];wire(a,(a[0],48.26));label('5V_MAIN',(a[0],48.26))
capfields={'MPN':'CL32B226KAJNNNE','Manufacturer':'Samsung Electro-Mechanics','LCSC':'C309062','Qualification':'Typical bias curve reviewed; combined-corner aging and loop stability pending'}
for channel,y,out,sense,cref in [(1,63.5,'VDD_LOGIC','VDD_LOGIC_SENSE',501),(2,129.54,'VDD_GPU','VDD_GPU_SENSE',505),(5,195.58,'VCC_1V8','VCC_1V8_SENSE',509)]:
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
 note(f'BUCK{channel}: '+('1.8V' if channel==5 else '0.9V')+' startup / 2.5A rated; 3 x 22uF output bank',(223.52 if channel==5 else 175.26,y-12.7))
# PMIC ground return and processor reset: pull up only to its fixed 3.3 V PMUIO1 domain.
for n in ['47','69']:
 a=units[3][n];wire(a,(a[0],279.4))
wire((99.06,279.4),(104.14,279.4));power('GND',(101.6,279.4),'#PWR520')
a=units[3]['67'];wire(a,(185.42,a[1]));label('RK_RESET_N',(185.42,a[1]))
add('Device','R_Small_US','R501','10kR',160.02,226.06,fp='Resistor_SMD:R_0603_1608Metric',fields={'MPN':'RC0603FR-0710KL','Manufacturer':'Yageo','LCSC':'C98220','Tolerance':'1%','Power Rating':'0.1W'})
wire((160.02,223.52),(160.02,215.9));label('VCC3V3_PMU',(160.02,215.9));wire((160.02,228.6),(160.02,a[1]));junction((160.02,a[1]))
add('Device','C_Small','C513','100nF / 25V',160.02,254,fp='Capacitor_SMD:C_0603_1608Metric',fields={'MPN':'CL10B104KA8NNNC','Manufacturer':'Samsung Electro-Mechanics','LCSC':'C1590','Qualification':'Place at RK3566 nPOR; reset assertion on brownout remains to verify'})
wire((160.02,a[1]),(160.02,251.46));wire((160.02,256.54),(160.02,269.24));power('GND',(160.02,269.24),'#PWR521')
# Reference nominal 1 uF RTC and VREF bypass capacitors; bias/corner margin remains explicit.
oneuf={'MPN':'CL10B105KA8NNNC','Manufacturer':'Samsung Electro-Mechanics','LCSC':'C29936','Qualification':'Manufacturer mass-production and bias curve reviewed; effective minimum pending'}
add('Device','C_Small','C514','1uF / 25V',50.8,215.9,fp='Capacitor_SMD:C_0603_1608Metric',fields=oneuf)
a=units[3]['45'];wire(a,(a[0],203.2));wire((50.8,203.2),(a[0],203.2));label('5V_MAIN',(50.8,203.2));wire((50.8,203.2),(50.8,213.36));wire((50.8,218.44),(50.8,228.6));power('GND',(50.8,228.6),'#PWR522')
add('Device','C_Small','C515','1uF / 25V',185.42,269.24,fp='Capacitor_SMD:C_0603_1608Metric',fields=oneuf)
a=units[3]['46'];wire(a,(185.42,a[1]));wire((185.42,a[1]),(185.42,266.7));wire((185.42,271.78),(185.42,281.94));power('GND',(185.42,281.94),'#PWR523')
# Feed the 3.3 V LDO bank from 5 V: the stated load ratings require headroom.
a=units[2]['30'];wire(a,(a[0],116.84));wire((50.8,116.84),(a[0],116.84));label('5V_MAIN',(50.8,116.84))
add('Device','C_Small','C516','22uF / 25V',50.8,129.54,fp='Capacitor_SMD:C_1210_3225Metric',fields=capfields)
wire((50.8,116.84),(50.8,127));wire((50.8,132.08),(50.8,139.7));power('GND',(50.8,139.7),'#PWR524')
a=units[2]['31'];wire(a,(193.04,a[1]));label('VCC3V3_PMU',(193.04,a[1]))
for ref,x in [('C517',160.02),('C518',185.42)]:
 add('Device','C_Small',ref,'1uF / 25V',x,182.88,fp='Capacitor_SMD:C_0603_1608Metric',fields=oneuf)
 wire((x,a[1]),(x,180.34));junction((x,a[1]));wire((x,185.42),(x,190.5))
wire((160.02,190.5),(185.42,190.5));power('GND',(172.72,190.5),'#PWR525')
# Analog 0.9 V domains share VCC5 input, but must remain distinct outputs.
a=units[2]['22'];wire(a,(a[0],134.62));label('3V3_MAIN',(a[0],134.62))
add('Device','C_Small','C519','22uF / 25V',50.8,165.1,fp='Capacitor_SMD:C_1210_3225Metric',fields=capfields)
wire((50.8,162.56),(50.8,152.4));label('3V3_MAIN',(50.8,152.4));wire((50.8,167.64),(50.8,175.26));power('GND',(50.8,175.26),'#PWR526')
for pin,net,y,cref in [('21','VDDA_0V9',63.5,520),('20','VDDA0V9_PMU',129.54,522)]:
 a=units[2][pin];b=(a[0]+7.62,a[1]);wire(a,b);label(net,b)
 wire((419.1,y),(449.58,y));label(net,(419.1,y))
 for j,x in enumerate([419.1,449.58]):
  add('Device','C_Small',f'C{cref+j}','1uF / 25V',x,y+12.7,fp='Capacitor_SMD:C_0603_1608Metric',fields=oneuf)
  wire((x,y),(x,y+10.16));wire((x,y+15.24),(x,y+22.86))
 wire((419.1,y+22.86),(449.58,y+22.86));power('GND',(434.34,y+22.86),f'#PWR{cref+10}')
 note(('LDO2: 0.9V / 400mA' if pin=='21' else 'LDO3: 0.9V / 100mA high PSRR')+'; load budget pending',(398.78,y-12.7))
# Separate analog 1.8 V rails and adjustable SD IO domain.
a=units[2]['4'];wire(a,(a[0],127));label('3V3_MAIN',(a[0],127))
add('Device','C_Small','C524','22uF / 25V',50.8,91.44,fp='Capacitor_SMD:C_1210_3225Metric',fields=capfields)
wire((50.8,88.9),(50.8,78.74));label('3V3_MAIN',(50.8,78.74));wire((50.8,93.98),(50.8,101.6));power('GND',(50.8,101.6),'#PWR534')
for pin,net,y,cref,title in [('3','VCCA1V8_PMU',195.58,525,'LDO7: 1.8V / slot 2'),('5','VCCA_1V8',261.62,527,'LDO8: 1.8V / slot 2'),('29','VCCIO_SD',327.66,529,'LDO5: 3.3V startup / slot 4; SD IO adjustable')]:
 a=units[2][pin];b=(a[0]+7.62,a[1]);wire(a,b);label(net,b)
 wire((419.1,y),(449.58,y));label(net,(419.1,y))
 for j,x in enumerate([419.1,449.58]):
  add('Device','C_Small',f'C{cref+j}','1uF / 25V',x,y+12.7,fp='Capacitor_SMD:C_0603_1608Metric',fields=oneuf)
  wire((x,y),(x,y+10.16));wire((x,y+15.24),(x,y+22.86))
 wire((419.1,y+22.86),(449.58,y+22.86));power('GND',(434.34,y+22.86),f'#PWR{cref+10}')
 note(title+'; load budget pending',(398.78,y-12.7))
note('PMIC capture in progress — buck / analog / IO rails',(35.56,22.86),2.54)
note('DRAFT: other rails and management/audio pins are deliberately unwired.\\nNo complete ERC or appliance BOM claim. Do not use for fabrication.\\nFeedback sense must route to processor load; verify ground return and placement.',(35.56,31.75))
text='(kicad_sch (version 20250114) (generator eeschema) (uuid "'+uid('root')+'") (paper "A2") (title_block (title "PMIC capture draft") (date "2026-10-03") (rev "0.1-draft")) (lib_symbols '+'\n'.join(used.values())+')\n'+'\n'.join(items)+'\n(sheet_instances (path "/" (page "1"))))\n'
(ROOT/'pmic.kicad_sch').write_text(text)
print('Generated PMIC draft; all 69 pins retained, unfinished pins intentionally visible.')
