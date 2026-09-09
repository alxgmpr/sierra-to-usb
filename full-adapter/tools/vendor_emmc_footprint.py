"""Vendor native JEDEC 153-ball lands after exact SanDisk array comparison."""
from pathlib import Path
import hashlib
import json
import sexpdata as sx

ROOT=Path(__file__).resolve().parents[1]
SHARE=Path('/Applications/KiCad/KiCad.app/Contents/SharedSupport')
NAME='SanDisk_SDINBDG4_BGA153_11.5x13mm_P0.5mm'
def nodes(n,tag):return [x for x in n if isinstance(x,list) and str(x[0])==tag]


def main():
    source=json.loads((ROOT/'research/emmc-pins.json').read_text())
    native=SHARE/'footprints/Package_BGA.pretty/LFBGA-153_11.5x13mm_Layout14x14_P0.5mm.kicad_mod'
    fp=sx.loads(native.read_text());fp[1]=NAME
    next(p for p in nodes(fp,'property') if p[1]=='Value')[2]=NAME
    nodes(fp,'descr')[0][1]='SanDisk SDINBDG4-8G, exact 153-ball array, 11.5x13mm, 0.5mm pitch; '+source['source']['url']
    expected={p['ball']:p['xy_mm'] for p in source['pins']}
    pads=nodes(fp,'pad')
    assert len(pads)==153 and {p[1] for p in pads}==set(expected)
    for p in pads:
        assert nodes(p,'at')[0][1:3]==expected[p[1]]
        assert nodes(p,'size')[0][1:3]==[.24,.24]
    model=ROOT/'build/emmc-model/Package_BGA.3dshapes/LFBGA-153_11.5x13mm_Layout14x14_P0.5mm.step'
    (ROOT/'lib/full-adapter.3dshapes'/(NAME+'.step')).write_bytes(model.read_bytes())
    nodes(fp,'model')[0][1]='${KIPRJMOD}/../lib/full-adapter.3dshapes/'+NAME+'.step'
    (ROOT/'lib/full-adapter.pretty'/(NAME+'.kicad_mod')).write_text(sx.dumps(fp)+'\n')
    (ROOT/'research/emmc-footprint-source.json').write_text(json.dumps({
        'native_footprint':str(native),'native_sha256':hashlib.sha256(native.read_bytes()).hexdigest(),
        'datasheet_url':source['source']['url'],'datasheet_pages':[20,21,22,23],
        'pads':153,'pad_diameter_mm':.24,'pitch_mm':.5,'array_span_mm':[6.5,6.5],
        'model_source':'KiCad Library Tools package/grid_array; lib/emmc-grid-array.yaml, overall height 0.8mm','model_sha256':hashlib.sha256(model.read_bytes()).hexdigest(),
        'body_tolerance_mm':[.1,.1],'height_max_mm':.8,
        'status':'Native lands compared to manufacturer top-view package and ball assignment; full PCB escape and assembly qualification remain.'},indent=2)+'\n')


if __name__=='__main__':main()
