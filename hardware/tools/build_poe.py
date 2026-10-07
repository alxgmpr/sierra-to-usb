#!/usr/bin/env python3
"""Adapt TI's imported Class-6 native reference while preserving power-stage nets."""
from pathlib import Path
import hashlib,json,re,uuid
from capture import ROOT,Sheet,block,prop

def children(text):
 pos=re.match(r'\([^\s()]+',text).end()
 while pos<len(text)-1:
  if text[pos]=='(':
   item=block(text,pos);yield item;pos+=len(item)
  else:pos+=1

def field(item,name):
 m=re.search(r'\(property "'+re.escape(name)+r'" "((?:[^"\\]|\\.)*)"',item)
 return m[1] if m else ''

def setfield(item,name,value):
 m=re.search(r'\(property "'+re.escape(name)+r'"',item)
 if m:
  old=block(item,m.start());new=re.sub(r'^(\(property "[^"]+" )"(?:[^"\\]|\\.)*"',lambda m:m[1]+'"'+value+'"',old);return item.replace(old,new,1)
 return item[:-1]+prop(name,value,0,0,True)+')'

fmap=json.loads((ROOT/'reference/tida-import/footprints.json').read_text())
libs={};meta={'poe-pd':Sheet('poe-pd','').root};counter=0
renets={'VDD':'POE_VDD','VSS1':'POE_VSS','VSS':'POE_VSS','RTN':'POE_RTN','UVLO':'POE_UVLO','VCOUT':'POE_VCOUT','VCIN':'POE_VCIN','TPH':'POE_TPH','TPL':'POE_TPL','BT':'POE_BT','APD':'POE_APD','MPS_DUTY':'POE_MPS_DUTY','PR12':'POE_PAIR12','PR36':'POE_PAIR36','PR45':'POE_PAIR45','PR78':'POE_PAIR78','VOUT':'ISO_12V','EARTH':'CHASSIS'}
for source,name in [('input','poe-input'),('flyback','poe-flyback')]:
 raw=(ROOT/f'reference/tida-import/{source}.kicad_sch').read_text()
 rootid=re.search(r'\(uuid "([^"]+)"',raw)[1]
 meta[name]=rootid
 source_lib=next(c for c in children(raw) if c.startswith('(lib_symbols'))
 mapping={};bodys={}
 for body in children(source_lib):
  old=re.search(r'^\(symbol "([^"]+)"',body)[1];new='TI_'+hashlib.sha256(body.encode()).hexdigest()[:12];mapping[old]=new
  canonical=body.replace(f'(symbol "{old}"',f'(symbol "{new}"',1).replace('"'+old.split(':')[-1]+'_','"'+new+'_')
  for a,b in renets.items():canonical=canonical.replace('"'+a+'"','"'+b+'"')
  libs[new]=canonical;bodys[old]=body
 output=[];library=[]
 for item in children(raw):
  if item.startswith('(lib_symbols'):
   continue
  if item.startswith('(text') and '${' in item:continue
  if item.startswith('(title_block'):
   item=f'(title_block (title "Isolated PoE — {source}, TI TIDA-050023 derivative") (date "2026-10-07"))'
  if item.startswith('(symbol') and '(lib_id ' in item:
   original=field(item,'Reference');identifier=re.search(r'\(lib_id "([^"]+)"',item)[1]
   override=re.search(r'\(lib_name "([^"]+)"',item);old=override[1] if override else identifier
   item=re.sub(r'\(lib_name "[^"]+"\)','',item)
   # The 1Gb passthrough transformer is replaced by the separate HX4110NL 2.5G ingress.
   if source=='input' and (original in ['T1','J1','J2','TP1','TP2','TP3','TP4','TP5'] or re.fullmatch(r'[RC][1-6]',original) or original in ['R7','R8']):continue
   if source=='input' and original.startswith('#'):
    y=float(re.search(r'\(at ([^()]+)\)',item)[1].split()[1])
    if y<125:continue
   if original.startswith('#'):
    # Altium's ARROW symbol is a net marker, including digital controls.
    # Replace it with a global label; it has no physical supply pin.
    x,y,angle=map(float,re.search(r'\(at ([^()]+)\)',item)[1].split())
    marker=Sheet(name,'');marker.net(renets.get(field(item,'Value'),field(item,'Value')),(x,y),0)
    output+=marker.items
    continue
   else:
    m=re.fullmatch(r'([A-Za-z]+)(\d+)',original);assert m,original;reference=m[1]+str(1700+int(m[2]))
    item=setfield(item,'MPN',field(item,'PARTNUMBER'))
    item=setfield(item,'Manufacturer',field(item,'MANUFACTURER'))
    item=setfield(item,'Datasheet',field(item,'COMPONENTLINK1URL'))
    item=setfield(item,'Value',field(item,'ALTIUM_VALUE') or field(item,'VALUEDISPLAYED') or field(item,'PARTNUMBER'))
    if original in fmap:item=setfield(item,'Footprint',fmap[original]['footprint'])
    if original in ['D6','D7','D8','D9','R62']:item=item.replace('(dnp no)','(dnp yes)')
   item=item.replace('"'+original+'"','"'+reference+'"')
   item=item.replace(f'(lib_id "{identifier}"',f'(lib_id "PoE:{mapping[old]}"')
   canonical=libs[mapping[old]].replace(f'(symbol "{mapping[old]}"',f'(symbol "PoE:{mapping[old]}"',1)
   if canonical not in library:library.append(canonical)
   item=re.sub(r'\(project "[^"]+"',f'(project "{name}"',item)
  if source=='input' and item.startswith(('(wire','(junction','(text','(polyline')):
   ys=[float(y) for y in re.findall(r'\(xy [-\d.]+ ([-\d.]+)\)',item)]
   if not ys:
    m=re.search(r'\(at [-\d.]+ ([-\d.]+)',item);ys=[float(m[1])] if m else []
   if ys and min(ys)<125:continue
  for a,b in renets.items():item=item.replace('"'+a+'"','"'+b+'"')
  output.append(item)
 # Add labels at the actual native pin/wire endpoints, then snap a proven 50-mil import grid.
 s=Sheet(name,'')
 if source=='flyback':
  s.net('ISO_12V',(359.41,66.294)) # C27 positive: output AFTER L8.
  s.net('POE_PWM_BIAS',(71.628,107.696)) # LM51551 BIAS, after R45.
  s.flag('#FLG1701','ISO_12V',381,25.4,'Isolated T1702 flyback secondary through D1718 and L1708')
  s.flag('#FLG1706','POE_VCIN',25.4,254,'T1702 auxiliary winding rectified by D1717')
  s.flag('#FLG1705','POE_PWM_BIAS',40.64,218.44,'TPS2373 VC_OUT through R1745 (zero-ohm bias link)')
  s.nc((273.05,71.374));s.nc((273.05,73.914)) # T2 NC pads 7 and 10.
 if source=='input':s.note('Cable pair feeds from HX4110NL 2.5G / four-pair 60W ingress.\nReference active bridge retained. Permanent VSS1-to-VSS current-link is now a PCB trace.\nPOE_VSS and POE_RTN remain isolated from system GND.',20.32,25.4)
 output+=s.items
 # Every native pin coordinate is on 1.27mm local grid. Snapping instance origins and
 # connected endpoints therefore retains pin/wire coincidence; golden netlist check verifies it.
 def snapmatch(m):
  return m[1]+str(round(round(float(m[2])/1.27)*1.27,4))+' '+str(round(round(float(m[3])/1.27)*1.27,4))
 output=[re.sub(r'(\((?:at|xy) )([-\d.]+) ([-\d.]+)',snapmatch,i) for i in output]
 # Any standard flag library used by helper must also be embedded.
 library+=list(s.library.values())
 text='(kicad_sch '+ ' '.join(output)+' (lib_symbols '+' '.join(library)+'))\n'
 assert block(text,0)==text.strip()
 text='\n'.join(line.rstrip() for line in text.splitlines())+'\n'
 (ROOT/f'{name}.kicad_sch').write_text(text)
(ROOT/'PoE.kicad_sym').write_text('(kicad_symbol_lib (version 20260830) (generator eeschema) '+''.join(libs.values())+')\n')
(ROOT/'reference/tida-import/roots.json').write_text(json.dumps(meta,indent=2)+'\n')
p=ROOT/'sym-lib-table';t=p.read_text()
if '(name "PoE")' not in t:p.write_text(t.rstrip()[:-1]+' (lib (name "PoE") (type "KiCad") (uri "${KIPRJMOD}/PoE.kicad_sym") (options "") (descr "TI TIDA-050023 native reference symbols")))\n')
print('Adapted native TI reference:',len(libs),'symbols, distinct cable-side grounds.')
