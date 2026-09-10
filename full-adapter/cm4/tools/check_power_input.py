"""Independent exported-net and manufacturer-land checks for the power input.

These checks validate capture and static limits, not surge, thermal or PCB release.
"""
from itertools import product
from pathlib import Path
import sexpdata as sx


def nodes(n, tag):
    return [v for v in n if isinstance(v, list) and str(v[0]) == tag]


def one(n, tag):
    return nodes(n, tag)[0]


def close(a, b):
    assert len(a) == len(b) and all(abs(x-y) < 1e-6 for x, y in zip(a, b)), (a, b)


def threshold(upper, lower, reference, bias):
    # 0.1% initial plus 25 ppm/K over the largest 100 K excursion from 25 C.
    error = .001 + 25e-6 * 100
    vals = [v * (1 + upper*(1+u)/lower/(1+l)) + i*upper*(1+u)
            for v, u, l, i in product(reference, [-error, error], [-error, error], [-bias, bias])]
    return [min(vals), max(vals)]


def check(root, tree):
    root = Path(root)
    nets = {n.get('name'): {(p.get('ref'), p.get('pin')) for p in n}
            for n in tree.findall('.//nets/net')}
    pn = {p: n for n, ps in nets.items() for p in ps}
    def pins(ref, mapping):
        for pin, net in mapping.items():
            assert pn[ref, str(pin)] == net, (ref, pin, pn[ref, str(pin)], net)
    def exact(net, endpoints):
        assert nets[net] == set(endpoints), (net, nets[net], endpoints)
    def nc(ref, numbers):
        for pin in map(str, numbers):
            assert nets[pn[ref, pin]] == {(ref, pin)}, (ref, pin)

    # USB4105 B4, HUSB238 Rev2.5, TPD6S300 SLVSDK3C Tables and Fig25.
    pins('J150', {**dict.fromkeys(['A4','A9','B4','B9'], 'AUX_VBUS'),
                  **dict.fromkeys(['A1','A12','B1','B12','SH'], 'GND'),
                  'A5':'AUX_CC1_PORT','B5':'AUX_CC2_PORT'})
    nc('J150', ['A6','A7','A8','B6','B7','B8'])
    for i, jpin, cpin, rd, internal, husb in [(1,'A5',4,7,12,4),(2,'B5',5,6,11,5)]:
        exact(f'AUX_CC{i}_PORT', [('J150',jpin),('U151',str(cpin)),('U151',str(rd))])
        exact(f'AUX_CC{i}', [('U151',str(internal)),('U150',str(husb))])
    pins('U151', {3:'AUX_CC_VBIAS',9:'AUX_WINDOW_OK',10:'AUX_3V3',
        **dict.fromkeys([1,2,8,13,14,15,16,17,18,19,20,21], 'GND')})
    exact('AUX_CC_VBIAS', [('U151','3'),('C150','1')])
    pins('U150', {1:'AUX_VBUS',9:'AUX_PD_ISET',10:'AUX_PD_GATE_N',11:'GND'})
    nc('U150', [2,3,6,7,8])
    exact('AUX_PD_ISET', [('U150','9'),('R150','1')])

    # BAT54C is common CATHODE pin3; DMP2035U pin2 is SOURCE.
    # D150 prevents a removed/shorted source from draining the LDO input
    # directly and bypasses OUT-to-IN current around the LDO pass transistor.
    pins('D150', {1:'AUX_VBUS',2:'AUX_3V3',3:'AUX_LDO_IN'})
    exact('AUX_LDO_IN', [('D150','3'),('U152','2'),('C154','1')])
    pins('U152', {1:'GND',2:'AUX_LDO_IN',3:'AUX_3V3'})
    nc('U152', [4,5])
    pins('Q150', {1:'AUX_PERMISSION_GATE',2:'AUX_3V3',3:'AUX_GATE_DRIVE'})
    exact('AUX_PERMISSION_GATE', [('Q150','1'),('R151','1'),('R152','2')])
    exact('AUX_PD_GATE_N', [('U150','10'),('R151','2')])
    exact('AUX_GATE_DRIVE', [('Q150','3'),('R153','1')])
    exact('AUX_WINDOW_OK', [('R153','2'),('R159','1'),('U151','9'),('U153','1'),('U153','6'),('U154','2')])
    exact('AUX_MUX_DISABLE', [('U154','4'),('R160','2'),('U160','5')])
    pins('U154', {2:'AUX_WINDOW_OK',3:'GND',4:'AUX_MUX_DISABLE',5:'AUX_3V3'})
    nc('U154', [1])
    pins('U153', {1:'AUX_WINDOW_OK',2:'GND',3:'AUX_UV_SENSE',4:'AUX_OV_SENSE',5:'AUX_3V3',6:'AUX_WINDOW_OK'})
    exact('AUX_UV_SENSE', [('R154','2'),('R155','1'),('U153','3')])
    exact('AUX_OV_UPPER', [('R156','2'),('R157','1')])
    exact('AUX_OV_SENSE', [('R157','2'),('R158','1'),('U153','4')])
    pins('U160', {1:'VIN_SYS',8:'VIN_SYS',2:'POE_12V',3:'POE_PRIORITY',4:'POE_MUX_DISABLE',
        5:'AUX_MUX_DISABLE',6:'AUX_PRIORITY',7:'AUX_VBUS',9:'GND',10:'MUX_ILIM',11:'MUX_SS',12:'GND'})
    exact('AUX_PRIORITY', [('U160','6'),('R161','2'),('R162','1')])
    exact('POE_PRIORITY', [('U160','3'),('R163','2'),('R164','1')])
    exact('MUX_ILIM', [('U160','10'),('R165','1')])
    exact('MUX_SS', [('U160','11'),('C160','1')])
    for n in [150,155,158,159,162,164,165]:
        assert pn[f'R{n}', '2'] == 'GND'
    for n in [154,156,161]:
        assert pn[f'R{n}', '1'] == 'AUX_VBUS'
    pins('R152', {1:'AUX_3V3'}); pins('R160', {1:'AUX_3V3'}); pins('R163', {1:'POE_12V'})
    for ref, rail in {'C150':'AUX_CC_VBIAS','C151':'AUX_3V3','C152':'AUX_VBUS',
        'C153':'AUX_3V3','C154':'AUX_LDO_IN','C155':'AUX_3V3','C156':'AUX_3V3',
        'C160':'MUX_SS','C161':'POE_12V','C162':'VIN_SYS','C163':'VIN_SYS'}.items():
        pins(ref, {1:rail,2:'GND'})
    # Housekeeping must remain AUX-only, never sourced from PoE, VIN_SYS or CM4.
    exact('AUX_3V3', [('D150','2'),('U152','3'),('U151','10'),('U153','5'),('U154','5'),
        ('Q150','2'),('R152','1'),('R160','1'),('C151','1'),('C153','1'),('C155','1'),('C156','1')])
    assert len({pn[p] for p in [('J150','A4'),('U160','2'),('U160','1'),('U152','3'),('J100','84')]}) == 5

    comps = {c.get('ref'): c for c in tree.findall('.//components/comp')}
    exact_parts = {'J150':'USB4105-GF-A-120','U150':'HUSB238_002DD','U151':'TPD6S300RUKR',
        'U152':'TLV70433DBVR','U153':'TPS3700DDCR','U154':'SN74LVC1G14DBVR','U160':'TPS2121RUXR',
        'D150':'BAT54CLT1G','Q150':'DMP2035U-7',
        'R150':'0402WGF2262TCE','R151':'0402WGF1001TCE','R152':'0402WGF1002TCE',
        'R153':'0402WGF4701TCE','R154':'RT0603BRD07453KL','R155':'RT0603BRD0710KL',
        'R156':'RT0603BRD07523KL','R157':'RT0603BRD076K8L','R158':'RT0603BRD0710KL',
        'R159':'0402WGF1003TCE','R160':'0402WGF1003TCE','R161':'0402WGF4992TCE',
        'R162':'0402WGF1002TCE','R163':'0402WGF4992TCE','R164':'0402WGF1002TCE','R165':'0402WGF2212TCE'}
    exact_parts.update(dict.fromkeys(['C150','C154','C155','C156','C163'], 'CC0402KRX7R9BB104'))
    exact_parts.update(dict.fromkeys(['C151','C153','C160'], 'CL10A105KO8NNNC'))
    exact_parts.update(dict.fromkeys(['C152','C161','C162'], 'CL21A225KBQNNNE'))
    for ref, mpn in exact_parts.items():
        fields = {f.get('name'): f.text for f in comps[ref].findall('fields/field')}
        assert fields['MPN'] == mpn, (ref, fields['MPN'], mpn)

    uv_rise = threshold(453e3, 10e3, [.396,.404], 25e-9)
    uv_fall = threshold(453e3, 10e3, [.387,.400], 25e-9)
    ov_rise = threshold(529.8e3, 10e3, [.396,.404], 15e-9)
    ov_fall = threshold(529.8e3, 10e3, [.387,.400], 15e-9)
    assert uv_rise[1] < 19 and uv_fall[0] > 17.7
    assert ov_rise[0] > 21 and ov_rise[1] < 22
    # Static logic uses deliberately broader bounding table rows at 3 and
    # 4.5 V, not a nominal 3.3 V threshold interpolation. Actual supply 3..3.6 V.
    # 0.1 ohm MOSFET bound is >2x the 45mohm 25C maximum at VGS=-2.5 V.
    valid_min = (3.0 - .001*.1) * (100e3*.98)/(100e3*.98+4.7e3*1.02) - 5.6e-6*4.7e3*1.02
    assert valid_min > 2.74
    assert .4 < .84  # TPD6S300 FLT VOL max, lowest 3 V falling threshold.
    assert 3.6/(4.7e3*.98) < .001  # <1 mA fault sink; TPS3700 rated at 3 mA.
    assert 3.6/(1e3*.98) < .010  # HUSB GATE peak sink <10 mA.
    gate_low_vgs = 3.0*(10e3*.98)/(10e3*.98+1e3*1.02+300) - 10e-6*1320
    assert gate_low_vgs > 2.5  # includes HUSB GATE's 300-ohm maximum pull-down.
    # Quantities for final system budget; this is not source/class sizing.
    mux_current = [4/1.02, 5/.98]

    def pads(name):
        return nodes(sx.loads((root/'lib/cm4.pretty'/(name+'.kicad_mod')).read_text()), 'pad')
    h = pads('Hynetek_DFN10_3x3_P0.5_EP1.8x2.5')
    numbered = [p for p in h if p[1]]
    assert {p[1] for p in numbered} == set(map(str, range(1,12))) and len(numbered) == 11
    for p in numbered:
        n = int(p[1])
        if n == 11:
            close(one(p,'at')[1:3], [0,0]);close(one(p,'size')[1:3], [1.8,2.5])
        else:
            close(one(p,'at')[1:3], [-1.475 if n <= 5 else 1.475, -1+((n-1) if n<=5 else 10-n)*.5])
            close(one(p,'size')[1:3], [.75,.25])
    paste = [p for p in h if not p[1]]
    assert len(paste) == 4
    coverage = sum(one(p,'size')[1]*one(p,'size')[2] for p in paste)/(1.8*2.5)
    assert .65 < coverage < .66
    pp = pads('TI_RUX0012_TPS2121')
    assert len(pp) == 12 and {p[1] for p in pp} == set(map(str,range(1,13)))
    anchors = {1:(-.675,-.35),2:(-.675,.35),7:(.675,.35),8:(.675,-.35),
        3:(-.75,1.15),4:(-.25,1.15),5:(.25,1.15),6:(.75,1.15),
        9:(.75,-1.15),10:(.25,-1.15),11:(-.25,-1.15),12:(-.75,-1.15)}
    for p in pp:
        n=int(p[1]);close(one(p,'at')[1:3], anchors[n])
        close(one(p,'size')[1:3], [1.05,.4] if n in [1,2,7,8] else [.2,.6])
    pp = pads('TI_RUK0020_TPD6S300')
    assert {p[1] for p in pp if p[1]} == set(map(str,range(1,22)))
    for p in pp:
        if not p[1]:continue
        n=int(p[1])
        if n == 21:
            close(one(p,'at')[1:3], [0,0]);close(one(p,'size')[1:3], [1.7,1.7])
        else:
            a = ((n-1)%5-2)*.4
            xy = [-1.4,a] if n<=5 else [a,1.4] if n<=10 else [1.4,-a] if n<=15 else [-a,-1.4]
            close(one(p,'at')[1:3], xy)
            close(one(p,'size')[1:3], [.6,.2] if n<=5 or 11<=n<=15 else [.2,.6])
    pp = pads('GCT_USB4105_GF_A_120')
    assert len(pp) == 22 and {p[1] for p in pp} == {'' ,'SH','A1','A4','A5','A6','A7','A8','A9','A12','B1','B4','B5','B6','B7','B8','B9','B12'}
    xs={'A1':-3.2,'B12':-3.2,'A4':-2.4,'B9':-2.4,'A9':2.4,'B4':2.4,'A12':3.2,'B1':3.2,
        'B8':-1.75,'A5':-1.25,'B7':-.75,'A6':-.25,'A7':.25,'B6':.75,'A8':1.25,'B5':1.75}
    for p in pp:
        n=p[1]
        if n in xs:
            close(one(p,'at')[1:3], [xs[n],-3.68])
            close(one(p,'size')[1:3], [.6 if abs(xs[n])>2 else .3,1.15])
        elif n == '':
            close([abs(one(p,'at')[1]),one(p,'at')[2]], [2.89,-2.605])
            assert one(p,'drill')[1] == .65
        else:
            x,y=one(p,'at')[1:3];assert abs(x)==4.32
            assert y in [-3.105,1.075]
    for name in ['GCT_USB4105_GF_A_120','TI_RUK0020_TPD6S300','TI_RUX0012_TPS2121','Hynetek_DFN10_3x3_P0.5_EP1.8x2.5']:
        model=root/'lib/cm4.3dshapes'/(name+'.step')
        assert model.stat().st_size > 1000 and model.read_text().lstrip().startswith('ISO-10303-21;')
    return {'captured_components':len(exact_parts),'custom_lands_checked':4,
        'aux_uv_rising_V':uv_rise,'aux_uv_falling_V':uv_fall,'aux_ov_rising_V':ov_rise,
        'aux_ov_falling_V':ov_fall,'window_high_bound_V':valid_min,'mux_limit_with_2percent_resistor_drift_A':mux_current,
        'status':'STATIC_CAPTURE_CHECKPOINT; surge, thermal and full-system power qualification remain open'}
