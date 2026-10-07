#!/usr/bin/env python3
"""B-key modem socket, mutually exclusive assembly straps, SIM and USB isolation."""
import re
from capture import ROOT, Sheet, stock, grouped, native_pins, block, children

def dnp(sheet, ref):
    for i,item in enumerate(sheet.items):
        if item.startswith('(symbol') and f'(property "Reference" "{ref}"' in item:
            sheet.items[i]=item.replace('(dnp no)','(dnp yes)')

s=Sheet('modem-socket','Modem socket and SIM — assembly profiles required','A1')
# PCI-SIG B-key contact numbering; retain all 67 contacts, including every unused pin.
pins={str(n):str(n) for n in range(1,76) if n not in range(12,20)}
assert set(pins)==set(native_pins(ROOT/'reference/modem-C590866-native.kicad_sym','2199119-3'))-{'76','77'}
power=['2','4','70','72','74'];grounds=['3','5','11','27','33','39','45','51','57','71','73']
left=['6','67','20','22','24','38','68','30','32','34','36']
right=['7','9','29','31','35','37']
names={'6':'FULL_CARD_POWER_OFF_N','67':'RESET_N','20':'PCIE_DIS / RESERVED','22':'VBUS_SENSE / RESERVED','24':'VCC / 1V8_OUT','38':'VCC / WLAN_DISABLE','68':'VCC / RESERVED','30':'SIM1_RESET','32':'SIM1_CLK','34':'SIM1_DATA','36':'SIM1_VCC','7':'USB_DP','9':'USB_DM','29':'USB_TXN','31':'USB_TXP','35':'USB_RXN','37':'USB_RXP'}
pins.update(names);pins.update({n:'VCC' for n in power});pins.update({n:'GND' for n in grounds})
remaining=sorted(set(pins)-set(power+grounds+left+right),key=int)
body=grouped('M2_B_67',pins,[{'top':power,'bottom':grounds,'left':left,'right':right},{'left':remaining[::2],'right':remaining[1::2]}],{n:'passive' for n in pins})
nets={n:None for n in pins};nets.update({n:'MODEM_VCC' for n in power});nets.update({n:'GND' for n in grounds})
nets.update({'6':'MODEM_OFF_N','67':'MODEM_RESET_N','20':'M2_PIN20','22':'M2_PIN22','24':'M2_PIN24','38':'M2_PIN38','68':'M2_PIN68','30':'SIM1_RESET_MODEM','32':'SIM1_CLK_MODEM','34':'SIM1_DATA_MODEM','36':'SIM1_VCC','7':'MODEM_USB_DP_PORT','9':'MODEM_USB_DM_PORT','29':'MODEM_TXN_PORT','31':'MODEM_TXP_PORT','35':'MODEM_RXN_PORT','37':'MODEM_RXP_PORT'})
for unit,x in [(1,137.16),(2,464.82)]:
    p=s.symbol('Appliance:M2_B_67',body,'J2001','MDT420B01411',x,86.36,'',{'MPN':'MDT420B01411','Manufacturer':'Amphenol Communications Solutions','Datasheet':'https://www.amphenol-cs.com/product/mdt420b01411.html','Contact Rating':'1A/power contact continuous at 25C, <=30C rise; hot derating and sharing require qualification','Footprint Hold':'Exact CMDT420X0X411 Rev A land pattern and retention pads required; do not reuse TE 2199119 footprint'},unit=unit)
    s.attach(p,{n:nets[n] for n in p})
# Safe default: all five Sierra-only links absent. Populate ONLY after exact module review.
for i,pin in enumerate(['24','38','68']):
    ref=f'R{2011+i}';s.passive('R',ref,'0R SIERRA ONLY / DNP',241.3,50.8+50.8*i,'MODEM_VCC',f'M2_PIN{pin}','RC0603JR-070RL','Resistor_SMD:R_0603_1608Metric','Yageo',{'Tolerance':'5%','Power Rating':'0.1W','Assembly Profile':'Sierra only; OMIT for every Quectel profile'},horizontal=True);dnp(s,ref)
