"""Draw manufacturer land-pattern dimensions using official KiCad KicadModTree.
Irregular TI corner pads are unions of same-number rounded rectangles.
These review footprints need independent package/stencil sign-off before layout release.
"""
from pathlib import Path
import json
from KicadModTree import Footprint,FootprintType,Pad,Rectangle,Property,Text,KicadFileHandler,RoundRadiusHandler
ROOT=Path(__file__).resolve().parents[1]
from generation_guard import preflight, record
OUTPUTS=[ROOT/p for p in ['lib/compact-usb.pretty/TI_RPW0010A.kicad_mod', 'lib/compact-usb.pretty/TI_RWY0009A.kicad_mod', 'lib/compact-usb.pretty/LTC_FE24_AA.kicad_mod', 'reference/land-pattern-dimensions.json']]
preflight(ROOT, 'power-footprints', OUTPUTS)
out=ROOT/'lib/compact-usb.pretty'
spec={}
def begin(name,body,source):
 f=Footprint(name,FootprintType.SMD)
 f.description=f'Manufacturer land pattern: {source}; generated for engineering review'
 f.tags='power compact USB'
 f.append(Property(name='Reference',text='REF**',at=[0,-body[1]/2-1.2],layer='F.SilkS',size=[1,1],thickness=.15))
 f.append(Property(name='Value',text=name,at=[0,body[1]/2+1.2],layer='F.Fab',size=[.7,.7],thickness=.1))
 f.append(Rectangle(start=[-body[0]/2,-body[1]/2],end=[body[0]/2,body[1]/2],layer='F.Fab',width=.1))
 # Courtyard contains copper including corner-pad arms.
 hx=max(body[0]/2,1.2)+.5;hy=max(body[1]/2,1.65)+.5
 if name=='LTC_FE24_AA':hx=3.55
 f.append(Rectangle(start=[-hx,-hy],end=[hx,hy],layer='F.CrtYd',width=.05))
 spec[name]={'body_mm':body,'source':source,'pads':[]}
 return f

def pad(f,num,x,y,w,h):
 spec[f.name]['pads'].append({'number':num,'center':[x,y],'size':[w,h]})
 f.append(Pad(number=num,type=Pad.TYPE_SMT,shape=Pad.SHAPE_ROUNDRECT,at=[x,y],size=[w,h],layers=Pad.LAYERS_SMT,round_radius_handler=RoundRadiusHandler(radius_ratio=.25,maximum_radius=.05)))
def save(f):KicadFileHandler(f).writeFile(out/(f.name+'.kicad_mod'))
f=begin('TI_RPW0010A',[2,2],'TPS25947 Rev C PDF p73, TI 4225183/A, 08/2019')
for side,nums in [(-1,[1,2,3,4]),(1,[10,9,8,7])]:
 for n,y in zip(nums,[-.7,-.225,.225,.7]):pad(f,n,side*.9,y,.6,.3 if abs(y)>.5 else .25)
 for n,sgn in [(nums[0],-1),(nums[-1],1)]:pad(f,n,side*.725,sgn*.875,.25,.65)
pad(f,5,-.25,0,.3,2.4);pad(f,6,.25,0,.3,2.4);save(f)
f=begin('TI_RWY0009A',[2,3],'TPS62816-Q1 SLUSDM1A PDF p38, TI 4224015/B, 01/2018')
for n,y in [(2,-.5),(3,0),(4,.5)]:pad(f,n,0,y,2.3,.25)
for n,sx,sy in [(1,-1,-1),(8,1,-1),(5,-1,1),(7,1,1)]:
 pad(f,n,sx*.7625,sy*1.0,.775,.25)
 pad(f,n,sx*.55,sy*1.2625,.35,.775)
pad(f,9,0,-1.325,.25,.65);pad(f,6,0,1.325,.25,.65);save(f)
f=begin('LTC_FE24_AA',[4.4,7.8],'LTC3128 datasheet 3128f p23, LTC 05-08-1771 FE24 AA Rev B')
for i in range(12):
 pad(f,i+1,-2.775,-3.575+.65*i,1.05,.45)
 pad(f,24-i,2.775,-3.575+.65*i,1.05,.45)
pad(f,25,0,0,3.25,2.74);save(f)
(ROOT/'reference/land-pattern-dimensions.json').write_text(json.dumps(spec,indent=2))
print('3 footprints generated; irregular pad pieces share physical pin numbers')

record(ROOT, 'power-footprints', OUTPUTS)
