"""USB2 PHY filters and shared USB3/PCIe2 combo-PHY analog power."""
import json
from schematic import ROOT, Sheet


def processor_phy_power():
    s = Sheet('processor-phy-power','Processor USB and PCIe combo-PHY supplies')
    ddr = json.loads((ROOT/'research/ddr-passives-search.json').read_text())['searches']
    extra = json.loads((ROOT/'research/core-power-capacitors.json').read_text())
    parts = {'100nF':ddr[6]['results'][0], '4.7uF':ddr[7]['results'][0], '1uF':extra['one_uF']['results'][0]}

    def cap(ref,value,x,y):
        part = parts[value]
        package = '0603_1608' if part['package']=='0603' else '0402_1005'
        return s.place('Device:C',ref,x,y,value=value,fields={
            'Footprint':f'Capacitor_SMD:C_{package}Metric','MPN':part['model'],
            'Manufacturer':part['manufacturer'],'LCSC':part['lcsc']})

    s.box('PHY supply rails',10.16,15.24,396.24,200.66)
    pins = s.place('full-adapter:RK3568B2','U1',66.04,114.3,unit=41)
    rows = [
        ('M23','VCC3V3_S0','100nF','OTG0 / HOST1 USB2 PHY: 3.3V, 10mA peak'),
        ('P9','VCC1V8_USB','100nF','HOST2 / HOST3 USB2 PHY: 1.8V, 30mA peak'),
        ('P10','VCC3V3_S0','100nF','HOST2 / HOST3 USB2 PHY: 3.3V, 10mA peak'),
        ('P22','VDD0V9_USB','100nF','OTG0 / HOST1 USB2 PHY: 0.9V, 5mA peak'),
        ('P23','VCC1V8_USB','100nF','OTG0 / HOST1 USB2 PHY: 1.8V, 30mA peak'),
        ('R8','VDD0V9_USB','100nF','HOST2 / HOST3 USB2 PHY: 0.9V, 5mA peak'),
        ('R20','VDD0V9_ANLG','100nF','Combo PHY0/1/2: shared 0.9V, 150mA total peak'),
        ('R21','VDD0V9_ANLG','100nF','Second 0.9V ball; C549 local bulk'),
        ('R22','VCC1V8_ANLG','4.7uF','Combo PHY0/1/2: shared 1.8V, 21mA total peak'),
    ]
    for i,(ball,rail,value,note) in enumerate(rows):
        p=pins[ball]; y=p[1]
        s.wire(p,(154.94,y));s.power(rail,(154.94,y))
        c=cap(f'C{540+i}',value,220.98,y+5.08)
        s.wire((154.94,y),(220.98,y));s.wire((220.98,y),c['1'])
        s.wire(c['2'],(220.98,y+10.16));s.power('GND',(220.98,y+10.16))
        if ball=='R20':
            c=cap('C549','4.7uF',238.76,y+5.08)
            s.wire((220.98,y),(238.76,y));s.wire((238.76,y),c['1']);s.junction((220.98,y))
            s.wire(c['2'],(238.76,y+10.16));s.wire((220.98,y+10.16),(238.76,y+10.16))
        s.text(note,261.62,y+2.54,1.05)
    s.box('USB filters',10.16,220.98,396.24,30.48)
    for i,(source,target) in enumerate([('VDD0V9_ANLG','VDD0V9_USB'),('VCC1V8_ANLG','VCC1V8_USB')]):
        dx=i*195.58; y=231.14
        p=s.place('Device:FerriteBead',f'FB{550+i}',101.6+dx,y,angle=90,value='120R @ 100MHz',fields={
            'Footprint':'full-adapter:Murata_BLM18PG121SN1D_0603','MPN':'BLM18PG121SN1D',
            'Manufacturer':'Murata','LCSC':'C14709',
            'Datasheet':'https://www.mouser.cn/datasheet/2/281/ENFA0003-1915778.pdf'})
        s.wire((50.8+dx,y),p['1']);s.power(source,(50.8+dx,y))
        s.wire(p['2'],(152.4+dx,y));s.power(target,(152.4+dx,y))
        for j,x in enumerate([50.8+dx,152.4+dx]):
            c=cap(f'C{550+i*2+j}','1uF',x,y+5.08)
            s.wire((x,y),c['1']);s.wire(c['2'],(x,y+10.16));s.power('GND',(x,y+10.16))
        flag=s.place('power:PWR_FLAG',f'#FLG_USB{i}',185.42+dx,y)
        s.wire((152.4+dx,y),flag['1']);s.junction((152.4+dx,y))
    s.text('Rockchip tablet reference pp15/24; HW Guide V1.2 sections 2.2.2.9 / 2.2.2.10.\n100nF capacitors under U1; 4.7uF and filtered-rail bulk close to U1. USB filters include 1uF on each side.\nFB550/551: 0.05 ohm maximum initial DCR; 0.10 ohm after qualification tests. Peak DC drops: 1mV / 6mV at 0.10 ohm.',15.24,269.24,1.1)
    return s
