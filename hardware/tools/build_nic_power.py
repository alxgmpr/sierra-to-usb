#!/usr/bin/env python3
"""RTL8125BG independent supplies and hardware sequencing, manufacturer pin tables."""
from capture import ROOT, Sheet, grouped, native_pins, stock, block
s=Sheet('nic-power','Ethernet power and hardware reset sequencing','A2')
controls=ROOT/'reference/nic-controls-native-candidates.kicad_sym'
sup_pins={'1':'RESET','2':'GND','3':'MR','4':'CT','5':'SENSE','6':'VDD'}
sup=grouped('TPS3808_DBV',sup_pins,[{'left':['3','4','5'],'right':['1'],'top':['6'],'bottom':['2']}],{n:'open_collector' if n=='1' else 'power_in' if n in ['2','6'] else 'input' for n in sup_pins})
assert native_pins(controls,'TPS3808G01DBVR')==sup_pins
buf=stock('74xGxx','SN74LVC1G125DCK')
p=s.symbol('74xGxx:SN74LVC1G125DCK',buf,'U1501','SN74LVC1G125DCKR',86.36,71.12,'Package_TO_SOT_SMD:SOT-353_SC-70-5',{'MPN':'SN74LVC1G125DCKR','Manufacturer':'Texas Instruments','LCSC':'C7833'})
s.attach(p,{'1':'GND','2':'MCU_ETH_POWER_EN','3':'GND','4':'ETH_SWITCH_EN','5':'3V3_MAIN'})
s.resistor('R1501','100kR',38.1,129.54,'MCU_ETH_POWER_EN','GND','RC0603FR-07100KL')
s.resistor('R1502','100kR',114.3,129.54,'ETH_SWITCH_EN','GND','RC0603FR-07100KL')
s.cap('C1501','100nF',160.02,129.54,'3V3_MAIN')
pins=native_pins(ROOT/'reference/interface-native-candidates.kicad_sym','TPS22965DSGR')
assert pins=={'1':'VIN','2':'VIN','3':'ON','4':'VBIAS','5':'GND','6':'CT','7':'VOUT','8':'VOUT','9':'EP'}
roles={n:'power_in' if n in ['1','2','4','5','9'] else 'power_out' if n=='7' else 'passive' if n in ['6','8'] else 'input' for n in pins}
switch=grouped('TPS22965_DSG',pins,[{'left':['3','6'],'right':['7','8'],'top':['1','2','4'],'bottom':['5','9']}],roles)
p=s.symbol('Appliance:TPS22965_DSG',switch,'U1502','TPS22965DSGR',238.76,76.2,'Appliance:UDFN-8_L2.0-W2.0-P0.50-TL-EP',{'MPN':'TPS22965DSGR','Manufacturer':'Texas Instruments','LCSC':'C122837','Datasheet':'https://www.ti.com/lit/ds/symlink/tps22965.pdf'})
s.attach(p,{'1':'3V3_MAIN','2':'3V3_MAIN','3':'ETH_SWITCH_EN','4':'5V_MAIN','5':'GND','6':'ETH_SWITCH_CT','7':'ETH_3V3','8':'ETH_3V3','9':'GND'})
s.passive('C','C1502','1nF',208.28,139.7,'ETH_SWITCH_CT','GND','CL10B102KB8NNNC','Capacitor_SMD:C_0603_1608Metric','Samsung Electro-Mechanics',{'Voltage Rating':'50V'})
s.cap('C1503','10uF',281.94,139.7,'ETH_3V3')
s.cap('C1504','100nF',320.04,139.7,'5V_MAIN')
s.note('Ioff buffer prevents MCU back-power when main supply is off.\nCT=1nF, VBIAS=5V: 1.33ms typical 3.3V rise (TI Table 1).\nQuick-output discharge 225R typical; measured decay required.',25.4,167.64)
# NIC controlled 0.95 V external regulator, BG variant only.
raw=(ROOT/'DdrPowerDraft.kicad_sym').read_text();sy=block(raw,raw.index('(symbol "SY8089AAAC"'))
p=s.symbol('DdrPowerDraft:SY8089AAAC',sy,'U1503','SY8089AAAC',96.52,236.22,'Package_TO_SOT_SMD:SOT-23-5',{'MPN':'SY8089AAAC','Manufacturer':'Silergy','LCSC':'C78988','Qualification':'Soft start 1.2ms typical; measured 0.5–5ms rise required by RTL8125BG'})
s.attach(p,{'1':'ETH_CORE_EN','2':'GND','3':'ETH_CORE_SW','4':'ETH_3V3','5':'ETH_CORE_FB'})
s.cap('C1505','10uF',48.26,304.8,'ETH_3V3')
s.resistor('R1503','100kR',99.06,304.8,'ETH_CORE_EN','GND','RC0603FR-07100KL')
s.passive('L','L1501','2.2uH',203.2,218.44,'ETH_CORE_SW','ETH_0V95','XGL4020-222MEC','Inductor_SMD:L_Coilcraft_XxL4020','Coilcraft',{'DCR Maximum':'21.5mOhm','Saturation Current 10% Drop':'2.7A'},horizontal=True)
s.cap('C1506','22uF',190.5,279.4,'ETH_0V95');s.cap('C1507','10uF',241.3,279.4,'ETH_0V95')
s.passive('R','R1504','59kR',309.88,238.76,'ETH_0V95','ETH_CORE_FB','RT0603BRD0759KL','Resistor_SMD:R_0603_1608Metric','Yageo',{'Tolerance':'0.1%','Power Rating':'0.1W'})
s.passive('R','R1505','100kR',309.88,287.02,'ETH_CORE_FB','GND','RT0603BRD07100KL','Resistor_SMD:R_0603_1608Metric','Yageo',{'Tolerance':'0.1%','Power Rating':'0.1W'})
s.flag('#FLG1502','ETH_0V95',292.1,218.44,'U1503 LX through L1501')
s.note('0.954V nominal; .588–.612V FB and 0.1% R: 0.934–0.974V.\nRTL8125BG .92–.98V operating rail, 650mA maximum (Table 29).\nPOW_EXT_SWR controls core startup; do not fit RTL8125BGS here.',25.4,335.28)
# Clock unblock comes 12–28 ms after valid 3.3 V. PERST release waits >=180ms after core valid.
for ref,value,y,rail,sense,out,ct in [('U1504','TPS3808G33DBVR',99.06,'ETH_3V3','ETH_3V3','ETH_3V3_GOOD',None),('U1505','TPS3808G01DBVR',246.38,'ETH_3V3','ETH_CORE_SENSE','ETH_PERST_N','ETH_RESET_CT')]:
 p=s.symbol('Appliance:TPS3808_DBV',sup,ref,value,431.8,y,'Package_TO_SOT_SMD:SOT-23-6',{'MPN':value,'Manufacturer':'Texas Instruments','LCSC':'C43698' if 'G33' in value else 'C19653','Datasheet':'https://www.ti.com/lit/ds/symlink/tps3808.pdf'})
 s.attach(p,{'1':out,'2':'GND','3':rail,'4':ct,'5':sense,'6':rail})
 s.cap('C1508' if 'G33' in value else 'C1509','100nF',525.78,y,rail)
