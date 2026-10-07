#!/usr/bin/env python3
"""Four-pair 2.5G magnetics, PoE center-tap extraction and PHY-side ESD."""
import re
from capture import ROOT,Sheet,stock,block,children,grouped,native_pins
s=Sheet('ethernet-ingress','2.5GbE cable ingress and four-pair PoE extraction','A2')
# Coil/CMC drawing from native TI reference; identical 24-contact topology audited to Pulse page 2.
raw=(ROOT/'reference/tida-import/input.kicad_sch').read_text();lib=next(i for i in children(raw) if i.startswith('(lib_symbols'))
instance=next(i for i in children(raw) if i.startswith('(symbol') and '(property "Reference" "T1"' in i)
name=re.search(r'\(lib_id "([^"]+)"',instance)[1];body=next(i for i in children(lib) if i.startswith('(symbol "'+name+'"'))
body=body.replace(name,'HX4110NL').replace('"'+name.split(':')[-1]+'_','"HX4110NL_')
assert set(re.findall(r'\(number "([^"]+)"',body))==set(map(str,range(1,25)))
p=s.symbol('Appliance:HX4110NL',body,'T1701','HX4110NLT',154.94,99.06,'',{'MPN':'HX4110NLT','Manufacturer':'Pulse Electronics','Datasheet':'https://productfinder.pulseeng.com/doc_type/WEB301/doc_num/HX4110NL/doc_part/HX4110NL.pdf','Speed':'2.5GBASE-T (manufacturer product finder)','PoE Rating':'4-pair 60W (manufacturer product finder)','Isolation':'1500Vrms','Footprint Status':'Manufacturer suggested land pattern pending native footprint audit'})
netmap={}
for pair,(ct,tp,tn,cp,cc,cn),feed in zip(range(4),[('1','2','3','23','24','22'),('4','5','6','20','21','19'),('7','8','9','17','18','16'),('10','11','12','14','15','13')],['12','36','45','78']):
 netmap.update({ct:f'ETH_CT{pair}',tp:f'ETH_MDI{pair}_P',tn:f'ETH_MDI{pair}_N',cp:f'CABLE_MDI{pair}_P',cc:'POE_PAIR'+feed,cn:f'CABLE_MDI{pair}_N'})
s.attach(p,netmap)
p=s.symbol('Connector:RJ45_Shielded',stock('Connector','RJ45_Shielded'),'J1701','2.5GbE + PoE',393.7,96.52,'',{'MPN':'RJE491881401','Manufacturer':'Amphenol Communications Solutions','Datasheet':'https://cdn.amphenol-cs.com/media/wysiwyg/files/drawing/rje491881x01.pdf','Current Rating':'1.25A per contact','Performance':'CAT6; PoE++ supported (S6103C Rev1.3)','Footprint Status':'Exact RJE49 drawing required; RJHSE footprint prohibited'})
s.attach(p,{'1':'CABLE_MDI0_P','2':'CABLE_MDI0_N','3':'CABLE_MDI1_P','6':'CABLE_MDI1_N','4':'CABLE_MDI2_P','5':'CABLE_MDI2_N','7':'CABLE_MDI3_P','8':'CABLE_MDI3_N','SH':'CHASSIS'})
for i in range(4):s.cap(f'C{1851+i}','100nF',63.5+71.12*i,213.36,f'ETH_CT{i}')
# PHY uses voltage-mode magnetics bias: each PHY center tap AC-grounded, never fed 3.3V.
esd_pins=native_pins(ROOT/'reference/sierra-esd-native.kicad_sym','TPD4E02B04DQAR')
assert esd_pins=={'1':'IO1','8':'GND','2':'IO2','4':'IO3','5':'IO4','6':'NC','7':'NC','9':'NC','10':'NC','3':'GND'}
esd=grouped('TPD4E02B04_DQA',esd_pins,[{'left':['1','2','4','5'],'right':['6','7','9','10'],'bottom':['3','8']}],{n:'passive' for n in esd_pins})
for i in range(2):
 p=s.symbol('Appliance:TPD4E02B04_DQA',esd,f'D{1851+i}','TPD4E02B04DQAR',411.48,210.82+88.9*i,'Appliance:USON-10_L2.5-W1.0-P0.50-BL',{'MPN':'TPD4E02B04DQAR','Manufacturer':'Texas Instruments','LCSC':'C106794','Datasheet':'https://www.ti.com/lit/ds/symlink/tpd4e02b04.pdf','Working Voltage':'-3.6 to +3.6V','Capacitance':'0.33pF maximum','Placement':'PHY side of transformer, short discharge path to GND'})
 nets={'1':f'ETH_MDI{2*i}_P','2':f'ETH_MDI{2*i}_N','4':f'ETH_MDI{2*i+1}_P','5':f'ETH_MDI{2*i+1}_N','3':'GND','8':'GND','6':None,'7':None,'9':None,'10':None};s.attach(p,nets)
# TI reference Bob-Smith network. Its center taps carry PoE DC, so series capacitors are mandatory.
for i,feed in enumerate(['12','36','45','78']):
 x=63.5+71.12*i
 s.passive('C',f'C{1861+i}','10nF / 100V',x,276.86,'POE_PAIR'+feed,f'BS_PAIR{i}','C1608X7R2A103K','Capacitor_SMD:C_0603_1608Metric','TDK',{'Voltage Rating':'100V','Tolerance':'10%','Source':'TI TIDA-050023 C1/C2/C4/C5'})
 s.passive('R',f'R{1861+i}','75R',x,332.74,f'BS_PAIR{i}','BOB_SMITH_COMMON','CRCW060375R0FKEA','Resistor_SMD:R_0603_1608Metric','Vishay',{'Tolerance':'1%','Power Rating':'0.1W'})
s.passive('C','C1865','1nF / 2kV',381,363.22,'BOB_SMITH_COMMON','CHASSIS','GR442QR73D102KW01L','Capacitor_SMD:C_1808_4520Metric','Murata',{'Voltage Rating':'2kV','Qualification':'TI reference HV MLCC. Isolation/EMC compliance must be reviewed; do not claim Y certification.'})
s.note('T1701 pin/polarity and four center taps audited to Pulse page 2.\nPHY CTs: one 100nF to GND each, following RTL8125BG reference.\nCable CTs feed active PoE bridge; 10nF series caps block PoE DC\nin Bob-Smith termination. CHASSIS is RJ45 shell/enclosure only.\nNo copper connection across magnetics or to primary PoE returns.\nExact transformer and RJ45 footprints remain a layout gate.',25.4,396.24)
s.save()
for name,body in [('hx4110nl',body),('tpd4e02b04',esd)]:
 (ROOT/f'reference/{name}-captured.kicad_sym').write_text('(kicad_symbol_lib (version 20260830) (generator eeschema) '+body+')\n')
