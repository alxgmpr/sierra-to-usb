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
def label(name,p):
 if name in {'PMIC_I2C_SCL','PMIC_I2C_SDA','PMIC_SLEEP','VDD_LOGIC','VDD_GPU','VDD_NPU','VCC3V3_PMU','RK_RESET_N','VDDA0V9_PMU','VCCA1V8_PMU','VDDA_0V9','VCCA_1V8','PMIC_INT_N'}:
  items.append(f'(global_label "{name}" (shape passive) (at {p[0]} {p[1]} 0) (effects (font (size 1.27 1.27)) (justify right)) (uuid "{uid("global"+name+str(p))}"))');return
 if name in {'5V_MAIN','3V3_MAIN','GND'}:
  items.append(f'(global_label "{name}" (shape passive) (at {p[0]} {p[1]} 0) (effects (font (size 1.27 1.27)) (justify left)) (uuid "{uid("global"+name+str(p))}"))');return
 items.append(f'(label "{name}" (at {p[0]} {p[1]} 0) (effects (font (size 1.27 1.27)) (justify left bottom)) (uuid "{uid("label"+name+str(p))}"))')
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
 items.append(f'(symbol (lib_id "Recovery:RK809-5") (at {x} {y} 0) (unit {unit}) (in_bom yes) (on_board yes) (dnp no) (uuid "{uid("U501:unit:"+str(unit))}") '+fields+' '+''.join(f'(pin "{n}" (uuid "{uid("U501:"+n)}"))' for n in pins)+f' (instances (project "pmic" (path "/{uid("root")}" (reference "U501") (unit {unit})))))')
def terminal(n,net,direction):
 a=units[1][str(n)];b=(round(a[0]+direction*7.62,4),a[1]);wire(a,b);label(net,b)
 # Left-side label text must extend away from the body.
 if direction<0:items[-1]=items[-1].replace('(justify left bottom)','(justify right bottom)')
for n,net,d in [(10,'5V_MAIN',0),(11,'5V_MAIN',0),(9,'PMIC_SW2',1),(12,'PMIC_SW1',1),(8,'VDD_GPU',-1),(13,'VDD_LOGIC',-1),(53,'PMIC_SW5',1),(59,'VCC_1V8',-1),(65,'PMIC_SW4',1),(64,'NPU_FB',-1)]:
 if d:terminal(n,net,d)
 else:
  a=units[1][str(n)];b=(a[0],40.64);wire(a,b)
wire((88.9,40.64),(93.98,40.64));label("5V_MAIN",(88.9,40.64))
a=units[1]['54'];wire(a,(a[0],48.26));label('5V_MAIN',(a[0],48.26))
capfields={'MPN':'CL32B226KAJNNNE','Manufacturer':'Samsung Electro-Mechanics','LCSC':'C309062','Qualification':'Typical bias curve reviewed; combined-corner aging and loop stability pending'}
for channel,y,out,sense,cref in [(1,63.5,'VDD_LOGIC','VDD_LOGIC',501),(2,129.54,'VDD_GPU','VDD_GPU',505),(5,195.58,'VCC_1V8','VCC_1V8',509)]:
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
# NPU BUCK4: off at boot; software must program the intended voltage before enabling.
a=units[1]['66'];wire(a,(a[0],33.02));label('5V_MAIN',(a[0],33.02))
add('Device','C_Small','C533','22uF / 25V',365.76,47.32,fp='Capacitor_SMD:C_1210_3225Metric',fields=capfields)
wire((365.76,44.78),(365.76,35.56));label('5V_MAIN',(365.76,35.56));wire((365.76,49.86),(365.76,58.42));power('GND',(365.76,58.42),'#PWR540')
add('Device','L_Small','L504','0.47uH',398.78,35.56,90,fp='Inductor_SMD:L_Coilcraft_XxL4020',fields={'MPN':'XGL4020-471MEC','Manufacturer':'Coilcraft','LCSC':'C5837785'})
wire((383.54,35.56),(396.24,35.56));label('PMIC_SW4',(383.54,35.56))
wire((401.32,35.56),(492.76,35.56));label('VDD_NPU',(461.26,35.56))
for ref,x,value,fp,fields in [('C541',430.78,'22uF / 25V','Capacitor_SMD:C_1210_3225Metric',capfields),('C542',461.26,'10uF / 25V','Capacitor_SMD:C_1206_3216Metric',{'MPN':'CL31B106KAHNNNE','Manufacturer':'Samsung Electro-Mechanics','LCSC':'C14860','Qualification':'NPU output bank; effective capacitance and loop stability pending'})]:
 add('Device','C_Small',ref,value,x,48.26,fp=fp,fields=fields)
 wire((x,35.56),(x,45.72));wire((x,50.8),(x,58.42));junction((x,35.56))
