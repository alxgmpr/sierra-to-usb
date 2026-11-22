#!/usr/bin/env python3
"""Build and attach the 3D models that close the 2026-10-21 model holds.

Generated models are written in KiCad's footprint frame (X right, Y up = -footprint y,
Z up from the board, seating plane Z=0) and attach with zero offset/rotation. Vendor STEPs
get their datum transform baked in (kicad_trsf) and are rewritten flat with their colours.

usage: uv run --with cadquery python hardware/tools/build_models.py [--attach]
"""
import json, re, sys, tempfile
from math import pi
from pathlib import Path
import cadquery as cq
sys.path.insert(0, str(Path(__file__).parent))
from check_footprint_reviews import strip_models

HW = Path(__file__).resolve().parents[1]
ZERO = ((0, 0, 0), (0, 0, 0))   # (offset, rotate)


# ------------------------------------------------------------------ STEP I/O
# Every model is written as ONE flat product: placements baked into the geometry, no assembly tree,
# zero attach transform. Backplane's 3D tab mis-composes nested STEP placements and reads (rotate)
# with the opposite sign to KiCad; a flat zero-transform file renders the same in both. XCAF keeps the
# vendor colours (the plain STEPControl writer drops them and the part renders as one grey slab).
from OCP.BRepBuilderAPI import BRepBuilderAPI_Transform
from OCP.gp import gp_Trsf, gp_Ax1, gp_Pnt, gp_Dir, gp_Vec
from OCP.IFSelect import IFSelect_RetDone
from OCP.Interface import Interface_Static
from OCP.Quantity import Quantity_Color
from OCP.STEPCAFControl import STEPCAFControl_Reader, STEPCAFControl_Writer
from OCP.STEPControl import STEPControl_AsIs
from OCP.TCollection import TCollection_ExtendedString
from OCP.TDF import TDF_Label, TDF_LabelSequence
from OCP.TDocStd import TDocStd_Document
from OCP.TopAbs import TopAbs_FACE
from OCP.TopExp import TopExp_Explorer
from OCP.TopLoc import TopLoc_Location
from OCP.TopoDS import TopoDS_Compound
from OCP.BRep import BRep_Builder
from OCP.XCAFDoc import XCAFDoc_DocumentTool, XCAFDoc_ColorTool, XCAFDoc_ColorSurf, XCAFDoc_ColorGen


def xcaf_doc():
    return TDocStd_Document(TCollection_ExtendedString('MDTV-XCAF'))


def read_parts(path, trsf=None):
    """Flatten a STEP into [(shape, colour, [(face, colour)])] with every placement (and trsf) baked in."""
    doc = xcaf_doc(); r = STEPCAFControl_Reader(); r.SetColorMode(True)
    assert r.ReadFile(str(path)) == IFSelect_RetDone, path
    r.Transfer(doc)
    st = XCAFDoc_DocumentTool.ShapeTool_s(doc.Main()); ct = XCAFDoc_DocumentTool.ColorTool_s(doc.Main())
    def colour(label):
        for kind in (XCAFDoc_ColorSurf, XCAFDoc_ColorGen):
            c = Quantity_Color()
            if XCAFDoc_ColorTool.GetColor_s(label, kind, c): return c
    parts = []
    def walk(label, loc, inherited):
        if st.IsAssembly_s(label):
            comps = TDF_LabelSequence(); st.GetComponents_s(label, comps)
            for i in range(1, comps.Length() + 1):
                comp = comps.Value(i); ref = TDF_Label(); st.GetReferredShape_s(comp, ref)
                walk(ref, loc.Multiplied(st.GetLocation_s(comp)), colour(comp) or colour(ref) or inherited)
            return
        shape = st.GetShape_s(label); base = colour(label) or inherited
        subs = TDF_LabelSequence(); st.GetSubShapes_s(label, subs)
        coloured = [(st.GetShape_s(subs.Value(i)), colour(subs.Value(i))) for i in range(1, subs.Length() + 1)]
        coloured = [(s, c) for s, c in coloured if c]
        t = loc.Transformation() if trsf is None else trsf.Multiplied(loc.Transformation())
        mk = BRepBuilderAPI_Transform(shape, t, True)
        faces = []
        if coloured:
            ex = TopExp_Explorer(shape, TopAbs_FACE)
            while ex.More():
                f = ex.Current(); ex.Next()
                c = next((c for s, c in coloured if s.IsSame(f)), None)
                if c is None:   # colour set on the solid/shell that owns this face
                    c = next((c for s, c in coloured if s.ShapeType() != TopAbs_FACE and any_face(s, f)), None)
                if c is not None: faces.append((mk.ModifiedShape(f), c))
        parts.append((mk.Shape(), base, faces))
    free = TDF_LabelSequence(); st.GetFreeShapes(free)
    for i in range(1, free.Length() + 1):
        walk(free.Value(i), TopLoc_Location(), colour(free.Value(i)))
    return parts


