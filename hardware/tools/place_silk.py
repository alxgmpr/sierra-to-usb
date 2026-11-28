"""Put every silkscreen reference in a free spot next to its part, checked by KiCad DRC.

Passive-style refs (C/R/L/FB/TP/D/Q, <= 4 pads) go to the Fab layer like board_pose.repose does.
Every other ref tries spots above, below, left and right of its courtyard,
upright (0 or 90 degrees), clear of other courtyards, through-hole pads, other refs and the edge.
`kicad-cli pcb drc` is the judge: a spot it flags is banned and the board is re-solved.
Refs with no clean spot go to Fab and are listed.

usage: uv run python hardware/tools/place_silk.py BOARD      (rewrites BOARD in place)
"""
import json, math, re, subprocess, sys, tempfile, os
sys.path.insert(0, os.path.dirname(__file__))
import board_pose as bp

PASSIVE = re.compile(r'^(C|R|L|FB|TP|D|Q)\d')
SILK_RULES = {'silk_overlap', 'silk_over_copper', 'silk_edge_clearance'}
CH, TH = 0.9, 0.15      # stroke-font advance per char and thickness at size 1 mm (measured off a render)
EDGE = 0.5              # text to board edge
GAP = 0.15              # text to obstacles
# ponytail: courtyard AABBs as obstacles (not real silk/pad shapes); DRC catches what the boxes miss

def rot_pt(x, y, r):
    a = math.radians(r); return x*math.cos(a) + y*math.sin(a), -x*math.sin(a) + y*math.cos(a)

def ref_field(t):
    return re.search(r'(\(property "Reference" "[^"]*"\s*\(at )([-\d.]+) ([-\d.]+)(?: ([-\d.]+))?(\)\s*(?:\(unlocked yes\)\s*)?\(layer ")([FB])\.(SilkS|Fab)(")', t)

def geometry(s):
    fps = bp.parse(s)
    for f in fps.values():
        x0, y0, x1, y1 = f['crt']
        if f['side'] == 'B': y0, y1 = -y1, -y0          # parse stores B parts unflipped; file coords are flipped
        pts = [rot_pt(x, y, f['rot']) for x in (x0, x1) for y in (y0, y1)]
        f['box'] = (f['x'] + min(p[0] for p in pts), f['y'] + min(p[1] for p in pts),
                    f['x'] + max(p[0] for p in pts), f['y'] + max(p[1] for p in pts))
        f['padbox'] = []
        for p in f['pads']:
            py = -p['y'] if f['side'] == 'B' else p['y']
            dx, dy = rot_pt(p['x'], py, f['rot']); e = max(p['w'], p['h'])/2
            f['padbox'].append((f['x']+dx-e, f['y']+dy-e, f['x']+dx+e, f['y']+dy+e, p['kind']))
    return fps

def hit(a, b, g=0.0): return a[0] < b[2]+g and b[0] < a[2]+g and a[1] < b[3]+g and b[1] < a[3]+g

def candidates(f, n):
    w, h = n*CH + TH, 1.0 + TH
    x0, y0, x1, y1 = f['box']; cx, cy = (x0+x1)/2, (y0+y1)/2
    out = []
    for d in (0.1, 0.6):
        for sx in (0, -1, 1):            # centred, then slid to either end of the side
            for name, X, Y, ang in (('above', cx, y0-d-h/2, 0), ('below', cx, y1+d+h/2, 0)):
                X += sx*max(0, (x1-x0-w)/2); out.append((name, round(X, 3), round(Y, 3), ang))
            for name, X, Y, ang in (('left', x0-d-h/2, cy, 90), ('right', x1+d+h/2, cy, 90)):
                Y += sx*max(0, (y1-y0-w)/2); out.append((name, round(X, 3), round(Y, 3), ang))
    return out

def tbox(n, X, Y, ang):
    w, h = n*CH + TH, 1.0 + TH
    if ang == 90: w, h = h, w
    return (X-w/2, Y-h/2, X+w/2, Y+h/2)

