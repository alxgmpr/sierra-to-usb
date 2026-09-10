"""Vendor IPC-style QFN lands matching RTL8125BG package dimensions."""
from pathlib import Path
import json,hashlib
import sexpdata as sx
import cadquery as cq
ROOT=Path(__file__).resolve().parents[1]
NAME='Realtek_RTL8125BG_QFN48_EP4.3'
source=Path('/Applications/KiCad/KiCad.app/Contents/SharedSupport/footprints/Package_DFN_QFN.pretty/QFN-48-1EP_6x6mm_P0.4mm_EP4.3x4.3mm.kicad_mod')
f=sx.loads(source.read_text());f[1]=NAME
def nodes(n,t):return [v for v in n if isinstance(v,list) and str(v[0])==t]
next(p for p in nodes(f,'property') if p[1]=='Value')[2]=NAME
nodes(f,'descr')[0][1]='RTL8125BG-CG QFN48:6x6mm,0.4mm pitch,4.3mm EP; native IPC-style lands; https://atta.szlcsc.com/upload/public/pdf/source/20220512/84CEBB847F37F5F3AD7D5F5F4E80AB39.pdf'
nodes(f,'model')[0][1]='${KIPRJMOD}/../lib/full-adapter.3dshapes/'+NAME+'.step'
(ROOT/'lib/full-adapter.pretty'/(NAME+'.kicad_mod')).write_text(sx.dumps(f)+'\n')
body=cq.Workplane('XY').box(6,6,1,centered=(True,True,False))
cq.exporters.export(body,str(ROOT/'lib/full-adapter.3dshapes'/(NAME+'.step')))
(ROOT/'research/rtl8125-footprint.json').write_text(json.dumps(dict(native=str(source),native_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),body_mm=[6,6],height_max_mm=1,exposed_pad_nominal_mm=[4.3,4.3],lead_width_range_mm=[.15,.25],pitch_mm=.4,lands='0.8x0.2 at normal distance2.95mm;4.3mm squareEP; native windowed paste; thermal vias to be added during board layout',orientation='Native pin1 is upper left, with numbering counterclockwise around top view; rotated90 degrees from the pin-assignment illustration. Verify assembly rotation against library pin1.',model='Nominal6x6 and maximum1mm height solid envelope, not manufacturer STEP'),indent=2)+'\n')