def any_face(shape, face):
    ex = TopExp_Explorer(shape, TopAbs_FACE)
    while ex.More():
        if ex.Current().IsSame(face): return True
        ex.Next()
    return False


def write_parts(path, parts):
    """Write parts as a single flat, coloured STEP product."""
    comp = TopoDS_Compound(); bb = BRep_Builder(); bb.MakeCompound(comp)
    for shape, _, _ in parts: bb.Add(comp, shape)
    doc = xcaf_doc()
    st = XCAFDoc_DocumentTool.ShapeTool_s(doc.Main()); ct = XCAFDoc_DocumentTool.ColorTool_s(doc.Main())
    top = st.AddShape(comp, False, False)
    for shape, base, faces in parts:
        if base is not None: ct.SetColor(st.AddSubShape(top, shape), base, XCAFDoc_ColorSurf)
        for f, c in faces: ct.SetColor(st.AddSubShape(top, f), c, XCAFDoc_ColorSurf)
    Interface_Static.SetIVal_s('write.step.assembly', 0)
    Interface_Static.SetIVal_s('write.surfacecurve.mode', 0)
    w = STEPCAFControl_Writer(); w.SetColorMode(True)
    assert w.Transfer(doc, STEPControl_AsIs) and w.Write(str(path)) == IFSelect_RetDone, path
    return cq.Compound(comp)


def kicad_trsf(offset, rotate):
    """KiCad's model transform as a gp_Trsf: each angle negated, applied X, then Y, then Z, then the offset
    (checked against kicad-cli STEP export)."""
    t = gp_Trsf()
    for axis, angle in zip(((1, 0, 0), (0, 1, 0), (0, 0, 1)), rotate):
        r = gp_Trsf(); r.SetRotation(gp_Ax1(gp_Pnt(0, 0, 0), gp_Dir(*axis)), -angle * pi / 180); t = r.Multiplied(t)
    m = gp_Trsf(); m.SetTranslation(gp_Vec(*offset))
    return m.Multiplied(t)


# ------------------------------------------------------------------ vendor models
def powerdi5():
    """Diodes PowerDI-5 (SBRT20U60SP5-7, D1718): STEP embedded in TI TIDA-050023 PSIL024A_PCB.

    Native: length along Z, height along Y (body 1.15 mm, seating Y=-7.976), body width
    4.05 mm along X centred at -9.568. Cathode tab Z -3.3..1.2 (3.05 wide), two anode leads
    at X -10.488/-8.648 (1.84 apart) and Z 2.4..3.3. Footprint: pad 3 (cathode) at x=-1.12,
    pads 1/2 at x=2.862, y=+-0.92 (1.84 apart); Fab body 5.45 x 4.05 centred.
    Map: X = z, Y = x + 9.568, Z = y + 7.976 (a proper rotation: 120 deg about (1,1,1)).
    """
    r = gp_Trsf(); r.SetRotation(gp_Ax1(gp_Pnt(0, 0, 0), gp_Dir(1, 1, 1)), 120 * pi / 180)
    m = gp_Trsf(); m.SetTranslation(gp_Vec(0, 9.568, 7.976))
    return read_parts(HW / 'PoE.3dshapes/PowerDI-5.stp', m.Multiplied(r))


