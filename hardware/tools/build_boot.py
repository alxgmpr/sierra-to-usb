#!/usr/bin/env python3
"""Capture 16 GB native-mode eMMC, 24 MHz clock and physical recovery points."""
from capture import ROOT, Sheet, grouped, native_pins, stock

sheet = Sheet('boot', 'Boot storage and system clock')
sheet.rectangle('16 GB eMMC — 1.8V I/O, HS200 HOST', 20.32, 20.32, 187.96, 193.04)
pins = native_pins(ROOT/'reference/appliance-native-candidates.kicad_sym','IS21TF16G-JCLI')
assert len(pins) == 153
assert {n:v for n,v in pins.items() if v not in {'NC','RFU'}} == {
    'M6':'CLK','M5':'CMD','A3':'DAT0','A4':'DAT1','A5':'DAT2','B2':'DAT3','B3':'DAT4','B4':'DAT5','B5':'DAT6','B6':'DAT7','H5':'DS','K5':'RST_n','C2':'VDDI',
    'E6':'VCC','F5':'VCC','J10':'VCC','K9':'VCC','C6':'VCCQ','M4':'VCCQ','N4':'VCCQ','P3':'VCCQ','P5':'VCCQ',
    'A6':'VSS','E7':'VSS','G5':'VSS','H10':'VSS','J5':'VSS','K8':'VSS','C4':'VSSQ','N2':'VSSQ','N5':'VSSQ','P4':'VSSQ','P6':'VSSQ'}
reserved = [n for n,v in pins.items() if v in {'NC','RFU'}]
roles = {n:'no_connect' if v in {'NC','RFU'} else 'power_in' if v in {'VCC','VCCQ','VSS','VSSQ'} else 'power_out' if v == 'VDDI' else 'input' if v in {'CLK','RST_n'} else 'output' if v == 'DS' else 'bidirectional' for n,v in pins.items()}
symbol = grouped('IS21TF16G_JCLI',pins,[
    {'left':['M6','M5','K5'],'right':['A3','A4','A5','B2','B3','B4','B5','B6','H5','C2'],'top':['E6','F5','J10','K9','C6','M4','N4','P3','P5'],'bottom':['A6','E7','G5','H10','J5','K8','C4','N2','N5','P4','P6']},
    {'left':reserved[:30],'right':reserved[30:60]},
    {'left':reserved[60:90],'right':reserved[90:]},
],roles)
fields = {'MPN':'IS21TF16G-JCLI','Manufacturer':'ISSI','LCSC':'C17441928','Datasheet':'https://www.issi.com/WW/pdf/21-22TF16G-32G-64G-128G.pdf','Qualification':'153 balls audited to ISSI Rev A page 11; RK3566 compatibility and sourcing remain bench/release checks'}
footprint = 'Appliance:VFBGA-153_L13.0-W11.5-P0.50-BL_ISSI_IS2XES0XG-XXXX'
for unit,x,y in [(1,101.6,86.36),(2,294.64,76.2),(3,294.64,195.58)]:
    p = sheet.symbol('Appliance:IS21TF16G_JCLI',symbol,'U1101','IS21TF16G-JCLI',x,y,footprint,fields,unit=unit)
    nets = {}
    for n in p:
        value = pins[n]
        nets[n] = None if value in {'NC','RFU'} else 'GND' if value in {'VSS','VSSQ'} else '3V3_MAIN' if value == 'VCC' else 'VCC_1V8' if value == 'VCCQ' else 'EMMC_VDDI' if value == 'VDDI' else 'EMMC_CLK' if value == 'CLK' else 'EMMC_CMD' if value == 'CMD' else 'EMMC_RESET_N' if value == 'RST_n' else 'EMMC_STROBE' if value == 'DS' else 'EMMC_D'+value[3:]
    sheet.attach(p,nets)
sheet.cap('C1101','10uF',43.18,162.56,'3V3_MAIN')
sheet.cap('C1102','1uF',81.28,162.56,'VCC_1V8')
sheet.cap('C1103','100nF',119.38,162.56,'VCC_1V8')
sheet.cap('C1104','4.7uF',157.48,162.56,'EMMC_VDDI')
sheet.resistor('R1101','10kR',43.18,195.58,'VCC_1V8','EMMC_CMD','RC0603FR-0710KL')
sheet.resistor('R1102','10kR',93.98,195.58,'VCC_1V8','EMMC_D0','RC0603FR-0710KL')
sheet.resistor('R1103','22R',157.48,127,'EMMC_CLK_SOC','EMMC_CLK','RC0603FR-0722RL',horizontal=True)
sheet.resistor('R1104','100kR',190.5,195.58,'EMMC_STROBE','GND','RC0603FR-07100KL')
sheet.rectangle('24 MHz TOTAL ±20 ppm CLOCK',20.32,223.52,187.96,58.42)
osc = stock('Oscillator','SiT8008xx-2x-xxE')
p = sheet.symbol('Oscillator:SiT8008xx-2x-xxE',osc,'Y1101','SiT8008BI-21-18E-24.000000',68.58,256.54,'Oscillator:Oscillator_SMD_SiT_PQFN-4Pin_3.2x2.5mm',{'MPN':'SiT8008BI-21-18E-24.000000','Manufacturer':'SiTime','LCSC':'C820729','Datasheet':'https://www.sitime.com/datasheet/sit8008','Frequency Stability':'20ppm total','Supply Voltage':'1.8V','Temperature Range':'-40 to 85C'})
sheet.attach(p,{'1':'OSC_ENABLE','2':'GND','3':'OSC24_OUT','4':'VCCA1V8_PMU'})
sheet.cap('C1105','100nF',157.48,256.54,'VCCA1V8_PMU')
sheet.resistor('R1105','10kR',106.68,246.38,'VCCA1V8_PMU','OSC_ENABLE','RC0603FR-0710KL',horizontal=True)
sheet.resistor('R1106','22R',111.76,274.32,'OSC24_OUT','CLK24_IN','RC0603FR-0722RL',horizontal=True)
sheet.note('NC/RFU balls remain floating per ISSI page 13.\nUse native TLC capacity; measure A/B image and logging endurance.\nKeep CLK/D0 MaskROM test branches short.\nUSB recovery remains independent of eMMC contents.',223.52,271.78)
for ref,x,net in [('TP1101',223.52,'EMMC_CLK'),('TP1102',266.7,'EMMC_D0'),('TP1103',309.88,'GND')]:
 p=sheet.symbol('Connector:TestPoint',stock('Connector','TestPoint'),ref,net,x,208.28,'TestPoint:TestPoint_Pad_D1.0mm',{'Placement Intent':'short recovery probe branch; use controlled MaskROM procedure'})
 sheet.attach(p,{'1':net})
sheet.save()
(ROOT/'reference/emmc-captured.kicad_sym').write_text('(kicad_symbol_lib (version 20211014) (generator eeschema) '+symbol+')\n')
