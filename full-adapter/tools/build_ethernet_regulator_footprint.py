"""TI RWY0009A/C lands and stencil using official KicadModTree primitives."""
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT.parent/'tmp/kicad-library-tools'))
from KicadModTree import Footprint,FootprintType,Property,Text,Line,Rectangle,Pad,Model,KicadFileHandler
from KicadModTree.util.corner_handling import RoundRadiusHandler
import cadquery as cq
NAME='TI_RWY0009_2x3mm'
f=Footprint(NAME,FootprintType.SMD)
f.setDescription('TI RWY0009A/C; 2x3mm VQFN-HR; datasheet SLVSDU1K drawings4224015/B and4226803/A; https://www.ti.com/lit/ds/symlink/tps62813-q1.pdf')
f.setTags('Texas Instruments TPS6281 QFN hotrod')
f.append(Property(name='Reference',text='REF**',at=[0,-2.3],layer='F.SilkS'))
f.append(Property(name='Value',text=NAME,at=[0,2.3],layer='F.Fab'))
f.append(Text(text='${REFERENCE}',at=[0,0],layer='F.Fab',size=[.65,.65],thickness=.1))
for a,b in [((-1,-1.2),(-.7,-1.5)),((-.7,-1.5),(1,-1.5)),((1,-1.5),(1,1.5)),((1,1.5),(-1,1.5)),((-1,1.5),(-1,-1.2))]:
 f.append(Line(start=a,end=b,layer='F.Fab',width=.1))
f.append(Rectangle(start=[-1.4,-1.9],end=[1.4,1.9],layer='F.CrtYd',width=.05))
for y in [-1.8,1.8]:f.append(Line(start=[-1.1,y],end=[1.1,y],layer='F.SilkS',width=.12))
f.append(Line(start=[-1.35,-1.8],end=[-1.35,-.85],layer='F.SilkS',width=.12))
def land(n,x,y,w,h,layers):
 f.append(Pad(number=n,type=Pad.TYPE_SMT,shape=Pad.SHAPE_ROUNDRECT,at=[x,y],size=[w,h],layers=layers,round_radius_handler=RoundRadiusHandler(radius_ratio=.05/min(w,h))))
# TI's broad VIN/SW/GND bars are single electrical pads. Split paste leaves a
# 0.2mm central web, matching the manufacturer's 0.1mm-thick stencil example.
for n,y in [('2',-.5),('3',0),('4',.5)]:
 land(n,0,y,2.3,.25,['F.Cu','F.Mask'])
 for x in [-.625,.625]:land('',x,y,1.05,.25,['F.Paste'])
for n,y in [('9',-1.325),('6',1.325)]:land(n,0,y,.25,.65,Pad.LAYERS_SMT)
# Each L-shaped contact is a union of two same-number rounded rectangles.
# This retains the TI copper envelope; the internal concave corner is square.
# Paste uses 0.31/0.21mm arms per the TI stencil instead of copying copper.
for n,sx,sy in [('1',-1,-1),('8',1,-1),('5',-1,1),('7',1,1)]:
 land(n,sx*.7625,sy*1,.775,.25,['F.Cu','F.Mask'])
 land(n,sx*.55,sy*1.2625,.35,.775,['F.Cu','F.Mask'])
 land('',sx*.7625,sy*1,.775,.21,['F.Paste'])
 land('',sx*.53,sy*1.2625,.31,.775,['F.Paste'])
f.append(Model(filename='${KIPRJMOD}/../lib/full-adapter.3dshapes/'+NAME+'.step'))
KicadFileHandler(f).writeFile(str(ROOT/'lib/full-adapter.pretty'/(NAME+'.kicad_mod')))
# Maximum package dimensions, including height, for clearance inspection.
body=cq.Workplane('XY').box(2.1,3.1,1,centered=(True,True,False))
cq.exporters.export(body,str(ROOT/'lib/full-adapter.3dshapes'/(NAME+'.step')))
step=ROOT/'lib/full-adapter.3dshapes'/(NAME+'.step')
step.write_text('\n'.join(line.rstrip() for line in step.read_text().splitlines())+'\n')
print('Built RWY0009 copper/stencil lands and maximum package envelope.')