def keystone5019():
    """Keystone 5019 test point (TP17xx), TI TIDA-050023 embedded STEP; footprint transform baked in."""
    return read_parts(HW / 'PoE.3dshapes/5019.stp', kicad_trsf((-0.00009, -0.00008, 0.127), (-90, 0, 0)))

def efd25():
    """Wurth EFD25 flyback transformer (T1702), TI TIDA-050023 embedded STEP; footprint transform baked in."""
    return read_parts(HW / 'PoE.3dshapes/EFD25_4476.stp', kicad_trsf((-16.18809, 13.51504, -0.22083), (-90, 0, -180)))

def mdt420():
    """Amphenol MDT420B0X411 Rev A vendor STEP (reference/amphenol-mdt420-3d.zip, byte-identical to the
    download from Amphenol). Native X row axis, Y height, Z depth; all contact/retention feet bottom at
    Y=2.43 (pegs 0.5 lower into the NPTH), housing 4.20 above (drawing p1). Foot centres odd Z=-3.615,
    even Z=+4.171, retention Z=-3.0 vs lands -5.25/+2.275/-4.9 -> footprint y = Z - 1.9. Key gaps at the
    same -X: no mirror. Baked KiCad transform: rotate (-90 0 0), offset (0 1.9 -2.43)."""
    import tempfile, zipfile
    with tempfile.TemporaryDirectory() as tmp:
        src = zipfile.ZipFile(HW / 'reference/amphenol-mdt420-3d.zip').extract('MDT420B0X411_A.stp', tmp)
        return read_parts(src, kicad_trsf((0, 1.9, -2.43), (-90, 0, 0)))

VENDOR_BUILDS = {powerdi5, keystone5019, efd25, mdt420}


# ------------------------------------------------------------------ envelope models
# Geometry below is in footprint coordinates (x right, y down), read from the cited drawing.
# (d) = derived arithmetically from printed dimensions. XY nominal, height = package maximum.
BODY, METAL, MARK = cq.Color(0.12, 0.12, 0.12), cq.Color(0.80, 0.80, 0.78), cq.Color(0.85, 0.85, 0.85)

def box(x0, y0, x1, y1, z0, z1):
    """Axis box from FOOTPRINT coordinates (y down) into the model frame (Y up)."""
    return cq.Workplane().box(x1 - x0, y1 - y0, z1 - z0, centered=False).translate((x0, -y1, z0))

def envelope(body, height, standoff=0.0, terminals=(), pin1=None, extra=(), body_color=BODY):
    """body: (x0, y0, x1, y1) footprint coords; terminals: (x0, y0, x1, y1, z0, z1) metal boxes;
    extra: (x0, y0, x1, y1, z0, z1, color) additional features; pin1: (x, y) dot on the top face."""
    a = cq.Assembly()
    a.add(box(*body, standoff, height), name='body', color=body_color)
    for i, t in enumerate(terminals):
        a.add(box(*t), name=f't{i}', color=METAL)
    for i, (*t, c) in enumerate(extra):
        a.add(box(*t), name=f'x{i}', color=c)
    if pin1:
        a.add(cq.Workplane().circle(min(body[2] - body[0], body[3] - body[1]) * 0.06 + 0.1).extrude(0.01)
              .translate((pin1[0], -pin1[1], height)), name='pin1', color=MARK)
    return a

