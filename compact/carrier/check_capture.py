"""Check exported connectivity and evaluate profile logic from its actual exported nets."""
from pathlib import Path
import xml.etree.ElementTree as ET
import json,itertools
P=Path(__file__).resolve().parent
root=ET.parse(P/'build/carrier.xml').getroot()
pins={}; netnodes={}
for net in root.findall('./nets/net'):
 name=net.attrib['name'];netnodes[name]=[]
 for n in net.findall('node'):
  k=(n.attrib['ref'],n.attrib['pin']);pins[k]=name;netnodes[name].append(k)
checks=[]
def check(ok,msg):
 checks.append({'passed':bool(ok),'check':msg})
 if not ok: raise AssertionError(msg)
def same(a,b):return pins[a]==pins[b]
# Source anchors: Sierra 41113174 Rev8 Table3-1; Quectel V1.0 Table5.
for pin in ['2','4','70','72','74']:
 check(pins['J201',pin]=='MODEM_VCC','Common VCC contact '+pin)
for mp,hp in [('24','1'),('38','3'),('68','5'),('20','7'),('22','9'),('28','17')]:
 check(same(('J201',mp),('J202',hp)),'Vendor-dependent contact '+mp+' reaches profile isolation')
 check(pins['J201',mp] not in ['MODEM_VCC','MODEM_CTRL_1V8','GND'],'No fixed drive on isolated contact '+mp)
for pin in ['1','10','21','23','25','26','40','41','42','43','44','46','47','48','49','50','52','53','54','55','56','58','59','60','61','62','63','64','65','69','75']:
 check(len(netnodes.get(pins.get(('J201',pin)),[]))<=1,'Unused module contact '+pin+' not externally connected')
for a,b in [('A6','B6'),('A7','B7')]:check(same(('J101',a),('J101',b)),'USB2 receptacle join '+a+'/'+b)
check(same(('J201','36'),('J203','1')),'SIM voltage supplied by module pin36')
check(same(('J203','4'),('J201','66')),'Normally closed SIM detect reaches pin66')
# ST DS13102 Rev6 Table1 independently specifies CC/DB pins 1/2 and 4/5.
for a,b,p in [('1','2','A5'),('5','4','B5')]:
 check(same(('U101',a),('U101',b)) and same(('U101',b),('J101',p)),'CC dead-battery termination '+p)
check(pins['U101','22']=='AUX_3V3','STUSB4500L VSYS receives auxiliary 3.3 V')
# TI SLASE74F table: SEL0=A-B; SEL1=A-C. ST CC1=HiZ, CC2=low.
for mod,mux in [('31','3'),('29','4'),('37','7'),('35','8')]:check(same(('J201',mod),('U104',mux)),'Module SS mapping '+mod)
for usb,mux in [('A2','15'),('A3','14'),('B11','13'),('B10','12'),('B2','19'),('B3','18'),('A11','17'),('A10','16')]:check(same(('J101',usb),('U104',mux)),'Orientation path '+usb)
# Evaluate the actual exported gate wiring, including all eight input states.
rows=[]
for a,b,absent in itertools.product([0,1],repeat=3):
 values={'AUX_3V3':1,'GND':0,'PROFILE_A':a,'PROFILE_B':b,'PROFILE_ABSENT':absent}
 for ref,op in [('U201','xor'),('U202','not'),('U203','and')]:
  if op=='not':val=1-values[pins[ref,'2']]
  else:
   aa,bb=values[pins[ref,'1']],values[pins[ref,'2']]
   val=(aa^bb) if op=='xor' else aa&bb
  values[pins[ref,'4']]=val
 expected=int(not absent and a!=b)
 check(values['PROFILE_OK']==expected,f'Profile truth table A={a}, B={b}, absent={absent}')
 rows.append({'A':a,'B':b,'absent':absent,'PROFILE_OK':values['PROFILE_OK']})
# RF harnesses are separate from M.2 edge contacts; no hidden bias or stub load.
for i,(mhf,sma) in enumerate([('J601','J602'),('J603','J604'),('J605','J606'),('J607','J608'),('J609','J610')],1):
 net='RF_GPS' if i==5 else 'RF'+str(i)
 check(set(netnodes.get(net,[]))=={(mhf,'1'),(sma,'1')},f'RF{i} is an isolated two-connector passive path')
 check(pins[mhf,'2']==pins[sma,'2']=='GND',f'RF{i} shields both return to ground')
check(pins['D301','1']=='USB_VBUS' and pins['D301','2']=='GND','Input TVS cathode at VBUS, anode at ground')
check(same(('U301','7'),('R308','1')) and same(('R308','2'),('C302','1')) and pins['C302','2']=='GND','TPS25947 dVdt capacitor includes TI recommended series resistor')
check(same(('R401','2'),('R411','1')) and same(('R411','2'),('U401','18')) and pins['R401','1']=='MODEM_VCC','Buck feedback uses complete precision series top leg')
report={'scope':'Exported module, USB, profile, protection and RF connectivity assertions. Power/controls regression checks are separate; this does not prove analog behavior, physical interlock, mechanical fit or fabrication readiness.','checks':checks,'profile_truth_table':rows,'complete_carrier':False}
(P/'build/capture-checks.json').write_text(json.dumps(report,indent=2)+'\n')
print(len(checks),'capture checks passed; see separate board and handoff reviews')