wire((430.78,58.42),(461.26,58.42));power('GND',(430.78,58.42),'#PWR566')
add('Device','R_Small_US','R512','100R',492.76,48.26,fp='Resistor_SMD:R_0603_1608Metric',fields={'MPN':'RC0603FR-07100RL','Manufacturer':'Yageo','LCSC':'C105588','Tolerance':'1%','Power Rating':'0.1W','Qualification':'NPU remote sense series resistor; NanoPi R3S reference sheet 14'})
wire((492.76,35.56),(492.76,45.72));wire((492.76,50.8),(492.76,58.42));label('NPU_FB',(492.76,58.42))
note('NPU BUCK4: 1.5A; startup OFF. Program 0.9V before enable. Local load bypass pending.',(360.68,22.86))
# PMIC ground return and processor reset: pull up only to its fixed 3.3 V PMUIO1 domain.
for n in ['47','69']:
 a=units[3][n];wire(a,(a[0],279.4))
wire((99.06,279.4),(104.14,279.4));power('GND',(101.6,279.4),'#PWR520')
a=units[3]['67'];wire(a,(185.42,a[1]));label('RK_RESET_N',(185.42,a[1]));items[-1]=items[-1].replace('(justify left bottom)','(justify right bottom)')
add('Device','R_Small_US','R501','10kR',160.02,226.06,fp='Resistor_SMD:R_0603_1608Metric',fields={'MPN':'RC0603FR-0710KL','Manufacturer':'Yageo','LCSC':'C98220','Tolerance':'1%','Power Rating':'0.1W'})
wire((160.02,223.52),(160.02,215.9));label('VCC3V3_PMU',(160.02,215.9));wire((160.02,228.6),(160.02,a[1]));junction((160.02,a[1]))
add('Device','C_Small','C513','100nF / 25V',160.02,254,fp='Capacitor_SMD:C_0603_1608Metric',fields={'MPN':'CL10B104KA8NNNC','Manufacturer':'Samsung Electro-Mechanics','LCSC':'C1590','Qualification':'Place at RK3566 nPOR; reset assertion on brownout remains to verify'})
wire((160.02,a[1]),(160.02,251.46));wire((160.02,256.54),(160.02,269.24));power('GND',(160.02,269.24),'#PWR521')
# Reference nominal 1 uF RTC and VREF bypass capacitors; bias/corner margin remains explicit.
oneuf={'MPN':'CL10B105KA8NNNC','Manufacturer':'Samsung Electro-Mechanics','LCSC':'C29936','Qualification':'Manufacturer mass-production and bias curve reviewed; effective minimum pending'}
add('Device','C_Small','C514','1uF / 25V',50.8,215.9,fp='Capacitor_SMD:C_0603_1608Metric',fields=oneuf)
a=units[3]['45'];wire(a,(a[0],203.2));wire((50.8,203.2),(a[0],203.2));label('5V_MAIN',(50.8,203.2));wire((50.8,203.2),(50.8,213.36));wire((50.8,218.44),(50.8,223.52));power('GND',(50.8,223.52),'#PWR522')
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
 note(('LDO2: 0.9V / 400mA' if pin=='21' else 'LDO3: 0.9V / 100mA high PSRR')+'; load budget pending',(398.78,y+33.02 if pin=='21' else y-12.7))
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
 note(title+'; load budget pending',(398.78,y+33.02 if pin=='21' else y-12.7))
