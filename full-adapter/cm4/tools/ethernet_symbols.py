"""Manufacturer pin maps for the native-PHY Ethernet front end."""
from collections import OrderedDict


def build(make_symbol):
    units = OrderedDict()
    for channel in range(4):
        a, b = 3 * channel, 24 - 3 * channel
        pins = [(a+2, 'TD+', 'L'), (a+3, 'TD-', 'L'), (a+1, 'TCT', 'L'),
                (b-1, 'MX+', 'R'), (b-2, 'MX-', 'R'), (b, 'MCT', 'R')]
        units[f'Pair {"ABCD"[channel]} / 1:1 / CMC'] = [
            {'ball':str(n), 'name':name, 'display_name':name,
             'side':side, 'type':'passive'} for n, name, side in pins]
    transformer, manifest = make_symbol('HX6096NL', 'cm4:Pulse_HX6096NL',
        'https://productfinder.pulseeng.com/doc_type/WEB301/doc_num/HX6096NL/doc_part/HX6096NL.pdf',
        'Pulse Electronics', 'C5339289',
        'Four 1:1 gigabit transformers with chip-side CMC; 720mA at 57V; 1500Vrms isolation',
        units, keywords='gigabit Ethernet PoE transformer', footprint_filter='Pulse_HX6096NL')
    transformer = transformer.replace('(property "Reference" "U"', '(property "Reference" "T"')
    pins = [dict(ball=str(n), name=f'Contact {n}', side='L', type='passive') for n in range(1, 9)]
    pins.append(dict(ball='SH', name='Shield', side='B', type='passive'))
    jack, jack_manifest = make_symbol('855437002', 'cm4:Molex_855437002',
        'https://www.molex.com/content/dam/molex/molex-dot-com/products/automated/en-us/salesdrawingpdf/855/85543/855437002_sd.pdf',
        'Molex', 'C3179022', 'Cat5e shielded SMT RJ45, 1.5A contacts, 125VDC',
        {'Cat5e / cable interface':pins}, keywords='RJ45 Cat5e',
        footprint_filter='Molex_855437002', side_pins_from_top=True)
    jack = jack.replace('(property "Reference" "U"', '(property "Reference" "J"')
    return [transformer, jack], {'HX6096NL':manifest, '855437002':jack_manifest}
