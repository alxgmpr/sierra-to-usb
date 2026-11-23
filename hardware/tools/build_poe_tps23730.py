#!/usr/bin/env python3
"""Capture the TPS23730 PD + primary-side-regulated 12 V flyback from TI PMP22477.

Source of truth: reference/pmp22477-import/power-stage.kicad_sch, which is sheet 2 of TI's
PMP22477 Rev C Altium project (reference/pmp22477-cad.zip, TIDMA52), imported with
`kicad-cli sch import`. Kept parts keep TI's symbols and pin connectivity.
check_appliance_capture.py proves the captured partition against the import using the rules below.

Our active input bridge (poe-input, TIDA-050023) stays and feeds POE_VDD/POE_VSS.
"""
import hashlib, re, subprocess, tempfile, xml.etree.ElementTree as ET
from capture import ROOT, Sheet, block, children, quote

CLI = '/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli'
SRC = ROOT / 'reference/pmp22477-import/power-stage.kicad_sch'
# Adapter input path and its OR diode (aux ORing lives on aux-power), output/test terminals,
# setpoint-shift jumper circuit, and the input TVS that duplicates D1705 on the bridge.
DROP = {'D10', 'L4', 'L5', 'L6', 'C15', 'C19', 'C20', 'J10', 'J11', 'J12', 'J13', 'J14',
        'U11', 'Q5', 'R54', 'R56', 'R57', 'R62', 'D13'}
STRAPS = {'R48', 'R49', 'R52', 'R55', 'R59', 'R60', 'R73'}   # 0R configuration links: tied directly
OPEN = {'R65'}           # 0R SCDIS->VSS selects the serial grant code; open SCDIS = parallel TPH/TPL/BT
TIES = [('PPD', 'VSS')]  # PPD was driven by TI's sheet 3; unused here, tied to VSS
NETS = {'VDD': 'POE_VDD', 'VSS': 'POE_VSS', 'PGND': 'POE_RTN', 'GND': 'GND', 'VOUT': 'ISO_12V_PSU',
        'TPH': 'POE_TPH', 'TPL': 'POE_TPL', 'BT': 'POE_BT', 'VCC': 'POE_VCC', 'VB': 'POE_VB'}


def ref(r):
    return re.sub(r'\d+', lambda m: str(1700 + int(m[0])), r)


def import_netlist():
    with tempfile.TemporaryDirectory() as d:
        out = f'{d}/pmp.xml'
        subprocess.run([CLI, 'sch', 'export', 'netlist', '--format', 'kicadxml', '--output', out, str(SRC)],
                       check=True, capture_output=True)
        return ET.parse(out).getroot()


def groups(tree):
    """Kept pins grouped into nets after straps, ties and drops: {group name: {(ref, pin)}}."""
    parent = {}
    def find(a):
        while parent.setdefault(a, a) != a: a = parent[a]
        return a
    def union(a, b): parent[find(a)] = find(b)
    pins = {}
    for net in tree.findall('./nets/net'):
        name = net.get('name'); find(name)
        for n in net.findall('node'): pins[(n.get('ref'), n.get('pin'))] = name
    for r in STRAPS:
        union(pins[(r, '1')], pins[(r, '2')])
    for a, b in TIES:
        union(a, b)
    out = {}
    for (r, p), name in pins.items():
        if r in DROP | STRAPS | OPEN or r.startswith(('Logo',)):
            continue
        out.setdefault(find(name), set()).add((ref(r), p))
    named = {}
    for root, members in out.items():
        nets = {n for n in parent if find(n) == root}
        iface = {NETS[n] for n in nets if n in NETS}
        assert len(iface) <= 1, iface
        if iface:
            label = iface.pop()
        elif root.startswith('unconnected-') or len(members) == 1:   # e.g. SCDIS once R65 is left open
            label = None
        else:
            plain = sorted(n for n in nets if not n.startswith('Net-('))
            label = 'PMP_' + (plain[0] if plain else re.sub(r'\W+', '_', re.sub(r'^Net-\((\w+?)-', lambda m: ref(m[1]) + '_', root)).strip('_'))
        named[label or 'unconnected-' + root] = members
    return named


