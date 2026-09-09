"""Deterministic KiCad power-circuit capture. Run using compact/.venv/bin/python."""
from pathlib import Path
import math, json, uuid, copy
import sexpdata as sx
ROOT=Path(__file__).resolve().parent

STD=Path('/Applications/KiCad/KiCad.app/Contents/SharedSupport/symbols')
S=sx.Symbol
def uid(key):return str(uuid.uuid5(uuid.NAMESPACE_URL,'compact-carrier/'+key))
def q(s):return json.dumps(str(s),ensure_ascii=False)
def eff(size=1.27,just=''):
 return f'(effects (font (size {size} {size}))'+(f' (justify {just})' if just else '')+')'
def node(a,k):return next((v for v in a if isinstance(v,list) and str(v[0])==k),None)
def nodes(a,k):return [v for v in a if isinstance(v,list) and str(v[0])==k]
libs={};custom={};specs={};items=[];placed={};nets={};rootid=uid('sheet')
def lib(name):
 if name in libs:return libs[name]
 prefix,part=name.split(':')
 a=sx.load(open(STD/(prefix+'.kicad_sym')))
 sym=copy.deepcopy(next(v for v in nodes(a,'symbol') if v[1]==part))
 if node(sym,'extends'):raise ValueError('Inherited symbol: '+name)
 sym[1]=name;libs[name]=sym;return sym

def ic(name,pins,foot,ds,desc):
 # Pins are explicit (number,name,type,side). Datasheet pin numbers never inferred from drawing order.
 w=15.24; groups={s:[] for s in 'LRTB'}
 for pin in pins:groups[pin[3]].append(pin)
 h=max(10.16,2.54*(max(len(groups['L']),len(groups['R']))+1))
 body=f'(symbol "{name}_0_1" (rectangle (start {-w} {h/2}) (end {w} {-h/2}) (stroke (width 0.254) (type default)) (fill (type background))))'
 pintext=''
 for side,ps in groups.items():
  for i,(num,pn,pt,_) in enumerate(ps):
   v=(i-(len(ps)-1)/2)*2.54
   if side=='L':x,y,angle=-w-2.54,-v,0
   elif side=='R':x,y,angle=w+2.54,-v,180
   elif side=='T':x,y,angle=v,h/2+2.54,270
   else:x,y,angle=v,-h/2-2.54,90
   pintext+=f'(pin {pt} line (at {x} {y} {angle}) (length 2.54) (name {q(pn)} {eff()}) (number {q(num)} {eff()}))'
 props=''.join(f'(property {q(k)} {q(v)} (at 0 {h/2+5.08-i*2.54} 0) {eff()}'+(' (hide yes)' if i>1 else '')+')' for i,(k,v) in enumerate([('Reference','U'),('Value',name),('Footprint',foot),('Datasheet',ds),('Description',desc),('ki_keywords','power controller'),('ki_fp_filters',foot.split(':')[-1])]))
 sym=sx.loads(f'(symbol {q(name)} (pin_names (offset 0.508)) (in_bom yes) (on_board yes) {props} {body} (symbol "{name}_1_1" {pintext}))')
 custom[name]=sym;embedded=copy.deepcopy(sym);embedded[1]='carrier-parts:'+name;libs[embedded[1]]=embedded
 specs[name]={'pins':{str(p[0]):{'name':p[1],'type':p[2]} for p in pins},'footprint':foot,'datasheet':ds,'height':h}
 return 'carrier-parts:'+name

def wire(a,b):
 if a==b:return
 items.append(f'(wire (pts (xy {a[0]} {a[1]}) (xy {b[0]} {b[1]})) (stroke (width 0) (type default)) (uuid {q(uid("wire"+str(a)+str(b)))}))')
def label(n,p,angle=0):items.append(f'(label {q(n)} (at {p[0]} {p[1]} {angle}) {eff(just="right bottom" if angle==180 else "left bottom")} (uuid {q(uid("label"+n+str(p)))}))')
def text(t,x,y,size=1.27):items.append(f'(text {q(t)} (at {x} {y} 0) {eff(size,"left top")} (uuid {q(uid("text"+t))}))')
def box(title,x,y,w,h):
 items.append(f'(rectangle (start {x} {y}) (end {x+w} {y+h}) (stroke (width 0.254) (type default) (color 60 110 145 1)) (fill (type none)) (uuid {q(uid(title))}))')
 text(title,x+5.08,y+5.08,1.8)
