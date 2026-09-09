"""Verify boot straps and regulator-control endpoints using physical balls."""
from pathlib import Path
from xml.etree import ElementTree as ET
import json
import subprocess
import tempfile

ROOT=Path(__file__).resolve().parents[1]
CLI='/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli'


def check(root=ROOT):
    with tempfile.TemporaryDirectory(prefix='processor-control-check-') as directory:
        xml=Path(directory)/'nets.xml'
        subprocess.run([CLI,'sch','export','netlist','--format','kicadxml','-o',str(xml),
                        str(root/'cad/full-adapter.kicad_sch')],check=True,capture_output=True)
        tree=ET.parse(xml)
        nets={n.get('name'):{(p.get('ref'),p.get('pin')) for p in n.findall('node')}
              for n in tree.findall('.//nets/net')}
        parts={c.get('ref'):c for c in tree.findall('.//components/comp')}
        assert nets['FLASH_VOL_SEL']=={('U1','AG25'),('R560','2')}
        assert nets['SD_CARD_DET_L']=={('U1','Y22'),('R562','2')}
        assert nets['SOC_TSHUT_L']=={('U1','AG26'),('R561','1')}
        assert {('U1','AH27'),('U5','67'),('R561','2'),('C560','1')} <= nets['SYS_RESET_L']
        assert ('C560','2') in nets['GND']
        assert {('U1','AF24'),('U4','A3'),('R490','1')} <= nets['I2C0_SCL_PMIC']
        assert {('U1','AB21'),('U4','B1'),('R491','1')} <= nets['I2C0_SDA_PMIC']
        assert ('R492','1') in nets['VCC1V8_PMU'] and ('R493','1') in nets['VCC1V8_PMU']
        assert ('U1','W19') in nets['VCC1V8_PMU']
        assert ('U1','Y20') in nets['VCC3V3_PMU']
        for ref in ['R560','R562']:
            assert (ref,'1') in nets['VCC3V3_PMU']
            assert parts[ref].findtext('value')=='10kR 1%'
            fields={f.get('name'):f.text for f in parts[ref].findall('fields/field')}
            assert fields['LCSC']=='C25744'
        assert parts['R561'].findtext('value')=='0R'
        fields={f.get('name'):f.text for f in parts['R561'].findall('fields/field')}
        assert (fields['MPN'],fields['LCSC'])==('0402WGF0000TCE','C17168')
        assert parts['C560'].findtext('value')=='100nF'
        assert nets['SOC_UART2_RX_1V8']=={('U1','AC20'),('TP560','1')}
        assert nets['SOC_UART2_TX_1V8']=={('U1','AH24'),('TP561','1')}
        assert ('TP562','1') in nets['GND']
        for ref in ['TP560','TP561','TP562']:
            assert parts[ref].findtext('footprint')=='TestPoint:TestPoint_Pad_D1.0mm'
            assert parts[ref].find("property[@name='exclude_from_bom']") is not None
    return {'status':'PROCESSOR_CONTROL_CAPTURE_CHECKPOINT_NOT_RELEASE',
            'PMIC_I2C_host_connected':True,'storage_voltage_strap_integrated':True,
            'thermal_watchdog_reset_path_integrated':True,
            'console_external_interface_integrated':False,'power_good_restart_integrated':False}


if __name__=='__main__':
    result=check()
    (ROOT/'research/processor-control-validation.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
