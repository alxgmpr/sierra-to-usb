"""RTL8125BG exact external-regulator variant library definition."""
from collections import OrderedDict


def ethernet_symbol():
    from build_core_symbols import make_symbol
    groups=OrderedDict()
    groups['Supplies']=[(4,'NC','no_connect'),(5,'NC','no_connect'),(7,'NC','no_connect'),(8,'DVDD09','power_in'),(11,'AVDD09','power_in'),(15,'AVDD33','power_in'),(16,'AVDD09','power_in'),(19,'AVDD33','power_in'),(22,'AVDD09','power_in'),(28,'DVDD09','power_in'),(29,'DVDD33','power_in'),(33,'AVDD33','power_in'),(34,'AVDD33_XTAL','power_in'),(37,'EVDD09','power_in'),(40,'GND','power_in'),(43,'EVDD33','power_in'),(46,'DVDD33','power_in'),(47,'DVDD09','power_in'),(49,'GND','power_in')]
    groups['PCIe Gen2 x1']=[(1,'ISOLATEB','input'),(2,'LANWAKEB','open_collector'),(36,'PERSTB','input'),(38,'HSOP','output'),(39,'HSON','output'),(41,'HSIP','input'),(42,'HSIN','input'),(44,'REFCLK_P','input'),(45,'REFCLK_N','input'),(48,'CLKREQB','bidirectional')]
    groups['2.5GbE MDI']=[(12,'RSET','input'),(13,'MDIP0','bidirectional'),(14,'MDIN0','bidirectional'),(17,'MDIP1','bidirectional'),(18,'MDIN1','bidirectional'),(20,'MDIP2','bidirectional'),(21,'MDIN2','bidirectional'),(23,'MDIP3','bidirectional'),(24,'MDIN3','bidirectional')]
    groups['Clock and configuration']=[(3,'GPI','bidirectional'),(6,'POW_EXT_SWR','output'),(9,'CKXTAL2','output'),(10,'CKXTAL1','input'),(25,'LED2/EEDO/SPISO','bidirectional'),(26,'SPICSB','output'),(27,'LED1/EESK/SPISCK','bidirectional'),(30,'LED0/EEDI/SPISI/SDA','bidirectional'),(31,'EECS/SCL','output'),(32,'EEPROM_SEL/PPS_PIN','bidirectional'),(35,'LED3','output')]
    units=OrderedDict()
    for title,items in groups.items():
        units[title]=[dict(ball=str(n),name=name,display_name=name,type=t,side='B' if name=='GND' else 'R' if t in ['power_in','output','open_collector'] or title=='2.5GbE MDI' else 'L',pitch_mm=5.08,visible_nc=True) for n,name,t in items]
    return make_symbol('RTL8125BG-CG','full-adapter:Realtek_RTL8125BG_QFN48_EP4.3',
        'https://atta.szlcsc.com/upload/public/pdf/source/20220512/84CEBB847F37F5F3AD7D5F5F4E80AB39.pdf',
        'Realtek','C3013605','PCIe Gen2 x1 2.5GbE controller; external 0.95V regulator required',units,
        keywords='Ethernet PCIe 2.5GbE',footprint_filter='Realtek?RTL8125BG*',side_pins_from_top=True)