s.resistor('R2014','10kR',370.84,55.88,'MODEM_VCC','SIERRA_USB_SELECT_1V8','RC0603FR-0710KL')
s.resistor('R2015','10kR',370.84,111.76,'SIERRA_USB_SELECT_1V8','GND','RC0603FR-0710KL')
for ref,first,second,y in [('R2016','SIERRA_USB_SELECT_1V8','M2_PIN20',203.2),('R2017','MODEM_VCC','M2_PIN22',254)]:
    s.passive('R',ref,'0R SIERRA ONLY / DNP',241.3,y,first,second,'RC0603JR-070RL','Resistor_SMD:R_0603_1608Metric','Yageo',{'Tolerance':'5%','Assembly Profile':'Sierra USB: populate. Quectel: omit; reserved pins stay floating'},horizontal=True);dnp(s,ref)
s.resistor('R2018','100kR',53.34,203.2,'MODEM_VCC','MODEM_OFF_N','RC0603FR-07100KL')
s.note('Default assembly: R2011/12/13/16/17 DNP (Quectel). NEVER feed Quectel pins 24,38,68.\nSierra USB profile: fit all five links; pins 24/38/68 add VCC, 20 selects USB, 22 detects VBUS.\nPin 20 divider is powered by modem VCC; include module pulldown in level verification.\nRESET uses module internal 1.8V pull-up; Q301/Q302 only sink reset/power-off signals.\nAll unused PCIe, coexistence, SIM2, antenna control and configuration contacts float.\nNo host drive before valid rail delay. No mmWave antenna power hardware is captured.\nEvery profile remains on release hold pending current controlled module guide and power envelope.',25.4,335.28)
# Nano-SIM, no hot insertion. Native auxiliary contacts 7/8 are unused.
sp=native_pins(ROOT/'reference/modem-C585349-native.kicad_sym','1042240820')
assert sp=={'1':'VCC','2':'RST','3':'CLK','4':'GND','5':'VPP','6':'I/O','7':'NC','8':'NC','9':'SHELL','10':'SHELL','11':'SHELL','12':'SHELL'}
sim=grouped('NANO_SIM_1042240820',sp,[{'left':['1','2','3','6','5','7','8'],'bottom':['4','9','10','11','12']}],{n:'passive' for n in sp})
p=s.symbol('Appliance:NANO_SIM_1042240820',sim,'J2002','1042240820',421.64,238.76,'Appliance:SIM-SMD_1042240820',{'MPN':'1042240820','Manufacturer':'Molex','LCSC':'C585349','Datasheet':'https://www.molex.com/content/dam/molex/molex-dot-com/products/automated/en-us/salesdrawingpdf/104/104224/1042240820_sd.pdf','Temperature Range':'-25 to +85C; broader product range requires alternate connector','Usage':'Insert/remove only with modem off; SIM detect disabled; auxiliary contacts 7/8 unused'})
s.attach(p,{'1':'SIM1_VCC','2':'SIM1_RESET','3':'SIM1_CLK','4':'GND','5':None,'6':'SIM1_DATA','7':None,'8':None,'9':'GND','10':'GND','11':'GND','12':'GND'})
for i,(name,y) in enumerate([('RESET',411.48),('CLK',462.28),('DATA',513.08)]):
    s.resistor(f'R{2021+i}','22R',63.5,y,f'SIM1_{name}_MODEM',f'SIM1_{name}','RC0603FR-0722RL',horizontal=True)
    s.passive('C',f'C{2021+i}','10pF',223.52,y,f'SIM1_{name}','GND','CL10C100JB8NNNC','Capacitor_SMD:C_0603_1608Metric','Samsung Electro-Mechanics',{'Voltage Rating':'50V','Dielectric':'C0G'})
