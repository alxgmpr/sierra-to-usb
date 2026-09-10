"""Capture the common USB modem interface and physically isolated assembly profiles."""
import json
from cad import ROOT, Sheet
from build_power_input import cap

PARTS={}
for file in ['initial-parts.json','power-input-parts.json','ethernet-parts.json','modem-parts.json']:
    data=json.loads((ROOT/'research'/file).read_text())
    for entry in data.get('parts',data.get('selected',[])):
        for p in entry.get('results',[entry]):PARTS[p['model']]=p


def resistor(s,ref,value,x,y,a,b,dnp=False):
    mpn={'0R':'RC0603JR-070RL','22R':'0402WGF220JTCE','18k':'0402WGF1802TCE'}[value]
    # RC0603 links are 1 A rated, 2 A maximum, <50mOhm. Profile links default DNP.
    p=PARTS[mpn]
    fp='Resistor_SMD:R_0603_1608Metric' if value=='0R' else 'Resistor_SMD:R_0402_1005Metric'
    pins=s.place('Device:R_Small_US',ref,x,y,angle=90,value=value+(' PROFILE / DNP' if dnp else ''),dnp=dnp,
        fields={'Footprint':fp,'MPN':mpn,'Manufacturer':p['manufacturer'],'LCSC':p['lcsc'],
                'Datasheet':p.get('datasheet',''),'Assembly': 'profile-dependent' if dnp else 'all'})
    s.connect(ref,'1',a,length=7.62,global_net=True);s.connect(ref,'2',b,length=7.62,global_net=True)
    return pins


def socket(s,unit,x,y):
    return s.place('cm4:MODEM_M2_B','J200',x,y,unit=unit,value='MDT420B01411',
        fields={'Assembly':'sourcing unresolved / 1 A per power contact required'})


def power():
    s=Sheet('modem-power','Modem: socket power and profiles')
    s.box('J200 / exact B-key, 1 A power contacts',10.16,15.24,190.5,190.5)
    pins=socket(s,1,104.14,83.82)
    s.connect('J200','[2,4,70,72,74]','VCC_MODEM',global_net=True)
    for n in ['24','38','68']:s.connect('J200',n,'M2_P'+n,global_net=True)
    ends=[]
    for n in ['3','5','11','27','33','39','45','51','57','71','73','SH']:
        p=pins[n];end=(p[0],134.62);s.wire(p,end);ends.append(end)
    ends.sort();s.wire(ends[0],ends[-1])
    for p in ends[1:-1]:s.junction(p)
    s.power('GND',ends[-1])
    cap(s,'C200','1uF',63.5,172.72,'VCC_MODEM')
    cap(s,'C201','100nF',144.78,172.72,'VCC_MODEM')
    s.box('Sierra extra power contacts / never fit for Quectel',213.36,15.24,190.5,190.5)
    for i,n in enumerate([24,38,68]):
        resistor(s,f'R{200+i}','0R',309.88,63.5+i*45.72,'VCC_MODEM',f'M2_P{n}',True)
    s.text('EM9190 / EM9191: fit all three links.\nEM929x: fit all three for eight-contact current sharing.\nRM520N-GLAA: all three MUST be absent.\nP24 is Quectel 1.8 V output; P38 is an input; P68 reserved.',220.98,175.26,1.1)
    s.box('Independent modem rail / safe unconfigured state',10.16,218.44,393.7,33.02)
    s.text('VCC_MODEM comes from the independent switched rail; converter, bulk and sequencing are being integrated.\nAll assembly-profile links default DNP. Configure only with all sources removed and VCC_MODEM discharged.\n3.135-4.4 V operating range; design target 3.7 V. This sheet does not establish the final power budget.',17.78,231.14,1.2)
    return s


