"""RK809 control-page capture; explicit unused audio termination."""
import json
from schematic import ROOT, Sheet


def pmic_control():
    s=Sheet('pmic-control','PMIC control, RTC and unused audio')
    caps=json.loads((ROOT/'research/core-power-capacitors.json').read_text())
    source=json.loads((ROOT/'research/pmic-control-passives.json').read_text())
    cap100=json.loads((ROOT/'research/ddr-passives-search.json').read_text())['searches'][6]['results'][0]

    def cap(ref,value,x,y):
        part=({'100nF':cap100,'22pF':source['load_capacitor']['results'][0]}[value]
              if value in {'100nF','22pF'} else caps['one_uF' if value=='1uF' else 'ten_uF']['results'][0])
        package='0603_1608' if value=='10uF' else '0402_1005'
        return s.place('Device:C',ref,x,y,value=value,fields={
            'Footprint':f'Capacitor_SMD:C_{package}Metric','Manufacturer':part['manufacturer'],
            'MPN':part['model'],'LCSC':part['lcsc']})

    s.box('Audio unused — retain internal supply bypass',210.82,15.24,195.58,124.46)
    u=s.place('full-adapter:RK809-5','U5',299.72,81.28,unit=11)
    grounded=['14','15','16','17','19']
    for pin in grounded:s.wire(u[pin],(264.16,u[pin][1]))
    ys=sorted(u[pin][1] for pin in grounded)
    for a,b in zip(ys,ys[1:]):s.wire((264.16,a),(264.16,b))
    for y in ys[1:-1]:s.junction((264.16,y))
    s.wire((264.16,ys[0]),(264.16,60.96));s.power('GND',(264.16,60.96))
    s.wire(u['40'],(266.7,u['40'][1]));s.wire((266.7,u['40'][1]),(266.7,104.14))
    s.power('GND',(266.7,104.14))
    s.wire(u['33'],(226.06,u['33'][1]));s.power('VCC3V3_SYS',(226.06,u['33'][1]))
    c=cap('C482','10uF',226.06,101.6)
    s.wire((226.06,u['33'][1]),c['1']);s.wire(c['2'],(226.06,111.76));s.power('GND',(226.06,111.76))
    for pin,ref,x,name in [('44','C480',381,'RK809_1P8A'),('48','C481',345.44,'RK809_1P8D')]:
        s.wire(u[pin],(x,u[pin][1]));s.wire((x,u[pin][1]),(x,96.52));s.label(name,(x,96.52))
        c=cap(ref,'1uF',x,109.22)
        s.wire((x,96.52),c['1']);s.wire(c['2'],(x,119.38));s.power('GND',(x,119.38))
    for pin in ['18','32','34','35','36','37','38','39','41','42','43']:s.connect('U5',pin,None)
    s.text('Ground/open pins follow Rockchip tablet reference p22.\nVCC_1P8A/D are internal outputs; never feed external 1.8V into them.\nVCC_SPK_HP accepts 2.7–5.5V; 3.3V is retained with codec disabled.',218.44,129.54,1.0)
    resistors={v:source[k]['results'][0] for v,k in [('22R 1%','resistor_22'),('2.2kR 1%','pullup_2k2'),
                ('10kR 1%','pullup_10k'),('56kR 1%','divider_56k')]}
    resistors['100kR 1%']=json.loads((ROOT/'research/cpu-control-resistors.json').read_text())[2]['result']['results'][0]
    def resistor(ref,value,x,y,angle=0):
        p=resistors[value]
        return s.place('Device:R_Small_US',ref,x,y,value=value,angle=angle,fields={
            'Footprint':'Resistor_SMD:R_0402_1005Metric','Manufacturer':p['manufacturer'],
            'MPN':p['model'],'LCSC':p['lcsc']})

    s.box('RK809-5 control — PMU I/O levels',10.16,15.24,190.5,78.74)
    u=s.place('full-adapter:RK809-5','U5',101.6,63.5,unit=10)
    s.wire(u['45'],(76.2,u['45'][1]));s.power('VCC3V3_SYS',(76.2,u['45'][1]))
    for pin,net in [('1','RK809_SCL'),('2','RK809_SDA'),('50','RK809_XIN'),('51','RK809_XOUT'),('46','RK809_VREF'),('61','RK809_VDC')]:
        s.connect('U5',pin,net,5.08)
    for pin,net in [('49','PMIC_SLEEP_H'),('52','PMIC_PWRON_L'),('7','PMIC_INT_L'),('67','SYS_RESET_L')]:
        s.connect('U5',pin,net,5.08,global_net=True)
    for pin in ['68','60']:s.connect('U5',pin,None)
    for pins,x in [(['56','62','63'],73.66),(['47','69'],129.54)]:
        ys=sorted(u[p][1] for p in pins)
        for pin in pins:s.wire(u[pin],(x,u[pin][1]))
        for a,b in zip(ys,ys[1:]):s.wire((x,a),(x,b))
        for y in ys[1:-1]:s.junction((x,y))
        s.wire((x,ys[-1]),(x,86.36));s.power('GND',(x,86.36))

    for i,signal in enumerate(['SCL','SDA']):
        x=40.64+i*99.06
        r=resistor(f'R{490+i}','22R 1%',x+25.4,121.92,angle=90)
        a,b=sorted(r.values(),key=lambda p:p[0])
        s.wire((x,121.92),a);s.label(f'I2C0_{signal}_PMIC',(x,121.92),180,global_net=True)
        s.wire(b,(x+40.64,121.92));s.label('RK809_'+signal,(x+40.64,121.92))
        r=resistor(f'R{492+i}','2.2kR 1%',x,109.22)
        s.wire(r['2'],(x,121.92));s.junction((x,121.92))
        s.wire(r['1'],(x,101.6));s.power('VCC1V8_PMU',(x,101.6))
    for i,net in enumerate(['SYS_RESET_L','PMIC_INT_L']):
        x=40.64+i*99.06
        r=resistor(f'R{494+i}','10kR 1%',x,157.48)
        s.wire(r['1'],(x,149.86));s.power('VCC3V3_PMU',(x,149.86))
        s.wire(r['2'],(x,170.18));s.label(net,(x,170.18),global_net=True)
        if i==0:
            c=cap('C486','100nF',x,185.42)
            s.wire((x,170.18),c['1']);s.wire(c['2'],(x,193.04));s.power('GND',(x,193.04))
    for ref,value,x,net in [('C483','1uF',40.64,'VCC3V3_SYS'),('C484','1uF',101.6,'RK809_VREF'),
                            ('C485','100nF',162.56,'PMIC_PWRON_L')]:
        c=cap(ref,value,x,223.52)
        s.wire((x,213.36),c['1'])
        if net=='VCC3V3_SYS':s.power(net,(x,213.36))
        else:s.label(net,(x,213.36),global_net=net=='PMIC_PWRON_L')
        s.wire(c['2'],(x,231.14));s.power('GND',(x,231.14))

    s.box('32.768kHz RTC — keep away from switching nodes',210.82,144.78,195.58,45.72)
    part=source['crystal']
    xtal=s.place('Device:Crystal','Y490',299.72,162.56,value='32.768kHz / 12.5pF',fields={
        'Footprint':'full-adapter:Epson_FC-135R_3.2x1.5mm','Manufacturer':part['manufacturer'],
        'MPN':part['model'],'LCSC':part['lcsc'],'Datasheet':source['manufacturer_pdf_url']})
    a,b=sorted(xtal.values(),key=lambda p:p[0])
    for i,(end,x,net) in enumerate([(a,269.24,'RK809_XIN'),(b,335.28,'RK809_XOUT')]):
        s.wire(end,(x,162.56));s.label(net,(x,162.56),180 if i==0 else 0)
        c=cap(f'C{488+i}','22pF',x,175.26)
        s.wire((x,162.56),c['1']);s.wire(c['2'],(x,182.88));s.power('GND',(x,182.88))

    s.box('Delayed auto-start',210.82,195.58,83.82,71.12)
    r=resistor('R496','100kR 1%',236.22,218.44)
    s.wire(r['1'],(236.22,208.28));s.power('VCC3V3_SYS',(236.22,208.28))
    s.wire(r['2'],(236.22,233.68));s.label('RK809_VDC',(236.22,233.68))
    r=resistor('R497','56kR 1%',236.22,246.38)
    s.wire((236.22,233.68),r['1']);s.junction((236.22,233.68))
    s.wire(r['2'],(236.22,256.54));s.power('GND',(236.22,256.54))
    c=cap('C487','1uF',279.4,246.38)
    s.wire((236.22,233.68),(279.4,233.68));s.wire((279.4,233.68),c['1'])
    s.wire(c['2'],(279.4,256.54));s.power('GND',(279.4,256.54))
    s.text('VDC: 1.185V, tau 35.9ms nominal. Require 3.3V supply rise <=10ms.\nVerify the VDC edge occurs after VCC_RTC/VCC9 are valid, including brownout recovery.\nPWRON uses its internal pull-up; reset retains the required 100nF capacitor.',15.24,248.92,1.0)
    s.text('I2C0 / PMUIO2: 1.8V. INT/reset: 3.3V PMU domain. See processor-control for host connections.\nRTC 22pF loads assume about 1.5pF stray; verify startup margin, drive level and frequency.',15.24,276.86,1.0)
    return s
