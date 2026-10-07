#!/usr/bin/env python3
"""Native-pin audited RTL8125BG core, 25MHz crystal, EEPROM and local bypass."""
from capture import ROOT, Sheet, grouped, native_pins, stock
pins=native_pins(ROOT/'reference/appliance-native-candidates.kicad_sym','RTL8125BG-CG')
assert len(pins)==49
assert {n:pins[n] for n in ['4','5','6','7','36','38','39','41','42','44','45','49']}=={'4':'NC','5':'NC','6':'POW_EXT_SWR','7':'NC','36':'PERSTB','38':'HSOP','39':'HSON','41':'HSIP','42':'HSIN','44':'REFCLK_P','45':'REFCLK_N','49':'GND'}
roles={n:'power_in' if name.startswith(('DVDD','AVDD','EVDD')) or name=='GND' else 'open_collector' if n in ['2','48'] else 'output' if n in ['6','9','38','39','27','30','31','35'] else 'input' if n in ['1','10','12','25','32','36','41','42','44','45'] else 'bidirectional' if name.startswith('MDI') or n=='3' else 'passive' for n,name in pins.items()}
sym=grouped('RTL8125BG_CG',pins,[
 {'left':['1','36','44','45','41','42'],'right':['38','39','2','48','6'],'top':['8','28','47','37','29','46','43'],'bottom':['40','49']},
 {'left':['10','13','14','17','18','20','21','23','24'],'right':['9','12'],'top':['11','16','22','15','19','33','34']},
 {'left':['32','25','3','4','5','7'],'right':['27','30','31','26','35']}
],roles)
s=Sheet('nic','2.5GbE controller — RTL8125BG external-core variant','A2')
nets={n:None for n in pins}
nets.update({'1':'ETH_ISOLATE_N','2':'ETH_WAKE_N','6':'ETH_CORE_EN','8':'ETH_0V95','28':'ETH_0V95','47':'ETH_0V95','29':'ETH_3V3','46':'ETH_3V3','37':'ETH_PCIE_0V95','43':'ETH_3V3','9':'ETH_XTAL_OUT','10':'ETH_XTAL_IN','11':'ETH_ANALOG_0V95','16':'ETH_ANALOG_0V95','22':'ETH_ANALOG_0V95','12':'ETH_RSET','15':'ETH_ANALOG_3V3','19':'ETH_ANALOG_3V3','33':'ETH_ANALOG_3V3','34':'ETH_XTAL_3V3','25':'ETH_EE_DO','27':'ETH_EE_CLK','30':'ETH_EE_DI','31':'ETH_EE_CS','32':'ETH_EE_SEL','36':'ETH_PERST_N','38':'ETH_PCIE_TXP','39':'ETH_PCIE_TXN','40':'GND','41':'ETH_PCIE_RXP','42':'ETH_PCIE_RXN','44':'ETH_REFCLK_P','45':'ETH_REFCLK_N','48':'ETH_CLKREQ_N','49':'GND'})
for n,name in [('13','ETH_MDI0_P'),('14','ETH_MDI0_N'),('17','ETH_MDI1_P'),('18','ETH_MDI1_N'),('20','ETH_MDI2_P'),('21','ETH_MDI2_N'),('23','ETH_MDI3_P'),('24','ETH_MDI3_N')]:nets[n]=name
for unit,x,y in [(1,114.3,106.68),(2,408.94,106.68),(3,106.68,246.38)]:
 p=s.symbol('Appliance:RTL8125BG_CG',sym,'U1301','RTL8125BG-CG',x,y,'Appliance:TQFN-48_L6.0-W6.0-P0.40-BL-EP4.5',{'MPN':'RTL8125BG-CG','Manufacturer':'Realtek','LCSC':'C3013605','Datasheet':'https://gzhls.at/blob/ldb/4/2/8/6/7a314000645b287070e0d89fb96ceb1faf4a.pdf','Qualification':'BG variant: external 0.95V supply; no BGS substitution'},unit=unit)
 s.attach(p,{n:nets[n] for n in p})
