"""Capture the CM4 carrier core; remaining integration is explicit in ERC.

Run build_cm4_symbols.py first. This generator only writes the CM4 hierarchy.
It never changes the historical RK3568 project.
"""
import json
from cad import ROOT, ROOT_ID, Sheet, Q, effects, uid

MANIFEST=json.loads((ROOT/'research/cm4-symbols.json').read_text())
PARTS=json.loads((ROOT/'research/initial-parts.json').read_text())['parts']
PARTS={v['model']:v for r in PARTS for v in (r['results'] if 'results' in r else [r])}


def part(s, symbol, ref, value, mpn, fp, x, y, angle=0):
    p=PARTS[mpn]
    return s.place(symbol,ref,x,y,value=value,angle=angle,fields={
        'MPN':mpn,'Manufacturer':p['manufacturer'],'LCSC':p['lcsc'],'Footprint':fp})


def resistor(s,ref,value,mpn,x,y,angle=0):
    return part(s,'Device:R_Small_US',ref,value,mpn,'Resistor_SMD:R_0402_1005Metric',x,y,angle)


def cap(s,ref,value,x,y):
    mpn='CL05B104KO5NNNC' if value=='100nF' else 'CL10A106KP8NNNC'
    fp='Capacitor_SMD:C_0402_1005Metric' if value=='100nF' else 'Capacitor_SMD:C_0603_1608Metric'
    return part(s,'Device:C',ref,value,mpn,fp,x,y)


def supply_bus(s, ref, pins, net):
    ends=[]
    for num in pins:
        p=s.pins[ref,str(num)]
        end=(p[0],p[1]+5.08)
        s.wire(p,end);ends.append(end)
    ends.sort()
    for a,b in zip(ends,ends[1:]):s.wire(a,b)
    for p in ends[1:-1]:s.junction(p)
    s.power(net,ends[0])


def button(s, ref, label, x, y):
    p=s.place('Switch:SW_Push',ref,x,y,value=label,fields={
        'Footprint':'cm4:Alps_SKRPACE010','MPN':'SKRPACE010',
        'Manufacturer':'Alps Alpine','LCSC':'C139797',
        'Datasheet':'https://tech.alpsalpine.com/cms.media/product_catalog_ta_02_skrp_en_2cd80f610b.pdf'})
    import re
    s.items[-1]=re.sub(r'(\(property "(?:Reference|Value)" "[^"]*" \(at )[^)]+',
        lambda m:m[1]+f'{x} {y-10.16 if "Reference" in m[0] else y-7.62} 0',s.items[-1])
    return p


def unit(s,ref,symbol,n,x,y,nets):
    s.place('cm4:'+symbol,ref,x,y,unit=n,value='DF40C-100DS-0.4V(58)')
    for p in MANIFEST[symbol][n-1]['pins']:
        name=p['name'];num=p['ball']
        if name=='GND':continue
        net=nets.get(name)
        s.connect(ref,num,net,global_net=True)
    grounds=[p['ball'] for p in MANIFEST[symbol][n-1]['pins'] if p['name']=='GND']
    if grounds:supply_bus(s,ref,grounds,'GND')


