#!/usr/bin/env python3
"""Capture the native TCS4525 reference CPU rail against its public 5 A limits."""
from capture import ROOT, Sheet, grouped, native_pins

pins = native_pins(ROOT / 'reference/appliance-native-candidates.kicad_sym', 'TCS4525_WT_C7501359')
expected = {'A1':'VSEL','A2':'EN','A3':'SCL','A4':'FB','B1':'SDA','B2':'PGND','B3':'PGND/PG','B4':'AGND','C1':'PGND','C2':'PGND','C3':'PGND','C4':'PGND','D1':'AVIN','D2':'PVIN','D3':'SW','D4':'SW','E1':'PVIN','E2':'PVIN','E3':'SW','E4':'SW'}
assert pins == expected, 'Native pin table differs from manufacturer v1.0 page 3'
roles = {n:'power_in' if name in {'PVIN','AVIN','PGND','AGND','PGND/PG'} else 'power_out' if name == 'SW' else 'bidirectional' if name in {'SDA','SCL'} else 'input' for n,name in pins.items()}
for number in ['D4','E3','E4']:
    roles[number] = 'passive'  # Internally common switching node; D3 represents its driver.
symbol = grouped('TCS4525_WT', pins, [{'left':['A2','A1','A3','B1'],'right':['D3','D4','E3','E4','A4'],'top':['D1','D2','E1','E2'],'bottom':['B2','B3','B4','C1','C2','C3','C4']}], roles)
sheet = Sheet('cpu-power', 'CPU supply — reference DVS implementation')
sheet.rectangle('CPU DYNAMIC VOLTAGE SCALING', 20.32, 20.32, 375.92, 223.52)
p = sheet.symbol('Appliance:TCS4525_WT', symbol, 'U1001', 'TCS4525_WT', 96.52, 91.44, 'Appliance:WLCSP-20_L2.0-W1.6-R5-C4-P0.40-TL', {'MPN':'TCS4525_WT','Manufacturer':'Torch-Chip','LCSC':'C7501359','Datasheet':'https://datasheet4u.com/pdf/1549392/TCS4525.pdf','Qualification':'Public v1.0 5A limits; current 6A revision and supplier lifecycle unresolved'})
nets = {n:'5V_MAIN' if name in {'AVIN','PVIN'} else 'GND' if name in {'AGND','PGND','PGND/PG','VSEL'} else 'CPU_SW' if name == 'SW' else {'EN':'PMIC_CPU_EN','FB':'CPU_FB','SDA':'PMIC_I2C_SDA','SCL':'PMIC_I2C_SCL'}[name] for n,name in pins.items()}
sheet.attach(p,nets)
sheet.passive('L','L1001','0.47uH',228.6,71.12,'CPU_SW','VDD_CPU','XGL4020-471MEC','Inductor_SMD:L_Coilcraft_XxL4020','Coilcraft', {'Saturation Current 10% Drop':'6.1A','DCR Maximum':'5.1mOhm'}, horizontal=True)
sheet.cap('C1001','10uF',43.18,165.1,'5V_MAIN')
sheet.cap('C1002','100nF',81.28,165.1,'5V_MAIN')
for i,x in enumerate([203.2,241.3]):
    sheet.cap(f'C{1003+i}','22uF',x,121.92,'VDD_CPU')
for i,value in enumerate(['4.7uF','4.7uF','22uF','22uF','22uF']):
    sheet.cap(f'C{1005+i}',value,190.5+38.1*i,190.5,'VDD_CPU')
sheet.resistor('R1001','100kR',134.62,165.1,'PMIC_CPU_EN','GND','RC0603FR-07100KL')
sheet.note('VSEL strapped low: 1.025V reset value; I2C address 0x1C.\nRK809 EXT_EN controls startup. Retain DVS via fan53555 driver.\nFive local bypass capacitors follow NanoPi R3S power sheet.\nRoute FB separately to processor load; CPU worst-case load and current revision require closure.', 30.48, 223.52)
sheet.flag('#FLG1001','VDD_CPU',289.56,121.92,'U1001 D3 switching output through L1001')
sheet.save()
(ROOT/'reference/tcs4525-captured.kicad_sym').write_text('(kicad_symbol_lib (version 20211014) (generator eeschema) '+symbol+')\n')
