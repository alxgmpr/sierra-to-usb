"""Eight-bit eMMC storage, local power bypass and accessible recovery pads."""
import json
from schematic import ROOT,Sheet


def resistor(s,ref,value,x,y,angle=0):
    pmic=json.loads((ROOT/'research/pmic-control-passives.json').read_text())
    if value=='10kR 1%':p=pmic['pullup_10k']['results'][0]
    elif value=='22R 1%':p=pmic['resistor_22']['results'][0]
    elif value=='0R':p=json.loads((ROOT/'research/processor-control-passives.json').read_text())['zero_ohm']['results'][0]
    elif value=='47kR 1%':p=json.loads((ROOT/'research/emmc-qualification.json').read_text())['pulldown']
    else:raise ValueError(value)
    return s.place('Device:R_Small_US',ref,x,y,value=value,angle=angle,fields={
        'Footprint':'Resistor_SMD:R_0402_1005Metric','MPN':p['model'],'LCSC':p['lcsc'],'Manufacturer':p['manufacturer']})


def cap(s,ref,value,x,y):
    source=json.loads((ROOT/'research/ddr-passives-search.json').read_text())
    if value=='100nF':p=source['searches'][6]['results'][0]
    elif value=='22uF':p={'model':'CL21A226MAYNNNE','lcsc':'C602037','manufacturer':'Samsung'}
    elif value=='1uF':p={'model':'CL05A105KA5NQNC','lcsc':'C52923','manufacturer':'Samsung'}
    else:raise ValueError(value)
    return s.place('Device:C',ref,x,y,value=value,fields={
        'Footprint':'Capacitor_SMD:C_0805_2012Metric' if value=='22uF' else 'Capacitor_SMD:C_0402_1005Metric',
        'MPN':p['model'],'LCSC':p['lcsc'],'Manufacturer':p['manufacturer']})


def tp(s,ref,value,x,y):
    return s.place('Connector:TestPoint',ref,x,y,value=value,
                   fields={'Footprint':'TestPoint:TestPoint_Pad_D1.0mm'})


def emmc_signals():
    s=Sheet('emmc-signals','8GB eMMC interface, reset and boot recovery')
    manifest=json.loads((ROOT/'research/core-symbols.json').read_text())
    s.box('Processor storage bank — VCCIO2 = 1.8V',10.16,15.24,175.26,175.26)
    s.place('full-adapter:RK3568B2','U1',66.04,73.66,unit=10)
    connections={p['ball']:p['name'] for p in manifest['RK3568B2'][9]['pins'] if p['name'].startswith('EMMC_')}
    connections.update({'A23':'SOC_EMMC_CLK','A26':'EMMC_DS','F20':'EMMC_RESET_L'})
    for p in manifest['RK3568B2'][9]['pins']:s.connect('U1',p['ball'],connections.get(p['ball']),7.62)
    r=resistor(s,'R600','22R 1%',91.44,124.46,90)
    s.wire(r['1'],(48.26,124.46));s.label('SOC_EMMC_CLK',(48.26,124.46),180)
    s.wire(r['2'],(142.24,124.46));s.label('EMMC_CLK',(142.24,124.46))
    p=tp(s,'TP600','MASKROM D0',60.96,149.86)
    s.wire(p['1'],(60.96,157.48));s.label('EMMC_D0',(60.96,157.48))
    p=tp(s,'TP601','GND',134.62,149.86)
    s.wire(p['1'],(134.62,157.48));s.power('GND',(134.62,157.48))
    s.text('R600: place at U1 A23. FLASH_VOL_SEL is strapped HIGH.\nFSPI/NAND alternatives are unused; no storage-bus branches.',17.78,172.72,1.1)
    s.box('SanDisk SDINBDG4-8G — eight-bit bus',195.58,15.24,210.82,175.26)
    s.place('full-adapter:SDINBDG4-8G','U6',330.2,76.2,unit=1)
    for p in manifest['SDINBDG4-8G'][0]['pins']:
        name=p['name']
        net='EMMC_D'+name[3:] if name.startswith('DAT') else {
            'CMD':'EMMC_CMD','CLK':'EMMC_CLK','RST_n':'EMMC_RESET_L','RCLK':'EMMC_DS_RAW'}[name]
        s.connect('U6',p['ball'],net,15.24)
    r=resistor(s,'R601','0R',302.26,132.08,90)
    s.wire(r['1'],(248.92,132.08));s.label('EMMC_DS_RAW',(248.92,132.08),180)
    s.wire(r['2'],(363.22,132.08));s.label('EMMC_DS',(363.22,132.08))
    r=resistor(s,'R602','47kR 1%',363.22,147.32)
    s.wire((363.22,132.08),r['1']);s.wire(r['2'],(363.22,157.48));s.power('GND',(363.22,157.48))
    s.text('R601: place near U6 H5. R602 defines the strobe idle state.\nEnable the eMMC hardware-reset function during provisioning.\nVCC/VCCQ, internal bypass and VSF test pads are on emmc-power.',203.2,170.18,1.1)
    s.box('Defined idle states — pull-ups to the same 1.8V storage rail',10.16,198.12,396.24,50.8)
    s.power('VCC1V8_SYS',(30.48,213.36))
    nets=[f'EMMC_D{i}' for i in range(8)]+['EMMC_CMD','EMMC_RESET_L']
    xs=[30.48+i*38.1 for i in range(10)]
    for i,(net,x) in enumerate(zip(nets,xs)):
        r=resistor(s,f'R{610+i}','10kR 1%',x,220.98)
        s.wire((x,213.36),r['1'])
        if i:s.wire((xs[i-1],213.36),(x,213.36))
        if 0<i<len(xs)-1:s.junction((x,213.36))
        s.wire(r['2'],(x,233.68));s.label(net,(x,233.68))
    s.text('Recovery: Rockchip documents shorting D0 to GND during power-on, then releasing after MaskROM USB enumeration; misuse can damage IO.\nReserve these pads for controlled service recovery. USB recovery connector and normal boot/recovery controls are captured separately.\nAll data/CMD pull-ups are populated for defined reset behavior; maximum static pull-up load is 1.8mA with all ten nets LOW.',15.24,259.08,1.05)
    return s


