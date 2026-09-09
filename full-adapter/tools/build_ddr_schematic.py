"""Capture the selected 1GiB / x32 DDR3 subsystem in the current hierarchy."""
from pathlib import Path
import json
import re
from schematic import ROOT, ROOT_ID, Q, Sheet, effects, uid

MANIFEST = json.loads((ROOT / 'research/core-symbols.json').read_text())
PARTS = [s['results'][0] for s in json.loads((ROOT / 'research/ddr-passives-search.json').read_text())['searches']]
PART_BY_VALUE = dict(zip(['1kR 1%', '120R 1%', '240R 1%', '49.9R 1%', '100pF C0G', '1nF', '100nF', '4.7uF'], PARTS))
CPU = 'full-adapter:RK3568B2'
RAM = 'full-adapter:H5TQ4G63EFR-RDC'


def ddr_net(name):
    name = re.sub(r'(DDR3_(?:DQS\d|CLK))([PN])$', r'\1_\2', name)
    return re.sub(r'n$', '_N', name)


def passive(sheet, ref, value, x, y, angle=0, dnp=False):
    part = PART_BY_VALUE[value]
    resistor = ref.startswith('R')
    fp = 'Resistor_SMD:R_0402_1005Metric' if resistor else ('Capacitor_SMD:C_0603_1608Metric' if part['package'] == '0603' else 'Capacitor_SMD:C_0402_1005Metric')
    return sheet.place('Device:R_Small_US' if resistor else 'Device:C', ref, x, y,
                       value=value, angle=angle, dnp=dnp,
                       fields={'Footprint':fp, 'MPN':part['model'], 'Manufacturer':part['manufacturer'], 'LCSC':part['lcsc']})