SAM, TDK, YAG = 'Samsung Electro-Mechanics', 'TDK', 'Yageo'
CAP = {  # TI MPN -> our standard part (same or better spec), value, extra fields
    'GRM32ER71E226KE15L': ('CL32B226KAJNNNE', SAM, '22uF', '25V', 'X7R', '10%'),
    'GRJ188R71E105KE11D': ('CL10B105KA8NNNC', SAM, '1uF', '25V', 'X7R', '10%'),
    'C0603C104J3RACTU': ('CL10B104KA8NNNC', SAM, '100nF', '25V', 'X7R', '10%'),
    'GRM188R71C473KA01D': ('CL10B473KB8NNNC', SAM, '47nF', '50V', 'X7R', '10%'),
    'GRM188R71H221KA01D': ('CL10C221JB8NNNC', SAM, '220pF', '50V', 'C0G', '5%'),
    '885012206083': ('C1608X7R2A102K', TDK, '1nF', '100V', 'X7R', '10%'),
    '885012006057': ('CL10C101JB8NNNC', SAM, '100pF', '50V', 'C0G', '5%'),
    'C0603C222K5RAC': ('06031C222KAT2A', 'AVX', '2.2nF', '100V', 'X7R', '10%'),
    '06031C222KAT2A': ('06031C222KAT2A', 'AVX', '2.2nF', '100V', 'X7R', '10%'),
    'C2012X7R2A104K125AA': ('C2012X7R2A104K125AA', TDK, '100nF', '100V', 'X7R', '10%'),
    'GRM32ER72A225KA35L': ('GRM32ER72A225KA35L', 'Murata', '2.2uF', '100V', 'X7R', '10%'),
    'C1608X7R1H153K080AA': ('C1608X7R1H153K080AA', TDK, '15nF', '50V', 'X7R', '10%'),
    'GRM21A5C2E101JW01D': ('GRM21A5C2E101JW01D', 'Murata', '100pF', '250V', 'C0G', '5%'),
    'C4532X7R3D222K130KA': ('C4532X7R3D222K130KA', TDK, '2.2nF', '2kV', 'X7R', '10%'),
    'EEE-FK1K470P': ('EEE-FK1K470P', 'Panasonic', '47uF', '80V', 'Al', '20%'),
    'EEE-FK1E221P': ('EEE-FK1E221P', 'Panasonic', '220uF', '25V', 'Al', '20%'),
}
YAGEO_0603 = {'110k': '110K', '10.0k': '10K', '39.2k': '39K2', '24.9k': '24K9', '237k': '237K', '60.4k': '60K4',
              '4.99k': '4K99', '4.7': '4R7', '49.9k': '49K9', '750k': '750K', '25.5k': '25K5', '1.00k': '1K', '499k': '499K'}
FP = {'0603': 'R_0603_1608Metric_Pad0.98x0.95mm_HandSolder', '0603L': 'R_0603_1608Metric_Pad0.98x0.95mm_HandSolder',
      '0805_HV': 'R_0805_2012Metric_Pad1.20x1.40mm_HandSolder', '1206': 'R_1206_3216Metric_Pad1.30x1.75mm_HandSolder',
      '1206L': 'R_1206_3216Metric_Pad1.30x1.75mm_HandSolder', '2512': 'R_2512_6332Metric_Pad1.40x3.35mm_HandSolder',
      '2010': 'R_2010_5025Metric_Pad1.40x2.65mm_HandSolder'}
CFP = {'0603': 'C_0603_1608Metric_Pad1.08x0.95mm_HandSolder', '0603L': 'C_0603_1608Metric_Pad1.08x0.95mm_HandSolder',
       '0805_HV': 'C_0805_2012Metric_Pad1.18x1.45mm_HandSolder', '1210_270': 'C_1210_3225Metric_Pad1.33x2.70mm_HandSolder',
       '1812_HV': 'C_1812_4532Metric_Pad1.57x3.40mm_HandSolder'}
