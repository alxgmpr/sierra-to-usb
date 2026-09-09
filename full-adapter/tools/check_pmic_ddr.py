"""Independent physical-node and divider-limit checks for RK809 BUCK3."""
from pathlib import Path
from xml.etree import ElementTree as ET
import json
import subprocess
import tempfile

ROOT=Path(__file__).resolve().parents[1]
CLI='/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli'


def check(root=ROOT):
    with tempfile.TemporaryDirectory(prefix='pmic-ddr-check-') as directory:
        output=Path(directory)/'nets.xml'
        subprocess.run([CLI,'sch','export','netlist','--format','kicadxml','-o',str(output),
                        str(root/'cad/full-adapter.kicad_sch')],check=True,capture_output=True)
        tree=ET.parse(output)
        nets={n.get('name'):{(p.get('ref'),p.get('pin')) for p in n.findall('node')}
              for n in tree.findall('.//nets/net')}
        parts={p.get('ref'):p for p in tree.findall('.//components/comp')}
        assert next(n for n in nets.values() if ('U5','25') in n)=={('U5','25'),('L420','1')}
        assert next(n for n in nets.values() if ('U5','27') in n)=={('U5','27'),('R420','2'),('R421','1')}
        expected={('U5','26'),('L420','2'),('R420','1'),('C422','1'),('C423','1'),('C424','1')}
        assert {p for p in nets['VCC_DDR'] if p[0] in {'U5','L420','R420','R421','C420','C421','C422','C423','C424'}}==expected
        assert ('R421','2') in nets['GND']
        for ref in ['C420','C421']:
            assert (ref,'1') in nets['VCC3V3_SYS']
        assert ('U5','24') in nets['VCC3V3_SYS']
        selected={'L420':('0.47uH','SPM5030T-R47M','C501964'),
                  'R420':('87.6kR 0.1%','RT0402BRD0787K6L','C852937'),
                  'R421':('100kR 0.1%','RT0402BRD07100KL','C852472')}
        selected.update({f'C{i}':('22uF','CL21A226MAYNNNE','C602037') for i in range(420,425)})
        for ref,(value,mpn,lcsc) in selected.items():
            p=parts[ref];f={x.get('name'):x.text for x in p.findall('fields/field')}
            assert (p.findtext('value'),f['MPN'],f['LCSC'])==(value,mpn,lcsc)
            if ref.startswith('C'):assert (ref,'2') in nets['GND']
        assert parts['L420'].findtext('footprint')=='full-adapter:L_TDK_SPM5030'
    # Worst opposing 25ppm/C coefficients, -40 to +85C versus 25C reference.
    # This arithmetic does not include load-transient/ripple or resistor aging.
    error=.001+25e-6*65
    minimum=.784*(1+87.6*(1-error)/(100*(1+error)))
    maximum=.816*(1+87.6*(1+error)/(100*(1-error)))
    assert 1.425 < minimum < 1.5008 < maximum < 1.575
    return {'status':'PMIC_DDR_CAPTURE_CHECKPOINT_NOT_RELEASE','nominal_V':1.5008,
            'static_V_with_initial_tolerance_and_TCR':[minimum,maximum],
            'temperature_range_C':[-40,85],
            'remaining_low_high_margin_V':[minimum-1.425,1.575-maximum],
            'ripple_transient_aging_qualified':False,'local_input_caps':2,'local_output_caps':3,
            'pmic_buck3_max_output_A':1.5,'upstream_power_integrated':False}


if __name__=='__main__':
    result=check()
    (ROOT/'research/pmic-ddr-validation.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
