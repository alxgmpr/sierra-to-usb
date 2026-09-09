"""RK809-5 pin map reviewed against Rev 1.7 pages 15–19 and reference page 22."""
from pathlib import Path
import hashlib
import json

ROOT = Path(__file__).resolve().parents[1]
pdf = next((ROOT/'reference').glob('Rockchip*RK809*.pdf'))
download = next(p for p in json.loads((ROOT/'research/source-downloads.json').read_text()) if p['name']==pdf.name)
assert hashlib.sha256(pdf.read_bytes()).hexdigest()==download['sha256']
names = ('SCL SDA LDO7 VCC7 LDO8 LDO9 INT FB2 SW2 VCC2 VCC1 SW1 FB1 '
         'LRCLK BCLK MCLK SDI SDO/PDMDATA PDMCLK LDO3 LDO2 VCC5 LDO1 '
         'VCC3 SW3 VBUCK3 FB3 LDO4 LDO5 VCC6 LDO6 SPKP_OUT VCC_SPK_HP '
         'SPKN_OUT VCC_CPVSS CPN CPP VCC_CPVDD HPL_OUT HP_SNS HPR_OUT '
         'MIC1N MIC1P VCC_1P8A VCC_RTC VREF GNDREF VCC_1P8D SLEEP XIN '
         'XOUT PWRON SW5 VCC9 SWOUT1 BATDIV VCC8 SWOUT2 FB5 EXT_EN VDC '
         'SNSP SNSN FB4 SW4 VCC4 RESETB CLK32K').split()
assert len(names) == 68
groups = {
    'BUCK1 — LOGIC': [11,12,13], 'BUCK2 — GPU': [10,9,8],
    'BUCK3 — DDR': [24,25,26,27], 'BUCK4 — NPU': [66,65,64],
    'BUCK5 and switch 1': [54,53,59,55],
    'LDO1 / LDO2 / LDO3': [22,23,21,20],
    'LDO4 / LDO5 / LDO6': [30,28,29,31],
    'LDO7 / LDO8 / LDO9': [4,3,5,6],
    'Switch 2': [57,58],
    'System control and RTC': [45,1,2,49,52,61,50,51,7,67,68,60,46,47,56,62,63,69],
    'Audio interface — unused': [14,15,16,17,18,19,33,44,48,32,34,35,36,37,38,39,40,41,42,43],
}
power_inputs={4,10,11,22,24,30,33,45,54,57,66,47,69}
power_outputs={3,5,6,9,12,20,21,23,25,28,29,31,44,48,53,55,58,65}
outputs={18,32,34,35,36,37,38,39,41,46,51,60}
open_drain={7,67,68}
bidirectional={2,14,15}
pins=[]
for title,numbers in groups.items():
    for number in numbers:
        name = names[number-1] if number <=68 else 'GND'
        typ = ('power_in' if number in power_inputs else 'power_out' if number in power_outputs else
               'open_collector' if number in open_drain else 'output' if number in outputs else
               'bidirectional' if number in bidirectional else 'input')
        side = 'R' if typ in {'power_out','output','open_collector'} or number in {47,69} else 'L'
        pins.append({'ball':str(number),'name':name,'type':typ,'side':side,'unit_title':title})
        if number in {7,52,67}:
            pins[-1]['display_name']='~{'+('RESET' if number==67 else name)+'}'
assert sorted(int(p['ball']) for p in pins)==list(range(1,70))
result={
    'mpn':'RK809-5','manufacturer':'Rockchip','lcsc':'C2939628',
    'source':{'file':pdf.name,'sha256':hashlib.sha256(pdf.read_bytes()).hexdigest(),
              'url':download['url'],
              'pin_pages':[15,16,17],'package_page':19},
    'footprint':'full-adapter:RK809_QFN-68-1EP_7x7mm_P0.35mm_EP5.49x5.49mm_ThermalVias',
    'package':{'body_mm':[7,7],'maximum_height_mm':.8,'pitch_mm':.35,
               'exposed_pad_nominal_mm':[5.49,5.49],'exposed_pad_number':'69'},
    'notes':{
        '69':'Project pad-number assignment for the manufacturer unnumbered exposed ground pad.',
        '26':'VBUCK3 senses the external inductor output; FB3 is the separate 0.8V divider feedback.',
        '44_48':'Internal 1.8V supply outputs; decouple, do not externally drive. Reference diagram verifies this.',
        '19':'Clock for the PDM data output interface is driven by the SoC PDM clock. Rockchip reference ties it to ground when audio is unused.',
        '42_43':'Pin diagram MIC1N/MIC1P matches microphone polarity; table uses MICIN/MICIP typographic aliases.'},
    'unused_audio_ground':[14,15,16,17,19,40],
    'unused_audio_open':[18,36,37,38,35,39,41,34,32,43,42],
    'pins':pins,
}
(ROOT/'research/pmic-pins.json').write_text(json.dumps(result,indent=2)+'\n')
print('Recorded 68 numbered PMIC pins and exposed ground pad')
