"""Small deterministic KiCad capture helpers; symbols retain native pin identities."""
from pathlib import Path
import math
import re
import uuid

ROOT = Path(__file__).resolve().parents[1]
LIB = Path('/Applications/KiCad/KiCad.app/Contents/SharedSupport/symbols')


def block(text, start):
    depth = 0
    quoted = escaped = False
    for i in range(start, len(text)):
        c = text[i]
        if escaped:
            escaped = False
            continue
        if quoted and c == '\\':
            escaped = True
            continue
        if c == '"':
            quoted = not quoted
        if not quoted:
            depth += (c == '(') - (c == ')')
            if depth == 0:
                return text[start:i + 1]
    raise ValueError('Unbalanced KiCad expression')


def children(text):
    """Yield immediate children without confusing instances and embedded symbols."""
    position = re.match(r'\([^\s()]+', text).end()
    while position < len(text) - 1:
        if text[position] == '(':
            item = block(text, position)
            yield item
            position += len(item)
        else:
            position += 1


def quote(value):
    return str(value).replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n')


def prop(name, value, x, y, hidden=False):
    return f'(property "{name}" "{quote(value)}" (at {x} {y} 0) (effects (font (size 1.27 1.27))' + (' (hide yes)' if hidden else '') + '))'


def stock(library, name):
    text = (LIB / f'{library}.kicad_sym').read_text()
    body = block(text, text.index(f'(symbol "{name}"'))
    if '(extends ' in body:
        parent = re.search(r'\(extends "([^"]+)"\)', body)[1]
        resolved = stock(library, parent).replace(f'{library}:{parent}', f'{library}:{name}').replace(f'"{parent}_', f'"{name}_')
        for m in re.finditer(r'\(property "([^"]+)"', body):
            child_prop = block(body, m.start())
            existing = re.search(r'\(property "'+re.escape(m[1])+r'"', resolved)
            if existing:
                resolved = resolved.replace(block(resolved,existing.start()), child_prop, 1)
            else:
                resolved = resolved[:-1]+child_prop+')'
        return resolved
    return body.replace(f'(symbol "{name}"', f'(symbol "{library}:{name}"', 1)


def native_pins(path, name):
    text = Path(path).read_text()
    body = block(text, text.index(f'(symbol "{name}"'))
    pairs = re.findall(r'\(pin \w+ \w+.*?\(name "([^"]+)".*?\(number "([^"]+)"', body, re.S)
    assert len(pairs) == len({n for _, n in pairs})
    return {number: name for name, number in pairs}


