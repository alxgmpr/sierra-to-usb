"""RK809 control-page capture; explicit unused audio termination."""
import json
from schematic import ROOT, Sheet


def pmic_control():
    s=Sheet('pmic-control','PMIC control, RTC and unused audio')
    caps=json.loads((ROOT/'research/core-power-capacitors.json').read_text())

    def cap(ref,value,x,y):
        part=caps['one_uF' if value=='1uF' else 'ten_uF']['results'][0]
        package='0402_1005' if value=='1uF' else '0603_1608'
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
    s.text('RTC, system control and processor-side signals are being captured.\nThis page is incomplete and cannot authorize fabrication.',20.32,30.48,1.27)
    return s
