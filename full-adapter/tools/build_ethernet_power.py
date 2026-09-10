"""Forced-PWM Ethernet rails with controlled soft start and precision dividers."""
from collections import OrderedDict
import json
from schematic import ROOT,Sheet
from build_emmc import resistor,cap,tp
from build_recovery import props

MPN='TPS6281320QWRWYRQ1'
def regulator_symbol():
    from build_core_symbols import make_symbol
    pins=[(2,'VIN','power_in','L'),(8,'EN','input','L'),(1,'MODE/SYNC','input','L'),(7,'COMP/FSET','input','L'),
          (3,'SW','power_out','R'),(5,'FB','input','R'),(6,'SS/TR','input','R'),(9,'PG','open_collector','R'),(4,'GND','power_in','B')]
    units=OrderedDict([('3A buck',[dict(ball=str(n),name=name,type=t,side=side,pitch_mm=10.16) for n,name,t,side in pins])])
    return make_symbol(MPN,'full-adapter:TI_RWY0009_2x3mm','https://www.ti.com/lit/ds/symlink/tps62813-q1.pdf',
        'Texas Instruments','C1849536','3A adjustable buck; forced PWM, soft start, discharge and spread spectrum',units,
        keywords='buck regulator FPWM',footprint_filter='TI?RWY0009*',side_pins_from_top=True)

