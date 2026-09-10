"""Power-input pin maps, transcribed from the cited manufacturer datasheets."""
from collections import OrderedDict
import sexpdata as sx


def build(make_symbol):
    symbols, manifest = [], {}
    def add(name, fp, url, maker, lcsc, groups, ref='U'):
        units=OrderedDict((title,[dict(ball=str(n),name=label,display_name=label,type=typ,side=side)
              for n,label,typ,side in pins]) for title,pins in groups.items())
        if name=='TPS2121RUXR':
            pins=next(iter(units.values()))
            out=next(p for p in pins if p['ball']=='1')
            out['ball']='[1,8]';out['physical_pins']=['1','8']
            pins[:]=[p for p in pins if p['ball']!='8']
        symbol,meta=make_symbol(name,fp,url,maker,lcsc,name,units,
            keywords='CM4 carrier power input',footprint_filter=fp.split(':')[-1],side_pins_from_top=True)
        symbol=symbol.replace('(property "Reference" "U"',f'(property "Reference" "{ref}"')
        parsed=sx.loads(symbol)
        for unit in [p for p in parsed if isinstance(p,list) and str(p[0])=='symbol']:
            unit[:]=[p for p in unit if not (isinstance(p,list) and str(p[0])=='text')]
        symbol=sx.dumps(parsed)
        symbols.append(symbol);manifest[name]=meta
    add('HUSB238_002DD','cm4:Hynetek_DFN10_3x3_P0.5_EP1.8x2.5',
        'https://www.hynetek.com/uploadfiles/site/219/news/c16af076-8c40-4e8d-b126-b4f9b83e86ea.pdf',
        'Hynetek','C7471904',{'20 V / 3 A PD sink':[
            (1,'VIN','power_in','T'),(2,'D+','passive','L'),(3,'D-','passive','L'),
            (4,'CC1','passive','L'),(5,'CC2','passive','L'),(6,'SDA','bidirectional','R'),
            (7,'SCL','input','R'),(8,'VSET','passive','R'),(9,'ISET','passive','R'),
            (10,'GATE','open_collector','R'),(11,'GND','power_in','B')]})
    add('TPD6S300RUKR','cm4:TI_RUK0020_TPD6S300',
        'https://www.ti.com/lit/ds/symlink/tpd6s300.pdf','Texas Instruments','C2649810',{
            'CC protection / dead battery':[(4,'C_CC1','passive','L'),(7,'RPD_G1','passive','L'),
                (5,'C_CC2','passive','L'),(6,'RPD_G2','passive','L'),
                (12,'CC1','passive','R'),(11,'CC2','passive','R'),(9,'~{FLT}','open_collector','R'),
                (10,'VPWR','power_in','T'),(3,'VBIAS','passive','T'),
                *[(n,'GND','power_in','B') for n in [8,13,18,21]]],
            'Unused channels / ground':[(n,label,'passive','L') for n,label in [
                (1,'C_SBU1'),(2,'C_SBU2'),(15,'SBU1'),(14,'SBU2'),
                (19,'D2'),(20,'D1'),(16,'NC / GND'),(17,'NC / GND')]]})
    add('TLV70433DBVR','Package_TO_SOT_SMD:SOT-23-5',
        'https://www.ti.com/lit/ds/symlink/tlv704.pdf','Texas Instruments','C94917',{
            'Auxiliary housekeeping 3.3 V':[(2,'IN','power_in','L'),(3,'OUT','power_out','R'),
                (1,'GND','power_in','B'),(4,'NC','passive','R'),(5,'NC','passive','R')]})
    add('TPS3700DDCR','Package_TO_SOT_SMD:TSOT-23-6',
        'https://www.ti.com/lit/ds/symlink/tps3700.pdf','Texas Instruments','C33002',{
            'USB-C voltage window':[(3,'INA+','input','L'),(4,'INB-','input','L'),
                (1,'OUTA','open_collector','R'),(6,'OUTB','open_collector','R'),
                (5,'VDD','power_in','T'),(2,'GND','power_in','B')]})
    add('SN74LVC1G14DBVR','Package_TO_SOT_SMD:SOT-23-5',
        'https://www.ti.com/lit/ds/symlink/sn74lvc1g14.pdf','Texas Instruments','C7835',{
            'Schmitt fault inverter':[(2,'A','input','L'),(4,'~{Y}','output','R'),
                (5,'VCC','power_in','T'),(3,'GND','power_in','B'),(1,'NC','passive','R')]})
    add('TPS2121RUXR','cm4:TI_RUX0012_TPS2121',
        'https://www.ti.com/lit/ds/symlink/tps2121.pdf','Texas Instruments','C485916',{
            'Power mux / reverse blocking':[(7,'IN1','power_in','L'),(2,'IN2','power_in','L'),
                # Datasheet explicitly directs grounding unused ST. Its passive
                # type here describes that selected configuration, not a driver.
                (1,'OUT','power_out','R'),(8,'OUT','power_out','R'),(9,'ST / unused=GND','passive','R'),
                (6,'PR1','input','L'),(3,'CP2','input','L'),(5,'OV1','input','L'),(4,'OV2','input','L'),
                (10,'ILIM','passive','R'),(11,'SS','passive','R'),(12,'GND','power_in','B')]})
    pins=[]
    for n in ['A4','A9','B4','B9']:pins.append((n,'VBUS','passive','T'))
    for n,label in [('A5','CC1'),('B5','CC2'),('A6','D+'),('B6','D+'),('A7','D-'),('B7','D-'),('A8','SBU1'),('B8','SBU2')]:
        pins.append((n,label,'passive','R'))
    for n in ['A1','A12','B1','B12','SH']:pins.append((n,'GND / shell','passive','B'))
    add('USB4105-GF-A-120','cm4:GCT_USB4105_GF_A_120','https://gct.co/files/drawings/usb4105.pdf',
        'Global Connector Technology','C5184243',{'USB-C auxiliary power':pins},ref='J')
    return symbols,manifest