def signals():
    s = Sheet('ddr-signals', '1 GiB DDR3: command, data and clock termination')
    s.box('RK3568B2 — single rank, x32', 10.16, 15.24, 243.84, 157.48)
    locations = {1:(43.18,88.9), 2:(132.08,55.88), 3:(132.08,116.84), 4:(208.28,55.88), 5:(208.28,116.84)}
    for unit, (x,y) in locations.items():
        s.place(CPU,'U1',x,y,unit=unit)
        for p in MANIFEST['RK3568B2'][unit-1]['pins']:
            net = None if p['name'] in {'DDR3_A15','DDR3_ODT1','DDR3_CS1n'} else ddr_net(p['name'])
            s.connect('U1',p['ball'],net)
    for ref, y, offset in [('U2',80.01,0), ('U3',200.66,16)]:
        s.place(RAM,ref,330.2,y,unit=1)
        for p in MANIFEST['H5TQ4G63EFR-RDC'][0]['pins']:
            name = p['name']
            if re.fullmatch(r'DQ[LU]\d', name):
                bit = int(name[-1]) + (8 if name[2] == 'U' else 0) + offset
                net = f'DDR3_DQ{bit}'
            elif name in {'DML','DMU'}:
                net = 'DDR3_DM' + str(offset//8 + (1 if name == 'DMU' else 0))
            elif name.startswith('DQS'):
                net = f'DDR3_DQS{offset//8 + (1 if name[3] == "U" else 0)}_{name[-1]}'
            elif name.startswith(('A','BA')):
                net = 'DDR3_' + name.split('/')[0]
            elif name in {'CK_P','CK_N'}:
                net = 'DDR3_CLK_' + name[-1]
            elif name == 'CS_N': net = 'DDR3_CS0_N'
            elif name == 'ODT': net = 'DDR3_ODT0'
            else: net = 'DDR3_' + name
            s.connect(ref,p['ball'],net)
        s.text(f'{ref}: data bits {offset}–{offset+15}',304.8,y+47.0)
    s.box('Clock termination — at the T branch',10.16,180.34,139.7,63.5)
    for ref, net, y in [('R101','DDR3_CLK_P',200.66),('R102','DDR3_CLK_N',218.44)]:
        p = passive(s,ref,'49.9R 1%',73.66,y,angle=90)
        left, right = sorted(p.values(),key=lambda p:p[0])
        s.wire((43.18,y),left);s.label(net,(43.18,y))
        s.wire(right,(96.52,y))
    s.wire((96.52,200.66),(96.52,210.82));s.wire((96.52,210.82),(96.52,218.44));s.junction((96.52,210.82))
    p = passive(s,'C101','100pF C0G',116.84,210.82,angle=90)
    left,right=sorted(p.values(),key=lambda p:p[0]);s.wire((96.52,210.82),left)
    s.wire(right,(137.16,210.82));s.wire((137.16,210.82),(137.16,218.44));s.power('GND',(137.16,218.44))
    s.text('Rockchip HW Guide V1.2, Fig. 3-42:\n49.9R + 49.9R, common 100pF C0G to ground.',15.24,228.6)
    s.box('Unused ECC byte',162.56,180.34,91.44,86.36)
    s.place(CPU,'U1',200.66,224.79,unit=6)
    for p in MANIFEST['RK3568B2'][5]['pins']: s.connect('U1',p['ball'],None)
    # Optional memory reset filters, kept with the memory signals on this page.
    for ref,x in [('C102',281.94),('C103',281.94)]:
        y=119.38 if ref=='C102' else 240.03
        p=passive(s,ref,'1nF',x,y,dnp=True)
        s.connect(ref,'1','DDR3_RESET_N',2.54)
        s.wire(p['2'],(x,y+7.62));s.power('GND',(x,y+7.62))
    s.text('4Gb x16 + 4Gb x16 = 1 GiB. 1.5V only.\nInitial boot target: DDR3 1560 MT/s (780 MHz); training configuration pending.\nRD grade supports up to 1866 MT/s. No A15 or second chip select is required.\nDQ/DM point-to-point; command and clock branch to both devices.\nDo not substitute DDR4/LPDDR pin-function names when routing.',15.24,251.46)
    return s


def supply_bus(s, ref, unit, net, up=True):
    ps=[s.pins[ref,p['ball']] for p in unit['pins'] if p['type']=='power_in' and ((p['side']=='T') == up)]
    if not ps:return None
    y=ps[0][1]+(-5.08 if up else 5.08)
    ends=sorted((p[0],round(y,6)) for p in ps)
    for p,end in zip(sorted(ps),ends):s.wire(p,end)
    for a,b in zip(ends,ends[1:]):s.wire(a,b)
    for p in ends[1:-1]:s.junction(p)
    s.power(net,ends[-1] if up else ends[0])
    return ends[0]


def power_page():
    s=Sheet('ddr-power','DDR3 references, calibration and local bypass')
    cnum=120
    for ref,cx,ncap,model,unitnum in [('U1',73.66,14,'RK3568B2',7),('U2',208.28,18,'H5TQ4G63EFR-RDC',2),('U3',342.9,18,'H5TQ4G63EFR-RDC',2)]:
        s.box(ref+' — DDR supplies',cx-60.96,15.24,124.46,231.14)
        s.place('full-adapter:'+model,ref,cx,73.66,unit=unitnum)
        u=MANIFEST[model][unitnum-1]
        rail=supply_bus(s,ref,u,'VCC_DDR',True)
        trunk=cx-(58.42 if ref=="U1" else 66.04)
        s.wire(rail,(trunk,rail[1]))
        previous_y=rail[1]
        if ref!='U1':supply_bus(s,ref,u,'GND',False)
        # 100nF for each VDD/VDDQ ball. Bank wiring represents the common rail;
        # placement must distribute these at the relevant physical supply balls.
        rows=(ncap+6)//7
        for row in range(rows):
            count=min(7,ncap-row*7)
            y=137.16+row*25.4
            xs=[cx-48.26+i*15.24 for i in range(count)]
            top,bottom=y-7.62,y+7.62
            for x in xs:
                refc='C'+str(cnum);cnum+=1
                p=passive(s,refc,'100nF',x,y)
                s.wire((x,top),p['1']);s.wire(p['2'],(x,bottom))
            for x1,x2 in zip(xs,xs[1:]):s.wire((x1,top),(x2,top));s.wire((x1,bottom),(x2,bottom))
            for x in xs[1:-1]:s.junction((x,top));s.junction((x,bottom))
            s.wire((trunk,previous_y),(trunk,top));s.wire((trunk,top),(xs[0],top))
            previous_y=top
            s.power('GND',(xs[0],bottom))
        refc='C'+str(cnum);cnum+=1
        p=passive(s,refc,'4.7uF',cx+40.64,213.36)
        s.wire((trunk,previous_y),(trunk,205.74));s.wire((trunk,205.74),(cx+40.64,205.74));s.wire(p['1'],(cx+40.64,205.74))
        s.wire(p['2'],(cx+40.64,220.98));s.power('GND',(cx+40.64,220.98))
        s.text(f'{ncap} × 100nF, distributed at supply balls.\n4.7uF local bulk, in addition to PMIC output caps.',cx-55.88,233.68)
    # RK3568 calibration resistor and the mandatory reference bypass pair.
    rzq=s.pins['U1','H7']; r=passive(s,'R103','120R 1%',114.3,88.9)
    s.wire(rzq,(114.3,rzq[1]));s.wire((114.3,rzq[1]),r['1']);s.wire(r['2'],(114.3,99.06));s.power('GND',(114.3,99.06))
    v=s.pins['U1','P8'];s.wire(v,(101.6,v[1]));s.wire((101.6,v[1]),(101.6,109.22));s.label('DDR_VREFDQ',(101.6,109.22))
    a=passive(s,'C110','1nF',78.74,109.22,angle=90)
    left,right=sorted(a.values(),key=lambda p:p[0])
    s.wire(right,(101.6,109.22));s.junction((101.6,109.22))
    s.wire(left,(66.04,109.22));s.wire((66.04,109.22),(66.04,101.6));s.power('VCC_DDR',(66.04,101.6))
    b=passive(s,'C111','1nF',101.6,116.84)
    s.wire((101.6,109.22),b['1']);s.wire(b['2'],(101.6,121.92));s.power('GND',(101.6,121.92))
    # Each DRAM reference pin gets its own local 1nF; ZQ is 240R 1% to GND.
    for ref,cx,cr,rr in [('U2',208.28,112,'R106'),('U3',342.9,114,'R107')]:
        for ball,net,y,cap in [('M8','DDR_VREFCA',104.14,'C'+str(cr)),('H1','DDR_VREFDQ',116.84,'C'+str(cr+1))]:
            p=s.pins[ref,ball]; x=cx-48.26 if ball=='M8' else cx-35.56
            s.wire(p,(x,p[1]));s.wire((x,p[1]),(x,y-5.08));s.label(net,(x,y-5.08))
            c=passive(s,cap,'1nF',x,y)
            s.wire((x,y-5.08),c['1']);s.wire(c['2'],(x,y+5.08));s.power('GND',(x,y+5.08))
        p=s.pins[ref,'L8'];x=cx-58.42
        r=passive(s,rr,'240R 1%',x,88.9)
        s.wire(p,(x,p[1]));s.wire((x,p[1]),r['1']);s.wire(r['2'],(x,99.06));s.power('GND',(x,99.06))
    s.box('VREFCA = 0.75V nominal',15.24,251.46,139.7,30.48)
    p=passive(s,'R104','1kR 1%',55.88,266.7,angle=90);a,b=sorted(p.values(),key=lambda p:p[0])
    s.wire(a,(40.64,266.7));s.wire((40.64,266.7),(40.64,264.16));s.power('VCC_DDR',(40.64,264.16))
    s.wire(b,(76.2,266.7));s.label('DDR_VREFCA',(76.2,266.7))
    p=passive(s,'R105','1kR 1%',106.68,266.7,angle=90);a,b=sorted(p.values(),key=lambda p:p[0])
    s.wire((76.2,266.7),a);s.wire(b,(121.92,266.7));s.wire((121.92,266.7),(121.92,274.32));s.power('GND',(121.92,274.32))
    s.text('VCC_DDR = 1.5V from RK809-5 BUCK3. VDDQ and VDDQL both use 1.5V.\nReference connections: Rockchip HW Guide V1.2, Figures 2-14 / 2-15.\nU1 ground balls are on the processor core power page.',162.56,251.46)
    return s


def main():
    from build_core_power import core_power
    from build_cpu_power import cpu_power
    from build_pmic_ldo import pmic_ldo
    from build_pmic_ddr import pmic_ddr
    from build_pmic_core import pmic_core
    from build_pmic_aux import pmic_aux
    from build_pmic_control import pmic_control
    from build_processor_pmu import processor_pmu
    from build_processor_io_power import processor_io_power
    from build_processor_phy_power import processor_phy_power
    from build_processor_unused import processor_unused
    from build_processor_control import processor_control
    from build_processor_clock import processor_clock
    pages=[signals(),power_page(),core_power(),cpu_power(),pmic_ldo(),pmic_ddr(),pmic_core(),pmic_aux(),pmic_control(),processor_pmu(),processor_io_power(),processor_phy_power(),processor_unused(),processor_control(),processor_clock()]
    root=Sheet('full-adapter','Integrated Linux USB3 modem / 2.5GbE development board',root=True)
    root.text('CURRENT DESIGN — IN PROGRESS',20.32,20.32,2.54)
    root.text('RK3568B2 + 1 GiB DDR3 + PCIe RTL8125BG-CG\nUSB3 M.2 modem; isolated PoE and USB-C auxiliary power\n\nDDR, PMIC and processor supply capture is present. Remaining subsystems\nand PCB routing are active work. This project is not a manufacturing release.',20.32,33.02,1.8)
    for i,s in enumerate(pages):
        x,y=25.4+(i%3)*130.81,81.28+(i//3)*33.02
        root.items.append(f'(sheet (at {x} {y}) (size 111.76 20.32) (fields_autoplaced yes) (stroke (width 0.254) (type default)) (fill (color 0 0 0 0)) (uuid {Q(uid("sheet-block/"+s.name))}) (property "Sheetname" {Q(s.title)} (at {x} {y-1.27} 0) {effects(justify="left bottom")}) (property "Sheetfile" {Q(s.name+".kicad_sch")} (at {x} {y+21.59} 0) {effects(justify="left top")}))')
        s.save()
    root.save('A3')
    project=ROOT/'cad/full-adapter.kicad_pro'
    if not project.exists(): project.write_text(json.dumps({'meta':{'filename':'full-adapter.kicad_pro','version':1}},indent=2)+'\n')
    (ROOT/'cad/sym-lib-table').write_text('(sym_lib_table (version 7) (lib (name "full-adapter") (type "KiCad") (uri "${KIPRJMOD}/../lib/full-adapter.kicad_sym") (options "") (descr "Verified processor and memory symbols")))\n')
    (ROOT/'cad/fp-lib-table').write_text('(fp_lib_table (version 7) (lib (name "full-adapter") (type "KiCad") (uri "${KIPRJMOD}/../lib/full-adapter.pretty") (options "") (descr "Verified local footprints")))\n')
    (ROOT/'research/ddr-schematic-intent.json').write_text(json.dumps({s.name:s.intent for s in pages},indent=2)+'\n')
    print('Captured DDR and core power pages; full-system integration remains unfinished.')


if __name__=='__main__':main()
