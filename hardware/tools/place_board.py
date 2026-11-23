"""Block floorplan placement for hardware/appliance.kicad_pcb (top side only).

Each schematic block gets its own region with routing channels between blocks.
Phases: anchors (core first, then edge connectors and magnetics) -> parts that
straddle the PoE isolation line -> remaining ICs by ratsnest -> passives packed
next to the pad they serve. The outline is trimmed to the placed parts.

usage: uv run python hardware/tools/place_board.py IN.kicad_pcb OUT.kicad_pcb [--keep]

--keep: incremental. Parts already inside the outline stay exactly where they are
(anchors included); only parts parked off-board by sync_board.py are placed.
"""
import math, re, sys
from collections import defaultdict
def blocks(s):
    idx=[m.start()+2 for m in re.finditer(r'\n\t\(footprint "',s)]
    ends=[]
    for a in idx:
        d=0;i=a
        while True:
            c=s[i]
            if c=='(':d+=1
            elif c==')':
                d-=1
                if d==0: ends.append(i+1);break
            elif c=='"':
                i+=1
                while s[i]!='"':
                    if s[i]=='\\': i+=1
                    i+=1
            i+=1
    return list(zip(idx,ends))
NUM=r'(-?[\d.]+)'
def parse(s):
    fps={}
    for a,b in blocks(s):
        t=s[a:b]
        ref=re.search(r'\(property "Reference" "([^"]+)"',t)[1]
        m=re.search(r'\(transform\s*\(translate '+NUM+' '+NUM+r'\)\s*\(rotate '+NUM+r'\)',t)
        pads=[]
        for pm in re.finditer(r'\(pad "([^"]*)" (\w+) (\w+)\s*\(at '+NUM+' '+NUM+r'(?: '+NUM+r')?\)\s*\(size '+NUM+' '+NUM+r'\)(.*?)\(uuid',t,re.S):
            net=re.search(r'\(net "([^"]*)"\)',pm[9]);
            pads.append(dict(num=pm[1],kind=pm[2],x=float(pm[4]),y=float(pm[5]),w=float(pm[7]),h=float(pm[8]),net=net[1] if net else ''))
        xs=[];ys=[]
        for cm in re.finditer(r'\((fp_line|fp_rect|fp_poly|fp_circle|fp_arc)(.*?)\(layer "[FB]\.(?:CrtYd|Fab)"\)',t,re.S):
            pts=[(float(p[1]),float(p[2])) for p in re.finditer(r'\((?:start|end|xy|center|mid) '+NUM+' '+NUM+r'\)',cm[2])]
            if cm[1]=='fp_circle':
                (cx,cy),(ex,ey)=pts[:2]; rr=math.hypot(ex-cx,ey-cy); pts=[(cx-rr,cy-rr),(cx+rr,cy+rr)]
            for x,y in pts: xs.append(x);ys.append(y)
        for p in pads:   # pads always inside the keep-out (some courtyards omit tabs)
            e=max(p['w'],p['h'])/2+.15; xs+= [p['x']-e,p['x']+e]; ys+=[p['y']-e,p['y']+e]
        sh=re.search(r'\(sheetfile "([^"]+)"',t)
        side=re.search(r'\(layer "([^"]+)"',t)[1][0]
        if side=='B':   # store bottom parts in their top-side (unflipped) shape
            for p in pads: p['y']=-p['y']
            ys=[-y for y in ys]
        fps[ref]=dict(side=side,ref=ref,lib=re.match(r'\(footprint "([^"]+)"',t)[1],x=float(m[1]),y=float(m[2]),rot=float(m[3]),
            layer=re.search(r'\(layer "([^"]+)"',t)[1],sheet=sh[1] if sh else '',
            val=re.search(r'\(property "Value" "([^"]*)"',t)[1],pads=pads,
            crt=(min(xs),min(ys),max(xs),max(ys)),span=(a,b))
    return fps


# ============================================================== floorplan (board-local mm, x right, y down)
SRC, DST = sys.argv[1], sys.argv[2]   # input board, output board
KEEP = '--keep' in sys.argv[3:]
s = open(SRC).read()
fps = parse(s)
X0, Y0 = 333.8, 38.05      # outline top-left stays put
W, H = 200.0, 100.0        # placement sandbox; outline is trimmed to fit afterwards
XB, MOAT = 40.0, 1.25      # vertical PoE isolation line, half of the 2.5 mm moat
XN, NY = 30.0, 25.0        # above NY the line steps left to XN so the magnetics sit right behind the RJ45
GAP = 0.25                 # minimum courtyard-to-courtyard spacing
INSET = 1.0                # keep parts this far inside their block -> 2 mm channels between blocks
EDGE = 1.0