def lands(fp_id, shrink=0.0, z1=0.05, numbers=None):
    """Terminal boxes at the footprint's own copper (for leadless parts whose drawing gives the same
    terminal pattern the land pattern was reviewed against), optionally shrunk per side."""
    lib, name = fp_id.split(':')
    p = HW / f'{lib}.pretty/{name}.kicad_mod'
    if not p.exists():
        p = Path(json.loads((HW / 'footprint-policy.json').read_text())['default_library_root']) / f'{lib}.pretty/{name}.kicad_mod'
    out = []
    for m in re.finditer(r'\(pad "([^"]*)" smd \w+\s*\(at ([-\d.]+) ([-\d.]+)(?: ([-\d.]+))?\)\s*\(size ([-\d.]+) ([-\d.]+)\)', p.read_text()):
        if numbers is not None and m[1] not in numbers: continue
        x, y, w, h = float(m[2]), float(m[3]), float(m[5]), float(m[6])
        if m[4] and round(float(m[4])) % 180 == 90: w, h = h, w
        out.append((x - w/2 + shrink, y - h/2 + shrink, x + w/2 - shrink, y + h/2 - shrink, 0, z1))
    return out

def side_row(centres, edge, depth, width, axis, z1=0.2):
    """Leadless terminals flush with a body edge: axis 'x' = row along x at y=edge (sign = side)."""
    out = []
    for c in centres:
        lo, hi = (edge - depth, edge) if edge > 0 else (edge, edge + depth)
        out.append((c - width/2, lo, c + width/2, hi, 0, z1) if axis == 'x' else (lo, c - width/2, hi, c + width/2, 0, z1))
    return out

def rtl8125():
    """RTL8125BG-CG TQFN-48 6x6: rtl8125bg-v1.5.pdf p53 (DS p45, Table 38). D/E 6.0 BSC, A 1.0 max,
    b 0.20, L 0.40, e 0.40 (12/side at +-2.2 (d)), EP 4.30 sq; footprint = datasheet view turned 90 deg,
    pin 1 at bottom-left (-2.2, +2.8 (d))."""
    c = [-2.2 + 0.4*i for i in range(12)]
    t = side_row(c, 3.0, 0.4, 0.2, 'x') + side_row(c, -3.0, 0.4, 0.2, 'x') + side_row(c, 3.0, 0.4, 0.2, 'y') + side_row(c, -3.0, 0.4, 0.2, 'y')
    return envelope((-3, -3, 3, 3), 1.0, terminals=t + [(-2.15, -2.15, 2.15, 2.15, 0, 0.2)], pin1=(-2.4, 2.4))

def tps56837():
    """TPS56837 RPA0010A: tps56837.pdf p31, drawing 4224047/A. 3.0 nom sq, A 1.00 max; terminal
    sizes/centres per drawing (pins 1-4 at x=-1.30; 5/10 at (-0.93,+-1.30); 7 at (+0.87,+1.30);
    6 at (+0.37,+0.75) 0.25x1.5; 9 bar 0.40x1.9 at (-0.205,-0.55); 8 bar at (+0.945,-0.55) + three
    0.25 fingers to the +x edge at y=-0.75/-0.25/+0.25). Pin 1 top-left."""
    r = lambda cx, cy, w, h: (cx - w/2, cy - h/2, cx + w/2, cy + h/2, 0, 0.2)
    t = [r(-1.30, y, 0.40, 0.25) for y in (-0.75, -0.25, 0.25, 0.75)]
    t += [r(-0.93, 1.30, 0.25, 0.40), r(-0.93, -1.30, 0.25, 0.40), r(0.87, 1.30, 0.25, 0.40), r(0.37, 0.75, 0.25, 1.5),
          r(-0.205, -0.55, 0.40, 1.9), r(0.945, -0.55, 0.40, 1.9)]
    t += [(1.145, y - 0.125, 1.5, y + 0.125, 0, 0.2) for y in (-0.75, -0.25, 0.25)]
    return envelope((-1.5, -1.5, 1.5, 1.5), 1.0, terminals=t, pin1=(-1.05, -1.05))