def usb():
    s=Sheet('modem-usb','Modem: USB3 and vendor detection')
    s.box('Module-side directions / Linux USB3 host',10.16,15.24,393.7,137.16)
    socket(s,2,210.82,88.9)
    for n,net in [(7,'MODEM_USB2_P'),(9,'MODEM_USB2_N'),
        (29,'MODEM_USB3_M2H_N'),(31,'MODEM_USB3_M2H_P'),
        (35,'MODEM_USB3_H2M_N'),(37,'MODEM_USB3_H2M_P'),(20,'M2_P20'),(22,'M2_P22')]:
        s.connect('J200',str(n),net,global_net=True)
    s.box('Sierra USB personality / Quectel reserved-pin isolation',10.16,165.1,393.7,71.12)
    resistor(s,'R203','0R',109.22,203.2,'MODEM_1V8','M2_P20',True)
    resistor(s,'R204','0R',312.42,203.2,'MODEM_USB_VBUS_SENSE','M2_P22',True)
    s.text('Fit R203/R204 for EM919x/EM929x only; leave both absent for RM520N-GLAA.\nSierra PCIE_DIS must be 1.8 V at boot; VBUS_SENSE follows the selected host port.\nAC coupling is at each transmitter: modem TX capacitors are internal; host TX capacitors belong at the controller.\nNative CM4 USB2 is recovery-only. No modem PCIe path and no connection between two USB hosts.',17.78,241.3,1.1)
    return s


def controls():
    s=Sheet('modem-signals','Modem: controls and reserved contacts')
    s.box('Control endpoints / driver circuit integration pending',10.16,15.24,218.44,149.86)
    socket(s,3,116.84,86.36)
    for n,net in [(6,'MODEM_FULL_ON'),(8,'MODEM_RADIO_N'),(26,'MODEM_GNSS_N'),
                  (67,'MODEM_RESET_N'),(10,'MODEM_LED_N'),(23,'MODEM_WAKE_N'),(28,'M2_P28')]:
        s.connect('J200',str(n),net,global_net=True)
    s.connect('J200','25',None)
    s.box('Sierra shutdown acknowledgement only',10.16,177.8,218.44,76.2)
    resistor(s,'R205','0R',121.92,208.28,'M2_P28','MODEM_PLA_N',True)
    s.text('R205: Sierra only; P28 is reserved on RM520N.\nRESET / radio / GNSS use open-drain drivers.\nDPR unused; firmware RF power policy requires verification.',17.78,228.6,1.1)
    s.box('Explicit no-connects / no repurposing',241.3,15.24,162.56,233.68)
    p=socket(s,6,342.9,139.7)
    for n in p:s.connect('J200',n,None)
    return s


def sim2_profile():
    s=Sheet('modem-sim-profile','Modem: SIM1 and SIM2 profile links')
    s.box('SIM1 / common to all qualified module families',10.16,15.24,190.5,119.38)
    socket(s,4,91.44,76.2)
    for n,net in [(30,'SIM1_RST_MODULE'),(32,'SIM1_CLK_MODULE'),(34,'SIM1_DATA_MODULE'),
                  (36,'SIM1_PWR'),(66,'SIM1_DET')]:s.connect('J200',str(n),net,global_net=True)
    s.box('SIM2 or EM9190 mmWave control pins',213.36,15.24,190.5,119.38)
    socket(s,5,307.34,76.2)
    for n in [40,42,44,46,48]:s.connect('J200',str(n),'M2_P'+str(n),global_net=True)
    s.box('SIM2 external-card option / all five links default absent',10.16,147.32,393.7,88.9)
    for i,(n,sig) in enumerate([(40,'DET'),(42,'DATA_MODULE'),(44,'CLK_MODULE'),(46,'RST_MODULE'),(48,'PWR')]):
        x=109.22 if i<3 else 312.42;y=175.26+(i if i<3 else i-3)*22.86
        resistor(s,f'R{220+i}','0R',x,y,'M2_P'+str(n),'SIM2_'+sig,True)
    s.text('EM9190: R220-R224 absent; contacts carry QTM antenna signals, not SIM2. EM9191: these contacts are NC.\nEM929x / RM520N-GLAA: fit all five only for an external SIM2 and an exact SKU supporting it.\nQuectel internal eSIM option: keep all five absent. SIM supply is always generated by the modem.',17.78,243.84,1.1)
    return s


