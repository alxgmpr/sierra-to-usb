"""Fresh placement-only PCB, derived from exported schematic. Never imports routing."""
from pathlib import Path
import json, math, sys, uuid, xml.etree.ElementTree as ET
import sexpdata as sx
P=Path(__file__).resolve().parent
sys.path.insert(0,str(P.parent/'tools'))
from generation_guard import preflight,record
S=sx.Symbol
N=lambda k,*v:[S(k),*v]
def nodes(a,k):return [v for v in a if isinstance(v,list) and str(v[0])==k]
def node(a,k):return next(iter(nodes(a,k)),None)
def uid(s):return str(uuid.uuid5(uuid.NAMESPACE_URL,'carrier-placement/'+s))
def load(p):return sx.loads(p.read_text())
outputs=[P/'carrier.kicad_pcb',P/'build/placement-source.json']
preflight(P,'carrier-board',outputs)
root=ET.parse(P/'build/carrier.xml').getroot()
pos=json.loads((P/'placement.json').read_text())
components={c.attrib['ref']:c for c in root.find('components')}
assert set(pos)==set(components),(set(components)-set(pos),set(pos)-set(components))
nets={}
for n in root.find('nets'):
 for p in n.findall('node'):nets[p.attrib['ref'],p.attrib['pin']]=n.attrib['name']
standard=Path('/Applications/KiCad/KiCad.app/Contents/SharedSupport/footprints')
libs={'carrier':P/'carrier.pretty','compact-usb':P.parent/'lib/compact-usb.pretty','sierra-to-usb':P/'reused.pretty'}
# Read only the layer declaration, not any root component or routing geometry.
reference=load(P.parents[1]/'sierra-to-usb.kicad_pcb')
board=[S('kicad_pcb'),N('version',20260206),N('generator','compact-placement'),N('general',N('thickness',1.5)),N('paper','A3'),node(reference,'layers')]
stack=[]
for name,t,th in [('F.Mask','Top Solder Mask',.015),('F.Cu','copper',.035),('dielectric 1','prepreg',.18),('In1.Cu','copper',.018),('dielectric 2','core',1.004),('In2.Cu','copper',.018),('dielectric 3','prepreg',.18),('B.Cu','copper',.035),('B.Mask','Bottom Solder Mask',.015)]:
 layer=N('layer',name,N('type',t),N('thickness',th))
 if t in ('prepreg','core'):layer.extend([N('material','FR408HR — provisional custom stack'),N('epsilon_r',3.61),N('loss_tangent',.009)])
 stack.append(layer)
board.append(N('setup',N('stackup',*stack,N('copper_finish','ENIG'),N('dielectric_constraints',S('yes'))),N('pad_to_mask_clearance',0)))
report=[]
models={'U301':'TI_RPW0010A','SW501':'JS102011SAQN_envelope','SW502':'JS102011SAQN_envelope','Q501':'SOT523_envelope','Q502':'SOT523_envelope','U105':'RSE10_envelope','U401':'LTC3310S_envelope','L401':'XEL4030_envelope','R307':'CSM2512_envelope','D301':'SMF_envelope','J201':'M2_MDT420_Detailed','J202':'IDC_3M_N2520_Detailed',**{r:'T530_D_envelope' for r in ['C405','C406','C415','C416']},**{r:'MHF4_envelope' for r in ['J601','J603','J605','J607','J609']}}
def model(name):return N('model','${KIPRJMOD}/models/'+name+'.wrl',N('offset',N('xyz',0,0,0)),N('scale',N('xyz',1,1,1)),N('rotate',N('xyz',0,0,0)))
def freshids(a,ref,path=''):
 for i,v in enumerate(a):
  if isinstance(v,list):
   if str(v[0])=='uuid':v[1]=uid(ref+path+str(i))
   else:freshids(v,ref,path+'/'+str(i))
