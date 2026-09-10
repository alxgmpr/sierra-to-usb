"""Independent physical-pin connectivity and passive checks for the RTL capture."""
from pathlib import Path
from xml.etree import ElementTree as ET
import json,subprocess,tempfile
import sexpdata as sx

ROOT=Path(__file__).resolve().parents[1]
CLI='/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli'
def nodes(n,t):return [v for v in n if isinstance(v,list) and str(v[0])==t]


def capacitance(root):
    c4=json.loads((root/'research/ethernet-4u7-bias.json').read_text())
    c22=json.loads((root/'research/core-22uf-qualification.json').read_text())['dc_bias_curve']
    def estimate(curve,nominal,tolerance,v):
        points=sorted((float(p['x']),float(p['y'])) for p in curve['selectPartsList'][0]['chartList'][0]['data'])
        for (x0,y0),(x1,y1) in zip(points,points[1:]):
            if x0<=v<=x1:
                factor=1+(y0+(y1-y0)*(v-x0)/(x1-x0))/100
                return nominal*factor*(1-tolerance)*.85*.8
        raise ValueError(v)
    c={name:estimate(curve,n,t,v) for name,curve,n,t,v in [
        ('4u7_at_3v46',c4,4.7,.1,3.46),('4u7_at_0v98',c4,4.7,.1,.98),
        ('22u_at_3v46',c22,22,.2,3.46),('22u_at_0v98',c22,22,.2,.98)]}
    assert c['4u7_at_3v46']>1
    assert c['4u7_at_0v98']>2.2
    assert c['22u_at_3v46']>2.2
    assert c['22u_at_0v98']>10
    # Upper bounds omit negative DC-bias loss, include positive tolerance/temp.
    # Include regulator banks and U13 input bank in U12's capacitive load.
    upper33=(5+2+3+1)*22*1.2*1.15+4.7*1.1*1.15+3*.1*1.1*1.15
    upper09=(5+2)*22*1.2*1.15+5*4.7*1.1*1.15
    assert upper33<470 and upper09<470
    return {'estimated_effective_uF':c,'total_output_capacitance_upper_uF':{'3v3':upper33,'core':upper09},
        'limits':'Typical Samsung DC-bias curves with 20% design allowance, nominal tolerance and X5R temperature loss. Estimates are not guaranteed production minima. Ripple, filter resonance and startup require hardware validation.'}


