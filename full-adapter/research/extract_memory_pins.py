"""Exact H5TQ4G63EFR-RDC ball map, checked against manufacturer table and KiCad lands."""
from pathlib import Path
import hashlib
import json
import pymupdf
import sexpdata as sx

ROOT = Path(__file__).resolve().parents[1]
# Manufacturer Rev 1.2, September 2016, PDF page 6, top view. Bars were
# visually reviewed because PDF table extraction loses active-low notation.
ROWS = {
    'A': 'VDDQ DQU5 DQU7 DQU4 VDDQ VSS',
    'B': 'VSSQ VDD VSS DQSU_N DQU6 VSSQ',
    'C': 'VDDQ DQU3 DQU1 DQSU_P DQU2 VDDQ',
    'D': 'VSSQ VDDQ DMU DQU0 VSSQ VDD',
    'E': 'VSS VSSQ DQL0 DML VSSQ VDDQ',
    'F': 'VDDQ DQL2 DQSL_P DQL1 DQL3 VSSQ',
    'G': 'VSSQ DQL6 DQSL_N VDD VSS VSSQ',
    'H': 'VREFDQ VDDQ DQL4 DQL7 DQL5 VDDQ',
    'J': 'NC VSS RAS_N CK_P VSS NC',
    'K': 'ODT VDD CAS_N CK_N VDD CKE',
    'L': 'NC CS_N WE_N A10/AP ZQ NC',
    'M': 'VSS BA0 BA2 NC VREFCA VSS',
    'N': 'VDD A3 A0 A12/BC_N BA1 VDD',
    'P': 'VSS A5 A2 A1 A4 VSS',
    'R': 'VDD A7 A9 A11 A6 VDD',
    'T': 'VSS RESET_N A13 A14 A8 VSS',
}
COLUMNS = [1, 2, 3, 7, 8, 9]
FP_NAME = 'FBGA-96_7.5x13mm_Layout9x16_P0.8mm'
SOURCE_FP = Path('/Applications/KiCad/KiCad.app/Contents/SharedSupport/footprints/Package_BGA.pretty') / (FP_NAME + '.kicad_mod')


def main():
    pdf_path = ROOT / 'reference/h5tq4g63efr.pdf'
    pdf = pymupdf.open(pdf_path)
    tables = [t.extract() for t in pdf[5].find_tables().tables]
    # Verify each table cell against the PDF text. Polarity is independently
    # taken from the overbars in the rendered manufacturer drawing.
    candidates = [t for t in tables if len(t) == 16 and len(t[0]) == 3]
    assert len(candidates) == 2, [(len(t), len(t[0])) for t in tables]
    pins = []
    for row_index, (letter, cells) in enumerate(ROWS.items()):
        names = cells.split()
        extracted = candidates[0][row_index] + candidates[1][row_index]
        for col, name, pdf_name in zip(COLUMNS, names, extracted):
            plain = name.replace('_N', '').replace('_P', '')
            assert plain == pdf_name.strip(), (letter, col, name, pdf_name)
            function = name
            if name.startswith('DQL') and name[-1].isdigit():
                function = 'DQ' + name[3:]
            elif name.startswith('DQU') and name[-1].isdigit():
                function = 'DQ' + str(8 + int(name[3:]))
            typ = ('power_in' if name in {'VDD', 'VDDQ', 'VSS', 'VSSQ'} else
                   'no_connect' if name == 'NC' else
                   'bidirectional' if name.startswith(('DQL', 'DQU', 'DQS')) else
                   'passive' if name == 'ZQ' else 'input')
            pins.append({'ball': f'{letter}{col}', 'name': name,
                         'function': function, 'electrical_type': typ,
                         'xy_mm': [round((col - 5) * .8, 6), round((row_index - 7.5) * .8, 6)]})
    def child(n, t): return next(x for x in n if isinstance(x, list) and str(x[0]) == t)
    footprint = sx.loads(SOURCE_FP.read_text())
    pads = {p[1]: p for p in footprint if isinstance(p, list) and str(p[0]) == 'pad'}
    assert len(pads) == len(pins) == 96
    for pin in pins:
        assert child(pads[pin['ball']], 'at')[1:3] == pin['xy_mm']
        assert child(pads[pin['ball']], 'size')[1:3] == [.36, .36]
    target = ROOT / 'lib/full-adapter.pretty' / SOURCE_FP.name
    target.write_bytes(SOURCE_FP.read_bytes())
    output = {'mpn': 'H5TQ4G63EFR-RDC', 'lcsc': 'C2803259',
              'manufacturer': 'SK hynix', 'capacity_bits': 4294967296,
              'organization': '256M x 16, eight banks', 'speed_grade': 'DDR3-1866 13-13-13',
              'voltage_v': 1.5, 'voltage_tolerance_v': .075,
              'land_diameter_mm': .36,
              'land_basis': 'Vendored KiCad footprint; engineering land choice, not Hynix land recommendation',
              'package_mm': [7.5, 13.0], 'package_height_mm': 1.1,
              'footprint': 'full-adapter:' + FP_NAME,
              'sources': {pdf_path.name: hashlib.sha256(pdf_path.read_bytes()).hexdigest(),
                          SOURCE_FP.name: hashlib.sha256(SOURCE_FP.read_bytes()).hexdigest()},
              'checks': ['96 table cells cross-checked to PDF page 6',
                         'Overbars visually reviewed on rendered manufacturer page 6',
                         'All ball names and coordinates match vendored footprint',
                         'Package dimensions visually checked against PDF page 33'],
              'pins': pins}
    (ROOT / 'research/memory-pins.json').write_text(json.dumps(output, indent=2) + '\n')
    print('96 memory balls and 96 footprint pads agree; polarity reviewed against manufacturer drawing.')


if __name__ == '__main__':
    main()
