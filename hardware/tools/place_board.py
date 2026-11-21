"""Block floorplan placement for hardware/appliance.kicad_pcb (top side only).

Each schematic block gets its own region with routing channels between blocks.
Phases: anchors (core first, then edge connectors and magnetics) -> parts that
straddle the PoE isolation line -> remaining ICs by ratsnest -> passives packed
next to the pad they serve. The outline is trimmed to the placed parts.

usage: uv run python hardware/tools/place_board.py IN.kicad_pcb OUT.kicad_pcb
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
            pads.append(dict(num=pm[1],x=float(pm[4]),y=float(pm[5]),w=float(pm[7]),h=float(pm[8]),net=net[1] if net else ''))
        xs=[];ys=[]
        for cm in re.finditer(r'\((fp_line|fp_rect|fp_poly|fp_circle|fp_arc)(.*?)\(layer "F\.(?:CrtYd|Fab)"\)',t,re.S):
            pts=[(float(p[1]),float(p[2])) for p in re.finditer(r'\((?:start|end|xy|center|mid) '+NUM+' '+NUM+r'\)',cm[2])]
            if cm[1]=='fp_circle':
                (cx,cy),(ex,ey)=pts[:2]; rr=math.hypot(ex-cx,ey-cy); pts=[(cx-rr,cy-rr),(cx+rr,cy+rr)]
            for x,y in pts: xs.append(x);ys.append(y)
        for p in pads:   # pads always inside the keep-out (some courtyards omit tabs)
            e=max(p['w'],p['h'])/2+.15; xs+= [p['x']-e,p['x']+e]; ys+=[p['y']-e,p['y']+e]
        sh=re.search(r'\(sheetfile "([^"]+)"',t)
        fps[ref]=dict(ref=ref,lib=re.match(r'\(footprint "([^"]+)"',t)[1],x=float(m[1]),y=float(m[2]),rot=float(m[3]),
            layer=re.search(r'\(layer "([^"]+)"',t)[1],sheet=sh[1] if sh else '',
            val=re.search(r'\(property "Value" "([^"]*)"',t)[1],pads=pads,
            crt=(min(xs),min(ys),max(xs),max(ys)),span=(a,b))
    return fps


# ============================================================== floorplan (board-local mm, x right, y down)
SRC, DST = sys.argv[1], sys.argv[2]   # input board, output board
s = open(SRC).read()
fps = parse(s)
X0, Y0 = 333.8, 38.05      # outline top-left stays put
W, H = 200.0, 100.0        # placement sandbox; outline is trimmed to fit afterwards
XB, MOAT = 40.0, 1.25      # vertical PoE isolation line, half of the 2.5 mm moat
GAP = 0.25                 # minimum courtyard-to-courtyard spacing
INSET = 1.0                # keep parts this far inside their block -> 2 mm channels between blocks
EDGE = 1.0

BLOCKS = {   # block: (sheets, region rectangles)
    'PRIM':  ((), [(0, 0, XB, 100)]),
    'NIC':   (('nic', 'nic-power', 'nic-bypass', 'nic-interface', 'phy-power', 'ethernet-ingress'), [(XB, 0, 83, 42)]),
    'PSEC':  (('poe-input', 'poe-pd', 'poe-flyback', 'poe-status', 'main5v', 'main3v3', 'always-on'), [(XB, 42, 83, 100)]),
    'CORE':  (('processor', 'ram', 'boot', 'pmic', 'cpu-power', 'ddr-power', 'core-power', 'peripheral-power'), [(83, 0, 140, 91)]),
    'MODEM': (('modem-socket', 'modem-power', 'modem-bypass', 'modem-interface'), [(140, 0, 200, 70), (121, 30, 141, 66)]),
    'CTRL':  (('supervisor', 'controls', 'host-interface', 'recovery'), [(140, 70, 200, 100), (83, 91, 140, 100)]),
}
ANCH = {   # most important first: core, then the connectors and magnetics that fix the edges
    'U801':  (111, 46, 0),      # RK3566; DDR balls top-left, USB3/PCIe on the right
    'J2001': (144, 50, 90),     # M.2 Key-B; card extends to +x towards the right edge
    'J1701': (17.5, 14, 270),   # RJ45, opening on the left edge
    'T1701': (XB, 14, 90),      # magnetics straddle the isolation line, cable side left
    'U1301': (51, 13, 180),     # NIC, MDI pins facing the magnetics
    'T1702': (XB, 78, 0),       # flyback transformer, primary left
    'U1901': (160, 14, 0),      # modem buck
    'J2002': (184, 13, 0),      # SIM
    'U201':  (166, 82, 0),      # supervisor MCU
    'J1711': (58, 94.9, 0), 'J1712': (68, 95.5, 90),
    'J1201': (152, 96.6, 0), 'SW201': (163, 96, 0), 'SW801': (173, 96, 0), 'SW802': (183, 96, 0),
    'J1202': (190.5, 97.2, 90),
    'J101': (87, 97.2, 90), 'J102': (93.5, 97.2, 90), 'J201': (122, 97.2, 90), 'J202': (141, 97.2, 90),
}
OVERHANG = {'J1701', 'J1201'}             # connectors allowed to sit on/over the board edge
CARD = (146.0, 34.5, 199.5, 65.5)         # M.2 3042/3052 card: keep clear
BARRIER = {'T1701', 'T1702', 'U1703', 'U1801', 'U1802', 'U1803'}

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
stop = {n for n in netpads if short(n) in ('GND', 'ISO_12V', '+3V3')}
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
block = {r: 'PRIM' if domain[r] == 'P' else None if domain[r] == 'B' else sheet_block[f['sheet']] for r, f in fps.items()}

# ============================================================== geometry and legality
def rot_pt(x, y, r):
    a = math.radians(r); return x*math.cos(a) + y*math.sin(a), -x*math.sin(a) + y*math.cos(a)
def rect(f, u, v, r, infl=0.0):
    x0, y0, x1, y1 = f['crt']; pts = [rot_pt(x, y, r) for x in (x0, x1) for y in (y0, y1)]
    return (u + min(p[0] for p in pts) - infl, v + min(p[1] for p in pts) - infl,
            u + max(p[0] for p in pts) + infl, v + max(p[1] for p in pts) + infl)
placed = {}
def pad_abs(ref, i, pos=None):
    u, v, r = pos or placed[ref]; p = fps[ref]['pads'][i]
    dx, dy = rot_pt(p['x'], p['y'], r); return u + dx, v + dy

CELL = 4.0
grid = defaultdict(list)
def cells(R):
    for i in range(int(R[0]//CELL), int(R[2]//CELL) + 1):
        for j in range(int(R[1]//CELL), int(R[3]//CELL) + 1): yield i, j
def collide(R):
    for c in cells(R):
        for Q in grid[c]:
            if R[0] < Q[2] and Q[0] < R[2] and R[1] < Q[3] and Q[1] < R[3]: return True
    return False
def commit(ref, u, v, r, R):
    placed[ref] = (u, v, r)
    for c in cells(R): grid[c].append(R)
def inside(R, box, m): return R[0] >= box[0] + m and R[1] >= box[1] + m and R[2] <= box[2] - m and R[3] <= box[3] - m
def legal(ref, R):
    """R is the courtyard grown by GAP/2 on each side."""
    if ref not in OVERHANG and not inside(R, (0, 0, W, H), EDGE - GAP/2): return False
    d = domain[ref]
    if d == 'P' and R[2] > XB - MOAT + GAP/2: return False
    if d == 'S' and R[0] < XB + MOAT - GAP/2: return False
    if d != 'B':
        if R[0] < CARD[2] and CARD[0] < R[2] and R[1] < CARD[3] and CARD[1] < R[3]: return False
        if block[ref] and not any(inside(R, b, INSET - GAP/2) for b in BLOCKS[block[ref]][1]): return False
    return not collide(R)

# ============================================================== phase 1: anchors
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

def place_ic(ref, target, halo, dist_w, rmax=60):
    best = None
    for du, dv in offsets(rmax, 1.0):
        u, v = round(target[0] + du), round(target[1] + dv)
        for r in (0, 90, 180, 270):
            R = rect(fps[ref], u, v, r, GAP/2 + halo)
            if not legal(ref, R): continue
            sc = ratsnest(ref, (u, v, r)) + dist_w * math.hypot(du, dv)
            if best is None or sc < best[0]: best = (sc, u, v, r, R)
    if best is None: raise SystemExit(f'no spot for {ref} ({block[ref]})')
    commit(ref, *best[1:4], best[4])
def target_of(ref):
    f = fps[ref]; nb = [r for r in neighbours(ref) if r in placed]
    nb = [r for r in nb if fps[r]['sheet'] == f['sheet']] or [r for r in placed if fps[r]['sheet'] == f['sheet']] \
        or [r for r in nb if block[r] == block[ref]] or [r for r in placed if block[r] == block[ref]] or nb
    if nb: return sum(placed[r][0] for r in nb)/len(nb), sum(placed[r][1] for r in nb)/len(nb)
    b = BLOCKS[block[ref]][1][0]; return (b[0]+b[2])/2, (b[1]+b[3])/2

# ============================================================== phase 2: barrier parts on the line
for ref in sorted(BARRIER - set(ANCH), key=lambda r: (-len(fps[r]['pads']), r)):
    f = fps[ref]; best = None; cv = target_of(ref)[1]
    for v in [y*0.5 for y in range(4, int(H*2) - 4)]:
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
         'U1701', 'U1702', 'Q1705', 'U701', 'U601', 'U401']
HALO = {'U901': 3.0, 'U1101': 2.0, 'U501': 3.0}
TARGET = {'U2001': (130, 49), 'U2002': (130, 41), 'U501': (100, 74)}   # keep SoC->M.2 lane corridor for the muxes
for ref in ORDER:
    place_ic(ref, TARGET.get(ref) or target_of(ref), HALO.get(ref, 1.5), 1.0 if ref in TARGET else 0.1)
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
def target_for(ref, defer):
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
    if rail:
        bigs = [(r, j) for r, j in pool if not is_small(fps[r])] or pool
        r, j = min(bigs, key=lambda t: (load[t], t[1]))
    else:
        r, j = min(pool, key=lambda t: (is_small(fps[t[0]]), t[1]))
    load[(r, j)] += 1
    return i, pad_abs(r, j)
def place_small(ref, own_pad, tgt):
    f = fps[ref]; best = None; c = tgt
    if block[ref]:   # start the search inside the part's own block
        c = min(((min(max(tgt[0], b[0]+3), b[2]-3), min(max(tgt[1], b[1]+3), b[3]-3)) for b in BLOCKS[block[ref]][1]),
                key=lambda q: math.dist(q, tgt))
    c = (round(c[0] / SNAP) * SNAP, round(c[1] / SNAP) * SNAP)
    base = math.dist(c, tgt)
    for offs in (OFF_FINE, OFF_COARSE):
        for du, dv in offs:
            if best and math.hypot(du, dv) > best[0] - base + 2.0: break
            u, v = c[0] + du, c[1] + dv
            for r in (0, 90, 180, 270):
                R = rect(f, u, v, r, GAP/2)
                if not legal(ref, R): continue
                a = pad_abs(ref, own_pad, (u, v, r))
                sc = math.hypot(a[0]-tgt[0], a[1]-tgt[1]) + (0.15 if r >= 180 else 0)   # prefer 0/90 for tidy silk
                if best is None or sc < best[0]: best = (sc, u, v, r, R)
        if best: break
    if best is None: return False
    commit(ref, *best[1:4], best[4]); return True
def prio(ref):
    k = 0 if ref.startswith('L') else 1 if ref.startswith('C') else 2 if ref.startswith(('R', 'FB')) else 3
    return (k, val(fps[ref]) if k == 1 else 0, ref)
pending = sorted([r for r in fps if r not in placed], key=prio)
for it in range(16):
    nxt = []
    for ref in pending:
        t = target_for(ref, defer=it < 8)
        if t is None: nxt.append(ref)
        elif not place_small(ref, *t): raise SystemExit(f'no room for {ref} ({block[ref]})')
    if not nxt or (nxt == pending and it >= 8): pending = nxt; break
    pending = sorted(nxt, key=prio)
for ref in pending:
    if not place_small(ref, 0, target_of(ref)): raise SystemExit(f'no room for {ref}')

# ============================================================== trim outline to the parts
ext = [rect(fps[r], *placed[r]) for r in placed if r not in OVERHANG]
TW = min(W, math.ceil(max(max(R[2] for R in ext), CARD[2]) + 0.5))
TH = min(H, math.ceil(max(R[3] for R in ext) + 0.5))
print(f'placed {len(placed)}/{len(fps)}  outline {TW} x {TH} mm')

# ============================================================== write back (pose + absolute pad/text angles)
out = []; last = 0
for ref, f in sorted(fps.items(), key=lambda kv: kv[1]['span'][0]):
    a, b = f['span']; t = s[a:b]
    u, v, r = placed[ref]
    t = re.sub(r'\(translate [-\d.]+ [-\d.]+\)', f'(translate {X0+u:.4f} {Y0+v:.4f})', t, count=1)
    t = re.sub(r'\(rotate [-\d.]+\)', f'(rotate {r % 360:g})', t, count=1)
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
