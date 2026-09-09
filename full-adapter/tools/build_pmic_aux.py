"""RK809 BUCK5 and independent sequenced 3.3 V switches."""
import json
from schematic import ROOT, Sheet


def pmic_aux():
    s=Sheet('pmic-aux','1.8V system buck and switched 3.3V supplies')
    source=json.loads((ROOT/'research/pmic-buck-passives.json').read_text())
    cap22=next(p for p in json.loads((ROOT/'research/cpu-passives-search-2.json').read_text())[3]['result']['results']
               if p['model']=='CL21A226MAYNNNE')
    cap1=json.loads((ROOT/'research/core-power-capacitors.json').read_text())['one_uF']['results'][0]
    parts={'22uF':cap22,'1uF':cap1,'0.47uH':source['inductor']['results'][0]}

    def passive(ref,value,x,y,angle=0):
        part=parts[value]
        if ref.startswith('L'):lib,fp='Device:L','full-adapter:L_TDK_SPM5030'
        else:lib,fp='Device:C','Capacitor_SMD:C_'+('0805_2012' if value=='22uF' else '0402_1005')+'Metric'
        return s.place(lib,ref,x,y,value=value,angle=angle,fields={
            'Footprint':fp,'Manufacturer':part['manufacturer'],'MPN':part['model'],'LCSC':part['lcsc']})

    s.box('BUCK5: 1.8V, slot 2, 2.5A max; SWOUT1: 3.3V, slot 4, 2.1A max',10.16,15.24,396.24,142.24)
    u=s.place('full-adapter:RK809-5','U5',147.32,66.04,unit=5)
    for i,x in enumerate([35.56,66.04]):
        c=passive(f'C{460+i}','22uF',x,81.28)
        s.wire((x,63.5),c['1']);s.wire(c['2'],(x,91.44))
    s.wire((35.56,63.5),u['54']);s.junction((66.04,63.5))
    s.wire((35.56,63.5),(35.56,53.34));s.junction((35.56,63.5));s.power('VCC3V3_SYS',(35.56,53.34))
    s.wire((35.56,91.44),(66.04,91.44));s.power('GND',(66.04,91.44))
    l=passive('L460','0.47uH',223.52,63.5,angle=90)
    a,b=sorted(l.values(),key=lambda p:p[0]);s.wire(u['53'],a);s.wire(b,(391.16,63.5))
    s.power('VCC1V8_SYS',(375.92,63.5));s.junction((375.92,63.5))
    s.place('power:PWR_FLAG','#FLG1v8',391.16,63.5)
    for i,x in enumerate([279.4,312.42,345.44]):
        c=passive(f'C{462+i}','22uF',x,86.36)
        s.wire((x,63.5),c['1']);s.junction((x,63.5));s.wire(c['2'],(x,96.52))
        if i:s.wire((x-33.02,96.52),(x,96.52))
        if i==1:s.junction((x,96.52))
    s.power('GND',(345.44,96.52))
    s.wire(u['59'],(111.76,66.04));s.wire((111.76,66.04),(111.76,109.22))
    s.power('VCC1V8_SYS',(111.76,109.22))
    # SWOUT1 is supplied from VCC9, not from BUCK5's 1.8 V output.
    s.wire(u['55'],(185.42,66.04));s.wire((185.42,66.04),(185.42,119.38))
    s.wire((185.42,119.38),(248.92,119.38));s.power('VCC3V3_S0',(248.92,119.38))
    c=passive('C465','1uF',248.92,132.08)
    s.wire((248.92,119.38),c['1']);s.wire(c['2'],(248.92,139.7));s.power('GND',(248.92,139.7))
    s.text('FB5 senses the 1.8V output bank.\nSWOUT1 carries the 3.3V input rail.\nInclude switch resistance/drop in load budget.',279.4,121.92,1.27)
    s.box('SWOUT2: SD-card power, slot 4, 2.1A maximum',10.16,172.72,396.24,73.66)
    u=s.place('full-adapter:RK809-5','U5',147.32,200.66,unit=9)
    vin=u['57'];out=u['58']
    s.wire(vin,(66.04,vin[1]));s.power('VCC3V3_SYS',(66.04,vin[1]))
    c=passive('C466','1uF',66.04,220.98)
    s.wire((66.04,vin[1]),c['1']);s.wire(c['2'],(66.04,228.6));s.power('GND',(66.04,228.6))
    s.wire(out,(248.92,out[1]));s.power('VCC3V3_SD',(248.92,out[1]))
    c=passive('C467','1uF',248.92,220.98)
    s.wire((248.92,out[1]),c['1']);s.wire(c['2'],(248.92,228.6));s.power('GND',(248.92,228.6))
    s.text('RK809-5 Table 4-4 and AN_RK809 V1.1 section 6.4. BUCK5 local output: 3 x 22uF.\nVCC3V3_S0 is a sequenced main rail; VCC3V3_SD powers the card, VCC_SDIO powers its I/O domain.\nNeither switched rail may backfeed an unpowered processor through external interfaces.',15.24,261.62,1.27)
    return s
