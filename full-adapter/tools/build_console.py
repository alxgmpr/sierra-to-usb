"""UART2 console with separately supplied cable-side logic and fixed directions."""
from collections import OrderedDict
from schematic import Sheet
from build_emmc import cap, resistor


def console_symbol():
    from build_core_symbols import make_symbol
    # TI SCES942A Table 6-1; independently checked against EasyEDA C5186957.
    pins=[('1','B2','input','R'),('2','GND','power_in','B'),
          ('3','VCCA','power_in','T'),('4','A2Y','tri_state','L'),
          ('5','A1','input','L'),('6','OE','input','L'),
          ('7','VCCB','power_in','T'),('8','B1Y','tri_state','R')]
    return make_symbol('TXU0202DCUR','full-adapter:TI_TXU0202_DCU0008A',
        'https://www.ti.com/lit/ds/symlink/txu0202.pdf','Texas Instruments','C5186957',
        'Dual fixed-direction level translator, partial-power-down isolation',
        OrderedDict([('UART translator',[dict(ball=b,name=n,type=t,side=s,pitch_mm=7.62) for b,n,t,s in pins])]),
        keywords='UART voltage translator isolation',footprint_filter='TI?TXU0202*')


def console():
    s=Sheet('console','Linux UART2 console with power-off isolation')
    s.box('1.8V processor side / adapter-powered 3.3V cable side',10.16,15.24,254,177.8)
    u=s.place('full-adapter:TXU0202DCUR','U7',137.16,86.36)
    import sexpdata as sx
    symbol=sx.loads(s.items[-1])
    for p in symbol:
        if isinstance(p,list) and str(p[0])=='property' and p[1] in ['Reference','Value']:
            next(a for a in p if isinstance(a,list) and str(a[0])=='at')[1:3]=[137.16,27.94 if p[1]=='Reference' else 30.48]
    s.items[-1]=sx.dumps(symbol)
    for pin,net in [('5','SOC_UART2_TX_1V8'),('4','SOC_UART2_RX_1V8')]:
        s.connect('U7',pin,net,25.4,global_net=True)
    for pin,rail,x in [('3','VCC1V8_PMU',106.68),('7','VCC_CONSOLE',175.26)]:
        y=48.26 if pin=='3' else 40.64
        p=u[pin];s.wire(p,(p[0],y));s.wire((p[0],y),(x,y));s.power(rail,(x,y))
        c=cap(s,'C620' if pin=='3' else 'C621','100nF',x,58.42)
        s.wire((x,y),c['1']);s.wire(c['2'],(x,66.04));s.power('GND',(x,66.04))
    p=u['2'];s.wire(p,(p[0],119.38));s.power('GND',(p[0],119.38))
    end=(u['6'][0]-10.16,u['6'][1]);s.power('VCC1V8_PMU',end)
    s.wire(u['6'],end)
    for pin,net in [('8','CONSOLE_TX_RAW'),('1','CONSOLE_RX_RAW')]:s.connect('U7',pin,net,15.24)
    s.text('A1 -> B1Y: processor TX to adapter RX. B2 -> A2Y: adapter TX to processor RX.\nOE follows PMUIO2; either supply absent isolates both outputs.\nEach supply has local 100nF bypass. VCC_CONSOLE has no connection to board power.',17.78,142.24,1.27)
    s.box('Keyed service connector — 3.3V TTL, 1.5Mbaud initial target',271.78,15.24,134.62,177.8)
    j=s.place('Connector_Generic:Conn_01x04','J620',381,78.74,value='CONSOLE',fields={
        'MPN':'B4B-PH-SM4-TB(LF)(SN)','Manufacturer':'JST','LCSC':'C160354',
        'Datasheet':'https://www.jst-mfg.com/product/pdf/eng/ePH.pdf',
        'Footprint':'full-adapter:JST_PH_B4B-PH-SM4-TB'})
    for pin,net in [('1','GND'),('2','CONSOLE_TX'),('3','CONSOLE_RX'),('4','VCC_CONSOLE')]:
        p=j[pin];x={'1':309.88,'4':294.64}.get(pin,327.66)
        s.wire(p,(x,p[1]))
        if pin in ['1','4']:
            y=63.5 if pin=='4' else 104.14
            s.wire((x,p[1]),(x,y));s.power(net,(x,y))
        else:s.label(net,(x,p[1]),180)
    for i,net in enumerate(['TX','RX']):
        y=129.54+25.4*i
        from build_ddr_schematic import passive
        r=passive(s,f'R{620+i}','1kR 1%',340.36,y,90)
        s.wire(r['1'],(292.1,y));s.label('CONSOLE_'+net+'_RAW',(292.1,y),180)
        s.wire(r['2'],(391.16,y));s.label('CONSOLE_'+net,(391.16,y))
    s.place('power:PWR_FLAG','#FLG620',294.64,55.88)
    s.wire((294.64,55.88),(294.64,63.5))
    s.text('Pin 1 GND | 2 board TX | 3 board RX | 4 adapter 3.3V\nPHR-4 housing; cross TX/RX at the USB-UART adapter.\nPin 4 is an input, powering only U7 cable-side logic.\nUse short service cable; never connect RS-232 levels.',279.4,170.18,1.0)
    s.box('UART idle HIGH — each pull-up stays in its own supply domain',10.16,203.2,396.24,45.72)
    for i,(net,rail) in enumerate([('SOC_UART2_TX_1V8','VCC1V8_PMU'),('SOC_UART2_RX_1V8','VCC1V8_PMU'),('CONSOLE_RX_RAW','VCC_CONSOLE'),('CONSOLE_TX_RAW','VCC_CONSOLE')]):
        x=55.88+93.98*i;r=resistor(s,f'R{622+i}','10kR 1%',x,233.68)
        s.wire(r['1'],(x,223.52));s.power(rail,(x,223.52))
        s.wire(r['2'],(x,246.38));s.label(net,(x,246.38),global_net=net.startswith('SOC_'))
    s.text('TXU inputs have internal weak pull-downs; external pull-ups prevent a BREAK state with no driver.\nSeries 1kR limits DC contention; verify cable capacitance and edge timing at the selected baud rate. Service interface, no external power output.',15.24,271.78,1.05)
    return s
