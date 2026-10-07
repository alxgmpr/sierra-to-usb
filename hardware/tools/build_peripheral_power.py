#!/usr/bin/env python3
"""Complete processor analog filters and enforce routed Kelvin feedback nets."""
from capture import Sheet
s=Sheet('peripheral-power','Processor peripheral supplies and remote feedback','A2')
for i,(src,out,y) in enumerate([('VDDA_0V9','MULTI_AVDD_0V9',66.04),('VCCA_1V8','MULTI_AVDD_1V8',139.7),('VDDA_0V9','USB2_AVDD_0V9',213.36),('VCCA_1V8','USB2_AVDD_1V8',287.02)]):
 s.passive('FB',f'FB{1401+i}','120R @ 100MHz',91.44,y,src,out,'MPZ1608S121ATAH0','Inductor_SMD:L_0603_1608Metric','TDK',{'DCR Maximum':'45mOhm','Current Rating':'2A','Placement Intent':'close to analog supply pins'},horizontal=True)
 for j,val in enumerate(['1uF','100nF','1uF']):s.cap(f'C{1401+3*i+j}',val,162.56+38.1*j,y,out)
 s.flag(f'#FLG{1401+i}',out,292.1,y,f'RK809 analog LDO through FB{1401+i}')
s.note('MULTI-PHY supplies serve PCIe plus USB3 OTG1.\nUSB2 filters serve unused host PHY; keep host2/3 disabled.\nDCR drop, PDN impedance and reference tolerances require review.',25.4,335.28)
# Every additionally powered display/camera supply gets local bypass.
for i,rail in enumerate(['VDDA_0V9','VCCA_1V8']*7+['3V3_MAIN']):
 s.cap(f'C{1420+i}','100nF',350.52+38.1*(i%5),66.04+63.5*(i//5),rail)
s.note('Local bypass at powered inactive MIPI/HDMI/eDP analog domains.\nFirmware keeps unused PHYs off; check combined RK809 LDO loading.',330.2,226.06)
# Keep FB copper distinct from power copper until the load-side 0R links.
for i,(rail,sense) in enumerate([('VDD_CPU','CPU_FB'),('VDD_LOGIC','LOGIC_FB'),('VDD_GPU','GPU_FB'),('VDD_NPU','NPU_FB')]):
 x=342.9+50.8*i
 if i<3:
  s.resistor(f'R{1401+i}','100R',x,274.32,rail,sense,'RC0603FR-07100RL')
 s.passive('C',f'C{1441+i}','1uF',x,335.28,rail,sense,'CL10B105KA8NNNC','Capacitor_SMD:C_0603_1608Metric','Samsung Electro-Mechanics',{'Placement Intent':'DC/DC-side parallel feedback compensation; RK3566 guide Fig 2-23'})
 s.resistor(f'R{1411+i}','0R',x,391.16,rail,sense,'RC0603JR-070RL')
s.note('100R || 1uF at DC/DC: feedback remains controlled if Kelvin trace opens.\nR1411–R1414 connect FB nets to power at processor load pads.\nNPU uses existing R512 (100R). Route FB separately to load.',330.2,246.38)
for ref,net,x,source in [('#FLG1411','USB_AVDD_0V9',101.6,'FB801 fed by RK809 LDO3'),('#FLG1412','USB_AVDD_1V8',215.9,'FB802 fed by RK809 LDO5')]:
 s.flag(ref,net,x,381,source)
s.save()
