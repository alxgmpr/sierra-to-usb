"""Processor IO supply choices and per-ball bypass from Rockchip reference."""
import json
from schematic import ROOT, Sheet


def processor_io_power():
    s = Sheet('processor-io-power', 'Processor IO, ADC and OTP supplies')
    part = json.loads((ROOT/'research/ddr-passives-search.json').read_text())['searches'][6]['results'][0]
    s.box('IO rail assignments',10.16,15.24,396.24,236.22)
    pins = s.place('full-adapter:RK3568B2','U1',60.96,129.54,unit=40)
    rows = [
        ('H17','VCC3V3_S0','VCCIO1: 3.3V general-purpose IO'),
        ('H18','VCC1V8_SYS','VCCIO2: 1.8V storage IO; FLASH_VOL_SEL must be HIGH'),
        ('H20','VCC1V8_SYS','OTP: 1.8V, 59mA peak; powered for boot'),
        ('H22','VCC1V8_ANLG','SARADC: 1.8V, 1.5mA peak; powered for recovery'),
        ('J21','VCC3V3_S0','VCCIO4: 3.3V general-purpose IO'),
        ('L22','VCC_SDIO','VCCIO3: 3.3V startup; switchable 1.8V SD IO'),
        ('R9','VCC3V3_S0','VCCIO6: 3.3V, first supply ball'),
        ('U9','VCC3V3_S0','VCCIO6: 3.3V, second supply ball'),
        ('V10','VCC3V3_S0','VCCIO5: 3.3V, first supply ball'),
        ('V11','VCC3V3_S0','VCCIO5: 3.3V, second supply ball'),
        ('V12','VCC3V3_S0','VCCIO7: 3.3V general-purpose IO'),
    ]
    for i,(ball,rail,note) in enumerate(rows):
        p=pins[ball]; y=p[1]
        s.wire(p,(154.94,y));s.power(rail,(154.94,y))
        c=s.place('Device:C',f'C{520+i}',220.98,y+5.08,value='100nF',fields={
            'Footprint':'Capacitor_SMD:C_0402_1005Metric','MPN':part['model'],
            'Manufacturer':part['manufacturer'],'LCSC':part['lcsc']})
        s.wire((154.94,y),(220.98,y));s.wire((220.98,y),c['1'])
        s.wire(c['2'],(220.98,y+10.16));s.power('GND',(220.98,y+10.16))
        if ball == 'R9':
            bulk = json.loads((ROOT/'research/core-power-capacitors.json').read_text())['one_uF']['results'][0]
            c = s.place('Device:C','C531',238.76,y+5.08,value='1uF',fields={
                'Footprint':'Capacitor_SMD:C_0402_1005Metric','MPN':bulk['model'],
                'Manufacturer':bulk['manufacturer'],'LCSC':bulk['lcsc']})
            s.wire((220.98,y),(238.76,y));s.wire((238.76,y),c['1']);s.junction((220.98,y))
            s.wire(c['2'],(238.76,y+10.16));s.wire((220.98,y+10.16),(238.76,y+10.16))
        s.text(note,254.0,y+2.54,1.1)
    s.text('Rockchip tablet reference pp14/16/17/19/20; HW Guide V1.2 sections 2.2.2.8 / 2.2.2.16 / 2.2.2.17.\nPlace each 100nF under U1 near its ball; C531 (VCCIO6 bulk) close to U1. External IO current budgets remain open.\nVCCIO2 needs a physical HIGH strap; DTS does not set its voltage mode. IO3 must track the SD regulator voltage.',15.24,269.24,1.1)
    return s