# I2C0 uses PMUIO2, selected as 3.3 V alongside PMUIO1; do not attach 5 V pull-ups.
for n,net in [('1','PMIC_I2C_SCL'),('2','PMIC_I2C_SDA')]:
 a=units[3][n];b=(a[0]-7.62,a[1]);wire(a,b);label(net,b);items[-1]=items[-1].replace('(justify left bottom)','(justify right bottom)')
for ref,x,net in [('R502',50.8,'PMIC_I2C_SCL'),('R503',88.9,'PMIC_I2C_SDA')]:
 add('Device','R_Small_US',ref,'2.2kR',x,320.04,fp='Resistor_SMD:R_0603_1608Metric',fields={'MPN':'RC0603FR-072K2L','Manufacturer':'Yageo','LCSC':'C114662','Tolerance':'1%','Power Rating':'0.1W','Voltage Rating':'75V'})
 wire((x,317.5),(x,309.88));wire((x,322.58),(x,330.2));label(net,(x,330.2))
wire((50.8,309.88),(88.9,309.88));label('VCC3V3_PMU',(50.8,309.88))
note('I2C0: 3.3V PMUIO2; 2.2kR pull-ups. Capacitance and firmware speed review pending.',(35.56,345.44))
# Interrupt is active-low open drain; its processor input must use the 3.3 V PMU domain.
a=units[3]['7'];b=(a[0]+7.62,a[1]);wire(a,b);label('PMIC_INT_N',b)
add('Device','R_Small_US','R504','10kR',127,320.04,fp='Resistor_SMD:R_0603_1608Metric',fields={'MPN':'RC0603FR-0710KL','Manufacturer':'Yageo','LCSC':'C98220','Tolerance':'1%','Power Rating':'0.1W','Voltage Rating':'75V'})
wire((127,317.5),(127,309.88));wire((88.9,309.88),(127,309.88));junction((88.9,309.88));wire((127,322.58),(127,330.2));label('PMIC_INT_N',(127,330.2))
# Sleep is active high by reset default; hold low while host pin is high impedance.
a=units[3]['49'];b=(a[0]-7.62,a[1]);wire(a,b);label('PMIC_SLEEP',b);items[-1]=items[-1].replace('(justify left bottom)','(justify right bottom)')
add('Device','R_Small_US','R505','10kR',185.42,320.04,fp='Resistor_SMD:R_0603_1608Metric',fields={'MPN':'RC0603FR-0710KL','Manufacturer':'Yageo','LCSC':'C98220','Tolerance':'1%','Power Rating':'0.1W','Voltage Rating':'75V'})
wire((185.42,317.5),(185.42,309.88));label('PMIC_SLEEP',(185.42,309.88));wire((185.42,322.58),(185.42,330.2));power('GND',(185.42,330.2),'#PWR550')
# VDC rising-edge startup sensing, referenced to main 5 V rather than raw PoE.
a=units[3]['61'];b=(a[0]-7.62,a[1]);wire(a,b);label('PMIC_VDC',b);items[-1]=items[-1].replace('(justify left bottom)','(justify right bottom)')
for ref,y in [('R506',307.34),('R507',330.2)]:
 add('Device','R_Small_US',ref,'100kR',260.35,y,fp='Resistor_SMD:R_0603_1608Metric',fields={'MPN':'RC0603FR-07100KL','Manufacturer':'Yageo','LCSC':'C14675','Tolerance':'1%','Power Rating':'0.1W','Voltage Rating':'75V'})
