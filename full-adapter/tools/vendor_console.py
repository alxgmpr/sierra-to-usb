"""Vendor console footprints and native models; use TI's recommended DCU lands."""
from pathlib import Path
import hashlib,json
import sexpdata as sx
ROOT=Path(__file__).resolve().parents[1]
SHARE=Path('/Applications/KiCad/KiCad.app/Contents/SharedSupport')
def nodes(n,t):return [v for v in n if isinstance(v,list) and str(v[0])==t]
records=[]
for name,group,native,doc in [('TI_TXU0202_DCU0008A','Package_SO','VSSOP-8_2.3x2mm_P0.5mm','txu0202.pdf'),('JST_PH_B4B-PH-SM4-TB','Connector_JST','JST_PH_B4B-PH-SM4-TB_1x04-1MP_P2.00mm_Vertical','jst-ph.pdf')]:
 source=SHARE/'footprints'/(group+'.pretty')/(native+'.kicad_mod')
 fp=sx.loads(source.read_text());fp[1]=name
 next(p for p in nodes(fp,'property') if p[1]=='Value')[2]=name
 if group=='Package_SO':
  for p in nodes(fp,'pad'):
   a=nodes(p,'at')[0];a[1]=1.55 if a[1]>0 else -1.55
   nodes(p,'size')[0][1:]=[.85,.3]
   nodes(p,'roundrect_rratio')[0][1]=1/6
 model=SHARE/'3dmodels'/(group+'.3dshapes')/(native+'.step')
 target=ROOT/'lib/full-adapter.3dshapes'/(name+'.step')
 if group=='Connector_JST':
  import cadquery as cq
  # Manufacturer nominal header envelope; deliberately solid for clearance checks.
  # The footprint F.Fab body is x +/-5.975, y -4.25..0.75. STEP Y is inverted.
  body=cq.Workplane('XY').box(11.95,5,6.6,centered=(True,True,False)).translate((0,1.75,0))
  cq.exporters.export(body,str(target))
 else:
  target.write_bytes(model.read_bytes())
 nodes(fp,'model')[0][1]='${KIPRJMOD}/../lib/full-adapter.3dshapes/'+name+'.step'
 (ROOT/'lib/full-adapter.pretty'/(name+'.kicad_mod')).write_text(sx.dumps(fp)+'\n')
 records.append(dict(name=name,native=str(source),native_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),datasheet=doc,datasheet_sha256=hashlib.sha256((ROOT/'reference'/doc).read_bytes()).hexdigest(),model='JST solid nominal 11.95 x 5 x 6.6mm header envelope; allow mating cable above it' if group=='Connector_JST' else 'Native generic DCU package model',pads=[dict(number=p[1],at=nodes(p,'at')[0][1:3],size=nodes(p,'size')[0][1:3]) for p in nodes(fp,'pad')]))
(ROOT/'research/console-footprints.json').write_text(json.dumps(records,indent=2)+'\n')
