"""Vendor lands checked against GCT B4, TI RUK/RUX and Hynetek Rev2.5.

The Hynetek datasheet specifies package terminals, not a recommended land.
Its lands use the official IPC-derived WDFN pattern; EP equals maximum metal.
"""
from pathlib import Path
import sexpdata as sx
import cadquery as cq
from cad import ROOT,nodes,one
from build_ethernet_footprints import base,write
from KicadModTree import FootprintType,Rectangle,Line,Pad
from KicadModTree.util.corner_handling import RoundRadiusHandler

STD=Path('/Applications/KiCad/KiCad.app/Contents/SharedSupport')


def vendor(name, source, model):
    f=sx.loads((STD/'footprints'/source).read_text());f[1]=name
    if name=='TI_RUK0020_TPD6S300':
        # TPD6S300 SLVSDK3C p33, RUK0020B 422676/A: .6 x .2 lands.
        # The installed generic KiCad land is .7 long; follow the device DS.
        for p in nodes(f,'pad'):
            if p[1] and int(p[1])<=20:
                size=one(p,'size')
                size[1:3]=[.6,.2] if int(p[1])<=5 or 11<=int(p[1])<=15 else [.2,.6]
    f[:]=[x for x in f if not (isinstance(x,list) and str(x[0])=='model')]
    for p in nodes(f,'property'):
        if p[1]=='Value':p[2]=name
    f.append(sx.loads('(model "${KIPRJMOD}/../lib/cm4.3dshapes/'+name+'.step" (offset (xyz 0 0 0)) (scale (xyz 1 1 1)) (rotate (xyz 0 0 0)))'))
    (ROOT/'lib/cm4.pretty'/(name+'.kicad_mod')).write_text(sx.dumps(f)+'\n')
    path=ROOT/'lib/cm4.3dshapes'/(name+'.step')
    cq.exporters.export(model,str(path));assert path.stat().st_size>1000
    path.write_text('\n'.join(line.rstrip() for line in path.read_text().splitlines())+'\n')
    assert cq.importers.importStep(str(path)).val().isValid()


def build():
    # GCT current 2023 B4: lower edge of contact pads to front shield centre
    # 4.18 mm; front shield centre to PCB edge 2.60 mm. Existing origin is
    # 3.675 mm behind the PCB edge. Signal/GND pads share A/B numbers.
    src='Connector_USB.pretty/USB_C_Receptacle_GCT_USB4105-xx-A_16P_TopMnt_Horizontal.kicad_mod'
    model=cq.importers.importStep(str(STD/'3dmodels/Connector_USB.3dshapes/USB_C_Receptacle_GCT_USB4105-xx-A_16P_TopMnt_Horizontal.step'))
    # -120 variant uses 1.20 +-0.15 mm stakes. Extend the nominal library
    # stake geometry to the maximum depth; no invented mating clearance.
    for x in [-4.32,4.32]:
        for y,length in [(-3.105,1.30),(1.075,1.0)]:
            tab=cq.Workplane('XY').box(.25,length,1.35,centered=(True,True,False)).translate((x,-y,-1.35))
            model=model.union(tab)
    vendor('GCT_USB4105_GF_A_120',src,model)
    vendor('TI_RUK0020_TPD6S300',
        'Package_DFN_QFN.pretty/Texas_RUK0020B_WQFN-20-1EP_3x3mm_P0.4mm_EP1.7x1.7mm.kicad_mod',
        cq.Workplane('XY').box(3.1,3.1,.8,centered=(True,True,False)))
    vendor('TI_RUX0012_TPS2121',
        'Package_DFN_QFN.pretty/Texas_VQFN-HR-12_2x2.5mm_P0.5mm.kicad_mod',
        cq.Workplane('XY').box(2.1,2.6,1,centered=(True,True,False)))
    name='Hynetek_DFN10_3x3_P0.5_EP1.8x2.5'
    f=base(name,FootprintType.SMD,'HUSB238 Rev2.5: body3x3 L.324-.476 b.2-.3 EP1.6-1.8x2.3-2.5; IPC-derived .75x.25 lands P.5, EP1.8x2.5',-2.3,2.3)
    f.append(Rectangle(start=[-1.5,-1.5],end=[1.5,1.5],layer='F.Fab',width=.1))
    f.append(Rectangle(start=[-2.1,-1.8],end=[2.1,1.8],layer='F.CrtYd',width=.05))
    for y in [-1.65,1.65]:f.append(Line(start=[-1.5,y],end=[1.5,y],layer='F.SilkS',width=.12))
    f.append(Line(start=[-1.5,-1.65],end=[-1.85,-1.65],layer='F.SilkS',width=.12))
    f.append(Line(start=[-1.5,-1.0],end=[-1,-1.5],layer='F.Fab',width=.1))
    for n in range(1,11):
        x=-1.475 if n<=5 else 1.475;y=-1+((n-1) if n<=5 else (10-n))*.5
        f.append(Pad(number=str(n),type=Pad.TYPE_SMT,shape=Pad.SHAPE_ROUNDRECT,
            at=[x,y],size=[.75,.25],layers=Pad.LAYERS_SMT,
            round_radius_handler=RoundRadiusHandler(radius_ratio=.2)))
    f.append(Pad(number='11',type=Pad.TYPE_SMT,shape=Pad.SHAPE_RECT,
        at=[0,0],size=[1.8,2.5],layers=['F.Cu','F.Mask']))
    # Four .73x1.01 windows: 65.5% paste coverage. Keep vias out of paste.
    for x in [-.45,.45]:
        for y in [-.625,.625]:
            f.append(Pad(number='',type=Pad.TYPE_SMT,shape=Pad.SHAPE_RECT,
                at=[x,y],size=[.73,1.01],layers=['F.Paste']))
    write(f,name,cq.Workplane('XY').box(3.076,3.076,.8,centered=(True,True,False)))
    path=ROOT/'lib/cm4.3dshapes'/(name+'.step')
    path.write_text('\n'.join(line.rstrip() for line in path.read_text().splitlines())+'\n')


if __name__=='__main__':build()
