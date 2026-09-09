"""Deterministic KiCad power-circuit capture. Run using compact/.venv/bin/python."""
from pathlib import Path
import math, json, uuid, copy
import sexpdata as sx
ROOT=Path(__file__).resolve().parents[1]
from generation_guard import preflight, record
OUTPUTS=[ROOT/p for p in ['lib/compact-power.kicad_sym', 'sym-lib-table', 'energy-storage.kicad_sch', 'reference/power-pin-map.json', 'reference/intended-nets.json']]
preflight(ROOT, 'power-schematic', OUTPUTS)
STD=Path('/Applications/KiCad/KiCad.app/Contents/SharedSupport/symbols')
S=sx.Symbol
def uid(key):return str(uuid.uuid5(uuid.NAMESPACE_URL,'compact-usb-power/'+key))
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
 custom[name]=sym;embedded=copy.deepcopy(sym);embedded[1]='compact-power:'+name;libs[embedded[1]]=embedded
 specs[name]={'pins':{str(p[0]):{'name':p[1],'type':p[2]} for p in pins},'footprint':foot,'datasheet':ds,'height':h}
 return 'compact-power:'+name

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
 fields={'Footprint':foot if foot is not None else props.get('Footprint',''),'Datasheet':props.get('Datasheet',''),'MPN':fields.get('MPN',''),'Manufacturer':fields.get('Manufacturer',''),'Status':'ENGINEERING PROTOTYPE — see power-design-review.md',**fields}
 h=specs.get(name.split(':')[1],{}).get('height',0)
 if name.startswith('compact-power:'):
  positions=[(x-15.24,y-h/2-12.7),(x-15.24,y-h/2-10.16)];justify='right'
 else:positions=[(x+3.81,y-1.27),(x+3.81,y+1.27)];justify='left'
 pp=''
 for i,(k,v) in enumerate([('Reference',ref),('Value',value),*fields.items()]):
  px,py=positions[i] if i<2 else (x,y)
  pp+=f'(property {q(k)} {q(v)} (at {px} {py} 0) {eff(just=justify)}'+(' (hide yes)' if i>=2 else '')+')'
 pins=[]
 for unit in nodes(a,'symbol'):pins.extend(nodes(unit,'pin'))
 items.append(f'(symbol (lib_id {q(name)}) (at {x} {y} {angle}) (unit 1) (in_bom yes) (on_board yes) (dnp no) (uuid {q(uid(ref))}) {pp} '+''.join(f'(pin {q(node(p,"number")[1])} (uuid {q(uid(ref+node(p,"number")[1]))}))' for p in pins)+f'(instances (project "energy-storage" (path {q("/"+rootid)} (reference {q(ref)}) (unit 1)))))')
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
 place('Device:'+kind,ref,val,x,y,foot=foot or ('Resistor_SMD:R_0603_1608Metric' if kind=='R' else 'Capacitor_SMD:C_0805_2012Metric'),fields=fields)
 allpins(ref,{1:top,2:bottom})
def R(ref,val,x,y,a,b):passive('R',ref,val,x,y,a,b)
def C(ref,val,x,y,a,b,foot='',fields=None):passive('C',ref,val,x,y,a,b,foot,fields)

