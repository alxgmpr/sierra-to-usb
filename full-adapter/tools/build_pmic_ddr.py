"""RK809 BUCK3, hardware-selected 1.5008 V DDR3 rail."""
import json
from schematic import ROOT, Sheet


def pmic_ddr():
    s=Sheet('pmic-ddr','DDR3 buck and hardware voltage selection')
    source=json.loads((ROOT/'research/pmic-buck-passives.json').read_text())
    cap22=next(p for p in json.loads((ROOT/'research/cpu-passives-search-2.json').read_text())[3]['result']['results']
               if p['model']=='CL21A226MAYNNNE')
    parts={'22uF':cap22,'0.47uH':source['inductor']['results'][0],
           '87.6kR 0.1%':next(p for p in source['divider_top']['results'] if p['package']=='0402'),
           '100kR 0.1%':source['divider_bottom']['results'][0]}

    def passive(ref,value,x,y,angle=0):
        part=parts[value]
        if ref.startswith('C'):lib,fp='Device:C','Capacitor_SMD:C_0805_2012Metric'
        elif ref.startswith('L'):lib,fp='Device:L','full-adapter:L_TDK_SPM5030'
        else:lib,fp='Device:R_Small_US','Resistor_SMD:R_0402_1005Metric'
        return s.place(lib,ref,x,y,value=value,angle=angle,fields={
            'Footprint':fp,'Manufacturer':part['manufacturer'],'MPN':part['model'],'LCSC':part['lcsc']})

    s.box('RK809-5 BUCK3 — 1.5008V nominal, startup slot 3, 1.5A maximum',10.16,15.24,396.24,180.34)
    u=s.place('full-adapter:RK809-5','U5',152.4,91.44,unit=3)
    for i,x in enumerate([35.56,66.04]):
        c=passive(f'C{420+i}','22uF',x,55.88)
        s.wire((x,43.18),c['1']);s.wire(c['2'],(x,63.5))
    s.wire((35.56,43.18),(66.04,43.18));s.wire((35.56,63.5),(66.04,63.5))
    s.power('VCC3V3_SYS',(35.56,43.18));s.power('GND',(66.04,63.5))
    s.wire((66.04,43.18),(111.76,43.18));s.junction((66.04,43.18))
    s.wire((111.76,43.18),(111.76,88.9));s.wire((111.76,88.9),u['24'])
    l=passive('L420','0.47uH',205.74,88.9,angle=90)
    a,b=sorted(l.values(),key=lambda p:p[0]);s.wire(u['25'],a)
    s.wire(b,(375.92,88.9));s.power('VCC_DDR',(355.6,88.9));s.junction((355.6,88.9))
    # U5 SW3 drives this rail through L420; the flag conveys that existing path.
    s.place('power:PWR_FLAG','#FLGddr',375.92,88.9)
    for i,x in enumerate([248.92,289.56,330.2]):
        c=passive(f'C{422+i}','22uF',x,111.76)
        s.wire((x,88.9),c['1']);s.junction((x,88.9))
        s.wire(c['2'],(x,121.92))
        if i:s.wire((x-40.64,121.92),(x,121.92))
        if i==1:s.junction((x,121.92))
    s.power('GND',(330.2,121.92))
    s.wire(u['26'],(119.38,91.44));s.wire((119.38,91.44),(119.38,114.3))
    s.power('VCC_DDR',(119.38,114.3))
    upper=passive('R420','87.6kR 0.1%',76.2,124.46)
    lower=passive('R421','100kR 0.1%',76.2,157.48)
    s.wire((76.2,111.76),upper['1']);s.power('VCC_DDR',(76.2,111.76))
    s.wire(upper['2'],(76.2,139.7));s.wire((76.2,139.7),lower['1']);s.junction((76.2,139.7))
    s.wire(u['27'],(129.54,93.98));s.wire((129.54,93.98),(129.54,139.7))
    s.wire((129.54,139.7),(76.2,139.7));s.label('DDR_BUCK_FB',(129.54,139.7))
    s.wire(lower['2'],(76.2,170.18));s.power('GND',(76.2,170.18))
    s.text('VBUCK3 senses the output bank. Keep FB3/divider away from SW3.\nHardware divider selects 1.5V before any firmware runs.\nDo not change BUCK3 to internal-divider mode in the bootloader.',177.8,144.78,1.27)
    s.text('2 x 22uF input; 3 x 22uF local output, plus DDR-side bypass.\nUse the recorded Samsung DC-bias data for capacitance derating.\nKeep the VCC3 / SW3 / input-ground switching loop compact.',177.8,170.18,1.27)
    s.text('Reference: RK809 Rev 1.7; AN_RK809 V1.1 section 6.2; Rockchip tablet p22.\n0.8V x (1 + 87.6k / 100k) = 1.5008V. Resistors: 0.1%, 25ppm/C.\nVerify ripple, load transients and cold/hot voltage against Hynix 1.425–1.575V limits.',15.24,213.36,1.27)
    return s
