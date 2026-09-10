"""Independent CM4 capture assertions; passing is not manufacturing release."""
from collections import Counter
from pathlib import Path
import json
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET
import sexpdata as sx

KICAD='/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli'


def nodes(n,tag):return [v for v in n if isinstance(v,list) and str(v[0])==tag]
def one(n,tag):return nodes(n,tag)[0]


def expand(number):
    return number[1:-1].split(',') if number.startswith('[') else [number]


def check(root=None, output=None):
    root=Path(root or Path(__file__).resolve().parents[1])
    lib=sx.loads((root/'lib/cm4.kicad_sym').read_text())
    symbols={s[1]:s for s in nodes(lib,'symbol')}
    source=json.loads((root/'research/cm4-pins.json').read_text())['pins']
    assert set(source)==set(map(str,range(1,201)))
    # Preserve source pin names, with the following explicit rail aliases.
    names={}
    for name,offset in [('CM4_J1',0),('CM4_J2',100)]:
        pins=[p for u in nodes(symbols[name],'symbol') for p in nodes(u,'pin')]
        flat=[(n,one(p,'name')[1]) for p in pins for n in expand(one(p,'number')[1])]
        assert len(flat)==100 and {n for n,_ in flat}==set(map(str,range(1,101)))
        names[name]=dict(flat)
        for n,actual in flat:
            expected=source[str(int(n)+offset)]['datasheet_name'].replace(' (Input)','').replace(' (Output)','')
            expected={'+5V':'VCC5V_CM4','CM4_3.3V':'CM4_3V3','CM4_1.8V':'CM4_1V8'}.get(expected,expected)
            assert actual==expected,(name,n,actual,expected)
    # Fixed physical anchors from CM4 datasheet pp18-20, independent of generator.
    for n,name in {'57':'SD_CLK','61':'SD_DAT3','62':'SD_CMD','63':'SD_DAT0',
        '67':'SD_DAT1','69':'SD_DAT2','73':'SD_VDD_OVERRIDE','75':'SD_PWR_ON',
        '76':'Reserved','78':'GPIO_VREF','84':'CM4_3V3','92':'RUN_PG',
        '93':'nRPIBOOT','99':'GLOBAL_EN','100':'nEXTRST'}.items():assert names['CM4_J1'][n]==name
    for n,name in {'1':'USB_OTG_ID','2':'PCIe_CLK_nREQ','3':'USB_N','4':'Reserved',
        '5':'USB_P','6':'Reserved','9':'PCIe_nRST','10':'PCIe_CLK_P','12':'PCIe_CLK_N',
        '16':'PCIe_RX_P','18':'PCIe_RX_N','22':'PCIe_TX_P','24':'PCIe_TX_N'}.items():assert names['CM4_J2'][n]==name
    fp=sx.loads((root/'lib/cm4.pretty/Hirose_DF40C-100DS-0.4V_2x50_P0.4mm.kicad_mod').read_text())
    pads=nodes(fp,'pad')
    assert len(pads)==100 and {p[1] for p in pads}==set(map(str,range(1,101)))
    # Hirose drawing 0001210104, 0.4 pitch, 19.6 end-to-end, 0.2 x 0.7 lands.
    for pad in pads:
        n=int(pad[1]);x=-9.8+((n-1)//2)*.4;y=1.54 if n%2 else -1.54
        assert max(abs(a-b) for a,b in zip(one(pad,'at')[1:3],[x,y]))<1e-6
        assert one(pad,'size')[1:3]==[.2,.7]
    with tempfile.TemporaryDirectory(prefix='cm4-core-check-') as temp:
        temp=Path(temp);xml=temp/'nets.xml';erc=temp/'erc.json'
        sch=root/'cad/cm4-carrier.kicad_sch'
        subprocess.run([KICAD,'sch','export','netlist','--format','kicadxml','-o',str(xml),str(sch)],check=True,stdout=subprocess.DEVNULL)
        tree=ET.parse(xml).getroot()
        nets={n.get('name'):{(p.get('ref'),p.get('pin')) for p in n} for n in tree.findall('.//nets/net')}
        pin_net={p:n for n,ps in nets.items() for p in ps}
        def exact(net,pins):assert nets[net]==set(pins),(net,nets[net],pins)
        for ref,sym in [('J100','CM4_J1'),('J101','CM4_J2')]:
            assert {p for r,p in pin_net if r==ref}==set(map(str,range(1,101)))
            for pin,name in names[sym].items():
                if name=='GND':assert pin_net[ref,pin]=='GND'
                elif name=='Reserved':assert nets[pin_net[ref,pin]]=={(ref,pin)}
        for n in [77,79,81,83,85,87]:assert pin_net['J100',str(n)]=='VCC5V_CM4'
        for n in [78,84,86]:assert pin_net['J100',str(n)]=='CM4_3V3'
        for n in [88,90]:assert pin_net['J100',str(n)]=='CM4_1V8'
        assert all(nets['VCC5V_CM4'].isdisjoint(nets[rail]) for rail in ['GND','CM4_3V3','CM4_1V8','SD_VDD'])
        for cm,sd,net in [(57,5,'SD_CLK'),(62,3,'SD_CMD'),(63,7,'SD_DAT0'),(67,8,'SD_DAT1'),(69,1,'SD_DAT2'),(61,2,'SD_DAT3')]:
            exact(net,[('J100',str(cm)),('J110',str(sd))])
        for n in [64,68,70,72,73]:assert nets[pin_net['J100',str(n)]]=={('J100',str(n))}
        exact('SD_VDD',[('U110','1'),('C111','1'),('J110','4')])
        exact('SD_PWR_ON',[('J100','75'),('U110','4'),('R110','2')])
        for p in [('U110','5'),('R110','1'),('C110','1')]:assert pin_net[p]=='CM4_3V3'
        for p in [('U110','2'),('C110','2'),('C111','2'),('J110','6'),('J110','SH')]:assert pin_net[p]=='GND'
        for i,(pin,net) in enumerate([(92,'CM4_RUN_PG'),(99,'CM4_GLOBAL_EN'),(93,'CM4_nRPIBOOT'),(20,'CM4_EEPROM_nWP')]):
            exact(net,[('J100',str(pin)),('R100','1') if i==0 else (f'SW{100+i}','1')])
            assert pin_net[f'SW{100+i}','2']=='GND'
        assert pin_net['SW100','1']==pin_net['R100','2']
        comps={c.get('ref'):c for c in tree.findall('.//components/comp')}
        for ref,mpn in [('J100','DF40C-100DS-0.4V(58)'),('J101','DF40C-100DS-0.4V(58)'),('J110','5033981892'),('U110','RT9742GGJ5'),('R100','0402WGF2200TCE'),('R110','0402WGF1002TCE')]:
            fields={f.get('name'):f.text for f in comps[ref].findall('fields/field')}
            assert fields['MPN']==mpn
        assert comps['R100'].findtext('value')=='220R 1%'
        for c in comps.values():
            fields={f.get('name'):f.text for f in c.findall('fields/field')}
            assert fields.get('MPN') and fields.get('Manufacturer') and fields.get('LCSC'),c.get('ref')
        subprocess.run([KICAD,'sch','erc','--format','json','-o',str(erc),str(sch)],check=True,stdout=subprocess.DEVNULL)
        report=json.loads(erc.read_text())
        counts=Counter(v['type'] for s in report['sheets'] for v in s['violations'])
        assert counts=={'isolated_pin_label':51,'pin_not_driven':3,'power_pin_not_driven':2},counts
        pending={'CM4_1V8','CM4_Pi_nLED_Activity','CM4_SCL0','CM4_SDA0','CM4_nEXTRST','ID_SC','ID_SD',
                 'PCIE_CLK_nREQ','PCIE_nRST','RECOVERY_USB_P','RECOVERY_USB_N'}
        pending|={f'GPIO{i}' for i in range(2,28)}
        pending|={f'ETH_MDI{i}_{p}' for i in range(4) for p in ['P','N']}
        pending|={f'PCIE_{signal}_{p}' for signal in ['CLK','TX','RX'] for p in ['P','N']}
        actual={v['items'][0]['description'] for s in report['sheets'] for v in s['violations'] if v['type']=='isolated_pin_label'}
        assert actual=={f"Global Label '{n}'" for n in pending},actual
        project=json.loads((root/'cad/cm4-carrier.kicad_pro').read_text())
        assert not project.get('erc',{}).get('erc_exclusions')
        result={'status':'CM4_CORE_CAPTURE_CHECKPOINT_NOT_RELEASE','cm4_contacts_checked':200,
                'physical_socket_quantity':2,'sd_data_connections':6,'physical_controls':4,
                'erc_unfinished_integration':dict(counts),'system_routed':False,
                'scope':'core capture only; PoE, auxiliary power, USB3, modem, GPIO and protection remain open'}
        if output:Path(output).write_text(json.dumps(result,indent=2)+'\n')
        print(json.dumps(result,indent=2))
        return result


if __name__=='__main__':check(sys.argv[1] if len(sys.argv)>1 else None,sys.argv[2] if len(sys.argv)>2 else None)
