#!/usr/bin/env python3
"""Carry PoE allocation to always-on MCU without crossing the isolation barrier."""
from capture import ROOT, Sheet, grouped, native_pins, children, block
import re
pins=native_pins(ROOT/'reference/sierra-opto-native.kicad_sym','TLP293')
assert pins=={'1':'Anode','2':'Cathode','3':'Emitter','4':'Collector'}
sym=grouped('TLP293_GB',pins,[{'left':['1','2'],'right':['4','3']}],{'1':'passive','2':'passive','3':'passive','4':'open_collector'})
s=Sheet('poe-status','Isolated PoE allocation — supervisor inputs','A3')
for i,signal in enumerate(['TPH','TPL','BT']):
 y=63.5+71.12*i
 p=s.symbol('Appliance:TLP293_GB',sym,f'U{1801+i}','TLP293(GB-TPL,E)',190.5,y,'Appliance:SOP-4_L4.4-W2.8-P1.27-LS7.0-BR',{'MPN':'TLP293(GB-TPL,E)','Manufacturer':'Toshiba','LCSC':'C77656','Datasheet':'https://toshiba.semicon-storage.com/info/docget.jsp?did=14419&prodName=TLP293','CTR Rank':'GB (100% min at IF=0.5mA, VCE=5V, Ta=25C)','Isolation':'3750Vrms component rating; PCB creepage and assembly still require review'})
 s.attach(p,{'1':f'POE_{signal}_LED_A','2':f'POE_{signal}','3':'GND','4':f'POE_{signal}_N'})
 s.resistor(f'R{1801+i}','6.8kR',83.82,y,'POE_VCOUT',f'POE_{signal}_LED_A','RC0603FR-076K8L')
 s.resistor(f'R{1811+i}','12kR',284.48,y,'+3V3',f'POE_{signal}_N','RC0603FR-0712KL')
 s.passive('C',f'C{1801+i}','10nF',353.06,y,f'POE_{signal}_N','GND','CL10B103KB8NNNC','Capacitor_SMD:C_0603_1608Metric','Samsung Electro-Mechanics',{'Voltage Rating':'50V','Dielectric':'X7R'})
s.note('Primary LEDs are driven by TPS2373 open-drain outputs referenced to POE_RTN.\nSecondary outputs: PB10 / PB11 / PB12 (MCU pads 22 / 23 / 24), active low.\nClass 6 grant: TPH_N=0, TPL_N=1, BT_N=0, stable after startup.\nReject all other combinations. Keep MAIN5V, modem and Ethernet power off until grant.\n6.8k limits each LED to <2.3mA at 15V; TPS2373 recommended sink <=3mA.\n12k collector pull-up and 10nF filter. Verify CTR/leakage at -40 to 85C and bias corners.\nAll-high also means unpowered / invalid status. Loss of grant cuts main loads.\nDo not join POE_RTN, POE_VSS or POE_VDD to secondary GND.',25.4,256.54)
s.save()
(ROOT/'reference/tlp293-captured.kicad_sym').write_text('(kicad_symbol_lib (version 20211014) (generator eeschema) '+sym+')\n')
# Upgrade the existing MCU capture in place, preserving user-visible geometry and context.
p=ROOT/'supervisor.kicad_sch';raw=p.read_text();library=next(i for i in children(raw) if i.startswith('(lib_symbols'));body=next(i for i in children(library) if i.startswith('(symbol "MCU_ST'))
instance=next(i for i in children(raw) if i.startswith('(symbol') and '(lib_id "MCU_ST' in i);x,y,a=map(float,re.search(r'\(at ([^()]+)',instance)[1].split())
points=Sheet('tmp','').symbol('MCU',body,'U201','',x,y,angle=a)
patch=Sheet('supervisor-status','')
for number,signal in [('22','TPH'),('23','TPL'),('24','BT')]:
 x,y,angle=points[number]
 for item in children(raw):
  if item.startswith('(no_connect'):
   at=re.search(r'\(at ([^()]+)',item)[1].split()
   if abs(float(at[0])-x)<.0001 and abs(float(at[1])-y)<.0001:raw=raw.replace(item,'')
 patch.wire((x,y),(x+12.7,y));patch.net(f'POE_{signal}_N',(x+12.7,y),180)
for item in patch.items:
 if item not in raw:raw=raw.rstrip()[:-1]+item+')\n'
p.write_text("\n".join(line.rstrip() for line in raw.splitlines())+"\n")