def solve(fps, edge, bans):
    """Greedy, smallest parts first. Pass 1 keeps text off every other courtyard; pass 2 (for parts
    still unlabelled) only keeps it off pads, so it may sit on a neighbour's body if DRC allows."""
    W0, H0, W1, H1 = edge
    labels = sorted((r for r, f in fps.items() if f['label']),
                    key=lambda r: (fps[r]['box'][2]-fps[r]['box'][0])*(fps[r]['box'][3]-fps[r]['box'][1]))
    placed, texts = {}, {'F': [], 'B': []}
    for loose in (False, True):
        for ref in labels:
            if ref in placed: continue
            f = fps[ref]; S = f['side']; n = len(ref)
            for c in candidates(f, n):
                if c in bans.get(ref, ()): continue
                T = tbox(n, *c[1:])
                if not (T[0] >= W0+EDGE and T[1] >= H0+EDGE and T[2] <= W1-EDGE and T[3] <= H1-EDGE): continue
                if loose:
                    if any(hit(T, p, GAP) for o in fps.values() if o['side'] == S or o is f for p in o['padbox']): continue
                elif any(hit(T, o['box'], GAP) for r2, o in fps.items() if r2 != ref and o['side'] == S): continue
                if any(hit(T, p, GAP) for o in fps.values() if o['side'] != S for p in o['padbox'] if p[4] == 'thru_hole'): continue
                if any(hit(T, t, GAP) for t in texts[S]): continue
                placed[ref] = c; texts[S].append(T); break
    return placed

def apply(s, fps, placed):
    out, last = [], 0
    for ref, f in sorted(fps.items(), key=lambda kv: kv[1]['span'][0]):
        if not (f['label'] or f['tofab']): continue
        a, b = f['span']; t = s[a:b]; m = ref_field(t)
        if ref in placed:
            _, X, Y, ang = placed[ref]
            lx, ly = rot_pt(X - f['x'], Y - f['y'], -f['rot'])
            t = t[:m.start()] + f'{m[1]}{lx:.3f} {ly:.3f}' + (f' {ang:g}' if ang else '') + m[5] + m[6] + '.SilkS' + m[8] + t[m.end():]
        else:
            t = t[:m.start()] + m[1] + m[2] + ' ' + m[3] + (f' {m[4]}' if m[4] else '') + m[5] + m[6] + '.Fab' + m[8] + t[m.end():]
        out += [s[last:a], t]; last = b
    return ''.join(out + [s[last:]])

def flagged(path):
    with tempfile.TemporaryDirectory() as d:
        j = os.path.join(d, 'drc.json')
        subprocess.run(['kicad-cli', 'pcb', 'drc', '--format', 'json', '--severity-all', '-o', j, path], capture_output=True)
        v = json.load(open(j))['violations']
    bad = set()
    for x in v:
        if x['type'] in SILK_RULES:
            for i in x['items']:
                m = re.match(r'Reference field of (\S+)', i['description'])
                if m: bad.add(m[1])
    return bad, v

def main(path):
    s0 = open(path).read(); fps = geometry(s0)
    for ref, f in fps.items():
        m = ref_field(s0[f['span'][0]:f['span'][1]])
        on_silk = bool(m and m[7] == 'SilkS')
        f['tofab'] = on_silk and bool(PASSIVE.match(ref)) and len(f['pads']) <= 4
        f['label'] = on_silk and not f['tofab']
    e = re.search(r'\(gr_rect\s*\(start ([-\d.]+) ([-\d.]+)\)\s*\(end ([-\d.]+) ([-\d.]+)\)', s0)
    edge = tuple(map(float, e.groups()))
    bans = {}
    for rnd in range(15):
        placed = solve(fps, edge, bans)
        s = apply(s0, fps, placed); open(path, 'w').write(s)
        bad, v = flagged(path)
        bad &= set(placed)
        print(f'round {rnd}: {len(placed)} on silk, {len(bad)} flagged by DRC')
        if not bad: break
        for r in bad: bans.setdefault(r, set()).add(placed[r])
    else:
        placed = {r: c for r, c in placed.items() if r not in bad}
        open(path, 'w').write(apply(s0, fps, placed))
    print('passive refs to Fab:', ' '.join(sorted(r for r, f in fps.items() if f['tofab'])))
    print('no clean spot, to Fab:', ' '.join(sorted(r for r, f in fps.items() if f['label'] and r not in placed)))

if __name__ == '__main__':
    main(sys.argv[1])
