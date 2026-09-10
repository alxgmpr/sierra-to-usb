"""Check Ethernet buck pin/pad mapping, exported connectivity and sizing corners."""
from pathlib import Path
from xml.etree import ElementTree as ET
import json,subprocess,tempfile
import sexpdata as sx
ROOT=Path(__file__).resolve().parents[1]
CLI='/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli'
def nodes(n,t):return [v for v in n if isinstance(v,list) and str(v[0])==t]

def sizing(root):
    # Independent equations: includes opposing resistor TCR through -40..125C,
    # 0.1% resistance tolerance, +/-1% VFB and +/-70nA feedback leakage.
    rails={}
    for name,rt,rb,ppm in [('3v3',45300,10000,50),('core',14000,24000,25)]:
        a=.001+ppm*1e-6*100;b=.001+25e-6*100
        low=.594*(1+rt*(1-a)/(rb*(1+b)))-70e-9*rt*(1+a)
        high=.606*(1+rt*(1+a)/(rb*(1-b)))+70e-9*rt*(1+a)
        rails[name]={'nominal_V':.6*(1+rt/rb),'dc_min_V':low,'dc_max_V':high}
    assert 3.14<rails['3v3']['dc_min_V']<rails['3v3']['dc_max_V']<3.46
    assert .92<rails['core']['dc_min_V']<rails['core']['dc_max_V']<.98
    # Samsung's DC-bias curve is typical, not a guaranteed minimum. Add 20%
    # allowance for aging/curve spread, in addition to tolerance and X5R temp.
    curve=json.loads((root/'research/core-22uf-qualification.json').read_text())['dc_bias_curve']['selectPartsList'][0]['chartList'][0]['data']
    curve=sorted((float(v['x']),float(v['y'])) for v in curve)
    def bias(v):
        for (x0,y0),(x1,y1) in zip(curve,curve[1:]):
            if x0<=v<=x1:return 1+(y0+(y1-y0)*(v-x0)/(x1-x0))/100
        raise ValueError(v)
    cap={name:count*22*bias(v)*.8*.85*.8 for name,v,count in [('input_5v',5.25,2),('output_3v3',3.46,5),('input_core',3.46,2),('output_core',.98,5)]}
    assert cap['input_5v']>5 and cap['input_core']>5
    assert cap['output_3v3']>32 and cap['output_core']>53
    # 10nF +/-5%, C0G +/-30ppm/C; source current 2.1..2.8uA.
    ramp=[.594*10e-9*(1-.053)/2.8e-6*1000,.606*10e-9*(1+.053)/2.1e-6*1000]
    assert .5<.8*ramp[0] and ramp[1]<5
    ton=rails['core']['dc_min_V']/rails['3v3']['dc_max_V']/(2.475e6+.288e6)*1e9
    assert ton>75
    return {'voltage_corners':rails,'estimated_effective_capacitance_uF':cap,'soft_start_0_to_100_ms':ramp,
            'core_on_time_ns_at_max_base_frequency_plus_typical_SSC':ton,
            'calculation_limits':'DC bounds exclude ripple, transient excursion and PCB drop. Capacitance includes 20% design allowance, not a manufacturer minimum guarantee. Soft start uses the TI reference-charge model; SSC deviation and tracking gain/offset are typical. Validate waveforms on hardware.'}