def ts3usb221():
    """TS3USB221A RSE0010A UQFN-10: ts3usb221a.pdf p24, drawing 4220307/A. 2.0 (x) x 1.5 (y), A 0.6 max;
    side terminals 0.35 deep, 0.25 (corner) / 0.20 (inner) wide at x=+-0.75/+-0.25, y=+-0.575 (d);
    end terminals 5/10 at (+-0.80, 0) 0.40 x 0.30. Footprint = datasheet turned 90 deg; pin 1 bottom-left."""
    t = []
    for edge in (0.75, -0.75):
        t += side_row([-0.75, 0.75], edge, 0.35, 0.25, 'x', 0.12) + side_row([-0.25, 0.25], edge, 0.35, 0.20, 'x', 0.12)
    t += [(0.6, -0.15, 1.0, 0.15, 0, 0.12), (-1.0, -0.15, -0.6, 0.15, 0, 0.12)]
    return envelope((-1.0, -0.75, 1.0, 0.75), 0.6, terminals=t, pin1=(-0.65, 0.4))

def tps259474():
    """TPS259474L RPW0010A VQFN-10 2x2: tps25947.pdf p72, drawing 4225183/A. 2.0 nom sq, A 1.0 max;
    pins 5/6 full-length 0.30 strips at x=+-0.25; pins 2/3/8/9 0.40 x 0.25 at (+-0.80 (d), +-0.225);
    corner pins 1/4/7/10 occupy |x| 0.6..1.0, |y| 0.55..1.0 (corner square simplified). Pin 1 top-left."""
    t = [(x - 0.15, -1.0, x + 0.15, 1.0, 0, 0.1) for x in (-0.25, 0.25)]
    t += [(sx*0.80 - 0.2, sy*0.225 - 0.125, sx*0.80 + 0.2, sy*0.225 + 0.125, 0, 0.1) for sx in (-1, 1) for sy in (-1, 1)]
    t += [(min(sx*0.6, sx*1.0), min(sy*0.55, sy*1.0), max(sx*0.6, sx*1.0), max(sy*0.55, sy*1.0), 0, 0.1) for sx in (-1, 1) for sy in (-1, 1)]
    return envelope((-1.0, -1.0, 1.0, 1.0), 1.0, terminals=t, pin1=(-0.55, -0.55))

def tps54620():
    """TPS54620 RHL0014A VQFN-14 3.5x3.5: tps54620.pdf p44, drawing 4228405/A. 3.5 nom sq, A 1.0 max;
    terminals 0.24 x 0.40 (pins 1/14/7/8 at (+-0.75, +-1.55); 2-6 / 9-13 at x=+-1.55, y=-1..1 step 0.5);
    thermal pad 2.05 sq + 0.75-wide tabs (d) to the +-y edges. Pin 1 at (-0.75, -1.55)."""
    t = side_row([-0.75, 0.75], 1.75, 0.4, 0.24, 'x') + side_row([-0.75, 0.75], -1.75, 0.4, 0.24, 'x')
    t += side_row([-1.0, -0.5, 0, 0.5, 1.0], 1.75, 0.4, 0.24, 'y') + side_row([-1.0, -0.5, 0, 0.5, 1.0], -1.75, 0.4, 0.24, 'y')
    t += [(-1.025, -1.025, 1.025, 1.025, 0, 0.2), (-0.375, -1.75, 0.375, -1.025, 0, 0.2), (-0.375, 1.025, 0.375, 1.75, 0, 0.2)]
    return envelope((-1.75, -1.75, 1.75, 1.75), 1.0, terminals=t, pin1=(-1.25, -1.25))

def tcs4525():
    """TCS4525 WLCSP-20: tcs4525-v1.0-mirror.pdf p21. D 1.60-1.66 (x) x E 2.00-2.06 (y) -> 1.63 x 2.03 (d),
    A 0.60 max, ball height 0.15-0.23. Ball diameter is NOT given, so balls are not modelled: the body
    floats at the 0.19 (d) mid ball height. A1 top-left."""
    return envelope((-0.815, -1.015, 0.815, 1.015), 0.60, standoff=0.19, pin1=(-0.5, -0.7))

