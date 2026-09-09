"""PMU-domain control, hardware voltage strap and PMIC I2C connection."""
import json
from schematic import ROOT,Sheet


def processor_control():
    s=Sheet('processor-control','Processor reset, PMIC interface and boot straps')
    manifest=json.loads((ROOT/'research/core-symbols.json').read_text())['RK3568B2']
    source=json.loads((ROOT/'research/pmic-control-passives.json').read_text())
    pullup=source['pullup_10k']['results'][0]
    zero=json.loads((ROOT/'research/processor-control-passives.json').read_text())['zero_ohm']['results'][0]
    def resistor(ref,part,value,x,y,angle=0):
        return s.place('Device:R_Small_US',ref,x,y,angle=angle,value=value,fields={
            'Footprint':'Resistor_SMD:R_0402_1005Metric','MPN':part['model'],
            'LCSC':part['lcsc'],'Manufacturer':part['manufacturer']})
    s.box('PMUIO1 — fixed 3.3V',10.16,15.24,172.72,91.44)
    s.place('full-adapter:RK3568B2','U1',76.2,60.96,unit=29)
    connections={'AH27':'SYS_RESET_L','Y22':'SD_CARD_DET_L','AA22':'PMIC_INT_L',
                 'AG25':'FLASH_VOL_SEL','AG26':'SOC_TSHUT_L','AG28':'PMIC_SLEEP_H'}
    for p in manifest[28]['pins']:s.connect('U1',p['ball'],connections.get(p['ball']),7.62,global_net=True)
    s.text('GPU power and SD power are controlled through RK809.\nREFCLK_OUT is unused; PCIe uses its dedicated clock pins.',17.78,93.98,1.1)
    s.box('PMUIO2 — 1.8V PMIC bus and console',10.16,116.84,172.72,111.76)
    s.place('full-adapter:RK3568B2','U1',76.2,170.18,unit=34)
    connections={'AB21':'I2C0_SDA_PMIC','AF24':'I2C0_SCL_PMIC',
                 'AC20':'SOC_UART2_RX_1V8','AH24':'SOC_UART2_TX_1V8'}
    for p in manifest[33]['pins']:s.connect('U1',p['ball'],connections.get(p['ball']),7.62,global_net=True)
    for ref,net,y,value in [('TP560','SOC_UART2_RX_1V8',152.4,'RX 1.8V'),
                            ('TP561','SOC_UART2_TX_1V8',177.8,'TX 1.8V'),
                            ('TP562','GND',200.66,'GND')]:
        p=s.place('Connector:TestPoint',ref,137.16,y,value=value,fields={
            'Footprint':'TestPoint:TestPoint_Pad_D1.0mm'})
        end=(137.16,y+7.62);s.wire(p['1'],end)
        if net=='GND':s.power(net,end)
        else:s.label(net,end,global_net=True)
    s.text('I2C0 connects both RK809 and RK860.\n1.8V pull-ups and PMIC series resistors are on the PMIC page.\nConsole connector/level conversion remain to be captured.',17.78,208.28,1.1)
    s.box('Hardware boot configuration',198.12,15.24,208.28,91.44)
    for ref,net,x in [('R560','FLASH_VOL_SEL',238.76),('R562','SD_CARD_DET_L',342.9)]:
        r=resistor(ref,pullup,'10kR 1%',x,45.72)
        s.wire(r['1'],(x,38.1));s.power('VCC3V3_PMU',(x,38.1))
        s.wire(r['2'],(x,60.96));s.label(net,(x,60.96),global_net=True)
    s.text('FLASH_VOL_SEL HIGH selects 1.8V VCCIO2.\nNever drive this strap LOW with the current storage supply.\nSD_CARD_DET_L: HIGH selects boot JTAG; inserted card pulls LOW\nto select SDMMC0. Card-detect contact and debug access follow.',205.74,76.2,1.1)
    s.box('Reset and thermal/watchdog shutdown',198.12,116.84,208.28,111.76)
    r=resistor('R561',zero,'0R',292.1,147.32,angle=90)
    s.wire(r['1'],(238.76,147.32));s.label('SOC_TSHUT_L',(238.76,147.32),180,global_net=True)
    s.wire(r['2'],(345.44,147.32));s.label('SYS_RESET_L',(345.44,147.32),global_net=True)
    part=json.loads((ROOT/'research/ddr-passives-search.json').read_text())['searches'][6]['results'][0]
    c=s.place('Device:C','C560',345.44,172.72,value='100nF',fields={
        'Footprint':'Capacitor_SMD:C_0402_1005Metric','MPN':part['model'],
        'Manufacturer':part['manufacturer'],'LCSC':part['lcsc']})
    s.wire((345.44,147.32),c['1']);s.junction((345.44,147.32))
    s.wire(c['2'],(345.44,182.88));s.power('GND',(345.44,182.88))
    s.text('C560 is local to U1 AH27; C486 remains local to RK809.\nRK809 RESETB and the 3.3V pull-up share SYS_RESET_L.\nConfigure TSADC/watchdog output active LOW before use.\nR561 follows the Rockchip reference and can isolate TSHUT for debug.',205.74,198.12,1.1)
    s.text('Rockchip HW Guide V1.2 pp6–10; tablet reference p13.\nReset must remain asserted for at least 100 cycles of 24MHz. Power-good, manual reset and brownout recovery are still unfinished.\nUnused PMU pins are explicitly disconnected; development IO will use the powered 3.3V peripheral banks.',15.24,248.92,1.1)
    return s
