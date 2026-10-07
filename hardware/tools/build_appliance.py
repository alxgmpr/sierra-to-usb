#!/usr/bin/env python3
"""Attach current draft sheets under appliance root; keep their standalone contexts."""
from pathlib import Path
import re, uuid
ROOT=Path(__file__).resolve().parents[1]
def uid(key):return str(uuid.uuid5(uuid.NAMESPACE_URL,'sierra-appliance-'+key))
root=uid('root'); rec=uid('recovery'); pmic=uid('pmic'); main=uid('main3v3'); main5=uid('main5v'); processor=uid('processor'); phy=uid('phy'); core=uid('core'); ram=uid('ram'); ddr=uid('ddr')
cpu=uid('cpu'); boot=uid('boot'); host=uid('host'); peripheral=uid('peripheral'); nic=uid('nic'); nicpower=uid('nicpower'); nicinterface=uid('nicinterface'); nicbypass=uid('nicbypass')
import json
poe_roots=json.loads((ROOT/'reference/tida-import/roots.json').read_text())
poeids={n:uid(n) for n in poe_roots}
extra={n:uid(n) for n in ['poe-status','ethernet-ingress','modem-power','modem-socket','modem-interface','modem-bypass']}
for filename,project,oldroot,newpath in [
 ('recovery.kicad_sch','recovery','37b14702-5d54-5543-b96e-899c36eac351',f'/{root}/{rec}'),
 ('supervisor.kicad_sch','recovery','37b14702-5d54-5543-b96e-899c36eac351',f'/{root}/{rec}'),
 ('controls.kicad_sch','recovery','37b14702-5d54-5543-b96e-899c36eac351',f'/{root}/{rec}'),
 ('always-on.kicad_sch','recovery','37b14702-5d54-5543-b96e-899c36eac351',f'/{root}/{rec}'),
 ('main3v3.kicad_sch','main3v3','2e6dd71a-ab95-5ea3-b14d-00e36bba2be3',f'/{root}/{main}'),
 ('main5v.kicad_sch','main5v','67626c44-65b2-5096-88fd-dd5ad98a1eca',f'/{root}/{main5}'),
 ('ddr-power.kicad_sch','ddr-power','16a05598-21a4-5ad2-92a4-949b38fbc8f1',f'/{root}/{ddr}'),
 ('ram.kicad_sch','ram','fe21b9a6-b2db-5231-a3fb-c55eced9f4ac',f'/{root}/{ram}'),
 ('core-power.kicad_sch','core-power','3a5434a2-586b-50f0-b09b-0612ac42cdd1',f'/{root}/{core}'),
 ('phy-power.kicad_sch','phy-power','ca155a7e-d9ea-59e1-bc36-3f46f6f2a8ef',f'/{root}/{phy}'),
 ('processor.kicad_sch','processor','e562e6d7-6054-5734-8bbe-ccdbe844f626',f'/{root}/{processor}'),
 ('pmic.kicad_sch','pmic','152b7cfd-b2ed-5d28-883d-f6de3f0c70ef',f'/{root}/{pmic}'),
 ('cpu-power.kicad_sch','cpu-power',str(uuid.uuid5(uuid.NAMESPACE_URL,'sierra-cpu-power-root')),f'/{root}/{cpu}'),
 ('boot.kicad_sch','boot',str(uuid.uuid5(uuid.NAMESPACE_URL,'sierra-boot-root')),f'/{root}/{boot}'),
 ('host-interface.kicad_sch','host-interface',str(uuid.uuid5(uuid.NAMESPACE_URL,'sierra-host-interface-root')),f'/{root}/{host}'), ('peripheral-power.kicad_sch','peripheral-power',str(uuid.uuid5(uuid.NAMESPACE_URL,'sierra-peripheral-power-root')),f'/{root}/{peripheral}'), ('nic.kicad_sch','nic',str(uuid.uuid5(uuid.NAMESPACE_URL,'sierra-nic-root')),f'/{root}/{nic}'), ('nic-power.kicad_sch','nic-power',str(uuid.uuid5(uuid.NAMESPACE_URL,'sierra-nic-power-root')),f'/{root}/{nicpower}'), ('nic-interface.kicad_sch','nic-interface',str(uuid.uuid5(uuid.NAMESPACE_URL,'sierra-nic-interface-root')),f'/{root}/{nicinterface}'), ('nic-bypass.kicad_sch','nic-bypass',str(uuid.uuid5(uuid.NAMESPACE_URL,'sierra-nic-bypass-root')),f'/{root}/{nicbypass}')]+[(n+'.kicad_sch',n,str(uuid.uuid5(uuid.NAMESPACE_URL,f'sierra-{n}-root')),f'/{root}/{sid}') for n,sid in extra.items()]+[(n+'.kicad_sch',n,old,f'/{root}/{poeids[n]}') for n,old in poe_roots.items()]:
 p=ROOT/filename;s=p.read_text()
 # Remove previously generated project contexts before refreshing them.
 s=re.sub(r' \(project "appliance" \(path "[^"]+" \((?:reference|page) "[^"]+"\)(?: \(unit \d+\))?\)\)', '',s)
 pattern=r'(\(project "'+project+r'" \(path "/'+oldroot+r'([^"]*)" (\((?:reference|page) "[^"]+"\)(?: \(unit \d+\))?)\)\))'
 s=re.sub(pattern,lambda m:m[1]+f' (project "appliance" (path "{newpath}{m[2]}" {m[3]}))',s)
 p.write_text(s)
