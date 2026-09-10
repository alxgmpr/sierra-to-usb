"""Physical modem contacts; conditional pins are checked by assembly profile.

Pin names describe the module side. No generic PCIe M.2 pinout is substituted
for the three manufacturers' exact modem tables.
"""
from collections import OrderedDict
import sexpdata as sx


COMMON_VCC = [2, 4, 70, 72, 74]
GROUNDS = [3, 5, 11, 27, 33, 39, 45, 51, 57, 71, 73]


def build(make_symbol):
    symbols, manifest = [], {}

    def add(name, fp, url, maker, lcsc, groups, ref='U'):
        units=OrderedDict((title,[dict(ball=str(n),name=label,display_name=label,type=typ,side=side)
            for n,label,typ,side in pins]) for title,pins in groups.items())
        if name=='MODEM_M2_B':
            pins=next(iter(units.values()))
            head=pins[0];head['ball']='[2,4,70,72,74]';head['physical_pins']=list(map(str,COMMON_VCC))
            pins[:]=[p for p in pins if p is head or p['ball'] not in set(map(str,COMMON_VCC))]
        sym,meta=make_symbol(name,fp,url,maker,lcsc,name,units,
            keywords='CM4 modem SIM profile',footprint_filter=fp.split(':')[-1],side_pins_from_top=True)
        sym=sym.replace('(property "Reference" "U"',f'(property "Reference" "{ref}"')
        if name=='MODEM_M2_B':
            sym=sym.replace('(property "MPN" "MODEM_M2_B"','(property "MPN" "MDT420B01411"')
        p=sx.loads(sym)
        for unit in [v for v in p if isinstance(v,list) and str(v[0])=='symbol']:
            unit[:]=[v for v in unit if not(isinstance(v,list) and str(v[0])=='text')]
        symbols.append(sx.dumps(p));manifest[name]=meta

    add('MODEM_M2_B','cm4:Amphenol_MDT420B01411',
        'https://cdn.amphenol-cs.com/media/wysiwyg/files/drawing/cmdt420x0x411.pdf',
        'Amphenol ICC','',{
        'Power / profile-dependent contacts':[
            *[(n,'VCC_MODEM','power_in','L') for n in COMMON_VCC],
            *[(n,'GND','power_in','B') for n in GROUNDS],
            ('SH','Board locks / GND','passive','B'),
            (24,'P24 / VCC or 1V8_OUT','passive','R'),
            (38,'P38 / VCC or WLAN_IN','passive','R'),
            (68,'P68 / VCC or reserved','passive','R')],
        'USB3 / USB2 / Sierra interface selection':[
            (7,'USB_D+','passive','L'),(9,'USB_D-','passive','L'),
            (29,'USB3_TX-','passive','R'),(31,'USB3_TX+','passive','R'),
            (35,'USB3_RX-','passive','L'),(37,'USB3_RX+','passive','L'),
            (20,'P20 / PCIE_DIS or reserved','passive','L'),
            (22,'P22 / VBUS_SENSE or reserved','passive','L')],
        'Power, reset, radio and status':[
            (6,'FULL_CARD_POWER_OFF_N','input','L'),(8,'W_DISABLE_N','passive','L'),
            (26,'GPS_DISABLE_N','passive','L'),(67,'RESET_N','passive','L'),
            (25,'DPR / optional','passive','L'),(10,'WWAN_LED_N','open_collector','R'),
            (23,'WAKE_ON_WAN_N','open_collector','R'),(28,'P28 / PLA_N or reserved','passive','R')],
        'Common SIM1':[(30,'SIM1_RST','output','R'),(32,'SIM1_CLK','output','R'),
            (34,'SIM1_DATA','bidirectional','R'),(36,'SIM1_PWR','power_out','R'),
            (66,'SIM1_DET','passive','L')],
        'SIM2 / EM9190 mmWave outputs':[
            (40,'P40 / SIM2_DET or QTM0','passive','L'),
            (42,'P42 / SIM2_DATA or QTM1','bidirectional','R'),
            (44,'P44 / SIM2_CLK or QTM2','output','R'),
            (46,'P46 / SIM2_RST or QTM3','output','R'),
            (48,'P48 / SIM2_PWR or QTM_IO','power_out','R')],
        'Unused PCIe / reserved contacts':[(n,label,'passive','L') for n,label in [
            (1,'CONFIG3'),(21,'CONFIG0'),(69,'CONFIG1'),(75,'CONFIG2'),
            (41,'PCIE_TX-'),(43,'PCIE_TX+'),(47,'PCIE_RX-'),(49,'PCIE_RX+'),
            (50,'PCIE_PERST_N'),(52,'PCIE_CLKREQ_N'),(53,'PCIE_REFCLK-'),
            (54,'PCIE_WAKE_N'),(55,'PCIE_REFCLK+'),(56,'P56'),(58,'P58'),
            (59,'P59'),(60,'P60'),(61,'P61'),(62,'P62'),(63,'P63'),(64,'P64'),(65,'P65')]]},ref='J')
    add('SMN-303-ARP7','cm4:Xunpu_SMN303_ARP7',
        'https://wmsc.lcsc.com/wmsc/upload/file/pdf/v2/lcsc/2208151601_XUNPU-SMN-303-ARP7_C5137194.pdf',
        'XUNPU','C5137194',{'Nano-SIM / normally closed detection':[
            ('C1','VCC','power_in','T'),('C2','RST','input','L'),('C3','CLK','input','L'),
            ('C7','I/O','bidirectional','L'),('CD','DET / NC switch','passive','R'),
            ('C6','VPP / NC','passive','R'),('C5','GND','power_in','B'),
            ('SH','Shield / detect GND','passive','B')]},ref='J')
    add('TPD1E05U06DPYR','cm4:TI_DPY0002_TPD1E05U06',
        'https://www.ti.com/lit/ds/symlink/tpd1e05u06.pdf','Texas Instruments','C436349',{
        'SIM supply ESD':[(1,'IO','passive','T'),(2,'GND','passive','B')]},ref='D')
    return symbols,manifest
