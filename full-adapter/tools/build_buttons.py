"""Physical recovery, processor reset and PMIC power controls."""
import json
from schematic import ROOT,Sheet
from build_emmc import resistor,tp
from build_recovery import props


def button(s,ref,value,x,y):
    p=s.place('Switch:SW_Push',ref,x,y,value=value,fields={'Footprint':'full-adapter:Alps_SKRPACE010','MPN':'SKRPACE010','Manufacturer':'Alps Alpine','LCSC':'C139797','Datasheet':'https://tech.alpsalpine.com/cms.media/product_catalog_ta_02_skrp_en_2cd80f610b.pdf'})
    props(s,x,y-12.7)
    return p


def buttons():
    s=Sheet('buttons','Recovery, reset and PMIC power buttons')
    s.box('Recovery — hardware-defined SARADC_VIN0',10.16,15.24,215.9,215.9)
    u=s.place('full-adapter:RK3568B2','U1',172.72,88.9,unit=11)
    for p in ['C26','D24','E23','F21','F22','G20','G21']:s.connect('U1',p,None)
    p=u['B27'];s.wire(p,(76.2,p[1]));s.label('RECOVERY_KEY',(76.2,p[1]))
    r=resistor(s,'R640','10kR 1%',76.2,55.88);s.wire(r['2'],(76.2,p[1]));s.wire(r['1'],(76.2,45.72));s.power('VCC1V8_ANLG',(76.2,45.72))
    s.wire((76.2,p[1]),(76.2,124.46));s.junction((76.2,p[1]))
    b=button(s,'SW640','RECOVERY',101.6,124.46);s.wire((76.2,124.46),b['1']);s.wire(b['2'],(124.46,124.46));s.wire((124.46,124.46),(124.46,134.62));s.power('GND',(124.46,134.62))
    t=tp(s,'TP640','RECOVERY 1.8V',45.72,106.68);s.wire(t['1'],(45.72,124.46));s.wire((45.72,124.46),(76.2,124.46));s.junction((76.2,124.46))
    s.text('R640 uses the same rail as SARADC_AVDD_1V8.\nNo button: HIGH selects normal boot.\nHold RECOVERY during startup/reset to request Loader.\nRelease after the PC recognizes the USB device.\nDo not attach an external powered signal to TP640.\n\nUnused internal ADC channels are disconnected.\nPractical analog expansion will use a protected external ADC.\nMaskROM fallback remains on eMMC D0/GND service pads.',17.78,160.02,1.27)
    s.box('Processor reset — active LOW',238.76,15.24,167.64,91.44)
    s.box('PMIC power key — active LOW',238.76,116.84,167.64,114.3)
    part=json.loads((ROOT/'research/cpu-control-resistors.json').read_text())[1]['result']['results'][0]
    assert part['model']=='0402WGF1000TCE'
    for i,(net,title,y) in enumerate([('SYS_RESET_L','RESET',58.42),('PMIC_PWRON_L','POWER',157.48)]):
        r=s.place('Device:R_Small_US',f'R{641+i}',276.86,y,angle=90,value='100R 1%',fields={'Footprint':'Resistor_SMD:R_0402_1005Metric','MPN':part['model'],'Manufacturer':part['manufacturer'],'LCSC':part['lcsc']})
        s.wire(r['1'],(251.46,y));s.label(net,(251.46,y),180,global_net=True)
        b=button(s,f'SW{641+i}',title,335.28,y);s.wire(r['2'],b['1']);s.wire(b['2'],(373.38,y));s.wire((373.38,y),(373.38,y+10.16));s.power('GND',(373.38,y+10.16))
    s.text('R641 limits discharge of existing reset capacitors.\nReset does not remove power from the board.\nPMIC RESETB is open drain; keep reset pull-up R494.',246.38,81.28,1.1)
    s.text('R642 limits discharge of C485. Internal pull-up is 17k.\nPress >=500ms to start when PMIC input is valid.\nLong-press behavior depends on RK809 register settings;\nprovision and test shutdown/restart behavior explicitly.\nThis button does not solve brownout auto-restart.',246.38,193.04,1.1)
    s.text('Three identical normally-open Alps switches. Physical contacts 1/2 map to logical pad1; 3/4 map to logical pad2.\nReserve finger access and label RECOVERY / RESET / POWER on final silkscreen.\nRockchip HW Guide V1.2 p69; RK809 V1.7 pp26–29. USB recovery electrical qualification and automatic restart remain unfinished.',15.24,251.46,1.27)
    return s