def grouped(name, pins, units, roles):
    """Place top supply pins, bottom grounds, left inputs and right outputs."""
    result = [f'(symbol "{name}" (pin_names (offset 0.508)) (in_bom yes) (on_board yes)', prop('Reference', 'U', 0, 5.08), prop('Value', name, 0, 2.54)]
    seen = set()
    for unit, sides in enumerate(units, 1):
        maximum = max(len(sides.get('left', [])), len(sides.get('right', [])), 4)
        half_height = math.ceil((maximum + 2) / 2) * 2.54
        half_width = max(17.78, math.ceil(max(len(sides.get('top', [])), len(sides.get('bottom', []))) / 2) * 2.54)
        result.append(f'(symbol "{name}_{unit}_1" (rectangle (start {-half_width} {half_height}) (end {half_width} {-half_height}) (stroke (width 0.254) (type default)) (fill (type background))))')
        body = []
        for side in ['left', 'right', 'top', 'bottom']:
            numbers = sides.get(side, [])
            for i, number in enumerate(numbers):
                assert number not in seen and number in pins
                seen.add(number)
                offset = (i - (len(numbers) - 1) // 2) * 2.54
                if side in ['left', 'right']:
                    x = (-1 if side == 'left' else 1) * (half_width + 5.08)
                    y = -offset
                    angle = 0 if side == 'left' else 180
                else:
                    x = offset
                    y = (1 if side == 'top' else -1) * (half_height + 5.08)
                    angle = 270 if side == 'top' else 90
                body.append(f'(pin {roles[number]} line (at {x} {y} {angle}) (length 5.08) (name "{quote(pins[number])}" (effects (font (size 1.27 1.27)))) (number "{number}" (effects (font (size 1.27 1.27)))))')
        result.append(f'(symbol "{name}_{unit}_0" {"".join(body)})')
    assert seen == set(pins), (name, set(pins) - seen)
    result.append(')')
    return ''.join(result)


class Sheet:
    def __init__(self, name, title, paper='A3'):
        self.name, self.title, self.paper = name, title, paper
        self.root = self.uid('root')
        self.items = []
        self.library = {}
        self.references = set()

    def uid(self, key):
        return str(uuid.uuid5(uuid.NAMESPACE_URL, f'sierra-{self.name}-{key}'))

    def wire(self, a, b):
        if a == b:
            return
        item = f'(wire (pts (xy {a[0]} {a[1]}) (xy {b[0]} {b[1]})) (stroke (width 0) (type default)) (uuid "{self.uid("wire-" + str((a,b)))}"))'
        if item not in self.items:
            self.items.append(item)

    def net(self, name, point, angle=0):
        self.items.append(f'(global_label "{name}" (shape passive) (at {point[0]} {point[1]} {angle}) (effects (font (size 1.27 1.27)) (justify {"right" if angle == 0 else "left"})) (uuid "{self.uid("net-" + name + str(point))}"))')

    def nc(self, point):
        self.items.append(f'(no_connect (at {point[0]} {point[1]}) (uuid "{self.uid("nc-"+str(point))}"))')

    def note(self, text, x, y):
        self.items.append(f'(text "{quote(text)}" (at {x} {y} 0) (effects (font (size 1.27 1.27)) (justify left)) (uuid "{self.uid("note-" + text)}"))')

    def rectangle(self, title, x, y, w, h):
        self.items.append(f'(rectangle (start {x} {y}) (end {x+w} {y+h}) (stroke (width 0.254) (type default)) (fill (color 0 0 0 0)) (uuid "{self.uid("box-"+title)}"))')
        self.note(title, x+2.54, y+3.81)

    def symbol(self, lib_id, body, reference, value, x, y, footprint='', fields=None, unit=1, angle=0):
        self.library[lib_id] = body.replace(re.search(r'^\(symbol "([^"]+)"', body)[0], f'(symbol "{lib_id}"', 1)
        assert (reference, unit) not in self.references
        self.references.add((reference, unit))
        self.items.append(f'(symbol (lib_id "{lib_id}") (at {x} {y} {angle}) (unit {unit}) (in_bom {'no' if reference.startswith('#') else 'yes'}) (on_board {'no' if reference.startswith('#') else 'yes'}) (dnp no) (uuid "{self.uid(reference+str(unit))}") ' + prop('Reference', reference, x, y-27.94) + prop('Value', value, x, y-25.4) + prop('Footprint', footprint, x, y, True) + ''.join(prop(k, v, x, y, True) for k, v in (fields or {}).items()) + f'(instances (project "{self.name}" (path "/{self.root}" (reference "{reference}") (unit {unit})))))')
        points = {}
        radians = math.radians(angle)
        for pin in re.finditer(r'\(pin \w+ \w+', body):
            b = block(body, pin.start())
            child = body[:pin.start()].rsplit('(symbol "',1)[-1].split('"',1)[0]
            if not any(f'_{u}_' in child for u in [0,unit]):
                continue
            px, py, a = map(float, re.search(r'\(at ([-\d.]+) ([-\d.]+) ([-\d.]+)\)', b).groups())
            number = re.search(r'\(number "([^"]+)"', b)[1]
            points[number] = (round(x+px*math.cos(radians)-py*math.sin(radians), 4), round(y-px*math.sin(radians)-py*math.cos(radians), 4), (a+angle)%360)
        if reference.startswith('#'):
            self.items[-1] = self.items[-1].replace(prop('Reference',reference,x,y-27.94),prop('Reference',reference,x,y,True)).replace(prop('Value',value,x,y-25.4),prop('Value',value,x,y-3.81))
        if not angle and reference.startswith(('U','Y','J','T')) and points:
            top = min(p[1] for p in points.values()) - 17.78
            self.items[-1] = self.items[-1].replace(prop('Reference',reference,x,y-27.94),prop('Reference',reference,x,top-2.54)).replace(prop('Value',value,x,y-25.4),prop('Value',value,x,top))
        return points

    def attach(self, pins, nets):
        buses = {}
        for number, net in nets.items():
            if net is not None and pins[number][2] in {90,270}:
                buses.setdefault((net,pins[number][2]),[]).append(number)
        bussed = set()
        for (net,angle), numbers in buses.items():
            if len(numbers) < 2:
                continue
            low = min(pins[n][0] for n in numbers)
            high = max(pins[n][0] for n in numbers)
            interspersed = [n for n in nets if n not in numbers and pins[n][2] == angle and low <= pins[n][0] <= high]
            assert not interspersed, (self.name, net, "bus would short another pin", interspersed)
            endpoints = []
            for number in numbers:
                x,y,_ = pins[number]
                end = (x,round(y + (-10.16 if angle == 270 else 10.16),4))
                self.wire((x,y),end)
                endpoints.append(end)
                bussed.add(number)
            endpoints.sort()
            for a,b in zip(endpoints,endpoints[1:]):
                self.wire(a,b)
            self.net(net,endpoints[0])
        for number, net in nets.items():
            if number in bussed:
                continue
            x, y, angle = pins[number]
            if net is None:
                self.nc((x, y))
                continue
            # Extend away from the body in the reverse of the pin direction.
            radians = math.radians(angle)
            end = (round(x-10.16*math.cos(radians), 4), round(y+10.16*math.sin(radians), 4))
            self.wire((x,y), end)
            self.net(net, end, 0 if end[0] <= x else 180)

    def passive(self, kind, ref, value, x, y, first, second, mpn, footprint, manufacturer, fields=None, horizontal=False):
        name = {'R':'R_Small_US','C':'C_Small','L':'L_Small','FB':'FerriteBead_Small'}[kind]
        extra = {'MPN':mpn, 'Manufacturer':manufacturer, **(fields or {})}
        pins = self.symbol('Device:'+name, stock('Device',name), ref, value, x, y, footprint, extra, angle=90 if horizontal else 0)
        # Place passive properties beside the body, not at IC title height.
        self.items[-1] = self.items[-1].replace(prop('Reference',ref,x,y-27.94), prop('Reference',ref,x if horizontal else x+8.89,y-7.62 if horizontal else y-1.27)).replace(prop('Value',value,x,y-25.4), prop('Value',value,x if horizontal else x+8.89,y-5.08 if horizontal else y+1.27))
        if horizontal:
            for field in ['Reference','Value']:
                match = re.search(r'\(property "'+field+r'"',self.items[-1])
                original = block(self.items[-1],match.start())
                self.items[-1] = self.items[-1].replace(original,re.sub(r'(\(at [^()]+) 0\)',r'\1 90)',original,count=1))
        self.attach(pins, {'1':first,'2':second})
        return pins

    def cap(self, ref, value, x, y, rail):
        parts = {'100nF':('CL10B104KA8NNNC','C_0603_1608Metric'),'1uF':('CL10B105KA8NNNC','C_0603_1608Metric'),'4.7uF':('CL10A475KA8NQNC','C_0603_1608Metric'),'10uF':('CL31B106KAHNNNE','C_1206_3216Metric'),'22uF':('CL32B226KAJNNNE','C_1210_3225Metric')}
        mpn, fp = parts[value]
        return self.passive('C',ref,value,x,y,rail,'GND',mpn,'Capacitor_SMD:'+fp,'Samsung Electro-Mechanics', {'Voltage Rating':'25V'})

    def resistor(self, ref, value, x, y, first, second, mpn, horizontal=False):
        return self.passive('R',ref,value,x,y,first,second,mpn,'Resistor_SMD:R_0603_1608Metric','Yageo', {'Tolerance':'1%','Power Rating':'0.1W'}, horizontal)

    def flag(self, reference, net, x, y, source):
        pins = self.symbol('power:PWR_FLAG',stock('power','PWR_FLAG'),reference,'PWR_FLAG',x,y,fields={'Power Source':source})
        self.attach(pins,{'1':net})

    def save(self):
        text = f'(kicad_sch (version 20250114) (generator eeschema) (uuid "{self.root}") (paper "{self.paper}") (title_block (title "{self.title}") (date "2026-10-07")) (lib_symbols {"".join(self.library.values())}) {"".join(self.items)})\n'
        assert block(text, 0) == text.strip()
        (ROOT / f'{self.name}.kicad_sch').write_text(text)


def register(symbols):
    (ROOT / 'Appliance.kicad_sym').write_text('(kicad_symbol_lib (version 20260830) (generator eeschema) ' + ''.join(symbols) + ')\n')
    path = ROOT / 'sym-lib-table'
    text = path.read_text()
    if '(name "Appliance")' not in text:
        path.write_text(text.rstrip()[:-1] + ' (lib (name "Appliance") (type "KiCad") (uri "${KIPRJMOD}/Appliance.kicad_sym") (options "") (descr "Manufacturer and native-pin audited appliance symbols")))\n')