def check(root=ROOT):
    with tempfile.TemporaryDirectory() as tmp:
        xml=Path(tmp)/'nets.xml';subprocess.run([CLI,'sch','export','netlist','--format','kicadxml','-o',str(xml),str(root/'cad/full-adapter.kicad_sch')],check=True,capture_output=True)
        tree=ET.parse(xml)
        nets={n.get('name'):{(p.get('ref'),p.get('pin')) for p in n.findall('node')} for n in tree.findall('.//nets/net')}
        def net(name):
            matches=[v for k,v in nets.items() if k.rsplit('/',1)[-1]==name];assert len(matches)==1,(name,matches)
            return matches[0]
        def attached(ref,pin):
            matches=[v for v in nets.values() if (ref,pin) in v];assert len(matches)==1,(ref,pin,matches)
            return matches[0]
        def exact(name,pins):assert net(name)==set(pins),(name,net(name)^set(pins))
        ground=net('GND');v33=net('VCC3V3_ETH');core=net('VDD0V95_ETH');pll=net('VCC3V3_ETH_PLL')
        assert {p for r,p in v33 if r=='U11'}=={'19','29','33','34','43','46'}
        assert {p for r,p in core if r=='U11'}=={'8','11','16','22','28','37','47'}
        assert {p for r,p in ground if r=='U11'}=={'40','49'}
        assert pll=={('U11','15'),('FB670','2'),('C676','1'),('C677','1')}
        assert ('FB670','1') in v33
        assert all(a.isdisjoint(b) for i,a in enumerate([ground,v33,core,pll,net('VCC3V3_S0')]) for b in [ground,v33,core,pll,net('VCC3V3_S0')][i+1:])
        for n in range(670,685):
            rail=v33 if n<=675 else pll if n<=677 else core
            assert (f'C{n}','1') in rail and (f'C{n}','2') in ground,n
        exact('ETH_CORE_ENABLE',[('U11','6'),('U13','8'),('R662','1')])
        for name,pin,ref in [('ETH_GPI','3','R672'),('ETH_LED1','27','R673'),('ETH_WAKE_N','2','R677'),('ETH_CLKREQ_N','48','R678')]:
            exact(name,[('U11',pin),(ref,'2')]);assert (ref,'1') in v33
        for name,pin,ref in [('ETH_EEDO_IDLE','25','R674'),('ETH_EEDI_STRAP','30','R675'),('ETH_EESEL_STRAP','32','R676'),('ETH_PERST_N','36','R679')]:
            exact(name,[('U11',pin),(ref,'1')]);assert (ref,'2') in ground
        exact('ETH_ISOLATE_N',[('U11','1'),('R680','2'),('R681','1')]);assert ('R680','1') in v33 and ('R681','2') in ground
        for pin in ['4','5','7','26','31','35']:assert attached('U11',pin)=={('U11',pin)}
        exact('ETH_XTAL_IN',[('U11','10'),('Y670','1'),('C685','1')])
        exact('ETH_XTAL_OUT',[('U11','9'),('R671','1')])
        exact('ETH_XTAL_LOAD',[('R671','2'),('Y670','3'),('C686','1')])
        assert {('Y670','2'),('Y670','4'),('C685','2'),('C686','2'),('R670','2')}<=ground
        assert attached('U11','12')=={('U11','12'),('R670','1')}
        for name,pins in {
            'SOC_PCIE_TX_P':[('U1','W27'),('C687','1')], 'SOC_PCIE_TX_N':[('U1','W28'),('C688','1')],
            'PCIE_SOC_TO_ETH_P':[('C687','2'),('U11','41')], 'PCIE_SOC_TO_ETH_N':[('C688','2'),('U11','42')],
            'ETH_PCIE_TX_P':[('U11','38'),('C689','1')], 'ETH_PCIE_TX_N':[('U11','39'),('C690','1')],
            'PCIE_ETH_TO_SOC_P':[('C689','2'),('U1','Y27')], 'PCIE_ETH_TO_SOC_N':[('C690','2'),('U1','Y28')],
            'PCIE_REFCLK_P':[('U1','V24'),('U11','44')], 'PCIE_REFCLK_N':[('U1','V25'),('U11','45')]}.items():exact(name,pins)
        for pair,p,n in [(0,'13','14'),(1,'17','18'),(2,'20','21'),(3,'23','24')]:
            exact(f'ETH_MDI{pair}_P',[('U11',p)]);exact(f'ETH_MDI{pair}_N',[('U11',n)])
        parts={p.get('ref'):p for p in tree.findall('.//components/comp')}
        expected={'U11':('RTL8125BG-CG','C3013605'),'Y670':('X322525MOB4SI','C9006'),
            'FB670':('BLM18PG330SN1D','C88984'),'R670':('RT0603BRD072K49L','C861299'),'R681':('0402WGF1502TCE','C25756')}
        expected.update({f'C{n}':('CL21A226MAYNNNE','C602037') for n in [670,671,672,676,683,684]})
        expected.update({f'C{n}':('CL10A475KA8NQNC','C69335') for n in [673,678,679,680,681,682]})
        expected.update({f'C{n}':('0402CG200J500NT','C1554') for n in [685,686]})
        expected.update({f'R{n}':('0402WGF4701TCE','C25900') for n in [672,673,677,678]})
        for ref,(mpn,lcsc) in expected.items():
            fields={f.get('name'):f.text for f in parts[ref].findall('fields/field')}
            assert (fields['MPN'],fields['LCSC'])==(mpn,lcsc),ref
        for n in [674,675,677,687,688,689,690]:assert parts[f'C{n}'].findtext('value')=='100nF'
        assert parts['R671'].findtext('value')=='0R'
        for n in [674,675,676,679]:assert parts[f'R{n}'].findtext('value')=='47kR 1%'
        assert parts['R680'].findtext('value')=='1kR 1%'
    # Independently check all four physical crystal pins, not just the stacked symbol.
    f=sx.loads((root/'lib/full-adapter.pretty/YXC_X322525MOB4SI.kicad_mod').read_text())
    pads={p[1]:p for p in nodes(f,'pad')};assert set(pads)=={'1','2','3','4'}
    for n,xy in {'1':[-1.1,.85],'2':[1.1,.85],'3':[1.1,-.85],'4':[-1.1,-.85]}.items():
        assert nodes(pads[n],'at')[0][1:3]==xy and nodes(pads[n],'size')[0][1:3]==[1.4,1.2]
    f=sx.loads((root/'lib/full-adapter.pretty/Murata_BLM18PG330SN1D_0603.kicad_mod').read_text())
    assert {p[1] for p in nodes(f,'pad')}=={'1','2'}
    for p in nodes(f,'pad'):
        assert nodes(p,'at')[0][1:3]==[-.675 if p[1]=='1' else .675,0]
        assert nodes(p,'size')[0][1:3]==[.65,.7]
    return {'status':'ETHERNET_CONTROLLER_CAPTURE_NOT_RELEASE','controller_pins':49,'processor_PCIe_balls':6,
        'PCIe_transmit_coupling_capacitors':4,'local_bypass_capacitors':15,'crystal_load_capacitors':2,
        'capacitance':capacitance(root),'hardware_reset_complete':False,'magnetics_connected':False,'system_routed':False}

if __name__=='__main__':
    result=check();(ROOT/'research/ethernet-controller-validation.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
