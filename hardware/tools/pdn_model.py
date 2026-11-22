"""Board-level PDN impedance model for the appliance decoupling review.

Run:  uv run --with numpy python hardware/tools/pdn_model.py NETLIST.xml

Each MLCC/polymer = series ESR + L + C(V_rail).  Banks are built from the real
netlist (caps between a rail and GND).  Samsung parts with archived
characteristic JSON (hardware/reference/cl*-characteristics.json) use measured
DC-bias, SRF-derived ESL and ESR-at-SRF; everything else uses the ASSUMED table
below.  ESR is frequency-independent (low ESR -> worst-case anti-resonance Q).
No VRM loop, plane capacitance or spreading-inductance network: valid roughly
from the regulator crossover (~100 kHz) to f_ceil = Z_target / (2*pi*L_PKG),
above which BGA ball/via/package inductance alone exceeds the target.
"""
import json, math, pathlib, re, sys
import xml.etree.ElementTree as ET
import numpy as np

HERE = pathlib.Path(__file__).parent
REF = HERE.parent / 'reference'
NETLIST = pathlib.Path(sys.argv[1])   # kicad-cli sch export netlist --format kicadxml
F = np.logspace(5, 9, 4001)
W = 2 * np.pi * F
L_VIA = {'0201': 0.10e-9, '0402': 0.10e-9, '0603': 0.25e-9, '0805': 0.25e-9,
         '1206': 0.25e-9, '1210': 0.25e-9, 'poly': 0.5e-9}   # mounting, added to part L
ESR_SCALE = 1.0  # sensitivity knob

# mpn: (C_nom, V_rated, pkg, L_part, ESR, {V: retained fraction}) -- ASSUMED unless Samsung JSON exists
PARTS = {
    'CL05B104KB54PNC': (100e-9, 50, '0402', 0.35e-9, 0.030, {0: 1, 3.3: 0.98}),
    'CL05B105KQ5NNNC': (1e-6, 6.3, '0402', 0.35e-9, 0.012, {0: 1, 0.6: .95, 1.1: .90, 1.8: .80, 3.3: .60}),
    'CL05A475MP5NRNC': (4.7e-6, 10, '0402', 0.35e-9, 0.006, {0: 1, 0.6: .90, 1.1: .80, 1.8: .65, 3.3: .40}),
    'CL05B103KB5NNNC': (10e-9, 50, '0402', 0.35e-9, 0.080, {0: 1, 3.3: 1}),   # only for the decade test
    'CL10A475KA8NQNC': (4.7e-6, 25, '0603', 0.45e-9, 0.006, {0: 1, 0.6: .97, 1.1: .93, 1.8: .85, 3.3: .65}),
    'CL31B106KBHNNNE': (10e-6, 50, '1206', 1.03e-9, 0.005, {0: 1, 3.3: .90, 5: .80, 12: .50}),
    '6SVPC220MV': (220e-6, 6.3, 'poly', 2.0e-9, 0.015, {0: 1}),
}
SAMSUNG = {'CL10B104KA8NNNC': 25, 'CL10B105KA8NNNC': 25, 'CL31B106KAHNNNE': 25, 'CL32B226KAJNNNE': 25,
           'CL31B475KBHNNNE': 50, 'CL31B225KBHNNNE': 50}

RAILS = {  # name: (V, dI step A, allowed dV fraction, load-side pkg/pin loop L) -- ASSUMED, see report
    'VDD_CPU': (1.0, 3.0, .05, 50e-12), 'VDD_LOGIC': (0.9, 1.25, .05, 50e-12),
    'VDD_GPU': (0.9, 1.25, .05, 50e-12), 'VDD_NPU': (0.9, 1.0, .05, 50e-12),
    'VDD_DDR_1V1': (1.1, 0.5, .03, 100e-12), 'VDD_DDR_0V6': (0.6, 0.3, .03, 100e-12),
    'VCC_1V8': (1.8, 0.3, .05, 300e-12), 'VCCA_1V8': (1.8, 0.1, .03, 300e-12),
    'VDDA_0V9': (0.9, 0.1, .03, 300e-12), '3V3_MAIN': (3.3, 1.0, .05, 500e-12),
    'ETH_0V95': (0.95, 0.4, .03, 300e-12), 'ETH_3V3': (3.3, 0.3, .05, 500e-12),
    'MODEM_VCC': (3.7, 2.0, .027, 200e-12), '5V_MAIN': (5.0, 3.0, .03, 500e-12),
}


