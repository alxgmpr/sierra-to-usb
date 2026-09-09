"""Vendor matching native 3215 lands and enforce Epson's center keepout."""
from pathlib import Path
import copy
import hashlib
import json
import sexpdata as sx

ROOT=Path(__file__).resolve().parents[1]
SHARE=Path('/Applications/KiCad/KiCad.app/Contents/SharedSupport')
NAME='Epson_FC-135R_3.2x1.5mm'
def nodes(n,tag):return [x for x in n if isinstance(x,list) and str(x[0])==tag]


def main():
    native=SHARE/'footprints/Crystal.pretty/Crystal_SMD_3215-2Pin_3.2x1.5mm.kicad_mod'
    fp=sx.loads(native.read_text());fp[1]=NAME
    next(p for p in nodes(fp,'property') if p[1]=='Value')[2]=NAME
    model_src=SHARE/'3dmodels/Crystal.3dshapes/Crystal_SMD_3215-2Pin_3.2x1.5mm.step'
    (ROOT/'lib/full-adapter.3dshapes'/(NAME+'.step')).write_bytes(model_src.read_bytes())
    nodes(fp,'model')[0][1]='${KIPRJMOD}/../lib/full-adapter.3dshapes/'+NAME+'.step'
    nodes(fp,'descr')[0][1]='Epson FC-135R; manufacturer lands and center keepout; https://download.epsondevice.com/td/pdf/app/FC-135R_en.pdf'
    template=sx.loads((SHARE/'footprints/RF_Module.pretty/ESP32-WROOM-32E.kicad_mod').read_text())
    zone=copy.deepcopy(nodes(template,'zone')[0])
    zone[:]=[x for x in zone if not isinstance(x,list) or str(x[0])!='uuid']
    polygon=nodes(zone,'polygon')[0]
    polygon[1]=[sx.Symbol('pts')]+[[sx.Symbol('xy'),x,y] for x,y in [(-.75,-.9),(.75,-.9),(.75,.9),(-.75,.9)]]
    fp.append(zone)
    pads=nodes(fp,'pad')
    assert len(pads)==2 and all(nodes(p,'size')[0][1:]==[1,1.8] for p in pads)
    assert {tuple(nodes(p,'at')[0][1:3]) for p in pads}=={(-1.25,0),(1.25,0)}
    (ROOT/'lib/full-adapter.pretty'/(NAME+'.kicad_mod')).write_text(sx.dumps(fp)+'\n')
    (ROOT/'research/rtc-footprint-source.json').write_text(json.dumps({
        'native_footprint':str(native),'native_sha256':hashlib.sha256(native.read_bytes()).hexdigest(),
        'datasheet_sha256':hashlib.sha256((ROOT/'reference/fc-135r-en.pdf').read_bytes()).hexdigest(),
        'datasheet_page':4,'pad_size_mm':[1,1.8],'pad_centers_x_mm':[-1.25,1.25],
        'center_keepout_mm':[1.5,1.8],'keepout_layers':'all copper layers',
        'pin_polarity':'passive nonpolar crystal; native left/right numbering retained'},indent=2)+'\n')


if __name__=='__main__':main()
