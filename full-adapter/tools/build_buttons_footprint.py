"""Alps SKRP manufacturer lands using official KicadModTree primitives."""
from pathlib import Path
import sys,json,hashlib
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT.parent/'tmp/kicad-library-tools'))
from KicadModTree import Footprint,FootprintType,Property,Text,Rectangle,Line,Pad,Model,KicadFileHandler
from KicadModTree.util.corner_handling import RoundRadiusHandler
import cadquery as cq
NAME='Alps_SKRPACE010'
f=Footprint(NAME,FootprintType.SMD)
f.setDescription('Alps SKRPACE010; 4.2x3.2mm body, 2.5mm height; manufacturer SKRP catalog2510 drawing1 https://tech.alpsalpine.com/cms.media/product_catalog_ta_02_skrp_en_2cd80f610b.pdf')
f.setTags('Alps SKRP tactile push button')
f.append(Property(name='Reference',text='REF**',at=[0,-2.5],layer='F.SilkS'))
f.append(Property(name='Value',text=NAME,at=[0,2.5],layer='F.Fab'))
f.append(Text(text='${REFERENCE}',at=[0,0],layer='F.Fab',size=[.7,.7],thickness=.1))
f.append(Rectangle(start=[-2.1,-1.6],end=[2.1,1.6],layer='F.Fab',width=.1))
f.append(Rectangle(start=[-2.85,-1.85],end=[2.85,1.85],layer='F.CrtYd',width=.05))
for y in [-1.72,1.72]:f.append(Line(start=[-2.1,y],end=[2.1,y],layer='F.SilkS',width=.12))
for x in [-2.72,2.72]:f.append(Line(start=[x,-.5],end=[x,.5],layer='F.SilkS',width=.12))
for n,x,y in [('1',-2.075,-1.075),('2',2.075,-1.075),('3',-2.075,1.075),('4',2.075,1.075)]:
 f.append(Pad(number='1' if n in ['1','2'] else '2',type=Pad.TYPE_SMT,shape=Pad.SHAPE_ROUNDRECT,at=[x,y],size=[1.05,.65],layers=Pad.LAYERS_SMT,round_radius_handler=RoundRadiusHandler(radius_ratio=.15)))
f.append(Model(filename='${KIPRJMOD}/../lib/full-adapter.3dshapes/'+NAME+'.step'))
KicadFileHandler(f).writeFile(str(ROOT/'lib/full-adapter.pretty'/(NAME+'.kicad_mod')))
body=cq.Workplane('XY').box(4.2,3.2,1.8,centered=(True,True,False))
stem=cq.Workplane('XY').workplane(offset=1.8).slot2D(3,1.6).extrude(.7)
body=body.union(stem)
for x in [-2.2,2.2]:
 for y in [-1.075,1.075]:body=body.union(cq.Workplane('XY').box(.2,.65,.2,centered=(True,True,False)).translate((x,y,0)))
cq.exporters.export(body,str(ROOT/'lib/full-adapter.3dshapes'/(NAME+'.step')))
print('Created manufacturer lands and nominal body/stem envelope.')