def sim(which):
    s=Sheet('sim'+str(which),f'SIM{which}: protected nano-SIM socket')
    ref=f'J{200+which}';base=230+(which-1)*10;prefix='SIM'+str(which)
    s.box('Module-powered / 1.8 V or 3 V SIM',10.16,15.24,393.7,132.08)
    jp=s.place('cm4:SMN-303-ARP7',ref,312.42,91.44)
    for pin,sig in [('C1','PWR'),('C2','RST'),('C3','CLK'),('C7','DATA'),('CD','DET')]:
        s.connect(ref,pin,prefix+'_'+sig,global_net=True)
    ends=[(jp[n][0],129.54) for n in ['C5','SH']]
    for n,end in zip(['C5','SH'],ends):s.wire(jp[n],end)
    s.wire(*ends);s.power('GND',ends[-1])
    s.connect(ref,'C6',None)
    for i,sig in enumerate(['RST','CLK','DATA']):
        resistor(s,f'R{base+i}','22R',101.6,55.88+i*30.48,prefix+'_'+sig+'_MODULE',prefix+'_'+sig)
    resistor(s,f'R{base+3}','18k',208.28,55.88,prefix+'_PWR',prefix+'_DATA')
    cap(s,f'C{base}','100nF',210.82,114.3,prefix+'_PWR')
    if which==2:
        # J200.48 is the source through fitted R224; absent R224 leaves SIM2 unused.
        s.place('power:PWR_FLAG','#FLG224',246.38,111.76)
        s.label('SIM2_PWR',(246.38,111.76),global_net=True)
        s.text('Supply flag represents J200.48 through fitted R224.\nWith R224 absent this socket is unpowered / unused.',251.46,137.16,.9)
    s.box('Socket-side ESD / RF bypass / no shared SIM power',10.16,160.02,393.7,91.44)
    u=f'U{base}';s.place('Power_Protection:TPD4EUSB30',u,76.2,203.2,value='TPD4EUSB30DQAR',fields={
        'MPN':'TPD4EUSB30DQAR','Manufacturer':'Texas Instruments','LCSC':'C90627',
        'Footprint':'cm4:TI_DQA0010_TPD4EUSB30','Datasheet':'https://www.ti.com/lit/ds/symlink/tpd4eusb30.pdf'})
    s.field_position(u,'Reference',76.2,180.34);s.field_position(u,'Value',76.2,182.88)
    for n,sig in [('1','RST'),('2','CLK'),('4','DATA'),('5','DET')]:
        s.connect(u,n,prefix+'_'+sig,global_net=True)
    for n in ['3','8']:s.connect(u,n,'GND',global_net=True)
    for n in ['6','7','9','10']:s.connect(u,n,None)
    for i,sig in enumerate(['RST','CLK','DATA']):
        refc=f'C{base+1+i}';x=182.88+i*55.88;p=PARTS['GRM1555C1H100JA01D']
        cp=s.place('Device:C',refc,x,213.36,value='10pF C0G',fields={
            'MPN':p['model'],'Manufacturer':p['manufacturer'],'LCSC':p['lcsc'],
            'Footprint':'Capacitor_SMD:C_0402_1005Metric','Datasheet':p['datasheet']})
        s.connect(refc,'1',prefix+'_'+sig,global_net=True);s.connect(refc,'2','GND',global_net=True)
    d=f'D{base}';s.place('cm4:TPD1E05U06DPYR',d,373.38,213.36)
    s.connect(d,'1',prefix+'_PWR',global_net=True);s.connect(d,'2','GND',global_net=True)
    s.text('Detect switch: absent = GND, inserted = open. Quectel: AT+QSIMDET=1,1; Sierra: matching detect polarity.\nKeep each SIM path <100 mm, clock/data parallel runs <20 mm; ground guard and low-capacitance routing.\nVerify 1.8/3 V operation, hot-plug, <1 us rise time and 5 MHz clock on assembled hardware.',17.78,259.08,1.1)
    return s