def samsung(mpn, vr):
    d = json.load(open(REF / f'{mpn[:-1].lower()}-characteristics.json'))
    g = {x['graphType']: x for x in d}
    zr = {c['graphSubType']: c['data'] for c in g['|Z|_R']['selectPartsList'][0]['chartList']}
    f = np.array([float(p['x']) for p in zr['|Z|']]) * 1e6
    z = np.array([float(p['y']) for p in zr['|Z|']])
    c0 = 1 / (2 * np.pi * f[0] * z[0]); i = z.argmin()
    bias = g['DCBias']['selectPartsList'][0]['chartList'][0]['data']
    bias = {float(p['x']): min(1.0, 1 + float(p['y']) / 100) for p in bias}   # no credit for +bias
    nom = float(re.match(r'CL\d\d[A-C](\d\d)(\d)', mpn).group(1)) * 10 ** int(mpn[7]) * 1e-12
    pkg = {'05': '0402', '10': '0603', '31': '1206', '32': '1210'}[mpn[2:4]]
    return nom, vr, pkg, 1 / ((2 * np.pi * f[i]) ** 2 * c0), z[i], bias


for m, vr in SAMSUNG.items():
    PARTS[m] = samsung(m, vr)


def fallback(value, fp):
    """Generic MLCC for MPNs not in PARTS (RF C0G etc.)."""
    mult = {'p': 1e-12, 'n': 1e-9, 'u': 1e-6}
    m = re.match(r'([\d.]+)\s*([pnu])', value)
    c = float(m.group(1)) * mult[m.group(2)]
    pkg = (re.search(r'C_(\d{4})', fp) or [None, 'poly'])[1]
    return c, 50, pkg, {'0402': .35e-9, '0603': .45e-9, '0805': .6e-9}.get(pkg, 1e-9), \
        0.03 * (100e-9 / c) ** 0.3, {0: 1}


def ceff(p, v):
    xs = sorted(p[5]); ys = [p[5][x] for x in xs]
    return p[0] * float(np.interp(v, xs, ys))


def zcap(p, v, n=1):
    c, _, pkg, lp, esr, _ = p
    return (esr * ESR_SCALE + 1j * W * (lp + L_VIA[pkg]) + 1 / (1j * W * ceff(p, v))) / n


def zbank(bank, v):
    return 1 / sum(1 / zcap(PARTS[m], v, n) for m, n in bank.items())


def load_banks():
    root = ET.parse(NETLIST).getroot()
    comps = {}
    for c in root.iter('comp'):
        if re.match(r'C\d', c.get('ref')):
            f = {x.get('name'): x.text or '' for x in c.iter('field')}
            comps[c.get('ref')] = (f.get('MPN', ''), c.findtext('value'), c.findtext('footprint') or '')
    nets = {}
    for n in root.iter('net'):
        for nd in n.iter('node'):
            nets.setdefault(nd.get('ref'), []).append(n.get('name'))
    banks = {}
    for ref, (mpn, val, fp) in comps.items():
        a, b = nets[ref]
        rail = a if b == 'GND' else b if a == 'GND' else None
        if rail in RAILS:
            if mpn not in PARTS:
                PARTS[mpn] = fallback(val, fp)
            banks.setdefault(rail, {}).setdefault(mpn, 0)
            banks[rail][mpn] += 1
    return len(comps), banks


def remap(rail, bank, scen):
    mapping, add = scen
    out = {}
    for m, n in bank.items():
        for tm, tn in (mapping(m, n) if callable(mapping) else [(mapping.get(m, m), n)]):
            out[tm] = out.get(tm, 0) + tn
    for m, n in add.get(rail, {}).items():
        out[m] = out.get(m, 0) + n
    return out