wire((260.35,304.8),(260.35,294.64));label('5V_MAIN',(260.35,294.64))
wire((260.35,309.88),(260.35,327.66));junction((260.35,320.04));wire((260.35,320.04),(335.28,320.04));label('PMIC_VDC',(335.28,320.04))
add('Device','C_Small','C531','100nF / 25V',335.28,330.2,fp='Capacitor_SMD:C_0603_1608Metric',fields={'MPN':'CL10B104KA8NNNC','Manufacturer':'Samsung Electro-Mechanics','LCSC':'C1590','Qualification':'VDC filter and startup ramp verification pending'})
wire((335.28,320.04),(335.28,327.66));wire((335.28,332.74),(335.28,340.36));wire((260.35,332.74),(260.35,340.36));wire((260.35,340.36),(335.28,340.36));power('GND',(279.4,340.36),'#PWR551')
note('VDC: 100kR / 100kR, 100nF; nominal 2.5V at main 5V. Startup timing pending.',(241.3,355.6))
# PWRON has its own internal pull-up to 5 V RTC; external control must sink only.
a=units[3]['52'];b=(a[0]-7.62,a[1]);wire(a,b);label('PMIC_PWRON_N',b);items[-1]=items[-1].replace('(justify left bottom)','(justify right bottom)')
add('Device','C_Small','C532','100nF / 25V',50.8,368.3,fp='Capacitor_SMD:C_0603_1608Metric',fields={'MPN':'CL10B104KA8NNNC','Manufacturer':'Samsung Electro-Mechanics','LCSC':'C1590','Qualification':'PWRON pulse timing and open-drain recovery interface pending'})
wire((50.8,365.76),(50.8,355.6));label('PMIC_PWRON_N',(50.8,355.6));wire((50.8,370.84),(50.8,378.46));power('GND',(50.8,378.46),'#PWR552')
note('PWRON: internal 35kR pull-up to 5V RTC. Open-drain control required.',(76.2,403.86))
# Reuse the already-resolved recovery transistor symbol, preserving manufacturer pad mapping.
controls=(ROOT/'controls.kicad_sch').read_text()
used['Transistor_BJT:MMBT3904']=block(controls,controls.index('(symbol "Transistor_BJT:MMBT3904"'))
qpins=add('Transistor_BJT','MMBT3904','Q501','MMBT3904,215',127,368.3,fp='Package_TO_SOT_SMD:SOT-23',fields={'MPN':'MMBT3904,215','Manufacturer':'Nexperia','Datasheet':'https://assets.nexperia.com/documents/data-sheet/MMBT3904.pdf'})
assert qpins=={'1':(-5.08,0.0),'2':(2.54,-5.08),'3':(2.54,5.08)},qpins
wire((129.54,363.22),(129.54,355.6));label('PMIC_PWRON_N',(129.54,355.6));wire((129.54,373.38),(129.54,378.46));power('GND',(129.54,378.46),'#PWR553')
add('Device','R_Small_US','R508','10kR',101.6,368.3,90,fp='Resistor_SMD:R_0603_1608Metric',fields={'MPN':'RC0603FR-0710KL','Manufacturer':'Yageo','LCSC':'C98220','Tolerance':'1%','Power Rating':'0.1W'})
items[-1]=re.sub(r'(\(property "Reference" "R508" \(at )[^)]+',r'\g<1>101.6 360.68 90',items[-1])
items[-1]=re.sub(r'(\(property "Value" "10kR" \(at )[^)]+',r'\g<1>101.6 363.22 90',items[-1])
wire((86.36,368.3),(99.06,368.3));items.append(f'(global_label "MCU_PWRON_KICK" (shape input) (at 86.36 368.3 0) (effects (font (size 1.27 1.27)) (justify left)) (uuid "{uid("kick-global")}"))');wire((104.14,368.3),(121.92,368.3))
add('Device','R_Small_US','R509','100kR',114.3,386.08,fp='Resistor_SMD:R_0603_1608Metric',fields={'MPN':'RC0603FR-07100KL','Manufacturer':'Yageo','LCSC':'C14675','Tolerance':'1%','Power Rating':'0.1W'})
wire((114.3,368.3),(114.3,383.54));junction((114.3,368.3));wire((114.3,388.62),(114.3,393.7));power('GND',(114.3,393.7),'#PWR554')
# Internal headphone supply bypass, following RK809 Figure 1-2.
add('Device','C_Small','C534','1uF / 25V',330.2,290.83,fp='Capacitor_SMD:C_0603_1608Metric',fields=oneuf)
a=units[4]['38'];b=(a[0],a[1]-7.62);wire(a,b);label('PMIC_INTERNAL_CPVDD',b)
wire((330.2,288.29),(330.2,278.13));label('PMIC_INTERNAL_CPVDD',(330.2,278.13))
wire((330.2,293.37),(330.2,300.99));power('GND',(330.2,300.99),'#PWR555')
# Internal analog/digital 1.8 V LDO outputs: individual bypasses, never external feeds.
for pin,ref,name,x,pwr in [('44','C535','PMIC_INTERNAL_1V8A',330.2,'#PWR556'),('48','C536','PMIC_INTERNAL_1V8D',358.14,'#PWR557')]:
 a=units[4][pin];b=(a[0]+12.7,a[1]);wire(a,b);label(name,b)
 add('Device','C_Small',ref,'1uF / 25V',x,250.19,fp='Capacitor_SMD:C_0603_1608Metric',fields=oneuf)
 wire((x,247.65),(x,237.49));label(name,(x,237.49))
 wire((x,252.73),(x,260.35));power('GND',(x,260.35),pwr)
