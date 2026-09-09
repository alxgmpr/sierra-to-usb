"""RK3568 always-on domains and PLL bypass, following the tablet reference p13."""
import json
from schematic import ROOT, Sheet


def processor_pmu():
    s = Sheet('processor-pmu', 'Processor PMU and PLL supplies')
    ddr = json.loads((ROOT/'research/ddr-passives-search.json').read_text())['searches']
    extra = json.loads((ROOT/'research/core-power-capacitors.json').read_text())
    parts = {'100nF': ddr[6]['results'][0], '1uF': extra['one_uF']['results'][0]}
    s.box('PMU / PLL supplies', 10.16, 15.24, 396.24, 236.22)
    pins = s.place('full-adapter:RK3568B2', 'U1', 60.96, 129.54, unit=14)
    rows = [
        ('V21', 'VDD0V9_PMU', ['1uF', '100nF'], 'PMUPLL: 10mA peak'),
        ('Y21', 'VCC1V8_PMU', ['1uF', '100nF'], 'PMUPLL: 9mA peak; also PMUIO0'),
        ('P11', 'VDD0V9_ANLG', ['1uF', '100nF'], 'SYSPLL: 30mA peak'),
        ('N10', 'VCC1V8_ANLG', ['1uF', '100nF'], 'SYSPLL: 18mA peak'),
        ('V19', 'VDD0V9_PMU', ['1uF', '100nF'], 'PMU logic: 50mA peak'),
        ('Y20', 'VCC3V3_PMU', ['100nF'], 'PMUIO1: fixed 3.3V'),
        ('W19', 'VCC1V8_PMU', ['100nF'], 'PMUIO2: selected 1.8V; I2C0 / PMIC'),
    ]
    cnum = 500
    for ball, rail, values, note in rows:
        p = pins[ball]
        y = p[1]
        s.wire(p, (154.94, y)); s.power(rail, (154.94, y))
        previous = (154.94, y)
        xs = [208.28, 251.46][:len(values)]
        for x, value in zip(xs, values):
            part = parts[value]
            ref = f'C{cnum}'; cnum += 1
            c = s.place('Device:C', ref, x, y+7.62, value=value, fields={
                'Footprint': 'Capacitor_SMD:C_0402_1005Metric',
                'MPN': part['model'], 'Manufacturer': part['manufacturer'], 'LCSC': part['lcsc']})
            s.wire(previous, (x, y)); s.wire((x, y), c['1'])
            s.wire(c['2'], (x, y+15.24))
            if x != xs[0]:
                s.wire((xs[0], y+15.24), (x, y+15.24))
            if x != xs[-1]: s.junction((x, y))
            previous = (x, y)
        s.power('GND', (xs[-1], y+15.24))
        s.text(note, 287.02, y+5.08, 1.1)
    s.text('Source: Rockchip tablet reference p13; HW Guide V1.2 sections 2.2.2.2 / 2.2.2.3.\nLDO3 supplies 60mA combined documented PMUPLL + PMU-logic peaks (100mA rating).\nKeep PMU rails powered in standby. PLL ripple: <20mV at 0.9V; <50mV at 1.8V.',15.24,269.24,1.1)
    return s