BLOCKS = {   # block: (sheets, region rectangles)
    'PRIM':  ((), [(0, 0, XN, 100), (0, NY, XB, 100)]),
    'NIC':   (('nic', 'nic-power', 'nic-bypass', 'nic-interface', 'phy-power', 'ethernet-ingress'), [(XB, 0, 83, 42), (XN, 0, 83, NY)]),
    'PSEC':  (('poe-input', 'poe-pd', 'poe-flyback', 'poe-status', 'main5v', 'main3v3', 'always-on', 'aux-power'), [(XB, 42, 83, 100)]),
    'CORE':  (('processor', 'ram', 'boot', 'pmic', 'cpu-power', 'ddr-power', 'core-power', 'peripheral-power', 'boot-media'), [(83, 0, 140, 91)]),
    'MODEM': (('modem-socket', 'modem-power', 'modem-bypass', 'modem-interface'), [(140, 0, 200, 70), (121, 30, 141, 66)]),
    'CTRL':  (('supervisor', 'controls', 'host-interface', 'recovery', 'management'), [(140, 70, 200, 100), (83, 91, 140, 100)]),
}
ANCH = {   # most important first: core, then the connectors and magnetics that fix the edges
    'U801':  (111, 46, 0),      # RK3566; DDR balls top-left, USB3/PCIe on the right
    'J2001': (144, 50, 90),     # M.2 Key-B; card extends to +x towards the right edge
    'J1701': (17.5, 14, 270),   # RJ45, opening on the left edge
    'T1701': (XN, 14, 90),      # magnetics straddle the isolation line, cable side left, hard behind the jack
    'D1851': (38, 17, 180), 'D1852': (38, 9.5, 180),   # ESD arrays in the MDI lane, each centred on its two pairs
    'U1301': (45, 14, 180),     # NIC on the magnetics' axis, MDI pins facing them
    'U1901': (160, 14, 0),      # modem buck
    'J2002': (184, 13, 0),      # SIM
    'U201':  (166, 82, 0),      # supervisor MCU
    'J1201': (152, 96.6, 0), 'SW201': (163, 96, 0), 'SW801': (173, 96, 0), 'SW802': (183, 96, 0),
    'J1202': (190.5, 97.2, 90),
    'J101': (87, 97.2, 90), 'J102': (93.5, 97.2, 90), 'J201': (122, 97.2, 90), 'J202': (141, 97.2, 90),
}
OVERHANG = {'J1701', 'J1201'}             # connectors allowed to sit on/over the board edge
CARD = (146.0, 34.5, 199.5, 65.5)         # M.2 3042/3052 card: keep clear
TIDY = {'CORE', 'PSEC', 'NIC', 'MODEM', 'CTRL'} # blocks whose passives are fanned around their host in rows
STAGE = {'PSEC', 'NIC', 'MODEM', 'CTRL'} # blocks of discrete regulators: ICs keep pin 1 one way and get their inductor placed with them
# PoE front end in flow order below the jack: Bob Smith row, bridge (high side over low side, every cathode up,
# so the pair nodes sit between the rows and the rails run along the top and bottom), ideal-diode FET with its
# gate network beside each low-side diode, then choke -> TVS -> bulk cap -> PD controller left to right.
ANCH.update({r: (13 + 2*i, 26, 90) for i, r in enumerate(('C1861', 'R1861', 'C1862', 'R1862', 'C1863', 'R1863', 'C1864', 'R1864'))})
for i, x in enumerate((3.25, 12.0, 20.75, 29.5)):   # one column per cable pair: 12, 36, 45, 78
    ANCH.update({f'D{1701+i}': (x, 33, 270), f'D{1706+i}': (x, 43, 270), f'Q{1701+i}': (x + 4.25, 40.5, 90),
                 f'R{1713+i}': (x + 4.25, 43.75, 0), f'C{1709+i}': (x + 4.25, 45.5, 0), f'R{1709+i}': (x + 4.25, 47.25, 0)})
ANCH['C1865'] = (8, 26, 180)   # Bob Smith common to chassis, at the end of the row next to the shield pin
ANCH.update({'L1702': (6, 55, 180), 'D1705': (14, 54.5, 270)})
BARRIER = {'T1701', 'T1702', 'U1801', 'U1802', 'U1803'}

def short(n): return re.sub(r'^/.*/', '', n)
sheet_block = {sh + '.kicad_sch': b for b, (shs, _) in BLOCKS.items() for sh in shs}