OTHER_FP = {'SMA': 'Diode_SMD:D_SMA_Handsoldering', 'SOD-123': 'Diode_SMD:D_SOD-123', 'TO-277A': 'PoE:TI_TO-277A',
            'SM_RADIAL_G': 'PoE:TI_SM_RADIAL_G', 'SM_RADIAL_F': 'PoE:TI_SM_RADIAL_F',
            'TRANS_Fairchild_PQFN08A': 'PoE:TI_TRANS_Fairchild_PQFN08A', 'LPS4018': 'Inductor_SMD:L_Coilcraft_LPS4018',
            'RMT0045A': 'PoE:TI_RMT0045A', 'FP-LDT9055-B_SMT_27MM5_26MM0-MFG': 'PoE:TI_LDT9055'}


def part_fields(r, comp):
    f = {x.get('name'): x.text or '' for x in comp.findall('./fields/field')}
    mpn, maker, value, tifp = f.get('PARTNUMBER', comp.findtext('value')), f.get('MANUFACTURER', ''), f.get('ALTIUM_VALUE') or comp.findtext('value'), comp.findtext('footprint').split(':')[-1]
    fields = {'Datasheet': f.get('COMPONENTLINK1URL', '')} if f.get('COMPONENTLINK1URL') else {}
    if r.startswith('C') and mpn in CAP:
        mpn, maker, value, volts, diel, tol = CAP[mpn]
        fields.update({'Voltage Rating': volts, 'Dielectric': diel, 'Tolerance': tol})
        fp = 'Capacitor_SMD:' + CFP[tifp] if tifp in CFP else OTHER_FP[tifp]
    elif r.startswith('R'):
        if tifp in ('0603', '0603L') and value in YAGEO_0603:
            mpn, maker = f'RC0603FR-07{YAGEO_0603[value]}L', YAG
        fields.update({'Tolerance': f.get('TOLERANCE_%', '1') .rstrip('%') + '%', 'Power Rating': (f.get('POWER_W') or '').replace('mW', 'mW')})
        fp = 'Resistor_SMD:' + FP[tifp]
    else:
        fp = OTHER_FP[tifp]
    return value, mpn, maker, fp, {k: v for k, v in fields.items() if v}


class PoESheet(Sheet):
    LOCAL = set()

    def net(self, name, point, angle=0):
        if name not in self.LOCAL:
            return super().net(name, point, angle)
        self.items.append(f'(label "{quote(name)}" (at {point[0]} {point[1]} {angle}) (effects (font (size 1.27 1.27)) '
                          f'(justify {"right" if angle == 0 else "left"})) (uuid "{self.uid("lnet-" + name + str(point))}"))')


def extent(body):
    pts = [tuple(map(float, re.search(r'\(at ([-\d.]+) ([-\d.]+)', block(body, m.start())).groups()))
           for m in re.finditer(r'\(pin \w+ \w+', body)]
    xs, ys = [p[0] for p in pts], [p[1] for p in pts]
    return min(xs) - 25.4, max(xs) + 25.4, min(ys) - 10.16, max(ys) + 10.16


