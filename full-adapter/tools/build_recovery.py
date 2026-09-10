"""Dedicated USB2 BootROM port; voltage-detect qualification remains open."""
from collections import OrderedDict
from schematic import Sheet
from build_emmc import cap,resistor


def recovery_switch_symbol():
    from build_core_symbols import make_symbol
    pins=[('1','1D+','passive','L'),('2','1D-','passive','L'),('3','2D+','passive','L'),('4','2D-','passive','L'),('5','GND','power_in','B'),('6','~{OE}','input','L'),('7','D-','passive','R'),('8','D+','passive','R'),('9','S','input','L'),('10','VCC','power_in','T')]
    return make_symbol('TS3USB221ARSER','full-adapter:TI_TS3USB221A_RSE0010A',
      'https://www.ti.com/lit/ds/symlink/ts3usb221a.pdf','Texas Instruments','C128396',
      'USB2 2:1 analog switch with specified power-off leakage',
      OrderedDict([('USB mux',[dict(ball=b,name=n,type=t,side=s,pitch_mm=5.08) for b,n,t,s in pins])]),
      keywords='USB switch isolation',footprint_filter='TI?TS3USB221A*',side_pins_from_top=True)


def rpart(s,ref,value,x,y,angle=0):
    parts={'5.1kR 1%':('0402WGF5101TCE','C25905','UNI-ROYAL'),
           '4.7kR 1%':('0402WGF4701TCE','C25900','UNI-ROYAL'),
           '2.2R 1%':('RC-02U2R20FT','C321161','FH (Guangdong Fenghua Advanced Tech)')}
    mpn,lcsc,mfr=parts[value]
    return s.place('Device:R_Small_US',ref,x,y,angle=angle,value=value,fields={'Footprint':'Resistor_SMD:R_0402_1005Metric','MPN':mpn,'LCSC':lcsc,'Manufacturer':mfr})


def props(s,x,y):
    import sexpdata as sx
    n=sx.loads(s.items[-1])
    for p in n:
        if isinstance(p,list) and str(p[0])=='property' and p[1] in ['Reference','Value']:
            next(a for a in p if isinstance(a,list) and str(a[0])=='at')[1:3]=[x,y+(2.54 if p[1]=='Value' else 0)]
    s.items[-1]=sx.dumps(n)


def recovery_usb():
    s=Sheet('recovery-usb','Processor USB2 recovery connector and isolation')
    s.box('Device-only service port — external VBUS is sense-only',10.16,15.24,175.26,160.02)
    j=s.place('Connector:USB_C_Receptacle_USB2.0_16P','J630',45.72,71.12,fields={'MPN':'USB4105-GF-A-120','Manufacturer':'GCT','LCSC':'C5184243','Footprint':'full-adapter:GCT_USB4105_120','Datasheet':'https://gct.co/files/drawings/usb4105.pdf'});props(s,45.72,35.56)
    for pin in ['A8','B8']:s.connect('J630',pin,None)
    for pin in ['A1','SH']:
        p=j[pin];s.wire(p,(p[0],104.14));s.power('GND',(p[0],104.14))
    p=j['A4'];s.wire(p,(96.52,p[1]));s.wire((96.52,p[1]),(96.52,43.18));s.power('VCC_RECOVERY5V',(96.52,43.18))
    for pin,net in [('A6','RECOVERY_CABLE_P'),('B6','RECOVERY_CABLE_P'),('A7','RECOVERY_CABLE_N'),('B7','RECOVERY_CABLE_N')]:s.connect('J630',pin,net,15.24)
    for i,pin in enumerate(['A5','B5']):
        x=137.16+i*25.4;p=j[pin];s.wire(p,(x,p[1]));r=rpart(s,f'R{630+i}','5.1kR 1%',x,91.44)
        s.wire((x,p[1]),r['1']);s.wire(r['2'],(x,104.14));s.power('GND',(x,104.14))
    capx=86.36;c=cap(s,'C630','100nF',capx,132.08);s.wire(c['1'],(capx,121.92));s.power('VCC_RECOVERY5V',(capx,121.92));s.wire(c['2'],(capx,139.7));s.power('GND',(capx,139.7))
    s.place('power:PWR_FLAG','#FLG630',96.52,35.56);s.wire((96.52,35.56),(96.52,43.18))
    s.text('CC1 and CC2 have independent Rd. No PD negotiation.\nNo VBUS connection to a system power supply.\nAntenna/modem host access is a separate interface.',17.78,157.48,1.1)
    s.box('USB data path — default channel 1; powered from S0',195.58,15.24,210.82,160.02)
    u=s.place('full-adapter:TS3USB221ARSER','U8',297.18,83.82);props(s,297.18,25.4)
    for p,n in [('1','RECOVERY_CABLE_P'),('2','RECOVERY_CABLE_N'),('8','RECOVERY_SWITCH_P'),('7','RECOVERY_SWITCH_N')]:s.connect('U8',p,n,12.7)
    for p in ['3','4']:s.connect('U8',p,None)
    p=u['5'];s.wire(p,(p[0],p[1]+7.62));s.power('GND',(p[0],p[1]+7.62))
    for pin in ['6','9']:
        p=u[pin];s.wire(p,(p[0]-7.62,p[1]))
    x=u['6'][0]-7.62;s.wire((x,u['6'][1]),(x,u['9'][1]+7.62));s.junction((x,u['9'][1]));s.power('GND',(x,u['9'][1]+7.62))
    p=u['10'];s.wire(p,(p[0],43.18));s.power('VCC3V3_S0',(p[0],43.18))
    c=cap(s,'C631','100nF',375.92,55.88);s.wire((p[0],43.18),(375.92,43.18));s.wire((375.92,43.18),c['1']);s.wire(c['2'],(375.92,66.04));s.power('GND',(375.92,66.04))
    s.text('S=0 and OE=0 connect 1D to D. Unused channel is NC.\nVCC=0 leakage specified <=2uA; intermediate supply\nbehavior remains part of system sequencing qualification.\n6R maximum switch resistance; route short at 90 ohm differential.',203.2,144.78,1.1)
    s.box('BootROM USB0 and independent modem USB1 endpoints',10.16,185.42,175.26,83.82)
    s.place('full-adapter:RK3568B2','U1',68.58,220.98,unit=19)
    for p,n in [('L23',None),('M24','RECOVERY_VBUSDET'),('P24','MODEM_HOST_USB2_P'),('P25','MODEM_HOST_USB2_N'),('P27','SOC_RECOVERY_P'),('P28','SOC_RECOVERY_N')]:s.connect('U1',p,n,7.62,global_net=True)
    s.text('Only USB0 supports BootROM flashing. ID left open.\nModem USB1 connects on the modem host-selection sheet.',17.78,254,1.05)
    s.box('Connector ESD and processor series termination',195.58,185.42,210.82,63.5)
    e=s.place('Power_Protection:TPD2EUSB30','U10',246.38,213.36,fields={'MPN':'TPD2EUSB30DRTR','Manufacturer':'Texas Instruments','LCSC':'C97502','Footprint':'full-adapter:TI_TPD2EUSB30_DRT0003A','Datasheet':'https://www.ti.com/lit/ds/symlink/tpd2eusb30.pdf'});props(s,246.38,198.12)
    for p,n in [('1','RECOVERY_CABLE_P'),('2','RECOVERY_CABLE_N')]:s.connect('U10',p,n,5.08)
    s.wire(e['3'],(246.38,233.68));s.power('GND',(246.38,233.68))
    for i,n in enumerate(['P','N']):
        y=213.36+i*25.4;r=rpart(s,f'R{632+i}','2.2R 1%',350.52,y,90)
        s.wire(r['1'],(307.34,y));s.label('RECOVERY_SWITCH_'+n,(307.34,y),180)
        s.wire(r['2'],(378.46,y));s.label('SOC_RECOVERY_'+n,(378.46,y),global_net=True)
    s.text('U10 at connector; R632/R633 at SoC. Verify USB eye and IEC ESD on assembled hardware.',15.24,279.4,1.0)
    return s


