"""Independent RTL8125BG pin/pad check; not circuit or release validation."""
from pathlib import Path
import json
import sexpdata as sx
ROOT=Path(__file__).resolve().parents[1]
def nodes(n,t):return [v for v in n if isinstance(v,list) and str(v[0])==t]
def check(root=ROOT):
    lib=sx.loads((root/'lib/full-adapter.kicad_sym').read_text());sym=next(v for v in nodes(lib,'symbol') if v[1]=='RTL8125BG-CG')
    pins={nodes(p,'number')[0][1]:(nodes(p,'name')[0][1],str(p[1])) for u in nodes(sym,'symbol') for p in nodes(u,'pin')}
    source=json.loads((root/'research/rtl8125-pinout-distributor.json').read_text())
    raw={p['number']:p['name'] for p in source['pins']}
    # Datasheet Tables6/7 expand truncated distributor SPI aliases.
    raw['25']='LED2/EEDO/SPISO';raw['27']='LED1/EESK/SPISCK'
    assert {k:v[0] for k,v in pins.items()}==raw
    assert {k for k,v in pins.items() if v[1]=='no_connect'}=={'4','5','7'}
    assert pins['6']==('POW_EXT_SWR','output')
    assert pins['40']==pins['49']==('GND','power_in')
    f=sx.loads((root/'lib/full-adapter.pretty/Realtek_RTL8125BG_QFN48_EP4.3.kicad_mod').read_text())
    pads={p[1]:p for p in nodes(f,'pad') if p[1]};assert set(pads)=={str(i) for i in range(1,50)}
    for i in range(1,49):
        p=pads[str(i)];j=(i-1)%12;t=round(-2.2+j*.4,6)
        expected=[-2.95,t] if i<=12 else [t,2.95] if i<=24 else [2.95,-t] if i<=36 else [-t,-2.95]
        assert nodes(p,'at')[0][1:3]==expected,(i,nodes(p,'at'))
        assert nodes(p,'size')[0][1:3]==([.8,.2] if i<=12 or 25<=i<=36 else [.2,.8])
    assert nodes(pads['49'],'size')[0][1:3]==[4.3,4.3]
    return dict(status='ETHERNET_LIBRARY_CHECK_NOT_RELEASE',pins_checked=49,footprint_pads_checked=49,external_core_regulator_required=True,temperature_C=[0,70],circuit_validation='check_ethernet_controller.py')
if __name__=='__main__':
    result=check();(ROOT/'research/rtl8125-library-validation.json').write_text(json.dumps(result,indent=2)+'\n');print(result)