# Custom library pin maps transcribed from manufacturer pin-function tables.
efu=ic('TPS259470LRPWR',[(5,'IN','power_in','T'),(6,'OUT','power_out','R'),(1,'EN/UVLO','input','L'),(2,'OVLO','input','L'),(7,'dVdt','output','L'),(9,'ILM','passive','R'),(10,'ITIMER','passive','R'),(4,'~{FLT}','open_collector','R'),(3,'AUXOFF','open_collector','R'),(8,'GND','power_in','B')],'compact-usb:TI_RPW0010A','https://www.ti.com/lit/ds/symlink/tps25947.pdf','OVLO, current-limiting, reverse-blocking eFuse; latch-off fault option')
chg=ic('LTC3128IFE',[(11,'VIN','power_in','T'),(5,'RSENP','passive','L'),(6,'RSENS','passive','L'),(7,'RUN','input','L'),(8,'PROG','passive','L'),(14,'PFI','input','L'),(15,'MAXV','passive','L'),(1,'SW1','passive','T'),(4,'SW1','passive','T'),(23,'SW2','passive','T'),(24,'SW2','passive','T'),(20,'VOUTP','power_out','R'),(21,'VOUTP','passive','R'),(19,'VOUTS','input','R'),(18,'MID','passive','R'),(16,'FB','input','R'),(17,'PGOOD','open_collector','R'),(13,'PFO','open_collector','R'),(2,'GND','power_in','B'),(3,'GND','passive','B'),(12,'GND','passive','B'),(25,'EP_GND','passive','B'),(9,'NC_GND','passive','B'),(10,'NC_GND','passive','B'),(22,'NC_GND','passive','B')],'compact-usb:LTC_FE24_AA','https://www.analog.com/media/en/technical-documentation/data-sheets/3128f.pdf','Buck-boost supercapacitor charger, input-current regulation and active two-cell balancing')
buck=ic('TPS62816QWRWYRQ1',[(2,'VIN','power_in','T'),(3,'SW','power_out','R'),(5,'FB','input','R'),(9,'PG','open_collector','R'),(8,'EN','input','L'),(1,'MODE/SYNC','input','L'),(7,'COMP/FSET','input','L'),(6,'SS/TR','passive','L'),(4,'GND','power_in','B')],'compact-usb:TI_RWY0009A','https://www.ti.com/lit/ds/symlink/tps62816-q1.pdf','6 A buck; programmable compensation and soft start')
sup=ic('TPS3808G01DBVR',[(6,'VDD','power_in','T'),(5,'SENSE','input','L'),(3,'~{MR}','input','L'),(4,'CT','passive','L'),(1,'~{RESET}','open_collector','R'),(2,'GND','power_in','B')],'Package_TO_SOT_SMD:SOT-23-6','https://www.ti.com/lit/ds/symlink/tps3808.pdf','Adjustable voltage supervisor; asynchronous brownout shutdown')
ldo=ic('TPS7A2033PDBVR',[(1,'IN','power_in','L'),(3,'EN','input','L'),(5,'OUT','power_out','R'),(4,'NC','no_connect','R'),(2,'GND','power_in','B')],'Package_TO_SOT_SMD:SOT-23-5','https://www.ti.com/lit/ds/symlink/tps7a20.pdf','3.3 V auxiliary LDO supplied only from protected input')
ff=ic('SN74LVC1G74DCUR',[(8,'VCC','power_in','T'),(2,'D','input','L'),(1,'CLK','input','L'),(6,'~{CLR}','input','L'),(7,'~{PRE}','input','L'),(5,'Q','output','R'),(3,'~{Q}','output','R'),(4,'GND','power_in','B')],'Package_SO:VSSOP-8_2.3x2mm_P0.5mm','https://www.ti.com/lit/ds/symlink/sn74lvc1g74.pdf','Manual-start latch; brownout clears without automatic retry')
buf=ic('SN74LVC1G17DBVR',[(5,'VCC','power_in','T'),(2,'A','input','L'),(4,'Y','output','R'),(1,'NC','no_connect','L'),(3,'GND','power_in','B')],'Package_TO_SOT_SMD:SOT-23-5','https://www.ti.com/lit/ds/symlink/sn74lvc1g17.pdf','Schmitt buffer for debounced start button')

