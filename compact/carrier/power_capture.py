"""Power input capture; called inside the guarded hierarchy build."""


def capture(c, ic, put):
    c.reset_sheet('power')
    c.box('REVERSE BLOCKING / INRUSH / FAULT PROTECTION',15.24,15.24,558.8,111.76)
    fuse = ic('TPS259470LRPWR', [
        (5,'IN','power_in','T'),(6,'OUT','power_out','R'),
        (1,'EN_UVLO','input','L'),(2,'OVLO','input','L'),
        (7,'dVdt','output','R'),(9,'ILM','passive','L'),
        (10,'ITIMER','passive','L'),(4,'FLT_N','open_collector','R'),
        (3,'AUXOFF','open_collector','R'),(8,'GND','power_in','B')],
        'compact-usb:TI_RPW0010A','https://www.ti.com/lit/ds/symlink/tps25947.pdf')
    put(fuse,'U301',114.3,60.96,{5:'USB_VBUS',6:'PROTECTED_VBUS',
        1:'INPUT_UVLO',2:'INPUT_OVLO',7:'INPUT_SLEW',9:'FAULT_ILIM',
        10:None,4:'INPUT_FAULT_N',3:None,8:'GND'})
    for ref,val,x,a,b in [
        ('R301','200k',30.48,'USB_VBUS','INPUT_UVLO'),
        ('R302','100k',30.48,'INPUT_UVLO','GND'),
        ('R303','340k',210.82,'USB_VBUS','INPUT_OVLO'),
        ('R304','100k',210.82,'INPUT_OVLO','GND'),
        ('R305','1.02k',292.1,'FAULT_ILIM','GND'),
        ('R306','10k',368.3,'AUX_3V3','INPUT_FAULT_N')]:
        c.R(ref,val,x,55.88 if ref in ('R301','R303','R305','R306') else 86.36,a,b)
    c.C('C301','1u / 50V',444.5,55.88,'USB_VBUS','GND')
    c.R('R308','100R',523.24,55.88,'INPUT_SLEW','INPUT_SLEW_CAP')
    c.C('C302','100n',523.24,86.36,'INPUT_SLEW_CAP','GND')
    c.place('Device:D_TVS','D301','SMF6.0A',368.3,86.36,angle=90,
        foot='carrier:Littelfuse_SMF_SOD123FL',fields={'MPN':'SMF6.0A','Manufacturer':'Littelfuse',
        'Datasheet':'https://www.littelfuse.com/assetdocs/tvs-diodes-smf-datasheet?assetguid=7eb8a5b6-bdd0-4561-8f19-0c3cc6f9b2af'})
    c.allpins('D301',{1:'USB_VBUS',2:'GND'})
    c.text('Fault limit is above the normal input-current loop; it is not the 3 A authorization.\nITIMER open: minimum fault delay. 100 nF dVdt limits charging of downstream input capacitors.\nUVLO nominal 3.6 V; OVLO nominal 5.28 V. Dynamic overshoot remains a bench gate.',81.28,104.14)

    c.box('KELVIN INPUT SHUNT / ALWAYS-ON AUXILIARY SUPPLY',15.24,139.7,558.8,101.6)
    shunt=ic('CSM2512_KELVIN',[(1,'I1','passive','T'),(2,'I2','passive','B'),
        (3,'E1','passive','L'),(4,'E2','passive','R')],
        'carrier:VPG_CSM2512_Kelvin','https://vpgfoilresistors.com/products/current-sense-resistors/csm2512/datasheet')
    c.place(shunt,'R307','10m / 0.1%',71.12,185.42,fields={
        'MPN':'Y14870R01000B9R','Manufacturer':'VPG Foil Resistors',
        'Status':'Four-terminal Kelvin shunt; verify adapted land pattern during assembly review'})
    c.allpins('R307',{1:'PROTECTED_VBUS',2:'SENSED_VBUS',3:'INPUT_SENSE_P',4:'INPUT_SENSE_N'})
    ldo=ic('TPS7A2033PDBVR',[(1,'IN','power_in','T'),(2,'GND','power_in','B'),
        (3,'EN','input','L'),(4,'NC','no_connect','L'),(5,'OUT','power_out','R')],
        'Package_TO_SOT_SMD:SOT-23-5','https://www.ti.com/lit/ds/symlink/tps7a20.pdf')
    put(ldo,'U302',185.42,180.34,{1:'SENSED_VBUS',2:'GND',3:'SENSED_VBUS',4:None,5:'AUX_3V3'})
    c.C('C303','2.2u / 10V',266.7,177.8,'SENSED_VBUS','GND')
    c.C('C304','2.2u / 10V',347.98,177.8,'AUX_3V3','GND')
    ina=ic('INA190A1IDCKR',[(1,'REF','input','L'),(2,'GND','power_in','B'),
        (3,'VS','power_in','T'),(4,'IN+','input','L'),(5,'IN-','input','L'),(6,'OUT','output','R')],
        'Package_TO_SOT_SMD:SOT-363_SC-70-6','https://www.ti.com/lit/ds/symlink/ina190.pdf')
    put(ina,'U303',459.74,180.34,{1:'GND',2:'GND',3:'AUX_3V3',
        4:'INPUT_SENSE_P',5:'INPUT_SENSE_N',6:'INPUT_CURRENT_MON'})
    c.C('C305','100n',535.94,215.9,'AUX_3V3','GND')
    c.text('25 V/V x 10 milliohm = 0.25 V/A. Route E1/E2 as separate Kelvin sense traces; never join them to force copper.\nAll main buck and auxiliary loads must be downstream of R307; budget upstream CC/eFuse separately.',30.48,220.98)

    c.box('POWER-SOURCE ANNOTATIONS / PHYSICAL PATHS',15.24,254,558.8,137.16)
    for i,net in enumerate(['USB_VBUS','GND','SENSED_VBUS','MODEM_VCC']):
        ref='#FLG'+str(301+i)
        c.place('power:PWR_FLAG',ref,'PWR_FLAG',63.5+i*129.54,294.64)
        c.allpins(ref,{1:net})
    c.text('USB_VBUS and GND enter through J101. SENSED_VBUS is fed through U301 and passive R307.\nMODEM_VCC is fed from U401 through passive L401. These flags describe real supply paths;\nthey do not validate regulation, source current or an external supply connected to a test point.\n\nThe regulator sheet captures the direct buck and precision input-current feedback.\nThe controls sheet implements USB_3A_OK AND PROFILE_OK AND POWER_REQUEST.\nRemaining power-budget and loop verification gates are recorded in REVIEW.md.',30.48,320.04,1.6)
    c.local_path('INPUT_UVLO',('R301',2),('R302',1))
    c.local_path('INPUT_OVLO',('R303',2),('R304',1))
    c.local_path('INPUT_SLEW_CAP',('R308',2),('C302',1))
    return c.save_sheet('power','Input protection and current measurement')
