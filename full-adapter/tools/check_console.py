"""Check console pin map, supply separation, idle defaults and connector wiring."""
from pathlib import Path
import json,subprocess,tempfile
from xml.etree import ElementTree as ET
import sexpdata as sx
ROOT=Path(__file__).resolve().parents[1]
CLI='/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli'
def nodes(n,t):return [v for v in n if isinstance(v,list) and str(v[0])==t]
def check(root=ROOT):
 lib=sx.loads((root/'lib/full-adapter.kicad_sym').read_text())
 sym=next(v for v in nodes(lib,'symbol') if v[1]=='TXU0202DCUR')
 pins={nodes(p,'number')[0][1]:(nodes(p,'name')[0][1],str(p[1])) for u in nodes(sym,'symbol') for p in nodes(u,'pin')}
 assert pins=={'1':('B2','input'),'2':('GND','power_in'),'3':('VCCA','power_in'),'4':('A2Y','tri_state'),'5':('A1','input'),'6':('OE','input'),'7':('VCCB','power_in'),'8':('B1Y','tri_state')}
 fp=sx.loads((root/'lib/full-adapter.pretty/TI_TXU0202_DCU0008A.kicad_mod').read_text())
 pads={p[1]:p for p in nodes(fp,'pad')};assert set(pads)==set(pins)
 for i in range(1,9):
  p=pads[str(i)];assert nodes(p,'size')[0][1:3]==[.85,.3]
  assert nodes(p,'at')[0][1:3]==([-1.55,-.75+(i-1)*.5] if i<=4 else [1.55,.75-(i-5)*.5])
 fp=sx.loads((root/'lib/full-adapter.pretty/JST_PH_B4B-PH-SM4-TB.kicad_mod').read_text())
 pads=nodes(fp,'pad');assert len(pads)==6
 for p in pads:
  if p[1]=='MP':assert nodes(p,'size')[0][1:3]==[1.6,3]
  else:
   assert nodes(p,'at')[0][1:3]==[-3+(int(p[1])-1)*2,.5]
   assert nodes(p,'size')[0][1:3]==[1,5.5]
 with tempfile.TemporaryDirectory() as d:
  path=Path(d)/'nets.xml';subprocess.run([CLI,'sch','export','netlist','--format','kicadxml','-o',str(path),str(root/'cad/full-adapter.kicad_sch')],check=True,capture_output=True)
  tree=ET.parse(path);nets={n.get('name'):{(p.get('ref'),p.get('pin')) for p in n.findall('node')} for n in tree.findall('.//nets/net')}
  def local(n):
   found=[v for k,v in nets.items() if k.endswith('/'+n)];assert len(found)==1,(n,found);return found[0]
  assert nets['SOC_UART2_TX_1V8']=={('U1','AH24'),('TP561','1'),('U7','5'),('R622','2')}
  assert nets['SOC_UART2_RX_1V8']=={('U1','AC20'),('TP560','1'),('U7','4'),('R623','2')}
  assert local('CONSOLE_TX_RAW')=={('U7','8'),('R620','1'),('R625','2')}
  assert local('CONSOLE_RX_RAW')=={('U7','1'),('R621','1'),('R624','2')}
  assert local('CONSOLE_TX')=={('R620','2'),('J620','2')}
  assert local('CONSOLE_RX')=={('R621','2'),('J620','3')}
  assert nets['VCC_CONSOLE']=={('U7','7'),('C621','1'),('J620','4'),('R624','1'),('R625','1')}
  assert {('U7','3'),('U7','6'),('C620','1'),('R622','1'),('R623','1')} <= nets['VCC1V8_PMU']
  assert {('U7','2'),('C620','2'),('C621','2'),('J620','1')} <= nets['GND']
  parts={p.get('ref'):p for p in tree.findall('.//components/comp')}
  for ref,mpn,lcsc in [('U7','TXU0202DCUR','C5186957'),('J620','B4B-PH-SM4-TB(LF)(SN)','C160354')]:
   fields={f.get('name'):f.text for f in parts[ref].findall('fields/field')};assert (fields['MPN'],fields['LCSC'])==(mpn,lcsc)
  for ref in ['R620','R621']:assert parts[ref].findtext('value')=='1kR 1%'
  for ref in ['R622','R623','R624','R625']:assert parts[ref].findtext('value')=='10kR 1%'
 return dict(status='CONSOLE_CAPTURE_NOT_RELEASE',translator_pins_checked=8,external_power_separate=True,connector_pinout={'1':'GND','2':'board TX','3':'board RX','4':'adapter 3.3V input'},hardware_tested=False)
if __name__=='__main__':
 result=check();(ROOT/'research/console-validation.json').write_text(json.dumps(result,indent=2)+'\n');print(result)
