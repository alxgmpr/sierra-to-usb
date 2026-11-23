"""Read footprint poses from a KiCad 10.99 board and write new ones back (text level, unrouted boards).

parse(s) -> {ref: footprint info}; footprints on B.Cu are stored in their unflipped (top-side) shape.
repose(t, f, u, v, r, side) -> footprint text moved to board-local (u, v), rotation r, side 'F' or 'B'.
Board-local coordinates have their origin at the outline's top-left corner (X0, Y0).

usage: uv run python hardware/tools/board_pose.py BOARD POSES.json
       POSES = {"REF": [u, v, rot] or [u, v, rot, "F"|"B"], ...}; the board is rewritten in place.
"""
import json, math, re, sys
X0, Y0 = 333.8, 38.05   # outline top-left in KiCad board coordinates

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


def repose(t, f, u, v, r, side):
    """Footprint text `t` (parsed as `f`) at board-local (u, v), rotation r, on side 'F' or 'B'.
    Pad and text (at) angles are absolute in the file, so a rotation adds its delta to all of them;
    a flip mirrors local y, swaps F/B layers, mirrors text and reflects the angles."""
    ref = f['ref']
    t = re.sub(r'\(translate [-\d.]+ [-\d.]+\)', f'(translate {X0+u:.4f} {Y0+v:.4f})', t, count=1)
    t = re.sub(r'\(rotate [-\d.]+\)', f'(rotate {r % 360:g})', t, count=1)
    if side != f['side']:
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
    return t


def write(s, fps, poses):
    """Board text with every ref in `poses` ({ref: (u, v, r, side)}) moved; other footprints untouched."""
    out = []; last = 0
    for ref, f in sorted(fps.items(), key=lambda kv: kv[1]['span'][0]):
        if ref not in poses: continue
        a, b = f['span']
        out.append(s[last:a]); out.append(repose(s[a:b], f, *poses[ref])); last = b
    out.append(s[last:])
    return ''.join(out)


if __name__ == '__main__':
    path = sys.argv[1]; s = open(path).read(); fps = parse(s)
    poses = {ref: (p[0], p[1], p[2], p[3] if len(p) > 3 else fps[ref]['side']) for ref, p in json.load(open(sys.argv[2])).items()}
    missing = set(poses) - set(fps); assert not missing, missing
    open(path, 'w').write(write(s, fps, poses)); print(f'moved {len(poses)} footprints')
