#!/usr/bin/env python3
"""Validate and export engineering PDF, native XML and assembly-aware BOM."""
import argparse,csv,json,subprocess
from pathlib import Path
from check_appliance_capture import CLI,ROOT,export,validate
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=True)
subprocess.run([CLI,'sch','erc','--severity-all','--exit-code-violations','--format','json','--output',str(a.output/'erc.json'),str(ROOT/'appliance.kicad_sch')],check=True)
tree=export(ROOT/'appliance.kicad_sch',a.output/'appliance.xml');report=validate(tree,a.output);report['ERC_violations']=0
(a.output/'capture-report.json').write_text(json.dumps(report,indent=2)+'\n')
subprocess.run([CLI,'sch','export','pdf','--output',str(a.output/'appliance.pdf'),str(ROOT/'appliance.kicad_sch')],check=True)
rows=[]
for c in tree.findall('./components/comp'):
 fields={f.get('name'):f.text or '' for f in c.findall('./fields/field')};ref=c.get('ref');dnp=c.find('property[@name="dnp"]') is not None
 rows.append({'Reference':ref,'Value':c.findtext('value'),'MPN':fields.get('MPN','PCB feature' if ref.startswith('TP') else ''),'Manufacturer':fields.get('Manufacturer','PCB fabrication' if ref.startswith('TP') else ''),'Footprint':c.findtext('footprint') or 'RELEASE HOLD','Default Assembly':'DNP' if dnp else 'Fit','Profile Rule':fields.get('Assembly Profile',''), 'Datasheet':fields.get('Datasheet',''),'Release':'Engineering inventory; modem/footprint/electrical qualification pending'})
with (a.output/'bom.csv').open('w',newline='') as f:
 w=csv.DictWriter(f,rows[0].keys(),lineterminator='\n');w.writeheader();w.writerows(rows)
print('Exported review inventory:',len(rows),'rows. This is not a procurement or fabrication release.')
