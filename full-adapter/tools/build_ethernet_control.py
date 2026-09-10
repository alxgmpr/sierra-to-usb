"""PCIe M1 controls, partial-power isolation and qualified startup reset delay."""
from collections import OrderedDict
import json
from schematic import ROOT, Sheet
from build_core_symbols import make_symbol
from build_emmc import cap, resistor
from build_recovery import props
from build_ethernet_controller import finish


def control_symbol():
    pins=[('1','VCCA','power_in','T'),('2','A0','bidirectional','L'),
          ('3','A1','bidirectional','L'),('4','GND','power_in','B'),
          ('5','OE','input','L'),('7','B0','bidirectional','R'),
          ('6','B1','bidirectional','R'),('8','VCCB','power_in','T')]
    return make_symbol('FXMA2102L8X','full-adapter:Onsemi_FXMA2102_523AY',
        'https://www.onsemi.com/pdf/datasheet/fxma2102-d.pdf','onsemi','C107408',
        'Dual bidirectional open-drain translator, independent supply order',
        OrderedDict([('PCIe open-drain control translator',[dict(ball=b,name=n,type=t,side=s,pitch_mm=5.08) for b,n,t,s in pins])]),
        keywords='open drain translator isolation',footprint_filter='Onsemi?FXMA2102*')


def reset_buffer_symbol():
    pins=[('1','NC','no_connect','L'),('2','A','input','L'),('3','GND','power_in','B'),
          ('4','Y','open_collector','R'),('5','VCC','power_in','T')]
    return make_symbol('SN74LVC1G07DCKR','full-adapter:TI_DCK0005A',
        'https://www.ti.com/lit/ds/symlink/sn74lvc1g07.pdf','Texas Instruments','C7830',
        'Noninverting open-drain buffer, 5.5V tolerant input, partial-power isolation',
        OrderedDict([('Reset buffer',[dict(ball=b,name=n,type=t,side=s,pitch_mm=5.08,visible_nc=True) for b,n,t,s in pins])]),
        keywords='open drain buffer reset',footprint_filter='TI?DCK0005A*')


def supervisor_symbol():
    pins=[('1','~{RESET}','open_collector','R'),('2','GND','power_in','B'),
          ('3','~{MR}','input','L'),('4','CT','passive','L'),
          ('5','SENSE','input','L'),('6','VDD','power_in','T')]
    return make_symbol('TPS3808G33DBVR','full-adapter:TI_DBV0006A',
        'https://www.ti.com/lit/ds/symlink/tps3808.pdf','Texas Instruments','C43698',
        '3.07V supervisor with manual reset and selectable reset delay',
        OrderedDict([('Ethernet reset supervisor',[dict(ball=b,name=n,type=t,side=s,pitch_mm=5.08) for b,n,t,s in pins])]),
        keywords='supervisor reset delay',footprint_filter='TI?DBV0006A*')


def ethernet_control():
    s=Sheet('ethernet-control','PCIe M1 controls and supply isolation')
    s.box('VCCIO5 — functional PCIe M1 group',10.16,15.24,170.18,172.72)
    u=s.place('full-adapter:RK3568B2','U1',55.88,96.52,unit=31)
    props(s,55.88,43.18)
    used={'AD1':'SOC_PCIE_PERST_N','AD7':'SOC_PCIE_WAKE_N','AG6':'SOC_PCIE_CLKREQ_N'}
    for pin in u:s.connect('U1',pin,used.get(pin),12.7,global_net=pin in used)
    s.text('AD1: PERSTn M1 / GPIO3_C1\nAD7: WAKEn M1 / GPIO2_D1\nAG6: CLKREQn M1 / GPIO2_D0\nAll three pads use VCC3V3_S0.\nOther VCCIO5 functions are unused.',17.78,152.4,1.05)
    s.box('Bidirectional open-drain bridge — either rail may power first',187.96,15.24,218.44,172.72)
    u=s.place('full-adapter:FXMA2102L8X','U14',294.64,86.36)
    props(s,294.64,33.02)
    for pin,net in [('2','SOC_PCIE_WAKE_N'),('3','SOC_PCIE_CLKREQ_N'),('7','ETH_WAKE_N'),('6','ETH_CLKREQ_N')]:
        s.connect('U14',pin,net,10.16,global_net=True)
    s.connect('U14','5','VCC3V3_S0',7.62,global_net=True)
    for pin,rail,x,ref,y in [('1','VCC3V3_S0',218.44,'C700',48.26),('8','VCC3V3_ETH',370.84,'C701',40.64)]:
        p=u[pin];s.wire(p,(p[0],y));s.wire((p[0],y),(x,y));s.power(rail,(x,y))
        c=cap(s,ref,'100nF',x,y+10.16);s.wire((x,y),c['1']);s.wire(c['2'],(x,y+20.32));s.power('GND',(x,y+20.32))
    p=u['4'];s.wire(p,(p[0],127));s.power('GND',(p[0],127))
    s.text('OE is hard-wired to VCCA as permitted by onsemi note4.\nDo not substitute a translator that requires VCCA <= VCCB.\nBoth ports isolate when either supply reaches 0V.\nKeep both segments short; target <=50pF per port.\nCheck slow ramps and LOW voltage drop on hardware.',195.58,152.4,1.05)
    s.box('Host defaults — account for the 16k minimum internal pull-down',10.16,198.12,396.24,50.8)
    p=json.loads((ROOT/'research/ethernet-control-parts.json').read_text())['host_pullup']
    for ref,net,x in [('R700','SOC_PCIE_WAKE_N',66.04),('R701','SOC_PCIE_CLKREQ_N',205.74)]:
        r=s.place('Device:R_Small_US',ref,x,220.98,value='1.5kR 1%',fields={'MPN':p['model'],'Manufacturer':p['manufacturer'],'LCSC':p['lcsc'],'Footprint':'Resistor_SMD:R_0402_1005Metric'})
        s.wire(r['1'],(x,210.82));s.power('VCC3V3_S0',(x,210.82));s.wire(r['2'],(x,236.22));s.label(net,(x,236.22),global_net=True)
    r=resistor(s,'R702','47kR 1%',345.44,226.06)
    s.wire(r['1'],(345.44,213.36));s.label('SOC_PCIE_PERST_N',(345.44,213.36),global_net=True)
    s.wire(r['2'],(345.44,238.76));s.power('GND',(345.44,238.76))
    s.text('Boot firmware must select WAKEn/CLKREQn functional M1 and disable their internal pulls. PERST defaults LOW.\nNo D3cold wake with Ethernet powered off. Suspend/resume and ASPM require verified pinmux, reference-clock and driver sequencing.',15.24,269.24,1.05)
    return finish(s)


