#!/usr/bin/env python3
"""PCIe coupling, reset/wake isolation and reference-clock disconnect for NIC power cycling."""
from capture import ROOT, Sheet, grouped, native_pins, stock, block
s=Sheet('nic-interface','PCIe and powered-off-safe Ethernet interfaces','A2')
for i,(a,b) in enumerate([('PCIE_TXP_SOC','ETH_PCIE_RXP'),('PCIE_TXN_SOC','ETH_PCIE_RXN'),('ETH_PCIE_TXP','PCIE_RXP_SOC'),('ETH_PCIE_TXN','PCIE_RXN_SOC')]):
 s.passive('C',f'C{1601+i}','100nF',78.74,66.04+43.18*i,a,b,'GRM033R60J104KE19D','Capacitor_SMD:C_0201_0603Metric','Murata',{'Voltage Rating':'6.3V','Tolerance':'10%','Dielectric':'X5R','Placement Intent':'at transmitter; Realtek small-package PCIe recommendation'},horizontal=True)
s.note('100-ohm differential pairs; one AC-coupling capacitor per conductor at transmitter.\nSoC TX reaches NIC HSIP/HSIN; NIC HSOP/HSON reaches SoC RX.\nKeep PCIe controller quiescent before Ethernet power removal.',25.4,233.68)
# Open-drain buffers tolerate a powered host while the NIC domain is off.
pins=native_pins(ROOT/'reference/nic-controls-native-candidates.kicad_sym','SN74LVC1G07DCKR')
assert pins=={'1':'N.C','2':'A','3':'GND','4':'Y','5':'VCC'}
buf=grouped('SN74LVC1G07_DCK',pins,[{'left':['2','1'],'right':['4'],'top':['5'],'bottom':['3']}],{'1':'no_connect','2':'input','3':'power_in','4':'open_collector','5':'power_in'})
for i,(inp,out,rail,x,y) in enumerate([('PCIE_PERST_SOC_N','ETH_PERST_N','ETH_3V3',289.56,66.04),('ETH_CLKREQ_N','PCIE_CLKREQ_N','VCC3V3_PMU',289.56,149.86),('ETH_WAKE_N','PCIE_WAKE_N','VCC3V3_PMU',289.56,233.68)]):
 p=s.symbol('Appliance:SN74LVC1G07_DCK',buf,f'U{1601+i}','SN74LVC1G07DCKR',x,y,'Package_TO_SOT_SMD:SOT-353_SC-70-5',{'MPN':'SN74LVC1G07DCKR','Manufacturer':'Texas Instruments','LCSC':'C7830','Datasheet':'https://www.ti.com/lit/ds/symlink/sn74lvc1g07.pdf'})
 s.attach(p,{'1':None,'2':inp,'3':'GND','4':out,'5':rail})
 s.cap(f'C{1605+i}','100nF',370.84,y,rail)
 if i:s.resistor(f'R{1601+i}','4.7kR',411.48,y,'VCC3V3_PMU',out,'RC0603FR-074K7L')