def core_power():
    s=Sheet('cm4-power','CM4 Lite: supply domains and reset controls')
    s.box('Two physical sockets / separately fitted CM4001000',10.16,15.24,190.5,160.02)
    unit(s,'J100','CM4_J1',1,101.6,73.66,{
        'VCC5V_CM4':'VCC5V_CM4','GPIO_VREF':'CM4_3V3',
        'CM4_3V3':'CM4_3V3','CM4_1V8':'CM4_1V8'})
    # Bypass is wired as a local bank with visible supply and ground symbols.
    for ref,x,value in [('C100',45.72,'10uF'),('C101',91.44,'10uF'),('C102',137.16,'100nF')]:
        c=cap(s,ref,value,x,144.78)
        s.wire(c['1'],(x,132.08));s.wire(c['2'],(x,157.48))
    s.wire((45.72,132.08),(137.16,132.08));s.junction((91.44,132.08))
    s.wire((45.72,157.48),(137.16,157.48));s.junction((91.44,157.48))
    s.power('VCC5V_CM4',(45.72,132.08));s.power('GND',(137.16,157.48))
    s.box('Power and sequencing rules',10.16,185.42,190.5,76.2)
    s.text('5 V input: 4.75-5.25 V at the module contacts.\nAll six 5 V contacts and every ground contact are connected.\nGPIO_VREF uses CM4_3V3; never feed an external 3.3 V rail here.\nCM4_3V3 and CM4_1V8: 600 mA total per rail.\nBoth rails turn off when GLOBAL_EN is held low.\nCarrier load budget / input current limit: integration pending.\nModule load-current table gives typical, not maximum, values.',17.78,198.12)
    s.box('System control contacts',213.36,15.24,190.5,246.38)
    used=['EEPROM_nWP','SCL0','SDA0','RUN_PG','nRPIBOOT','GLOBAL_EN','nEXTRST','Pi_nLED_Activity']
    unit(s,'J100','CM4_J1',5,302.26,81.28,{n:'CM4_'+n for n in used})
    for i,(net,label,x,y) in enumerate([
        ('CM4_RUN_PG','RESET',274.32,147.32),
        ('CM4_GLOBAL_EN','WAKE / OFF',373.38,147.32),
        ('CM4_nRPIBOOT','RECOVERY',274.32,185.42),
        ('CM4_EEPROM_nWP','EEPROM WP',373.38,185.42)]):
        b=button(s,f'SW{100+i}',label,x,y)
        if i==0:
            r=resistor(s,'R100','220R 1%','0402WGF2200TCE',x-27.94,y,90)
            s.wire(r['2'],b['1']);s.wire(r['1'],(x-40.64,y));s.label(net,(x-40.64,y),180,True)
        else:
            s.wire(b['1'],(x-20.32,y));s.label(net,(x-20.32,y),180,True)
        s.wire(b['2'],(x+12.7,y));s.wire((x+12.7,y),(x+12.7,y+10.16));s.power('GND',(x+12.7,y+10.16))
    s.text('Open switches use the CM4 internal pull-ups.\nRESET discharges RUN_PG through the specified 220R resistor.\nHold RECOVERY at startup for rpiboot; hold WP to inhibit writes.\nGLOBAL_EN low >1 ms restarts CM4 after software shutdown.\nDo not use WAKE / OFF before the OS has shut down.\nReserved contact 76 and unused PMIC analog pins remain isolated.',220.98,218.44)
    return s


def storage():
    s=Sheet('cm4-storage','CM4 Lite: switched microSD storage')
    s.box('CM4 Lite SDIO / 3.3 V startup signalling',10.16,15.24,172.72,119.38)
    unit(s,'J100','CM4_J1',3,86.36,71.12,{n:n for n in ['SD_CLK','SD_CMD','SD_DAT0','SD_DAT1','SD_DAT2','SD_DAT3','SD_PWR_ON']})
    s.text('SD_DAT4..7 are unused. SD_VDD_OVERRIDE is unconnected.\nDo not fit an eMMC CM4 variant to this microSD design.',17.78,109.22)
    s.box('Accessible push-push socket / 5033981892',195.58,15.24,208.28,119.38)
    s.place('Connector:Micro_SD_Card_Det2','J110',345.44,71.12,value='5033981892',fields={
        'Footprint':'cm4:SDCARD_MOLEX_503398-1892','MPN':'5033981892',
        'Manufacturer':'Molex','LCSC':'C428492','Datasheet':'https://www.molex.com/en-us/products/part-detail/5033981892'})
    # Keep connector reference/value above its body.
    import re
    s.items[-1]=re.sub(r'(\(property "(?:Reference|Value)" "[^"]*" \(at )[^)]+',
        lambda m:m[1]+('345.44 45.72 0' if 'Reference' in m[0] else '345.44 48.26 0'),s.items[-1])
    for p,n in {'1':'SD_DAT2','2':'SD_DAT3','3':'SD_CMD','5':'SD_CLK','7':'SD_DAT0','8':'SD_DAT1'}.items():
        s.connect('J110',p,n,global_net=True)
    s.connect('J110','4','SD_VDD',global_net=True)
    for p in ['6','SH']:
        end=s.connect('J110',p,'GND',global_net=True)
    for p in ['9','10']:s.connect('J110',p,None)
    s.text('Shell grounded; mechanical card detection unused.\nBoot card must be fitted before power-on.\nFit card socket at the board edge with ejection clearance.',203.2,109.22)
    s.box('Hardware-default ON / software power cycle / output discharge',10.16,147.32,393.7,114.3)
    p=s.place('cm4:RT9742GGJ5','U110',210.82,208.28)
    s.wire(p['5'],(137.16,p['5'][1]));s.wire((137.16,p['5'][1]),(137.16,180.34));s.power('CM4_3V3',(137.16,180.34))
    s.wire(p['4'],(93.98,p['4'][1]));s.label('SD_PWR_ON',(93.98,p['4'][1]),180,True)
    r=resistor(s,'R110','10kR 1%','0402WGF1002TCE',93.98,190.5)
    s.wire(r['1'],(93.98,180.34));s.power('CM4_3V3',(93.98,180.34));s.wire(r['2'],(93.98,p['4'][1]))
    s.junction((93.98,p['4'][1]));s.connect('U110','3',None)
    s.wire(p['2'],(p['2'][0],251.46));s.power('GND',(p['2'][0],251.46))
    s.wire(p['1'],(327.66,p['1'][1]));s.label('SD_VDD',(327.66,p['1'][1]),0,True)
    for ref,x,y,value,rail in [('C110',35.56,218.44,'100nF','CM4_3V3'),('C112',66.04,218.44,'10uF','CM4_3V3'),('C111',327.66,233.68,'10uF','SD_VDD')]:
        c=cap(s,ref,value,x,y)
        if rail=='SD_VDD':s.wire(c['1'],(x,p['1'][1]));s.junction((x,p['1'][1]))
        else:s.wire(c['1'],(x,y-12.7));s.power(rail,(x,y-12.7))
        s.wire(c['2'],(x,y+12.7));s.power('GND',(x,y+12.7))
    return s


