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
    assert nets['3V3_MAIN']=={('C602','1'),('C603','1'),('L601','2'),('R601','1'),('U601','5'),('U501','22'),('U501','4'),('C519','1'),('C524','1'),('U501','57'),('C538','1'),('U801','1H18'),('C817','1')},nets['3V3_MAIN']
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
    assert nets['PMIC_INT_N']=={('U501','7'),('R504','2'),('U801','1R19')}
    assert nets['RK_RESET_N']=={('U501','67'),('R501','2'),('C513','1'),('U801','AG38'),('SW802','1')}
    assert nets['PMIC_SLEEP']=={('U501','49'),('R505','1'),('U801','1P19')}
    assert len({p for r,p in nets['GND'] if r=='U801'})==187
    assert nets['VDD_LOGIC']=={('U501','13'),('L501','2'),('C501','1'),('C502','1'),('C503','1')}|{('U801',b) for b in ['1H7','1H8','1H9','1H10','1J7','1J10','1K7','1K10','1L7']}
    assert nets['VDD_GPU']=={('U501','8'),('L502','2'),('C505','1'),('C506','1'),('C507','1')}|{('U801',b) for b in ['1L8','1L9','1M7','1M8','1M9']}
    assert nets['VCC3V3_PMU']=={('R501','1'),('U501','31'),('C517','1'),('C518','1'),('R502','1'),('R503','1'),('R504','1'),('U801','1P16'),('U801','1N15'),('C811','1'),('C812','1')}
    assert nets['VDDA0V9_PMU']=={('U501','20'),('C522','1'),('C523','1'),('U801','1N16'),('U801','1P17')}|{(f'C{n}','1') for n in [801, 802, 809, 810]}
    assert nets['VCCA1V8_PMU']=={('U501','3'),('C525','1'),('C526','1'),('U801','1N18')}|{(f'C{n}','1') for n in [803, 804]}
    assert nets['VDDA_0V9']=={('U501','21'),('C520','1'),('C521','1'),('U801','1H5')}|{(f'C{n}','1') for n in [805, 806]}|{('FB801','1'),('C813','1')}
    assert nets['VCCA_1V8']=={('U501','5'),('C527','1'),('C528','1'),('U801','1H4')}|{(f'C{n}','1') for n in [807, 808]}|{('FB802','1'),('C814','1'),('U801','1D15'),('U801','1D16'),('C818','1'),('C819','1'),('R801','1')}
    assert {(f'C{n}','2') for n in range(801,813)} <= nets['GND']
    assert nets['USB_AVDD_0V9']=={('FB801','2'),('U801','1J17'),('C815','1')}
    assert nets['USB_AVDD_1V8']=={('FB802','2'),('U801','1H16'),('C816','1')}
    assert {('C813','2'),('C814','2'),('C815','2'),('C816','2'),('C817','2'),('C818','2'),('C819','2'),('C820','2')} <= nets['GND']
    for ref in ['FB801','FB802']:
        comp=next(c for c in tree.findall('./components/comp') if c.get('ref')==ref)
        fields={f.get('name'):f.text for f in comp.findall('./fields/field')}
        assert fields['MPN']=='MPZ1608S121ATAH0' and fields['DCR Maximum']=='45mOhm'
    assert {('SW801','2'),('SW802','2')} <= nets['GND']
    assert nets['SARADC_BOOT_KEY']=={('U801','1D17'),('R801','2'),('C820','1'),('SW801','1')}
    assert len(tree.findall('./components/comp'))==142
print('PASS: appliance restart GPIO connection and 142-component capture; not full ERC.')