box('1  USB INPUT PROTECTION / CURRENT AUTHORIZATION',15.24,20.32,266.7,157.48)
place('Connector_Generic:Conn_01x03','J1','USB-C FRONT-END INTERFACE',53.34,48.26,foot='Connector_PinHeader_2.54mm:PinHeader_1x03_P2.54mm_Vertical')
allpins('J1',{1:'USB_VBUS',2:'USB_3A_OK',3:'BUF_GND'})
text('J1 is an integration boundary, NOT a second USB port.\nUSB_3A_OK must be asserted only by the sole CC owner\nafter valid 5 V / 3 A advertisement (or valid 5 V contract).\nDefault / 1.5 A / absent cable: keep low; modem stays off.',22.86,76.2)
place(efu,'U1','TPS259470L',134.62,60.96,fields={'MPN':'TPS259470LRPWR','Manufacturer':'Texas Instruments'})
allpins('U1',{5:'USB_VBUS',6:'USB_PROTECTED',1:'USB_3A_OK',2:'USB_OV_SENSE',7:'INPUT_SLEW',9:'INPUT_ILM',10:None,4:'INPUT_FAULT_N',3:'INPUT_VALID',8:'BUF_GND'})
C('C3','1u / 50V X7R',48.26,119.38,'USB_VBUS','BUF_GND')
R('R1','100k',86.36,119.38,'USB_3A_OK','BUF_GND')
R('R2','340k 0.1%',124.46,104.14,'USB_VBUS','USB_OV_SENSE')
R('R3','100k 0.1%',124.46,129.54,'USB_OV_SENSE','BUF_GND')
C('C4','10n / 25V C0G',162.56,119.38,'INPUT_SLEW','BUF_GND')
R('R4','1.02k 0.1%',203.2,119.38,'INPUT_ILM','BUF_GND')
C('C5','22u / 16V X7R',248.92,119.38,'USB_PROTECTED','BUF_GND','Capacitor_SMD:C_1210_3225Metric')
text('OVLO nominal 5.28 V; tolerance and cable-insertion overshoot require bench verification.\n3.27 A nominal eFuse FAULT limit; LTC3128 controls normal TOTAL average input current.\n10 nF slew capacitor: about 0.2 V/ms. No ITIMER capacitor / no intentional overload window.',22.86,152.4)

box('2  LIVE-SOURCE BUFFER / TWO-CELL PROTECTION',292.1,20.32,284.48,157.48)
place(chg,'U2','LTC3128IFE#PBF',375.92,71.12,fields={'MPN':'LTC3128IFE#PBF','Manufacturer':'Analog Devices'})
allpins('U2',{11:'USB_PROTECTED',5:'USB_SENSED',6:'USB_SENSED',7:'INPUT_VALID',8:'CHG_PROG',14:'BUF_UV_SENSE',15:'CELL_MAXV',1:'CHG_SW1',4:'CHG_SW1',23:'CHG_SW2',24:'CHG_SW2',20:'VCAP_STORE',21:'VCAP_STORE',19:'VCAP_STORE',18:'SC_MID',16:'CHG_FB',17:'CAP_READY',13:'BUF_UV_N',2:'BUF_GND',3:'BUF_GND',12:'BUF_GND',25:'BUF_GND',9:'BUF_GND',10:'BUF_GND',22:'BUF_GND'})
passive('L','L1','3.3u / XAL7030',452.12,43.18,'CHG_SW1','CHG_SW2','Inductor_SMD:L_Coilcraft_XAL7030-332',{'MPN':'XAL7030-332MEC','Manufacturer':'Coilcraft'})
for ref,y,a,b in [('C1',66.04,'VCAP_STORE','SC_MID'),('C2',101.6,'SC_MID','BUF_GND')]:
 passive('C_Polarized',ref,'5F / 2.7V',515.62,y,a,b,'compact-usb:Eaton_HV1020_D10.5max_P5.0mm',{'MPN':'HV1020-2R7505-R','Manufacturer':'Eaton','DigiKey':'283-HV1020-2R7505-R-ND','Datasheet':'https://www.eaton.com/us/en-us/skuPage.HV1020-2R7505-R.html'})
