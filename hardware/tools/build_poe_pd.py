#!/usr/bin/env python3
"""Fixed Class-6 PD; remove EVM selectors and auxiliary-input detection loading."""
import re
from capture import ROOT, Sheet, grouped, block, children, stock
raw=(ROOT/'reference/tida-import/pd.kicad_sch').read_text()
source=next(i for i in children(next(i for i in children(raw) if i.startswith('(lib_symbols'))) if '(name "CLSA"' in i)
pins={re.search(r'\(number "([^"]+)"',b)[1]:re.search(r'\(name "([^"]+)"',b)[1] for m in re.finditer(r'\(pin \w+ \w+',source) for b in [block(source,m.start())]}
assert pins=={'1':'VDD','2':'DEN','3':'CLSA','4':'VSS','5':'VSS','6':'CLSB','7':'REF','8':'AMPS_CTL','9':'MPS_DUTY','10':'APD','11':'RTN','12':'RTN','13':'PG','14':'VC_OUT','15':'VC_IN','16':'UVLO_SEL','17':'TPL','18':'TPH','19':'BT','20':'NC','21':'PAD'}
roles={n:'power_in' if n in ['1','4','5','21','15'] else 'power_out' if n=='14' else 'open_collector' if n in ['13','17','18','19'] else 'input' if n in ['9','10','16'] else 'output' if n in ['3','6','7','8'] else 'passive' for n in pins}
sym=grouped('TPS2373_3RGW',pins,[{'top':['1'],'bottom':['4','5','21'],'left':['2','3','6','7','8','9','10','16','20'],'right':['11','12','13','14','15','18','17','19']}],roles)
s=Sheet('poe-pd','Class-6 powered device — fixed assembly configuration','A2')
p=s.symbol('Appliance:TPS2373_3RGW',sym,'U1701','TPS2373-3RGWR',116.84,96.52,'PoE:TI_RGW0020B',{'MPN':'TPS2373-3RGWR','Manufacturer':'Texas Instruments','Datasheet':'https://www.ti.com/lit/ds/symlink/tps2373.pdf','Source':'TI TIDA-050023, TPS2373 Rev C','ERC Model':'RTN is passive MOSFET drain; VC_OUT is the internally generated bias supply'})
s.attach(p,{'1':'POE_VDD','2':'POE_DEN','3':'POE_CLSA','4':'POE_VSS','5':'POE_VSS','6':'POE_CLSB','7':'POE_REF','8':'POE_AMPS_CTL','9':'POE_VSS','10':'POE_RTN','11':'POE_RTN','12':'POE_RTN','13':'POE_UVLO','14':'POE_VCOUT','15':'POE_VCIN','16':None,'17':'POE_TPL','18':'POE_TPH','19':'POE_BT','20':None,'21':'POE_VSS'})
for ref,val,x,y,a,b,mpn in [
 ('R1723','24.9kR',274.32,55.88,'POE_VDD','POE_DEN','CRCW060324K9FKEA'),
 ('R1724','63.4R',274.32,111.76,'POE_CLSA','POE_VSS','CRCW060363R4FKEA'),
 ('R1727','249R',358.14,111.76,'POE_CLSB','POE_VSS','CRCW0603249RFKEA'),
 ('R1732','49.9kR',441.96,111.76,'POE_REF','POE_VSS','CRCW060349K9FKEA')]:
 s.passive('R',ref,val,x,y,a,b,mpn,'Resistor_SMD:R_0603_1608Metric','Vishay',{'Tolerance':'1%','Power Rating':'0.1W'})
s.passive('R','R1730','1kR',274.32,172.72,'POE_AMPS_CTL','POE_VSS','CRCW20101K00FKEF','Resistor_SMD:R_2010_5025Metric','Vishay',{'Tolerance':'1%','Power Rating':'0.75W','Qualification':'24.9V/990R, 26.4% worst MPS duty: 0.166W maximum average'})
# TI reference bias and bulk capacitors retained. C1740 on flyback supplies the additional 1uF VC_OUT bypass.
for ref,val,x,y,a,b,mpn,fp,maker,voltage in [
 ('C1716','10nF',274.32,233.68,'POE_VCIN','POE_RTN','GRM188R61H103KA01D','C_0603_1608Metric','Murata','50V'),
 ('C1718','100nF',358.14,233.68,'POE_VCOUT','POE_RTN','06033D104KAT2A','C_0603_1608Metric','KYOCERA AVX','25V'),
 ('C1719','100nF',441.96,233.68,'POE_VDD','POE_VSS','C0805C104K1RACTU','C_0805_2012Metric','KEMET','100V')]:
 s.passive('C',ref,val,x,y,a,b,mpn,'Capacitor_SMD:'+fp,maker,{'Voltage Rating':voltage,'Dielectric':'X7R','Tolerance':'10%'})
p=s.symbol('Device:C_Polarized',stock('Device','C_Polarized'),'C1717','47uF / 63V',116.84,243.84,'PoE:TI_SM_RADIAL_F',{'MPN':'EEE-FK1J470P','Manufacturer':'Panasonic','Voltage Rating':'63V','Source':'TI TIDA-050023'})
s.attach(p,{'1':'POE_VDD','2':'POE_RTN'})
# Flag only physical PSE-derived sources and the enabled internal hotswap return.
for ref,net,x,source in [('#FLG1702','POE_RTN',68.58,'TPS2373 internal hotswap MOSFET to POE_VSS'),('#FLG1703','POE_VDD',154.94,'PSE through T1701 center taps and active input bridge'),('#FLG1704','POE_VSS',241.3,'PSE return through input bridge and permanent port-current trace')]:s.flag(ref,net,x,325.12,source)
s.note('Fixed Class 6: CLSA 63.4R, CLSB 249R. Accept only 51W bt grant: TPH low / TPL high / BT low.\nThree optocouplers carry status across isolation to the always-on supervisor.\nNo auxiliary input. APD tied to RTN; detection resistor changes from reference 27.4k to 24.9k\nbecause its auxiliary-divider parallel load was removed. MPS_DUTY tied to VSS (12.5% bt).\nUVLO_SEL left open, following the LM51551 TI reference; validate startup at input corners.\nPOE_VSS is the cable return. POE_RTN is the switched primary return. Neither connects to GND.',30.48,391.16)
s.save()
(ROOT/'reference/tps2373-captured.kicad_sym').write_text('(kicad_symbol_lib (version 20211014) (generator eeschema) '+sym+')\n')
