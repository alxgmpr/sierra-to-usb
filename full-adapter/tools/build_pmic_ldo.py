"""RK809-5 LDO groups, with the manufacturer's local input/output bypass."""
import json
from schematic import ROOT, Sheet


def pmic_ldo():
    s = Sheet('pmic-ldo', 'PMIC LDO supplies and startup defaults')
    part = json.loads((ROOT/'research/core-power-capacitors.json').read_text())['one_uF']['results'][0]

    def cap(ref, x, y):
        return s.place('Device:C', ref, x, y, value='1uF', fields={
            'Footprint':'Capacitor_SMD:C_0402_1005Metric', 'Manufacturer':part['manufacturer'],
            'MPN':part['model'], 'LCSC':part['lcsc']})

    groups = [
        (6, '22', [('23','VDD0V9_IMAGE','LDO1: OFF at startup; reserved'),
                   ('21','VDD0V9_ANLG','LDO2: 0.9V, slot 1, 400mA max'),
                   ('20','VDD0V9_PMU','LDO3: 0.9V, slot 1, 100mA max')]),
        (7, '30', [('28','VCC3V3_CODEC','LDO4: OFF at startup; reserved'),
                   ('29','VCC_SDIO','LDO5: 3.3V, slot 4, 200mA max'),
                   ('31','VCC3V3_PMU','LDO6: 3.3V, slot 2, 200mA max')]),
        (8, '4', [('3','VCC1V8_ANLG','LDO7: 1.8V, slot 2, 400mA max'),
                  ('5','VCC1V8_PMU','LDO8: 1.8V, slot 2, 400mA max'),
                  ('6','VCC1V8_IMAGE','LDO9: OFF at startup; reserved')]),
    ]
    for row, (unit, supply_pin, outputs) in enumerate(groups):
        y = 45.72 + row*76.2
        s.box(f'RK809-5 — LDO group {row+1}', 10.16, y-30.48, 396.24, 73.66)
        pins = s.place('full-adapter:RK809-5','U5',109.22,y,unit=unit)
        p = pins[supply_pin]
        s.wire(p,(40.64,p[1]));s.wire((40.64,p[1]),(40.64,y-10.16))
        s.power('VCC3V3_SYS',(40.64,y-10.16))
        c = cap(f'C{400+row*4}',40.64,y+15.24)
        s.wire((40.64,p[1]),c['1']);s.junction((40.64,p[1]))
        s.wire(c['2'],(40.64,y+22.86));s.power('GND',(40.64,y+22.86))
        # The longest upper wire reaches the farthest capacitor. Lower wires
        # terminate earlier, so the three fan-outs never cross.
        for i,(pin,rail,note) in enumerate(outputs):
            x = 335.28-i*71.12
            p=pins[pin]
            s.wire(p,(x,p[1]));s.wire((x,p[1]),(x,y+10.16))
            s.power(rail,(x,y+10.16))
            c=cap(f'C{401+row*4+i}',x,y+22.86)
            s.wire((x,y+10.16),c['1']);s.wire(c['2'],(x,y+30.48))
            s.power('GND',(x,y+30.48))
            s.text(note,x-25.4,y+38.1,1.0)
    s.text('AN_RK809 V1.1 section 6.5: 1uF at every LDO input group and output.\nUse the exact -5 startup sequence. Reserved outputs remain disabled in firmware.',15.24,264.16,1.0)
    s.text('3.3V outputs have less than 0.4V headroom: LDO5/6 are limited to 200mA (datasheet p22-23).\nInclude dropout in rail limits. LDO6 enables the CPU buck; VCC_RTC shares the highest input rail.',15.24,276.86,1.0)
    return s
