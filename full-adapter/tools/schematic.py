"""Small deterministic KiCad schematic writer; inspect CLI plots and exported nets."""
from pathlib import Path
import copy
import json
import math
import uuid
import sexpdata as sx

ROOT = Path(__file__).resolve().parents[1]
STD = Path('/Applications/KiCad/KiCad.app/Contents/SharedSupport/symbols')
Q = lambda value: json.dumps(str(value), ensure_ascii=False)

def uid(key): return str(uuid.uuid5(uuid.NAMESPACE_URL, 'sierra-full-adapter/' + key))
def nodes(n, tag): return [v for v in n if isinstance(v, list) and str(v[0]) == tag]
def one(n, tag): return nodes(n, tag)[0]
def effects(size=1.27, justify=''):
    return f'(effects (font (size {size} {size}))' + (f' (justify {justify})' if justify else '') + ')'
ROOT_ID = uid('full-adapter-root')


class Sheet:
    def __init__(self, name, title, root=False):
        self.name, self.title = name, title
        self.id = ROOT_ID if root else uid(name)
        self.path = '/' + ROOT_ID + ('' if root else '/' + uid('sheet-block/' + name))
        self.items, self.libs, self.pins, self.intent = [], {}, {}, {}
        self.power_count = 0

    def library(self, name):
        if name in self.libs: return self.libs[name]
        prefix, part = name.split(':')
        path = ROOT / 'lib/full-adapter.kicad_sym' if prefix == 'full-adapter' else STD / (prefix + '.kicad_sym')
        lib = sx.loads(path.read_text())
        symbol = copy.deepcopy(next(s for s in nodes(lib, 'symbol') if s[1] == part))
        assert not nodes(symbol, 'extends'), 'Resolve inherited symbol before use: ' + name
        symbol[1] = name
        self.libs[name] = symbol
        return symbol

    def place(self, name, ref, x, y, unit=1, value=None, angle=0, fields=None, dnp=False):
        symbol = self.library(name)
        defaults = {p[1]: p[2] for p in nodes(symbol, 'property')}
        value = defaults['Value'] if value is None else value
        properties = {'Reference': ref, 'Value': value,
                      **{k: v for k, v in defaults.items() if k not in {'Reference', 'Value', 'ki_fp_filters', 'ki_keywords'}},
                      **(fields or {})}
        subunits = [s for s in nodes(symbol, 'symbol') if int(s[1].rsplit('_', 2)[1]) in (0, unit)]
        pins = [p for s in subunits for p in nodes(s, 'pin')]
        body = [r for s in subunits for r in nodes(s, 'rectangle')]
        height = max([abs(one(r, 'start')[2]) for r in body] + [0])
        custom = name.startswith('full-adapter:') and not nodes(symbol, 'power')
        pp = []
        for i, (key, val) in enumerate(properties.items()):
            if custom:
                extra = 20.32 if any(one(p,'at')[3] == 270 for p in pins) else 7.62
                px, py, justify = x, y-height-extra+i*2.54, ''
            else:
                px, py, justify = (x, y-6.35+i*2.54, '') if angle in (90,270) else (x+2.54, y-1.27+i*2.54, 'left')
            if name.startswith('power:') or nodes(symbol, 'power'):
                px, py, justify = x, y+(5.08 if value == 'GND' else -5.08), ''
            hidden = i > 1 or key == 'Reference' and (name.startswith('power:') or nodes(symbol, 'power'))
            pp.append(f'(property {Q(key)} {Q(val)} (at {px} {py} {angle if not custom else 0}) {effects(justify=justify)}' + (' (hide yes)' if hidden else '') + ')')
        sid = uid(self.name + '/' + ref + '/' + str(unit))
        bom = 'no' if ref.startswith('#') or name == 'Device:NetTie_2' else 'yes'
        on_board = 'no' if ref.startswith('#') else 'yes'
        self.items.append(f'(symbol (lib_id {Q(name)}) (at {x} {y} {angle}) (unit {unit}) (in_bom {bom}) (on_board {on_board}) (dnp {"yes" if dnp else "no"}) (uuid {Q(sid)}) ' + '\n'.join(pp) + '\n' +
            '\n'.join(f'(pin {Q(one(p,"number")[1])} (uuid {Q(uid(sid+one(p,"number")[1]))}))' for p in pins) +
            f'(instances (project "full-adapter" (path {Q(self.path)} (reference {Q(ref)}) (unit {unit})))))')
        result = {}
        for p in pins:
            px, py, pa = one(p, 'at')[1:]
            r = math.radians(angle)
            pos = (round(x+px*math.cos(r)-py*math.sin(r), 6), round(y-px*math.sin(r)-py*math.cos(r), 6), (pa+angle)%360)
            num = one(p, 'number')[1]
            result[num] = pos
            self.pins[ref, num] = pos
        return result

    def wire(self, a, b):
        a, b = tuple(round(v,6) for v in a[:2]), tuple(round(v,6) for v in b[:2])
        if a == b: return
        assert a[0] == b[0] or a[1] == b[1], (a,b)
        self.items.append(f'(wire (pts (xy {a[0]} {a[1]}) (xy {b[0]} {b[1]})) (stroke (width 0) (type default)) (uuid {Q(uid(self.name+"/wire/"+str(a)+str(b)))}))')

    def junction(self, p):
        self.items.append(f'(junction (at {p[0]} {p[1]}) (diameter 0) (color 0 0 0 0) (uuid {Q(uid(self.name+"/junction/"+str(p)))}))')

    def label(self, name, p, angle=0, global_net=False):
        kind = 'global_label' if global_net else 'label'
        extra = '(shape bidirectional)' if global_net else ''
        self.items.append(f'({kind} {Q(name)} (at {p[0]} {p[1]} {angle}) {extra} {effects(justify="left bottom" if angle == 0 else "right bottom")} (uuid {Q(uid(self.name+"/label/"+name+str(p)))}))')

    def connect(self, ref, pin, net, length=5.08, global_net=False):
        p = self.pins[ref, str(pin)]
        if net is None:
            self.items.append(f'(no_connect (at {p[0]} {p[1]}) (uuid {Q(uid(self.name+"/nc/"+ref+str(pin)))}))')
            return
        angle = math.radians(p[2])
        end = (round(p[0]-length*math.cos(angle),6), round(p[1]+length*math.sin(angle),6))
        self.wire(p,end)
        self.label(net,end,180 if p[2] == 0 else 0,global_net)
        self.intent.setdefault(net, []).append([ref,str(pin)])
        return end

    def power(self, net, p):
        self.power_count += 1
        name = 'power:GND' if net == 'GND' else 'full-adapter:' + net
        self.place(name, f'#PWR{self.name.replace("-", "")}{self.power_count:03}', *p)

    def text(self, text, x, y, size=1.27):
        self.items.append(f'(text {Q(text)} (at {x} {y} 0) {effects(size,"left top")} (uuid {Q(uid(self.name+"/text/"+text))}))')

    def box(self, title, x, y, w, h):
        self.items.append(f'(rectangle (start {x} {y}) (end {x+w} {y+h}) (stroke (width 0.254) (type default) (color 60 110 145 1)) (fill (type none)) (uuid {Q(uid(self.name+"/box/"+title))}))')
        self.text(title,x+3.81,y+3.81,1.8)

    def save(self, paper='A3'):
        path = ROOT / 'cad' / (self.name + '.kicad_sch')
        path.write_text(f'(kicad_sch (version 20250114) (generator "full_adapter_schematic") (uuid {Q(self.id)}) (paper {Q(paper)})\n(title_block (title {Q(self.title)}) (rev "WORK IN PROGRESS") (company "Integrated modem development board"))\n(lib_symbols ' + '\n'.join(sx.dumps(s) for s in self.libs.values()) + ')\n' + '\n'.join(self.items) + '\n)\n')
        return path
