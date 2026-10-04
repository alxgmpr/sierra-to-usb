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
    assert nets['RK_RESET_N']=={('U501','67'),('R501','2'),('C513','1'),('U801','AG38'),('SW802','1'),('Q801','3')}
    assert nets['PMIC_SLEEP']=={('U501','49'),('R505','1'),('U801','1P19')}
    assert len({p for r,p in nets['GND'] if r=='U801'})==187
    assert nets['VDD_LOGIC']=={('U501','13'),('L501','2'),('C501','1'),('C502','1'),('C503','1')}|{('U801',b) for b in ['1H7','1H8','1H9','1H10','1J7','1J10','1K7','1K10','1L7']}|{(f'C{n}','1') for n in range(825,832)}
    assert nets['VDD_GPU']=={('U501','8'),('L502','2'),('C505','1'),('C506','1'),('C507','1')}|{('U801',b) for b in ['1L8','1L9','1M7','1M8','1M9']}|{(f'C{n}','1') for n in range(832,837)}
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
    assert nets['SARADC_BOOT_KEY']=={('U801','1D17'),('R801','2'),('C820','1'),('SW801','1'),('Q802','3')}
    assert nets['MCU_PROCESSOR_RESET_ASSERT']=={('U201','21'),('R802','1')}
    base=next(v for v in nets.values() if ('Q801','1') in v)
    assert base=={('Q801','1'),('R802','2'),('R803','1')}
    assert {('Q801','2'),('R803','2')} <= nets['GND']
    assert nets['MCU_PROCESSOR_RECOVERY_ASSERT']=={('U201','42'),('R804','1')}
    recovery_base=next(v for v in nets.values() if ('Q802','1') in v)
    assert recovery_base=={('Q802','1'),('R804','2'),('R805','1')}
    assert {('Q802','2'),('R805','2')} <= nets['GND']
    assert nets['VDD_NPU']=={('L504','2'),('C541','1'),('C542','1'),('R512','1')}|{(f'C{n}','1') for n in range(821,825)}|{('U801',b) for b in ['1G15','1H14','1H15','1J14','1J15']}
    assert {('C541','2'),('C542','2')}|{(f'C{n}','2') for n in range(821,825)} <= nets['GND']
    assert {(f'C{n}','2') for n in range(825,837)} <= nets['GND']
    core_ids=__import__('re').findall(r'\(uuid "([^\"]+)"\)',(root/'core-power.kicad_sch').read_text())
    assert len(core_ids)==len(set(core_ids))
    for ref,mpn in {**{f'C{n}':'CL10A475KA8NQNC' for n in [826,827,828,833]},**{f'C{n}':'CL10B104KA8NNNC' for n in [825,832]},**{f'C{n}':'CL32B226KAJNNNE' for n in [829,831,834,836]},**{f'C{n}':'CL31B106KAHNNNE' for n in [830,835]}}.items():
        component=next(c for c in tree.findall('./components/comp') if c.get('ref')==ref)
        fields={f.get('name'):f.text for f in component.findall('./fields/field')}
        assert fields['MPN']==mpn and fields['Voltage Rating']=='25V'
    assert len(tree.findall('./components/comp'))==176
    assert {('U901',r['ball']) for r in __import__('csv').DictReader((root/'reference/micron-ddr-electrical-review.csv').open()) if r['resolved_name']=='VSS'} <= nets['GND']
    ram_rows=list(__import__('csv').DictReader((root/'reference/micron-ddr-electrical-review.csv').open()))
    assert {p for p in nets['VCC_1V8'] if p[0]=='U901'}=={('U901',r['ball']) for r in ram_rows if r['resolved_name']=='VDD1'}
    assert {('U901','G2'),('U901','T2')} <= nets['GND']
    assert nets['PMIC_SW3']=={('U501','25'),('L901','1')}
    assert nets['DDR_FB']=={('U501','27'),('R901','2'),('R902','1')}
    assert nets['VDD_DDR_1V1']=={('U501','26'),('L901','2'),('C901','1'),('C902','1'),('R901','1')}|{('U901',r['ball']) for r in ram_rows if r['resolved_name']=='VDD2'}
    assert {('C901','2'),('C902','2'),('C903','2'),('R902','2')} <= nets['GND']
    assert {('U501','24'),('C903','1')} <= nets['5V_MAIN']
    assert nets['VDD_DDR_0V6']=={('R903','1')}|{('U901',r['ball']) for r in ram_rows if r['resolved_name']=='VDDQ'}
    zq=next(p for p in nets.values() if ('U901','A5') in p)
    assert zq=={('U901','A5'),('R903','2')}
print('PASS: appliance restart GPIO connection and 176-component capture; not full ERC.')