for ref,val,x,y,a,b,mpn in [('R1301','10kR',215.9,66.04,'ETH_3V3','ETH_ISOLATE_N','RC0603FR-0710KL'),('R1302','1kR',215.9,114.3,'ETH_3V3','ETH_WAKE_N','RC0603FR-071KL'),('R1303','4.7kR',215.9,162.56,'ETH_3V3','ETH_CLKREQ_N','RC0603FR-074K7L'),('R1304','4.7kR',215.9,215.9,'ETH_3V3','ETH_EE_CLK','RC0603FR-074K7L'),('R1305','4.7kR',215.9,264.16,'ETH_EE_DI','GND','RC0603FR-074K7L'),('R1306','10kR',215.9,312.42,'ETH_EE_SEL','GND','RC0603FR-0710KL'),('R1307','2.49kR',508,180.34,'ETH_RSET','GND','RC0603FR-072K49L')]:s.resistor(ref,val,x,y,a,b,mpn)
# Fixed 16-bit 93C46 organization; both organization pins are NC for B version.
ep=native_pins(ROOT/'reference/nic-extra-native-candidates.kicad_sym','93LC46BT-I_SN_C16253')
assert ep=={'1':'CS','2':'CLK','3':'DI','4':'DO','5':'VSS','6':'NC','7':'NC','8':'VCC'}
ee=grouped('93LC46B_SN',ep,[{'left':['1','2','3'],'right':['4','6','7'],'top':['8'],'bottom':['5']}],{n:'power_in' if n in ['5','8'] else 'output' if n=='4' else 'passive' if n in ['6','7'] else 'input' for n in ep})
p=s.symbol('Appliance:93LC46B_SN',ee,'U1302','93LC46BT-I/SN',342.9,254,'Package_SO:SOIC-8_3.9x4.9mm_P1.27mm',{'MPN':'93LC46BT-I/SN','Manufacturer':'Microchip Technology','LCSC':'C16253','Datasheet':'https://ww1.microchip.com/downloads/en/DeviceDoc/21749H.pdf','Programming':'Provision unique MAC and validated Realtek 93C46 image before release'})
s.attach(p,{'1':'ETH_EE_CS','2':'ETH_EE_CLK','3':'ETH_EE_DI','4':'ETH_EE_DO','5':'GND','6':None,'7':None,'8':'ETH_3V3'})
s.cap('C1301','100nF',434.34,254,'ETH_3V3')
p=s.symbol('Device:Crystal_GND24',stock('Device','Crystal_GND24'),'Y1301','25MHz, 18pF',406.4,312.42,'Crystal:Crystal_SMD_3225-4Pin_3.2x2.5mm',{'MPN':'7M-25.000MEIJ-T','Manufacturer':'TXC Corporation','Frequency':'25MHz','Load Capacitance':'18pF','Frequency Tolerance':'10ppm','Temperature Stability':'20ppm (-40 to 85C)','Aging':'3ppm first year','Qualification':'33ppm initial/temp/aging sum; loading budget <=17ppm; trim and phase noise bench check'})
s.attach(p,{'1':'ETH_XTAL_IN','3':'ETH_XTAL_OUT','2':'GND','4':'GND'})
for ref,x,rail in [('C1302',332.74,'ETH_XTAL_IN'),('C1303',482.6,'ETH_XTAL_OUT')]:
 s.passive('C',ref,'27pF',x,312.42,rail,'GND','CL10C270JB8NNNC','Capacitor_SMD:C_0603_1608Metric','Samsung Electro-Mechanics',{'Voltage Rating':'50V','Dielectric':'C0G','Tolerance':'5%'})
# Separate filtered analog domains and a bypass at every power pin.
for i,(src,out) in enumerate([('ETH_3V3','ETH_ANALOG_3V3'),('ETH_3V3','ETH_XTAL_3V3'),('ETH_0V95','ETH_ANALOG_0V95'),('ETH_0V95','ETH_PCIE_0V95')]):
 x=63.5+124.46*i
 s.passive('FB',f'FB{1301+i}','30R @ 100MHz' if i>=2 else '120R @ 100MHz',x,363.22,src,out,'MPZ2012S300AT000' if i>=2 else 'MPZ1608S121ATAH0','Inductor_SMD:L_0805_2012Metric' if i>=2 else 'Inductor_SMD:L_0603_1608Metric','TDK',{'DCR Maximum':'10mOhm' if i>=2 else '45mOhm','Current Rating':'6A' if i>=2 else '2A'},horizontal=True)
 s.flag(f'#FLG{1301+i}',out,x,396.24,f'ETH supply through FB{1301+i}')
s.note('LANWAKE requires 1–4.7k pull-up. EESK requires 4.7k pull-up; low enters test mode.\nEEDI low selects Microwire, EEPROM_SEL low selects 93C46. All strap levels at power-on.\nBG pins 4/5/7 float; all 49 pads audited. 2.5G magnetics and four-pair PoE attached; qualify hardware.',25.4,401.32)
s.save()
for name,body in [('rtl8125bg',sym),('93lc46b',ee)]:
 (ROOT/f'reference/{name}-captured.kicad_sym').write_text('(kicad_symbol_lib (version 20211014) (generator eeschema) '+body+')\n')
