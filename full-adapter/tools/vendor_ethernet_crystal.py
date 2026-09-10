"""Vendor native 3225 lands matching the exact YXC X322525MOB4SI drawing."""
from pathlib import Path
import hashlib, json
import sexpdata as sx

ROOT=Path(__file__).resolve().parents[1]
SHARE=Path('/Applications/KiCad/KiCad.app/Contents/SharedSupport')
NAME='YXC_X322525MOB4SI'
def nodes(n,t):return [v for v in n if isinstance(v,list) and str(v[0])==t]

def main():
    native=SHARE/'footprints/Crystal.pretty/Crystal_SMD_3225-4Pin_3.2x2.5mm.kicad_mod'
    fp=sx.loads(native.read_text());fp[1]=NAME
    next(p for p in nodes(fp,'property') if p[1]=='Value')[2]=NAME
    fp.append([sx.Symbol('tags'),'crystal 25MHz 3225 grounded case'])
    nodes(fp,'descr')[0][1]='YXC X322525MOB4SI 25MHz/12pF; manufacturer 1.4x1.2 lands and 0.8/0.5 gaps; pins2/4 grounded; https://www.micros.com.pl/mediaserver/Q25.000_3.2x2.5_Y_0001.pdf'
    model=SHARE/'3dmodels/Crystal.3dshapes/Crystal_SMD_3225-4Pin_3.2x2.5mm.step'
    out=ROOT/'lib/full-adapter.3dshapes'/(NAME+'.step')
    out.write_text('\n'.join(line.rstrip() for line in model.read_text().splitlines())+'\n')
    m=nodes(fp,'model')[0];m[1]='${KIPRJMOD}/../lib/full-adapter.3dshapes/'+NAME+'.step'
    nodes(nodes(m,'scale')[0],'xyz')[0][3]=1.25
    (ROOT/'lib/full-adapter.pretty'/(NAME+'.kicad_mod')).write_text(sx.dumps(fp)+'\n')
    (ROOT/'research/ethernet-crystal-footprint.json').write_text(json.dumps({
        'native':str(native),'native_sha256':hashlib.sha256(native.read_bytes()).hexdigest(),
        'manufacturer_pdf':'reference/yxc-x322525mob4si.pdf','sha256':hashlib.sha256((ROOT/'reference/yxc-x322525mob4si.pdf').read_bytes()).hexdigest(),
        'page':1,'lands_mm':[1.4,1.2],'centers_mm':{'1':[-1.1,.85],'2':[1.1,.85],'3':[1.1,-.85],'4':[-1.1,-.85]},
        'model':'Native generic 3225, nominal XY, Z scale1.25 gives0.8mm maximum height; package XY tolerance +/-0.1mm requires clearance allowance.'},indent=2)+'\n')

if __name__=='__main__':main()
