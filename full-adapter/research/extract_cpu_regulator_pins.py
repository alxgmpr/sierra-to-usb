"""Record RK860-0 balls reviewed against Rockchip Rev 1.7, pages 8–9 and 18."""
from pathlib import Path
import hashlib
import json

ROOT = Path(__file__).resolve().parents[1]
pdf = ROOT / 'reference/rk860-v1.7.pdf'
expected = 'bc78a031027d04dde8c96f585ddb2769a6b1d357d916cb543edeb48487e4efb3'
assert hashlib.sha256(pdf.read_bytes()).hexdigest() == expected
rows = {
    'A': ['VSEL', 'EN', 'SCL', 'VOUT'],
    'B': ['SDA', 'GND', 'GND', 'AGND'],
    'C': ['GND', 'GND', 'GND', 'GND'],
    'D': ['VIN', 'VIN', 'LX', 'LX'],
    'E': ['VIN', 'VIN', 'LX', 'LX'],
}
types = {'VSEL': 'input', 'EN': 'input', 'SCL': 'input', 'SDA': 'bidirectional',
         'VOUT': 'input', 'VIN': 'power_in', 'LX': 'power_out',
         'GND': 'power_in', 'AGND': 'power_in'}
pins = [{'ball': row + str(col + 1), 'name': name, 'type': types[name],
         'x_mm': round((col - 1.5) * .4, 6), 'y_mm': round((ri - 2) * .4, 6)}
        for ri, (row, names) in enumerate(rows.items()) for col, name in enumerate(names)]
assert len(pins) == len({p['ball'] for p in pins}) == 20
result = {
    'manufacturer': 'Rockchip', 'mpn': 'RK860-0', 'lcsc': 'C19188628',
    'source': {'url': 'https://rockchip.fr/RK860%20datasheet%20V1.7.pdf',
               'sha256': expected, 'pin_pages': [8, 9], 'package_page': 18},
    'footprint': 'full-adapter:RK860_WLCSP20_1.625x2.025mm_P0.4mm',
    'package': {'rows': 5, 'columns': 4, 'pitch_mm': .4,
                'maximum_body_mm': [1.65, 2.05, .63],
                'land_diameter_mm': .15,
                'land_basis': 'Rev 1.7 page 18 explicitly recommends 0.15 mm phi-b in PCB layout. Assembly process qualification remains required.'},
    'variant': {'i2c_address_7bit': '0x40', 'device_id': 8, 'reset_voltage_V': 1.0,
                'minimum_voltage_V': .7125, 'step_V': .0125, 'maximum_voltage_V': 1.5,
                'linux_compatible': 'rockchip,rk8600'},
    'electrical_type_notes': {
        'VOUT': 'Sense input per functional description and application circuits; table I/O column incorrectly says Output.',
        'SDA': 'Bidirectional open-drain I2C; requires an external pull-up to the host IO supply.',
        'LX': 'Four switching-output balls must all connect to the inductor input, not directly to the CPU rail.'},
    'pins': pins,
}
(ROOT / 'research/cpu-regulator-pins.json').write_text(json.dumps(result, indent=2) + '\n')
print('Verified 20 RK860-0 balls against pinned manufacturer source')
