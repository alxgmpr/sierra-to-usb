#!/usr/bin/env python3
"""Validate full native appliance connectivity; report explicit release holds."""
import argparse, csv, json, re, subprocess, tempfile
from pathlib import Path
import xml.etree.ElementTree as E
from capture import ROOT
from check_footprint_reviews import check as check_footprint_reviews
from check_modem_documentation import check as check_modem_documentation
from check_bga_process import check as check_bga_process
from check_model_reviews import check as check_model_reviews
CLI='/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli'
def export(path, output):
 subprocess.run([CLI,'sch','export','netlist','--format','kicadxml','--output',str(output),str(path)],check=True,capture_output=True)
 return E.parse(output).getroot()
def validate(tree,directory):
 check_footprint_reviews()
 check_modem_documentation()
 check_bga_process()
 check_model_reviews()
 C={c.get('ref'):c for c in tree.findall('./components/comp')}
 N={n.get('name'):{(v.get('ref'),v.get('pin')) for v in n.findall('node')} for n in tree.findall('./nets/net')}
 B={p:n for n,ps in N.items() for p in ps}
 F=lambda ref:{f.get('name'):f.text for f in C[ref].findall('./fields/field')}
 def on(ref,pin,net):assert B[(ref,pin)]==net,(ref,pin,B.get((ref,pin)),net)
 probe=lambda ps:{p for p in ps if not p[0].startswith('TP24')}   # bring-up probe pads never count toward exact membership
 def exact(net,*pins):assert probe(N[net])=={tuple(p.split(':')) for p in pins},(net,N[net],pins)
 def subset(net,*pins):assert {tuple(p.split(':')) for p in pins}<=N[net],(net,N[net],pins)
 def nc(ref,pin):
  name=B[(ref,pin)];assert name.startswith('unconnected-') and N[name]=={(ref,pin)},(ref,pin,name)
 def connected(ref,mapping):
  for net,pins in mapping.items():
   for pin in pins.split():on(ref,pin,net)
 assert len(C)==820,len(C)
 assert len(B)==sum(len(p) for p in N.values()),'Physical pin appears in two nets'
 for ref in C:
  if ref in ['TP1101','TP1102','TP1103'] or ref.startswith('TP24'):assert C[ref].findtext('footprint')=='TestPoint:TestPoint_Pad_D1.0mm'
  else:assert F(ref).get('MPN') and F(ref).get('Manufacturer'),ref
 libs={(p.get('lib'),p.get('part')):{v.get('num') for v in p.findall('./pins/pin')} for p in tree.findall('./libparts/libpart')}
 counts={'U801':565,'U901':200,'U1101':153,'U501':69,'U1001':20,'U1301':49,'U201':48,'U1710':47,'U1901':15,'U1902':10,'J2001':67,'J2002':12}
 for ref,count in counts.items():
  src=C[ref].find('libsource');numbers=libs[(src.get('lib'),src.get('part'))]
  assert len(numbers)==count,(ref,len(numbers),count)
  assert {p for r,p in B if r==ref}==numbers,(ref,'Unaccounted native contacts')
 rows=list(csv.DictReader((ROOT/'pinmaps/processor-capture.csv').open()));assert len(rows)==565
 for row in rows:
  if row['net']:on('U801',row['ball'],row['net'])
  else:nc('U801',row['ball'])
 manufacturer=list(csv.DictReader((ROOT/'pinmaps/rk3566.csv').open()))
 grounds={r['ball'] for r in manufacturer if re.fullmatch(r'(?:VSS|AVSS|AVSS1)_\d+',r['manufacturer_name']) or r['manufacturer_name'] in {'DDR_AVSS','PMUPLL_AVSS','SYSPLL_AVSS'}}
 assert len(grounds)==187
 assert {p for r,p in N['GND'] if r=='U801'}==grounds|{'1C17','1B18','1A19'}
 ram=list(csv.DictReader((ROOT/'reference/micron-ddr-electrical-review.csv').open()));assert len(ram)==200
 for name,net in [('VDD1','VCC_1V8'),('VDD2','VDD_DDR_1V1'),('VDDQ','VDD_DDR_0V6'),('VSS','GND')]:
  for row in ram:
   if row['resolved_name']==name:on('U901',row['ball'],net)
 bus=list(csv.DictReader((ROOT/'reference/ddr-bus-map.csv').open()));assert len(bus)==65
 for row in bus:exact(row['net'],f"U801:{row['processor_ball']}",f"U901:{row['ram_ball']}")
 for row in csv.DictReader((ROOT/'reference/ram-local-bypass-plan.csv').open()):
  on(row['reference'],'1',row['rail']);on(row['reference'],'2','GND')
  assert C[row['reference']].findtext('value')==row['value']
  assert float(F(row['reference'])['Voltage Rating'].rstrip('V'))>=3*{'VCC_1V8':1.8,'VDD_DDR_1V1':1.1,'VDD_DDR_0V6':0.6}[row['rail']],row   # >= 3x rail
 exact('DDR_VDDQ_SW','U902:3','L902:1');exact('DDR_VDDQ_FB','U902:5','R905:2','R906:1','C959:2')
 subset('VDD_DDR_0V6','L902:2','C956:1','C957:1','C958:1','R903:1','R905:1','C959:1')
 exact('DDR_VDDQ_EN','U902:1','R907:2','R908:1','C960:1')
 exact('PMIC_SW3','U501:25','L901:1');exact('DDR_FB','U501:27','R901:2','R902:1')
 on('U501','26','VDD_DDR_1V1');exact('DDR_SOC_RZQ','U801:1F3','R904:1')
 connected('U501',{'5V_MAIN':'10 11 24 30 33 45 54 66','3V3_MAIN':'4 22 57','GND':'16 17 40 47 56 62 63 69','LOGIC_FB':'13','GPU_FB':'8','NPU_FB':'64','PMIC_CPU_EN':'60','VCC_1V8':'59','VCCA1V8_PMU':'3','VCCIO_SD':'29','VCC3V3_PMU':'31','VDDA0V9_PMU':'20','VCCA_1V8':'5','VDDA_0V9':'21'})
 for pin in ['6','23','28','55','58']:
  ps=N[B[('U501',pin)]];assert len(ps)==2 and any(r.startswith('C') and p=='1' for r,p in ps)
 exact('MCU_PWRON_KICK','U201:43','R508:1')
 subset('RK_RESET_N','U501:67','U801:AG38','Q801:3','Q1201:3','SW802:1','R501:2','C513:1')
 exact('PMIC_I2C_SCL','U501:1','U801:AJ37','R502:2','U1001:A3');exact('PMIC_I2C_SDA','U501:2','U801:AK38','R503:2','U1001:B1')
 connected('U1001',{'5V_MAIN':'D1 D2 E1 E2','GND':'A1 B2 B3 B4 C1 C2 C3 C4','CPU_SW':'D3 D4 E3 E4','CPU_FB':'A4','PMIC_CPU_EN':'A2'})
 exact('CPU_FB','U1001:A4','R1401:2','C1441:2','R1411:2');on('R1411','1','VDD_CPU');on('L1001','2','VDD_CPU')
 exact('MCU_MAIN5V_EN','U201:45','R704:1');exact('MAIN5V_GOOD','U701:4','R706:2','U201:46')
 subset('MAIN3V3_GOOD','U602:4','U201:44','U2003:1');on('U602','5','+3V3')
 exact(B[('U701','7')],'U701:7','C701:1');exact(B[('U701','6')],'U701:6','C701:2','L701:1')
 connected('U701',{'ISO_12V':'8','GND':'3 9'});connected('U401',{'ISO_12V':'2 3'});on('U201','4','+3V3');on('U601','5','3V3_MAIN')
 # Memory and host interfaces checked against manufacturer pin tables and reference.
 for net,pin in {'EMMC_D0':'A3','EMMC_D1':'A4','EMMC_D2':'A5','EMMC_D3':'B2','EMMC_D4':'B3','EMMC_D5':'B4','EMMC_D6':'B5','EMMC_D7':'B6','EMMC_CMD':'M5','EMMC_CLK':'M6','EMMC_STROBE':'H5','EMMC_RESET_N':'K5'}.items():on('U1101',pin,net)
 exact('EMMC_CLK_SOC','U801:A29','R1103:1');subset('EMMC_CLK','R1103:2','TP1101:1')
 connected('J1201',{'GND':'5 6','RECOVERY_VBUS':'1','RECOVERY_PORT_D_P':'3','RECOVERY_PORT_D_N':'2'});nc('J1201','4')
 assert not any(r in ['U401','U701'] for r,p in N['RECOVERY_VBUS'])
 connected('U1301',{'GND':'40 49','ETH_0V95':'8 28 47','ETH_PCIE_0V95':'37','ETH_3V3':'29 43 46','ETH_ANALOG_0V95':'11 16 22','ETH_ANALOG_3V3':'15 19 33','ETH_XTAL_3V3':'34','ETH_CORE_EN':'6','ETH_PERST_N':'36','ETH_PCIE_RXP':'41','ETH_PCIE_RXN':'42','ETH_PCIE_TXP':'38','ETH_PCIE_TXN':'39','ETH_REFCLK_P':'44','ETH_REFCLK_N':'45'})
 for pin in ['4','5','7']:nc('U1301',pin)
 for ref,src,dst in [('C1601','PCIE_SOC_TXP','ETH_PCIE_RXP'),('C1602','PCIE_SOC_TXN','ETH_PCIE_RXN'),('C1603','ETH_PCIE_TXP','PCIE_SOC_RXP'),('C1604','ETH_PCIE_TXN','PCIE_SOC_RXN')]:on(ref,'1',src);on(ref,'2',dst)
 for i,(ct,p,n,cp,cc,cn,rp,rn) in enumerate([('1','2','3','23','24','22','1','2'),('4','5','6','20','21','19','3','6'),('7','8','9','17','18','16','4','5'),('10','11','12','14','15','13','7','8')]):
  connected('T1701',{f'ETH_CT{i}':ct,f'ETH_MDI{i}_P':p,f'ETH_MDI{i}_N':n,f'CABLE_MDI{i}_P':cp,f'CABLE_MDI{i}_N':cn,'POE_PAIR'+['12','36','45','78'][i]:cc})
  on('J1701',rp,f'CABLE_MDI{i}_P');on('J1701',rn,f'CABLE_MDI{i}_N')
 on('J1701','SH','CHASSIS')
 # TPS23730 (PMP22477): straps tie APD/EMPS/EA_DIS/PSRS to RTN and DTHR/DT to VB; PPD to VSS; SCDIS open = parallel grant pins.
 connected('U1710',{'POE_VDD':'23','POE_VSS':'19 27 28 47','POE_RTN':'2 5 7 8 9 11 36 39 45 46','POE_TPH':'13','POE_TPL':'14','POE_BT':'12','POE_VCC':'42','POE_VB':'3 31 37'});nc('U1710','18')
 on('R1771','1','POE_VDD');on('R1771','2',B[('U1710','24')]);assert F('R1771')['MPN']=='RC0603FR-0725K5L'   # DEN 25.5k
 for r,pin,mpn in [('R1768','21','CRCW080531R6FKEA'),('R1769','20','CRCW0805130RFKEA')]:on(r,'1','POE_VSS');on(r,'2',B[('U1710',pin)]);assert F(r)['MPN']==mpn   # Class 6 CLSA/CLSB
 on('R1801','1','POE_VCC');on('R1802','1','POE_VCC');on('R1803','1','POE_VB')   # BT pin abs max 6.5 V: its opto hangs off VB
 for i,sig in enumerate(['TPH','TPL','BT']):
  ref=f'U{1801+i}';on(ref,'2',f'POE_{sig}');on(ref,'3','GND');on(ref,'4',f'POE_{sig}_N');on('U201',str(22+i),f'POE_{sig}_N')
 connected('U1901',{'ISO_12V':'4 5 6','GND':'2 3 15','MODEM_BUCK_SW':'11 12','MODEM_BUCK_FB':'7','MODEM_BUCK_BOOT':'13','MODEM_BUCK_COMP':'8','MODEM_BUCK_SS':'9','MODEM_BUCK_EN':'10','MODEM_BUCK_RT':'1','MODEM_BUCK_GOOD':'14'})
 exact('MODEM_BUCK_SW','U1901:11','U1901:12','L1901:1','C1901:2');exact('MODEM_BUCK_BOOT','U1901:13','C1901:1')
 exact('MODEM_BUCK_FB','U1901:7','R1901:2','R1902:1');on('R1901','1','MODEM_3V7_RAW');on('R1902','2','GND')
 connected('U1902',{'MODEM_3V7_RAW':'5','MODEM_VCC':'6','GND':'8','MODEM_FUSE_EN':'1','MODEM_FUSE_OVLO':'2','MODEM_SWITCH_GOOD':'3','MODEM_FUSE_PGTH':'4','MODEM_FUSE_DVDT':'7','MODEM_FUSE_ILM':'9'});nc('U1902','10')
 connected('U1903',{'MODEM_RAIL_GOOD':'1','GND':'2','+3V3':'3 6','MODEM_MON_CT':'4','MODEM_MON_SENSE':'5'})
 exact('MODEM_MON_CT','U1903:4','R1926:2');on('R1926','1','+3V3')
 connected('U1904',{'MCU_MODEM_POWER_EN':'2','GND':'3','MODEM_DISCHARGE_GATE':'4','+3V3':'5'})
 connected('Q1901',{'MODEM_DISCHARGE_GATE':'1','GND':'2','MODEM_DISCHARGE_DRAIN':'3'});on('R1924','1','MODEM_VCC');on('R1924','2','MODEM_DISCHARGE_DRAIN')
 connected('U201',{'MCU_MODEM_POWER_EN':'40','MODEM_RAIL_GOOD':'25','MODEM_SWITCH_GOOD':'26','MODEM_BUCK_GOOD':'27'})
 connected('U2001',{'+3V3':'1 6 10','GND':'5 9 11 20 21','MODEM_USB_OE_N':'2','MODEM_AC_TXP':'3','MODEM_AC_TXN':'4','MODEM_USB_RXP':'7','MODEM_USB_RXN':'8','MODEM_PORT_TXP':'17','MODEM_PORT_TXN':'16','MODEM_PORT_RXP':'19','MODEM_PORT_RXN':'18'})
 connected('U2002',{'+3V3':'10','GND':'5 9','MODEM_USB_OE_N':'6','/Modem USB isolation/MODEM_USB_MUX_D_P':'8','/Modem USB isolation/MODEM_USB_MUX_D_N':'7','MODEM_USB_PORT_D_P':'1','MODEM_USB_PORT_D_N':'2'})
 connected('U2003',{'MAIN3V3_GOOD':'1','MODEM_RAIL_GOOD':'2','GND':'3','MODEM_USB_VALID':'4','+3V3':'5'})
 for i,pol in enumerate(['P','N']):on(f'R{2004+i}','1',f'MODEM_USB_D_{pol}');on(f'R{2004+i}','2',f'/Modem USB isolation/MODEM_USB_MUX_D_{pol}')
 for i,pol in enumerate(['P','N']):on(f'C{2001+i}','1',f'MODEM_USB_SOC_TX{pol}');on(f'C{2001+i}','2',f'MODEM_AC_TX{pol}')
 connected('J2001',{'MODEM_VCC':'2 4 70 72 74','GND':'3 5 11 27 33 39 45 51 57 71 73','MODEM_OFF_N':'6','MODEM_RESET_N':'67','MODEM_USB_PORT_D_P':'7','MODEM_USB_PORT_D_N':'9','MODEM_PORT_TXN':'29','MODEM_PORT_TXP':'31','MODEM_PORT_RXN':'35','MODEM_PORT_RXP':'37','SIM1_RESET_MODEM':'30','SIM1_CLK_MODEM':'32','SIM1_DATA_MODEM':'34','SIM1_VCC':'36','M2_PIN20':'20','M2_PIN22':'22','M2_PIN24':'24','M2_PIN38':'38','M2_PIN68':'68'})
 nc('J2001','66');connected('J2002',{'SIM1_VCC':'1','SIM1_RESET':'2','SIM1_CLK':'3','SIM1_DATA':'6','GND':'4 9 10 11 12'})
 for pin in ['5','7','8']:nc('J2002',pin)
 for pin,ref in [('24','R2011'),('38','R2012'),('68','R2013'),('20','R2016'),('22','R2017')]:
  assert C[ref].find('property[@name="dnp"]') is not None,ref
  on(ref,'2',f'M2_PIN{pin}')
 exact('MODEM_RESET_N','Q301:3','J102:3','J2001:67');subset('MODEM_OFF_N','Q302:3','J102:4','J2001:6','R2018:2');on('R2018','1','MODEM_VCC')
 default_dnp={r for r,c in C.items() if c.find('property[@name="dnp"]') is not None}
 # 2026-11-22 bring-up additions: MCU link, sensing, aux power path, boot media, eSIM and test pads.
 connected('U201',{'ADC_AUX_12V':'11','ADC_5V_MAIN':'12','ADC_3V3_MAIN':'15','ADC_MODEM_VCC':'16','ADC_MODEM_ILM':'17','ADC_NTC_MODEM':'18','ADC_NTC_POWER':'21','MCU_LINK_TX':'30','MCU_LINK_RX':'31','MON_I2C_SCL':'47','MON_I2C_SDA':'48','MON_ALERT_N':'2','LED_PWR_N':'28','LED_SYS_N':'37','LED_WAN_N':'38','LED_FAULT_N':'39','MCU_HEALTH_IN':'1','MCU_ETH_POWER_EN':'41','MCU_PROCESSOR_RESET_ASSERT':'9'})
 connected('U2201',{'GND':'1 3','SOC_LINK_TX':'2','MCU_LINK_RX':'4','+3V3':'5'});connected('U2202',{'GND':'1 3','MCU_LINK_TX':'2','SOC_LINK_RX':'4','3V3_MAIN':'5'})
 on('U801','B22','SOC_LINK_TX');on('U801','A22','SOC_LINK_RX');on('R2213','1','MODEM_FUSE_ILM');on('R2213','2','ADC_MODEM_ILM')
 for q,u,src,tag in [('Q2101','U2101','AUX_12V_IN','AUX'),('Q2102','U2102','ISO_12V_PSU','PSU')]:
  connected(q,{src:'1 2 3',f'{tag}_DIODE_GATE':'4','ISO_12V_BUS':'5'});connected(u,{src:'3 6','ISO_12V_BUS':'4',f'{tag}_DIODE_GATE':'5','GND':'2'})
 on('R2101','1','ISO_12V_BUS');on('R2101','2','ISO_12V');connected('U2103',{'ISO_12V_BUS':'10','ISO_12V':'8 9','+3V3':'6','GND':'1 2 7'})
 assert not any(r in ['U701','U401','U1901'] for r,p in N['ISO_12V_PSU']|N['ISO_12V_BUS'])
 assert {'C1729','D1711','R1775'}<={r for r,p in N['ISO_12V_PSU']}
 connected('U2301',{'FSPI_CS0_N':'1','FSPI_D1':'2','FSPI_WP_N':'3','GND':'4 9','FSPI_D0':'5','FSPI_CLK':'6','FSPI_D3':'7','VCC_1V8':'8'})
 for ball,net in {'1A15':'FSPI_CLK','1A17':'FSPI_D0','1A18':'FSPI_D1','1B17':'FSPI_CS0_N','1C15':'FSPI_D3','1B16':'EMMC_RESET_N'}.items():on('U801',ball,net)
 connected('J2301',{'SD_D2':'1','SD_D3':'2','SD_CMD':'3','SD_VDD':'4','SD_CLK':'5','GND':'6 10 SH','SD_D0':'7','SD_D1':'8','SDMMC0_DET':'9'})
 for pin,ref in [('48','R2311'),('46','R2312'),('44','R2313'),('42','R2314')]:exact(f'M2_PIN{pin}',f'J2001:{pin}',f'{ref}:1')
 for ref in ['J2301','R2304','U2302','D2301','D2302','U2303','R2311','R2312','R2313','R2314','C2305']:assert ref in default_dnp,ref
 tps=[r for r in C if r.startswith('TP24')];assert len(tps)==80
 for r in tps:assert B[(r,'1')]==C[r].findtext('value'),(r,B[(r,'1')])
 profiles=json.loads((ROOT/'reference/modem-assembly-profiles.json').read_text())
 for profile in profiles:
  populated=set(profile['populate_optional']);assert not profile['released'];graph={}
  for ref,c in C.items():
   if ref in default_dnp and ref not in populated:continue
   if c.findtext('value').split()[0]!='0R':continue
   aa,bb=B[(ref,'1')],B[(ref,'2')];graph.setdefault(aa,set()).add(bb);graph.setdefault(bb,set()).add(aa)
  reachable={'MODEM_VCC'};pending=['MODEM_VCC']
  while pending:
   for nxt in graph.get(pending.pop(),set())-reachable:reachable.add(nxt);pending.append(nxt)
  actual={pin for pin in ['2','4','24','38','68','70','72','74'] if B[('J2001',pin)] in reachable}
  assert actual==set(profile['VCC_contacts']),(profile['model'],actual)
  if profile['vendor']=='Quectel':assert not populated & {'R2011','R2012','R2013','R2016','R2017','C2036','C2037','C2038'}
 # Prove TI retained net partitions; intentional deleted evaluation hardware is excluded.
 golden=[]
 for source in ['input']:
  old=export(ROOT/f'reference/tida-import/{source}.kicad_sch',directory/f'poe-{source}.xml')
  removed=({'T1','J1','J2','TP1','TP2','TP3','TP4','TP5'}|{f'{k}{n}' for k in 'RC' for n in range(1,7)}|{'R7','R8'}) if source=='input' else set()
  rename=lambda r:re.sub(r'\d+$',lambda m:str(1700+int(m[0])),r)
  live={c.get('ref') for c in old.findall('./components/comp') if c.get('ref') not in removed and rename(c.get('ref')) in C}
  groups={frozenset((rename(n.get('ref')),n.get('pin')) for n in net.findall('node') if n.get('ref') in live) for net in old.findall('./nets/net')}-{frozenset()}
  allpins=set().union(*groups);projected={frozenset(ps & allpins) for ps in N.values() if ps & allpins}
  assert projected==groups,(source,'Native TI net partition changed',groups-projected,projected-groups)
  golden.append({'source':source,'retained_components':len(live),'pins':len(allpins),'net_groups':len(groups)})
 # PMP22477 PD + flyback (native Altium import): same partition after the documented drops, straps and ties.
 from build_poe_tps23730 import import_netlist, groups as pmp_groups
 pmp={frozenset(v) for v in pmp_groups(import_netlist()).values()}
 allpins=set().union(*pmp);projected={frozenset(ps & allpins) for ps in N.values() if ps & allpins}
 assert projected==pmp,('PMP22477 net partition changed',pmp-projected,projected-pmp)
 assert {r for r,p in allpins}=={r for r,c in C.items() if c.find('sheetpath').get('names')=='/PoE PD and isolated 12V flyback/'}-{'R1775'}
 golden.append({'source':'PMP22477 power stage','retained_components':len({r for r,p in allpins}),'pins':len(allpins),'net_groups':len(pmp)})
 # Every assigned footprint must contain exactly the model's electrical pads.
 policy=json.loads((ROOT/'footprint-policy.json').read_text())
 holds=set(policy['land_pattern_release_holds'])
 assert all(c.findtext('footprint') for c in C.values()), 'Unassigned footprint'
 assert {r:c.findtext('footprint') for r,c in C.items()}==policy['assignments'], 'Footprint policy drift'
 for ref,c in C.items():
  fp=c.findtext('footprint')
  if not fp:continue
  lib,name=fp.split(':');base=ROOT if lib in ['Recovery','Appliance','PoE'] else Path('/Applications/KiCad/KiCad.app/Contents/SharedSupport/footprints')
  text=(base/(lib+'.pretty')/(name+'.kicad_mod')).read_text();pads={aa or bb for aa,bb in re.findall(r'\(pad (?:"([^\"]*)"|([^\s)]+))',text)}-{''}
  src=c.find('libsource');assert pads==libs[(src.get('lib'),src.get('part'))],(ref,fp,'Pad identities differ')
 for path in ROOT.glob('*.kicad_sch'):
  ids=re.findall(r'\(uuid "([^\"]+)"\)',path.read_text());assert len(ids)==len(set(ids)),path
 return {'date':'2026-10-21','scope':'Full appliance native connectivity and footprint identities; PCB is unrouted. No manufacturing release or physical qualification.','components':len(C),'nets':len(N),'accounted_major_native_pins':counts,'manufacturer_DDR_pairs':len(bus),'TI_golden_topology':golden,'default_DNP':sorted(default_dnp),'footprint_release_holds':sorted(holds),'modem_profiles_released':0,'assigned_footprints_with_exact_pad_parity':len(C)}
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path);p.add_argument('--kicad-cli',default=CLI);a=p.parse_args()
 global_cli=a.kicad_cli
 globals()['CLI']=global_cli
 with tempfile.TemporaryDirectory() as temp:
  directory=a.output or Path(temp);directory.mkdir(parents=True,exist_ok=True)
  project=json.loads((ROOT/'appliance.kicad_pro').read_text());assert not project.get('erc',{}).get('erc_exclusions')
  subprocess.run([CLI,'sch','erc','--severity-all','--exit-code-violations','--format','json','--output',str(directory/'erc.json'),str(ROOT/'appliance.kicad_sch')],check=True,capture_output=True)
  erc=json.loads((directory/'erc.json').read_text());assert not any(sh.get('violations') for sh in erc['sheets'])
  report=validate(export(ROOT/'appliance.kicad_sch',directory/'appliance.xml'),directory);report['ERC_violations']=0
  (directory/'capture-report.json').write_text(json.dumps(report,indent=2)+'\n')
  print(f"PASS: {report['components']} components, {report['nets']} nets, zero full ERC violations, native pin coverage, DDR map, TI topology, modem assembly isolation and assigned-footprint pad parity.")
  print(f"Engineering capture complete. {len(report['footprint_release_holds'])} BGA footprint release holds; four modem profiles and physical hardware remain unqualified.")
if __name__=='__main__':main()
