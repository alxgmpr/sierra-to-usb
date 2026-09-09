"""Isolated carrier capture. Does not write the historical candidate or root project."""
import capture as c
from pathlib import Path
import sys, json, copy
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from generation_guard import preflight,record
P=Path(__file__).resolve().parent
names=['module','usb','power','regulator','protection','controls','service','storage','rf']
outputs=[P/(n+'.kicad_sch') for n in names]+[P/'carrier.kicad_sch',P/'carrier-parts.kicad_sym',P/'sym-lib-table',P/'fp-lib-table',P/'intended-nets.json']

reuse_names=['M.2_Key-B-SMD_Socket_LOTES_APCI0105-P001A','NanoSIM_XKB_XKNANO-113','USB_C_Receptacle_HRO_TYPE-C-31-M-04']
outputs += [P/'reused.pretty'/(n+'.kicad_mod') for n in reuse_names]
preflight(P,'carrier-schematic',outputs)
(P/'reused.pretty').mkdir(exist_ok=True)
for n in reuse_names:
 src=P.parents[1]/'lib/sierra-to-usb.pretty'/(n+'.kicad_mod')
 content=src.read_text().replace('${KIPRJMOD}/lib/', '${KIPRJMOD}/../../lib/')
 if n=='NanoSIM_XKB_XKNANO-113':
  # XKB XKNANO-113 A0 recommended PCB: two0.75mm NPTH holes.
  content=content.replace('(size 0.9 0.9)', '(size 0.75 0.75)').replace('(drill 0.9)', '(drill 0.75)')
 (P/'reused.pretty'/(n+'.kicad_mod')).write_text(content)
# Shared labels make the hierarchy explicit; local node names include stage prefixes.
def gl(n,p,angle=0):
 c.items.append(f'(global_label {c.q(n)} (shape bidirectional) (at {p[0]} {p[1]} {angle}) {c.eff(just="right" if angle==180 else "left")} (uuid {c.q(c.uid("gl"+c.rootid+n+str(p)))}))')
c.label=gl
allnets={}
def ic(name,pins,foot,ds='',mfr=''):
 return c.ic(name,pins,foot,ds,'Manufacturer pin table; development capture')
def put(part,ref,x,y,mapping,mpn=None):
 c.place(part,ref,mpn or part.split(':')[-1],x,y,fields={'MPN':mpn or part.split(':')[-1],'Manufacturer':'Analog Devices' if part.startswith('carrier-parts:LTC') else 'STMicroelectronics' if part.startswith('carrier-parts:STUSB') else 'Amphenol Communications Solutions' if ref=='J201' else 'Texas Instruments'});c.allpins(ref,mapping)
def gate(name):
 return ic(name,[(1,'A','input','L'),(2,'B','input','L'),(4,'Y','output','R'),(5,'VCC','power_in','T'),(3,'GND','power_in','B')],'Package_TO_SOT_SMD:SOT-23-5','https://www.ti.com/lit/ds/symlink/'+name.lower().removesuffix('dbvr')+'.pdf')
andg=gate('SN74LVC1G08DBVR');xorg=gate('SN74LVC1G86DBVR');norg=gate('SN74LVC1G02DBVR')
inv=ic('SN74LVC1G04DBVR',[(2,'A','input','L'),(4,'Y','output','R'),(5,'VCC','power_in','T'),(3,'GND','power_in','B'),(1,'NC','no_connect','L')],'Package_TO_SOT_SMD:SOT-23-5')
def g(part,ref,x,y,a,b,out,cap):
 put(part,ref,x,y,{1:a,2:b,3:'GND',4:out,5:'AUX_3V3'});c.C(cap,'100n',x+38.1,y+25.4,'AUX_3V3','GND')
def invert(ref,x,y,a,out,cap):
 put(inv,ref,x,y,{1:None,2:a,3:'GND',4:out,5:'AUX_3V3'});c.C(cap,'100n',x+38.1,y+25.4,'AUX_3V3','GND')
