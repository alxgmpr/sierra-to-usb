"""Processor core decoupling and every physical ground ball."""
import json
from schematic import ROOT, Sheet


def core_power():
    manifest = json.loads((ROOT / 'research/core-symbols.json').read_text())['RK3568B2']
    ddr = json.loads((ROOT / 'research/ddr-passives-search.json').read_text())['searches']
    extra = json.loads((ROOT / 'research/core-power-capacitors.json').read_text())
    search = json.loads((ROOT / 'research/cpu-passives-search-2.json').read_text())
    parts = {'100nF': ddr[6]['results'][0], '4.7uF': ddr[7]['results'][0],
             '1uF': extra['one_uF']['results'][0], '10uF': extra['ten_uF']['results'][0],
             '22uF': next(p for p in search[3]['result']['results'] if p['model'] == 'CL21A226MAYNNNE')}
    s = Sheet('core-power', 'Processor core supplies and all ground balls')
    s.box('Core rails — remote sense is a separate net', 10.16, 15.24, 396.24, 132.08)
    s.place('full-adapter:RK3568B2', 'U1', 73.66, 88.9, unit=17)
    for rail in ('VDD_CPU', 'VDD_LOGIC', 'VDD_GPU', 'VDD_NPU'):
        pins = [p for p in manifest[16]['pins'] if p['name'].startswith(rail+'_') and p['name'] != 'VDD_CPU_COM']
        positions = sorted([s.pins['U1', p['ball']] for p in pins], key=lambda p:p[1])
        bus = [(45.72, p[1]) for p in positions]
        for pin, end in zip(positions, bus): s.wire(pin, end)
        for a,b in zip(bus,bus[1:]): s.wire(a,b)
        for p in bus[1:-1]: s.junction(p)
        s.power(rail, bus[0])
    s.connect('U1', 'M15', 'VDD_CPU_COM', length=20.32, global_net=True)
    rows = [
        ('VDD_CPU', ['100nF','4.7uF','22uF','22uF','22uF'], 'Under U1: first 3; last 2 close to U1.'),
        ('VDD_LOGIC', ['100nF','4.7uF','1uF','1uF','22uF','22uF','10uF'], 'Under U1: first 5; last 2 close to U1.'),
        ('VDD_GPU', ['100nF','4.7uF','22uF','22uF','10uF'], 'Under U1: first 3; last 2 close to U1.'),
        ('VDD_NPU', ['100nF','22uF','22uF','10uF'], 'Under U1: first 2; last 2 close to U1.'),
    ]
    cnum = 200
    for index, (rail, values, note) in enumerate(rows):
        y = 48.26 + index*27.94
        xs = [132.08 + i*30.48 for i in range(len(values))]
        top, bottom = round(y-7.62,6), round(y+7.62,6)
        s.power(rail, (114.3, top))
        s.wire((114.3,top), (xs[0],top))
        for i, (x,value) in enumerate(zip(xs,values)):
            part = parts[value]
            package = {'0402':'0402_1005','0603':'0603_1608','0805':'0805_2012'}[part['package']]
            ref = 'C'+str(cnum); cnum += 1
            pins = s.place('Device:C', ref, x, y, value=value,
                           fields={'Footprint':f'Capacitor_SMD:C_{package}Metric',
                                   'Manufacturer':part['manufacturer'], 'MPN':part['model'], 'LCSC':part['lcsc']})
            s.wire(pins['1'], (x,top)); s.wire(pins['2'], (x,bottom))
            if i:
                s.wire((xs[i-1],top),(x,top)); s.wire((xs[i-1],bottom),(x,bottom))
            if i < len(xs)-1: s.junction((x,top))
            if 0 < i < len(xs)-1: s.junction((x,bottom))
        s.power('GND', (xs[-1],bottom))
        s.text(note, 200.66, y+13.97, 1.0)
    ground_units = [unit for unit in manifest if unit['title'].startswith('Ground balls')]
    for index, unit in enumerate(ground_units):
        x = 60.96 + (index%4)*99.06
        y = 172.72 + (index//4)*50.8
        s.place('full-adapter:RK3568B2','U1',x,y,unit=unit['unit'])
        ps = sorted([s.pins['U1',p['ball']] for p in unit['pins']])
        by = round(max(p[1] for p in ps)+5.08,6)
        for pin in ps:s.wire(pin,(pin[0],by))
        for a,b in zip(ps,ps[1:]):s.wire((a[0],by),(b[0],by))
        for pin in ps[1:-1]:s.junction((pin[0],by))
        s.power('GND',(ps[-1][0],by))
    s.text('Rockchip tablet reference, p11: keep distributed bypass placement. CPU regulator and PMIC capture remain in progress.\n208 VSS/AVSS balls connect to secondary GND; do not confuse TVSS (temperature reference input) with a ground ball.',15.24,281.94,1.0)
    return s
