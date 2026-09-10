"""Independent control pin, supply, reset-net and corner checks."""
from pathlib import Path
from xml.etree import ElementTree as ET
import json, subprocess, tempfile
import sexpdata as sx
ROOT=Path(__file__).resolve().parents[1]
CLI='/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli'
def nodes(n,t):return [v for v in n if isinstance(v,list) and str(v[0])==t]


def margins():
    # 1% tolerance plus100ppm/K over100K, conservatively added.
    rpu=1500*1.02;rpd=16000;leak=15e-6
    high_drop=3.465*rpu/(rpu+rpd)+leak*rpu*rpd/(rpu+rpd)
    sink=3.465/(1500*.98)+3.380541/(4700*.98)
    supervisor_rise=3.07*1.015*1.025
    reset_high=(3.256156/(10000*1.02)-.8e-6)/(1/(10000*1.02)+1/(47000*.98))
    mr_sink=3.380541*(2/(47000*.98)+1/70000)
    assert high_drop<.4 and sink<.006
    assert supervisor_rise<3.256156 and reset_high>2.0
    assert mr_sink<.002 and .55<.3*3.256156
    assert .180-.010>.100
    return dict(host_HIGH_drop_bound_V=high_drop,FXMA_HIGH_drop_limit_V=.4,
        maximum_static_LOW_pullup_current_A=sink,supervisor_rising_threshold_upper_V=supervisor_rise,
        PERST_HIGH_lower_V=reset_high,condition_LOW_pullup_current_upper_A=mr_sink,
        delay_min_s=.180,delay_max_s=.420,normal_ramp_allowance_s=.010,
        limits='FXMA VOL max is specified at0.15V input/6mA. Endpoint VOL may reach0.4V; the data sheet gives only a typical transfer curve there. Verify translated LOW<0.8V at actual load, temperature and process. No guaranteed fast-fault timing claimed.')