# ============================================================== nets and PoE domains
netpads = defaultdict(list)
for f in fps.values():
    for i, p in enumerate(f['pads']):
        if p['net'] and not p['net'].startswith('unconnected'):
            netpads[p['net']].append((f['ref'], i))
RAIL = {n for n, v in netpads.items() if len({r for r, _ in v}) > 8 or short(n) == 'GND'}
def is_small(f): return len(f['pads']) <= 3 or bool(re.match(r'^(C|R|FB|TP|L|D)\d', f['ref']))

prim_nets = {n for n in netpads if re.fullmatch(r'CABLE_MDI\d_[NP]|POE_PAIR\d+|POE_(VDD|VSS|RTN|VCIN|VCOUT|DEN|CLSA|CLSB|REF|UVLO|TPH|TPL|BT|AMPS_CTL)|CHASSIS', short(n))}
stop = {n for n in netpads if short(n) in ('GND', 'ISO_12V', 'ISO_12V_PSU', 'ISO_12V_BUS', '+3V3')}
changed = True
while changed:
    changed = False
    for f in fps.values():
        if f['ref'] in BARRIER: continue
        ns = {p['net'] for p in f['pads'] if p['net'] in netpads}
        if ns & prim_nets and not ns & stop and ns - prim_nets:
            prim_nets |= ns; changed = True
domain = {}
for f in fps.values():
    ns = {p['net'] for p in f['pads'] if p['net'] in netpads}
    domain[f['ref']] = 'B' if f['ref'] in BARRIER or (ns & prim_nets and ns & stop) else 'P' if ns & prim_nets else 'S'
BARRIER |= {r for r, d in domain.items() if d == 'B'}
# Parts that belong next to another block's hardware; test pads go wherever their net is (no block).
PART_BLOCK = {**{r: 'MODEM' for r in ('U2303', 'R2311', 'R2312', 'R2313', 'R2314', 'C2305', 'R2213', 'C2206', 'RT2201', 'C2207', 'R2214')},
              **{r: 'PSEC' for r in ('RT2202', 'C2208', 'R2215')}}
block = {r: 'PRIM' if domain[r] == 'P' else None if domain[r] == 'B' or f['sheet'] == 'test-points.kicad_sch' else PART_BLOCK.get(r) or sheet_block[f['sheet']] for r, f in fps.items()}

# Local bypass caps of the SoC, RAM and eMMC go on the bottom, under or beside their package.
BGAS = ('U801', 'U901', 'U1101')
def bottom_cap(f):
    if not re.match(r'C\d', f['ref']) or not re.search(r'C_0(603|402)_', f['lib']) or len(f['pads']) != 2: return False
    if f['sheet'] not in ('processor.kicad_sch', 'core-power.kicad_sch', 'peripheral-power.kicad_sch', 'ram.kicad_sch', 'boot.kicad_sch'): return False
    m = re.match(r'([\d.]+)\s*([pnu])', f['val'])
    if not m or float(m[1]) * {'p': 1e-12, 'n': 1e-9, 'u': 1e-6}[m[2]] > 4.7e-6: return False
    nets = [p['net'] for p in f['pads']]
    return any(short(n) == 'GND' for n in nets) and any(r in BGAS for n in nets for r, _ in netpads.get(n, ()))
BOTTOM = {r for r, f in fps.items() if bottom_cap(f)}
side = {r: ('B' if r in BOTTOM else 'F') for r in fps}

# ============================================================== geometry and legality
def rot_pt(x, y, r):
    a = math.radians(r); return x*math.cos(a) + y*math.sin(a), -x*math.sin(a) + y*math.cos(a)
def rect(f, u, v, r, infl=0.0, flip=None):
    x0, y0, x1, y1 = f['crt']
    if flip if flip is not None else side[f['ref']] == 'B': y0, y1 = -y1, -y0
    pts = [rot_pt(x, y, r) for x in (x0, x1) for y in (y0, y1)]
    return (u + min(p[0] for p in pts) - infl, v + min(p[1] for p in pts) - infl,
            u + max(p[0] for p in pts) + infl, v + max(p[1] for p in pts) + infl)
placed = {}
SPILL = []   # --keep: new parts that had to go on the bottom side
def pad_abs(ref, i, pos=None):
    u, v, r = pos or placed[ref]; p = fps[ref]['pads'][i]
    dx, dy = rot_pt(p['x'], -p['y'] if side[ref] == 'B' else p['y'], r); return u + dx, v + dy