s.resistor('R2024','15kR',142.24,411.48,'SIM1_VCC','SIM1_DATA','RC0603FR-0715KL')
s.cap('C2024','100nF',142.24,482.6,'SIM1_VCC')
raw=(ROOT/'reference/tpd4e02b04-captured.kicad_sym').read_text();esd=block(raw,raw.index('(symbol "TPD4E02B04_DQA"'))
p=s.symbol('Appliance:TPD4E02B04_DQA',esd,'D2001','TPD4E02B04DQAR',421.64,454.66,'Appliance:USON-10_L2.5-W1.0-P0.50-BL',{'MPN':'TPD4E02B04DQAR','Manufacturer':'Texas Instruments','LCSC':'C106794','Datasheet':'https://www.ti.com/lit/ds/symlink/tpd4e02b04.pdf','Placement':'At SIM contacts, short ground return'})
s.attach(p,{'1':'SIM1_RESET','2':'SIM1_CLK','3':'GND','4':'SIM1_DATA','5':'SIM1_VCC','6':None,'7':None,'8':'GND','9':None,'10':None})
s.flag('#FLG2001','SIM1_VCC',330.2,381,'Modem internal SIM regulator through socket contact 36')
s.note('SIM routing <=200mm and away from RF/SW; 22R/10pF and 15k follow RM520 reference.\nDisable AT+QSIMDET; keep modem SIM-detect contact 66 open. Sierra open means card present.\nValidate SIM ATR/retry behavior with card present/absent and each profile.',317.5,533.4)
s.save()
for name,symbol in [('m2-b',body),('nano-sim',sim)]:
    (ROOT/f'reference/{name}-captured.kicad_sym').write_text('(kicad_symbol_lib (version 20211014) (generator eeschema) '+symbol+')\n')