def check(root=ROOT):
    lib=sx.loads((root/'lib/full-adapter.kicad_sym').read_text())
    maps={
        'FXMA2102L8X':{'1':('VCCA','power_in'),'2':('A0','bidirectional'),'3':('A1','bidirectional'),'4':('GND','power_in'),'5':('OE','input'),'6':('B1','bidirectional'),'7':('B0','bidirectional'),'8':('VCCB','power_in')},
        'SN74LVC1G07DCKR':{'1':('NC','no_connect'),'2':('A','input'),'3':('GND','power_in'),'4':('Y','open_collector'),'5':('VCC','power_in')},
        'TPS3808G33DBVR':{'1':('~{RESET}','open_collector'),'2':('GND','power_in'),'3':('~{MR}','input'),'4':('CT','passive'),'5':('SENSE','input'),'6':('VDD','power_in')}}
    for name,expected in maps.items():
        sym=next(v for v in nodes(lib,'symbol') if v[1]==name)
        pins={nodes(p,'number')[0][1]:(nodes(p,'name')[0][1],str(p[1])) for u in nodes(sym,'symbol') for p in nodes(u,'pin')}
        assert pins==expected,(name,pins)
    geometries={
        'Onsemi_FXMA2102_523AY':{'1':([-.605,-.5],[.4,.25]),'2':([-.605,0],[.4,.25]),'3':([-.605,.5],[.4,.25]),'4':([0,.575],[.25,.45]),'5':([.605,.5],[.4,.25]),'6':([.605,0],[.4,.25]),'7':([.605,-.5],[.4,.25]),'8':([0,-.575],[.25,.45])},
        'TI_DCK0005A':{str(i):(xy,[.95,.4]) for i,xy in enumerate([[-1.1,-.65],[-1.1,0],[-1.1,.65],[1.1,.65],[1.1,-.65]],1)},
        'TI_DBV0006A':{str(i):(xy,[1.1,.6]) for i,xy in enumerate([[-1.3,-.95],[-1.3,0],[-1.3,.95],[1.3,.95],[1.3,0],[1.3,-.95]],1)}}
    for name,expected in geometries.items():
        fp=sx.loads((root/'lib/full-adapter.pretty'/(name+'.kicad_mod')).read_text())
        actual={p[1]:(nodes(p,'at')[0][1:3],nodes(p,'size')[0][1:3]) for p in nodes(fp,'pad')}
        assert actual==expected,(name,actual)
        assert (root/'lib/full-adapter.3dshapes'/(name+'.step')).stat().st_size>1000
    with tempfile.TemporaryDirectory() as tmp:
        path=Path(tmp)/'nets.xml';subprocess.run([CLI,'sch','export','netlist','--format','kicadxml','-o',str(path),str(root/'cad/full-adapter.kicad_sch')],check=True,capture_output=True)
        tree=ET.parse(path)
        nets={n.get('name'):{(p.get('ref'),p.get('pin')) for p in n.findall('node')} for n in tree.findall('.//nets/net')}
        def exact(name,pins):
            found=[v for k,v in nets.items() if k.rsplit('/',1)[-1]==name]
            assert len(found)==1 and found[0]==set(pins),(name,found)
        for name,pins in {
            'SOC_PCIE_PERST_N':[('U1','AD1'),('R702','1'),('U15','2')],
            'SOC_PCIE_WAKE_N':[('U1','AD7'),('R700','2'),('U14','2')],
            'SOC_PCIE_CLKREQ_N':[('U1','AG6'),('R701','2'),('U14','3')],
            'ETH_WAKE_N':[('U11','2'),('R677','2'),('U14','7')],
            'ETH_CLKREQ_N':[('U11','48'),('R678','2'),('U14','6')],
            'ETH_RESET_CONDITION_N':[('U12','9'),('U13','9'),('R653','2'),('R663','2'),('TP651','1'),('TP661','1'),('U15','4'),('U16','3')],
            'ETH_RESET_CT':[('U16','4'),('R703','2')],
            'ETH_PERST_N':[('U11','36'),('R679','1'),('U16','1'),('R704','2')]}.items():exact(name,pins)
        assert {('U14','1'),('U14','5'),('C700','1'),('R700','1'),('R701','1')}<=nets['VCC3V3_S0']
        assert {('U14','8'),('U15','5'),('U16','5'),('U16','6'),('C701','1'),('C702','1'),('C703','1'),('R703','1'),('R704','1')}<=nets['VCC3V3_ETH']
        assert {('U14','4'),('U15','3'),('U16','2'),('R702','2')}|{(f'C{i}','2') for i in range(700,704)}<=nets['GND']
        assert next(v for v in nets.values() if ('U15','1') in v)=={('U15','1')}
        assert nets['VCC3V3_S0'].isdisjoint(nets['VCC3V3_ETH'])
        parts={p.get('ref'):p for p in tree.findall('.//components/comp')}
        for ref,mpn,lcsc in [('U14','FXMA2102L8X','C107408'),('U15','SN74LVC1G07DCKR','C7830'),('U16','TPS3808G33DBVR','C43698'),('R700','0402WGF1501TCE','C25867'),('R701','0402WGF1501TCE','C25867')]:
            fields={f.get('name'):f.text for f in parts[ref].findall('fields/field')}
            assert (fields['MPN'],fields['LCSC'])==(mpn,lcsc),ref
        for ref,value in [('R700','1.5kR 1%'),('R701','1.5kR 1%'),('R702','47kR 1%'),('R703','100kR 1%'),('R704','10kR 1%')]:assert parts[ref].findtext('value')==value
    return dict(status='ETHERNET_CONTROL_CAPTURE_NOT_RELEASE',physical_IC_pins_checked=19,
        functional_M1_balls=['AD1','AD7','AG6'],startup_delay_captured=True,control_isolation_captured=True,
        fast_fault_timing_qualified=False,hardware_tested=False,system_routed=False,margins=margins())


if __name__=='__main__':
    result=check();(ROOT/'research/ethernet-control-validation.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