def lps4018():
    """Coilcraft LPS4018: lps4018.pdf p2. Octagonal case 3.90 sq, flats 2.4 (0.75 chamfer legs (d)),
    case height 1.70 +-0.10 -> 1.80; terminations wrap the +-x sides, 1.52 gap along the +-y edges,
    +0.13 overall per note 7 (0.065 per side (d)). Marking dot on the -x side."""
    oct_ = (cq.Workplane().polyline([(-1.95, -1.2), (-1.2, -1.95), (1.2, -1.95), (1.95, -1.2), (1.95, 1.2),
                                     (1.2, 1.95), (-1.2, 1.95), (-1.95, 1.2)]).close().extrude(1.8))
    a = cq.Assembly(); a.add(oct_, name='body', color=cq.Color(0.25, 0.25, 0.25))
    for s in (-1, 1):
        a.add(box(min(s*0.76, s*2.015), -1.2, max(s*0.76, s*2.015), 1.2, 0, 0.12), name=f'pad{s}', color=METAL)
        a.add(box(min(s*1.95, s*2.015), -1.2, max(s*1.95, s*2.015), 1.2, 0, 0.9), name=f'wrap{s}', color=METAL)
    a.add(cq.Workplane().circle(0.2).extrude(0.01).translate((-1.3, 0, 1.8)), name='dot', color=MARK)
    return a

def sit8008():
    """SiTime SiT8008 PQFN-4 3.2x2.5: sit8008.pdf p11 (POD-PQFN-004-X03225-002 A04). 3.2 (x) x 2.5 (y),
    A 0.80 max; pads 0.90 (x) x 0.80 (y) at (+-1.05, +-0.75) (d); pin 1 bottom-left (-1.05, +0.75)."""
    t = [(x - 0.45, y - 0.4, x + 0.45, y + 0.4, 0, 0.05) for x in (-1.05, 1.05) for y in (-0.75, 0.75)]
    return envelope((-1.6, -1.25, 1.6, 1.25), 0.80, standoff=0.02, terminals=t, pin1=(-1.2, 0.85),
                    body_color=cq.Color(0.75, 0.75, 0.72))

def emmc153():
    """ISSI IS21TF16G-JCLI 153-ball VFBGA 11.5 x 13 x 1.0: issi-emmc-tf.pdf p34 (Rev A, MO-276).
    E 11.5 (x) x D 13.0 (y), A 1.00 max, A1 0.15 min, ball b 0.30 nom at the footprint's 0.5 mm
    14x14 grid positions (A1 at (-3.25, -3.25)). Balls modelled as 0.30 spheres, body from 0.20 (d)."""
    a = envelope((-5.75, -6.5, 5.75, 6.5), 1.0, standoff=0.20, pin1=(-4.9, -5.6))
    balls = [cq.Solid.makeSphere(0.15, cq.Vector((x0 + x1)/2, -(y0 + y1)/2, 0.15), angleDegrees1=-90, angleDegrees2=90)
             for x0, y0, x1, y1, *_ in lands('Package_BGA:LFBGA-153_11.5x13mm_Layout14x14_P0.5mm')]
    a.add(cq.Compound.makeCompound(balls), name='balls', color=METAL)
    return a


BUILD = {
    'Sierra_PowerDI-5_SBRT20U60SP5': powerdi5,
    'Sierra_RTL8125BG_TQFN48': rtl8125,
    'Sierra_TPS56837_RPA0010A': tps56837,
    'Sierra_TS3USB221A_RSE0010A': ts3usb221,
    'Sierra_TPS259474L_RPW0010A': tps259474,
    'Sierra_TPS54620_RHL0014A': tps54620,
    'Sierra_TCS4525_WLCSP20': tcs4525,
    'Sierra_LPS4018': lps4018,
    'Sierra_SiT8008_PQFN4_3.2x2.5': sit8008,
    'Sierra_IS21TF16G_VFBGA153': emmc153,
    'Sierra_Keystone5019': keystone5019,
    'Sierra_EFD25_4476': efd25,
    'Sierra_MDT420B01411': mdt420,
}

