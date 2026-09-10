"""Manufacturer lands for Ethernet control ICs, using official KiCad primitives."""
from pathlib import Path
import sys, json, hashlib
import sexpdata as sx
import cadquery as cq
ROOT=Path(__file__).resolve().parents[1]
SHARE=Path('/Applications/KiCad/KiCad.app/Contents/SharedSupport')
sys.path.insert(0,str(ROOT.parent/'tmp/kicad-library-tools'))
from KicadModTree import Footprint,FootprintType,Property,Text,Line,Rectangle,Pad,Model,KicadFileHandler


def nodes(n,t):return [v for v in n if isinstance(v,list) and str(v[0])==t]


name='Onsemi_FXMA2102_523AY'
f=Footprint(name,FootprintType.SMD)
f.setDescription('onsemi FXMA2102L8X; CASE523AY issueO; 1.6x1.6mm, 0.5mm pitch; manufacturer lands https://www.onsemi.com/pdf/datasheet/fxma2102-d.pdf')
f.setTags('onsemi MicroPak UQFN8 FXMA2102')
f.append(Property(name='Reference',text='REF**',at=[0,-1.8],layer='F.SilkS'))
f.append(Property(name='Value',text=name,at=[0,1.8],layer='F.Fab'))
f.append(Text(text='${REFERENCE}',at=[0,0],layer='F.Fab',size=[.5,.5],thickness=.075))
outline=[[-.8,-.4],[-.4,-.8],[.8,-.8],[.8,.8],[-.8,.8],[-.8,-.4]]
for a,b in zip(outline,outline[1:]):f.append(Line(start=a,end=b,layer='F.Fab',width=.1))
f.append(Rectangle(start=[-1.1,-1.1],end=[1.1,1.1],layer='F.CrtYd',width=.05))
# The top-through diagram has pin1 at bottom-left. Rotate it90deg clockwise
# on the page so KiCad pin1 is top-left and numbering advances down the left.
pads=[('1',-.605,-.5,.4,.25),('2',-.605,0,.4,.25),('3',-.605,.5,.4,.25),
      ('4',0,.575,.25,.45),('5',.605,.5,.4,.25),('6',.605,0,.4,.25),
      ('7',.605,-.5,.4,.25),('8',0,-.575,.25,.45)]
for n,x,y,w,h in pads:
    f.append(Pad(number=n,type=Pad.TYPE_SMT,shape=Pad.SHAPE_RECT,at=[x,y],size=[w,h],layers=Pad.LAYERS_SMT))
for a,b in [([-.45,-.92],[-.92,-.92]),([-.92,-.92],[-.92,-.4]),([.45,-.92],[.92,-.92]),([.92,-.92],[.92,-.4]),([-.45,.92],[-.92,.92]),([-.92,.92],[-.92,.4]),([.45,.92],[.92,.92]),([.92,.92],[.92,.4])]:
    # Silkscreen corners stay clear of all eight copper lands.
    a=[v/abs(v)*1.1 if abs(v)==.92 else v for v in a]
    b=[v/abs(v)*1.1 if abs(v)==.92 else v for v in b]
    f.append(Line(start=a,end=b,layer='F.SilkS',width=.12))
f.append(Line(start=[-1.3,-.85],end=[-1.3,-.35],layer='F.SilkS',width=.12))
f.append(Model(filename='${KIPRJMOD}/../lib/full-adapter.3dshapes/'+name+'.step'))
KicadFileHandler(f).writeFile(str(ROOT/'lib/full-adapter.pretty'/(name+'.kicad_mod')))
# Maximum package envelope, not a die-accurate model. Underside lands indicate
# the same rotation as the footprint; model Y is the negative of KiCad board Y.
body=cq.Workplane('XY').box(1.65,1.65,.525,centered=(True,True,False)).translate((0,0,.025))
for n,x,y,w,h in pads:
    body=body.union(cq.Workplane('XY').box(w,h,.025,centered=(True,True,False)).translate((x,-y,0)))
cq.exporters.export(body,str(ROOT/'lib/full-adapter.3dshapes'/(name+'.step')))
records=[dict(name=name,source='fxma2102.pdf',page=15,orientation='Figure2 top-through rotated90deg clockwise on page; pin1 top-left',pads=[dict(number=n,at=[x,y],size=[w,h]) for n,x,y,w,h in pads],model='Maximum1.65x1.65x0.55mm package envelope; underside lands show rotation',klc_exceptions=['F6.3 rectangular pads preserve manufacturer lands','F9.3 project-relative local STEP path'])]
for name,native,doc,page,dx,size,cy in [
    ('TI_DCK0005A','SOT-353_SC-70-5','sn74lvc1g07.pdf',47,1.1,[.95,.4],[1.85,1.35]),
    ('TI_DBV0006A','SOT-23-6','tps3808.pdf',37,1.3,[1.1,.6],[2.1,1.8])]:
    source=SHARE/'footprints/Package_TO_SOT_SMD.pretty'/(native+'.kicad_mod')
    fp=sx.loads(source.read_text());fp[1]=name
    next(p for p in nodes(fp,'property') if p[1]=='Value')[2]=name
    nodes(fp,'descr')[0][1]=f'{name}; manufacturer https://www.ti.com/lit/ds/symlink/{doc} page{page}; native KiCad outline with TI recommended lands'
    for p in nodes(fp,'pad'):
        a=nodes(p,'at')[0];a[1]=dx if a[1]>0 else -dx
        nodes(p,'size')[0][1:]=size;nodes(p,'roundrect_rratio')[0][1]=.05/min(size)
    fp=[p for p in fp if not (isinstance(p,list) and str(p[0]).startswith('fp_') and any(v[1]=='F.CrtYd' for v in nodes(p,'layer')))]
    fp.append(sx.loads(f'(fp_rect (start {-cy[0]} {-cy[1]}) (end {cy[0]} {cy[1]}) (stroke (width 0.05) (type solid)) (fill none) (layer "F.CrtYd"))'))
    model=SHARE/'3dmodels/Package_TO_SOT_SMD.3dshapes'/(native+'.step')
    (ROOT/'lib/full-adapter.3dshapes'/(name+'.step')).write_bytes(model.read_bytes())
    nodes(fp,'model')[0][1]='${KIPRJMOD}/../lib/full-adapter.3dshapes/'+name+'.step'
    (ROOT/'lib/full-adapter.pretty'/(name+'.kicad_mod')).write_text(sx.dumps(fp)+'\n')
    records.append(dict(name=name,source=doc,page=page,native=str(source),native_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),pads=[dict(number=p[1],at=nodes(p,'at')[0][1:3],size=nodes(p,'size')[0][1:3]) for p in nodes(fp,'pad')],model='Native KiCad generic package model; final mechanical clearance uses manufacturer maximum height',klc_exceptions=['F9.3 project-relative local STEP path']))
for r in records:
    r['source_sha256']=hashlib.sha256((ROOT/'reference'/r['source']).read_bytes()).hexdigest()
    model=ROOT/'lib/full-adapter.3dshapes'/(r['name']+'.step')
    model.write_text('\n'.join(line.rstrip() for line in model.read_text().splitlines())+'\n')
(ROOT/'research/ethernet-control-footprints.json').write_text(json.dumps(records,indent=2)+'\n')
print('Created three control footprints and STEP models.')
