#!/usr/bin/env python3
"""Attach current draft sheets under appliance root; keep their standalone contexts."""
from pathlib import Path
import re, uuid
ROOT=Path(__file__).resolve().parents[1]
def uid(key):return str(uuid.uuid5(uuid.NAMESPACE_URL,'sierra-appliance-'+key))
root=uid('root'); rec=uid('recovery'); pmic=uid('pmic'); main=uid('main3v3'); main5=uid('main5v'); processor=uid('processor'); phy=uid('phy')
for filename,project,oldroot,newpath in [
 ('recovery.kicad_sch','recovery','37b14702-5d54-5543-b96e-899c36eac351',f'/{root}/{rec}'),
 ('supervisor.kicad_sch','recovery','37b14702-5d54-5543-b96e-899c36eac351',f'/{root}/{rec}'),
 ('controls.kicad_sch','recovery','37b14702-5d54-5543-b96e-899c36eac351',f'/{root}/{rec}'),
 ('always-on.kicad_sch','recovery','37b14702-5d54-5543-b96e-899c36eac351',f'/{root}/{rec}'),
 ('main3v3.kicad_sch','main3v3','2e6dd71a-ab95-5ea3-b14d-00e36bba2be3',f'/{root}/{main}'),
 ('main5v.kicad_sch','main5v','67626c44-65b2-5096-88fd-dd5ad98a1eca',f'/{root}/{main5}'),
 ('phy-power.kicad_sch','phy-power','ca155a7e-d9ea-59e1-bc36-3f46f6f2a8ef',f'/{root}/{phy}'),
 ('processor.kicad_sch','processor','e562e6d7-6054-5734-8bbe-ccdbe844f626',f'/{root}/{processor}'),
 ('pmic.kicad_sch','pmic','152b7cfd-b2ed-5d28-883d-f6de3f0c70ef',f'/{root}/{pmic}')]:
 p=ROOT/filename;s=p.read_text()
 # Remove previously generated project contexts before refreshing them.
 s=re.sub(r' \(project "appliance" \(path "[^"]+" \((?:reference|page) "[^"]+"\)(?: \(unit \d+\))?\)\)', '',s)
 pattern=r'(\(project "'+project+r'" \(path "/'+oldroot+r'([^"]*)" (\((?:reference|page) "[^"]+"\)(?: \(unit \d+\))?)\)\))'
 s=re.sub(pattern,lambda m:m[1]+f' (project "appliance" (path "{newpath}{m[2]}" {m[3]}))',s)
 p.write_text(s)
font='(effects (font (size 1.27 1.27)))'
sheets=[]
for name,file,sid,x,y,page in [('Recovery and always-on supply','recovery.kicad_sch',rec,35.56,35.56,2),('Processor PMIC draft','pmic.kicad_sch',pmic,157.48,35.56,6),('Main 3.3V draft','main3v3.kicad_sch',main,35.56,106.68,7),('Main 5V control draft','main5v.kicad_sch',main5,157.48,106.68,8),('RK3566 processor draft','processor.kicad_sch',processor,35.56,177.8,9),('USB analog filters draft','phy-power.kicad_sch',phy,157.48,177.8,10)]:
 sheets.append(f'(sheet (at {x} {y}) (size 96.52 50.8) (stroke (width 0.254) (type default)) (fill (color 0 0 0 0)) (uuid "{sid}") (property "Sheetname" "{name}" (at {x} {y-2.54} 0) {font}) (property "Sheetfile" "{file}" (at {x} {y+53.34} 0) {font}) (instances (project "appliance" (path "/{root}" (page "{page}")))))')
(ROOT/'appliance.kicad_sch').write_text(f'(kicad_sch (version 20250114) (generator eeschema) (uuid "{root}") (paper "A3") (title_block (title "Cellular WAN appliance — INCOMPLETE") (date "2026-10-04")) (lib_symbols) '+''.join(sheets)+f' (text "DRAFT: Processor circuitry, DDR and storage incomplete.\\nEthernet, PoE and modem sheets still required.\\nPMIC circuitry incomplete.\\nSupervisor restart output joins the PMIC input." (at 279.4 50.8 0) (effects (font (size 1.27 1.27)) (justify left)) (uuid "{uid("note")}")) (sheet_instances (path "/" (page "1"))))\n')
print('Generated appliance root and refreshed annotation contexts.')
