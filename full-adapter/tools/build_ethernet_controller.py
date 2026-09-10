"""RTL8125BG bypass, oscillator, configuration and PCIe lane capture."""
import json
from schematic import ROOT, Sheet
from build_emmc import cap, resistor
from build_recovery import props, rpart


def part(s, key, lib, ref, value, x, y, footprint, angle=0):
    p=json.loads((ROOT/'research/ethernet-controller-parts.json').read_text())[key]
    return s.place(lib,ref,x,y,value=value,angle=angle,fields={
        'MPN':p['model'],'Manufacturer':p['manufacturer'],'LCSC':p['lcsc'],
        'Footprint':footprint,'Datasheet':p.get('datasheet','')})


def local_cap(s, ref, value, x, y):
    if value!='4.7uF':return cap(s,ref,value,x,y)
    return part(s,'local_4u7','Device:C',ref,value,x,y,'Capacitor_SMD:C_0603_1608Metric')


def finish(s):
    s.items=[v.replace('(justify left bottom)','(justify left)').replace('(justify right bottom)','(justify right)') if v.startswith('(global_label ') else v for v in s.items]
    return s


def ethernet_local_power():
    s=Sheet('ethernet-local-power','RTL8125BG supplies and local decoupling')
    s.box('External-regulator BG variant',10.16,15.24,165.1,172.72)
    u=s.place('full-adapter:RTL8125BG-CG','U11',66.04,99.06,unit=1)
    props(s,66.04,48.26)
    for pin in ['4','5','7']:s.connect('U11',pin,None)
    for pin in ['8','11','16','22','28','37','47']:s.connect('U11',pin,'VDD0V95_ETH',12.7,global_net=True)
    for pin in ['19','29','33','34','43','46']:s.connect('U11',pin,'VCC3V3_ETH',12.7,global_net=True)
    s.connect('U11','15','VCC3V3_ETH_PLL',12.7,global_net=True)
    for pin in ['40','49']:s.wire(u[pin],(u[pin][0],157.48))
    s.wire((u['40'][0],157.48),(u['49'][0],157.48));s.power('GND',(u['49'][0],157.48))
    s.text('Pin43 EVDD33 uses 3.3V. Pin40 and EP49 are GND.\nPins4/5/7 are NC; do not fit BGS regulator parts.\nEP49 requires a low-inductance thermal ground connection.',17.78,170.18,1.05)
    # Each entry corresponds to one physical supply pin in the Realtek reference.
    banks=[('3.3V local bypass — at the indicated pins','VCC3V3_ETH',15.24,
            [(670,'22uF','19'),(671,'22uF','33'),(672,'22uF','34'),(673,'4.7uF','43'),(674,'100nF','29'),(675,'100nF','46')]),
           ('0.95V local bypass — at the indicated pins','VDD0V95_ETH',104.14,
            [(678,'4.7uF','11'),(679,'4.7uF','16'),(680,'4.7uF','22'),(681,'4.7uF','47'),(682,'4.7uF','37'),(683,'22uF','8'),(684,'22uF','28')])]
    for title,rail,y,entries in banks:
        s.box(title,185.42,y,220.98,78.74)
        xs=[200.66+i*27.94 for i in range(len(entries))]
        top=y+27.94;bottom=y+50.8
        s.power(rail,(xs[0],top))
        for i,((n,value,pin),x) in enumerate(zip(entries,xs)):
            c=local_cap(s,f'C{n}',value,x,y+38.1)
            s.wire((x,top),c['1']);s.wire(c['2'],(x,bottom))
            if i:s.wire((xs[i-1],top),(x,top));s.wire((xs[i-1],bottom),(x,bottom))
            if 0<i<len(xs)-1:s.junction((x,top));s.junction((x,bottom))
            s.text('pin '+pin,x-2.54,y+60.96,1.05)
        s.power('GND',(xs[-1],bottom))
    s.box('Pin15 PLL filter — separate branch, close to U11',10.16,198.12,396.24,50.8)
    f=part(s,'ferrite','Device:FerriteBead','FB670','33R @ 100MHz',116.84,218.44,'full-adapter:Murata_BLM18PG330SN1D_0603',90)
    a,b=sorted(f.values(),key=lambda p:p[0]);s.wire(a,(48.26,218.44));s.power('VCC3V3_ETH',(48.26,218.44))
    s.wire(b,(271.78,218.44));s.power('VCC3V3_ETH_PLL',(271.78,218.44))
    for n,value,x in [(676,'22uF',218.44),(677,'100nF',271.78)]:
        c=local_cap(s,f'C{n}',value,x,228.6);s.wire((x,218.44),c['1']);s.junction((x,218.44));s.wire(c['2'],(x,238.76))
    s.wire((218.44,238.76),(271.78,238.76));s.power('GND',(271.78,238.76))
    s.place('power:PWR_FLAG','#FLGethpll',180.34,218.44);s.junction((180.34,218.44))
    s.text('BLM18PG330SN1D\nDCR <=25mR initial / 50mR after tests.\nNo other loads on the filtered branch.',304.8,220.98,1.05)
    s.text('22uF at 3.3V analog pins and 4.7uF at 0.95V analog pins retain margin after DC-bias loss; 4.7uF also replaces 1uF bypass.\nDistribute local capacitors at the named pins. Keep regulator compensation capacitors at U12/U13. See ethernet-controller-qualification.json.',15.24,269.24,1.05)
    return finish(s)