def interfaces():
    s=Sheet('cm4-interfaces','CM4 Lite: native gigabit and PCIe USB3 host interfaces')
    s.box('Native gigabit PHY / HX6096NL magnetics',10.16,15.24,190.5,215.9)
    nets={p['name']:p['name'].replace('Ethernet_Pair','ETH_MDI') for p in MANIFEST['CM4_J1'][3]['pins'] if p['name'].startswith('Ethernet_Pair')}
    unit(s,'J100','CM4_J1',4,93.98,78.74,nets)
    s.text('Four MDI pairs connect to T120 on ethernet-data.\nPoE extraction stays on the isolated cable side.\nNo discrete external Ethernet PHY or PCIe NIC.\nSYNC and LED contacts currently unused.',17.78,144.78)
    s.box('PCIe Gen2 x1 to dedicated USB3 host / USB2 recovery',213.36,15.24,190.5,215.9)
    nets={p['name']:p['name'].replace('PCIe','PCIE').replace('USB_','RECOVERY_USB_') for p in MANIFEST['CM4_J2'][0]['pins'] if p['name']!='USB_OTG_ID'}
    unit(s,'J101','CM4_J2',1,302.26,78.74,nets)
    s.text('J101 uses physical pins 1..100 (CM4 pin minus 100).\nCM4 already AC-couples its PCIe TX and reference clock.\nFit AC capacitors only at the external controller TX.\nConnect CLK_nREQ; preserve reset control at warm boot.\n90R differential target; intrapair skew target <0.1 mm.\n\nNative USB2 is reserved for rpiboot / recovery.\nUSB_OTG_ID is left open for peripheral operation.\nThe modem USB3 path uses the PCIe controller.',220.98,139.7)
    return s


def gpio():
    s=Sheet('cm4-gpio','CM4 Lite: GPIO allocation and development interfaces')
    s.box('CM4 GPIO bank / 3.3 V',10.16,15.24,190.5,246.38)
    nets={p['name']:p['name'] for p in MANIFEST['CM4_J1'][1]['pins']}
    unit(s,'J100','CM4_J1',2,88.9,111.76,nets)
    s.box('Development and control allocation',213.36,15.24,190.5,246.38)
    s.text('Capture in progress: external ports and protection follow.\n\nGPIO2 / GPIO3: I2C1 and Qwiic.\nGPIO7..11: SPI0.\nGPIO14 / GPIO15: serial console, 3.3 V.\nGPIO0 / GPIO1 (ID_SD / ID_SC): reserve HAT ID bus.\nRemaining GPIO: modem power / reset / radio controls,\nADC and general development access.\n\nAll external ports must avoid powering a shut-down CM4.\nCM4_3V3 load includes microSD, pull-ups and peripherals.\nTotal GPIO output current stays below 50 mA.\nHardware accessory limits are part of final power budget.\n\nUnfinished global endpoints remain visible to ERC.',220.98,35.56)
    return s


