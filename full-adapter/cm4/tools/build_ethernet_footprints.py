"""HX6096NL and Y1 capacitor lands from manufacturer drawings.

Uses the official KiCad Library Tools primitives. The capacitor model is the
maximum body envelope, not a vendor CAD model. RJ45 lands are generated only
after the revised Molex drawing is visually checked.
"""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT.parents[1] / 'tmp/kicad-library-tools'))
from KicadModTree import Footprint, FootprintType, Property, Text, Rectangle, Line, Pad, Model, KicadFileHandler
from KicadModTree.util.corner_handling import RoundRadiusHandler
from KicadModTree.nodes.base.Zone import Zone, Keepouts, Hatch
import cadquery as cq


def base(name, kind, description, ref_y, value_y):
    f = Footprint(name, kind)
    f.setDescription(description)
    f.append(Property(name='Reference', text='REF**', at=[0,ref_y], layer='F.SilkS'))
    f.append(Property(name='Value', text=name, at=[0,value_y], layer='F.Fab'))
    f.append(Text(text='${REFERENCE}', at=[0,0], layer='F.Fab', size=[1,1], thickness=.15))
    return f


def write(f, name, model):
    f.append(Model(filename='${KIPRJMOD}/../lib/cm4.3dshapes/'+name+'.step'))
    KicadFileHandler(f).writeFile(str(ROOT/'lib/cm4.pretty'/(name+'.kicad_mod')))
    model_dir=ROOT/'lib/cm4.3dshapes'
    model_dir.mkdir(exist_ok=True)
    model_path=model_dir/(name+'.step')
    cq.exporters.export(model,str(model_path))
    assert model_path.stat().st_size>1000,model_path
    assert cq.importers.importStep(str(model_path)).val().isValid(),model_path


def transformer():
    name = 'Pulse_HX6096NL'
    f = base(name,FootprintType.SMD,
        'HX6096NL Rev A 2015-09-25 page3: .030x.075in lands, .050in pitch, .575in row spacing; pin1 lower left', -9.3,9.3)
    f.append(Rectangle(start=[-9.08,-6.1],end=[9.08,6.1],layer='F.Fab',width=.1))
    f.append(Rectangle(start=[-9.5,-8.55],end=[9.5,8.55],layer='F.CrtYd',width=.05))
    for x in [-9.2,9.2]:
        f.append(Line(start=[x,-6.22],end=[x,6.22],layer='F.SilkS',width=.12))
    f.append(Line(start=[-9.2,6.22],end=[-8,6.22],layer='F.SilkS',width=.12))
    f.append(Line(start=[-9.08,4.8],end=[-7.78,6.1],layer='F.Fab',width=.1))
    model = cq.Workplane('XY').box(18.41,12.71,6.60,centered=(True,True,False))
    for n in range(1,25):
        x = -6.985 + (n-1 if n<=12 else 24-n)*1.27
        y = 7.3025 if n<=12 else -7.3025
        f.append(Pad(number=str(n),type=Pad.TYPE_SMT,shape=Pad.SHAPE_ROUNDRECT,
            at=[x,y],size=[.762,1.905],layers=Pad.LAYERS_SMT,
            round_radius_handler=RoundRadiusHandler(radius_ratio=.15)))
        # Leads are nominal; the housing is the maximum datasheet envelope.
        model = model.union(cq.Workplane('XY').box(.762,2.2,.25,
            centered=(True,True,False)).translate((x,-y,0)))
    write(f,name,model)


def safety_cap():
    name = 'Dersonic_CY1102ME14EF45W2A2_P10mm'
    f = base(name,FootprintType.THT,
        'CY1102ME14EF45W2A2 DEC-SA-WI001 B/0 2022-02-15: D6.3+-1 T4.4+-.8 P10+-1 wire .6+-.1mm; 1nF Y1 400VAC', -3.3,3.3)
    f.append(Rectangle(start=[-3.65,-2.6],end=[3.65,2.6],layer='F.Fab',width=.1))
    f.append(Rectangle(start=[-6.3,-2.9],end=[6.3,2.9],layer='F.CrtYd',width=.05))
    for y in [-2.75,2.75]:
        f.append(Line(start=[-3.8,y],end=[3.8,y],layer='F.SilkS',width=.12))
    for n,x in [('1',-5),('2',5)]:
        f.append(Pad(number=n,type=Pad.TYPE_THT,shape=Pad.SHAPE_CIRCLE,
            at=[x,0],size=[2,2],drill=1.0,layers=Pad.LAYERS_THT))
    # Body coating can extend 3mm down the leads. Reserve 10.3mm total height.
    model = cq.Workplane('XZ').circle(3.65).extrude(2.6,both=True).translate((0,0,6.65))
    for x in [-5,5]:
        model = model.union(cq.Workplane('XY').circle(.35).extrude(4.0).translate((x,0,-1.6)))
    write(f,name,model)


