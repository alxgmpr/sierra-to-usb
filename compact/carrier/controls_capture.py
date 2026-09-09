"""Hardware authorization, delayed modem startup and open-drain controls."""

def capture(c,ic,put,g,andg,invert):
    c.reset_sheet('controls')
    c.box('POWER / RUN CONTROLS — STOP RETAINS THE MODEM SUPPLY',15.24,15.24,558.8,101.6)
    for ref,x,net in [('SW501',50.8,'POWER_REQUEST'),('SW502',177.8,'RUN_REQUEST')]:
        c.place('Switch:SW_SPDT',ref,'JS102011SAQN',x,55.88,
            foot='Button_Switch_SMD:SW_SPDT_CK_JS102011SAQN',
            fields={'MPN':'JS102011SAQN','Manufacturer':'C&K',
                    'Datasheet':'https://www.ckswitches.com/media/1434/slides.pdf'})
        c.allpins(ref,{1:'AUX_3V3',2:net,3:'GND'})
    c.R('R501','100k',96.52,88.9,'POWER_REQUEST','GND')
    c.R('R502','100k',223.52,88.9,'RUN_REQUEST','GND')
    g(andg,'U501',335.28,55.88,'USB_3A_OK','PROFILE_OK','POWER_PERMIT','C501')
    g(andg,'U502',485.14,55.88,'POWER_PERMIT','POWER_REQUEST','BUCK_ENABLE','C502')
    c.text('POWER: enables VCC only with a valid profile and 3 A advertisement. RUN: starts modem after delays.\nNormal shutdown: use vendor procedure, set RUN off, wait for shutdown, then POWER off.\nLoss of source permission overrides manual controls and removes main power immediately.',30.48,99.06)

    supervisor=ic('TPS389033DSER',[(1,'SENSE','input','L'),(2,'GND','power_in','B'),
        (3,'MR_N','input','L'),(4,'VDD','power_in','T'),(5,'CT','passive','L'),
        (6,'RESET_N','open_collector','R')],
        'Package_SON:WSON-6_1.5x1.5mm_P0.5mm','https://www.ti.com/lit/ds/symlink/tps3890.pdf')
    c.box('RAIL QUALIFICATION / NO EXTERNAL LOGIC VOLTAGE DURING FIRST 100 ms',15.24,132.08,558.8,101.6)
    put(supervisor,'U503',88.9,177.8,{1:'MODEM_VCC',2:'GND',3:'BUCK_ENABLE',
        4:'AUX_3V3',5:'RAIL_DELAY_CT',6:'DRIVE_ALLOWED'})
    c.C('C503','330n / effective 214.5..429n',40.64,208.28,'RAIL_DELAY_CT','GND')
    c.C('C504','100n',160.02,208.28,'AUX_3V3','GND')
    c.R('R503','10k',195.58,165.1,'AUX_3V3','DRIVE_ALLOWED')
    ldo=ic('TPS7A2018PDBVR',[(1,'IN','power_in','T'),(2,'GND','power_in','B'),
        (3,'EN','input','L'),(4,'NC','no_connect','L'),(5,'OUT','power_out','R')],
        'Package_TO_SOT_SMD:SOT-23-5','https://www.ti.com/lit/ds/symlink/tps7a20.pdf')
    put(ldo,'U504',332.74,177.8,{1:'MODEM_VCC',2:'GND',3:'DRIVE_ALLOWED',4:None,5:'MODEM_CTRL_1V8'})
    c.C('C505','2.2u / 10V',269.24,208.28,'MODEM_VCC','GND')
    c.C('C506','2.2u / 10V',411.48,208.28,'MODEM_CTRL_1V8','GND')
    c.R('R504','100k',520.7,208.28,'MODEM_CTRL_1V8','GND')
    c.text('U503: 3.17 V nominal falling threshold; at least 185 ms rising delay for specified effective C503.\nSENSE/GND: Kelvin to output bank, upstream of socket contact drop. U504 supplies only Sierra straps and the FCPO pull-up.',215.9,142.24)

    c.box('RUN GUARD / USB ISOLATION / FCPO OPEN DRAIN',15.24,248.92,558.8,93.98)
    g(andg,'U505',66.04,284.48,'DRIVE_ALLOWED','RUN_REQUEST','RUN_PERMIT','C507')
    put(supervisor,'U506',213.36,284.48,{1:'MODEM_VCC',2:'GND',3:'RUN_PERMIT',
        4:'AUX_3V3',5:'RUN_DELAY_CT',6:'RUN_ALLOWED'})
    c.C('C508','2.2u / effective 1.43..2.86u',160.02,317.5,'RUN_DELAY_CT','GND')
    c.C('C509','100n',266.7,317.5,'AUX_3V3','GND')
    c.R('R505','10k',294.64,276.86,'AUX_3V3','RUN_ALLOWED')
    invert('U507',368.3,284.48,'RUN_ALLOWED','USB_MUX_OFF','C510')
    fet=ic('DMG1012T_7',[(1,'G','input','L'),(2,'S','passive','B'),(3,'D','passive','R')],
        'Package_TO_SOT_SMD:SOT-523','https://www.diodes.com/datasheet/download/DMG1012T.pdf')
    def transistor(ref,x,y,gate,drain):
        c.place(fet,ref,'DMG1012T-7',x,y,fields={'MPN':'DMG1012T-7','Manufacturer':'Diodes Incorporated'})
        c.allpins(ref,{1:gate,2:'GND',3:drain})
    transistor('Q501',492.76,284.48,'USB_MUX_OFF','FCPO_N')
    c.R('R506','10k',533.4,317.5,'MODEM_CTRL_1V8','FCPO_N')
    c.text('RUN rising delay >=1.239 s for specified effective C508; straps settle before FCPO and USB.\nRUN off asserts FCPO and isolates USB immediately. VCC remains until POWER off / detach / fault.',30.48,330.2)
    c.box('VENDOR SHUTDOWN RULES',15.24,355.6,558.8,43.18)
    c.text('RM520N-GL: send AT+CFUN=0 and wait for OK BEFORE RUN off; allow >=900 ms to finish.\nEM9190: RUN off after boot; wait until isolated PLA_S2# status goes low (up to 8 s) before POWER off.\nAbrupt unplug or authorization loss cannot guarantee graceful firmware shutdown. See sequencing-review.md.',30.48,368.3)
    controls=c.save_sheet('controls','Power and startup sequencing')

    c.reset_sheet('service')
    c.box('BOUNDED RESET / FALLING EDGE, NON-RETRIGGERING',15.24,15.24,558.8,172.72)
    timer=ic('LTC6993HS6_3_TRMPBF',[(1,'TRIG','input','L'),(2,'GND','power_in','B'),
        (3,'SET','passive','L'),(4,'DIV','input','L'),(5,'V+','power_in','T'),(6,'OUT','output','R')],
        'Package_TO_SOT_SMD:TSOT-23-6',
        'https://www.analog.com/media/en/technical-documentation/data-sheets/ltc6993-6993-1-6993-2-6993-3-6993-4.pdf')
    put(timer,'U508',299.72,86.36,{1:'RESET_BUTTON_N',2:'GND',3:'RESET_RSET',
        4:'RESET_DIV',5:'AUX_3V3',6:'RESET_PULSE'},'LTC6993HS6-3#TRMPBF')
    c.R('R507','95.3k / 0.1%',218.44,134.62,'RESET_RSET','GND')
    c.R('R508','1M / 1%',88.9,134.62,'AUX_3V3','RESET_DIV')
    c.R('R509','681k / 1%',154.94,134.62,'RESET_DIV','GND')
    c.C('C511','100n',365.76,134.62,'AUX_3V3','GND')
    c.R('R510','100k',40.64,68.58,'AUX_3V3','RESET_BUTTON_N')
    c.C('C512','100n',106.68,68.58,'RESET_BUTTON_N','GND')
    def button(ref,x,y,net):
        c.place('Switch:SW_Push',ref,'PTS636 SK25 SMTR LFS',x,y,
            foot='Button_Switch_SMD:SW_Tactile_SPST_NO_Straight_CK_PTS636Sx25SMTRLFS',
            fields={'MPN':'PTS636 SK25 SMTR LFS','Manufacturer':'C&K'})
        c.allpins(ref,{1:net,2:'GND'})
    button('SW503',172.72,68.58,'RESET_BUTTON_N')
    transistor('Q502',469.9,86.36,'RESET_PULSE','MODEM_RESET_N')
    c.R('R511','100k',528.32,134.62,'RESET_PULSE','GND')
    c.text('DIV code 6 / POL=0, N=262144; t = N x 95.3k / 50k x 1 us = 499.65 ms.\nA held button does not hold RESET low; output is open drain at the modem. No host reset pull-up.\nManual reset is a recovery control, not a normal power-off method.',30.48,160.02)
    c.box('RF DISABLE / PROFILE-ISOLATED SHUTDOWN STATUS',15.24,200.66,558.8,71.12)
    button('SW504',86.36,238.76,'RF_DISABLE_N')
    c.text('Hold RF DISABLE to ground module pin 8.\nNo carrier pull-up; module owns its voltage.',160.02,228.6)
    c.text('TP509 exposes Sierra PLA_S2# only through Sierra profile.\nQuectel pin 28 must remain disconnected at the profile assembly.',350.52,228.6)
    c.box('SERVICE TEST PADS / NOT EXTERNAL POWER INPUTS',15.24,284.48,558.8,114.3)
    for i,net in enumerate(['GND','USB_VBUS','SENSED_VBUS','AUX_3V3','MODEM_VCC',
            'INPUT_CURRENT_MON','BUCK_ITH','FCPO_N','SIERRA_PLA_STATUS','MODEM_RESET_N',
            'DRIVE_ALLOWED','RUN_ALLOWED','CC_ATTACH_N','USB_3A_OK','PROFILE_OK']):
        ref='TP'+str(501+i);x=43.18+(i%5)*109.22;y=299.72+(i//5)*25.4
        c.place('Connector:TestPoint',ref,net,x,y,foot='TestPoint:TestPoint_Pad_D1.0mm',
            fields={'MPN':'PCB_TEST_PAD','Manufacturer':'PCB','Status':'Copper test pad; no purchased component'})
        c.allpins(ref,{1:net})
    c.R('R512','10k',543.56,238.76,'AUX_3V3','CC_ATTACH_N')
    service=c.save_sheet('service','Reset, RF disable and service access')
    return controls,service
