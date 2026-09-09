"""Export schematic review artifacts; board/overall checks are separate."""
from pathlib import Path
import subprocess,json,collections,os
P=Path(__file__).resolve().parent
K='/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli'
b=P/'build';b.mkdir(exist_ok=True)
for args in [
 ['sch','erc','--format','json','-o',str(b/'erc.json')],
 ['sch','export','netlist','--format','kicadxml','-o',str(b/'carrier.xml')],
 ['sch','export','bom','--fields','Reference,Value,Footprint,MPN,Manufacturer,Status','-o',str(b/'development-bom.csv')],
 ['sch','export','svg','-o',str(b/'svg')],
 ['sch','export','pdf','-o',str(b/'carrier-development.pdf')],
]:subprocess.run([K,*args,str(P/'carrier.kicad_sch')],check=True)
subprocess.run([str(P.parent/'.venv/bin/python'),str(P/'check_capture.py')],check=True)
d=json.loads((b/'erc.json').read_text());v=[v for s in d['sheets'] for v in s.get('violations',[])]
report={'ERC_findings':len(v),'ERC_types':dict(collections.Counter(x['type'] for x in v)),'ERC_severity':dict(collections.Counter(x['severity'] for x in v)),'capture_assertions':len(json.loads((b/'capture-checks.json').read_text())['checks']),'exports':'Review only; no production outputs','bench_tests':'None'}
(b/'schematic-checks.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
