"""Netlist-driven floorplan placement for hardware/appliance.kicad_pcb (top side only).

Phases: fixed anchors -> barrier parts on the PoE isolation line -> other ICs by
ratsnest minimisation -> small parts packed next to the pad they serve.
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
        for cm in re.finditer(r'\((fp_line|fp_rect|fp_poly|fp_circle|fp_arc)(.*?)\(layer "F\.CrtYd"\)',t,re.S):
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
def xf(fp,x,y,rot=None,cx=None,cy=None):
    r=math.radians(fp['rot'] if rot is None else rot)
    cx=fp['x'] if cx is None else cx; cy=fp['y'] if cy is None else cy
    # KiCad: y down, rotation CCW on screen => x' = x cos + y sin ; y' = -x sin + y cos
    return cx+x*math.cos(r)+y*math.sin(r), cy-x*math.sin(r)+y*math.cos(r)


SRC, DST = sys.argv[1], sys.argv[2]   # input board, output board
s = open(SRC).read()
fps = parse(s)
X0, Y0, W, H = 333.8, 38.05, 172.1, 185.3
VB = 44.0            # PoE isolation boundary (board-local v), for u < UB
UB = 100.0
MOAT = 1.25          # half of the 2.5 mm moat
GAP = 0.1            # courtyard spacing

def short(n): return re.sub(r'^/.*/', '', n)
# ---------------------------------------------------------------- anchors (u, v, rot)
ANCH = {
    'J1701': (88, 17.5, 180),   # RJ45, opening on top edge
    'T1701': (88, VB, 0),       # cable side up, PHY side down
    'T1702': (32, VB, 270),     # flyback: primary up, secondary down
    'U1301': (88, 61, 90),      # NIC, MDI side up
    'U801':  (82, 112, 0),      # RK3566
    'J2001': (126, 112, 90),    # M.2, card extends to +u
    'J1711': (5.5, 70, 90),     # ISO_12V terminal, left edge
    'J1712': (4, 84, 90),
    'U701':  (16, 82, 0), 'U1901': (140, 78, 0), 'U401': (44, 78, 0), 'U601': (18, 112, 0),
    'U201':  (40, 162, 0),
    'J101': (6, 182, 90), 'J102': (16, 182, 90), 'J201': (46, 182, 90), 'J202': (66, 182, 90),
    'SW201': (84, 180, 0), 'SW801': (96, 180, 0), 'SW802': (108, 180, 0),
    'J1201': (124, 182, 0), 'J1202': (140, 181, 90),
    'J2002': (145, 140, 0),
}
CARD = (127.5, 96.5, 171.5, 127.5)   # M.2 3042/3052 card footprint keep-out
BARRIER = {'T1701', 'T1702', 'U1703', 'U1801', 'U1802', 'U1803'}

# ---------------------------------------------------------------- nets
netpads = defaultdict(list)
for f in fps.values():
    for i, p in enumerate(f['pads']):
        if p['net'] and not p['net'].startswith('unconnected'):
            netpads[p['net']].append((f['ref'], i))
RAIL = {n for n, v in netpads.items() if len({r for r, _ in v}) > 8 or short(n) == 'GND'}
def is_small(f): return len(f['pads']) <= 3 or bool(re.match(r'^(C|R|FB|TP|L|D)\d', f['ref']))

# ---------------------------------------------------------------- PoE primary domain
prim_nets = {n for n in netpads if re.fullmatch(r'CABLE_MDI\d_[NP]|POE_PAIR\d+|POE_(VDD|VSS|RTN|VCIN|VCOUT|DEN|CLSA|CLSB|REF|UVLO|TPH|TPL|BT|AMPS_CTL)|CHASSIS', short(n))}
stop = {n for n in netpads if short(n) in ('GND', 'ISO_12V', '+3V3')}
changed = True
while changed:
    changed = False
    for f in fps.values():
        if f['ref'] in BARRIER: continue
        ns = {p['net'] for p in f['pads'] if p['net'] in netpads}
        if ns & prim_nets and not ns & stop:
            new = ns - prim_nets
            if new: prim_nets |= new; changed = True
domain = {}
for f in fps.values():
    ns = {p['net'] for p in f['pads'] if p['net'] in netpads}
    if f['ref'] in BARRIER: domain[f['ref']] = 'B'
    elif ns & prim_nets and ns & stop: domain[f['ref']] = 'B'
    elif ns & prim_nets: domain[f['ref']] = 'P'
    else: domain[f['ref']] = 'S'
for r, d in domain.items():
    if d == 'B' and r not in BARRIER: BARRIER.add(r)

# ---------------------------------------------------------------- geometry
def rot_pt(x, y, r):
    a = math.radians(r); return x*math.cos(a) + y*math.sin(a), -x*math.sin(a) + y*math.cos(a)
def rect(f, u, v, r, infl=0.0):
    x0, y0, x1, y1 = f['crt']; pts = [rot_pt(x, y, r) for x in (x0, x1) for y in (y0, y1)]
    return (u + min(p[0] for p in pts) - infl, v + min(p[1] for p in pts) - infl,
            u + max(p[0] for p in pts) + infl, v + max(p[1] for p in pts) + infl)
def pad_abs(ref, i, pos=None):
    f = fps[ref]; u, v, r = pos or placed[ref]; p = f['pads'][i]
    dx, dy = rot_pt(p['x'], p['y'], r); return u + dx, v + dy

CELL = 4.0
grid = defaultdict(list)
placed = {}
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
def legal(ref, R):
    if R[0] < 1.0 or R[1] < 1.0 or R[2] > W - 1.0 or R[3] > H - 1.0: return False
    d = domain[ref]
    in_prim_zone = R[0] < UB
    if d == 'P' and not (R[3] <= VB - MOAT and R[2] <= UB): return False
    if d == 'S' and in_prim_zone and R[1] < VB + MOAT: return False
    if d != 'B' and R[0] < CARD[2] and CARD[0] < R[2] and R[1] < CARD[3] and CARD[1] < R[3]: return False
    return not collide(R)

# ---------------------------------------------------------------- phase 1: anchors
HALO = {'U801': 3.5, 'U901': 2.5, 'U1101': 2.0, 'U501': 2.5, 'U1301': 2.0}
for ref, (u, v, r) in list(ANCH.items()):
    R = rect(fps[ref], u, v, r)
    u += max(0, 1.0 - R[0]) - max(0, R[2] - (W - 1.0)); v += max(0, 1.0 - R[1]) - max(0, R[3] - (H - 1.0))
    ANCH[ref] = (u, v, r)
    commit(ref, u, v, r, rect(fps[ref], u, v, r, GAP + HALO.get(ref, 0)))

# ---------------------------------------------------------------- scoring helpers
def ratsnest(ref, pos, rails=False):
    f = fps[ref]; tot = 0.0; n = 0
    for i, p in enumerate(f['pads']):
        net = p['net']
        if net not in netpads or (net in RAIL and not rails): continue
        best = None
        for r2, j in netpads[net]:
            if r2 == ref or r2 not in placed: continue
            a = pad_abs(ref, i, pos); b = pad_abs(r2, j)
            d = math.hypot(a[0]-b[0], a[1]-b[1]) * (1.0 if fps[r2]['sheet'] == f['sheet'] else 0.25)
            best = d if best is None else min(best, d)
        if best is not None: tot += best; n += 1
    return tot, n
def neighbours(ref):
    out = set()
    for p in fps[ref]['pads']:
        if p['net'] in netpads and p['net'] not in RAIL:
            out |= {r for r, _ in netpads[p['net']]}
    out.discard(ref); return out

def offsets(rmax, step):
    k = int(rmax/step); o = [(i*step, j*step) for i in range(-k, k+1) for j in range(-k, k+1) if (i*i+j*j)*step*step <= rmax*rmax]
    return sorted(o, key=lambda t: t[0]**2 + t[1]**2)
OFF_FINE = offsets(14, 0.25); OFF_COARSE = offsets(70, 1.0)

DW = 0.05
def place_ic(ref, target, rmax=45, step=1.0, halo=0.0):
    best = None
    for du, dv in offsets(rmax, step):
        u, v = target[0] + du, target[1] + dv
        for r in (0, 90, 180, 270):
            R = rect(fps[ref], u, v, r, GAP + halo)
            if not legal(ref, R): continue
            sc, n = ratsnest(ref, (u, v, r))
            sc += DW * math.hypot(du, dv)
            if best is None or sc < best[0]: best = (sc, u, v, r, R)
    if best is None:
        print('no spot', ref, domain[ref], [round(x,1) for x in rect(fps[ref],0,0,0)], {r: [round(x) for x in placed[r]] for r in placed if domain[r] in 'PB'}); raise SystemExit
    commit(ref, *best[1:4], best[4]); return best

# ---------------------------------------------------------------- phase 2: barrier parts on the boundary
for ref in sorted(BARRIER - set(ANCH), key=lambda r: -len(fps[r]['pads'])):
    f = fps[ref]; best = None
    nb = [r for r in neighbours(ref) if r in placed]
    cu = sum(placed[r][0] for r in nb)/len(nb) if nb else 50
    for u in [x*0.5 for x in range(4, int(UB*2) - 4)]:
        for r in (0, 90, 180, 270):
            # primary pads must sit above the line, secondary below
            ok = True
            for p in f['pads']:
                if p['net'] not in netpads: continue
                y = rot_pt(p['x'], p['y'], r)[1]
                if p['net'] in prim_nets and y > -0.2: ok = False
                if p['net'] not in prim_nets and y < 0.2: ok = False
            if not ok: continue
            R = rect(f, u, VB, r, GAP)
            if not legal(ref, R): continue
            sc = abs(u - cu)
            if best is None or sc < best[0]: best = (sc, u, r, R)
    if best is None: print('barrier unplaced', ref); continue
    commit(ref, best[1], VB, best[2], best[3])

# ---------------------------------------------------------------- phase 3: remaining big parts by ratsnest
ICS = ['U901', 'U1101', 'U501', 'U1001', 'U2001', 'U2002', 'U1604', 'U1701', 'U1702', 'Q1705', 'U1302', 'Y1301', 'U1503', 'U902']
def big_order():
    rest = [r for r, f in fps.items() if r not in placed and not is_small(f)]
    return rest
for ref in ICS:
    nb = [r for r in neighbours(ref) if r in placed]
    nb = [r for r in nb if fps[r]['sheet'] == fps[ref]['sheet']] or [r for r in placed if fps[r]['sheet'] == fps[ref]['sheet']] or nb
    if not nb: nb = [r for r in placed if fps[r]['sheet'] == fps[ref]['sheet']] or list(placed)
    tgt = (sum(placed[r][0] for r in nb)/len(nb), sum(placed[r][1] for r in nb)/len(nb))
    place_ic(ref, tgt, halo=HALO.get(ref, 0.8))
while True:
    rest = [r for r in big_order()]
    if not rest: break
    rest.sort(key=lambda r: -len([n for n in neighbours(r) if n in placed]))
    ref = rest[0]
    nb = [r for r in neighbours(ref) if r in placed]
    nb = [r for r in nb if fps[r]['sheet'] == fps[ref]['sheet']] or [r for r in placed if fps[r]['sheet'] == fps[ref]['sheet']] or nb or list(placed)
    tgt = (sum(placed[r][0] for r in nb)/len(nb), sum(placed[r][1] for r in nb)/len(nb))
    DW = 0.5
    place_ic(ref, tgt, rmax=30, halo=0.8)

# Rebuild the grid with real (un-haloed) courtyards for passive packing.
grid.clear()
for ref, (u, v, r) in placed.items():
    for c in cells(rect(fps[ref], u, v, r, GAP)): grid[c].append(rect(fps[ref], u, v, r, GAP))

# ---------------------------------------------------------------- phase 4: small parts next to their pad
def val(f):
    m = re.match(r'([\d.]+)\s*([pnuµm]?)', f['val'])
    if not m: return 1.0
    return float(m[1]) * {'p': 1e-12, 'n': 1e-9, 'u': 1e-6, 'µ': 1e-6, 'm': 1e-3, '': 1}[m[2]]
load = defaultdict(int)
def target_for(ref, defer=False):
    f = fps[ref]; cands = []
    for i, p in enumerate(f['pads']):
        net = p['net']
        if net not in netpads or short(net) == 'GND': continue
        others = [(r, j) for r, j in netpads[net] if r != ref and r in placed and not re.match(r'^C\d', r)]
        if not others: others = [(r, j) for r, j in netpads[net] if r != ref and r in placed]
        if not others: continue
        same = [(r, j) for r, j in others if fps[r]['sheet'] == f['sheet']]
        if defer and not same and net not in RAIL and any(fps[r]['sheet'] == f['sheet'] and r not in placed and r != ref for r, _ in netpads[net]):
            return None
        pool = same or others
        rail = net in RAIL
        cands.append((rail, i, pool))
    if not cands: return None
    cands.sort(key=lambda c: c[0])        # signal nets first
    rail, i, pool = cands[0]
    if rail:
        bigs = [(r, j) for r, j in pool if not is_small(fps[r])] or pool
        r, j = min(bigs, key=lambda t: (load[t], t[1]))
    else:
        r, j = min(pool, key=lambda t: (is_small(fps[t[0]]), t[1]))
    load[(r, j)] += 1
    return i, pad_abs(r, j)

def place_small(ref, own_pad, tgt):
    f = fps[ref]; best = None
    for offs in (OFF_FINE, OFF_COARSE):
        for du, dv in offs:
            if best and math.hypot(du, dv) > best[0] + 2.0: break
            u, v = tgt[0] + du, tgt[1] + dv
            for r in (0, 90, 180, 270):
                R = rect(f, u, v, r, GAP)
                if not legal(ref, R): continue
                a = pad_abs(ref, own_pad, (u, v, r))
                sc = math.hypot(a[0]-tgt[0], a[1]-tgt[1])
                if best is None or sc < best[0]: best = (sc, u, v, r, R)
        if best: break
    if best is None: return False
    commit(ref, *best[1:4], best[4]); return True

def prio(ref):
    f = fps[ref]; k = 0 if ref.startswith('L') else 1 if ref.startswith('C') else 2 if ref.startswith(('R', 'FB')) else 3
    return (k, val(f) if k == 1 else 0, ref)
pending = sorted([r for r in fps if r not in placed], key=prio)
for it in range(16):
    nxt = []
    for ref in pending:
        t = target_for(ref, defer=it < 8)
        if t is None: nxt.append(ref); continue
        if not place_small(ref, *t): print('no room', ref)
    if not nxt or (nxt == pending and it >= 8): pending = nxt; break
    pending = sorted(nxt, key=prio)
for ref in pending:   # isolated parts: drop near their sheet-mates
    mates = [placed[r] for r in placed if fps[r]['sheet'] == fps[ref]['sheet']] or [(W/2, H/2, 0)]
    tgt = (sum(m[0] for m in mates)/len(mates), sum(m[1] for m in mates)/len(mates))
    place_small(ref, 0, tgt)

missing = [r for r in fps if r not in placed]
print('placed', len(placed), 'missing', missing)

# ---------------------------------------------------------------- write back (translate + rotate only)
out = []; last = 0
for ref, f in sorted(fps.items(), key=lambda kv: kv[1]['span'][0]):
    a, b = f['span']; t = s[a:b]
    if ref in placed:
        u, v, r = placed[ref]
        t = re.sub(r'\(translate [-\d.]+ [-\d.]+\)', f'(translate {X0+u:.4f} {Y0+v:.4f})', t, count=1)
        t = re.sub(r'\(rotate [-\d.]+\)', f'(rotate {r % 360:g})', t, count=1)
        delta = (r - f['rot']) % 360
        if delta:
            def fix(m):
                a = (float(m[3] or 0) + delta) % 360
                return f'(at {m[1]} {m[2]}' + (f' {a:g})' if a else ')')
            t = re.sub(r'\(at (-?[\d.]+) (-?[\d.]+)(?: (-?[\d.]+))?\)', fix, t)
    out.append(s[last:a]); out.append(t); last = b
out.append(s[last:])
open(DST, 'w').write(''.join(out))

print('domains', {d: sum(1 for x in domain.values() if x == d) for d in 'PSB'}, 'barrier', sorted(BARRIER))
