#!/usr/bin/env python3
"""Compare native RAM inventory with PDF diagram cells; run with pdfplumber."""
from pathlib import Path
import pdfplumber,csv,re,collections
root=Path(__file__).resolve().parents[1]/'reference'; rows='A B C D E F G H J K L M N P R T U V W Y AA AB'.split(); cols=[1,2,3,4,5,8,9,10,11,12]
with pdfplumber.open(root/'micron-z42m-rev-i.pdf') as p:
 page=p.pages[21]; balls={}
 for i,row in enumerate(rows):
  if row in ['L','M']:continue
  cy=164+19.9612876*i
  for col in cols:
   cx=123.8+33.92*(col-1)
   words=page.crop((cx-16.5,cy-9,cx+16.5,cy+10)).extract_words()
   name=''.join(w['text'] for w in sorted(words,key=lambda w:(round(w['top']/3),w['x0'])))
   balls[row+str(col)]=name
native=list(csv.DictReader((root/'micron-ddr-native-pin-inventory.csv').open()));assert len(balls)==200
out=[]
for r in native:
 name=balls[r['ball']];status='exact' if r['native_name']==name else 'single_rank_nc_alias' if name=='NC' and r['native_name'].startswith('NC/') else 'difference'
 out.append({**r,'manufacturer_name':name,'status':status})
with (root/'micron-ddr-native-ball-audit.csv').open('w') as f:
 w=csv.DictWriter(f,fieldnames=list(out[0]),lineterminator='\n');w.writeheader();w.writerows(out)
print(collections.Counter(r['status'] for r in out))
for r in out:
 if r['status']=='difference':print(r)
