"""Verify exported modem contacts, physical isolation profiles and maker lands."""
import json
from pathlib import Path
import sexpdata as sx


def nodes(n,tag):return [v for v in n if isinstance(v,list) and str(v[0])==tag]
def one(n,tag):return nodes(n,tag)[0]
def close(a,b):assert len(a)==len(b) and all(abs(x-y)<1e-6 for x,y in zip(a,b)),(a,b)


def check(root,tree):
    root=Path(root)
    nets={n.get('name'):{(p.get('ref'),p.get('pin')) for p in n} for n in tree.findall('.//nets/net')}
    pn={p:n for n,ps in nets.items() for p in ps}
    comps={c.get('ref'):c for c in tree.findall('.//components/comp')}
    def exact(net,pins):assert nets[net]==set(pins),(net,nets[net],pins)
    def fields(ref):return {p.get('name'):p.text for p in comps[ref].findall('fields/field')}
    contacts=set(map(str,range(1,12)))|set(map(str,range(20,76)))
    assert {p for r,p in pn if r=='J200'}==contacts|{'SH'}
    ground={3,5,11,27,33,39,45,51,57,71,73}
    assert {int(p) for r,p in nets['GND'] if r=='J200' and p!='SH'}==ground
    assert pn['J200','SH']=='GND'
    assert {int(p) for r,p in nets['VCC_MODEM'] if r=='J200'}=={2,4,70,72,74}
    for n,ref in [(24,'R200'),(38,'R201'),(68,'R202'),(20,'R203'),(22,'R204'),(28,'R205'),
                  (40,'R220'),(42,'R221'),(44,'R222'),(46,'R223'),(48,'R224')]:
        expected_pin='2' if n in [24,38,68,20,22] else '1'
        exact('M2_P'+str(n),[('J200',str(n)),(ref,expected_pin)])
    for n,net in [(7,'MODEM_USB2_P'),(9,'MODEM_USB2_N'),(29,'MODEM_USB3_M2H_N'),
                  (31,'MODEM_USB3_M2H_P'),(35,'MODEM_USB3_H2M_N'),(37,'MODEM_USB3_H2M_P')]:
        assert pn['J200',str(n)]==net
    unused={1,21,25,41,43,47,49,50,52,53,54,55,56,58,59,60,61,62,63,64,65,69,75}
    for n in unused:assert nets[pn['J200',str(n)]]=={('J200',str(n))},n
    for n,net in [(6,'MODEM_FULL_ON'),(8,'MODEM_RADIO_N'),(26,'MODEM_GNSS_N'),
                  (67,'MODEM_RESET_N'),(10,'MODEM_LED_N'),(23,'MODEM_WAKE_N')]:assert pn['J200',str(n)]==net
    for n,sig in [(30,'RST_MODULE'),(32,'CLK_MODULE'),(34,'DATA_MODULE'),(36,'PWR'),(66,'DET')]:
        assert pn['J200',str(n)]=='SIM1_'+sig
    for which,base in [(1,230),(2,240)]:
        j='J'+str(200+which);prefix='SIM'+str(which)
        assert fields(j)['MPN']=='SMN-303-ARP7' and fields(j)['LCSC']=='C5137194'
        for pin,sig in [('C1','PWR'),('C2','RST'),('C3','CLK'),('C7','DATA'),('CD','DET')]:
            assert pn[j,pin]==prefix+'_'+sig
        for pin in ['C5','SH']:assert pn[j,pin]=='GND'
        assert nets[pn[j,'C6']]=={(j,'C6')}
        for i,sig in enumerate(['RST','CLK','DATA']):
            r=f'R{base+i}';assert fields(r)['MPN']=='0402WGF220JTCE'
            assert pn[r,'1']==prefix+'_'+sig+'_MODULE' and pn[r,'2']==prefix+'_'+sig
            assert pn[f'C{base+1+i}','1']==prefix+'_'+sig and pn[f'C{base+1+i}','2']=='GND'
        assert pn[f'R{base+3}','1']==prefix+'_PWR' and pn[f'R{base+3}','2']==prefix+'_DATA'
        assert fields(f'R{base+3}')['MPN']=='0402WGF1802TCE'
        assert pn[f'C{base}','1']==prefix+'_PWR' and pn[f'C{base}','2']=='GND'
        assert pn[f'D{base}','1']==prefix+'_PWR' and pn[f'D{base}','2']=='GND'
        u=f'U{base}'
        for n,sig in [('1','RST'),('2','CLK'),('4','DATA'),('5','DET')]:assert pn[u,n]==prefix+'_'+sig
        for n in ['3','8']:assert pn[u,n]=='GND'
        for n in ['6','7','9','10']:assert nets[pn[u,n]]=={(u,n)}
    profiles=json.loads((root/'research/modem-profiles.json').read_text())
    link_refs={f'R{i}' for i in range(200,206)}|{f'R{i}' for i in range(220,225)}
    assert set(profiles['profile_links'])==link_refs
    # Schematic DNP markers are the safe default, distinct from simulated fitted links.
    dnp=set()
    for file in (root/'cad').glob('*.kicad_sch'):
        for s in nodes(sx.loads(file.read_text()),'symbol'):
            ref=next(p[2] for p in nodes(s,'property') if p[1]=='Reference')
            if nodes(s,'dnp') and one(s,'dnp')[1]==sx.Symbol('yes'):dnp.add(ref)
    assert link_refs<=dnp
    for ref,(a,b) in profiles['profile_links'].items():
        assert (pn[ref,'1'],pn[ref,'2'])==(a,b)
        assert fields(ref)['MPN']=='RC0603JR-070RL'
    verified=[]
    for name,p in profiles['profiles'].items():
        fitted=set(p['fit']);assert fitted<=link_refs
        sierra=name.startswith('em');sim2=name.endswith('external_sim2')
        assert fitted==(({f'R{i}' for i in range(200,206)} if sierra else set())|
                        ({f'R{i}' for i in range(220,225)} if sim2 else set())),name
        parent={n:n for n in nets}
        def find(n):
            while parent[n]!=n:n=parent[n]
            return n
        for ref in fitted:
            a,b=profiles['profile_links'][ref];parent[find(a)]=find(b)
        reachable={int(n) for n in contacts if find(pn['J200',n])==find('VCC_MODEM')}
        assert reachable==({2,4,24,38,68,70,72,74} if sierra else {2,4,70,72,74})
        for n,signal in [(20,'MODEM_1V8'),(22,'MODEM_USB_VBUS_SENSE'),(28,'MODEM_PLA_N')]:
            assert (find('M2_P'+str(n))==find(signal))==sierra
        for n,sig in [(40,'DET'),(42,'DATA_MODULE'),(44,'CLK_MODULE'),(46,'RST_MODULE'),(48,'PWR')]:
            assert (find('M2_P'+str(n))==find('SIM2_'+sig))==sim2
        for rail in ['GND','SIM1_PWR','SIM2_PWR','CM4_3V3','VCC5V_CM4','MODEM_1V8']:
            assert find('VCC_MODEM')!=find(rail)
        verified.append(name)
    assert fields('J200')['MPN']=='MDT420B01411' and not fields('J200').get('LCSC')
    assert profiles['procurement_unresolved'][0]['ref']=='J200'
    def pads(name):return nodes(sx.loads((root/'lib/cm4.pretty'/(name+'.kicad_mod')).read_text()),'pad')
    ps=pads('Amphenol_MDT420B01411');assert len(ps)==71
    assert {p[1] for p in ps}==contacts|{'SH',''}
    by={p[1]:p for p in ps if p[1] and p[1]!='SH'}
    for n,at in {'1':[-9.25,-5.275],'11':[-6.75,-5.275],'21':[-4.25,-5.275],
                 '75':[9.25,-5.275],'2':[-9,2.275],'10':[-7,2.275],
                 '20':[-4.5,2.275],'74':[9,2.275]}.items():close(one(by[n],'at')[1:3],at)
    for p in by.values():close(one(p,'size')[1:3],[.3,1.55])
    holes={one(p,'at')[1]:one(p,'drill')[1] for p in ps if p[1]==''}
    assert holes=={-10:1.1,10:1.6}
    for p in ps:
        if p[1]=='SH':close(one(p,'size')[1:3],[1.2,2.75]);close([abs(one(p,'at')[1]),one(p,'at')[2]],[10.35,-4.5])
    ps=pads('Xunpu_SMN303_ARP7');assert len(ps)==11 and {p[1] for p in ps}=={'C1','C2','C3','C5','C6','C7','CD','SH'}
    anchors={'C3':-4.83,'C7':-3.56,'C2':-2.29,'C6':-1.02,'C1':.25,'C5':1.52,'CD':2.47}
    for p in ps:
        if p[1]=='SH':
            close(one(p,'size')[1:3],[.7,2.1]);assert abs(one(p,'at')[1])==6.5 and one(p,'at')[2] in [1.48,13.48]
        else:close(one(p,'at')[1:3],[anchors[p[1]],0]);close(one(p,'size')[1:3],[.8,1.14])
    ps=pads('TI_DPY0002_TPD1E05U06');assert len(ps)==2
    for p in ps:close(one(p,'at')[1:3],[-.35 if p[1]=='1' else .35,0]);close(one(p,'size')[1:3],[.3,.5])
    for name in ['Amphenol_MDT420B01411','Xunpu_SMN303_ARP7','TI_DPY0002_TPD1E05U06']:
        model=root/'lib/cm4.3dshapes'/(name+'.step');assert model.stat().st_size>1000
    return {'modem_contacts':67,'profiles_checked':verified,'physical_profile_links':11,
            'sim_sockets':2,'procurement_unresolved':['J200 / MDT420B01411'],
            'power_control_host_qualification_complete':False}


if __name__=='__main__':
    import sys,xml.etree.ElementTree as ET
    print(json.dumps(check(Path(__file__).resolve().parents[1],ET.parse(sys.argv[1]).getroot()),indent=2))