def emmc_power():
    s=Sheet('emmc-power','eMMC power, internal bypass and unused balls')
    manifest=json.loads((ROOT/'research/core-symbols.json').read_text())['SDINBDG4-8G']
    s.box('Flash and controller supplies — local bypass',10.16,15.24,254,142.24)
    s.place('full-adapter:SDINBDG4-8G','U6',50.8,88.9,unit=2)
    for index,(name,rail,count,start) in enumerate([('VCC','VCC3V3_S0',4,600),('VCCQ','VCC1V8_SYS',5,605)]):
        pin=next(p for p in manifest[1]['pins'] if p['name']==name)
        anchor=s.pins['U6',pin['ball']];y=anchor[1]
        s.wire(anchor,(91.44,y));s.power(rail,(91.44,y))
        xs=[114.3+j*22.86 for j in range(count+1)]
        previous=(91.44,y)
        for j,x in enumerate(xs):
            c=cap(s,f'C{start+j}','22uF' if j==0 else '100nF',x,y+7.62)
            s.wire(previous,(x,y));s.wire((x,y),c['1'])
            if j<count:s.junction((x,y))
            s.wire(c['2'],(x,y+15.24))
            if j:s.wire((xs[j-1],y+15.24),(x,y+15.24))
            if 0<j<count:s.junction((x,y+15.24))
            previous=(x,y)
        s.power('GND',(xs[-1],y+15.24))
    grounds=[s.pins['U6',p['ball']] for p in manifest[1]['pins'] if p['name'] in ['VSS','VSSQ']]
    for p in grounds:s.wire(p,(91.44,p[1]))
    s.wire((91.44,grounds[0][1]),(91.44,grounds[1][1]));s.wire((91.44,grounds[1][1]),(91.44,139.7));s.junction((91.44,grounds[1][1]));s.power('GND',(91.44,139.7))
    s.text('One 100nF per supply ball. Put bulk + local 100nF by F5 / P3.\n22uF bulk provides margin for DC-bias loss; use short ground returns.\nC600 / C605: Samsung CL21A226MAYNNNE, 25V X5R.',106.68,119.38,1.05)
    s.box('Internal regulator and isolated VSF test pads',271.78,15.24,134.62,142.24)
    s.place('full-adapter:SDINBDG4-8G','U6',307.34,83.82,unit=3)
    p=s.pins['U6','C2'];c=cap(s,'C611','1uF',386.08,p[1]+7.62)
    s.wire(p,(386.08,p[1]));s.wire((386.08,p[1]),c['1']);s.wire(c['2'],(386.08,p[1]+15.24));s.power('GND',(386.08,p[1]+15.24))
    for i,ball in enumerate(['E9','E10','F10','K10']):
        p=s.pins['U6',ball];probe=tp(s,f'TP{610+i}',f'VSF{i+1}',365.76,p[1]);s.wire(p,probe['1'])
    p=tp(s,'TP614','GND',391.16,139.7);s.wire(p['1'],(391.16,147.32));s.power('GND',(391.16,147.32))
    s.text('C611: only to VDDi/GND.\nVSF pads float; do not strap.\nPlace GND pad beside VSF group.',279.4,137.16,1.05)
    s.box('All 116 NC balls — explicitly disconnected',10.16,167.64,396.24,76.2)
    for i,unit in enumerate(range(4,8)):
        s.place('full-adapter:SDINBDG4-8G','U6',58.42+i*101.6,213.36,unit=unit)
        for p in manifest[unit-1]['pins']:s.connect('U6',p['ball'],None)
    s.text('SanDisk DOC56-34-01508 Rev1.4 pp23,33–36. VDDi bypass 0.1–2.2uF; it must never power an external load.\nKeep bypass-loop inductance <3nH and resistance <0.5R. VSF test pads are service-only; keep their nearby ground accessible.\nTypical peak current at 25C: HS200 VCC 150mA / VCCQ 210mA; these are not worst-case power-budget guarantees.',15.24,259.08,1.05)
    return s