def old_symbol(sheet,ref):
 a=c.sx.load(open(P.parents[1]/'sheets'/(sheet+'.kicad_sch')))
 inst=next(x for x in c.nodes(a,'symbol') if any(p[1]=='Reference' and p[2]==ref for p in c.nodes(x,'property')))
 name=c.node(inst,'lib_id')[1]
 sym=copy.deepcopy(next(x for x in c.nodes(c.node(a,'lib_symbols'),'symbol') if x[1]==name));c.libs[name]=sym
 return name,{p[1]:p[2] for p in c.nodes(inst,'property')}
# Module and profile assembly.
c.reset_sheet('module')
pins=[]
active={2:'MODEM_VCC',4:'MODEM_VCC',6:'FCPO_N',7:'MOD_USB_D_P',8:'RF_DISABLE_N',9:'MOD_USB_D_N',20:'PROFILE_PIN20',22:'PROFILE_PIN22',24:'PROFILE_PIN24',28:'PROFILE_PIN28',29:'MOD_TX_N',30:'SIM_RST',31:'MOD_TX_P',32:'SIM_CLK',34:'SIM_DATA',35:'MOD_RX_N',36:'SIM_VDD',37:'MOD_RX_P',38:'PROFILE_PIN38',66:'SIM_DETECT',67:'MODEM_RESET_N',68:'PROFILE_PIN68',70:'MODEM_VCC',72:'MODEM_VCC',74:'MODEM_VCC'}
for n in [3,5,11,27,33,39,45,51,57,71,73,76,77]:active[n]='GND'
for n in list(range(1,12))+list(range(20,78)):
 side='T' if active.get(n)=='MODEM_VCC' else 'B' if active.get(n)=='GND' else 'L' if n%2 else 'R'
 pins.append((n,'P'+str(n),'passive',side))