CELL = 4.0
grid = defaultdict(list)
def cells(R):
    for i in range(int(R[0]//CELL), int(R[2]//CELL) + 1):
        for j in range(int(R[1]//CELL), int(R[3]//CELL) + 1): yield i, j
grid_b = defaultdict(list)   # bottom side: bottom parts + through-hole pins
def collide(R, g=None):
    for c in cells(R):
        for Q in (grid if g is None else g)[c]:
            if R[0] < Q[2] and Q[0] < R[2] and R[1] < Q[3] and Q[1] < R[3]: return True
    return False
def commit(ref, u, v, r, R):
    placed[ref] = (u, v, r)
    for c in cells(R): (grid_b if side[ref] == 'B' else grid)[c].append(R)
def inside(R, box, m): return R[0] >= box[0] + m and R[1] >= box[1] + m and R[2] <= box[2] - m and R[3] <= box[3] - m
def legal(ref, R):
    """R is the courtyard grown by GAP/2 on each side."""
    if ref not in OVERHANG and not inside(R, (0, 0, W, H), EDGE - GAP/2): return False
    d = domain[ref]
    m = MOAT - GAP/2   # the isolation line runs down XN to NY, across to XB, then down XB
    if d == 'P' and R[2] > XN - m and (R[2] > XB - m or R[1] < NY + m): return False
    if d == 'S' and R[0] < XB + m and (R[0] < XN + m or R[3] > NY - m): return False
    if d != 'B':
        if side[ref] == 'F' and R[0] < CARD[2] and CARD[0] < R[2] and R[1] < CARD[3] and CARD[1] < R[3]: return False
        if block[ref] and not any(inside(R, b, INSET - GAP/2) for b in BLOCKS[block[ref]][1]): return False
    if side[ref] == 'B':   # through-hole pins of a bottom part also pierce the top side
        return not collide(R, grid_b) and not (any('thru_hole' in p['kind'] for p in fps[ref]['pads']) and collide(R))
    return not collide(R)

# ============================================================== phase 1: anchors
# DNP microSD: no top-side room left, so it sits on the bottom under the M.2 card (empty there),
# card opening (footprint +y) facing the right edge; its DNP support parts go on the bottom beside it.
SD_BOTTOM = ('J2301', 'D2301', 'D2302', 'R2305', 'R2306', 'R2307', 'R2308', 'R2309', 'U2302', 'R2310', 'C2302', 'C2303', 'C2304')
KEEP_ANCH = {'J2301': (190, 50, 270),
             # status LEDs in a column by the MCU, top to bottom: PWR, SYS, WAN, FAULT
             'D2201': (180.7, 72, 0), 'D2202': (180.7, 76, 0), 'D2203': (180.7, 80, 0), 'D2204': (180.7, 82, 0)}
# --keep search targets: the aux power path and the power NTC belong under the flyback secondary (bottom side).
KEEP_TARGET = {**{r: (70, 90) for r in ('J2101', 'U2101', 'U2102', 'Q2101', 'Q2102')}, 'U2103': (55, 86), 'R2101': (55, 91), 'RT2202': (55, 80)}
if KEEP:   # every part already on the board is fixed in its current pose and side
    for ref, f in fps.items():
        u, v = f['x'] - X0, f['y'] - Y0
        if 0 <= u <= W and 0 <= v <= H:
            side[ref] = f['side']; commit(ref, u, v, f['rot'], rect(f, u, v, f['rot'], GAP/2))
    for ref in SD_BOTTOM:
        if ref in fps and ref not in placed: side[ref] = 'B'; block[ref] = None
    for ref, (u, v, r) in KEEP_ANCH.items():
        if ref in fps and ref not in placed: commit(ref, u, v, r, rect(fps[ref], u, v, r, GAP/2))
    for ref in list(placed):   # through-hole pins of fixed parts occupy the bottom side too
        for i, p in enumerate(fps[ref]['pads']):
            if 'thru_hole' in p['kind']:
                x, y = pad_abs(ref, i); e = max(p['w'], p['h'])/2 + 0.25
                for c in cells((x-e, y-e, x+e, y+e)): grid_b[c].append((x-e, y-e, x+e, y+e))
else:
    for ref, (u, v, r) in ANCH.items():
        commit(ref, u, v, r, rect(fps[ref], u, v, r, GAP/2))

# ============================================================== scoring
def ratsnest(ref, pos):
    f = fps[ref]; tot = 0.0
    for i, p in enumerate(f['pads']):
        net = p['net']
        if net not in netpads or net in RAIL: continue
        best = None
        for r2, j in netpads[net]:
            if r2 == ref or r2 not in placed: continue
            a = pad_abs(ref, i, pos); b = pad_abs(r2, j)
            d = math.hypot(a[0]-b[0], a[1]-b[1]) * (1.0 if fps[r2]['sheet'] == f['sheet'] else 0.25)
            best = d if best is None else min(best, d)
        if best is not None: tot += best
    return tot
def neighbours(ref):
    out = set()
    for p in fps[ref]['pads']:
        if p['net'] in netpads and p['net'] not in RAIL: out |= {r for r, _ in netpads[p['net']]}
    out.discard(ref); return out
def offsets(rmax, step):
    k = int(rmax/step)
    return sorted([(i*step, j*step) for i in range(-k, k+1) for j in range(-k, k+1) if (i*i+j*j)*step*step <= rmax*rmax],
                  key=lambda t: t[0]**2 + t[1]**2)
OFF_FINE, OFF_COARSE = offsets(16, 0.5), offsets(80, 1.0)
SNAP = 0.5   # passives on a 0.5 mm grid -> aligned rows and columns

ROT_PEN = 2.0   # mm of ratsnest a non-zero IC rotation has to save
def area(ref): c = fps[ref]['crt']; return (c[2]-c[0]) * (c[3]-c[1])
def place_ic(ref, target, halo, dist_w, rmax=60):
    best = None
    if KEEP and ref in KEEP_TARGET: dist_w = max(dist_w, 5.0)   # targets beat ratsnest (INA226 Kelvin sense at the shunt)
    for du, dv in offsets(rmax, 1.0):
        u, v = round(target[0] + du), round(target[1] + dv)
        for r in (0, 90, 180, 270):
            R = rect(fps[ref], u, v, r, GAP/2 + halo)
            if not legal(ref, R): continue
            sc = ratsnest(ref, (u, v, r)) + dist_w * math.hypot(du, dv)
            if block[ref] in STAGE and r: sc += ROT_PEN   # pin 1 the same way unless turning pays off
            if best is None or sc < best[0]: best = (sc, u, v, r, R)
    if best is None and KEEP and side[ref] == 'F':   # top side full: fall back to the bottom, free of block regions
        side[ref] = 'B'; block[ref] = None; SPILL.append(ref); return place_ic(ref, target, halo, dist_w, rmax)
    if best is None: raise SystemExit(f'no spot for {ref} ({block[ref]})')
    commit(ref, *best[1:4], best[4])
    if block[ref] in STAGE and not is_small(fps[ref]):   # power inductors go in next, hard against the switch pin
        for ind in sorted(n for n in neighbours(ref) if n not in placed and re.match(r'L\d', n) and area(n) > 15 and block[n] == block[ref]):
            sw = [pad_abs(ref, j) for p in fps[ind]['pads'] for r2, j in netpads.get(p['net'], ()) if r2 == ref and p['net'] not in RAIL]
            place_ic(ind, sw[0], 0.0, 1.0, rmax=20)
def target_of(ref):
    if KEEP and ref in KEEP_TARGET: return KEEP_TARGET[ref]
    f = fps[ref]; nb = [r for r in neighbours(ref) if r in placed]
    nb = [r for r in nb if fps[r]['sheet'] == f['sheet']] or [r for r in placed if fps[r]['sheet'] == f['sheet']] \
        or [r for r in nb if block[r] == block[ref]] or [r for r in placed if block[r] == block[ref]] or nb
    if nb: return sum(placed[r][0] for r in nb)/len(nb), sum(placed[r][1] for r in nb)/len(nb)
    b = BLOCKS[block[ref]][1][0]; return (b[0]+b[2])/2, (b[1]+b[3])/2

# ============================================================== phase 2: barrier parts on the line
for ref in sorted(BARRIER - set(ANCH) - set(placed), key=lambda r: (-len(fps[r]['pads']), r)):
    f = fps[ref]; best = None; cv = target_of(ref)[1]
    for v in [y*0.5 for y in range(int(NY*2) + 6, int(H*2) - 4)]:
        for r in (0, 90, 180, 270):
            ok = True
            for p in f['pads']:
                if p['net'] not in netpads: continue
                x = rot_pt(p['x'], p['y'], r)[0]
                if (p['net'] in prim_nets) != (x < 0) or abs(x) < 0.2: ok = False
            if not ok: continue
            R = rect(f, XB, v, r, GAP/2)
            if legal(ref, R) and (best is None or abs(v - cv) < best[0]): best = (abs(v - cv), v, r, R)
    if best is None: raise SystemExit(f'barrier unplaced {ref}')
    commit(ref, XB, best[1], best[2], best[3])

# ============================================================== phase 3: other ICs, most important first
ORDER = ['U901', 'U1101', 'U2001', 'U2002', 'U1604', 'U501', 'U1001', 'U902', 'U1302', 'Y1301', 'U1503',
         'U1710', 'Q1706', 'U701', 'U601', 'U401']
HALO = {'U901': 3.0, 'U1101': 2.0, 'U501': 3.0}
TARGET = {'U2001': (130, 49), 'U2002': (130, 41), 'U501': (100, 74), 'U701': (66, 53), 'U601': (77, 50), 'U401': (77, 60)}   # keep SoC->M.2 lane corridor for the muxes
for ref in ORDER:
    if ref not in placed: place_ic(ref, TARGET.get(ref) or target_of(ref), HALO.get(ref, 1.5), 1.0 if ref in TARGET else 0.1)
while True:
    rest = [r for r, f in fps.items() if r not in placed and not is_small(f)]
    if not rest: break
    ref = max(rest, key=lambda r: (len([n for n in neighbours(r) if n in placed]), len(fps[r]['pads'])))
    place_ic(ref, target_of(ref), 1.0, 0.5)

grid.clear()   # passives may use the IC halos
for ref, (u, v, r) in placed.items():
    for c in cells(rect(fps[ref], u, v, r, GAP/2)): grid[c].append(rect(fps[ref], u, v, r, GAP/2))

# ============================================================== phase 4: passives next to the pad they serve
def val(f):
    m = re.match(r'([\d.]+)\s*([pnuµm]?)', f['val'])
    return float(m[1]) * {'p': 1e-12, 'n': 1e-9, 'u': 1e-6, 'µ': 1e-6, 'm': 1e-3, '': 1}[m[2]] if m else 1.0
load = defaultdict(int)
host = {}                  # passive -> the IC (or connector) it is laid out around
BIG = 7.0                  # hosts at least this wide get their own rings; smaller ones share the board lattice
def q(x, step, up): return (math.ceil(x/step - 1e-6) if up else math.floor(x/step + 1e-6)) * step
def fan(ref, u, v):
    """Fan lattice around the host: two-pad parts stand radially (pads pointing at the host) in rows
    along each host edge. Along a row the pitch is the part width on the SNAP grid, centred on the host;
    rings start at the host courtyard and step by the part length. Around a small host the same
    pitches are counted from the board origin instead. Yields the poses (u, v, r) that grid point (u, v) maps to, none if it is off the lattice."""
    f = fps[ref]; hx, hy, hr = placed[host[ref]]; h = rect(fps[host[ref]], hx, hy, hr, flip=False)
    ox, oy = max(h[0]-u, u-h[2], 0), max(h[1]-v, v-h[3], 0)
    if not ox and not oy: return
    vert = oy >= ox            # above or below the host: rows run along x
    a, t, t0, lo, hi = (v, u, hx, h[1], h[3]) if vert else (u, v, hy, h[0], h[2])
    loose = min(h[2]-h[0], h[3]-h[1]) < BIG   # small host: rows on the board-wide lattice so neighbouring groups line up
    if loose: t0 = 0
    for r in ((90, 270) if vert else (0, 180)):
        p = rect(f, 0, 0, r, GAP/2); p = (p[1], p[3], p[2]-p[0]) if vert else (p[0], p[2], p[3]-p[1])
        k = (t-t0) / q(p[2], SNAP, True); pr = q(p[1]-p[0], SNAP/2, True)
        if abs(k - round(k)) > 1e-6: continue
        if loose:
            pr = q(p[1]-p[0], SNAP, True); aa = round(a/pr) * pr
            if abs(aa-a) > SNAP/2 + 1e-6: continue
        elif a < (lo+hi)/2: base = q(lo - GAP/2 - p[1], SNAP/2, False); m = round((base-a)/pr); aa = base - m*pr
        else: base = q(hi + GAP/2 - p[0], SNAP/2, True); m = round((a-base)/pr); aa = base + m*pr
        if not loose and (m < 0 or abs(aa-a) > SNAP/2 + 1e-6): continue
        yield (t, aa, r) if vert else (aa, t, r)
def target_for(ref, defer):
    if KEEP and ref in KEEP_TARGET: return 0, KEEP_TARGET[ref]
    f = fps[ref]; cands = []
    for i, p in enumerate(f['pads']):
        net = p['net']
        if net not in netpads or short(net) == 'GND': continue
        others = [(r, j) for r, j in netpads[net] if r != ref and r in placed and not re.match(r'^C\d', r)] \
            or [(r, j) for r, j in netpads[net] if r != ref and r in placed]
        same = [(r, j) for r, j in others if fps[r]['sheet'] == f['sheet']]
        if defer and not same and net not in RAIL and any(fps[r]['sheet'] == f['sheet'] and r not in placed and r != ref for r, _ in netpads[net]):
            return None
        if others: cands.append((net in RAIL, i, same or others))
    if not cands: return None
    rail, i, pool = min(cands, key=lambda c: c[0])
    if ref in BOTTOM:   # bottom bypass caps serve the BGA balls on their rail
        pool = [(r, j) for r, j in netpads[f['pads'][i]['net']] if r in BGAS] or pool
    if rail:
        bigs = [(r, j) for r, j in pool if not is_small(fps[r])] or pool
        r, j = min(bigs, key=lambda t: (load[t], t[1]))
    else:
        r, j = min(pool, key=lambda t: (is_small(fps[t[0]]), t[1]))
    load[(r, j)] += 1
    host[ref] = host.get(r, r) if is_small(fps[r]) else r
    return i, pad_abs(r, j)
def place_small(ref, own_pad, tgt, lattice=True):
    f = fps[ref]; best = None; c = tgt; H = host.get(ref)
    one = lattice and side[ref] == 'F' and block[ref] in TIDY and len(f['pads']) != 2
    tidy = lattice and side[ref] == 'F' and len(f['pads']) == 2 and block[ref] in TIDY and H in placed and block[H] in (block[ref], None)
    if block[ref]:   # start the search inside the part's own block
        c = min(((min(max(tgt[0], b[0]+3), b[2]-3), min(max(tgt[1], b[1]+3), b[3]-3)) for b in BLOCKS[block[ref]][1]),
                key=lambda q: math.dist(q, tgt))
    c = (round(c[0] / SNAP) * SNAP, round(c[1] / SNAP) * SNAP)
    base = math.dist(c, tgt)
    for offs in (OFF_FINE, OFF_COARSE):
        for du, dv in offs:
            if best and math.hypot(du, dv) > best[0] - base + 2.0: break
            u, v = c[0] + du, c[1] + dv
            if tidy: poses = fan(ref, u, v)
            elif side[ref] == 'B': poses = [(u, v, r) for r in (0, 180)]   # bottom caps: one axis, clean rows
            elif one: poses = [(u, v, 0)]   # SOT-23s and the like: one orientation
            else: poses = [(u, v, r) for r in (0, 90, 180, 270)]
            for u, v, r in poses:
                R = rect(f, u, v, r, GAP/2)
                if not legal(ref, R): continue
                a = pad_abs(ref, own_pad, (u, v, r))
                sc = math.hypot(a[0]-tgt[0], a[1]-tgt[1]) + (0.15 if r >= 180 else 0)   # prefer 0/90 for tidy silk
                if best is None or sc < best[0]: best = (sc, u, v, r, R)
        if best: break
    if (tidy and best is None) or (one and (best is None or best[0] > 10)):
        return place_small(ref, own_pad, tgt, False)   # lattice full, or no room nearby at 0 deg: free placement
    if best is None and KEEP and side[ref] == 'F':
        side[ref] = 'B'; block[ref] = None; SPILL.append(ref); return place_small(ref, own_pad, tgt, False)
    if best is None: return False
    commit(ref, *best[1:4], best[4]); return True
def prio(ref):
    k = 0 if ref.startswith('L') else 1 if ref.startswith('C') else 2 if ref.startswith(('R', 'FB')) else 3
    if block[ref] in TIDY and area(ref) > (15 if k > 1 else 30): k = 0   # big parts first: the rows leave no room later
    return (k, val(fps[ref]) if k == 1 else 0, ref)
def top_passives(first):
    """Place the top-side passives, those in `first` before the rest. Returns a part that found no room."""
    for ref in first:
        if not place_small(ref, *(target_for(ref, defer=False) or (0, target_of(ref)))): return ref
    pending = sorted([r for r in fps if r not in placed and r not in BOTTOM], key=prio)
    for it in range(16):
        nxt = []
        for ref in pending:
            t = target_for(ref, defer=it < 8)
            if t is None: nxt.append(ref)
            elif not place_small(ref, *t): return ref
        if not nxt or (nxt == pending and it >= 8): pending = nxt; break
        pending = sorted(nxt, key=prio)
    for ref in pending:
        if not place_small(ref, 0, target_of(ref)): return ref
ics = dict(placed), {c: list(v) for c, v in grid.items()}
first = []   # parts that ran out of room go to the front of the queue and the pass is repeated
while True:
    ref = top_passives(first)
    if ref is None: break
    if ref in first: raise SystemExit(f'no room for {ref} ({block[ref]})')
    first.append(ref); load.clear(); host.clear()
    placed.clear(); placed.update(ics[0]); grid.clear(); grid.update({c: list(v) for c, v in ics[1].items()})

for ref in placed:   # through-hole pins also occupy the bottom side
    for i, p in enumerate(fps[ref]['pads']):
        if 'thru_hole' in p['kind']:
            x, y = pad_abs(ref, i); e = max(p['w'], p['h'])/2 + 0.25
            for c in cells((x-e, y-e, x+e, y+e)): grid_b[c].append((x-e, y-e, x+e, y+e))
load.clear()
for ref in sorted(BOTTOM - set(placed), key=prio):
    t = target_for(ref, defer=False)
    if not t or not place_small(ref, *t): raise SystemExit(f'no bottom room for {ref}')

# ============================================================== trim outline to the parts
ext = [rect(fps[r], *placed[r]) for r in placed if r not in OVERHANG]
TW = min(W, math.ceil(max(max(R[2] for R in ext), CARD[2]) + 0.5))
TH = min(H, math.ceil(max(R[3] for R in ext) + 0.5))
print(f'placed {len(placed)}/{len(fps)}  outline {TW} x {TH} mm')
if SPILL: print('bottom-side fallback:', ' '.join(sorted(set(SPILL))))

# ============================================================== write back (pose + absolute pad/text angles)
out = []; last = 0
for ref, f in sorted(fps.items(), key=lambda kv: kv[1]['span'][0]):
    a, b = f['span']; t = s[a:b]
    u, v, r = placed[ref]
    t = re.sub(r'\(translate [-\d.]+ [-\d.]+\)', f'(translate {X0+u:.4f} {Y0+v:.4f})', t, count=1)
    t = re.sub(r'\(rotate [-\d.]+\)', f'(rotate {r % 360:g})', t, count=1)
    if side[ref] != f['side']:   # flip: mirror local y, swap F/B layers, mirror text, reflect angles
        old = f['rot']
        def flip_at(m):
            a = (r - (float(m[3] or 0) - old)) % 360
            return f'(at {m[1]} {-float(m[2]):g}' + (f' {a:g})' if a else ')')
        t = re.sub(r'\(at (-?[\d.]+) (-?[\d.]+)(?: (-?[\d.]+))?\)', flip_at, t)
        t = re.sub(r'\((start|end|mid|center|xy) (-?[\d.]+) (-?[\d.]+)\)', lambda m: f'({m[1]} {m[2]} {-float(m[3]):g})', t)
        t = re.sub(r'"([FB])\.(Cu|Paste|Mask|SilkS|Fab|CrtYd|Adhes)"', lambda m: f'"{"B" if m[1] == "F" else "F"}.{m[2]}"', t)
        def mirror(m):
            flags = sorted(set((m[3] or '').split()) ^ {'mirror'})
            return '(effects' + m[1] + (' (justify ' + ' '.join(flags) + ')' if flags else '')
        t = re.sub(r'\(effects(\s*\(font(?:[^()]|\([^()]*\))*\))(\s*\(justify ([^)]*)\))?', mirror, t)
        delta = 0
    else:
        delta = (r - f['rot']) % 360
    if delta:
        def fix(m):
            a = (float(m[3] or 0) + delta) % 360
            return f'(at {m[1]} {m[2]}' + (f' {a:g})' if a else ')')
        t = re.sub(r'\(at (-?[\d.]+) (-?[\d.]+)(?: (-?[\d.]+))?\)', fix, t)
    if re.match(r'^(C|R|L|FB|TP|D|Q)\d', ref) and len(f['pads']) <= 4:   # passive refs to assembly drawing
        t = re.sub(r'(\(property "Reference" "[^"]*"\s*\(at [^)]*\)\s*\(layer )"F\.SilkS"', r'\1"F.Fab"', t, count=1)
    out.append(s[last:a]); out.append(t); last = b
out.append(s[last:])
board = ''.join(out)
board, n = re.subn(r'(\(gr_rect\s*\(start )[-\d.]+ [-\d.]+(\)\s*\(end )[-\d.]+ [-\d.]+(\)(?:(?!\(gr_rect).)*?\(layer "Edge\.Cuts"\))',
                   lambda m: f'{m[1]}{X0:g} {Y0:g}{m[2]}{X0+TW:g} {Y0+TH:g}{m[3]}', board, count=1, flags=re.S)
assert n == 1, 'outline rectangle not found'
open(DST, 'w').write(board)
