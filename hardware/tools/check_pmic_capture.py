#!/usr/bin/env python3
"""Check captured PMIC rail and reset connectivity only; other PMIC circuitry is unfinished."""
from pathlib import Path
import subprocess, tempfile, xml.etree.ElementTree as E
root=Path(__file__).resolve().parents[1]
with tempfile.TemporaryDirectory() as tmp:
 net=Path(tmp)/'pmic.xml'
 subprocess.run(['/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli','sch','export','netlist','--format','kicadxml','--output',str(net),str(root/'pmic.kicad_sch')],check=True)
 tree=E.parse(net).getroot()
 nets={n.attrib['name']:{(v.attrib['ref'],v.attrib['pin']) for v in n.findall('node')} for n in tree.findall('.//nets/net')}
 expected={
 '5V_MAIN':{('U501','10'),('U501','11'),('C504','1'),('C508','1'),('U501','54'),('C512','1'),('U501','45'),('C514','1'),('U501','30'),('C516','1'),('R506','1'),('U501','66'),('C533','1'),('U501','33'),('C537','1')},
 '/PMIC_SW1':{('U501','12'),('L501','1')},
 '/PMIC_SW2':{('U501','9'),('L502','1')},
 '/VDD_LOGIC':{('U501','13'),('L501','2'),('C501','1'),('C502','1'),('C503','1')},
 '/VDD_GPU':{('U501','8'),('L502','2'),('C505','1'),('C506','1'),('C507','1')},
 '/PMIC_SW5':{('U501','53'),('L505','1')},
 '/VCC_1V8':{('U501','59'),('L505','2'),('C509','1'),('C510','1'),('C511','1')},
 '/RK_RESET_N':{('U501','67'),('R501','2'),('C513','1')},
 '/VCC3V3_PMU':{('R501','1'),('U501','31'),('C517','1'),('C518','1'),('R502','1'),('R503','1'),('R504','1')},
 'Net-(U501C-VREF)':{('U501','46'),('C515','1')},
 '3V3_MAIN':{('U501','22'),('C519','1'),('U501','4'),('C524','1'),('U501','57'),('C538','1')},
 '/VDDA_0V9':{('U501','21'),('C520','1'),('C521','1')},
 '/VDDA0V9_PMU':{('U501','20'),('C522','1'),('C523','1')},
 '/VCCA1V8_PMU':{('U501','3'),('C525','1'),('C526','1')},
 '/VCCA_1V8':{('U501','5'),('C527','1'),('C528','1')},
 '/VCCIO_SD':{('U501','29'),('C529','1'),('C530','1')},
 '/PMIC_I2C_SCL':{('U501','1'),('R502','2')},
 '/PMIC_I2C_SDA':{('U501','2'),('R503','2')},
 '/PMIC_INT_N':{('U501','7'),('R504','2')},
 '/PMIC_SLEEP':{('U501','49'),('R505','1')},
 '/PMIC_VDC':{('U501','61'),('R506','2'),('R507','1'),('C531','1')},
 '/PMIC_PWRON_N':{('U501','52'),('C532','1'),('Q501','3')},
 'MCU_PWRON_KICK':{('R508','1')},
 'Net-(Q501-B)':{('Q501','1'),('R508','2'),('R509','1')},
 '/PMIC_INTERNAL_CPVDD':{('U501','38'),('C534','1')},
 '/PMIC_INTERNAL_1V8A':{('U501','44'),('C535','1')},
 '/PMIC_INTERNAL_1V8D':{('U501','48'),('C536','1')},
 '/PMIC_CPP':{('U501','37'),('C539','1')},
 '/PMIC_CPN':{('U501','36'),('C539','2')},
 '/PMIC_INTERNAL_CPVSS':{('U501','35'),('C540','1')},
 '/UNUSED_CODEC_LRCLK':{('U501','14'),('R510','1')},
 '/UNUSED_CODEC_BCLK':{('U501','15'),('R511','1')},
 'GND':{(f'C{n}','2') for n in range(501,539)}|{('C540','2'),('U501','16'),('U501','17'),('R510','2'),('R511','2')}|{('U501','47'),('U501','69'),('U501','62'),('U501','63'),('U501','40'),('R505','2'),('R507','2'),('Q501','2'),('R509','2')},
 }
 for name,pins in expected.items():assert nets[name]==pins,(name,nets[name],pins)
 comps=tree.findall('.//components/comp');assert len(comps)==56
 for c in comps:
  fields={f.attrib['name']:f.text for f in c.findall('fields/field')}
  assert fields.get('MPN'),c.attrib['ref']
 print('PASS: PMIC captured rails: exact thirty-three-net membership and 56 MPNs. Remaining PMIC channels and management are incomplete; this is not full ERC or qualification.')