for ref,c in components.items():
 name=c.findtext('footprint');lib,part=name.split(':',1)
 fp=load(libs.get(lib,standard/(lib+'.pretty'))/(part+'.kicad_mod'))
 fp[1]=name
 # One reference per component in the assembly drawing; suppress duplicate template text.
 fp[:]=[v for v in fp if not(isinstance(v,list) and str(v[0])=='fp_text' and len(v)>2 and v[2] in ('${REFERENCE}','${VALUE}'))]
 fp[:]=[v for v in fp if not(isinstance(v,list) and str(v[0]) in ('version','generator','generator_version','at','path','sheetname','sheetfile','uuid','locked'))]
 x,y,a=pos[ref]
 fp.extend([N('at',x,y,a),N('uuid',uid(ref)),N('path',c.find('sheetpath').attrib['tstamps']+c.findtext('tstamps')),N('sheetname',c.find('sheetpath').attrib['names'])])
 if ref.startswith('J') or ref.startswith('SW'):fp.append(N('locked',S('yes')))
 fp[:]=[v for v in fp if not(isinstance(v,list) and str(v[0])=='property' and v[1] not in ('Reference','Value'))]
 for field in c.find('fields'):
  if field.attrib['name'] not in ('Footprint',):
   fp.append(N('property',field.attrib['name'],field.text or '',N('at',0,0),N('layer','F.Fab'),N('hide',S('yes')),N('effects',N('font',N('size',1,1)))))
 if ref.startswith('TP'):
  attr=node(fp,'attr')
  attr[:]=[v for v in attr if str(v)!='exclude_from_bom']
 for p in nodes(fp,'property'):
  if p[1]=='Reference':
   p[2]=ref
   node(p,'layer')[1]='F.Fab'
   font=node(node(p,'effects'),'font');node(font,'size')[1:]=[.7,.7]
   if node(font,'thickness'):node(font,'thickness')[1]=.1
  elif p[1]=='Value':p[2]=c.findtext('value');p.append(N('hide',S('yes')))

 for pad in nodes(fp,'pad'):
  pad[:]=[v for v in pad if not(isinstance(v,list) and str(v[0])=='net')]
  if (ref,str(pad[1])) in nets:pad.append(N('net',nets[ref,str(pad[1])]))
  # KiCad 20260206 stores pad angles relative to the footprint.

 # Existing package models remain only if their repository path resolves; model qualification is separate.
 if ref in models:
  fp[:]=[v for v in fp if not(isinstance(v,list) and str(v[0])=='model')]
  fp.append(model(models[ref]))
 freshids(fp,ref)
 board.append(fp)
 report.append({'ref':ref,'footprint':name,'x_mm':x,'y_mm':y,'rotation_deg':a,'locked':ref.startswith(('J','SW'))})
def rect(x1,y1,x2,y2,layer,width=.1):
 board.append(N('gr_rect',N('start',x1,y1),N('end',x2,y2),N('stroke',N('width',width),N('type',S('default'))),N('fill',S('none')),N('layer',layer),N('uuid',uid(str((x1,y1,x2,y2,layer))))))
def text(t,x,y,layer='Dwgs.User',size=1):
 board.append(N('gr_text',t,N('at',x,y),N('layer',layer),N('effects',N('font',N('size',size,size),N('thickness',.15))),N('uuid',uid(t))))
# Four equal R4 mounting ears; R1 neck fillets preserve all connector edge datums.
def edge(kind,points):
 board.append(N(kind,*[N(k,*pt) for k,pt in zip(['start','mid','end'] if kind=='gr_arc' else ['start','end'],points)],N('stroke',N('width',.05),N('type',S('default'))),N('layer','Edge.Cuts'),N('uuid',uid(str(points)))))
for kind,points in [
 ('gr_line',[(9,0),(101,0)]),('gr_arc',[(101,0),(101.707107,-.292893),(102,-1)]),
 ('gr_line',[(102,-1),(102,-3)]),('gr_arc',[(102,-3),(106,-7),(110,-3)]),
 ('gr_line',[(110,-3),(110,103)]),('gr_arc',[(110,103),(106,107),(102,103)]),
 ('gr_line',[(102,103),(102,101)]),('gr_arc',[(102,101),(101.707107,100.292893),(101,100)]),
 ('gr_line',[(101,100),(9,100)]),('gr_arc',[(9,100),(8.292893,100.292893),(8,101)]),
 ('gr_line',[(8,101),(8,103)]),('gr_arc',[(8,103),(4,107),(0,103)]),
 ('gr_line',[(0,103),(0,-3)]),('gr_arc',[(0,-3),(4,-7),(8,-3)]),
 ('gr_line',[(8,-3),(8,-1)]),('gr_arc',[(8,-1),(8.292893,-.292893),(9,0)])]:edge(kind,points)