def recovery_detect():
    s=Sheet('recovery-detect','Recovery VBUS detection — qualification in progress')
    s.box('Host-supplied logic domain / processor S0 domain',10.16,15.24,396.24,190.5)
    u=s.place('full-adapter:TXU0202DCUR','U9',157.48,88.9);props(s,157.48,25.4)
    for pin,rail,x in [('3','VCC_RECOVERY5V',106.68),('7','VCC3V3_S0',223.52)]:
        p=u[pin];y=43.18 if pin=='3' else 35.56;s.wire(p,(p[0],y));s.wire((p[0],y),(x,y));s.power(rail,(x,y))
        c=cap(s,'C632' if pin=='3' else 'C633','100nF',x,55.88);s.wire((x,y),c['1']);s.wire(c['2'],(x,66.04));s.power('GND',(x,66.04))
    for pin in ['5','6']:
        p=u[pin];end=(p[0]-15.24,p[1]);s.wire(p,end);s.power('VCC_RECOVERY5V',end)
    for pin in ['1','2']:
        p=u[pin];end=(p[0]+12.7,p[1]) if pin=='1' else (p[0],p[1]+7.62);s.wire(p,end)
        if pin=='1':s.wire(end,(end[0],end[1]+5.08));end=(end[0],end[1]+5.08)
        s.power('GND',end)
    s.connect('U9','4',None)
    p=u['8'];r=rpart(s,'R634','4.7kR 1%',274.32,p[1],90);s.wire(p,r['1']);s.wire(r['2'],(325.12,p[1]));s.label('RECOVERY_VBUSDET',(325.12,p[1]),global_net=True)
    r=resistor(s,'R635','47kR 1%',304.8,124.46);s.wire((304.8,p[1]),r['1']);s.junction((304.8,p[1]));s.wire(r['2'],(304.8,137.16));s.power('GND',(304.8,137.16))
    c=cap(s,'C634','100nF',355.6,124.46);s.wire((325.12,p[1]),(355.6,p[1]));s.wire((355.6,p[1]),c['1']);s.wire(c['2'],(355.6,137.16));s.power('GND',(355.6,137.16))
    s.text('No host power is tied to a processor rail. A1 and OE follow connector VBUS.\nB1Y reports VBUS through a divider to the dedicated detector; B2 is tied LOW.\nEither translator supply absent disables its outputs. R635 defines the detector LOW.\n\nQUALIFICATION OPEN: dedicated VBUSDET leakage/LOW threshold, rail tolerance,\npartial-supply behavior, reset timing and USB BootROM operation.\nCalculated HIGH is 2.711–3.198V only under research/recovery-qualification.json assumptions.\nThis circuit is not release-qualified; resolve these bounds before manufacture.',17.78,157.48,1.27)
    s.text('USB programming port: use a USB data cable and independent board power.\nHold the recovery control during reset for Loader mode; eMMC D0 service pads provide MaskROM fallback.\nNormal recovery button and protected analog development IO are still to be captured.',15.24,233.68,1.27)
    return s