# Cell reversal clamps are secondary protection; no negative-voltage endurance claimed.
for ref,y,a,b in [('D1',66.04,'VCAP_STORE','SC_MID'),('D2',101.6,'SC_MID','BUF_GND')]:
 place('Device:D_Schottky',ref,'SS34',556.26,y,angle=270,foot='Diode_SMD:D_SMA',fields={'MPN':'SS34','Manufacturer':'Vishay','Status':'Secondary reverse-voltage clamp; verify leakage / fault behavior'})
 allpins(ref,{1:a,2:b})
C('C6','22u / 16V X7R',309.88,124.46,'USB_SENSED','BUF_GND','Capacitor_SMD:C_1210_3225Metric')
R('R5','4.02k 0.1%',350.52,124.46,'CHG_PROG','BUF_GND')
C('C7','390p C0G',381,124.46,'CHG_PROG','BUF_GND')
R('R6','125k 0.1%',411.48,124.46,'CELL_MAXV','BUF_GND')
R('R7','600k 0.1%',454.66,109.22,'VCAP_STORE','CHG_FB')
R('R8','100k 0.1%',454.66,134.62,'CHG_FB','BUF_GND')
C('C8','22u / 16V X7R',497.84,137.16,'VCAP_STORE','BUF_GND','Capacitor_SMD:C_1210_3225Metric')
for ref,y,net in [('TP1',53.34,'VCAP_STORE'),('TP2',88.9,'SC_MID'),('TP3',124.46,'BUF_GND')]:
 place('Connector:TestPoint',ref,net,482.6,y,foot='TestPoint:TestPoint_Pad_D2.0mm');allpins(ref,{1:net})
text('4.06 V nominal bank / 2.736 A nominal input / 2.50 V nominal individual-cell ceiling.\nAll modem energy flows through this node. Bank directly supplies the current deficit\nwhile USB remains live. No backup-mode input disconnection or switchover is required.',299.72,154.94)

box('3  MODEM REGULATOR / LOCAL TRANSIENT STORAGE',15.24,190.5,266.7,175.26)
place(buck,'U3','TPS62816-Q1 / 6A',91.44,241.3,fields={'MPN':'TPS62816QWRWYRQ1','Manufacturer':'Texas Instruments'})
allpins('U3',{2:'VCAP_STORE',3:'MODEM_SW',5:'MODEM_FB',9:'MODEM_PG',8:'MODEM_ENABLE',1:'AUX_3V3',7:'MODEM_FSET',6:'MODEM_SS',4:'BUF_GND'})
passive('L','L2','0.22u / XAL4020',144.78,231.14,'MODEM_SW','MODEM_VCC','Inductor_SMD:L_Coilcraft_XAL4020-XXX',{'MPN':'XAL4020-221MEC','Manufacturer':'Coilcraft'})
C('C9','22u / 16V X7R',35.56,243.84,'VCAP_STORE','BUF_GND','Capacitor_SMD:C_1210_3225Metric')
R('R9','82.5k 0.1%',43.18,297.18,'MODEM_FSET','BUF_GND')
C('C10','100n / 10V X7R',83.82,297.18,'MODEM_SS','BUF_GND')
R('R10','47.5k 0.1%',129.54,276.86,'MODEM_VCC','MODEM_FB')
R('R11','10.2k 0.1%',129.54,307.34,'MODEM_FB','BUF_GND')
C('C11','5.6p C0G',170.18,276.86,'MODEM_VCC','MODEM_FB')
for ref,x in [('C12',190.5),('C13',226.06)]:
 passive('C_Polarized',ref,'150u / 6.3V',x,233.68,'MODEM_VCC','BUF_GND','Capacitor_Tantalum_SMD:CP_EIA-7343-31_Kemet-D',{'MPN':'T520D157M006ATE015','Manufacturer':'KEMET','Rating':'15 mOhm ESR; +/-20%; confirm exact datasheet before release'})