s.resistor('R1506','115kR',373.38,330.2,'ETH_0V95','ETH_CORE_SENSE','RC0603FR-07115KL')
s.resistor('R1507','100kR',424.18,330.2,'ETH_CORE_SENSE','GND','RC0603FR-07100KL')
s.resistor('R1508','100kR',474.98,330.2,'ETH_3V3','ETH_RESET_CT','RC0603FR-07100KL')
s.resistor('R1509','10kR',525.78,330.2,'ETH_3V3','ETH_PERST_N','RC0603FR-0710KL')
s.resistor('R1510','10kR',525.78,165.1,'ETH_3V3','ETH_3V3_GOOD','RC0603FR-0710KL')
s.note('G33: open CT gives 12–28ms delay to clock-enable logic.\nG01: CT via 100k to VDD gives 180–420ms reset delay.\n0.871V nominal core supervision; worst release <=0.925V.\nThis detects collapse; it does not guarantee the .92V operating minimum.\nHold PERST for >=100ms with clock stable. Verify all corners on bench.',365.76,375.92)
s.save()
for name,body in [('tps22965',switch),('tps3808',sup)]:
 (ROOT/f'reference/{name}-captured.kicad_sym').write_text('(kicad_symbol_lib (version 20211014) (generator eeschema) '+body+')\n')