m2=ic('M2_B_67_CONTACTS',pins,'carrier:M2_B_Amphenol_MDT420_1A','https://cdn.amphenol-cs.com/media/wysiwyg/files/drawing/cmdt420x0x411.pdf')
c.box('MODULE / USB / SIM / PROFILE ISOLATION',15.24,15.24,246.38,195.58)
put(m2,'J201',124.46,111.76,{n:active.get(n) for n in list(range(1,12))+list(range(20,78))},'MDT420B01411')
c.text('EM9190: VCC REQUIRED on 2/4/24/38/68/70/72/74.\nRM520N-GL: 20/22/24/28/38/68 open at profile plug.\nNo PCIe, SIM2 or mmWave connections.\nRM551E excluded. Physical module identity must be checked.',25.4,180.34)
c.box('ONE KEYED 20-CONTACT PROFILE ASSEMBLY',274.32,15.24,299.72,195.58)
hdr='Connector_Generic:Conn_02x10_Odd_Even'
c.place(hdr,'J202','KEYED PROFILE PLUG',373.38,78.74,foot='carrier:IDC_3M_N2520_6002_RB',fields={'MPN':'N2520-6002-RB','Manufacturer':'3M','Mating Part':'89120-0101HA','Datasheet':'https://multimedia.3m.com/mws/media/330367O/3m-four-wall-header-2500-series-ts-0770.pdf','Status':'Build one coded IDC assembly per profile; see profile-assembly.md'})
c.allpins('J202',{1:'PROFILE_PIN24',2:'MODEM_VCC',3:'PROFILE_PIN38',4:'MODEM_VCC',5:'PROFILE_PIN68',6:'MODEM_VCC',7:'PROFILE_PIN20',8:'MODEM_CTRL_1V8',9:'PROFILE_PIN22',10:'MODEM_CTRL_1V8',11:'PROFILE_A',12:'GND',13:'PROFILE_B',14:'GND',15:'PROFILE_ABSENT',16:'GND',17:'PROFILE_PIN28',18:'SIERRA_PLA_STATUS',19:None,20:None})
c.text('SIERRA plug: bridge 1-2, 3-4, 5-6, 7-8, 9-10, 11-12, 15-16, 17-18.\nQUECTEL plug: bridge ONLY 13-14 and 15-16.\nBoth: keyed single assembly; power off before changing.\nNo plug / code 00 / code 11 => PROFILE_OK = 0.\nA wrong module in a valid profile is NOT automatically identified.',287.02,127)
for ref,x,net in [('R201',312.42,'PROFILE_A'),('R202',386.08,'PROFILE_B'),('R203',459.74,'PROFILE_ABSENT')]:c.R(ref,'10k',x,175.26,'AUX_3V3',net)
c.box('HARDWARE VALIDITY / NO SOFTWARE BYPASS',15.24,223.52,558.8,101.6)
g(xorg,'U201',76.2,256.54,'PROFILE_A','PROFILE_B','PROFILE_XOR','C201')
invert('U202',223.52,256.54,'PROFILE_ABSENT','PROFILE_PRESENT','C202')
g(andg,'U203',358.14,256.54,'PROFILE_XOR','PROFILE_PRESENT','PROFILE_OK','C203')
c.R('R204','100k',497.84,266.7,'PROFILE_OK','GND')
c.text('PROFILE_OK is a required hardware term in the main power enable.\nThe profile plug carries every vendor-dependent connection together.',35.56,307.34)
c.box('PHYSICAL NANO-SIM / MODULE-SUPPLIED VOLTAGE',15.24,335.28,558.8,66.04)
sim,props=old_symbol('sim','SIM1')
c.place(sim,'J203','XKNANO-113',99.06,368.3,foot=props['Footprint'],fields={'MPN':'XKNANO-113','Manufacturer':'XKB','LCSC':'C381071'})
c.allpins('J203',{1:'SIM_VDD',2:'SIM_SOCKET_RST',3:'SIM_SOCKET_CLK',4:'SIM_DETECT',5:'GND',6:None,7:'SIM_SOCKET_DATA',8:'GND'})
for ref,x,a,b in [('R205',200.66,'SIM_RST','SIM_SOCKET_RST'),('R206',276.86,'SIM_CLK','SIM_SOCKET_CLK'),('R207',353.06,'SIM_DATA','SIM_SOCKET_DATA')]:c.R(ref,'22R',x,360.68,a,b)
c.R('R208','15k',434.34,360.68,'SIM_VDD','SIM_SOCKET_DATA');c.C('C204','100n',518.16,360.68,'SIM_VDD','GND')
c.text('SIM ESD and 10 pF shunts are on the protection sheet; qualify loading and access.',180.34,386.08)
allnets['module']=c.save_sheet('module','M.2 module, hardware profile and nano-SIM')
# USB input and one CC owner, replacement for unsupported VDD5 architecture.
c.reset_sheet('usb')
c.box('ONE USB-C RECEPTACLE / 5 V ONLY',15.24,15.24,185.42,187.96)
us,props=old_symbol('usb3_data','J1')
c.place(us,'J101','TYPE-C-31-M-04',86.36,99.06,foot=props['Footprint'],fields={'MPN':'TYPE-C-31-M-04','Manufacturer':'HRO','LCSC':'C129018'})
m={p:'GND' for p in ['A1','A12','B1','B12','SH']};m.update({p:'USB_VBUS' for p in ['A4','A9','B4','B9']})
m.update({'A2':'C_TX1_P','A3':'C_TX1_N','A5':'CC1','A6':'USB_D_P','A7':'USB_D_N','A8':None,'A10':'C_RX2_N','A11':'C_RX2_P','B2':'C_TX2_P','B3':'C_TX2_N','B5':'CC2','B6':'USB_D_P','B7':'USB_D_N','B8':None,'B10':'C_RX1_N','B11':'C_RX1_P'})
c.allpins('J101',m)
c.text('A6=B6 and A7=B7 immediately at receptacle.\n3 A only after authorization. No 12 V request.',22.86,182.88)
stpins=[(1,'CC1DB','bidirectional','L'),(2,'CC1','bidirectional','L'),(3,'NU_GND','passive','B'),(4,'CC2','bidirectional','L'),(5,'CC2DB','bidirectional','L'),(6,'RESET','input','L'),(7,'SCL','input','L'),(8,'SDA','bidirectional','L'),(9,'DISCH','open_collector','R'),(10,'GND','power_in','B'),(11,'ATTACH_N','open_collector','R'),(12,'ADDR0','input','L'),(13,'ADDR1','input','L'),(14,'RP_1A5_N','open_collector','R'),(15,'GPIO','open_collector','R'),(16,'VBUS_EN_SNK_N','open_collector','R'),(17,'A_B_SIDE','open_collector','R'),(18,'VBUS_VS_DISCH','input','L'),(19,'ALERT_N','open_collector','R'),(20,'RP_3A_N','open_collector','R'),(21,'VREG_1V2','power_out','R'),(22,'VSYS','power_in','T'),(23,'VREG_2V7','power_out','R'),(24,'VDD','power_in','T'),(25,'EP','passive','B')]
st=ic('STUSB4500LQTR',stpins,'Package_DFN_QFN:QFN-24-1EP_4x4mm_P0.5mm_EP2.6x2.6mm','https://www.st.com/resource/en/datasheet/stusb4500l.pdf')
c.box('CC OWNER / 3 A AUTHORIZATION / ORIENTATION',213.36,15.24,360.68,187.96)
put(st,'U101',314.96,91.44,{1:'CC1',2:'CC1',3:'GND',4:'CC2',5:'CC2',6:'GND',7:'CC_SCL',8:'CC_SDA',9:None,10:'GND',11:'CC_ATTACH_N',12:'GND',13:'GND',14:None,15:'CC_NO_DEBUG',16:'CC_SINK_N',17:'USB_ORIENTATION',18:'CC_VBUS_MON',19:None,20:'CC_3A_N',21:'CC_1V2',22:'AUX_3V3',23:'CC_2V7',24:'USB_VBUS',25:'GND'})
c.R('R101','1k',246.38,157.48,'USB_VBUS','CC_VBUS_MON')
for ref,x,a in [('C101',365.76,'CC_1V2'),('C102',421.64,'CC_2V7'),('C103',477.52,'USB_VBUS'),('C104',533.4,'AUX_3V3')]:c.C(ref,'1u',x,157.48,a,'GND')
c.text('VSYS uses AUX_3V3 for the 4.0 V carrier-input boundary.\nNVM GPIO_CFG MUST be 10b (DEBUG); default 11b inhibits 3 A enable.\nProgram and read back with external I2C jig before bring-up.',223.52,180.34)
c.box('AUTHORIZATION LOGIC / OPEN-DRAIN DEFAULTS',15.24,215.9,558.8,93.98)
for ref,x,net in [('R102',40.64,'CC_3A_N'),('R103',111.76,'CC_SINK_N'),('R104',182.88,'CC_NO_DEBUG'),('R105',254,'USB_ORIENTATION')]:c.R(ref,'10k',x,246.38,'AUX_3V3',net)
g(norg,'U102',360.68,246.38,'CC_3A_N','CC_SINK_N','USB_SOURCE_3A','C105')
g(andg,'U103',490.22,246.38,'USB_SOURCE_3A','CC_NO_DEBUG','USB_3A_OK','C106')
c.text('NVM programming and independent default/fault-state validation remain design gates.',30.48,292.1)
c.box('USB3 MUX / TRANSMITTER COUPLING OWNERSHIP',15.24,320.04,558.8,81.28)
mux=ic('HD3SS3212IRKSR',[(n,p,t,s) for n,p,t,s in [(1,'RSVD1','output','L'),(2,'OEn','input','L'),(3,'A0p','bidirectional','L'),(4,'A0n','bidirectional','L'),(5,'GND','power_in','B'),(6,'VCC','power_in','T'),(7,'A1p','bidirectional','L'),(8,'A1n','bidirectional','L'),(9,'SEL','input','L'),(10,'RSVD2','output','L'),(11,'GND','passive','B'),(12,'C1n','bidirectional','R'),(13,'C1p','bidirectional','R'),(14,'C0n','bidirectional','R'),(15,'C0p','bidirectional','R'),(16,'B1n','bidirectional','R'),(17,'B1p','bidirectional','R'),(18,'B0n','bidirectional','R'),(19,'B0p','bidirectional','R'),(20,'GND','passive','B'),(21,'EP','passive','B')]],'Package_DFN_QFN:WQFN-20-1EP_2.5x4.5mm_P0.5mm_EP1x2.9mm','https://www.ti.com/lit/ds/symlink/hd3ss3212.pdf')
# CC1 => SEL high => port C. CC2 => SEL low => port B.
put(mux,'U104',116.84,358.14,{1:None,2:'USB_MUX_OFF',3:'MOD_TX_P',4:'MOD_TX_N',5:'GND',6:'AUX_3V3',7:'MOD_RX_P',8:'MOD_RX_N',9:'USB_ORIENTATION',10:None,11:'GND',12:'C_RX1_N',13:'C_RX1_P',14:'C_TX1_N',15:'C_TX1_P',16:'C_RX2_N',17:'C_RX2_P',18:'C_TX2_N',19:'C_TX2_P',20:'GND',21:'GND'})
c.C('C107','100n',233.68,350.52,'AUX_3V3','GND')
c.text('Module TX and laptop TX each own their AC coupling.\nNo duplicate series capacitors captured.\nUSB2 isolation and connector ESD are on the protection sheet.\nMUX_OFF must stay high until modem rail and sequencing are valid.\nPowered-off leakage and common-mode closure remain open.',299.72,342.9)
allnets['usb']=c.save_sheet('usb','USB-C authorization and orientation')
# Capture input protection and auxiliary supply before the main power stage.
from power_capture import capture as capture_power
allnets['power']=capture_power(c,ic,put)
from regulator_capture import capture as capture_regulator
allnets['regulator']=capture_regulator(c,ic,put)
from protection_capture import capture as capture_protection
allnets['protection']=capture_protection(c,ic,put)
from controls_capture import capture as capture_controls
allnets['controls'],allnets['service']=capture_controls(c,ic,put,g,andg,invert)
from storage_capture import capture as capture_storage
allnets['storage']=capture_storage(c)
from rf_capture import capture as capture_rf
allnets['rf']=capture_rf(c)
# Root hierarchy.
root=c.uid('carrier');parts=[]
for i,n in enumerate(names):
 x=45.72+(i%3)*177.8;y=60.96+(i//3)*101.6
 parts.append(f'(sheet (at {x} {y}) (size 144.78 60.96) (stroke (width 0.254) (type default)) (fill (color 0 0 0 0)) (uuid {c.q(c.uid("sheet-"+n))}) (property "Sheetname" {c.q(n)} (at {x} {y-2.54} 0) {c.eff(just="left bottom")}) (property "Sheetfile" {c.q(n+".kicad_sch")} (at {x} {y+63.5} 0) {c.eff(just="left top")}) (instances (project "carrier" (path {c.q("/"+root)} (page {c.q(i+2)})))))')
(P/'carrier.kicad_sch').write_text(f'(kicad_sch (version 20250114) (generator "eeschema") (uuid {c.q(root)}) (paper "A2") (title_block (title "Compact USB-C modem carrier — placement review") (rev "PLACEMENT1")) (lib_symbols) '+''.join(parts)+f'(text "UNROUTED PROTOTYPE — bench qualification required. See REVIEW.md." (at 45.72 30.48 0) {c.eff(2,"left")} (uuid {c.q(c.uid("status"))})) (sheet_instances (path "/" (page "1"))))')
(P/'carrier-parts.kicad_sym').write_text('(kicad_symbol_lib (version 20250114) (generator "kicad_symbol_editor") '+''.join(c.sx.dumps(s) for s in c.custom.values())+')')
(P/'sym-lib-table').write_text('(sym_lib_table (version 7) (lib (name "carrier-parts") (type "KiCad") (uri "${KIPRJMOD}/carrier-parts.kicad_sym") (options "") (descr "Development symbols")) (lib (name "sierra-to-usb") (type "KiCad") (uri "${KIPRJMOD}/../../lib/sierra-to-usb.kicad_sym") (options "") (descr "Audited root library")))')
(P/'fp-lib-table').write_text('(fp_lib_table (version 7) (lib (name "carrier") (type "KiCad") (uri "${KIPRJMOD}/carrier.pretty") (options "") (descr "Manufacturer land patterns")) (lib (name "compact-usb") (type "KiCad") (uri "${KIPRJMOD}/../lib/compact-usb.pretty") (options "") (descr "Reviewed power package geometry")) (lib (name "sierra-to-usb") (type "KiCad") (uri "${KIPRJMOD}/reused.pretty") (options "") (descr "Audited root geometry")))')
(P/'intended-nets.json').write_text(json.dumps(allnets,indent=2)+'\n')
record(P,'carrier-schematic',outputs)
print('Captured development hierarchy; power and interface gates remain explicitly open')
