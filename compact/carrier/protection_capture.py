"""USB isolation, connector ESD, module-powered SIM and programming access."""


def capture(c,ic,put):
    c.reset_sheet('protection')
    c.box('USB2 ISOLATION / BOTH DATA SWITCHES DISABLED DURING OFF STATE',15.24,15.24,558.8,91.44)
    sw=ic('TS3USB221ARSER',[(1,'1D+','bidirectional','R'),(2,'1D-','bidirectional','R'),
        (3,'2D+','bidirectional','R'),(4,'2D-','bidirectional','R'),(5,'GND','power_in','B'),
        (6,'OE_N','input','L'),(7,'D-','bidirectional','L'),(8,'D+','bidirectional','L'),
        (9,'S','input','L'),(10,'VCC','power_in','T')],
        'Package_DFN_QFN:Texas_UQFN-10_1.5x2mm_P0.5mm',
        'https://www.ti.com/lit/ds/symlink/ts3usb221a.pdf')
    put(sw,'U105',104.14,60.96,{1:'MOD_USB_D_P',2:'MOD_USB_D_N',3:None,4:None,5:'GND',
        6:'USB_MUX_OFF',7:'USB_D_N',8:'USB_D_P',9:'GND',10:'AUX_3V3'})
    c.C('C108','100n',215.9,60.96,'AUX_3V3','GND')
    c.R('R106','10k',292.1,60.96,'AUX_3V3','USB_MUX_OFF')
    c.text('S=0 selects 1D pair; OE_N=1 isolates host and modem.\nPower-off leakage specified by TI: +/-2 uA with VCC=0.\nUSB3 uses the same USB_MUX_OFF command.\nValidate detach, brownout and asymmetric rail collapse on hardware.',353.06,43.18)

    c.box('CONNECTOR-SIDE ESD / PLACE BEFORE USB SWITCHES',15.24,119.38,558.8,114.3)
    def esd(part,ref,x,nets):
        pinlist=[(1,'D1+','passive','L'),(2,'D1-','passive','L'),(3,'GND','passive','B'),
                 (4,'D2+','passive','L'),(5,'D2-','passive','L'),(8,'GND','passive','B')]
        pinlist += [(n,'NC','no_connect','R') for n in (6,7,9,10)]
        symbol=ic(part,pinlist,'Package_SON:USON-10_2.5x1.0mm_P0.5mm',
                  'https://www.ti.com/lit/ds/symlink/'+('tpd4eusb30' if 'USB30' in part else 'tpd4e05u06')+'.pdf')
        put(symbol,ref,x,165.1,{1:nets[0],2:nets[1],3:'GND',4:nets[2],5:nets[3],8:'GND',
                              6:None,7:None,9:None,10:None})
    esd('TPD4EUSB30DQAR','D101',111.76,['C_TX1_P','C_TX1_N','C_RX1_P','C_RX1_N'])
    esd('TPD4EUSB30DQAR','D102',299.72,['C_TX2_P','C_TX2_N','C_RX2_P','C_RX2_N'])
    esd('TPD4E05U06DQAR','D103',487.68,['CC1','CC2','USB_D_P','USB_D_N'])
    c.text('Each SS pair uses matched channels. Shield and ESD returns need a short ground path.\nNC pads are left electrically unconnected in this capture. Route protected pads without branch stubs.\nChannel/connector insertion loss and system ESD performance require qualification.',30.48,205.74)

    c.box('SIM PROTECTION / MODULE-SUPPLIED VOLTAGE ONLY',15.24,246.38,558.8,68.58)
    # Same numeric DQA pin map as the connector-side array above.
    symbol='carrier-parts:TPD4E05U06DQAR'
    put(symbol,'D203',99.06,284.48,{1:'SIM_VDD',2:'SIM_SOCKET_RST',3:'GND',
        4:'SIM_SOCKET_CLK',5:'SIM_SOCKET_DATA',8:'GND',6:None,7:None,9:None,10:None})
    for ref,x,net in [('C205',231.14,'SIM_SOCKET_RST'),('C206',337.82,'SIM_SOCKET_CLK'),
                      ('C207',444.5,'SIM_SOCKET_DATA')]:
        c.C(ref,'10p C0G',x,284.48,net,'GND')

    c.box('EXTERNAL CC NVM PROGRAMMING / TEST ACCESS',15.24,327.66,558.8,58.42)
    c.place('Connector_Generic:Conn_01x04','J102','I2C PROGRAM / USB POWERED',99.06,360.68,
        foot='Connector_PinHeader_2.54mm:PinHeader_1x04_P2.54mm_Vertical',
        fields={'MPN':'TSW-104-07-G-S','Manufacturer':'Samtec'})
    c.allpins('J102',{1:'GND',2:'AUX_3V3',3:'CC_SCL',4:'CC_SDA'})
    c.R('R107','4.7k',241.3,358.14,'AUX_3V3','CC_SCL')
    c.R('R108','4.7k',330.2,358.14,'AUX_3V3','CC_SDA')
    c.text('Pin 2 is target-voltage reference, not programmer power input.\nUse 3.3 V open-drain I2C with USB supplying the target.\nProgram DEBUG GPIO configuration; read back before enabling modem.',396.24,350.52)
    return c.save_sheet('protection','USB and SIM protection, USB2 isolation and CC programming')