def ethernet_power(core=False):
    n=660 if core else 650
    ref='U13' if core else 'U12'
    rail='VDD0V95_ETH' if core else 'VCC3V3_ETH'
    vin='VCC3V3_ETH' if core else 'VCC5V_SYS'
    pg='ETH_CORE_PG' if core else 'ETH_3V3_PG'
    s=Sheet('ethernet-core-power' if core else 'ethernet-3v3-power',
            'Ethernet 0.95V forced-PWM supply' if core else 'Ethernet 3.3V forced-PWM supply')
    s.box(('0.950V core — controlled by RTL8125BG POW_EXT_SWR' if core else '3.318V auxiliary — enabled by the sequenced S0 rail'),10.16,15.24,396.24,190.5)
    part=json.loads((ROOT/'research/ethernet-regulator-stock.json').read_text())['passives']
    def passive(r,mpn,value,x,y,angle=0):
        p=part[mpn]
        lib,fp=('Device:L','full-adapter:L_TDK_SPM5030') if r.startswith('L') else ('Device:C','Capacitor_SMD:C_0603_1608Metric') if r.startswith('C') else ('Device:R_Small_US','Resistor_SMD:R_0603_1608Metric')
        return s.place(lib,r,x,y,angle=angle,value=value,fields={'MPN':mpn,'Manufacturer':p['manufacturer'],'LCSC':p['lcsc'],'Footprint':fp})
    u=s.place('full-adapter:'+MPN,ref,157.48,96.52)
    props(s,157.48,60.96)
    # Input ceramic bank is wired directly to VIN, away from the switch node.
    for i,x in enumerate([35.56,66.04]):
        c=cap(s,f'C{n+i}','22uF',x,60.96)
        s.wire(c['1'],(x,50.8));s.wire(c['2'],(x,68.58))
    s.wire((35.56,50.8),(106.68,50.8));s.junction((66.04,50.8));s.power(vin,(35.56,50.8))
    s.wire((35.56,68.58),(66.04,68.58));s.power('GND',(66.04,68.58))
    s.wire((106.68,50.8),(106.68,u['2'][1]));s.wire((106.68,u['2'][1]),u['2'])
    # MODE is hard-tied HIGH. FSET is hard-tied LOW: 2.25MHz, compensation1.
    s.wire((106.68,u['2'][1]),(106.68,u['1'][1]));s.junction((106.68,u['2'][1]));s.wire((106.68,u['1'][1]),u['1'])
    s.wire(u['7'],(116.84,u['7'][1]));s.wire((116.84,u['7'][1]),(116.84,157.48));s.power('GND',(116.84,157.48))
    s.wire(u['4'],(u['4'][0],157.48));s.power('GND',(u['4'][0],157.48))
    # The RTL core-enable source is integrated on the controller page next.
    # The pulldown makes the unfinished endpoint safely disabled meanwhile.
    en=(66.04,u['8'][1]);s.wire(en,u['8'])
    if core:s.label('ETH_CORE_ENABLE',en,180,global_net=True)
    else:s.power('VCC3V3_S0',en)
    r=resistor(s,f'R{n+2}','47kR 1%',66.04,134.62);s.wire(en,r['1']);s.junction(en);s.wire(r['2'],(66.04,147.32));s.power('GND',(66.04,147.32))
    l=passive(f'L{n}','SPM5030T-R47M','0.47uH',223.52,u['3'][1],90)
    a,b=sorted(l.values(),key=lambda p:p[0]);s.wire(u['3'],a);s.wire(b,(383.54,u['3'][1]));s.power(rail,(383.54,u['3'][1]))
    s.label('ETH_SW_CORE' if core else 'ETH_SW_3V3',u['3'])
    # Kelvin feedback at the output bank. Keep it away from SW during layout.
    top='RT0603BRD0714KL' if core else 'RT0603BRE0745K3L'
    bottom='RT0603BRD0724KL' if core else 'RT0603BRD0710KL'
    r=passive(f'R{n}',top,'14kR 0.1%' if core else '45.3kR 0.1%',246.38,129.54)
    s.wire((246.38,u['3'][1]),r['1']);s.junction((246.38,u['3'][1]));s.wire(r['2'],(246.38,152.4))
    r=passive(f'R{n+1}',bottom,'24kR 0.1%' if core else '10kR 0.1%',246.38,175.26)
    s.wire((246.38,152.4),r['1']);s.junction((246.38,152.4));s.wire(r['2'],(246.38,187.96));s.power('GND',(246.38,187.96))
    s.wire(u['5'],(215.9,u['5'][1]));s.wire((215.9,u['5'][1]),(215.9,152.4));s.wire((215.9,152.4),(246.38,152.4))
    c=passive(f'C{n+2}','GRM1885C1H103JA01D','10nF C0G',198.12,129.54)
    s.wire(u['6'],(198.12,u['6'][1]));s.wire((198.12,u['6'][1]),c['1']);s.wire(c['2'],(198.12,142.24));s.power('GND',(198.12,142.24))
    # Five local 22uF capacitors; local capacitance alone satisfies comp1.
    xs=[276.86,299.72,322.58,345.44,368.3]
    for i,x in enumerate(xs):
        c=cap(s,f'C{n+3+i}','22uF',x,109.22)
        s.wire((x,u['3'][1]),c['1']);s.junction((x,u['3'][1]));s.wire(c['2'],(x,121.92))
        if i:s.wire((xs[i-1],121.92),(x,121.92))
        if 0<i<4:s.junction((x,121.92))
    s.power('GND',(xs[-1],121.92))
    s.wire((383.54,u['3'][1]),(398.78,u['3'][1]));s.junction((383.54,u['3'][1]));s.place('power:PWR_FLAG',f'#FLGeth{n}',398.78,u['3'][1])
    # PG is available for later hardware reset qualification, not a tight UV monitor.
    s.connect(ref,'9',pg,5.08,global_net=True)
    r=resistor(s,f'R{n+3}','47kR 1%',309.88,172.72)
    s.wire(r['1'],(309.88,160.02));s.power('VCC3V3_ETH',(309.88,160.02));s.wire(r['2'],(309.88,187.96));s.label(pg,(309.88,187.96),180,global_net=True)
    t=tp(s,f'TP{n+1}',pg,360.68,177.8);props(s,360.68,165.1);s.wire(t['1'],(360.68,187.96));s.wire((309.88,187.96),(360.68,187.96));s.junction((309.88,187.96))
    t=tp(s,f'TP{n}',rail,35.56,180.34);props(s,35.56,167.64);s.wire(t['1'],(60.96,t['1'][1]));s.power(rail,(60.96,t['1'][1]))
    s.text('VIN, MODE and EN crossings have no junction: EN must remain separate from VIN.\nPlace both input capacitors at VIN/GND; use compact SW/inductor copper.\nKeep five output capacitors at the regulator. Route FB as a quiet Kelvin trace.\nMODE = VIN forces PWM. FSET = GND selects 2.25MHz and compensation1.',15.24,213.36,1.27)
    s.text('10nF C0G: nominal 2.4ms soft start. 0.95V rail is cascaded from 3.3V for on-time margin.\n3.3V rail is dedicated to Ethernet and its core converter; do not export accessory power.\nPG does not guarantee Realtek voltage limits. Reset delay, controller connections and brownout re-arm remain unfinished.\nTI SLVSDU1K and Realtek RTL8125BG V1.5 / reference V122. See ethernet-power-qualification.json.',15.24,251.46,1.1)
    s.items=[v.replace('(justify left bottom)','(justify left)').replace('(justify right bottom)','(justify right)') if v.startswith('(global_label ') else v for v in s.items]
    return s
