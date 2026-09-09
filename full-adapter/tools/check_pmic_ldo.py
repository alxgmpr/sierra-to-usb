"""Check actual exported RK809 LDO pins, rail identities and local bypass."""
from pathlib import Path
from xml.etree import ElementTree as ET
import json
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
CLI = '/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli'


def check(root=ROOT):
    with tempfile.TemporaryDirectory(prefix='pmic-ldo-check-') as directory:
        output=Path(directory)/'nets.xml'
        subprocess.run([CLI,'sch','export','netlist','--format','kicadxml','-o',str(output),
                        str(root/'cad/full-adapter.kicad_sch')],check=True,capture_output=True)
        tree=ET.parse(output)
        nets={n.get('name'):{(p.get('ref'),p.get('pin')) for p in n.findall('node')}
              for n in tree.findall('.//nets/net')}
        parts={p.get('ref'):p for p in tree.findall('.//components/comp')}
        # Fixed physical pin/output pairing from the RK809 package table.
        rails={'VDD0V9_IMAGE':('23','C401'),'VDD0V9_ANLG':('21','C402'),
               'VDD0V9_PMU':('20','C403'),'VCC3V3_CODEC':('28','C405'),
               'VCC_SDIO':('29','C406'),'VCC3V3_PMU':('31','C407'),
               'VCC1V8_ANLG':('3','C409'),'VCC1V8_PMU':('5','C410'),
               'VCC1V8_IMAGE':('6','C411')}
        for rail,(pin,cap) in rails.items():
            expected={('U5',pin),(cap,'1')}
            if rail=='VCC3V3_PMU':expected|={('R300','1'),('R494','1'),('R495','1')}
            if rail=='VCC1V8_PMU':expected|={('R492','1'),('R493','1')}
            processor_loads = {
                'VDD0V9_PMU': {('U1','V21'),('U1','V19'),('C500','1'),('C501','1'),('C508','1'),('C509','1')},
                'VCC1V8_PMU': {('U1','Y21'),('U1','W19'),('C502','1'),('C503','1'),('C511','1')},
                'VDD0V9_ANLG': {('U1','P11'),('C504','1'),('C505','1'),('U1','R20'),('U1','R21'),
                                ('C546','1'),('C547','1'),('C549','1'),('FB550','1'),('C550','1')},
                'VCC1V8_ANLG': {('U1','N10'),('C506','1'),('C507','1'),('U1','H22'),('C523','1'),
                                ('U1','R22'),('C548','1'),('FB551','1'),('C552','1')},
                'VCC3V3_PMU': {('U1','Y20'),('C510','1'),('R560','1'),('R562','1')},
                'VCC_SDIO': {('U1','L22'),('C525','1')},
            }
            expected |= processor_loads.get(rail, set())
            assert nets[rail]==expected,(rail,nets[rail]^expected)
        assert nets['VCC3V3_SYS']=={('U5','22'),('U5','30'),('U5','4'),
                                    ('C400','1'),('C404','1'),('C408','1'),
                                    ('U5','24'),('C420','1'),('C421','1'),
                                    ('U5','11'),('U5','10'),('U5','66'),
                                    ('C430','1'),('C431','1'),('C440','1'),('C441','1'),('C450','1'),('C451','1'),
                                    ('U5','54'),('U5','57'),('C460','1'),('C461','1'),('C466','1'),
                                    ('U5','33'),('C482','1'),('U5','45'),('C483','1'),('R496','1')}
        for n in range(400,412):
            ref=f'C{n}';part=parts[ref]
            assert (ref,'2') in nets['GND']
            assert part.findtext('value')=='1uF'
            assert part.findtext('footprint')=='Capacitor_SMD:C_0402_1005Metric'
            fields={f.get('name'):f.text for f in part.findall('fields/field')}
            assert (fields['MPN'],fields['LCSC'])==('CL05A105KA5NQNC','C52923')
        fields={f.get('name'):f.text for f in parts['U5'].findall('fields/field')}
        assert (fields['MPN'],fields['LCSC'])==('RK809-5','C2939628')
    return {'status':'PMIC_LDO_CAPTURE_CHECKPOINT_NOT_RELEASE','ldo_outputs':9,
            'input_groups':3,'bypass_capacitors':12,'cpu_enable_source':'U5 LDO6 pin 31',
            'processor_supply_loads_integrated':True,'IO_load_and_thermal_budget_closed':False}


if __name__=='__main__':
    result=check()
    (ROOT/'research/pmic-ldo-validation.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