for ref,x in [('C14',190.5),('C15',226.06),('C16',261.62)]:C(ref,'22u / 10V X7R',x,297.18,'MODEM_VCC','BUF_GND','Capacitor_SMD:C_1210_3225Metric')
place('Connector_Generic:Conn_01x02','J2','MODEM RAIL',251.46,238.76,foot='Connector_PinHeader_2.54mm:PinHeader_1x02_P2.54mm_Vertical');allpins('J2',{1:'MODEM_VCC',2:'BUF_GND'})
R('R12','100k',43.18,332.74,'MODEM_ENABLE','BUF_GND')
R('R13','10k',88.9,332.74,'MODEM_VCC','BUF_GND')
text('3.394 V nominal; 2.18 MHz, compensation 2; 6 ms nominal soft start.\nEffective local ceramic C >= 26.4 uF. Total output C incl. module MUST stay <= 470 uF.\nTwo 150 uF polymer parts are provisional; validate ESR, loop stability and module capacitance.\n5 A is a prototype load-test envelope, NOT a verified RM551E requirement.',119.38,330.2)

box('4  BROWNOUT LATCH / MANUAL START AND STOP',292.1,190.5,284.48,175.26)
place(ldo,'U4','TPS7A2033',345.44,223.52,fields={'MPN':'TPS7A2033PDBVR','Manufacturer':'Texas Instruments'});allpins('U4',{1:'USB_PROTECTED',3:'USB_PROTECTED',5:'AUX_3V3',4:None,2:'BUF_GND'})
C('C17','1u / 10V X7R',309.88,259.08,'USB_PROTECTED','BUF_GND')
C('C18','1u / 10V X7R',342.9,259.08,'AUX_3V3','BUF_GND')
place(sup,'U5','TPS3808G01',419.1,241.3,fields={'MPN':'TPS3808G01DBVR','Manufacturer':'Texas Instruments'});allpins('U5',{6:'AUX_3V3',5:'BANK_SENSE',3:'USB_3A_OK',4:None,1:'LATCH_CLEAR_N',2:'BUF_GND'})
R('R14','787k 0.1%',386.08,266.7,'VCAP_STORE','BANK_SENSE')
R('R15','100k 0.1%',386.08,292.1,'BANK_SENSE','BUF_GND')
C('C19','100n',441.96,269.24,'AUX_3V3','BUF_GND')
R('R16','10k',426.72,302.26,'AUX_3V3','LATCH_CLEAR_N')
place(ff,'U6','SN74LVC1G74',513.08,228.6,fields={'MPN':'SN74LVC1G74DCUR','Manufacturer':'Texas Instruments'});allpins('U6',{8:'AUX_3V3',2:'CAP_READY',1:'START_CLK',6:'LATCH_CLEAR_N',7:'AUX_3V3',5:'MODEM_ENABLE',3:None,4:'BUF_GND'})
R('R17','10k',474.98,279.4,'AUX_3V3','CAP_READY')
R('R18','10k',513.08,279.4,'AUX_3V3','INPUT_VALID')
C('C20','100n',548.64,279.4,'AUX_3V3','BUF_GND')
place(buf,'U7','SN74LVC1G17',497.84,330.2,fields={'MPN':'SN74LVC1G17DBVR','Manufacturer':'Texas Instruments'});allpins('U7',{5:'AUX_3V3',2:'START_RC',4:'START_CLK',1:None,3:'BUF_GND'})
R('R19','100k',325.12,309.88,'START_RC','BUF_GND')
C('C21','100n',358.14,309.88,'START_RC','BUF_GND')
R('R20','1k',322.58,340.36,'START_SW','START_RC')
place('Switch:SW_Push','SW1','START',381,340.36,foot='Button_Switch_SMD:SW_SPST_TL3342');allpins('SW1',{1:'AUX_3V3',2:'START_SW'})
place('Switch:SW_Push','SW2','STOP',434.34,340.36,foot='Button_Switch_SMD:SW_SPST_TL3342');allpins('SW2',{1:'LATCH_CLEAR_N',2:'BUF_GND'})
C('C22','100n',551.18,332.74,'AUX_3V3','BUF_GND')
# Spare independent low-voltage telemetry from LTC3128 PFI (not used for latch timing).
R('R21','536k 0.1%',535.94,137.16,'VCAP_STORE','BUF_UV_SENSE')
R('R22','100k 0.1%',558.8,137.16,'BUF_UV_SENSE','BUF_GND')
text('Bank UV trip ~3.59 V clears latch. Recharge alone cannot restart the modem.\nPress START only after CAP_READY; STOP directly clears the latch.\nMCU not required. Removal of current authorization asserts supervisor manual reset.',299.72,350.52)
for ref,x,y,net in [('TP4',226.06,60.96,'INPUT_FAULT_N'),('TP5',254,332.74,'MODEM_PG'),('TP6',439.42,73.66,'BUF_UV_N')]:
 place('Connector:TestPoint',ref,net,x,y,foot='TestPoint:TestPoint_Pad_D2.0mm');allpins(ref,{1:net})