# No-battery reference: unused current-sense inputs share ground (Figure 1-2).
for pin in ['62','63']:
 a=units[3][pin];wire(a,(60.96,a[1]))
wire((60.96,254),(60.96,256.54));junction((60.96,256.54))
wire((60.96,256.54),(60.96,264.16));power('GND',(60.96,264.16),'#PWR558')
# Headphone reference return is ground, not a supply output.
a=units[4]['40'];wire(a,(a[0],279.4));power('GND',(a[0],279.4),'#PWR559')
# Preserve the manufacturer's speaker/charge-pump input supply and bypass.
a=units[4]['33'];b=(a[0],213.36);wire(a,b);label('5V_MAIN',b)
items[-1]=items[-1].replace('(justify left)','(justify right)')
add('Device','C_Small','C537','10uF / 50V',358.14,290.83,fp='Capacitor_SMD:C_1206_3216Metric',fields={'MPN':'CL31B106KBHNNNE','Manufacturer':'Samsung Electro-Mechanics','LCSC':'C89632','Dielectric':'X7R','Qualification':'Speaker/charge-pump supply bypass; unused audio policy pending'})
wire((358.14,288.29),(358.14,278.13));label('5V_MAIN',(358.14,278.13))
wire((358.14,293.37),(358.14,300.99));power('GND',(358.14,300.99),'#PWR560')
# Switch2 electrical range is 2.7–5 V: use main 3.3 V, not our 1.8 V BUCK5.
a=units[1]['57'];wire(a,(a[0],50.8));wire((a[0],50.8),(134.62,50.8));label('3V3_MAIN',(134.62,50.8))
add('Device','C_Small','C538','1uF / 25V',154.94,104.14,fp='Capacitor_SMD:C_0603_1608Metric',fields=oneuf)
wire((154.94,101.6),(154.94,93.98));label('3V3_MAIN',(154.94,93.98))
wire((154.94,106.68),(154.94,114.3));power('GND',(154.94,114.3),'#PWR561')
# RK809 Figure 1-2: 2.2 uF flying capacitor and negative-rail bypass.
for pin,name in [('36','PMIC_CPN'),('37','PMIC_CPP')]:
 a=units[4][pin];b=(a[0]-7.62,a[1]);wire(a,b);label(name,b)
 items[-1]=items[-1].replace('(justify left bottom)','(justify right bottom)')