def ethernet_clock_config():
    s=Sheet('ethernet-clock-config','RTL8125BG clock, straps and MDI interface')
    s.box('Clock and startup configuration',10.16,15.24,198.12,119.38)
    s.place('full-adapter:RTL8125BG-CG','U11',106.68,81.28,unit=4)
    for pin,net in {'3':'ETH_GPI','10':'ETH_XTAL_IN','9':'ETH_XTAL_OUT','25':'ETH_EEDO_IDLE','27':'ETH_LED1','30':'ETH_EEDI_STRAP','32':'ETH_EESEL_STRAP'}.items():
        s.connect('U11',pin,net,7.62)
    s.connect('U11','6','ETH_CORE_ENABLE',7.62,global_net=True)
    for pin in ['26','31','35']:s.connect('U11',pin,None)
    s.text('Pin6 drives U13 EN; the 47k pulldown is on its supply page.\nNo external EEPROM or flash is fitted. LED3 is unused.\nBoot/provisioning must assign a stable, unique local MAC.',17.78,111.76,1.05)
    s.box('25MHz / 12pF crystal — local loop',215.9,15.24,190.5,119.38)
    r=resistor(s,'R671','0R',381,50.8)
    s.wire(r['1'],(381,38.1));s.label('ETH_XTAL_OUT',(381,38.1),180)
    s.wire(r['2'],(381,73.66))
    y=part(s,'crystal','Device:Crystal_GND24','Y670','25MHz / 12pF',314.96,73.66,'full-adapter:YXC_X322525MOB4SI')
    props(s,314.96,60.96)
    s.wire(y['1'],(243.84,73.66));s.label('ETH_XTAL_IN',(243.84,73.66),180)
    s.wire(y['3'],(381,73.66));s.label('ETH_XTAL_LOAD',(381,73.66),180)
    s.wire(y['2'],(314.96,93.98));s.power('GND',(314.96,93.98))
    p=json.loads((ROOT/'research/processor-clock-parts.json').read_text())['load_capacitor']
    for ref,x in [('C685',243.84),('C686',381)]:
        c=s.place('Device:C',ref,x,104.14,value='20pF C0G',fields={'MPN':p['model'],'Manufacturer':p['manufacturer'],'LCSC':p['lcsc'],'Footprint':'Capacitor_SMD:C_0402_1005Metric'})
        s.wire((x,73.66),c['1']);s.junction((x,73.66));s.wire(c['2'],(x,114.3));s.power('GND',(x,114.3))
    s.text('R671 is on CKXTAL2 only. Tune damping and load on hardware.\nCL = 20pF / 2 + estimated 2pF stray. Drive must stay <=100uW.',223.52,121.92,1.05)
    s.box('2.5GbE MDI — magnetics integration next',10.16,142.24,198.12,106.68)
    s.place('full-adapter:RTL8125BG-CG','U11',50.8,198.12,unit=3)
    props(s,50.8,160.02)
    r=part(s,'rset','Device:R_Small_US','R670','2.49kR 0.1%',127,177.8,'Resistor_SMD:R_0603_1608Metric',90)
    s.wire(s.pins['U11','12'],r['1']);s.wire(r['2'],(165.1,177.8));s.wire((165.1,177.8),(165.1,182.88));s.power('GND',(165.1,182.88))
    for pin,net in {'13':'ETH_MDI0_P','14':'ETH_MDI0_N','17':'ETH_MDI1_P','18':'ETH_MDI1_N','20':'ETH_MDI2_P','21':'ETH_MDI2_N','23':'ETH_MDI3_P','24':'ETH_MDI3_N'}.items():s.connect('U11',pin,net,12.7,global_net=True)
    s.text('R670: place at pin12.\nMDI endpoints are unfinished\nuntil verified 2.5G/PoE\nmagnetics are connected.',142.24,203.2,1.05)
    s.box('Defined reset states — same supply domain',215.9,142.24,190.5,106.68)
    for ref,net,x in [('R672','ETH_GPI',241.3),('R673','ETH_LED1',330.2)]:
        r=rpart(s,ref,'4.7kR 1%',x,175.26)
        s.wire(r['1'],(x,165.1));s.power('VCC3V3_ETH',(x,165.1));s.wire(r['2'],(x,185.42));s.label(net,(x,185.42))
    for ref,net,x in [('R674','ETH_EEDO_IDLE',231.14),('R675','ETH_EEDI_STRAP',292.1),('R676','ETH_EESEL_STRAP',355.6)]:
        r=resistor(s,ref,'47kR 1%',x,215.9)
        s.wire(r['1'],(x,205.74));s.label(net,(x,205.74));s.wire(r['2'],(x,226.06));s.power('GND',(x,226.06))
    s.text('GPI and LED1 must latch HIGH to avoid test mode.\nEEDI LOW selects 3-wire; EESEL LOW selects 93C46 size.\nEEDO is held LOW with no EEPROM. See provisioning limits.',223.52,233.68,1.05)
    s.text('Realtek reference V122, Ethernet PHY page; RTL8125BG V1.5 Tables6/11/29. No OTP programming is authorized by this design.\nTotal crystal error must remain within +/-50ppm including initial tolerance, temperature, first-year aging and PCB loading.',15.24,261.62,1.05)
    return finish(s)


