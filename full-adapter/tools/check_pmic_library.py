"""Check RK809-5 pin coverage and physical QFN68/EP69 geometry."""
from pathlib import Path
import json
import sexpdata as sx

ROOT=Path(__file__).resolve().parents[1]
def children(node,tag):return [n for n in node if isinstance(n,list) and str(n[0])==tag]
def one(node,tag):return children(node,tag)[0]


def check(root=ROOT):
    source=json.loads((root/'research/pmic-pins.json').read_text())
    lib=sx.loads((root/'lib/full-adapter.kicad_sym').read_text())
    symbol=next(s for s in children(lib,'symbol') if s[1]=='RK809-5')
    pins=[p for u in children(symbol,'symbol') for p in children(u,'pin')]
    expected={p['ball']:p for p in source['pins']}
    assert len(pins)==len(expected)==69
    assert {one(p,'number')[1] for p in pins}==set(expected)
    for pin in pins:
        p=expected[one(pin,'number')[1]]
        assert one(pin,'name')[1]==p.get('display_name',p['name'])
        assert str(pin[1])==p['type']
        assert not children(pin,'hide')
        for v in one(pin,'at')[1:3]:assert abs(v/2.54-round(v/2.54))<1e-6
    assert {k:expected[k]['name'] for k in ['1','17','18','34','35','51','52','68','69']}=={
        '1':'SCL','17':'SDI','18':'SDO/PDMDATA','34':'SPKN_OUT','35':'VCC_CPVSS',
        '51':'XOUT','52':'PWRON','68':'CLK32K','69':'GND'}
    fp=sx.loads((root/'lib/full-adapter.pretty'/(source['footprint'].split(':')[1]+'.kicad_mod')).read_text())
    pads=[p for p in children(fp,'pad') if p[1]]
    assert {p[1] for p in pads}==set(expected)
    for n in range(1,69):
        p=next(p for p in pads if p[1]==str(n))
        side,index=divmod(n-1,17)
        along=round(-2.8+index*.35,6)
        xy=[[-3.3,along],[along,3.3],[3.3,-along],[-along,-3.3]][side]
        assert one(p,'at')[1:3]==xy,(n,one(p,'at'),xy)
        assert one(p,'size')[1:]==([.55,.25] if side%2==0 else [.25,.55])
    ep=[p for p in pads if p[1]=='69']
    land=[p for p in ep if str(p[2])=='smd'];vias=[p for p in ep if str(p[2])=='thru_hole']
    assert len(land)==2
    assert {tuple(one(p,'layers')[1:]) for p in land}=={('F.Cu','F.Mask'),('B.Cu',)}
    assert all(one(p,'size')[1:]==[5.49,5.49] for p in land)
    assert len(vias)==16
    for p in vias:
        assert one(p,'drill')[1]==.2 and one(p,'size')[1:]==[.5,.5]
        assert max(abs(v) for v in one(p,'at')[1:3])<=2.495
    paste=[p for p in children(fp,'pad') if not p[1]]
    assert len(paste)==9
    assert all(one(p,'layers')[1:]==['F.Paste'] for p in paste)
    rectangular_area=sum(one(p,'size')[1]*one(p,'size')[2] for p in paste)
    assert .55 < rectangular_area/(5.49**2) < .65
    model=one(fp,'model')[1]
    assert model.startswith('${KIPRJMOD}/../lib/full-adapter.3dshapes/')
    assert (root/'lib/full-adapter.3dshapes'/Path(model).name).is_file()
    assert set(source['unused_audio_ground'])=={14,15,16,17,19,40}
    assert set(source['unused_audio_open'])=={18,36,37,38,35,39,41,34,32,43,42}
    return {'status':'PMIC_LIBRARY_CHECKPOINT_NOT_RELEASE','numbered_pins':68,'exposed_pad_number':'69',
            'units':11,'thermal_vias':16,'scope':'library_only'}


if __name__=='__main__':
    result=check()
    (ROOT/'research/pmic-library-validation.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