a=units[4]['35'];b=(a[0]+12.7,a[1]);wire(a,b);label('PMIC_INTERNAL_CPVSS',b)
cpfields={'MPN':'CL31B225KBHNNNE','Manufacturer':'Samsung Electro-Mechanics','LCSC':'C50254','Dielectric':'X7R','Tolerance':'10%','Qualification':'Reference nominal charge-pump capacitance; effective corner and startup pending'}
add('Device','C_Small','C539','2.2uF / 50V',500.38,250.19,fp='Capacitor_SMD:C_1206_3216Metric',fields=cpfields)
wire((500.38,247.65),(500.38,237.49));label('PMIC_CPP',(500.38,237.49))
wire((500.38,252.73),(500.38,262.89));label('PMIC_CPN',(500.38,262.89))
add('Device','C_Small','C540','2.2uF / 50V',500.38,290.83,fp='Capacitor_SMD:C_1206_3216Metric',fields=cpfields)
wire((500.38,288.29),(500.38,278.13));label('PMIC_INTERNAL_CPVSS',(500.38,278.13))
wire((500.38,293.37),(500.38,300.99));power('GND',(500.38,300.99),'#PWR562')
# Unused codec: fixed inputs MCLK/SDI grounded; mode-dependent clocks weakly held low.
for pin in ['16','17']:
 a=units[4][pin];b=(a[0]-7.62,a[1]);wire(a,b);label('GND',b)
 items[-1]=items[-1].replace('(justify left bottom)','(justify right bottom)').replace('(justify left)','(justify right)')
wire((457.2,320.04),(457.2,327.66));label('GND',(457.2,320.04));power('GND',(457.2,327.66),'#PWR563')
for pin,ref,name,x,pwr in [('14','R510','UNUSED_CODEC_LRCLK',457.2,'#PWR564'),('15','R511','UNUSED_CODEC_BCLK',500.38,'#PWR565')]:
 a=units[4][pin];b=(a[0]-7.62,a[1]);wire(a,b);label(name,b)
 items[-1]=items[-1].replace('(justify left bottom)','(justify right bottom)')
 add('Device','R_Small_US',ref,'10kR',x,355.6,fp='Resistor_SMD:R_0603_1608Metric',fields={'MPN':'RC0603FR-0710KL','Manufacturer':'Yageo','LCSC':'C98220','Tolerance':'1%','Power Rating':'0.1W'})
 wire((x,353.06),(x,345.44));label(name,(x,345.44))
 wire((x,358.14),(x,365.76));power('GND',(x,365.76),pwr)
for pin in ['18','19','32','34','39','41','42','43']:
 a=units[4][pin];items.append(f'(no_connect (at {a[0]} {a[1]}) (uuid "{uid("unused-codec-"+pin)}"))')
note('PMIC capture in progress — buck / analog / IO rails',(35.56,22.86),2.54)
note('DRAFT: other rails and management/audio pins are deliberately unwired.\\nNo complete ERC or appliance BOM claim. Do not use for fabrication.\\nFeedback sense must route to processor load; verify ground return and placement.',(241.3,375.92))
text='(kicad_sch (version 20250114) (generator eeschema) (uuid "'+uid('root')+'") (paper "A2") (title_block (title "PMIC capture draft") (date "2026-10-03") (rev "0.1-draft")) (lib_symbols '+'\n'.join(used.values())+')\n'+'\n'.join(items)+'\n(sheet_instances (path "/" (page "1"))))\n'
(ROOT/'pmic.kicad_sch').write_text(text)
print('Generated PMIC draft; all 69 pins retained, unfinished pins intentionally visible.')
