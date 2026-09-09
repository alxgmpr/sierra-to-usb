"""Itemized static load bound, with data-sheet limits distinct from allowances."""
from pathlib import Path
import json,re,xml.etree.ElementTree as ET
P=Path(__file__).resolve().parents[1]/'carrier/build'
root=ET.parse(P/'carrier.xml')
nets={}
for net in root.findall('.//nets/net'):
    for p in net.findall('node'):
        nets.setdefault(p.attrib['ref'],set()).add(net.attrib['name'])
aux_sources={'AUX_3V3','PROFILE_OK','BUCK_ENABLE','POWER_REQUEST','RUN_REQUEST','RESET_PULSE'}
resistors=[]
for part in root.findall('.//components/comp'):
    ref=part.attrib['ref']
    if not ref.startswith('R') or not nets.get(ref,set())&aux_sources:continue
    match=re.match(r'([0-9.]+)([kMR]?)',part.findtext('value'))
    resistance=float(match[1])*{'':1,'R':1,'k':1000,'M':1e6}[match[2]]
    resistors.append({'ref':ref,'nets':sorted(nets[ref]),'ohm':resistance,
        'upper_current_A':3.4/(resistance*.98)})
# Summing every resistor at full supply overbounds incompatible logic states,
# and includes both programming pull-ups even though no programmer is normally present.
devices=[
 ('U101 STUSB4500L',500e-6,'allowance','210uA maximum at25C VDD5V; VSYS/hot-current allowance must be measured'),
 ('U104 HD3SS3212',800e-6,'published maximum','VCC3.3V active'),
 ('U105 TS3USB221A',30e-6,'published maximum','full-rail control inputs'),
 ('U303 INA190A1',100e-6,'allowance','90uA full-temperature limit specified atVS1.8V;100uA supply-voltage allowance'),
 ('U402 REF3312',8.5e-6+1.25625/(97400*.9965),'published limit plus load','8.5uA through125C; current-set divider load included'),
 ('U403 TLV333',28e-6+500e-6,'published limit plus allowance','28uA IQ full temperature plus500uA output-drive allocation'),
 ('U503/U506 TPS3890',2*6.5e-6,'published maximum','conservative5.5V/full-temperature IDD; SENSE current below counted on modem rail'),
 ('U508 LTC6993',250e-6,'allowance','175uA maximum idle atRSET50k/NDIV>=512/5.5V; extra active/load margin'),
 ('9 SN74LVC gates',9*10e-6,'family limit','10uA/gate with full-rail static inputs; exact02/04/86 tables still to cross-check'),
 ('U302 TPS7A2033 ground current',100e-6,'allowance','15uA no-load maximum; loaded ground current not maximum-specified'),
 ('Other leakage and switching average',1e-3,'allowance','ESD, FET, capacitor leakage and low-rate control transitions; excludes RF signal power'),
]
aux_a=sum(r['upper_current_A'] for r in resistors)+sum(row[1] for row in devices)
rail_v=json.loads((P/'replacement-power-budget.json').read_text())['rail_max_V']
bleeder=rail_v**2/(330*.99)
# Module operating load excludes these explicit carrier loads on the buck output.
rail_extra=[
 ('R410 bleeder',bleeder),
 ('Polymer leakage',rail_v*4*220e-6*6.3*.1),
 ('U504 control LDO plus straps/FCPO',rail_v*.0011),
 ('U503/U506 SENSE input',rail_v*16e-6),
 ('Feedback divider',rail_v**2/(66602*.998)),
]
rows=[]
for vbus in [4,4.25,4.5,4.75,5]:
    rows.append({'vbus_V':vbus,'auxiliary_input_W':vbus*aux_a,
        'carrier_output_load_W':sum(x[1] for x in rail_extra),
        'total_W':vbus*aux_a+sum(x[1] for x in rail_extra),
        'within_0_12W_allocation':vbus*aux_a+sum(x[1] for x in rail_extra)<=.12})
report={'status':'Itemized conditional bound; allowances require hot hardware verification',
    'auxiliary_rail_analysis_max_V':3.4,'resistor_min_factor':.98,
    'resistor_loads':resistors,'IC_loads':[dict(name=a,current_A=b,basis=c,condition=d) for a,b,c,d in devices],
    'auxiliary_total_input_current_A':aux_a,'carrier_output_loads_W':dict(rail_extra),'rows':rows,
    'exclusions':'Modem operating current is the separate3A load; no MCU,fan,LED bank or external load is authorized by this budget. Dynamic input-current peak is not bounded here.'}
(P/'auxiliary-budget.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'auxiliary_current_A':aux_a,'rows':rows},indent=2))