def place(name,ref,value,x,y,angle=0,foot=None,fields=None):
 a=libs.get(name) or lib(name);fields=fields or {}
 props={p[1]:p[2] for p in nodes(a,'property')}
 fields={'Footprint':foot if foot is not None else props.get('Footprint',''),'Datasheet':props.get('Datasheet',''),'MPN':fields.get('MPN',''),'Manufacturer':fields.get('Manufacturer',''),'Status':'DEVELOPMENT — see REVIEW.md',**fields}
 h=specs.get(name.split(':')[1],{}).get('height',0)
 if name.startswith('carrier-parts:'):
  positions=[(x-15.24,y-h/2-12.7),(x-15.24,y-h/2-10.16)];justify='right'
 else:positions=[(x+3.81,y-1.27),(x+3.81,y+1.27)];justify='left'
 if ref.startswith(('J','SW')) and not name.startswith('carrier-parts:'):
  ppins=[p for u in nodes(a,'symbol') for p in nodes(u,'pin')]
  top=y-max(float(node(p,'at')[2]) for p in ppins) if ppins else y
  positions=[(x,top-7.62),(x,top-5.08)];justify='left'
 if name=='Device:L':positions=[(x,y-7.62),(x,y-5.08)];justify='left'
 pp=''
 for i,(k,v) in enumerate([('Reference',ref),('Value',value),*fields.items()]):
  px,py=positions[i] if i<2 else (x,y)
  pp+=f'(property {q(k)} {q(v)} (at {px} {py} 0) {eff(just=justify)}'+(' (hide yes)' if i>=2 else '')+')'
 board_attr='no' if ref.startswith('#') else 'yes'
 pins=[]
 for unit in nodes(a,'symbol'):pins.extend(nodes(unit,'pin'))
 items.append(f'(symbol (lib_id {q(name)}) (at {x} {y} {angle}) (unit 1) (in_bom {board_attr}) (on_board {board_attr}) (dnp no) (uuid {q(uid(ref))}) {pp} '+''.join(f'(pin {q(node(p,"number")[1])} (uuid {q(uid(ref+node(p,"number")[1]))}))' for p in pins)+f'(instances (project "carrier" (path {q(instance_path)} (reference {q(ref)}) (unit 1)))))')
 pos={}
 for p in pins:
  at=node(p,'at');px,py,pa=map(float,at[1:]);r=math.radians(angle)
  xx=x+px*math.cos(r)-py*math.sin(r); yy=y-px*math.sin(r)-py*math.cos(r)
  pos[node(p,'number')[1]]=(round(xx,6),round(yy,6),(pa+angle)%360)
 placed[ref]=pos
 return pos

def connect(ref,pin,net,length=5.08):
 p=placed[ref][str(pin)];r=math.radians(p[2]);end=(round(p[0]-length*math.cos(r),6),round(p[1]+length*math.sin(r),6))
 wire(p[:2],end);label(net,end,180 if p[2]==0 else (0 if p[2] in (180,90) else 90))
 nets.setdefault(net,[]).append([ref,str(pin)])
def allpins(ref,mapping):
 groups={}
 for n,net in mapping.items():
  p=placed[ref][str(n)]
  if net is None:
   items.append(f'(no_connect (at {p[0]} {p[1]}) (uuid {q(uid("nc"+ref+str(n)))}))')
  elif p[2] in (90,270):groups.setdefault((net,p[2]),[]).append(str(n))
  else:connect(ref,n,net)
 for (net,angle),ps in groups.items():
  if len(ps)==1:connect(ref,ps[0],net);continue
  points=[]
  for pin in ps:
   p=placed[ref][pin]; end=(p[0],round(p[1]+(5.08 if angle==90 else -5.08),6))
   wire(p[:2],end); points.append(end);nets.setdefault(net,[]).append([ref,pin])
  points.sort();wire(points[0],points[-1]);label(net,points[0],0 if angle==90 else 90)
  for p in points[1:-1]:items.append(f'(junction (at {p[0]} {p[1]}) (diameter 0) (color 0 0 0 0) (uuid {q(uid("junction"+str(p)))}))')
def passive(kind,ref,val,x,y,top,bottom,foot='',fields=None):
 from passive_parts import selection
 selected_foot,selected_fields=selection(kind,ref,val)
 if kind=='C' and '/ 10V' in val:val=val.replace('/ 10V','/ 25V' if val.startswith('22u ') else '/ 50V')
 place('Device:'+kind,ref,val,x,y,angle=90 if kind=='L' else 0,foot=foot or selected_foot or ('Resistor_SMD:R_0603_1608Metric' if kind=='R' else 'Capacitor_SMD:C_0805_2012Metric'),fields={**selected_fields,**(fields or {})})
 allpins(ref,{1:top,2:bottom})
def R(ref,val,x,y,a,b):passive('R',ref,val,x,y,a,b)
def C(ref,val,x,y,a,b,foot='',fields=None):passive('C',ref,val,x,y,a,b,foot,fields)

instance_path='/' + rootid

def reset_sheet(name):
 global items,placed,nets,rootid,instance_path
 items=[];placed={};nets={}
 rootid=uid(name)
 instance_path='/'+uid('carrier')+'/'+uid('sheet-'+name)

def save_sheet(name,title,paper="A2"):
 content='(kicad_sch (version 20250114) (generator "eeschema") (uuid '+q(rootid)+') (paper '+q(paper)+') (title_block (title '+q(title)+') (rev "PLACEMENT1") (comment 1 "Unrouted prototype — qualification gates in REVIEW.md")) (lib_symbols '+''.join(sx.dumps(a) for a in libs.values())+') '+''.join(items)+')'
 (ROOT/(name+'.kicad_sch')).write_text(content)
 return dict(nets)

def local_path(net, first, second, bends=()):
 """Replace two label stubs with a visible orthogonal connection, retaining its net name."""
 terminals=[placed[ref][str(pin)] for ref,pin in (first,second)]
 stubs=[]
 for p in terminals:
  angle=math.radians(p[2]);end=(round(p[0]-5.08*math.cos(angle),6),round(p[1]+5.08*math.sin(angle),6))
  stubs.append((p[:2],end))
 kept=[]
 for item in items:
  a=sx.loads(item);kind=str(a[0])
  if kind in ('label','global_label') and a[1]==net and tuple(node(a,'at')[1:3]) in [e for _,e in stubs]:continue
  if kind=='wire':
   points=[tuple(v[1:3]) for v in node(a,'pts')[1:]]
   if any(points==[p,e] or points==[e,p] for p,e in stubs):continue
  kept.append(item)
 items[:]=kept
 points=[terminals[0][:2],*bends,terminals[1][:2]]
 for a,b in zip(points,points[1:]):
  assert a[0]==b[0] or a[1]==b[1],(net,a,b)
  wire(a,b)
 label(net,points[1] if bends else ((points[0][0]+points[-1][0])/2,(points[0][1]+points[-1][1])/2))