place('Device:D_TVS','D3','SMBJ6.0A',68.58,119.38,angle=270,foot='Diode_SMD:D_SMB',fields={'MPN':'SMBJ6.0A','Manufacturer':'Littelfuse'})
allpins('D3',{1:'USB_VBUS',2:'BUF_GND'})
# Wire the physical stack continuously, retaining midpoint labels for controller cross-references.
wire(placed['C1']['2'][:2],placed['C2']['1'][:2])
for top,bottom in [('R2','R3'),('R7','R8'),('R10','R11'),('R14','R15')]:
 wire(placed[top]['2'][:2],placed[bottom]['1'][:2])
text('REJECTED FOR LOW-LINE 3A OPERATION — candidate power subsection; do not place or fabricate this circuit.',20.32,378.46,1.8)
text('See compact/review/power-alternatives.md and compatibility-matrix.md. Full carrier schematic and placement are incomplete.',20.32,388.62)
# Explicit power flags only at externally supplied input and passive internal sense output.
for i,(net,x,y) in enumerate([('USB_VBUS',238.76,48.26),('BUF_GND',261.62,48.26),('USB_SENSED',309.88,43.18)]):
 ref='#FLG'+str(i+1);place('power:PWR_FLAG',ref,'PWR_FLAG',x,y);allpins(ref,{1:net})
# Embed definitions and save external custom library so ERC can compare the exact pin map.
(ROOT/'lib/compact-power.kicad_sym').write_text('(kicad_symbol_lib (version 20251024) (generator "kicad_symbol_editor")\n'+'\n'.join(sx.dumps(x) for x in custom.values())+'\n)\n')
(ROOT/'sym-lib-table').write_text('(sym_lib_table (version 7) (lib (name "compact-power") (type "KiCad") (uri "${KIPRJMOD}/lib/compact-power.kicad_sym") (options "") (descr "Datasheet-verified power pin maps")))\n')
content=f'(kicad_sch (version 20250114) (generator "eeschema") (uuid {q(rootid)}) (paper "A2") (title_block (title "Compact cellular carrier — buffered power") (date "2026-09-04") (rev "P0 — review"))\n(lib_symbols '+ '\n'.join(sx.dumps(x) for x in libs.values())+')\n'+'\n'.join(items)+'\n(sheet_instances (path "/" (page "1"))) (embedded_fonts no))\n'
(ROOT/'energy-storage.kicad_sch').write_text(content)
(ROOT/'reference/power-pin-map.json').write_text(json.dumps(specs,indent=2))
(ROOT/'reference/intended-nets.json').write_text(json.dumps(nets,indent=2))
print(len(placed),'symbols captured')

record(ROOT, 'power-schematic', OUTPUTS)
