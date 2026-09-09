"""Vendor native KiCad 0603 body/model, with Murata's reflow land dimensions."""
from pathlib import Path
import hashlib
import json
import sexpdata as sx

ROOT = Path(__file__).resolve().parents[1]
SHARE = Path('/Applications/KiCad/KiCad.app/Contents/SharedSupport')
NAME = 'Murata_BLM18PG121SN1D_0603'


def nodes(n,tag): return [x for x in n if isinstance(x,list) and str(x[0]) == tag]


def main():
    native = SHARE/'footprints/Inductor_SMD.pretty/L_0603_1608Metric.kicad_mod'
    fp = sx.loads(native.read_text()); fp[1] = NAME
    next(p for p in nodes(fp,'property') if p[1] == 'Value')[2] = NAME
    nodes(fp,'descr')[0][1] = 'Murata BLM18PG121SN1D; reflow a=0.7, b=2.0, c=d=0.7 mm; JENF243A-0003AJ-01 p9; 35um copper; https://www.mouser.cn/datasheet/2/281/ENFA0003-1915778.pdf'
    for text in nodes(fp,'fp_text'):
        font = nodes(nodes(text,'effects')[0],'font')[0]
        nodes(font,'size')[0][1:] = [.5,.5]
        nodes(font,'thickness')[0][1] = .075
    for pad in nodes(fp,'pad'):
        pad[3] = sx.Symbol('rect')
        nodes(pad,'at')[0][1:3] = [-.675 if pad[1] == '1' else .675, 0]
        nodes(pad,'size')[0][1:3] = [.65,.7]
        pad[:] = [x for x in pad if not isinstance(x,list) or str(x[0]) != 'roundrect_rratio']
    model_src = SHARE/'3dmodels/Inductor_SMD.3dshapes/L_0603_1608Metric.step'
    (ROOT/'lib/full-adapter.3dshapes'/(NAME+'.step')).write_bytes(model_src.read_bytes())
    nodes(fp,'model')[0][1] = '${KIPRJMOD}/../lib/full-adapter.3dshapes/'+NAME+'.step'
    (ROOT/'lib/full-adapter.pretty'/(NAME+'.kicad_mod')).write_text(sx.dumps(fp)+'\n')
    (ROOT/'research/usb-ferrite-footprint-source.json').write_text(json.dumps({
        'native_footprint':str(native),'native_sha256':hashlib.sha256(native.read_bytes()).hexdigest(),
        'manufacturer_document':'Murata JENF243A-0003AJ-01 pp1,4,9',
        'source_url':'https://www.mouser.cn/datasheet/2/281/ENFA0003-1915778.pdf',
        'datasheet_sha256':hashlib.sha256((ROOT/'reference/murata-blm18-mirror.pdf').read_bytes()).hexdigest(),
        'pad_size_mm':[.65,.7],'pad_centers_x_mm':[-.675,.675],
        'land_gap_mm':.7,'land_outer_span_mm':2,'outer_copper_um':35,
        'body_nominal_mm':[1.6,.8,.8],'body_dimension_tolerance_mm':.15,
        'native_model_note':'Nominal envelope; mechanical clearance must also allow body tolerance.'},indent=2)+'\n')


if __name__ == '__main__': main()