def esd():
    name='TI_DQA0010_TPD4EUSB30'
    f=base(name,FootprintType.SMD,
        'TPD4EUSB30 DQA0010A/B TI SLVSAC2G package addendum 2026: .565x.2 signal lands, .835 row spacing, .5 pitch; joined .4mm-wide ground lands 3/8',-1.9,1.9)
    f.append(Rectangle(start=[-.5,-1.25],end=[.5,1.25],layer='F.Fab',width=.1))
    f.append(Rectangle(start=[-.95,-1.5],end=[.95,1.5],layer='F.CrtYd',width=.05))
    for y in [-1.38,1.38]:f.append(Line(start=[-.5,y],end=[.5,y],layer='F.SilkS',width=.12))
    f.append(Line(start=[-.7,-1.38],end=[-.7,-1.65],layer='F.SilkS',width=.12))
    for n in range(1,11):
        x=-.4175 if n<=5 else .4175
        y=-1+(n-1 if n<=5 else 10-n)*.5
        f.append(Pad(number=str(n),type=Pad.TYPE_SMT,shape=Pad.SHAPE_ROUNDRECT,
            at=[x,y],size=[.565,.4 if n in [3,8] else .2],layers=Pad.LAYERS_SMT,
            round_radius_handler=RoundRadiusHandler(radius_ratio=.125 if n in [3,8] else .25)))
    # Both package variants allow joining 3 and 8. DQA0010B has the exposed
    # ground between them. Make the bridge explicit as a second pad3 region.
    f.append(Pad(number='3',type=Pad.TYPE_SMT,shape=Pad.SHAPE_RECT,
        at=[0,0],size=[.8,.4],layers=Pad.LAYERS_SMT))
    model=cq.Workplane('XY').box(1,2.5,.55,centered=(True,True,False))
    write(f,name,model)


def rj45():
    name='Molex_855437002'
    f=base(name,FootprintType.SMD,
        'Molex SD-85543-502 B3 2023-02-28 revised PCB layout, viewed from component side. Origin at board edge; port faces +Y. Lands .76x6.35 P1.27; SH 2.54x3.60. Nominal body extends .4mm past edge.',-23,2)
    f.append(Rectangle(start=[-8.3,-18.4],end=[8.3,.4],layer='F.Fab',width=.1))
    f.append(Rectangle(start=[-9.65,-22],end=[9.65,.9],layer='F.CrtYd',width=.05))
    for x in [-8.42,8.42]:
        f.append(Line(start=[x,-18.52],end=[x,-6.9],layer='F.SilkS',width=.12))
    f.append(Line(start=[-4.445,-21.95],end=[-5.5,-21.95],layer='F.SilkS',width=.12))
    f.append(Line(start=[-10,0],end=[10,0],layer='Dwgs.User',width=.1))
    f.append(Text(text='PCB EDGE / PORT',at=[0,1.2],layer='Dwgs.User',size=[.8,.8],thickness=.1))
    f.append(Rectangle(start=[-8.3,-18.4],end=[8.3,.4],layer='Cmts.User',width=.1))
    f.append(Zone(shape=[[-8.3,-18.4],[8.3,-18.4],[8.3,.4],[-8.3,.4]],
        layers=['F.Cu'],name='Molex housing: no surface routing',hatch=Hatch(Hatch.EDGE,.5),
        keepouts=Keepouts(tracks=Keepouts.DENY,vias=Keepouts.DENY,copperpour=Keepouts.DENY,
                          pads=Keepouts.ALLOW,footprints=Keepouts.DENY)))
    for n in range(1,9):
        f.append(Pad(number=str(n),type=Pad.TYPE_SMT,shape=Pad.SHAPE_RECT,
            at=[-4.445+(n-1)*1.27,-18.515],size=[.76,6.35],layers=Pad.LAYERS_SMT))
    for x in [-8.085,8.085]:
        f.append(Pad(number='SH',type=Pad.TYPE_SMT,shape=Pad.SHAPE_RECT,
            at=[x,-4.74],size=[2.54,3.60],layers=Pad.LAYERS_SMT))
    # Maximum housing envelope. Plug/latch/cable service keepout is defined
    # separately in the carrier mechanical constraints, beyond the board edge.
    model=cq.Workplane('XY').box(16.95,19.15,13.35,
        centered=(True,True,False)).translate((0,9,0))
    write(f,name,model)


if __name__ == '__main__':
    transformer()
    safety_cap()
    esd()
    rj45()