text('3052',60,25.75,'F.SilkS',.8)
text('3042',60,35.75,'F.SilkS',.8)
text('FIT ONE M.2 SUPPORT ONLY',55,20.5,'Dwgs.User',.8)
rect(39.775,25.6,70.225,77.90,'Dwgs.User')
text('UNROUTED / BENCH QUALIFICATION REQUIRED',55,19,'F.SilkS',1)
for ref,(x,y,a) in pos.items():
 if ref.startswith('TP'):text(ref,x,y-1.8 if y>=98 else y+1.8,'F.SilkS',.8)
for label,x in zip(['RF1','RF2','RF3','RF4','GPS'],[15,35,55,75,95]):text(label,x,8,'F.SilkS')
for t,x,y in [('POWER',101,29),('RUN',101,44),('RESET',101,59),('RF OFF',101,70),('USB-C',55,98),('SIM',10,70),('PROFILE — USB OFF TO CHANGE',90,97)]:text(t,x,y,'F.SilkS',.8)
# Mechanical holes are board-only, deliberately excluded from schematic parity/BOM.
for ref,x,y,d in [('H1',4,-3,2.7),('H2',106,-3,2.7),('H3',4,103,2.7),('H4',106,103,2.7),('H5',55,25.75,2.2),('H10',55,35.75,2.2)]:
 fp=N('footprint',ref,N('layer','F.Cu'),N('at',x,y),N('locked',S('yes')),N('uuid',uid(ref)),N('attr',S('board_only'),S('exclude_from_pos_files'),S('exclude_from_bom')),N('property','Reference',ref,N('at',0,-3),N('layer','F.SilkS'),N('effects',N('font',N('size',.8,.8),N('thickness',.12)))),N('pad','',S('np_thru_hole'),S('circle'),N('at',0,0),N('size',d,d),N('drill',d),N('layers','*.Cu','*.Mask')))
 if ref=='H5':fp.append(model('M2_support_assembly'))
 board.append(fp)
for ref,x,y,name in [('MECH1',55,25.75,'RM520N_GL_Detailed')]:
 board.append(N('footprint',ref,N('layer','F.Cu'),N('at',x,y),N('locked',S('yes')),N('uuid',uid(ref)),N('attr',S('board_only'),S('exclude_from_pos_files'),S('exclude_from_bom')),N('property','Reference',ref,N('at',0,0),N('layer','F.Fab'),N('hide',S('yes')),N('effects',N('font',N('size',1,1)))),model(name)))
# Rule-area holes reserve screw/washer clearance on both faces, with no copper fill.
for x,y,r in [(4,-3,3),(106,-3,3),(4,103,3),(106,103,3),(55,25.75,3),(55,35.75,3)]:
 pts=[N('xy',round(x+r*math.cos(i*math.pi/12),4),round(y+r*math.sin(i*math.pi/12),4)) for i in range(24)]
 board.append(N('zone',N('net',''),N('layers','F.Cu','In1.Cu','In2.Cu','B.Cu'),N('uuid',uid('keepout'+str((x,y)))),N('hatch',S('edge'),.5),N('connect_pads',N('clearance',0)),N('min_thickness',.25),N('keepout',N('tracks',S('not_allowed')),N('vias',S('not_allowed')),N('pads',S('allowed')),N('copperpour',S('not_allowed')),N('footprints',S('not_allowed'))),N('polygon',N('pts',*pts))))
# Conservative front-side no-copper reserve covering nano-SIM exposed contact areas.
board.append(N('zone',N('net',''),N('layer','F.Cu'),N('uuid',uid('SIM-contact-keepout')),N('hatch',S('edge'),.5),N('connect_pads',N('clearance',0)),N('min_thickness',.25),N('keepout',N('tracks',S('not_allowed')),N('vias',S('not_allowed')),N('pads',S('allowed')),N('copperpour',S('not_allowed')),N('footprints',S('allowed'))),N('polygon',N('pts',*[N('xy',x,y) for x,y in [(3.7,74.3),(12.6,74.3),(12.6,85.8),(3.7,85.8)]]))))
outputs[0].write_text(sx.dumps(board)+'\n')
outputs[1].write_text(json.dumps({'source':'build/carrier.xml','components':report,'board_mm':[110,114,1.5],'tracks':0,'vias':0,'filled_zones':0,'stage':'reviewed deliberate placement; entirely unrouted; qualification gates in REVIEW.md'},indent=2)+'\n')
record(P,'carrier-board',outputs)
print('Created',len(components),'schematic footprints and 6 mechanical holes; no routing.')