# footprint -> (model path, offset, rotate)
ATTACH = {
    'Appliance:Sierra_MDT420B01411_2x38-1MP_P0.5mm': ('${KIPRJMOD}/Appliance.3dshapes/Sierra_MDT420B01411.step', *ZERO),
    'PoE:TI_Keystone_5019': ('${KIPRJMOD}/Appliance.3dshapes/Sierra_Keystone5019.step', *ZERO),
    'PoE:TI_Wurth_EFD25_4476': ('${KIPRJMOD}/Appliance.3dshapes/Sierra_EFD25_4476.step', *ZERO),
    'Appliance:Diodes_PowerDI-5_3Pin_Derived':
        ('${KIPRJMOD}/Appliance.3dshapes/Sierra_PowerDI-5_SBRT20U60SP5.step', *ZERO),
    **{fp: (f'${{KIPRJMOD}}/Appliance.3dshapes/{name}.step', *ZERO) for fp, name in {
        'Appliance:TQFN-48_L6.0-W6.0-P0.40-BL-EP4.5': 'Sierra_RTL8125BG_TQFN48',
        'Appliance:Texas_RPA0010A_TPS56837': 'Sierra_TPS56837_RPA0010A',
        'Appliance:UQFN-10_L2.0-W1.5-P0.50-BL': 'Sierra_TS3USB221A_RSE0010A',
        'Appliance:VQFN-10_L2.0-W2.0-P0.45-TL': 'Sierra_TPS259474L_RPW0010A',
        'Appliance:VQFN-14_L3.5-W3.5-P0.50-TL-EP_TPS54622RHLT': 'Sierra_TPS54620_RHL0014A',
        'Appliance:WLCSP-20_L2.0-W1.6-R5-C4-P0.40-TL': 'Sierra_TCS4525_WLCSP20',
        'Inductor_SMD:L_Coilcraft_LPS4018': 'Sierra_LPS4018',
        'Oscillator:Oscillator_SMD_SiT_PQFN-4Pin_3.2x2.5mm': 'Sierra_SiT8008_PQFN4_3.2x2.5',
        'Package_BGA:LFBGA-153_11.5x13mm_Layout14x14_P0.5mm': 'Sierra_IS21TF16G_VFBGA153',
    }.items()},
}


# ------------------------------------------------------------------ attach
def model_block(path, offset, rotate, indent='\t\t'):
    xyz = lambda v: ' '.join(f'{c:g}' for c in v)
    return (f'{indent}(model "{path}"\n{indent}\t(offset\n{indent}\t\t(xyz {xyz(offset)})\n{indent}\t)\n'
            f'{indent}\t(scale\n{indent}\t\t(xyz 1 1 1)\n{indent}\t)\n{indent}\t(rotate\n{indent}\t\t(xyz {xyz(rotate)})\n{indent}\t)\n{indent})\n')

def with_model(block, path, offset, rotate, indent):
    block = re.sub(r'\s*\(model "[^"]*"(?:[^()]|\((?:[^()]|\([^()]*\))*\))*\)', '', block)   # one model per footprint
    end = block.rstrip().rfind(')')
    return block[:end].rstrip() + '\n' + model_block(path, offset, rotate, indent) + indent[:-1] + block[end:].lstrip('\n').rstrip() + ('\n' if block.endswith('\n') else '')