from capture import Sheet
p=ROOT/'recovery.kicad_sch';text=p.read_text();old=Sheet('recovery','')
for net,y in [('MCU_ETH_POWER_EN',200.66),('ETH_PERST_N',208.28),('MCU_HEALTH_IN',215.9)]:
 old.wire((190.5,y),(124.46,y));old.net(net,(124.46,y))
for item in old.items:text=text.replace(item,'')
for local,net in [('ETH_POWER_EN','MCU_ETH_POWER_EN'),('ETH_RESET_N','ETH_PERST_N'),('HEALTH_IN','MCU_HEALTH_IN'),('MODEM_POWER_EN','MCU_MODEM_POWER_EN'),('MODEM_RESET_N','MODEM_RESET_N'),('MODEM_OFF_N','MODEM_OFF_N')]:
 text=text.replace(f'(label "{local}"',f'(global_label "{net}" (shape passive)')
p.write_text(text)
font='(effects (font (size 1.27 1.27)))'
sheets=[]
for name,file,sid,x,y,page in [('Recovery and always-on supply','recovery.kicad_sch',rec,35.56,35.56,2),('Processor PMIC','pmic.kicad_sch',pmic,157.48,35.56,6),('Main 3.3V','main3v3.kicad_sch',main,35.56,106.68,7),('Main 5V control','main5v.kicad_sch',main5,157.48,106.68,8),('RK3566 processor','processor.kicad_sch',processor,35.56,177.8,9),('USB analog filters','phy-power.kicad_sch',phy,157.48,177.8,10),('Core local bypass','core-power.kicad_sch',core,279.4,106.68,11),('Micron RAM','ram.kicad_sch',ram,279.4,177.8,12),('DDR BUCK3','ddr-power.kicad_sch',ddr,279.4,35.56,13),('CPU dynamic voltage supply','cpu-power.kicad_sch',cpu,401.32,35.56,14),('Boot storage and clock','boot.kicad_sch',boot,401.32,106.68,15),('Host recovery interfaces','host-interface.kicad_sch',host,401.32,177.8,16),('Peripheral supply and feedback','peripheral-power.kicad_sch',peripheral,35.56,248.92,17),('2.5GbE controller','nic.kicad_sch',nic,157.48,248.92,18),('Ethernet power sequencing','nic-power.kicad_sch',nicpower,279.4,248.92,19),('PCIe and power-cycle interfaces','nic-interface.kicad_sch',nicinterface,401.32,248.92,20),('Ethernet local bypass','nic-bypass.kicad_sch',nicbypass,35.56,320.04,21),('PoE active input bridge','poe-input.kicad_sch',poeids['poe-input'],157.48,320.04,22),('PoE PD / Class 6','poe-pd.kicad_sch',poeids['poe-pd'],279.4,320.04,23),('Isolated 12V flyback','poe-flyback.kicad_sch',poeids['poe-flyback'],401.32,320.04,24),('Isolated PoE allocation','poe-status.kicad_sch',extra['poe-status'],35.56,391.16,25),('Ethernet cable ingress','ethernet-ingress.kicad_sch',extra['ethernet-ingress'],157.48,391.16,26),('Modem independent power','modem-power.kicad_sch',extra['modem-power'],279.4,391.16,27),('Modem and SIM sockets','modem-socket.kicad_sch',extra['modem-socket'],401.32,391.16,28),('Modem USB isolation','modem-interface.kicad_sch',extra['modem-interface'],35.56,462.28,29),('Modem local bypass','modem-bypass.kicad_sch',extra['modem-bypass'],157.48,462.28,30)]:
 sheets.append(f'(sheet (at {x} {y}) (size 96.52 50.8) (stroke (width 0.254) (type default)) (fill (color 0 0 0 0)) (uuid "{sid}") (property "Sheetname" "{name}" (at {x} {y-2.54} 0) {font}) (property "Sheetfile" "{file}" (at {x} {y+53.34} 0) {font}) (instances (project "appliance" (path "/{root}" (page "{page}")))))')
(ROOT/'appliance.kicad_sch').write_text(f'(kicad_sch (version 20250114) (generator eeschema) (uuid "{root}") (paper "A1") (title_block (title "Cellular WAN appliance — engineering capture") (date "2026-10-07")) (lib_symbols) '+''.join(sheets)+f' (text "Complete appliance connectivity captured; engineering review.\\nFour module assembly profiles require current controlled guides.\\nFootprint release, layout, isolation, thermal, USB/PCIe and recovery\\nqualification remain required before manufacturing." (at 35.56 551.18 0) (effects (font (size 1.27 1.27)) (justify left)) (uuid "{uid("note")}")) (sheet_instances (path "/" (page "1"))))\n')
print('Generated appliance root and refreshed annotation contexts.')