s=Sheet('modem-interface','Modem USB data isolation and coupling','A2')
raw=(ROOT/'reference/tmuxhs4212-captured.kicad_sym').read_text();mux=block(raw,raw.index('(symbol "TMUXHS4212_RKS"'))
p=s.symbol('Appliance:TMUXHS4212_RKS',mux,'U2001','TMUXHS4212IRKSR',182.88,81.28,'Appliance:DHVQFN-20_L4.5-W2.5-P0.50-BL-EP',{'MPN':'TMUXHS4212IRKSR','Manufacturer':'Texas Instruments','LCSC':'C3656912','Datasheet':'https://www.ti.com/lit/ds/symlink/tmuxhs4212.pdf','Supply Intent':'Always-on +3V3. Disabled when host or modem rail invalid. Do not rely on powered-off protection.'})
n={k:None for k in p};n.update({'1':'+3V3','6':'+3V3','10':'+3V3','2':'MODEM_USB_OE_N','9':'GND','3':'MODEM_TXP_AC','4':'MODEM_TXN_AC','7':'MODEM_USB_RXP','8':'MODEM_USB_RXN','19':'MODEM_RXP_PORT','18':'MODEM_RXN_PORT','17':'MODEM_TXP_PORT','16':'MODEM_TXN_PORT','5':'GND','11':'GND','20':'GND','21':'GND'});s.attach(p,n)
for i,pol in enumerate(['P','N']):s.passive('C',f'C{2001+i}','100nF',71.12,175.26+43.18*i,f'MODEM_USB_TX{pol}_SOC',f'MODEM_TX{pol}_AC','CL10B104KA8NNNC','Capacitor_SMD:C_0603_1608Metric','Samsung Electro-Mechanics',{'Voltage Rating':'25V','Placement':'At SoC USB3 transmitter; do not add receiver-side coupling'},horizontal=True)
s.cap('C2003','100nF',307.34,81.28,'+3V3')
up=native_pins(ROOT/'reference/modem-C128396-native.kicad_sym','TS3USB221ARSER')
assert up=={'1':'1D+','2':'1D-','3':'2D+','4':'2D-','5':'GND','6':'~{OE}','7':'D-','8':'D+','9':'S','10':'VCC'}
usb2=grouped('TS3USB221A_RSE',up,[{'left':['8','7','6','9'],'right':['1','2','3','4'],'top':['10'],'bottom':['5']}],{n:'power_in' if n in ['5','10'] else 'input' if n in ['6','9'] else 'passive' for n in up})
p=s.symbol('Appliance:TS3USB221A_RSE',usb2,'U2002','TS3USB221ARSER',441.96,81.28,'Appliance:UQFN-10_L2.0-W1.5-P0.50-BL',{'MPN':'TS3USB221ARSER','Manufacturer':'Texas Instruments','LCSC':'C128396','Datasheet':'https://www.ti.com/lit/ds/symlink/ts3usb221a.pdf','Supply Intent':'Always-on +3V3; OE high disconnects both USB2 conductors'})
s.attach(p,{'1':'MODEM_USB_DP_PORT','2':'MODEM_USB_DM_PORT','3':None,'4':None,'5':'GND','6':'MODEM_USB_OE_N','7':'MODEM_USB_DM','8':'MODEM_USB_DP','9':'GND','10':'+3V3'})
s.cap('C2004','100nF',533.4,81.28,'+3V3')
ap=native_pins(ROOT/'reference/modem-C7832-native.kicad_sym','SN74LVC1G08DCKR');assert ap=={'1':'A','2':'B','3':'GND','4':'Y','5':'VCC'}
gate=grouped('SN74LVC1G08_DCK',ap,[{'left':['1','2'],'right':['4'],'top':['5'],'bottom':['3']}],{'1':'input','2':'input','3':'power_in','4':'output','5':'power_in'})
p=s.symbol('Appliance:SN74LVC1G08_DCK',gate,'U2003','SN74LVC1G08DCKR',175.26,304.8,'Package_TO_SOT_SMD:SOT-353_SC-70-5',{'MPN':'SN74LVC1G08DCKR','Manufacturer':'Texas Instruments','LCSC':'C7832','Datasheet':'https://www.ti.com/lit/ds/symlink/sn74lvc1g08.pdf'})
s.attach(p,{'1':'MAIN3V3_GOOD','2':'MODEM_RAIL_GOOD','3':'GND','4':'MODEM_USB_VALID','5':'+3V3'})
s.cap('C2005','100nF',266.7,304.8,'+3V3')
p=s.symbol('Transistor_BJT:MMBT3904',stock('Transistor_BJT','MMBT3904'),'Q2001','MMBT3904,215',386.08,304.8,'Package_TO_SOT_SMD:SOT-23',{'MPN':'MMBT3904,215','Manufacturer':'Nexperia'})
s.attach(p,{'1':'MODEM_USB_BASE','2':'GND','3':'MODEM_USB_OE_N'})
s.resistor('R2001','10kR',327.66,238.76,'MODEM_USB_VALID','MODEM_USB_BASE','RC0603FR-0710KL',horizontal=True)
s.resistor('R2002','100kR',459.74,304.8,'MODEM_USB_BASE','GND','RC0603FR-07100KL')
s.resistor('R2003','10kR',533.4,304.8,'+3V3','MODEM_USB_OE_N','RC0603FR-0710KL')
s.note('Both USB muxes remain powered when modem/SoC are off. Hardware AND requires valid host\nand delayed modem rails before enabling data. U1903 releases after 180–420ms of valid VCC.\nHost TX -> module RX (37P/35N). Module TX (31P/29N) -> host RX. Module contains TX capacitors.\nNo M.2 PCIe routing: dedicated SoC PCIe port serves Ethernet. USB3 eye/jitter/loss and rail-fall\nisolation timing require measurement; capture/ERC does not establish recovery or throughput.',25.4,391.16)
s.save()
for name,symbol in [('ts3usb221a',usb2),('sn74lvc1g08',gate)]:
    (ROOT/f'reference/{name}-captured.kicad_sym').write_text('(kicad_symbol_lib (version 20211014) (generator eeschema) '+symbol+')\n')

