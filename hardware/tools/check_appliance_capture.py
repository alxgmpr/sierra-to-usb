#!/usr/bin/env python3
"""Check appliance restart integration only; not full ERC or completion."""
from pathlib import Path
import subprocess, tempfile, xml.etree.ElementTree as E
root=Path(__file__).resolve().parents[1]
with tempfile.TemporaryDirectory() as tmp:
    path=Path(tmp)/'appliance.xml'
    subprocess.run(['/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli','sch','export','netlist','--format','kicadxml','--output',str(path),str(root/'appliance.kicad_sch')],check=True)
    tree=E.parse(path).getroot()
    net=next(n for n in tree.findall('./nets/net') if n.get('name')=='MCU_PWRON_KICK')
    pins={(n.get('ref'),n.get('pin')) for n in net.findall('node')}
    assert pins=={('U201','43'),('R508','1')},pins
    nets={n.get('name'):{(v.get('ref'),v.get('pin')) for v in n.findall('node')} for n in tree.findall('./nets/net')}
    assert nets['3V3_MAIN']=={('C602','1'),('C603','1'),('L601','2'),('R601','1'),('U601','5'),('U501','22'),('U501','4'),('C519','1'),('C524','1'),('U501','57'),('C538','1')},nets['3V3_MAIN']
    recovery=next(p for p in nets.values() if ('U201','4') in p)
    assert not recovery & nets['3V3_MAIN']
    assert ('U601','2') in nets['5V_MAIN'] and ('U501','66') in nets['5V_MAIN']
    en=next(p for name,p in nets.items() if name.endswith('/MAIN3V3_EN'))
    assert en=={('U601','8'),('R603','2'),('R604','1')},en
    assert ('R603','1') in nets['5V_MAIN']
    pg=next(p for name,p in nets.items() if name.endswith('/MAIN3V3_PG_5V'))
    assert pg=={('U601','1'),('U602','2'),('R605','2'),('R606','1')},pg
    assert ('U602','5') in recovery and ('C604','1') in recovery
    assert nets['MAIN3V3_GOOD']=={('U602','4'),('U201','44')},nets['MAIN3V3_GOOD']
    fb=next(p for name,p in nets.items() if name.endswith('/MAIN5V_FB'))
    assert fb=={('U701','2'),('R702','2'),('R703','1')},fb
    mode=next(p for name,p in nets.items() if name.endswith('/MAIN5V_MODE'))
    assert mode=={('U701','10'),('R701','1')},mode
    assert ('R702','1') in nets['5V_MAIN']
    assert {('U701','3'),('U701','9'),('R701','2'),('R703','2')} <= nets['GND']
    sw=next(p for name,p in nets.items() if name.endswith('/MAIN5V_SW'))
    assert sw=={('U701','6'),('C701','2'),('L701','1')},sw
    boot=next(p for p in nets.values() if ('U701','7') in p)
    assert boot=={('U701','7'),('C701','1')},boot
    ss=next(p for p in nets.values() if ('U701','5') in p)
    assert ss=={('U701','5'),('C702','1')},ss
    assert ('C702','2') in nets['GND']
    assert nets['ISO_12V']=={('U701','8'),('C703','1'),('C704','1'),('C705','1'),('U401','2'),('U401','3'),('C401','1')},nets['ISO_12V']
    assert {('C703','2'),('C704','2'),('C705','2')} <= nets['GND']
    assert nets['MCU_MAIN5V_EN']=={('U201','45'),('R704','1')},nets['MCU_MAIN5V_EN']
    main5en=next(p for p in nets.values() if ('U701','1') in p)
    assert main5en=={('U701','1'),('R704','2'),('R705','1')},main5en
    assert ('R705','2') in nets['GND']
    assert nets['MAIN5V_GOOD']=={('U701','4'),('R706','2'),('U201','46')},nets['MAIN5V_GOOD']
    assert ('R706','1') in recovery
    assert {('L701','2'),('C706','1'),('C707','1')} <= nets['5V_MAIN']
    assert {('C706','2'),('C707','2')} <= nets['GND']
    assert nets['PMIC_I2C_SCL']=={('U501','1'),('R502','2'),('U801','AJ37')}
    assert nets['PMIC_I2C_SDA']=={('U501','2'),('R503','2'),('U801','AK38')}
    assert nets['PMIC_SLEEP']=={('U501','49'),('R505','1'),('U801','1P19')}
    assert len({p for r,p in nets['GND'] if r=='U801'})==187
    assert nets['VDD_LOGIC']=={('U501','13'),('L501','2'),('C501','1'),('C502','1'),('C503','1')}|{('U801',b) for b in ['1H7','1H8','1H9','1H10','1J7','1J10','1K7','1K10','1L7','1N16']}
    assert nets['VDD_GPU']=={('U501','8'),('L502','2'),('C505','1'),('C506','1'),('C507','1')}|{('U801',b) for b in ['1L8','1L9','1M7','1M8','1M9']}
    assert nets['VCC3V3_PMU']=={('R501','1'),('U501','31'),('C517','1'),('C518','1'),('R502','1'),('R503','1'),('R504','1'),('U801','1P16'),('U801','1N15')}
    assert len(tree.findall('./components/comp'))==117
print('PASS: appliance restart GPIO connection and 117-component capture; not full ERC.')