def attach():
    sys.path.insert(0, str(Path(__file__).parent))
    from capture import children
    policy_path = HW / 'footprint-policy.json'; policy = json.loads(policy_path.read_text())
    board_path = HW / 'appliance.kicad_pcb'; board = board_path.read_text()
    for fp_id, (path, offset, rotate) in ATTACH.items():
        lib, name = fp_id.split(':')
        local = HW / f'{lib}.pretty/{name}.kicad_mod'
        if local.exists():   # pure insertion before the closing paren: strip_models() restores the reviewed bytes
            text = strip_models(local.read_text()); end = text.rstrip().rfind(')')
            local.write_text(text[:end] + model_block(path, offset, rotate, '\t') + text[end:])
        else:   # stock footprint: zero-transform models only, remapped through the policy
            assert (offset, rotate) == ZERO, fp_id
            stock = re.search(r'\(model "([^"]+)"', (Path(policy['default_library_root']) / f'{lib}.pretty/{name}.kicad_mod').read_text())[1]
            policy['model_overrides'][stock] = path
        n = 0
        for fp in children(board):
            if fp.startswith(f'(footprint "{fp_id}"'):
                board = board.replace(fp, with_model(fp, path, offset, rotate, '\t\t'), 1); n += 1
        assert n, fp_id
        policy['model_release_holds'].pop(fp_id, None)
        print(f'attached {fp_id} x{n}')
    board_path.write_text(board)
    policy_path.write_text(json.dumps(policy, indent=2, ensure_ascii=False) + '\n')


def record(reviewed='2026-11-21'):
    """Write reference/model-reviews-<date>.json in the 2026-10-21 schema (checked by check_model_reviews.py)."""
    import hashlib, inspect
    sys.path.insert(0, str(Path(__file__).parent))
    from capture import children
    policy = json.loads((HW / 'footprint-policy.json').read_text())
    board = (HW / 'appliance.kicad_pcb').read_text()
    refs = lambda fp_id: sorted(re.search(r'\(property "Reference" "([^"]+)"', f)[1] for f in children(board) if f.startswith(f'(footprint "{fp_id}"'))
    attached = []
    for fp_id, (path, offset, rotate) in ATTACH.items():
        rel = path.replace('${KIPRJMOD}/', '')
        name = Path(rel).stem
        shape = cq.importers.importStep(str(HW / rel)).val(); b = shape.BoundingBox()
        doc = inspect.getdoc(BUILD[name])
        attached.append({'footprint': fp_id, 'file': rel, 'sha256': hashlib.sha256((HW / rel).read_bytes()).hexdigest(),
                         'references': refs(fp_id), 'offset_xyz_mm': list(offset), 'rotation_xyz_degrees': list(rotate),
                         'size_xyz_mm': [round(b.xlen, 4), round(b.ylen, 4), round(b.zlen, 4)], 'z_min_mm': round(b.zmin, 4),
                         'kind': 'vendor' if name not in BUILD or BUILD[name] in VENDOR_BUILDS else 'envelope', 'source': doc})
    holds = [{'footprint': fp, 'references': sorted(r for r, f in policy['assignments'].items() if f == fp), 'blocker': why}
             for fp, why in policy['model_release_holds'].items()]
    out = {'reviewed': reviewed,
           'scope': 'Closes 2026-10-21 model holds. Vendor STEPs are attached with a verified datum transform. '
                    'Envelopes use nominal XY, package-maximum height and drawing terminal geometry; they are not '
                    'vendor-exact solids or tolerance envelopes, and do not qualify mating, assembly or clearance.',
           'source_hashes': {}, 'attached': attached, 'remaining_holds': holds}
    (HW / f'reference/model-reviews-{reviewed}.json').write_text(json.dumps(out, indent=1) + '\n')
    print(f'record: {len(attached)} attached, {len(holds)} holds')


if __name__ == '__main__':
    for name, build in BUILD.items():
        model = build(); path = HW / f'Appliance.3dshapes/{name}.step'
        if isinstance(model, cq.Assembly):   # envelopes: round-trip through cadquery's STEP to pick up part colours
            with tempfile.TemporaryDirectory() as tmp:
                model.save(f'{tmp}/a.step', exportType='STEP'); model = read_parts(f'{tmp}/a.step')
        shape = write_parts(path, model)
        assert shape.isValid(), name
        b = shape.BoundingBox()
        print(f'{name}: X {b.xmin:.3f}..{b.xmax:.3f}  Y {b.ymin:.3f}..{b.ymax:.3f}  Z {b.zmin:.3f}..{b.zmax:.3f}')
    if '--attach' in sys.argv:
        attach()
        record()