def unused():
    s=Sheet('cm4-unused','CM4 Lite: unused high-speed interfaces and ground contacts')
    for u,x,y in [(2,99.06,55.88),(3,302.26,66.04),(4,302.26,187.96),(5,99.06,180.34)]:
        unit(s,'J101','CM4_J2',u,x,y,{})
    s.text('All CM4 ground contacts connect to the continuous secondary-side ground plane.\nUnused camera, display, HDMI, TV and reserved contacts have explicit no-connect markers.\nKeep unconnected pads physically isolated; do not ground reserved signal contacts.',15.24,248.92)
    return s


def root_page(sheets):
    s=Sheet('cm4-carrier','CM4 Lite integrated cellular modem development board',root=True)
    s.text('CM4001000 / 1 GB Lite / native gigabit / PCIe USB3 / isolated PoE',15.24,15.24,2.0)
    s.text('CURRENT IMPLEMENTATION - NOT FOR FABRICATION',15.24,25.4,1.6)
    descriptions={
        'cm4-power':'J100 / J101: two physical CM4 sockets\n5 V input, module rails, reset and boot controls',
        'cm4-storage':'J110: removable microSD boot and root filesystem\nU110: switched card supply with output discharge',
        'cm4-interfaces':'Native gigabit PHY / PCIe Gen2 x1\nUSB3 controller integration; native USB2 recovery',
        'cm4-gpio':'3.3 V GPIO, I2C, SPI and console allocation\nExternal interfaces and modem controls in progress',
        'cm4-unused':'Unused display / camera / HDMI contacts\nExplicit no-connects and all socket grounds',
        'ethernet-data':'T120: four 1:1 gigabit channels\nJ120: Cat5e jack; U120 / U121: PHY-side ESD',
        'ethernet-termination':'DC-blocked termination of four PoE centre taps\nC134: Y1 safety capacitor to secondary ground',
        'aux-usbc':'J150: power-only USB-C input\nU151: CC protection and dead-battery Rd',
        'aux-pd':'U150: fixed 20 V / 3 A PD request\nU152: independent auxiliary housekeeping',
        'aux-window':'U153: precise auxiliary voltage qualification\nHardware disconnect on voltage or CC fault',
        'input-mux':'U160: independent reverse blocking\nOnly qualified inputs may power VIN_SYS'}
    for index,child in enumerate(sheets):
        x=15.24+(index%3)*134.62;y=45.72+(index//3)*45.72
        s.items.append(f'(sheet (at {x} {y}) (size 121.92 30.48) (stroke (width 0.254) (type default)) (fill (color 0 0 0 0)) (uuid {Q(uid("sheet-block/"+child.name))}) '+
            f'(property "Sheetname" {Q(child.title)} (at {x} {y-1.27} 0) {effects(justify="left bottom")}) '+
            f'(property "Sheetfile" {Q(child.name+".kicad_sch")} (at {x} {y+31.75} 0) {effects(justify="left top")}) '+
            f'(instances (project "cm4-carrier" (path {Q("/"+ROOT_ID)} (page "{index+2}")))))')
        s.text(descriptions.get(child.name,''),x+7.62,y+8.89,1.52)
    s.text('CM4 implementation in progress. Historical RK3568 CAD remains separate.\nRelease requires electrical closure, full routing, ERC, parity, DRC and manufacturing review.',15.24,248.92)
    return s


if __name__=='__main__':
    from build_ethernet import ethernet_data, ethernet_termination
    from build_power_input import aux_usbc,aux_pd,aux_window,input_mux
    sheets=[core_power(),storage(),interfaces(),gpio(),unused(),ethernet_data(),ethernet_termination(),
            aux_usbc(),aux_pd(),aux_window(),input_mux()]
    root_page(sheets).save()
    for sheet in sheets:sheet.save()
    project=ROOT/'cad/cm4-carrier.kicad_pro'
    if not project.exists():
        project.write_text(json.dumps({'meta':{'filename':project.name,'version':1},'erc':{'erc_exclusions':[]},'schematic':{'drawing':{'label_size':50}},'net_settings':{'classes':[]}},indent=2)+'\n')