s.note('RESET sinks: SoC U1601, supervisor Q303, core monitor U1505.\nNo push-pull outputs share ETH_PERST_N. CLKREQ and wake outputs use Ioff buffers.\nWhile NIC is off, firmware ignores asserted wake/CLKREQ and disables ASPM.',208.28,289.56)
# A disabled analog switch prevents the live host clock from reaching an unpowered NIC.
tp=native_pins(ROOT/'reference/nic-extra-native-candidates.kicad_sym','TMUXHS4212IRKSR')
assert {n:v.upper() for n,v in tp.items()}=={'1':'RSVD1','2':'OEN','3':'A0P','4':'A0N','5':'GND','6':'VCC','7':'A1P','8':'A1N','9':'SEL','10':'RSVD2','11':'GND','12':'C1N','13':'C1P','14':'C0N','15':'C0P','16':'B1N','17':'B1P','18':'B0N','19':'B0P','20':'GND','21':'EP'}
roles={n:'power_in' if n in ['1','5','6','10','11','20','21'] else 'input' if n in ['2','9'] else 'passive' for n in tp}
mux=grouped('TMUXHS4212_RKS',tp,[{'left':['3','4','2','9','7','8'],'right':['19','18','17','16','15','14','13','12'],'top':['1','6','10'],'bottom':['5','11','20','21']}],roles)
p=s.symbol('Appliance:TMUXHS4212_RKS',mux,'U1604','TMUXHS4212IRKSR',129.54,332.74,'Appliance:DHVQFN-20_L4.5-W2.5-P0.50-BL-EP',{'MPN':'TMUXHS4212IRKSR','Manufacturer':'Texas Instruments','LCSC':'C3656912','Datasheet':'https://www.ti.com/lit/ds/symlink/tmuxhs4212.pdf','Qualification':'13GHz passive differential mux; HCSL CM/amplitude inside range. Reference-clock SI/jitter must be measured'})
nets={n:None for n in tp};nets.update({'1':'VCC3V3_PMU','6':'VCC3V3_PMU','10':'VCC3V3_PMU','2':'ETH_CLOCK_OE_N','9':'GND','3':'PCIE_REFCLK_P','4':'PCIE_REFCLK_N','19':'ETH_REFCLK_P','18':'ETH_REFCLK_N','5':'GND','11':'GND','20':'GND','21':'GND'})
s.attach(p,nets)
s.cap('C1608','100nF',223.52,332.74,'VCC3V3_PMU')
raw=(ROOT/'controls.kicad_sch').read_text();bjt=block(raw,raw.index('(symbol "Transistor_BJT:MMBT3904"'))
p=s.symbol('Transistor_BJT:MMBT3904',bjt,'Q1601','MMBT3904,215',388.62,355.6,'Package_TO_SOT_SMD:SOT-23',{'MPN':'MMBT3904,215','Manufacturer':'Nexperia'})
s.attach(p,{'1':'ETH_CLOCK_BASE','2':'GND','3':'ETH_CLOCK_OE_N'})
s.resistor('R1604','10kR',304.8,355.6,'ETH_3V3_GOOD','ETH_CLOCK_BASE','RC0603FR-0710KL',horizontal=True)
s.resistor('R1605','100kR',474.98,355.6,'ETH_CLOCK_BASE','GND','RC0603FR-07100KL')
s.resistor('R1606','10kR',525.78,355.6,'VCC3V3_PMU','ETH_CLOCK_OE_N','RC0603FR-0710KL')
s.note('Clock disconnected by default. Valid switched 3.3V after U1504 delay turns Q1601 on.\nMux stays on the SoC supply; NIC power cycling cannot turn on its clock path.\nCore reset delay ensures >100us clock-before-PERST margin. Validate shutdown transients.',269.24,398.78)
s.save()
for name,body in [('sn74lvc1g07',buf),('tmuxhs4212',mux)]:
 (ROOT/f'reference/{name}-captured.kicad_sym').write_text('(kicad_symbol_lib (version 20211014) (generator eeschema) '+body+')\n')
# Bypass at every NIC supply pad, plus bulk per filtered domain.
s=Sheet('nic-bypass','Ethernet local supply bypass','A3')
rails=['ETH_0V95']*3+['ETH_3V3']*3+['ETH_ANALOG_0V95']*3+['ETH_ANALOG_3V3']*3+['ETH_XTAL_3V3','ETH_PCIE_0V95']
for i,rail in enumerate(rails):s.cap(f'C{1620+i}','100nF',60.96+63.5*(i%5),60.96+55.88*(i//5),rail)
for i,rail in enumerate(['ETH_0V95','ETH_3V3','ETH_ANALOG_0V95','ETH_ANALOG_3V3','ETH_PCIE_0V95']):s.cap(f'C{1640+i}','4.7uF',60.96+63.5*i,228.6,rail)
s.note('One 100nF at each of 14 RTL8125BG supply pins.\nPlace bulk beside filtered analog banks; check DC drop and impedance under maximum load.',25.4,20.32)
s.save()
