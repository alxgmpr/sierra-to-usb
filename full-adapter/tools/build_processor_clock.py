"""24MHz oscillator and PMU analog reference, from Rockchip reference circuit."""
import json
from schematic import ROOT,Sheet


def processor_clock():
    s=Sheet('processor-clock','Processor 24MHz clock and temperature reference')
    source=json.loads((ROOT/'research/processor-clock-parts.json').read_text())
    def part(name,ref,key,value,x,y,angle=0,footprint=None):
        p=source[key]
        return s.place(name,ref,x,y,value=value,angle=angle,fields={
            'MPN':p['model'],'LCSC':p['lcsc'],'Manufacturer':p['manufacturer'],
            'Datasheet':p.get('datasheet',''),
            'Footprint':footprint or ('Capacitor_SMD:C_0402_1005Metric' if ref[0]=='C' else 'Resistor_SMD:R_0402_1005Metric')})
    s.box('PMU oscillator and analog reference',15.24,15.24,165.1,116.84)
    s.place('full-adapter:RK3568B2','U1',86.36,71.12,unit=35)
    s.connect('U1','AF28','SOC_XIN24M',5.08)
    s.connect('U1','AF27','SOC_XOUT24M',12.7)
    p=s.pins['U1','AB24'];end=(45.72,p[1])
    s.wire(p,end);s.wire(end,(45.72,86.36));s.power('GND',(45.72,86.36))
    for ball in ['AB23','AC24','AD25','AE26']:s.connect('U1',ball,None)
    s.text('TVSS is a temperature-reference INPUT.\nGround AB24 as shown in the Rockchip tablet reference.\nThe four spare PMU GPIOs are unused.',22.86,106.68,1.1)
    s.box('24MHz fundamental crystal — short, quiet local loop',190.5,15.24,215.9,167.64)
    # Feedback is across processor XIN/XOUT, before the XOUT series resistor.
    r=part('Device:R_Small_US','R570','feedback_resistor','1MR 1%',297.18,50.8,90)
    s.wire(r['1'],(223.52,50.8));s.wire(r['2'],(381,50.8))
    s.label('SOC_XIN24M',(223.52,50.8),180)
    s.label('SOC_XOUT24M',(381,50.8))
    p=json.loads((ROOT/'research/pmic-control-passives.json').read_text())['resistor_22']['results'][0]
    r=s.place('Device:R_Small_US','R571',381,78.74,value='22R 1%',fields={
        'Footprint':'Resistor_SMD:R_0402_1005Metric','MPN':p['model'],'LCSC':p['lcsc'],'Manufacturer':p['manufacturer']})
    s.wire((381,50.8),r['1']);s.wire(r['2'],(381,109.22))
    y=part('Device:Crystal_GND24','Y570','crystal','24MHz / 12pF',299.72,109.22,
           footprint='full-adapter:Yajingxin_TXM_3225_24MHz')
    s.wire(y['1'],(223.52,109.22));s.wire(y['3'],(381,109.22))
    s.wire((223.52,50.8),(223.52,109.22))
    s.label('SOC_XTAL_OUT',(381,109.22))
    s.wire(y['2'],(299.72,127));s.power('GND',(299.72,127))
    for ref,x in [('C570',223.52),('C571',381)]:
        c=part('Device:C',ref,'load_capacitor','20pF C0G',x,129.54)
        s.wire((x,109.22),c['1']);s.junction((x,109.22))
        s.wire(c['2'],(x,139.7));s.power('GND',(x,139.7))
    s.text('ESR <=30R; initial +/-10ppm; -40 to +85C, stability +/-20ppm.\n20pF each gives CL=12pF with estimated 2pF combined stray.\nRetain R571=22R and R570=1MR per Rockchip HW Guide.',198.12,157.48,1.1)
    s.box('Layout and bring-up requirements',15.24,198.12,391.16,50.8)
    s.text('Place Y570, R570/R571 and C570/C571 beside U1 AF27/AF28; keep clock copper short, on one layer and away from switch nodes.\nGround the crystal case pins 2/4 locally; use a quiet ground reference and avoid unrelated traces beneath the oscillator loop.\nMeasure startup margin, frequency and drive across supply/temperature. Treat the listed 100uW crystal drive as a conservative ceiling.\nLoad capacitors require tuning after PCB parasitics are known. CLK32K_IN remains unused; configure the internal PVTM low-speed clock.',22.86,213.36,1.1)
    s.text('Sources: Rockchip RK3568 HW Guide V1.2, clock section 2.2.2.3; tablet reference p13; Yajingxin exact-MPN datasheet p1.\nThis page captures the processor oscillator. Complete board integration, routing and release validation remain unfinished.',20.32,269.24,1.1)
    return s
