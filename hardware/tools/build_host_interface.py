#!/usr/bin/env python3
"""Capture documented boot straps, protected recovery USB and host supervision."""
from capture import ROOT, Sheet, stock, block, grouped

s = Sheet('host-interface', 'Processor recovery and supervision', 'A2')
import re
usb=grouped('USB_B_Micro_Device',{'1':'VBUS','2':'D-','3':'D+','4':'ID','5':'GND','6':'Front shell','SH':'Retention shell'},[{'left':['1','2','3','4'],'bottom':['5','6','SH']}],{n:'passive' for n in ['1','2','3','4','5','6','SH']})
# Port ground is a passive connection to system ground, not a second regulator.
(ROOT/'reference/micro-usb-captured.kicad_sym').write_text('(kicad_symbol_lib (version 20211014) (generator eeschema) '+usb+')\n')
s.rectangle('BOOT CONFIGURATION AND LOCAL I/O BYPASS',20.32,20.32,254,111.76)
s.resistor('R1201','10kR',63.5,60.96,'VCC3V3_PMU','FLASH_VOL_SEL','RC0603FR-0710KL')
s.resistor('R1202','10kR',124.46,60.96,'VCC3V3_PMU','SDMMC0_DET','RC0603FR-0710KL')
s.note('FLASH_VOL_SEL high selects 1.8V eMMC I/O.\nSDMMC0_DET high selects debug mux; no SD boot connector fitted.',30.48,111.76)
for i,rail in enumerate(['3V3_MAIN','VCC_1V8','VCCIO_SD','VCC_1V8','VCC_1V8','VCC_1V8','VCC_1V8','VCC_1V8','3V3_MAIN']):
    s.cap(f'C{1201+i}','100nF',304.8+25.4*(i%5),50.8+53.34*(i//5),rail)
s.note('One 100nF capacitor at every VCCIO ball:\n1D13, 1C13, 1F17, 1E16, 1N5/6, 1L4/5, 1N8.\nKeep unused peripherals disabled. Check domain voltages in DT.',289.56,127)

s.rectangle('USB OTG0 — DEVICE-ONLY RECOVERY PORT',20.32,147.32,259.08,190.5)
p=s.symbol('Appliance:USB_B_Micro_Device',usb,'J1201','RECOVERY USB',73.66,208.28,'Connector_USB:USB_Micro-B_Amphenol_10103594-0001LF_Horizontal',{'MPN':'10103594-0001LF','Manufacturer':'Amphenol ICC','LCSC':'C428495'})
s.attach(p,{'1':'RECOVERY_VBUS','2':'RECOVERY_DM_PORT','3':'RECOVERY_DP_PORT','4':None,'5':'GND','6':'GND','SH':'GND'})
for ref,y,a,b in [('R1203',195.58,'RECOVERY_DP_PORT','RECOVERY_USB_DP'),('R1204',220.98,'RECOVERY_DM_PORT','RECOVERY_USB_DM')]:
    s.resistor(ref,'2.2R',185.42,y,a,b,'RC0603FR-072R2L',horizontal=True)
p=s.symbol('Power_Protection:TPD2EUSB30',stock('Power_Protection','TPD2EUSB30'),'D1201','TPD2EUSB30DRTR',127,274.32,'Appliance:SOT-9X3-3_L1.0-W0.8-P0.35-LS1.0-BR',{'MPN':'TPD2EUSB30DRTR','Manufacturer':'Texas Instruments','LCSC':'C97502','Datasheet':'https://www.ti.com/lit/ds/symlink/tpd2eusb30.pdf'})
s.attach(p,{'1':'RECOVERY_DP_PORT','2':'RECOVERY_DM_PORT','3':'GND'})
s.resistor('R1205','10kR',223.52,269.24,'RECOVERY_VBUS','RECOVERY_VBUS_DET','RC0603FR-0710KL')
s.resistor('R1206','16.5kR',223.52,307.34,'RECOVERY_VBUS_DET','GND','RC0603FR-0716K5L')
s.note('VBUS senses cable presence only; it does not power the board.\n10k/16.5k divider: 2.718–3.293V at 4.4–5.25V, 1% resistor corners.\nUSB OTG ID floats: internal 1.8V pull-up selects device mode.\nPlace ESD at port; route DP/DM as a short 90-ohm pair.\nRecovery through Rockusb/MaskROM still requires device testing.',30.48,320.04)

s.rectangle('POWERED-OFF-SAFE HEALTH AND DEBUG UART',299.72,157.48,251.46,180.34)
buf=stock('74xGxx','SN74LVC1G125DCK')
for ref,x,y,inp,out,rail in [
    ('U1201',350.52,203.2,'SOC_HEALTH','MCU_HEALTH_IN','+3V3'),
    ('U1202',350.52,269.24,'DEBUG_UART_TX','UART_TX_PORT','VCC3V3_PMU'),
    ('U1203',472.44,269.24,'UART_RX_PORT','DEBUG_UART_RX','VCC3V3_PMU'),
]:
    p=s.symbol('74xGxx:SN74LVC1G125DCK',buf,ref,'SN74LVC1G125DCKR',x,y,'Package_TO_SOT_SMD:SOT-353_SC-70-5',{'MPN':'SN74LVC1G125DCKR','Manufacturer':'Texas Instruments','LCSC':'C7833','Datasheet':'https://www.ti.com/lit/ds/symlink/sn74lvc1g125.pdf','Qualification':'Ioff; inputs tolerate 5.5V. Debug is 3.3V TTL, not RS232'})
    s.attach(p,{'1':'GND','2':inp,'3':'GND','4':out,'5':rail})
for ref,net,x,y in [('R1207','SOC_HEALTH',487.68,195.58),('R1208','MCU_HEALTH_IN',487.68,223.52),('R1209','UART_RX_PORT',487.68,312.42)]:
    s.resistor(ref,'100kR',x,y,net,'GND','RC0603FR-07100KL')
for i,(x,y,rail) in enumerate([(401.32,203.2,'+3V3'),(411.48,307.34,'VCC3V3_PMU'),(449.58,307.34,'VCC3V3_PMU')]):
    s.cap(f'C{1210+i}','100nF',x,y,rail)
p=s.symbol('Connector_Generic:Conn_01x03',stock('Connector_Generic','Conn_01x03'),'J1202','3.3V DEBUG UART',563.88,269.24,'Connector_PinHeader_2.54mm:PinHeader_1x03_P2.54mm_Vertical',{'MPN':'61300311121','Manufacturer':'Wurth Elektronik'})
s.attach(p,{'1':'UART_TX_PORT','2':'UART_RX_PORT','3':'GND'})
s.note('GPIO0_C4 (AN37), 3.3V PMUIO2: firmware health toggles.\nU1201 runs from always-on 3.3V; both sides default low.\nUART2_M0: 1V19 RX, 1U18 TX; buffers prevent back-power.',307.34,332.74)

# Hardware thermal emergency sinks the shared processor/PMIC reset.
raw=(ROOT/'controls.kicad_sch').read_text();bjt=block(raw,raw.index('(symbol "Transistor_BJT:MMBT3904"'))
p=s.symbol('Transistor_BJT:MMBT3904',bjt,'Q1201','MMBT3904,215',223.52,378.46,'Package_TO_SOT_SMD:SOT-23',{'MPN':'MMBT3904,215','Manufacturer':'Nexperia'})
s.attach(p,{'1':'THERMAL_RESET_BASE','2':'GND','3':'RK_RESET_N'})
s.resistor('R1210','10kR',76.2,378.46,'TSADC_SHUTDOWN','THERMAL_RESET_BASE','RC0603FR-0710KL',horizontal=True)
s.resistor('R1211','100kR',304.8,378.46,'THERMAL_RESET_BASE','GND','RC0603FR-07100KL')
s.note('Configure TSADC_SHUT_M0 (1R20) active high.\nHardware overtemperature asserts RK_RESET_N via Q1201.\nCPU temperature thresholds and restart policy require qualification.',381,381)
s.save()
