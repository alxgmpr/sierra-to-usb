"""Vendor the native KiCad QFN geometry matching the reviewed RK809 drawing."""
from pathlib import Path
import hashlib
import json
import shutil

ROOT = Path(__file__).resolve().parents[1]
KICAD = Path('/Applications/KiCad/KiCad.app/Contents/SharedSupport')
BASE = 'ArtInChip_QFN-68-1EP_7x7mm_P0.35mm_EP5.49x5.49mm'
NAME = BASE.replace('ArtInChip','RK809')
source = KICAD / 'footprints/Package_DFN_QFN.pretty' / (BASE+'_ThermalVias.kicad_mod')
model = KICAD / '3dmodels/Package_DFN_QFN.3dshapes' / (BASE+'.step')
text = source.read_text().replace('ArtInChip','RK809')
text = text.replace('${KICAD10_3DMODEL_DIR}/Package_DFN_QFN.3dshapes/', '${KIPRJMOD}/../lib/full-adapter.3dshapes/')
text = text.replace('https://artinchip.com/upload/files/product/20240112/17050529177725663.pdf/#page=42',
                    json.loads((ROOT/'research/pmic-pins.json').read_text())['source']['url']+'#page=19; vendored native KiCad geometry')
(ROOT/'lib/full-adapter.pretty'/(NAME+'_ThermalVias.kicad_mod')).write_text(text)
shutil.copy2(model,ROOT/'lib/full-adapter.3dshapes'/(NAME+'.step'))
record={'source_footprint':str(source),'source_footprint_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
        'source_model':str(model),'source_model_sha256':hashlib.sha256(model.read_bytes()).hexdigest(),
        'pads':{'perimeter':68,'lead_pitch_mm':.35,'horizontal_land_mm':[.55,.25],
                'exposed_pad_number':'69','exposed_pad_mm':[5.49,5.49],
                'thermal_via_count':16,'thermal_via_drill_mm':.2,'thermal_via_land_mm':.5},
        'model_envelope_mm':[7,7,.9],
        'model_note':'Native KiCad model is 0.9mm high, conservatively 0.1mm taller than RK809 maximum. It is a clearance envelope, not a manufacturer model.',
        'manufacturing_note':'Thermal vias require the board filled/capped via process; preserve copper and solder-mask definitions.'}
(ROOT/'research/pmic-footprint-source.json').write_text(json.dumps(record,indent=2)+'\n')
print('Vendored QFN68/EP69 geometry and conservative clearance model')