def check(root=ROOT):
    sym=next(v for v in nodes(sx.loads((root/'lib/full-adapter.kicad_sym').read_text()),'symbol') if v[1]=='TPS6281320QWRWYRQ1')
    actual={nodes(p,'number')[0][1]:(nodes(p,'name')[0][1],str(p[1])) for u in nodes(sym,'symbol') for p in nodes(u,'pin')}
    names={'1':'MODE/SYNC','2':'VIN','3':'SW','4':'GND','5':'FB','6':'SS/TR','7':'COMP/FSET','8':'EN','9':'PG'}
    assert {k:v[0] for k,v in actual.items()}==names
    assert actual['2'][1]=='power_in' and actual['3'][1]=='power_out' and actual['9'][1]=='open_collector'
    f=sx.loads((root/'lib/full-adapter.pretty/TI_RWY0009_2x3mm.kicad_mod').read_text())
    pads=nodes(f,'pad');cu=[p for p in pads if p[1]]
    assert len(cu)==13 and {p[1] for p in cu}==set(names)
    def shape(p):return tuple(nodes(p,'at')[0][1:3]+nodes(p,'size')[0][1:3])
    expected={'2':[(0,-.5,2.3,.25)],'3':[(0,0,2.3,.25)],'4':[(0,.5,2.3,.25)],'9':[(0,-1.325,.25,.65)],'6':[(0,1.325,.25,.65)]}
    for n,x,y in [('1',-1,-1),('8',1,-1),('5',-1,1),('7',1,1)]:expected[n]=[(x*.7625,y,.775,.25),(x*.55,y*1.2625,.35,.775)]
    assert {n:sorted(shape(p) for p in cu if p[1]==n) for n in names}=={n:sorted(v) for n,v in expected.items()}
    paste=[p for p in pads if not p[1]];assert len(paste)==14
    assert all(nodes(p,'layers')[0][1:]==['F.Paste'] for p in paste)
    for y in [-.5,0,.5]:
        assert {(x,y,1.05,.25) for x in [-.625,.625]}<={shape(p) for p in paste}
    with tempfile.TemporaryDirectory() as d:
        path=Path(d)/'nets.xml';subprocess.run([CLI,'sch','export','netlist','--format','kicadxml','-o',str(path),str(root/'cad/full-adapter.kicad_sch')],check=True,capture_output=True)
        tree=ET.parse(path);nets={n.get('name'):{(p.get('ref'),p.get('pin')) for p in n.findall('node')} for n in tree.findall('.//nets/net')}
        def attached(ref,pin):return next(n for n in nets.values() if (ref,pin) in n)
        parts={p.get('ref'):p for p in tree.findall('.//components/comp')}
        assert ('U11','6') in nets['ETH_CORE_ENABLE']
        for n,u,vin,out,en,pg,top,bottom in [(650,'U12','VCC5V_SYS','VCC3V3_ETH','VCC3V3_S0','ETH_3V3_PG','RT0603BRE0745K3L','RT0603BRD0710KL'),(660,'U13','VCC3V3_ETH','VDD0V95_ETH','ETH_CORE_ENABLE','ETH_CORE_PG','RT0603BRD0714KL','RT0603BRD0724KL')]:
            assert {(u,'1'),(u,'2'),(f'C{n}','1'),(f'C{n+1}','1')}<=nets[vin]
            assert {(u,'8'),(f'R{n+2}','1')}<=nets[en] and vin!=en
            assert {(u,'4'),(u,'7'),(f'R{n+1}','2'),(f'R{n+2}','2')}<=nets['GND']
            assert attached(u,'3')=={(u,'3'),(f'L{n}','1')}
            assert attached(u,'5')=={(u,'5'),(f'R{n}','2'),(f'R{n+1}','1')}
            assert attached(u,'6')=={(u,'6'),(f'C{n+2}','1')}
            assert attached(u,'9')=={(u,'9'),(f'R{n+3}','2'),(f'TP{n+1}','1')}
            assert {(f'L{n}','2'),(f'R{n}','1'),(f'TP{n}','1')}|{(f'C{i}','1') for i in range(n+3,n+8)}<=nets[out]
            assert {(f'C{i}','2') for i in range(n,n+8)}<=nets['GND']
            assert (f'R{n+3}','1') in nets['VCC3V3_ETH']
            selected={u:'TPS6281320QWRWYRQ1',f'L{n}':'SPM5030T-R47M',f'R{n}':top,f'R{n+1}':bottom,f'C{n+2}':'GRM1885C1H103JA01D'}
            selected.update({f'C{i}':'CL21A226MAYNNNE' for i in list(range(n,n+2))+list(range(n+3,n+8))})
            stock=json.loads((root/'research/ethernet-regulator-stock.json').read_text());by_mpn={**stock['passives'],'TPS6281320QWRWYRQ1':stock['regulator']}
            for ref,mpn in selected.items():
                fields={f.get('name'):f.text for f in parts[ref].findall('fields/field')}
                assert (fields['MPN'],fields['LCSC'])==(mpn,by_mpn[mpn]['lcsc']),ref
    return dict(status='ETHERNET_POWER_CAPTURE_NOT_RELEASE',regulators=2,logical_pins_and_pads=9,sizing=sizing(root),controller_captured=True,hardware_reset_complete=False,system_routed=False)
if __name__=='__main__':
    result=check();(ROOT/'research/ethernet-power-validation.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