def decade(m, n):   # same 0402 slot count, split 10n/100n/1u
    if PARTS[m][2] != '0402':
        return [(m, n)]
    return [(x, k) for x, k in zip(('CL05B103KB5NNNC', 'CL05B104KB54PNC', 'CL05B105KQ5NNNC'),
                                   (n // 3 + (n % 3 > 0), n // 3 + (n % 3 > 1), n // 3)) if k]


S04 = ('CL05B104KB54PNC', 'CL05A475MP5NRNC', 'CL05B105KQ5NNNC')
TO1U = {m: 'CL05B105KQ5NNNC' for m in S04}
SCEN = {
    'current': ({}, {}),
    'all0402->1u': (TO1U, {}),
    'all0402->4u7': ({m: 'CL05A475MP5NRNC' for m in S04}, {}),
    'all0402->100n': ({m: 'CL05B104KB54PNC' for m in S04}, {}),
    'decade0402': (decade, {}),
    '0603 100n->1u': ({'CL10B104KA8NNNC': 'CL10B105KA8NNNC'}, {}),
    'merge 10u KAH->KBH': ({'CL31B106KAHNNNE': 'CL31B106KBHNNNE'}, {}),
    'PROPOSED': (dict(TO1U, CL31B106KAHNNNE='CL31B106KBHNNNE'), {}),
    'PROPOSED+fixes': (dict(TO1U, CL31B106KAHNNNE='CL31B106KBHNNNE'),
                       {'VDD_CPU': {'CL05B105KQ5NNNC': 8}, 'VDD_GPU': {'CL05B105KQ5NNNC': 3},
                        'VDD_NPU': {'CL05B105KQ5NNNC': 3}, 'VDD_LOGIC': {'CL05B105KQ5NNNC': 2},
                        'MODEM_VCC': {'CL10B105KA8NNNC': 4}, 'ETH_0V95': {'CL10B105KA8NNNC': 2}}),
}
BANDS = ((1e5, 1e6), (1e6, 1e7), (1e7, 1e8))


def peaks(z, lo, hi):
    """Anti-resonance peaks in [lo,hi]: local max whose height over the lower neighbouring valley > 1.2x."""
    s = (F >= lo) & (F <= hi); zz, ff = z[s], F[s]
    idx = [i for i in range(1, len(zz) - 1) if zz[i] >= zz[i - 1] and zz[i] > zz[i + 1]]
    out = []
    for i in idx:
        left, right = zz[:i].min(), zz[i:].min()
        if zz[i] > 1.2 * max(left, right):
            out.append((ff[i], zz[i]))
    return out


def selfcheck():
    p = PARTS['CL10B104KA8NNNC']
    z = np.abs(zcap(p, 0))
    srf = 1 / (2 * np.pi * math.sqrt((p[3] + L_VIA[p[2]]) * ceff(p, 0)))
    assert abs(F[z.argmin()] / srf - 1) < 0.01, 'min |Z| not at SRF'
    assert abs(z.min() / p[4] - 1) < 0.01, '|Z|min != ESR'
    assert np.allclose(np.abs(zbank({'CL10B104KA8NNNC': 4}, 0)), z / 4), 'N identical != Z/N'
    assert abs(PARTS['CL32B226KAJNNNE'][0] - 22e-6) < 1e-9 and abs(PARTS['CL10B104KA8NNNC'][0] - 100e-9) < 1e-12
    assert 0.9e-9 < PARTS['CL32B226KAJNNNE'][3] < 1.3e-9, 'Samsung 1210 SRF-derived ESL out of range'
    # two different caps in parallel must produce an anti-resonance between their SRFs
    zz = np.abs(zbank({'CL32B226KAJNNNE': 1, 'CL05B104KB54PNC': 1}, 0))
    pk = peaks(zz, 1e5, 1e9)
    assert len(pk) == 1 and 1e6 < pk[0][0] < 2.5e7, pk


def report(rail, bank, names=SCEN):
    v, di, tol, lpkg = RAILS[rail]
    zt = v * tol / di
    fceil = zt / (2 * np.pi * lpkg)
    hi = min(fceil, 1e8)
    print(f'== {rail}  V={v}  Zt={zt*1e3:.0f} mOhm  ceiling Zt/(2pi*{lpkg*1e12:.0f}pH)={fceil/1e6:.0f} MHz')
    print('   bank: ' + ', '.join(f'{n}x {m}' for m, n in bank.items()))
    print(f'   {"scenario":20s} max|Z| mOhm in 0.1-1 / 1-10 / 10-{hi/1e6:.0f} MHz   peaks (MHz:mOhm)')
    res = {}
    for name in names:
        b = remap(rail, bank, SCEN[name])
        if name not in ('current', 'PROPOSED') and b == bank:
            continue
        z = np.abs(zbank(b, v))
        mx = [z[(F >= lo) & (F <= min(h, hi))].max() for lo, h in BANDS]
        res[name] = max(mx)
        pk = peaks(z, 1e5, hi)
        print(f'   {name:20s} ' + ' / '.join(f'{m*1e3:6.1f}{"*" if m > zt else " "}' for m in mx) + '   ' +
              (', '.join(f'{f/1e6:.1f}:{zz*1e3:.0f}' for f, zz in pk) or '-'))
    print()
    return res


def main():
    global ESR_SCALE
    selfcheck()
    ncaps, banks = load_banks()
    assert ncaps > 0, ncaps
    print(f'netlist caps: {ncaps}; self-check OK   (* = above Z_target)\n')
    print('part library (C_nom, Vr, pkg, L_total nH, ESR mOhm):')
    for m, p in sorted(PARTS.items()):
        print(f'  {m:20s} {p[0]*1e6:9.4g}uF {p[1]:5g}V {p[2]:5s} {(p[3]+L_VIA[p[2]])*1e9:5.2f} {p[4]*1e3:6.1f}')
    print()
    for rail, bank in sorted(banks.items()):
        report(rail, bank)
    print('### sensitivity: 0402 mounting L x3 (0.3 nH) and all ESR x0.5')
    L_VIA['0402'] *= 3; ESR_SCALE = 0.5
    for rail in ('VDD_DDR_1V1', 'VDD_DDR_0V6', 'VDD_LOGIC'):
        report(rail, banks[rail], ('current', 'all0402->1u', 'all0402->100n', 'decade0402'))


if __name__ == '__main__':
    main()
