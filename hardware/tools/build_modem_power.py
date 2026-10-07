#!/usr/bin/env python3
"""Independent compensated 3.7V modem regulator, latched eFuse and discharge."""
import re
from capture import ROOT,Sheet,stock,grouped,native_pins,block
s=Sheet('modem-power','Independent modem power — 3.7V / burst allocation 5A','A1')
pins=native_pins(ROOT/'reference/modem-C263274-native.kicad_sym','TPS54620RHLR')
assert pins=={'1':'RT/CLK','2':'GND','3':'GND','4':'PVIN','5':'PVIN','6':'VIN','7':'VSENSE','8':'COMP','9':'SS/TR','10':'EN','11':'PH','12':'PH','13':'BOOT','14':'PWRGD','15':'EP'}
roles={n:'power_in' if n in ['2','3','4','5','6','15'] else 'power_out' if n=='11' else 'open_collector' if n=='14' else 'output' if n in ['8','9'] else 'input' if n in ['1','7','10'] else 'passive' for n in pins}
reg=grouped('TPS54620_RHL',pins,[{'top':['4','5','6'],'bottom':['2','3','15'],'left':['10','1','7','8','9'],'right':['13','11','12','14']}],roles)
p=s.symbol('Appliance:TPS54620_RHL',reg,'U1901','TPS54620RHLR',129.54,86.36,'Appliance:VQFN-14_L3.5-W3.5-P0.50-TL-EP_TPS54622RHLT',{'MPN':'TPS54620RHLR','Manufacturer':'Texas Instruments','LCSC':'C263274','Datasheet':'https://www.ti.com/lit/ds/symlink/tps54620.pdf','ERC Model':'BOOT floating supply terminal passive; PH pad 12 passive duplicate of power output 11'})
s.attach(p,{'1':'MODEM_BUCK_RT','2':'GND','3':'GND','4':'ISO_12V','5':'ISO_12V','6':'ISO_12V','7':'MODEM_BUCK_FB','8':'MODEM_BUCK_COMP','9':'MODEM_BUCK_SS','10':'MODEM_BUCK_EN','11':'MODEM_BUCK_SW','12':'MODEM_BUCK_SW','13':'MODEM_BUCK_BOOT','14':'MODEM_BUCK_GOOD','15':'GND'})
# 0.8*(1+36.3/10)=3.704V. Kelvin sense before the separately controlled eFuse.
for ref,val,x,y,a,b,mpn,tol in [('R1901','36.3kR',284.48,55.88,'MODEM_3V7_RAW','MODEM_BUCK_FB','RT0603BRD0736K3L','0.1%'),('R1902','10kR',284.48,104.14,'MODEM_BUCK_FB','GND','RT0603BRD0710KL','0.1%'),('R1903','100kR',63.5,162.56,'MODEM_BUCK_RT','GND','RC0603FR-07100KL','1%'),('R1904','10kR',203.2,162.56,'MCU_MODEM_POWER_EN','MODEM_BUCK_EN','RC0603FR-0710KL','1%'),('R1905','100kR',284.48,162.56,'MODEM_BUCK_EN','GND','RC0603FR-07100KL','1%'),('R1906','10kR',358.14,162.56,'+3V3','MODEM_BUCK_GOOD','RC0603FR-0710KL','1%')]:s.passive('R',ref,val,x,y,a,b,mpn,'Resistor_SMD:R_0603_1608Metric','Yageo',{'Tolerance':tol,'Power Rating':'0.1W'})
s.passive('C','C1901','100nF',203.2,55.88,'MODEM_BUCK_BOOT','MODEM_BUCK_SW','CL10B104KA8NNNC','Capacitor_SMD:C_0603_1608Metric','Samsung Electro-Mechanics',{'Voltage Rating':'25V','Placement':'Directly at BOOT and PH'})
s.passive('L','L1901','3.3uH',378.46,55.88,'MODEM_BUCK_SW','MODEM_3V7_RAW','XAL7070-332MEC','Inductor_SMD:L_Coilcraft_XAL7070-XXX','Coilcraft',{'Source':'Same manufacturer-audited part and land pattern as L701','Qualification':'480kHz ripple and current-limit corners; thermal qualification pending'},horizontal=True)
for i,x in enumerate([444.5,485.14,525.78]):s.cap(f'C{1902+i}','22uF',x,55.88,'MODEM_3V7_RAW')
for ref,val,x,y in [('C1905','10uF',444.5,127),('C1906','10uF',485.14,127),('C1907','100nF',525.78,127)]:s.cap(ref,val,x,y,'ISO_12V')
s.passive('C','C1908','47nF',63.5,228.6,'MODEM_BUCK_SS','GND','CL10B473KB8NNNC','Capacitor_SMD:C_0603_1608Metric','Samsung Electro-Mechanics',{'Voltage Rating':'50V','Dielectric':'X7R'})
# Type-II compensation. Analytical current-mode model report is a design check, not measured loop stability.
s.resistor('R1907','1kR',152.4,228.6,'MODEM_BUCK_COMP','MODEM_COMP_RC','RC0603FR-071KL')
s.cap('C1909','100nF',233.68,228.6,'MODEM_COMP_RC')
s.passive('C','C1910','1nF',314.96,228.6,'MODEM_BUCK_COMP','GND','CL10B102KB8NNNC','Capacitor_SMD:C_0603_1608Metric','Samsung Electro-Mechanics',{'Voltage Rating':'50V','Dielectric':'X7R'})
s.flag('#FLG1901','MODEM_3V7_RAW',444.5,203.2,'TPS54620 PH through L1901')
s.note('Compensated current-mode regulator supports the downstream 220uF modem bulk bank.\nType II: 1k / 100nF, 1nF high-frequency pole. Include eFuse resistance and both banks\nin loop analysis. Verify loop, burst droop, soft-start and thermal behavior on hardware.\n5A is a provisional burst design allocation. The selected 1A/power-contact M.2 socket permits\n5A total at 25C; sharing, hot derating and module envelope require qualification.\nThis is not a guaranteed current envelope for RM551E-GL or Sierra mmWave accessories.',25.4,294.64)
# Circuit-breaker, latch-off part: software must clear faults by toggling enable.
fpins=native_pins(ROOT/'reference/modem-C2864845-native.kicad_sym','TPS259474LRPWR');assert len(fpins)==10
expected={'1':'EN/UVLO','2':'OVLO/OVCSEL','3':'PG/AUXOFF','4':'PGTH/~{FLT}','5':'IN','6':'OUT','7':'DVDT','8':'GND','9':'ILM','10':'ITIMER'};assert fpins==expected
fuse=grouped('TPS259474L_RPW',fpins,[{'left':['1','2','4','9','7','10'],'right':['6','3'],'top':['5'],'bottom':['8']}],{n:'power_in' if n in ['5','8'] else 'power_out' if n=='6' else 'open_collector' if n=='3' else 'output' if n in ['7','9','10'] else 'input' for n in fpins})
p=s.symbol('Appliance:TPS259474L_RPW',fuse,'U1902','TPS259474LRPWR',660.4,86.36,'Appliance:VQFN-10_L2.0-W2.0-P0.45-TL',{'MPN':'TPS259474LRPWR','Manufacturer':'Texas Instruments','LCSC':'C2864845','Datasheet':'https://www.ti.com/lit/ds/symlink/tps25947.pdf','Fault Response':'Latch off; EN low/high clears. Reverse-current blocking always.'})
s.attach(p,{'1':'MODEM_FUSE_EN','2':'MODEM_FUSE_OVLO','3':'MODEM_SWITCH_GOOD','4':'MODEM_FUSE_PGTH','5':'MODEM_3V7_RAW','6':'MODEM_VCC','7':'MODEM_FUSE_DVDT','8':'GND','9':'MODEM_FUSE_ILM','10':None})
for ref,val,x,y,a,b,mpn,tol in [('R1911','10kR',609.6,162.56,'MCU_MODEM_POWER_EN','MODEM_FUSE_EN','RC0603FR-0710KL','1%'),('R1912','100kR',688.34,162.56,'MODEM_FUSE_EN','GND','RC0603FR-07100KL','1%'),('R1913','237kR',769.62,55.88,'MODEM_3V7_RAW','MODEM_FUSE_OVLO','RC0603FR-07237KL','1%'),('R1914','100kR',769.62,104.14,'MODEM_FUSE_OVLO','GND','RC0603FR-07100KL','1%'),('R1915','165kR',800.1,55.88,'MODEM_VCC','MODEM_FUSE_PGTH','RC0603FR-07165KL','1%'),('R1916','100kR',800.1,104.14,'MODEM_FUSE_PGTH','GND','RC0603FR-07100KL','1%'),('R1917','562R',609.6,223.52,'MODEM_FUSE_ILM','GND','RT0603BRD07562RL','0.1%'),('R1918','10kR',769.62,162.56,'+3V3','MODEM_SWITCH_GOOD','RC0603FR-0710KL','1%')]:s.passive('R',ref,val,x,y,a,b,mpn,'Resistor_SMD:R_0603_1608Metric','Yageo',{'Tolerance':tol,'Power Rating':'0.1W'})
s.passive('C','C1911','10nF',688.34,223.52,'MODEM_FUSE_DVDT','GND','CL10B103KB8NNNC','Capacitor_SMD:C_0603_1608Metric','Samsung Electro-Mechanics',{'Voltage Rating':'50V','Dielectric':'X7R','Nominal Output Slew':'0.2V/ms, about 18.5ms to 3.7V'})
s.cap('C1912','100nF',769.62,223.52,'MODEM_3V7_RAW')
s.note('Latch-off eFuse: 45mOhm maximum RON. 562R/0.1% gives approx. 5.27–6.45A threshold\nusing the 549R guaranteed table, NOT 5A continuous connector qualification. ITIMER open.\nOVLO: 237k/100k, 3.93–4.18V resistor/reference corners, below modem 4.4V limit.\nPGTH: 165k/100k, nominal 3.18V. Use separate always-on output monitor for USB isolation.\nMaximum continuous device current is 5.5A; connector/profile hot limits can be lower.\nNo UL assembly claim: this threshold does not meet the datasheet RILM>=750R recognition condition.',591.82,294.64)
# Rail monitor stays alive when eFuse or regulator is cut.
mpins=native_pins(ROOT/'reference/nic-controls-native-candidates.kicad_sym','TPS3808G01DBVR')
assert mpins=={'1':'RESET','2':'GND','3':'MR','4':'CT','5':'SENSE','6':'VDD'}
raw=(ROOT/'reference/tps3808-captured.kicad_sym').read_text();mon=block(raw,raw.index('(symbol "TPS3808_DBV"'))
p=s.symbol('Appliance:TPS3808_DBV',mon,'U1903','TPS3808G01DBVR',119.38,401.32,'Package_TO_SOT_SMD:SOT-23-6',{'MPN':'TPS3808G01DBVR','Manufacturer':'Texas Instruments','LCSC':'C19653','Datasheet':'https://www.ti.com/lit/ds/symlink/tps3808.pdf'})
s.attach(p,{'1':'MODEM_RAIL_GOOD','2':'GND','3':'+3V3','4':'MODEM_MON_CT','5':'MODEM_MON_SENSE','6':'+3V3'})
s.resistor('R1926','100kR',332.74,454.66,'+3V3','MODEM_MON_CT','RC0603FR-07100KL')
for ref,val,x,y,a,b,mpn in [('R1921','330kR',251.46,363.22,'MODEM_VCC','MODEM_MON_SENSE','RT0603BRD07330KL'),('R1922','47kR',251.46,411.48,'MODEM_MON_SENSE','GND','RT0603BRD0747KL'),('R1923','10kR',332.74,401.32,'+3V3','MODEM_RAIL_GOOD','RC0603FR-0710KL')]:
 s.passive('R',ref,val,x,y,a,b,mpn,'Resistor_SMD:R_0603_1608Metric','Yageo',{'Tolerance':'0.1%' if ref in ['R1921','R1922'] else '1%','Power Rating':'0.1W'})
