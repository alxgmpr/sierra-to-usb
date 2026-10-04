#!/usr/bin/env python3
"""Attach current draft sheets under appliance root; keep their standalone contexts."""
from pathlib import Path
import re, uuid
ROOT=Path(__file__).resolve().parents[1]
def uid(key):return str(uuid.uuid5(uuid.NAMESPACE_URL,'sierra-appliance-'+key))
root=uid('root'); rec=uid('recovery'); pmic=uid('pmic')
for filename,project,oldroot,newpath in [
 ('recovery.kicad_sch','recovery','37b14702-5d54-5543-b96e-899c36eac351',f'/{root}/{rec}'),
 ('supervisor.kicad_sch','recovery','37b14702-5d54-5543-b96e-899c36eac351',f'/{root}/{rec}'),
 ('controls.kicad_sch','recovery','37b14702-5d54-5543-b96e-899c36eac351',f'/{root}/{rec}'),
 ('always-on.kicad_sch','recovery','37b14702-5d54-5543-b96e-899c36eac351',f'/{root}/{rec}'),
 ('pmic.kicad_sch','pmic','152b7cfd-b2ed-5d28-883d-f6de3f0c70ef',f'/{root}/{pmic}')]:
 p=ROOT/filename;s=p.read_text()
 # Remove previously generated project contexts before refreshing them.
 s=re.sub(r' \(project "appliance" \(path "[^"]+" \((?:reference|page) "[^"]+"\)(?: \(unit \d+\))?\)\)', '',s)
 pattern=r'(\(project "'+project+r'" \(path "/'+oldroot+r'([^"]*)" (\((?:reference|page) "[^"]+"\)(?: \(unit \d+\))?)\)\))'
 s=re.sub(pattern,lambda m:m[1]+f' (project "appliance" (path "{newpath}{m[2]}" {m[3]}))',s)
 p.write_text(s)
font='(effects (font (size 1.27 1.27)))'
sheets=[]
for name,file,sid,x,page in [('Recovery and always-on supply','recovery.kicad_sch',rec,35.56,2),('Processor PMIC draft','pmic.kicad_sch',pmic,157.48,6)]:
 sheets.append(f'(sheet (at {x} 63.5) (size 96.52 50.8) (stroke (width 0.254) (type default)) (fill (color 0 0 0 0)) (uuid "{sid}") (property "Sheetname" "{name}" (at {x} 60.96 0) {font}) (property "Sheetfile" "{file}" (at {x} 116.84 0) {font}) (instances (project "appliance" (path "/{root}" (page "{page}")))))')
(ROOT/'appliance.kicad_sch').write_text(f'(kicad_sch (version 20250114) (generator eeschema) (uuid "{root}") (paper "A4") (title_block (title "Cellular WAN appliance — INCOMPLETE") (date "2026-10-03")) (lib_symbols) '+''.join(sheets)+f' (text "DRAFT: processor, DDR, storage, Ethernet, PoE and modem sheets still required.\\nPMIC circuitry incomplete; MCU-to-PMIC restart net is not yet joined." (at 35.56 144.78 0) (effects (font (size 1.27 1.27)) (justify left)) (uuid "{uid("note")}")) (sheet_instances (path "/" (page "1"))))\n')
print('Generated appliance root and refreshed annotation contexts.')