def ethernet_reset():
    s=Sheet('ethernet-reset','Ethernet startup reset qualification')
    s.box('Host reset — input may remain powered with Ethernet off',10.16,15.24,190.5,119.38)
    u=s.place('full-adapter:SN74LVC1G07DCKR','U15',109.22,83.82)
    props(s,76.2,45.72)
    s.connect('U15','1',None)
    s.connect('U15','2','SOC_PCIE_PERST_N',10.16,global_net=True)
    s.connect('U15','4','ETH_RESET_CONDITION_N',10.16,global_net=True)
    p=u['5'];s.wire(p,(p[0],40.64));s.wire((p[0],40.64),(165.1,40.64));s.power('VCC3V3_ETH',(165.1,40.64))
    c=cap(s,'C702','100nF',165.1,53.34);s.wire((165.1,40.64),c['1']);s.wire(c['2'],(165.1,63.5));s.power('GND',(165.1,63.5))
    p=u['3'];s.wire(p,(p[0],111.76));s.power('GND',(p[0],111.76))
    s.text('R702 holds the input LOW when the processor is absent.\n5.5V tolerant input; Ioff prevents off-domain back-power.\nOpen-drain output shares the U12/U13 PG condition bus.',17.78,119.38,1.05)
    s.box('180–420ms release delay — power and host reset must be valid',208.28,15.24,198.12,119.38)
    u=s.place('full-adapter:TPS3808G33DBVR','U16',325.12,83.82)
    props(s,287.02,40.64)
    s.connect('U16','3','ETH_RESET_CONDITION_N',7.62,global_net=True)
    s.connect('U16','5','VCC3V3_ETH',7.62,global_net=True)
    s.connect('U16','1','ETH_PERST_N',7.62,global_net=True)
    s.connect('U16','4','ETH_RESET_CT',7.62)
    p=u['6'];s.wire(p,(p[0],30.48));s.wire((p[0],30.48),(381,30.48));s.power('VCC3V3_ETH',(381,30.48))
    c=cap(s,'C703','100nF',381,45.72);s.wire((381,30.48),c['1']);s.wire(c['2'],(381,55.88));s.power('GND',(381,55.88))
    p=u['2'];s.wire(p,(p[0],111.76));s.power('GND',(p[0],111.76))
    s.text('SENSE threshold:3.07V. CT resistor selects300ms typical.\nEvery host reset or PG fault restarts the release timer.',215.9,121.92,1.05)
    s.box('Delay selection and local release pull-up',10.16,144.78,190.5,104.14)
    p=json.loads((ROOT/'research/cpu-control-resistors.json').read_text())[2]['result']['results'][0]
    r=s.place('Device:R_Small_US','R703',58.42,187.96,value='100kR 1%',fields={'MPN':p['model'],'Manufacturer':p['manufacturer'],'LCSC':p['lcsc'],'Footprint':'Resistor_SMD:R_0402_1005Metric'})
    s.wire(r['1'],(58.42,172.72));s.power('VCC3V3_ETH',(58.42,172.72));s.wire(r['2'],(58.42,205.74));s.label('ETH_RESET_CT',(58.42,205.74))
    r=resistor(s,'R704','10kR 1%',147.32,187.96)
    s.wire(r['1'],(147.32,172.72));s.power('VCC3V3_ETH',(147.32,172.72));s.wire(r['2'],(147.32,205.74));s.label('ETH_PERST_N',(147.32,205.74),global_net=True)
    s.text('R703 is within the40–200k selection range.\nR704 pulls up in the Ethernet domain only.\nR679 remains a47k local pulldown at U11.\nNo capacitor is placed on PERSTB.',17.78,220.98,1.05)
    s.box('Shared condition bus and validation boundaries',208.28,144.78,198.12,104.14)
    s.text('ETH_RESET_CONDITION_N joins U12 PG, U13 PG and U15 Y.\nR653/R663 pull up to Ethernet3.3V; any LOW holds reset.\nTP651/TP661 now observe this same shared condition.\nThe normal soft starts finish well before the180ms\nminimum delay expires. Configure stable REFCLK before\nraising host PERST; it must precede U11 release by100us.\n\nFast power-loss reset is NOT yet qualified: regulator PG\nhas40us typical deglitch with no guaranteed maximum.\nA fast fault path and its timing remain required work.',215.9,170.18,1.05)
    s.text('RTL8125BG Table35: >=100ms stable power, >=100us assertion/clock lead, >=10ms between releases.\nTPS3808 delay closes the normal-startup timing; abrupt faults, repeated power cycles and the final boot image still require qualification.',15.24,269.24,1.05)
    return finish(s)
