"""Historical RK3568/RTL8125 draft; not integrated or electrically qualified.

Preserved at the CM4 architecture handoff. Do not run this as a current carrier
generator. Its proposed timing/discharge claims remain unvalidated.
"""
import json
from schematic import ROOT, Sheet
from build_emmc import cap, resistor
from build_recovery import props
from build_ethernet_controller import finish


def ethernet_sequencing():
    s=Sheet('ethernet-sequencing','Ethernet power-cycle qualification and discharge')
    s.box('S0 must be present — open-drain translation to the 5V supervisor',10.16,15.24,190.5,111.76)
    u=s.place('full-adapter:SN74LVC1G07DCKR','U18',101.6,73.66)
    props(s,63.5,35.56)
    s.connect('U18','1',None)
    s.connect('U18','2','VCC3V3_S0',12.7,global_net=True)
    s.connect('U18','4','ETH_S0_VALID_N',10.16)
    p=u['5'];s.wire(p,(p[0],33.02));s.wire((p[0],33.02),(162.56,33.02));s.power('VCC3V3_SYS',(162.56,33.02))
    c=cap(s,'C711','100nF',162.56,48.26);s.wire((162.56,33.02),c['1']);s.wire(c['2'],(162.56,58.42));s.power('GND',(162.56,58.42))
    p=u['3'];s.wire(p,(p[0],104.14));s.power('GND',(p[0],104.14))
    s.text('Input follows S0; 2.0V VIH is below the3.135V S0 minimum.\nU18 pulls MR LOW with S0 absent. Its output tolerates5.5V.\nNo 5V pull-up is connected directly to a processor rail.',17.78,114.3,1.05)
    s.box('Input UV and S0 qualify every enable — 180–420ms delay',208.28,15.24,198.12,111.76)
    u=s.place('full-adapter:TPS3808G33DBVR','U17',322.58,76.2)
    props(s,289.56,33.02)
    for pin,net in [('3','ETH_S0_VALID_N'),('4','ETH_CYCLE_CT'),('5','ETH_INPUT_SENSE')]:s.connect('U17',pin,net,10.16)
    s.connect('U17','1','ETH_SUPPLY_ENABLE',10.16,global_net=True)
    p=u['6'];s.wire(p,(p[0],27.94));s.wire((p[0],27.94),(378.46,27.94));s.power('VCC5V_SYS',(378.46,27.94))
    c=cap(s,'C710','100nF',378.46,43.18);s.wire((378.46,27.94),c['1']);s.wire(c['2'],(378.46,53.34));s.power('GND',(378.46,53.34))
    p=u['2'];s.wire(p,(p[0],106.68));s.power('GND',(p[0],106.68))
    s.text('SENSE trips at about4.35V on the5V input. U17 resets\nits enable timer after input UV, S0 loss or cold power-up.\nU16 adds its separate endpoint reset delay after rail startup.',215.9,114.3,1.05)
    s.box('Input divider, delay and local enable pull-up',10.16,139.7,190.5,109.22)
    parts=json.loads((ROOT/'research/ethernet-regulator-stock.json').read_text())['passives']
    for ref,mpn,value,x,y in [('R716','RT0603BRD0710KL','10kR 0.1%',45.72,175.26),('R717','RT0603BRD0724KL','24kR 0.1%',45.72,213.36)]:
        p=parts[mpn];r=s.place('Device:R_Small_US',ref,x,y,value=value,fields={'MPN':mpn,'Manufacturer':p['manufacturer'],'LCSC':p['lcsc'],'Footprint':'Resistor_SMD:R_0603_1608Metric'})
        if ref=='R716':
            s.wire(r['1'],(x,162.56));s.power('VCC5V_SYS',(x,162.56));s.wire(r['2'],(x,193.04))
        else:
            s.wire(r['1'],(x,193.04));s.wire(r['2'],(x,226.06));s.power('GND',(x,226.06))
    s.label('ETH_INPUT_SENSE',(45.72,193.04))
    p=json.loads((ROOT/'research/cpu-control-resistors.json').read_text())[2]['result']['results'][0]
    r=s.place('Device:R_Small_US','R714',116.84,187.96,value='100kR 1%',fields={'MPN':p['model'],'Manufacturer':p['manufacturer'],'LCSC':p['lcsc'],'Footprint':'Resistor_SMD:R_0402_1005Metric'})
    s.wire(r['1'],(116.84,175.26));s.power('VCC5V_SYS',(116.84,175.26));s.wire(r['2'],(116.84,200.66));s.label('ETH_CYCLE_CT',(116.84,200.66))
    r=resistor(s,'R715','10kR 1%',172.72,187.96)
    s.wire(r['1'],(172.72,175.26));s.power('VCC3V3_S0',(172.72,175.26));s.wire(r['2'],(172.72,208.28));s.label('ETH_SUPPLY_ENABLE',(172.72,208.28),180,global_net=True)
    s.text('R714 selects300ms typical. R715 pulls up only to S0;\nR65247k remains a pulldown at U12EN. The input divider\nuses existing0.1% /25ppm parts. No CT capacitor is fitted.',17.78,236.22,1.05)
    s.box('Passive discharge — independent of internal regulator discharge',208.28,139.7,198.12,109.22)
    parts=json.loads((ROOT/'research/ethernet-sequencing-parts.json').read_text())
    for ref,x,key,value,rail,foot in [('R710',236.22,'bleed_100','100R 1%','VCC3V3_ETH','Resistor_SMD:R_1206_3216Metric'),('R711',276.86,'bleed_100','100R 1%','VCC3V3_ETH','Resistor_SMD:R_1206_3216Metric'),('R712',317.5,'bleed_100','100R 1%','VCC3V3_ETH','Resistor_SMD:R_1206_3216Metric'),('R713',378.46,'bleed_47','47R 1%','VDD0V95_ETH','Resistor_SMD:R_0603_1608Metric')]:
        p=parts[key];r=s.place('Device:R_Small_US',ref,x,187.96,value=value,fields={'MPN':p['model'],'Manufacturer':p['manufacturer'],'LCSC':p['lcsc'],'Footprint':foot})
        s.wire(r['1'],(x,172.72));s.power(rail,(x,172.72));s.wire(r['2'],(x,203.2));s.power('GND',(x,203.2))
    s.text('Three100R /0.25W parts give33.33R on Ethernet3.3V.\nAllow0.36W total bleed power; core47R dissipates~20mW.\nWith maximum capacitors and resistor corners, both rails\nfall below1mV within the reserved130ms discharge budget.\nKeep bleeders away from the PHY/crystal; verify hot restarts.',215.9,220.98,1.05)
    s.text('U17 rejects a5V dip even if the S0 rail retains charge. The >=180ms enable hold leaves >=50ms after a130ms discharge allowance.\nVerify no REFCLK/control back-power and restart monotonicity. Shallow/fast input dips, full-system brownout and fast-fault reset remain qualification work.',15.24,269.24,1.05)
    return finish(s)
