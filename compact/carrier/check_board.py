"""Independent exported netlist/PCB parity and forbidden-routing audit."""
from pathlib import Path
import json,xml.etree.ElementTree as ET
import sexpdata as sx
P=Path(__file__).resolve().parent
b=sx.loads((P/'carrier.kicad_pcb').read_text())
def nodes(a,k):return [v for v in a if isinstance(v,list) and str(v[0])==k]
def node(a,k):return next(iter(nodes(a,k)),None)
def walk(a):
 for v in a:
  if isinstance(v,list):yield v;yield from walk(v)
r=ET.parse(P/'build/carrier.xml').getroot()
components={c.attrib['ref']:c for c in r.find('components')}
refs={};mechanical=[];errors=[]
for fp in nodes(b,'footprint'):
 ref=next(p[2] for p in nodes(fp,'property') if p[1]=='Reference')
 if 'board_only' in [str(v) for v in (node(fp,'attr') or [])]:mechanical.append(ref);continue
 if ref in refs:errors.append('Duplicate '+ref)
 refs[ref]=fp
 if ref not in components:errors.append('Extra component '+ref);continue
 c=components[ref]
 if fp[1]!=c.findtext('footprint'):errors.append('Footprint differs '+ref)
expected={}
for net in r.find('nets'):
 for p in net.findall('node'):expected[p.attrib['ref'],p.attrib['pin']]=net.attrib['name']
actual={}
for ref,fp in refs.items():
 for pad in nodes(fp,'pad'):
  key=ref,str(pad[1]);n=node(pad,'net')
  if n:
   if expected.get(key)!=n[1]:errors.append('Net differs '+str(key))
   actual[key]=n[1]
if set(components)!=set(refs):errors.append('Component set differs')
if expected!=actual:errors.append('Numeric pin/net map differs')
forbidden={k:sum(str(n[0])==k for n in walk(b)) for k in ['segment','arc','via','filled_polygon','fill_segments']}
if any(forbidden.values()):errors.append('Forbidden routing/fill objects')
for z in [n for n in walk(b) if str(n[0])=='zone']:
 if not node(z,'keepout'):errors.append('Non-rule-area copper zone')
# An independently closed rounded perimeter: every endpoint occurs exactly twice.
edges=[n for n in b if isinstance(n,list) and str(n[0]) in ('gr_line','gr_arc') and node(n,'layer')[1]=='Edge.Cuts']
from collections import Counter
endpoints=Counter(tuple(node(e,k)[1:]) for e in edges for k in ['start','end'])
assert len(edges)==16 and all(count==2 for count in endpoints.values())
assert sum(str(e[0])=='gr_arc' for e in edges)==8
drc=json.loads((P/'build/placement-drc.json').read_text())
report={'schematic_components':len(components),'placed_schematic_components':len(refs),'board_only_mechanical_objects':mechanical,'numeric_pin_net_entries':len(actual),'forbidden_objects':forbidden,'rule_areas':sum(str(n[0])=='zone' for n in walk(b)),'schematic_parity_findings':len(drc['schematic_parity']),'placement_DRC_findings':len(drc['violations']),'expected_unconnected_findings':len(drc['unconnected_items']),'errors':errors,'bench_tests':'NONE','fabrication_ready':False}
(P/'build/board-checks.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
assert not errors
assert not drc['schematic_parity'] and not drc['violations']
