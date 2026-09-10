"""Vendor native recovery footprints/models; retain source hashes for review."""
from pathlib import Path
import sexpdata as sx
import hashlib,json
ROOT=Path(__file__).resolve().parents[1]
SHARE=Path('/Applications/KiCad/KiCad.app/Contents/SharedSupport')
def nodes(n,t):return [v for v in n if isinstance(v,list) and str(v[0])==t]
records=[]
for name,group,native in [('TI_TS3USB221A_RSE0010A','Package_DFN_QFN','Texas_UQFN-10_1.5x2mm_P0.5mm'),('TI_TPD2EUSB30_DRT0003A','Package_TO_SOT_SMD','Texas_DRT-3'),('GCT_USB4105_120','Connector_USB','USB_C_Receptacle_GCT_USB4105-xx-A_16P_TopMnt_Horizontal')]:
    source=SHARE/'footprints'/(group+'.pretty')/(native+'.kicad_mod')
    fp=sx.loads(source.read_text());fp[1]=name
    next(p for p in nodes(fp,'property') if p[1]=='Value')[2]=name
    model=SHARE/'3dmodels'/(group+'.3dshapes')/(native+'.step')
    target=ROOT/'lib/full-adapter.3dshapes'/(name+'.step')
    if model.exists():
        target.write_bytes(model.read_bytes());nodes(fp,'model')[0][1]='${KIPRJMOD}/../lib/full-adapter.3dshapes/'+name+'.step'
    elif name=='TI_TS3USB221A_RSE0010A':
        import cadquery as cq
        body=cq.Workplane('XY').box(1.5,2,.6,centered=(True,True,False))
        cq.exporters.export(body,str(target))
        nodes(fp,'model')[0][1]='${KIPRJMOD}/../lib/full-adapter.3dshapes/'+name+'.step'
    else:
        raise FileNotFoundError(model)
    (ROOT/'lib/full-adapter.pretty'/(name+'.kicad_mod')).write_text(sx.dumps(fp)+'\n')
    records.append(dict(name=name,source=str(source),sha256=hashlib.sha256(source.read_bytes()).hexdigest(),model='Native KiCad model; exact tail-length/clearance review pending' if group=='Connector_USB' else 'Nominal 1.5x2mm, maximum 0.6mm-height solid package envelope' if name=='TI_TS3USB221A_RSE0010A' else 'Native KiCad package model',pads=[dict(number=p[1],at=nodes(p,'at')[0][1:3],size=nodes(p,'size')[0][1:3]) for p in nodes(fp,'pad')]))
(ROOT/'research/recovery-footprints.json').write_text(json.dumps(records,indent=2)+'\n')