s=Sheet('modem-bypass','Modem local bulk and RF bypass','A3')
p=s.symbol('Device:C_Polarized',stock('Device','C_Polarized'),'C2030','220uF / 6.3V',71.12,71.12,'Capacitor_SMD:CP_Elec_6.3x5.9',{'MPN':'6SVPC220MV','Manufacturer':'Panasonic','Datasheet':'https://industrial.panasonic.com/ww/products/pt/os-con/models/6SVPC220MV','Tolerance':'20%','ESR Maximum':'15mOhm at 100kHz','Ripple Current':'3.16Arms at 105C/100kHz','Qualification':'Layout must audit Panasonic C6 land pattern and regulator stability with effective MLCC capacitance'})
# Keep capacitor labels adjacent to the visible body.
from capture import prop
s.items[-1]=s.items[-1].replace(prop('Reference','C2030',71.12,43.18),prop('Reference','C2030',85.09,69.85)).replace(prop('Value','220uF / 6.3V',71.12,45.72),prop('Value','220uF / 6.3V',85.09,72.39))
s.attach(p,{'1':'MODEM_VCC','2':'GND'})
for i in range(5):s.cap(f'C{2031+i}','100nF',63.5+66.04*i,157.48,'MODEM_VCC')
for i,pin in enumerate(['24','38','68']):
    ref=f'C{2036+i}';s.cap(ref,'100nF',193.04+66.04*i,71.12,f'M2_PIN{pin}');dnp(s,ref)
for i,(v,mpn) in enumerate([('220pF','CL10C221JB8NNNC'),('68pF','CL10C680JB8NNNC'),('15pF','CL10C150JB8NNNC'),('9.1pF','CL10C9R1BB8NNNC'),('4.7pF','CL10C4R7BB8NNNC')]):
    s.passive('C',f'C{2041+i}',v,63.5+66.04*i,228.6,'MODEM_VCC','GND',mpn,'Capacitor_SMD:C_0603_1608Metric','Samsung Electro-Mechanics',{'Voltage Rating':'50V','Dielectric':'C0G','Placement':'At M.2 VCC; RM520 recommended RF bypass bank'})
s.note('C2030 and RF bank at socket. One 100nF at each of five common VCC contacts.\nC2036/37/38 SIERRA ONLY: DNP in Quectel profiles along with their feed links.\nConfirm effective MLCC capacitance at DC bias and full modem internal capacitance.\nLayout must share current across every populated VCC/GND contact and minimize drop.\nNo released four-module burst specification or temperature/thermal qualification yet.',25.4,279.4)
s.save()
# Allocate three free supervisor inputs with explicit native pad identities.
p=ROOT/'supervisor.kicad_sch';raw=p.read_text();library=next(i for i in children(raw) if i.startswith('(lib_symbols'));body=next(i for i in children(library) if i.startswith('(symbol "MCU_ST'))
instance=next(i for i in children(raw) if i.startswith('(symbol') and '(lib_id "MCU_ST' in i);x,y,a=map(float,re.search(r'\(at ([^()]+)',instance)[1].split())
points=Sheet('tmp','').symbol('MCU',body,'U201','',x,y,angle=a);patch=Sheet('supervisor-modem','')
for number,signal in [('25','MODEM_RAIL_GOOD'),('26','MODEM_SWITCH_GOOD'),('27','MODEM_BUCK_GOOD')]:
    x,y,angle=points[number]
    for item in children(raw):
        if item.startswith('(no_connect'):
            at=re.search(r'\(at ([^()]+)',item)[1].split()
            if abs(float(at[0])-x)<.0001 and abs(float(at[1])-y)<.0001:raw=raw.replace(item,'')
    patch.wire((x,y),(x+12.7,y));patch.net(signal,(x+12.7,y),180)
for item in patch.items:
    if item not in raw:raw=raw.rstrip()[:-1]+item+')\n'
p.write_text("\n".join(line.rstrip() for line in raw.splitlines())+"\n")
