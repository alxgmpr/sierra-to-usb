"""Native CM4 PHY, four-pair PoE extraction and galvanically isolated termination."""
import json
from cad import ROOT, Sheet

PARTS = {}
for path,key in [('ethernet-parts.json','selected'),('ethernet-passives.json','parts')]:
    PARTS.update({p['model']:p for p in json.loads((ROOT/'research'/path).read_text())[key]})


def exact_part(s, symbol, ref, value, mpn, footprint, x, y, angle=0):
    p = PARTS[mpn]
    return s.place(symbol,ref,x,y,value=value,angle=angle,fields={
        'MPN':mpn,'Manufacturer':p['manufacturer'],'LCSC':p['lcsc'],
        'Footprint':footprint,'Datasheet':p.get('datasheet') or ''})


def ethernet_data():
    from build_core import cap
    s=Sheet('ethernet-data','Gigabit Ethernet / isolation and ESD')
    s.box('Four 1:1 channels / HX6096NL / 1500 Vrms isolation',10.16,15.24,203.2,246.38)
    for channel,y in enumerate([53.34,109.22,165.1,220.98]):
        p=s.place('cm4:HX6096NL','T120',111.76,y,unit=channel+1)
        a,b=channel*3,24-channel*3
        for n,pol in [(a+2,'P'),(a+3,'N')]:
            s.connect('T120',str(n),f'ETH_MDI{channel}_{pol}',global_net=True)
        for n,pol in [(b-1,'P'),(b-2,'N')]:
            s.connect('T120',str(n),f'ETH_CABLE{channel}_{pol}',global_net=True)
        s.connect('T120',str(b),'POE_CT_'+'ABCD'[channel],global_net=True)
        c=cap(s,f'C{120+channel}','100nF',60.96,y+17.78)
        s.wire(p[str(a+1)],(60.96,p[str(a+1)][1]))
        s.wire((60.96,p[str(a+1)][1]),c['1'])
        s.wire(c['2'],(60.96,y+27.94));s.power('GND',(60.96,y+27.94))
    s.box('Shielded Cat5e SMT connector / 1.5 A per contact',226.06,15.24,177.8,106.68)
    p=s.place('cm4:855437002','J120',342.9,71.12)
    for channel,pins in enumerate([(1,2),(3,6),(4,5),(7,8)]):
        for pin,pol in zip(pins,['P','N']):
            s.connect('J120',str(pin),f'ETH_CABLE{channel}_{pol}',global_net=True)
    s.wire(p['SH'],(p['SH'][0],104.14));s.power('GND',(p['SH'][0],104.14))
    s.box('Low-capacitance protection on the CM4 side only',226.06,134.62,177.8,127)
    for i,x in enumerate([276.86,365.76]):
        p=exact_part(s,'Power_Protection:TPD4EUSB30',f'U{120+i}','TPD4EUSB30DQAR',
            'TPD4EUSB30DQAR','cm4:TI_DQA0010_TPD4EUSB30',x,195.58)
        s.field_position(f'U{120+i}','Reference',x,175.26)
        s.field_position(f'U{120+i}','Value',x,177.8)
        for pin,ch,pol in [('1',2*i,'P'),('2',2*i,'N'),('4',2*i+1,'P'),('5',2*i+1,'N')]:
            s.connect(f'U{120+i}',pin,f'ETH_MDI{ch}_{pol}',global_net=True)
        for pin in ['3','8']:s.connect(f'U{120+i}',pin,'GND',global_net=True)
        for pin in ['6','7','9','10']:s.connect(f'U{120+i}',pin,None)
    s.text('No VCC connection: ESD arrays cannot inject into a stopped 3.3 V rail.\nKeep eight MDI branches short; arrays do not belong on 57 V cable pairs.\nPHY centre taps use 100 nF to GND, per the CM4 reference circuit.',233.68,231.14)
    return s


def ethernet_termination():
    s=Sheet('ethernet-termination','PoE Ethernet / common-mode termination')
    s.box('Four independent media centre taps / preserve both PoE pair sets',10.16,15.24,393.7,152.4)
    for i,x in enumerate([66.04,147.32,228.6,309.88]):
        c=exact_part(s,'Device:C',f'C{130+i}','22nF 100V','CC0603KRX7R0BB223',
            'Capacitor_SMD:C_0603_1608Metric',x,68.58)
        s.wire(c['1'],(x,48.26));s.label('POE_CT_'+'ABCD'[i],(x,48.26),0,True)
        r=exact_part(s,'Device:R_Small_US',f'R{130+i}','75R 1%','0603WAF750JT5E',
            'Resistor_SMD:R_0603_1608Metric',x,106.68)
        s.wire(c['2'],r['1']);s.wire(r['2'],(x,129.54))
    s.wire((66.04,129.54),(309.88,129.54))
    for x in [147.32,228.6]:s.junction((x,129.54))
    s.label('POE_BOB_SMITH',(309.88,129.54))
    s.text('Series capacitors prevent a DC load between PoE centre taps.\nDo not bridge these capacitors or join opposite-polarity taps through 75R.\nCT_A / CT_B feed one rectifier; CT_C / CT_D feed the second rectifier.',17.78,142.24)
    s.box('Safety capacitor crosses the primary / secondary isolation barrier',10.16,180.34,393.7,81.28)
    c=exact_part(s,'Device:C','C134','1nF Y1 400VAC','CY1102ME14EF45W2A2',
        'cm4:Dersonic_CY1102ME14EF45W2A2_P10mm',76.2,220.98)
    s.wire(c['1'],(76.2,205.74));s.label('POE_BOB_SMITH',(76.2,205.74))
    s.wire(c['2'],(76.2,241.3));s.power('GND',(76.2,241.3))
    s.text('C134 is an approved Y1 capacitor; ordinary MLCC substitution prohibited.\nThe RJ45 shield connects to the accessible secondary ground.\nKeep all primary copper clear of secondary copper and mounting hardware.\nPoE bridge / PD / isolated conversion: integration remains in progress.\nEnforce the isolation barrier in PCB rules, including inner layers.',157.48,208.28)
    return s
