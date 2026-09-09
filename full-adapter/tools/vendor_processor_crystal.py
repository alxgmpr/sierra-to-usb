"""Vendor native crystal lands matching the exact Yajingxin drawing."""
from pathlib import Path
import hashlib
import json
import sexpdata as sx

ROOT=Path(__file__).resolve().parents[1]
SHARE=Path('/Applications/KiCad/KiCad.app/Contents/SharedSupport')
NAME='Yajingxin_TXM_3225_24MHz'
def nodes(n,tag):return [x for x in n if isinstance(x,list) and str(x[0])==tag]


def main():
    native=SHARE/'footprints/Crystal.pretty/Crystal_SMD_3225-4Pin_3.2x2.5mm.kicad_mod'
    fp=sx.loads(native.read_text());fp[1]=NAME
    next(p for p in nodes(fp,'property') if p[1]=='Value')[2]=NAME
    model=SHARE/'3dmodels/Crystal.3dshapes/Crystal_SMD_3225-4Pin_3.2x2.5mm.step'
    (ROOT/'lib/full-adapter.3dshapes'/(NAME+'.step')).write_bytes(model.read_bytes())
    m=nodes(fp,'model')[0]
    m[1]='${KIPRJMOD}/../lib/full-adapter.3dshapes/'+NAME+'.step'
    # Native generic model is 0.64mm high; exact part is 0.7 +/-0.1mm.
    # Use maximum 0.8mm envelope without claiming exact internal construction.
    nodes(nodes(m,'scale')[0],'xyz')[0][3]=1.25
    nodes(fp,'descr')[0][1]='Yajingxin TXM24M0004322FBCDO00T; exact manufacturer 1.4x1.2mm lands, 0.8/0.5mm gaps; pins 2/4 grounded; generic model scaled to maximum 0.8mm height; https://wmsc.lcsc.com/wmsc/upload/file/pdf/v2/lcsc/1912111437_Yajingxin-TXM24M0004322FBCDO00T_C362340.pdf'
    fp.append([sx.Symbol('tags'),'crystal 24MHz 3225 grounded case'])
    expected={'1':[-1.1,.85],'2':[1.1,.85],'3':[1.1,-.85],'4':[-1.1,-.85]}
    pads=nodes(fp,'pad')
    assert len(pads)==4
    for p in pads:
        assert nodes(p,'at')[0][1:3]==expected[p[1]]
        assert nodes(p,'size')[0][1:3]==[1.4,1.2]
    (ROOT/'lib/full-adapter.pretty'/(NAME+'.kicad_mod')).write_text(sx.dumps(fp)+'\n')
    (ROOT/'research/processor-crystal-footprint-source.json').write_text(json.dumps({
        'native_footprint':str(native),'native_sha256':hashlib.sha256(native.read_bytes()).hexdigest(),
        'datasheet_sha256':hashlib.sha256((ROOT/'reference/yjx-txm24m0004322fbcd.pdf').read_bytes()).hexdigest(),
        'datasheet_page':1,'pad_centers_mm':expected,'pad_size_mm':[1.4,1.2],
        'body_mm':[3.2,2.5,.7],'body_tolerance_mm':[.1,.1,.1],
        'signal_pins':['1','3'],'ground_pins':['2','4'],
        'model':'Vendored native generic 3225, nominal XY, Z scaled 1.25 to maximum 0.8mm height. Allow XY tolerances during clearance review.'},indent=2)+'\n')


if __name__=='__main__':main()
