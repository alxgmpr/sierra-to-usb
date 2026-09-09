"""Direct buck and analog input-current override, under engineering review."""


def capture(c,ic,put):
    c.reset_sheet('regulator')
    c.box('DIRECT BUCK / 3 A DC DESIGN LOAD / LOCAL TRANSIENT STORAGE',15.24,15.24,558.8,157.48)
    pins=[(1,'EN','input','L'),(2,'AGND','power_in','B')]
    pins += [(n,'VIN','power_in','T') for n in (3,4,11,12)]
    pins += [(n,'PGND','power_in','B') for n in (5,10,19)]
    pins += [(n,'SW','power_out' if n==6 else 'passive','R') for n in (6,7,8,9)]
    pins += [(13,'MODE_SYNC','input','L'),(14,'PGOOD','open_collector','R'),
             (15,'RT','passive','L'),(16,'SSTT','passive','L'),
             (17,'ITH','passive','L'),(18,'FB','input','L')]
    buck=ic('LTC3310SIV_PBF',pins,'carrier:LTC_LQFN18_3x3_05-08-1548',
        'https://www.analog.com/media/en/technical-documentation/data-sheets/ltc3310s-3310s-1-3310-3310-1.pdf')
    nets={1:'BUCK_ENABLE',2:'GND',13:'GND',14:'BUCK_PG',15:'SENSED_VBUS',
          16:'BUCK_SS',17:'BUCK_ITH',18:'BUCK_FB'}
    nets.update({n:'SENSED_VBUS' for n in (3,4,11,12)})
    nets.update({n:'GND' for n in (5,10,19)})
    nets.update({n:'BUCK_SW' for n in (6,7,8,9)})
    put(buck,'U401',116.84,78.74,nets,'LTC3310SIV#PBF')
    c.passive('L','L401','0.47u / XEL4030-471MEC',223.52,78.74,'BUCK_SW','MODEM_VCC',
        'carrier:L_Coilcraft_XEL4030',{'MPN':'XEL4030-471MEC','Manufacturer':'Coilcraft'})
    for ref,x,net in [('C401',45.72,'SENSED_VBUS'),('C402',86.36,'SENSED_VBUS'),
                       ('C403',368.3,'MODEM_VCC'),('C404',444.5,'MODEM_VCC')]:
        c.C(ref,'22u / 10V',x,99.06,net,'GND')
    c.text('RT=VIN: 2 MHz. MODE=GND: pulse skipping; no forced reverse inductor current at light load.\nAll SW pins join before L401. Split input ceramics symmetrically across VIN/PGND pairs.\nCapacitors supply load-step deficit while the live source continues delivering power.\nExact BOM captured; effective capacitance, losses and both control loops require bench qualification.',30.48,142.24)

    c.box('VOLTAGE FEEDBACK / SOFT START / COMPENSATION',15.24,175.26,558.8,99.06)
    for ref,val,x,y,a,b in [
        ('R401','56.2k / 0.1% / 10ppm',43.18,205.74,'MODEM_VCC','BUCK_FB_TOP'),
        ('R411','402R / 0.1% / 25ppm',43.18,228.6,'BUCK_FB_TOP','BUCK_FB'),
        ('R402','10k / 0.1% / 10ppm',43.18,254,'BUCK_FB','GND'),
        ('R403','100k',299.72,213.36,'BUCK_ITH','BUCK_COMP'),
        ('R404','10k',444.5,220.98,'AUX_3V3','BUCK_PG'),
        ('R405','100k',523.24,220.98,'BUCK_ENABLE','GND'),
        ('R410','330R / 1%',444.5,254,'MODEM_VCC','GND')]:
        c.R(ref,val,x,y,a,b)
    c.C('C407','15p C0G',215.9,220.98,'MODEM_VCC','BUCK_FB')
    c.C('C408','4.7n C0G',299.72,248.92,'BUCK_COMP','GND')
    c.C('C409','15p C0G',375.92,220.98,'BUCK_ITH','GND')
    c.C('C410','1u',523.24,254,'BUCK_SS','GND')

    c.box('ANALOG INPUT-CURRENT OVERRIDE / NO FIRMWARE DEPENDENCY',15.24,287.02,558.8,109.22)
    ref=ic('REF3312AIDBZR',[(1,'IN','power_in','T'),(2,'OUT','output','R'),(3,'GND','power_in','B')],
        'Package_TO_SOT_SMD:SOT-23','https://www.ti.com/lit/ds/symlink/ref33.pdf')
    put(ref,'U402',63.5,330.2,{1:'AUX_3V3',2:'CURRENT_REF_1V25',3:'GND'},'REF3312AIDBZT')
    c.C('C411','1u',33.02,370.84,'AUX_3V3','GND')
    c.C('C412','1u',96.52,370.84,'CURRENT_REF_1V25','GND')
    c.R('R406','41.2k / 0.1%',157.48,322.58,'CURRENT_REF_1V25','CURRENT_SET')
    c.R('R407','56.2k / 0.1%',157.48,365.76,'CURRENT_SET','GND')
    amp=ic('TLV333IDBVR',[(1,'OUT','output','R'),(2,'V-','power_in','B'),
        (3,'IN+','input','L'),(4,'IN-','input','L'),(5,'V+','power_in','T')],
        'Package_TO_SOT_SMD:SOT-23-5','https://www.ti.com/lit/ds/symlink/tlv333.pdf')
    put(amp,'U403',317.5,332.74,{1:'CURRENT_AMP_OUT',2:'GND',3:'CURRENT_SET',
        4:'CURRENT_ERROR',5:'AUX_3V3'})
    c.R('R408','10k',236.22,370.84,'INPUT_CURRENT_MON','CURRENT_ERROR')
    c.C('C413','22n',363.22,373.38,'CURRENT_AMP_OUT','CURRENT_ERROR')
    c.R('R409','100R',406.4,325.12,'CURRENT_AMP_OUT','CURRENT_CLAMP')
    for name,ref,x,y,k,a in [
        ('D_Schottky','D401',469.9,322.58,'CURRENT_CLAMP','BUCK_ITH'),
        ('D_Schottky','D402',469.9,363.22,'CURRENT_ERROR','CURRENT_AMP_OUT')]:
        c.place('Device:'+name,ref,'BAT54WS-7-F',x,y,angle=90,
            foot='Diode_SMD:D_SOD-323',fields={'MPN':'BAT54WS-7-F','Manufacturer':'Diodes Incorporated'})
        c.allpins(ref,{1:k,2:a})
    c.C('C414','100n',541.02,350.52,'AUX_3V3','GND')
    c.text('D401 can only reduce ITH. D402 limits positive integrator windup.\nNominal current setpoint: 1.25 x 56.2 / 97.4 / 0.25 = 2.885 A.\nThis new dual-loop implementation requires stability and transient verification.',213.36,386.08)
    sw=c.placed['U401']['6'];lp=c.placed['L401']['1']
    c.local_path('BUCK_SW',('U401',6),('L401',1),[(175.26,sw[1]),(175.26,lp[1])])
    c.local_path('SENSED_VBUS',('C401',1),('C402',1))
    c.local_path('GND',('C401',2),('C402',2))
    c.local_path('MODEM_VCC',('L401',2),('C403',1),[(368.3,78.74)])
    c.local_path('MODEM_VCC',('C403',1),('C404',1))
    c.local_path('GND',('C403',2),('C404',2))
    c.local_path('BUCK_FB_TOP',('R401',2),('R411',1))
    c.local_path('BUCK_FB',('R411',2),('R402',1))
    c.local_path('BUCK_COMP',('R403',2),('C408',1))
    c.local_path('CURRENT_SET',('R406',2),('R407',1))
    return c.save_sheet('regulator','3.33 V regulator and input-current limit')