s.cap('C1913','100nF',187.96,401.32,'+3V3')
# NMOS discharge active when command is off. Logic inverter runs from the independent supply.
p=s.symbol('74xGxx:74LVC1G04',stock('74xGxx','74LVC1G04'),'U1904','SN74LVC1G04DCKR',429.26,401.32,'Package_TO_SOT_SMD:SOT-353_SC-70-5',{'MPN':'SN74LVC1G04DCKR','Manufacturer':'Texas Instruments','Datasheet':'https://www.ti.com/lit/ds/symlink/sn74lvc1g04.pdf'})
s.attach(p,{'1':None,'2':'MCU_MODEM_POWER_EN','3':'GND','4':'MODEM_DISCHARGE_GATE','5':'+3V3'})
s.cap('C1914','100nF',495.3,401.32,'+3V3')
p=s.symbol('Transistor_FET:AO3400A',stock('Transistor_FET','AO3400A'),'Q1901','AO3400A',607.06,416.56,'Package_TO_SOT_SMD:SOT-23',{'MPN':'AO3400A','Manufacturer':'Alpha & Omega Semiconductor','LCSC':'C20917','Datasheet':'https://www.aosmd.com/res/data_sheets/AO3400A.pdf'})
s.attach(p,{'1':'MODEM_DISCHARGE_GATE','2':'GND','3':'MODEM_DISCHARGE_DRAIN'})
s.passive('R','R1924','100R / 0.25W',688.34,401.32,'MODEM_VCC','MODEM_DISCHARGE_DRAIN','RC1206FR-07100RL','Resistor_SMD:R_1206_3216Metric','Yageo',{'Power Rating':'0.25W','Tolerance':'1%','Qualification':'Worst on-time <=0.15W at 3.75V; RC discharge must be measured at socket'})
s.resistor('R1925','100kR',769.62,401.32,'MCU_MODEM_POWER_EN','GND','RC0603FR-07100KL')
s.note('U1903 is powered from always-on 3.3V; output threshold nominal 3.249V.\nCT via 100k to VDD: 180–420ms delay exceeds Sierra 100ms no-drive interval.\nMODEM_RAIL_GOOD drives data isolation and MCU PB13 (pad25). MCU PA0 controls power.\nLow command enables Q1901 discharge; wait at least 1s and bench-verify socket <0.1V\nbefore restart. MCU default/high-Z command is off. Qualify timing per modem profile.\nClear a latched fault only after determining cause; do not create an autonomous reset loop.',25.4,508)
s.save()
for name,body in [('tps54620',reg),('tps259474',fuse)]:
 (ROOT/f'reference/{name}-captured.kicad_sym').write_text('(kicad_symbol_lib (version 20211014) (generator eeschema) '+body+')\n')
