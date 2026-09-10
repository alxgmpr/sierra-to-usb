"""Use qualified BLM18P reflow lands at the PLL branch's <=100mA load."""
from pathlib import Path
import hashlib, json
import sexpdata as sx

ROOT=Path(__file__).resolve().parents[1]
NAME='Murata_BLM18PG330SN1D_0603'
def nodes(n,t):return [v for v in n if isinstance(v,list) and str(v[0])==t]

def main():
    donor=ROOT/'lib/full-adapter.pretty/Murata_BLM18PG121SN1D_0603.kicad_mod'
    f=sx.loads(donor.read_text());f[1]=NAME
    next(p for p in nodes(f,'property') if p[1]=='Value')[2]=NAME
    nodes(f,'descr')[0][1]='Murata BLM18PG330SN1D; BLM18P reflow a=0.7/b=2.0/c=d=0.7mm for <=1.5A, actual PLL branch <=0.1A; do not claim3A with these lands; JENF243A-0003AG-01 p9; https://www.ecsimple.com/files/83/blm18pg330sn1d.pdf'
    # The two variants share the BLM18P package. Use the existing nominal model.
    (ROOT/'lib/full-adapter.pretty'/(NAME+'.kicad_mod')).write_text(sx.dumps(f)+'\n')
    (ROOT/'research/ethernet-ferrite-footprint.json').write_text(json.dumps({
        'source':'https://www.ecsimple.com/files/83/blm18pg330sn1d.pdf',
        'manufacturer_spec':'Murata JENF243A-0003AG-01, pages1/4/9',
        'sha256':hashlib.sha256((ROOT/'reference/blm18pg330sn1d.pdf').read_bytes()).hexdigest(),
        'pad_centers_x_mm':[-.675,.675],'pad_size_mm':[.65,.7],
        'reflow_land_dimensions_mm':{'a':.7,'b':2,'c':.7,'d':.7},
        'application_current_max_A':.1,'land_pattern_limit_A':1.5,
        'body_nominal_mm':[1.6,.8,.8],'body_tolerance_mm':.15,
        'note':'Existing BLM18P native-derived nominal model. Full3A rating requires larger copper extensions per manufacturer; not claimed for this low-current PLL filter.'},indent=2)+'\n')

if __name__=='__main__':main()