def ethernet_pcie():
    s=Sheet('ethernet-pcie','RK3568 PCIe2 x1 to RTL8125BG')
    s.box('RK3568 MULTI_PHY2 — PCIe RC mode',10.16,15.24,198.12,106.68)
    s.place('full-adapter:RK3568B2','U1',88.9,76.2,unit=28)
    for pin,net in {'Y27':'PCIE_ETH_TO_SOC_P','Y28':'PCIE_ETH_TO_SOC_N','W27':'SOC_PCIE_TX_P','W28':'SOC_PCIE_TX_N','V24':'PCIE_REFCLK_P','V25':'PCIE_REFCLK_N'}.items():s.connect('U1',pin,net,7.62)
    s.text('Reference clock outputs to the endpoint in RC mode.\nMULTI_PHY2 is dedicated to PCIe2; do not select SATA2/QSGMII.\nSelect functional CLKREQn/WAKEn M1 on VCCIO5 later.',17.78,101.6,1.05)
    s.box('RTL8125BG PCIe endpoint',215.9,15.24,190.5,106.68)
    s.place('full-adapter:RTL8125BG-CG','U11',312.42,76.2,unit=2)
    for pin,net in {'1':'ETH_ISOLATE_N','2':'ETH_WAKE_N','36':'ETH_PERST_N','38':'ETH_PCIE_TX_P','39':'ETH_PCIE_TX_N','41':'PCIE_SOC_TO_ETH_P','42':'PCIE_SOC_TO_ETH_N','44':'PCIE_REFCLK_P','45':'PCIE_REFCLK_N','48':'ETH_CLKREQ_N'}.items():s.connect('U11',pin,net,7.62)
    s.text('Control pull-ups use the Ethernet supply. Host-side isolation,\nreset qualification and functional GPIO connections are unfinished.',223.52,109.22,1.05)
    s.box('One AC capacitor per transmit leg — at its source',10.16,129.54,396.24,55.88)
    for ref,leftnet,rightnet,x,y in [('C687','SOC_PCIE_TX_P','PCIE_SOC_TO_ETH_P',101.6,152.4),('C688','SOC_PCIE_TX_N','PCIE_SOC_TO_ETH_N',101.6,172.72),('C689','ETH_PCIE_TX_P','PCIE_ETH_TO_SOC_P',302.26,152.4),('C690','ETH_PCIE_TX_N','PCIE_ETH_TO_SOC_N',302.26,172.72)]:
        p=json.loads((ROOT/'research/ddr-passives-search.json').read_text())['searches'][6]['results'][0]
        c=s.place('Device:C',ref,x,y,angle=90,value='100nF',fields={'MPN':p['model'],'Manufacturer':p['manufacturer'],'LCSC':p['lcsc'],'Footprint':'Capacitor_SMD:C_0402_1005Metric'})
        a,b=sorted(c.values(),key=lambda p:p[0]);s.wire(a,(x-17.78,y));s.label(leftnet,(x-17.78,y),180);s.wire(b,(x+17.78,y));s.label(rightnet,(x+17.78,y))
    s.box('Local control defaults — cold Ethernet powers off with S0',10.16,193.04,396.24,55.88)
    for ref,net,x in [('R677','ETH_WAKE_N',38.1),('R678','ETH_CLKREQ_N',116.84)]:
        r=rpart(s,ref,'4.7kR 1%',x,218.44);s.wire(r['1'],(x,210.82));s.power('VCC3V3_ETH',(x,210.82));s.wire(r['2'],(x,231.14));s.label(net,(x,231.14))
    r=resistor(s,'R679','47kR 1%',198.12,228.6);s.wire(r['1'],(198.12,213.36));s.label('ETH_PERST_N',(198.12,213.36));s.wire(r['2'],(198.12,238.76));s.power('GND',(198.12,238.76))
    from build_ddr_schematic import passive
    r=passive(s,'R680','1kR 1%',302.26,213.36,90);s.wire(r['1'],(264.16,213.36));s.power('VCC3V3_ETH',(264.16,213.36));s.wire(r['2'],(353.06,213.36));s.label('ETH_ISOLATE_N',(353.06,213.36))
    r=part(s,'isolate_pulldown','Device:R_Small_US','R681','15kR 1%',353.06,228.6,'Resistor_SMD:R_0402_1005Metric');s.wire((353.06,213.36),r['1']);s.wire(r['2'],(353.06,238.76));s.power('GND',(353.06,238.76))
    s.text('R679 holds PERSTB asserted until the hardware reset circuit is added. Do not bridge control pins directly across the two 3.3V domains.\nRoute each lane as a controlled-impedance pair with no stubs. C687/C688 at U1; C689/C690 at U11. Full routing and signal validation remain open.',15.24,266.7,1.05)
    return finish(s)
