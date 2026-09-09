"""RK860-0 CPU buck with hardware enable and remote sense compensation."""
import json
from schematic import ROOT, Sheet


def cpu_power():
    searches = json.loads((ROOT/'research/cpu-control-resistors.json').read_text())
    resistors = dict(zip(['51kR 1%','100R 1%','100kR 1%'],[r['result']['results'][0] for r in searches]))
    extra = json.loads((ROOT/'research/core-power-capacitors.json').read_text())
    ddr = json.loads((ROOT/'research/ddr-passives-search.json').read_text())['searches']
    allparts = json.loads((ROOT/'research/cpu-passives-search-2.json').read_text())
    cap22 = next(p for p in allparts[3]['result']['results'] if p['model']=='CL21A226MAYNNNE')
    parts = {**resistors, '22uF':cap22, '1uF':extra['one_uF']['results'][0], '100nF':ddr[6]['results'][0],
             '0.35uH':allparts[1]['result']['results'][0]}
    s = Sheet('cpu-regulator','CPU buck regulator and remote sense')
    def passive(ref,value,x,y,angle=0):
        part=parts[value]
        if ref.startswith('R'):lib,fp='Device:R_Small_US','Resistor_SMD:R_0402_1005Metric'
        elif ref.startswith('L'):lib,fp='Device:L','full-adapter:L_TDK_SPM5030'
        else:
            package={'0402':'0402_1005','0603':'0603_1608','0805':'0805_2012'}[part['package']]
            lib,fp='Device:C',f'Capacitor_SMD:C_{package}Metric'
        return s.place(lib,ref,x,y,value=value,angle=angle,
                       fields={'Footprint':fp,'Manufacturer':part['manufacturer'],'MPN':part['model'],'LCSC':part['lcsc']})
    s.box('RK860-0 — 0x40, 1.0V startup; limit CPU operating points to 1.15V',10.16,15.24,396.24,142.24)
    u=s.place('full-adapter:RK860-0','U4',147.32,96.52)
    # Four inputs retain more capacitance at 5V than the two nominal parts in
    # the reference; use the recorded Samsung bias curve in the power budget.
    for i,x in enumerate([25.4,45.72,66.04,86.36]):
        p=passive(f'C{300+i}','22uF',x,50.8)
        s.wire(p['1'],(x,43.18));s.wire(p['2'],(x,58.42))
        if i:s.wire((x-20.32,43.18),(x,43.18));s.wire((x-20.32,58.42),(x,58.42))
        if i:s.junction((x,43.18))
        if 0<i<3:s.junction((x,58.42))
    s.power('VCC5V_SYS',(25.4,43.18));s.power('GND',(86.36,58.42))
    s.wire((86.36,43.18),(106.68,43.18));s.wire((106.68,43.18),(106.68,91.44))
    s.wire((106.68,91.44),u['[D1,D2,E1,E2]'])
    r=passive('R300','51kR 1%',38.1,76.2)
    s.wire(r['1'],(38.1,66.04));s.power('VCC3V3_PMU',(38.1,66.04))
    s.wire(r['2'],(38.1,93.98));s.wire((38.1,93.98),u['A2'])
    c=passive('C304','100nF',38.1,109.22)
    s.wire((38.1,93.98),c['1']);s.junction((38.1,93.98))
    s.wire(c['2'],(38.1,116.84));s.power('GND',(38.1,116.84))
    s.wire(u['A1'],(68.58,96.52));s.label('PMIC_SLEEP_H',(88.9,96.52),global_net=True)
    r=passive('R302','100kR 1%',68.58,119.38)
    s.wire((68.58,96.52),r['1']);s.wire(r['2'],(68.58,127));s.power('GND',(68.58,127))
    for pin,net in [('A3','I2C0_SCL_PMIC'),('B1','I2C0_SDA_PMIC')]:s.connect('U4',pin,net,5.08,global_net=True)
    l=passive('L300','0.35uH',203.2,91.44,angle=90)
    a,b=sorted(l.values(),key=lambda p:p[0]);s.wire(u['[D3,D4,E3,E4]'],a)
    s.wire(b,(355.6,91.44));s.power('VDD_CPU',(355.6,91.44))
    # KiCad does not propagate power-output drive through a passive inductor.
    # This flag represents U4's verified LX -> L300 -> VDD_CPU path.
    s.wire((355.6,91.44),(375.92,91.44));s.junction((355.6,91.44))
    s.place('power:PWR_FLAG','#FLGcpu',375.92,91.44)
    for pin in ['[B2,B3,C1,C2,C3,C4]','B4']:
        p=u[pin];s.wire(p,(170.18,p[1]))
    s.wire((170.18,104.14),(170.18,106.68));s.wire((170.18,106.68),(170.18,121.92))
    s.junction((170.18,106.68));s.power('GND',(170.18,121.92))
    s.wire(u['A4'],(177.8,93.98));s.wire((177.8,93.98),(177.8,137.16))
    for ref,value,x in [('R301','100R 1%',210.82),('C305','1uF',233.68)]:
        p=passive(ref,value,x,119.38)
        s.wire((x,91.44),p['1']);s.junction((x,91.44))
        s.wire(p['2'],(x,137.16))
    s.wire((177.8,137.16),(210.82,137.16));s.wire((210.82,137.16),(233.68,137.16))
    s.junction((210.82,137.16));s.label('VDD_CPU_COM',(233.68,137.16),global_net=True)
    # Local output bank: 88uF nominal, separate from the processor-side bypass.
    xs=[256.54,287.02,317.5,347.98]
    for i,x in enumerate(xs):
        p=passive(f'C{306+i}','22uF',x,109.22)
        s.wire((x,91.44),p['1']);s.junction((x,91.44));s.wire(p['2'],(x,116.84))
        if i:s.wire((xs[i-1],116.84),(x,116.84))
        if 0<i<3:s.junction((x,116.84))
    s.power('GND',(xs[-1],116.84))
    s.text('R301 and C305 connect OUT to remote sense. Route M15 sense away from LX.\nPlace C305 at the output bank; connect its lower end to the sense trace.\nOutput bank is 88uF nominal; processor bypass adds 70.8uF nominal.',187.96,142.24,1.0)
    s.text('51k / 100nF enables CPU after VCC3V3_PMU rises.\nVSEL is low at reset; PMIC_SLEEP_H selects register 1 in suspend.\nI2C pull-ups belong on the PMIC/PMUIO2 sheet.\nDo not share VCC5V_SYS with an external USB host VBUS.',15.24,165.1,1.27)
    s.text('RK860 Rev 1.7 and Rockchip tablet reference, p24.\nSPM5030T-R35M: 0.35uH, 4.29mR maximum DCR, 14.9A typical Isat.\nVerify combined-bias capacitance, transient response and thermal limits on prototypes.\nUpstream rails, PMIC and processor I2C/control units remain in progress.',187.96,165.1,1.27)
    return s
