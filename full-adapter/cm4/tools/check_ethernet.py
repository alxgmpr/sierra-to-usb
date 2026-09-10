"""Check exported endpoints and manufacturer land dimensions, independently of capture."""
import json
import xml.etree.ElementTree as ET
from pathlib import Path
import sexpdata as sx


def nodes(n,tag):return [v for v in n if isinstance(v,list) and str(v[0])==tag]
def one(n,tag):return nodes(n,tag)[0]
def close(a,b):assert len(a)==len(b) and all(abs(x-y)<1e-6 for x,y in zip(a,b)),(a,b)


def check(root, tree):
    root=Path(root)
    nets={n.get('name'):{(p.get('ref'),p.get('pin')) for p in n} for n in tree.findall('.//nets/net')}
    pn={p:n for n,ps in nets.items() for p in ps}
    def exact(name,pins):assert nets[name]==set(pins),(name,nets[name],pins)
    # Rows are CM4 +/-, Pulse chip +/-, Pulse media +/-, RJ45 +/-, ESD ref +/-, CTs.
    # Sources: CM4 Table4, HX6096NL RevA p2, standard 1000BASE-T pair assignments.
    rows=[(12,10,2,3,23,22,1,2,'U120',1,2,1,24),
          (4,6,5,6,20,19,3,6,'U120',4,5,4,21),
          (11,9,8,9,17,16,4,5,'U121',1,2,7,18),
          (3,5,11,12,14,13,7,8,'U121',4,5,10,15)]
    for i,(cp,cn,tp,tn,mp,mn,jp,jn,esd,ep,en,tct,mct) in enumerate(rows):
        for pol,cm,chip,media,jack,e in [('P',cp,tp,mp,jp,ep),('N',cn,tn,mn,jn,en)]:
            exact(f'ETH_MDI{i}_{pol}',[('J100',str(cm)),('T120',str(chip)),(esd,str(e))])
            exact(f'ETH_CABLE{i}_{pol}',[('T120',str(media)),('J120',str(jack))])
        exact(pn['T120',str(tct)],[('T120',str(tct)),(f'C{120+i}','1')])
        assert pn[f'C{120+i}','2']=='GND'
        exact('POE_CT_'+'ABCD'[i],[('T120',str(mct)),(f'C{130+i}','1')])
        exact(pn[f'C{130+i}','2'],[(f'C{130+i}','2'),(f'R{130+i}','1')])
    exact(pn['C134','1'],[('C134','1')]+[(f'R{130+i}','2') for i in range(4)])
    for ref,pin in [('C134','2'),('J120','SH')]+[(u,p) for u in ['U120','U121'] for p in ['3','8']]:
        assert pn[ref,pin]=='GND'
    for ref in ['U120','U121']:
        for p in ['6','7','9','10']:assert nets[pn[ref,p]]=={(ref,p)}
    # No component other than the approved Y1 capacitor bridges Bob-Smith star to ground.
    comps={c.get('ref'):c for c in tree.findall('.//components/comp')}
    expected={'T120':'HX6096NL','J120':'855437002','U120':'TPD4EUSB30DQAR','U121':'TPD4EUSB30DQAR',
              'C134':'CY1102ME14EF45W2A2'}
    expected.update({f'C{130+i}':'CC0603KRX7R0BB223' for i in range(4)})
    expected.update({f'R{130+i}':'0603WAF750JT5E' for i in range(4)})
    for ref,mpn in expected.items():
        fields={f.get('name'):f.text for f in comps[ref].findall('fields/field')}
        assert fields['MPN']==mpn
    def pads(name):return nodes(sx.loads((root/'lib/cm4.pretty'/(name+'.kicad_mod')).read_text()),'pad')
    pp=pads('Pulse_HX6096NL')
    assert len(pp)==24 and {p[1] for p in pp}==set(map(str,range(1,25)))
    for p in pp:
        n=int(p[1]);close(one(p,'size')[1:3],[.762,1.905])
        close(one(p,'at')[1:3],[-6.985+(n-1 if n<=12 else 24-n)*1.27,7.3025 if n<=12 else -7.3025])
    pp=pads('Molex_855437002');assert len(pp)==10
    assert {p[1] for p in pp}==set(map(str,range(1,9)))|{'SH'}
    for p in pp:
        if p[1]=='SH':
            close(one(p,'size')[1:3],[2.54,3.6])
            close([abs(one(p,'at')[1]),one(p,'at')[2]],[8.085,-4.74])
        else:
            close(one(p,'at')[1:3],[-4.445+(int(p[1])-1)*1.27,-18.515])
            close(one(p,'size')[1:3],[.76,6.35])
    fp=sx.loads((root/'lib/cm4.pretty/Molex_855437002.kicad_mod').read_text())
    zones=nodes(fp,'zone');assert len(zones)==1
    assert one(zones[0],'layers')[1:]==['F.Cu']
    keep=one(zones[0],'keepout')
    assert all(one(keep,key)[1]==sx.Symbol('not_allowed') for key in ['tracks','vias','copperpour','footprints'])
    pp=pads('TI_DQA0010_TPD4EUSB30')
    assert len(pp)==11 and {p[1] for p in pp}==set(map(str,range(1,11)))
    for p in pp:
        at=one(p,'at')[1:3]
        if at==[0,0]:assert p[1]=='3';close(one(p,'size')[1:3],[.8,.4]);continue
        n=int(p[1]);close(at,[-.4175 if n<=5 else .4175,-1+(n-1 if n<=5 else 10-n)*.5])
        close(one(p,'size')[1:3],[.565,.4 if n in [3,8] else .2])
    pp=pads('Dersonic_CY1102ME14EF45W2A2_P10mm');assert len(pp)==2
    for p in pp:
        close(one(p,'at')[1:3],[-5 if p[1]=='1' else 5,0]);close(one(p,'size')[1:3],[2,2])
        assert one(p,'drill')[1]==1
    for name in ['Pulse_HX6096NL','Molex_855437002','TI_DQA0010_TPD4EUSB30','Dersonic_CY1102ME14EF45W2A2_P10mm']:
        path=root/'lib/cm4.3dshapes'/(name+'.step')
        assert path.is_file() and path.stat().st_size>1000,path
        assert path.read_text().startswith('ISO-10303-21;'),path
    return {'mdi_pairs':4,'cable_pairs':4,'isolated_poe_taps':4,'esd_channels':8,
            'safety_capacitor':'C134 / Y1', 'poe_conversion_integrated':False}


if __name__=='__main__':
    import sys
    print(json.dumps(check(Path(__file__).resolve().parents[1],ET.parse(sys.argv[1]).getroot()),indent=2))
