"""Finalize report only after the recorded manual visual review still matches exports."""
from pathlib import Path
import hashlib,json
P=Path(__file__).resolve().parent;B=P/'build'
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(name):return json.loads((B/name).read_text())
v=read('visual-review.json')
for name,h in v['reviewed_artifact_sha256'].items():assert digest(P/name)==h,'Repeat visual review: '+name
s=read('schematic-checks.json');b=read('board-checks.json');m=read('model-checks.json');power=read('replacement-power-budget.json')
assert s['ERC_findings']==0 and s['capture_assertions']==88
assert b['placed_schematic_components']==b['schematic_components']==161
assert not b['errors'] and not b['schematic_parity_findings'] and not b['placement_DRC_findings']
assert not any(b['forbidden_objects'].values())
assert 'Ran 19 tests' in (B/'unit-tests.log').read_text() and (B/'unit-tests.log').read_text().rstrip().endswith('OK')
guarded=0
for manifest in (P/'reference').glob('*generated-sha256.json'):
 for file,h in json.loads(manifest.read_text()).items():assert digest(P/file)==h,file;guarded+=1
artifacts=['carrier.kicad_pro','carrier.kicad_sch','carrier.kicad_pcb','carrier.kicad_dru','build/carrier-development.pdf','build/development-bom.csv','assembly-materials.csv','build/carrier.xml','build/component-positions.csv','build/placement-drawing.pdf','build/mechanical-drawing.pdf','build/assembly-envelopes.step','build/assembly-3d-isometric.png','build/assembly-3d-top.png','ROUTING.md','REVIEW.md','HANDOFF.md','source-to-pin-review.md','build/erc.json','build/placement-drc.json','build/board-checks.json','build/model-checks.json','build/replacement-power-budget.json','build/visual-review.json']
r={'date':'2026-09-07','endpoint_complete':True,'endpoint_scope':'Complete reviewed schematic and deliberate entirely unrouted placement, with explicit unresolved design/bench gates','complete_carrier_schematic':True,'compact_PCB_created':True,'stage':'PLACEMENT1 — NOT FABRICATION RELEASE','schematic':s,'board':b,'unit_tests_passed':19,'guarded_outputs_verified':guarded,'custom_STEP_envelopes_bounds_checked':len(m['models']),'visual_review':v['scope'],'production_gerbers':False,'bench_tests':'NONE','fabrication_ready':False,'electrical_qualification':'UNPERFORMED; conditional analytical envelope only','power_4V_conditional_surplus_W':power['recharge']['lowest_line_conditional_surplus_W'],'open_gates_document':'REVIEW.md','root_project':'Root files and pre-existing modifications preserved; only compact/ and task-status documentation changed by this continuation','artifact_sha256':{name:digest(P/name) for name in artifacts}}
(B/'check-summary.json').write_text(json.dumps(r,indent=2)+'\n')
(P.parent/'review/check-summary.json').write_text(json.dumps({'date':r['date'],'endpoint_complete':True,'authoritative_report':'../carrier/build/check-summary.json','current_design':'../carrier/carrier.kicad_pro','complete_carrier_schematic':True,'compact_PCB_created':True,'placed_components':161,'ERC_findings':0,'PCB_parity_findings':0,'placement_DRC_findings':0,'expected_unconnected_findings':454,'new_tracks':0,'new_routing_vias':0,'new_filled_zones':0,'production_gerbers':False,'bench_tests':'NONE','fabrication_ready':False,'power_candidate':'Historical LTC3128/TPS62816 candidate remains rejected; current direct-buck architecture has conditional69.8mW low-line surplus.','open_gates':'../carrier/REVIEW.md'},indent=2)+'\n')
print('Placement-stage handoff finalized; fabrication and bench qualification remain open.')