def build():
    tree = import_netlist()
    named = groups(tree)
    pin_net = {p: n for n, ps in named.items() for p in ps}
    raw = SRC.read_text()
    libs = block(raw, raw.index('(lib_symbols'))
    lib_of = {(re.search(r'\(reference "([^"]+)"', it) or re.search(r'\(property "Reference" "([^"]+)"', it))[1]:
              (re.search(r'\(lib_name "([^"]+)"', it[:200]) or re.search(r'\(lib_id "([^"]+)"', it))[1]   # lib_name marks a per-instance variant
              for it in children(raw) if it.startswith('(symbol') and '(lib_id' in it[:200]}
    comps = {c.get('ref'): c for c in tree.findall('./components/comp')}
    keep = sorted((r for r in comps if r not in DROP | STRAPS | OPEN and not r.startswith('Logo')),
                  key=lambda r: ({'U': 0, 'T': 1, 'Q': 2, 'D': 3, 'L': 4, 'C': 5, 'R': 6}[r[0]], int(r[1:])))
    s = PoESheet('poe-flyback', 'PoE PD and isolated 12 V flyback (TPS23730, TI PMP22477)', 'A1')
    s.LOCAL = {n for n in named if n.startswith('PMP_')}
    registry = (ROOT / 'PoE.kicad_sym').read_text()
    x, y, row_h = 30.48, 50.8, 0
    for r in keep:
        old = lib_of[r]
        body = block(libs, libs.index(f'(symbol "{old}"'))
        name = 'TI_' + hashlib.sha256(body.encode()).hexdigest()[:12]
        short = old.split(':')[-1]
        canon = body.replace(f'(symbol "{old}"', f'(symbol "{name}"', 1).replace(f'(symbol "{short}_', f'(symbol "{name}_')
        if f'(symbol "{name}"' not in registry:
            registry = registry.rstrip()[:-1] + canon + ')\n'
        x0, x1, y0, y1 = extent(canon)
        w, h = x1 - x0, y1 - y0
        if x + w > 800:
            x, y, row_h = 30.48, y + row_h + 12.7, 0
        cx, cy = round((x - x0) / 2.54) * 2.54, round((y - y0) / 2.54) * 2.54
        value, mpn, maker, fp, fields = part_fields(r, comps[r])
        pins = s.symbol(f'PoE:{name}', canon, ref(r), value, cx, cy, fp, {'MPN': mpn, 'Manufacturer': maker, **fields})
        s.attach(pins, {p: pin_net.get((ref(r), p)) if not pin_net.get((ref(r), p), 'unconnected-').startswith('unconnected-') else None for p in pins})
        x += w + 12.7; row_h = max(row_h, h)
    # Light-load clamp: PSR output rises to ~15.7 V at no load (TIDT259 2.3); 470R holds ~13.4 V.
    y += row_h + 25.4
    s.passive('R', 'R1775', '470R 1W', 50.8, y, 'ISO_12V_PSU', 'GND', 'RC2512FK-07470RL',
              'Resistor_SMD:R_2512_6332Metric_Pad1.40x3.35mm_HandSolder', YAG,
              {'Tolerance': '1%', 'Power Rating': '1W', 'Function': 'PSR light-load preload: ~13.4 V standby, 0.38 W idle'})
    s.flag('#FLG1701', 'POE_VDD', 101.6, y, 'Active bridge output (poe-input)')
    s.flag('#FLG1702', 'POE_RTN', 127, y, 'TPS23730 internal hotswap output')
    s.flag('#FLG1703', 'ISO_12V_PSU', 152.4, y, 'Flyback rectifier D1711')
    s.flag('#FLG1704', 'POE_VCC', 177.8, y, 'Bias winding via D1714 / TPS23730 startup')
    s.flag('#FLG1705', 'POE_VSS', 203.2, y, 'Active bridge output (poe-input)')
    s.note('TPS23730 (802.3bt Type 3, Class 6) + PSR flyback from TI PMP22477 Rev C sheet 2 (native import).\n'
           'Dropped: adapter path D10/L4-L6/C15/C19/C20/J10-J12, terminals J13/J14, setpoint shift U11/Q5/R54/R56/R57/R62,\n'
           'input TVS D13 (D1705 on the bridge). 0R straps R48/R49/R52/R55/R59/R60/R73 tied directly. R65 left open:\n'
           'SCDIS floats, so TPH/TPL/BT stay parallel (grant 0/1/0 unchanged). PPD tied to VSS. R1775 preload added.\n'
           'Release holds: LDT9055-51R orderability and isolation rating; light-load/no-load VOUT on the bench.',
           30.48, y + 25.4)
    s.save()
    (ROOT / 'PoE.kicad_sym').write_text(registry)
    print(f'Captured {len(keep) + 1} parts on poe-flyback from PMP22477.')


if __name__ == '__main__':
    build()
