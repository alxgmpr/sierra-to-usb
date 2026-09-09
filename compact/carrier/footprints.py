"""Manufacturer land patterns; no routing or thermal vias are generated."""
from pathlib import Path
import sys,json
from KicadModTree import Footprint,FootprintType,Pad,Rectangle,Property,KicadFileHandler,RoundRadiusHandler,Polygon,Model
P=Path(__file__).resolve().parent
sys.path.insert(0,str(P.parent/'tools'))
from generation_guard import preflight,record
out=P/'carrier.pretty'
outputs=[out/'L_Coilcraft_XEL4030.kicad_mod',out/'LTC_LQFN18_3x3_05-08-1548.kicad_mod',P/'reference/carrier-land-patterns.json']
outputs.append(out/'VPG_CSM2512_Kelvin.kicad_mod')
outputs.append(out/'KEMET_D_7343_Median.kicad_mod')
outputs.append(out/'SMA_Amphenol_132289_Manufacturer.kicad_mod')
outputs.append(out/'M2_B_Amphenol_MDT420_1A.kicad_mod')
outputs.append(out/'IPEX_MHF4_20449_001E_03.kicad_mod')
outputs.append(out/'IDC_3M_N2520_6002_RB.kicad_mod')
outputs.append(out/'Littelfuse_SMF_SOD123FL.kicad_mod')
preflight(P,'carrier-footprints',outputs)
out.mkdir(exist_ok=True)
f=Footprint('LTC_LQFN18_3x3_05-08-1548',FootprintType.SMD)
f.description='LTC 05-08-1548 Rev D, suggested PCB layout viewed from top; 18 perimeter contacts plus PGND19. No thermal vias.'
f.tags='LTC3310S LQFN 18 3x3'
f.append(Property(name='Reference',text='REF**',at=[0,-2.6],layer='F.SilkS',size=[1,1],thickness=.15))
f.append(Property(name='Value',text=f.name,at=[0,2.6],layer='F.Fab',size=[.6,.6],thickness=.1))
f.append(Rectangle(start=[-1.5,-1.5],end=[1.5,1.5],layer='F.Fab',width=.1))
f.append(Rectangle(start=[-2,-2],end=[2,2],layer='F.CrtYd',width=.05))
spec=[]
def pad(n,x,y,w,h,layers=None):
 spec.append({'number':n,'center':[x,y],'size':[w,h],'layers':layers or Pad.LAYERS_SMT})
 f.append(Pad(number=n,type=Pad.TYPE_SMT,shape=Pad.SHAPE_ROUNDRECT,at=[x,y],size=[w,h],
    layers=layers or Pad.LAYERS_SMT,round_radius_handler=RoundRadiusHandler(radius_ratio=.2,maximum_radius=.05)))
for i in range(5):
 pad(i+1,-1.4,-1+i*.5,.7,.25)
 pad(14-i,1.4,-1+i*.5,.7,.25)
for i in range(4):
 pad(6+i,-.75+i*.5,1.4,.25,.7)
 pad(18-i,-.75+i*.5,-1.4,.25,.7)
pad(19,0,0,1.70,1.51,['F.Cu','F.Mask'])
for x in [-.43,.43]:
 for y in [-.38,.38]:pad('',x,y,.70,.62,['F.Paste'])
KicadFileHandler(f).writeFile(outputs[1])
outputs[2].write_text(json.dumps({'LTC_LQFN18_3x3_05-08-1548':{
 'source':'https://www.analog.com/media/en/package-pcb-resources/package/pkg_pdf/ltc-legacy-lqfn/05081548_C_LQFN18.pdf',
 'drawing_revision':'05-08-1548 Rev D, July 2021 (URL retains C)',
 'review':'Manufacturer drawing visually inspected in browser 2026-09-06. Top-view pin numbering mirrored from package bottom view.',
 'paste':'Four 0.70 x 0.62 mm apertures, 67.6% EP area; engineering stencil choice, assembly qualification pending.',
 'body_mm':[3,3,1.03],'pads':spec,'thermal_vias':0}},indent=2)+'\n')
f=Footprint('L_Coilcraft_XEL4030',FootprintType.SMD)
f.description='Coilcraft Document 1321-3 revised 2026-02-19; recommended 2.37 mm pad pitch, 0.98 x 3.4 mm pads. Body 4.0 +/-0.3 mm, -471 height 3.10 mm maximum.'
f.append(Property(name='Reference',text='REF**',at=[0,-3],layer='F.SilkS',size=[1,1],thickness=.15))
f.append(Property(name='Value',text=f.name,at=[0,3],layer='F.Fab',size=[.7,.7],thickness=.1))
f.append(Rectangle(start=[-2.15,-2.15],end=[2.15,2.15],layer='F.Fab',width=.1))
f.append(Rectangle(start=[-2.4,-2.4],end=[2.4,2.4],layer='F.CrtYd',width=.05))
for n,x in [(1,-1.185),(2,1.185)]:
 f.append(Pad(number=n,type=Pad.TYPE_SMT,shape=Pad.SHAPE_ROUNDRECT,at=[x,0],size=[.98,3.4],layers=Pad.LAYERS_SMT,round_radius_handler=RoundRadiusHandler(radius_ratio=.1,maximum_radius=.05)))
KicadFileHandler(f).writeFile(outputs[0])
report=json.loads(outputs[2].read_text())
report[f.name]={'source':'https://www.coilcraft.com/getmedia/8245f050-f190-4295-8c41-7c03d662ee3d/xel4030.pdf','revision':'Document 1321-3 revised 2026-02-19','review':'Manufacturer drawing visually inspected in browser. Recommended pad dimensions also independently match installed XAL4030 footprint geometry. No XAL 3D model reused.','body_max_mm':[4.3,4.3,3.10],'pad_pitch_mm':2.37,'pad_size_mm':[.98,3.4]}
outputs[2].write_text(json.dumps(report,indent=2)+'\n')
f=Footprint('VPG_CSM2512_Kelvin',FootprintType.SMD)
f.description='VPG 4138-EN Rev 8-July-2025 p2, 10 milliohm CSM2512. Pads1/2 force,3/4 sense, diagonal Kelvin contacts. Sense pad longitudinal extent enlarged from1.39 to1.65mm for symmetric toe/heel allowance; confirm assembly stencil.'
f.append(Property(name='Reference',text='REF**',at=[0,-2.8],layer='F.SilkS',size=[1,1],thickness=.15))
f.append(Property(name='Value',text=f.name,at=[0,2.8],layer='F.Fab',size=[.7,.7],thickness=.1))
f.append(Rectangle(start=[-3.302,-1.715],end=[3.302,1.715],layer='F.Fab',width=.1))
f.append(Rectangle(start=[-3.95,-2.1],end=[3.95,2.1],layer='F.CrtYd',width=.05))
shuntpads=[(1,-2.855,-.835,1.65,2.01),(2,2.855,.835,1.65,2.01),
           (3,-2.855,1.27,1.65,1.14),(4,2.855,-1.27,1.65,1.14)]
for n,x,y,w,h in shuntpads:
 f.append(Pad(number=n,type=Pad.TYPE_SMT,shape=Pad.SHAPE_ROUNDRECT,at=[x,y],size=[w,h],layers=Pad.LAYERS_SMT,round_radius_handler=RoundRadiusHandler(radius_ratio=.1,maximum_radius=.05)))
KicadFileHandler(f).writeFile(outputs[3])
report[f.name]={'source':'https://vpgfoilresistors.com/products/current-sense-resistors/csm2512/datasheet',
 'revision':'4138-EN Rev 8-July-2025, page2',
 'review':'Package and land-pattern drawings visually inspected in browser; diagonally opposed sense pads. White dot identifies top side, not an electrical polarity.',
 'manufacturer_land_dimensions_mm':{'a':1.65,'b':3.68,'c':1.14,'d':.53,'e':1.39,'l':4.06},
 'adaptation':'Sense pad length enlarged to1.65mm, matching current pad inner/outer boundaries; retain0.53mm lateral gap. Assembly qualification pending.',
 'pin_mapping':{'1':'I1 force+','2':'I2 force-','3':'E1 sense+','4':'E2 sense-'},'pads':shuntpads,
 'body_nominal_mm':[6.350,3.175,.635],'body_tolerance_mm':.254}
outputs[2].write_text(json.dumps(report,indent=2)+'\n')
f=Footprint('KEMET_D_7343_Median',FootprintType.SMD)
f.description='KEMET T2076_T52X-530 2026-08-20 Table2 density B: pad length2.37 width2.43 gap3.87; anode pad1.'
f.append(Property(name='Reference',text='REF**',at=[0,-3.3],layer='F.SilkS',size=[1,1],thickness=.15))
f.append(Property(name='Value',text=f.name,at=[0,3.3],layer='F.Fab',size=[.7,.7],thickness=.1))
f.append(Rectangle(start=[-3.65,-2.15],end=[3.65,2.15],layer='F.Fab',width=.1))
f.append(Rectangle(start=[-4.56,-2.55],end=[4.56,2.55],layer='F.CrtYd',width=.05))
f.append(Rectangle(start=[-3.4,-1.8],end=[-3.1,1.8],layer='F.Fab',width=.1))
for n,x in [(1,-3.12),(2,3.12)]:
 f.append(Pad(number=n,type=Pad.TYPE_SMT,shape=Pad.SHAPE_ROUNDRECT,at=[x,0],size=[2.37,2.43],layers=Pad.LAYERS_SMT,round_radius_handler=RoundRadiusHandler(radius_ratio=.1,maximum_radius=.1)))
KicadFileHandler(f).writeFile(outputs[4])
report[f.name]={'source':'https://content.kemet.com/datasheets/kem_t2076_t52x-530.pdf','revision':'T2076_T52X-530 2026-08-20, Table2 p37','pad_size_mm':[2.37,2.43],'pad_center_x_mm':[-3.12,3.12],'gap_mm':3.87,'courtyard_mm':[9.12,5.10],'pin_mapping':{'1':'anode','2':'cathode'},'comparison':'Installed standard Kemet-D footprint uses same pad centres but2.07x2.59 pads; this custom footprint adopts current manufacturer median dimensions.'}
outputs[2].write_text(json.dumps(report,indent=2)+'\n')
f=Footprint('SMA_Amphenol_132289_Manufacturer',FootprintType.SMD)
f.description='Amphenol 132289 customer drawing Rev B 2011-11-30 recommended PCB layout. Origin at board edge/centreline; connector projects in +X. Maximum finished board thickness1.57mm.'
f.append(Property(name='Reference',text='REF**',at=[-6.5,0],layer='F.SilkS',size=[1,1],thickness=.15))
f.append(Property(name='Value',text='132289',at=[5.5,6],layer='F.Fab',size=[.8,.8],thickness=.1))
f.append(Rectangle(start=[-5.2,-4.76],end=[12.7,4.76],layer='F.Fab',width=.1))
for layer in ['F.CrtYd','B.CrtYd']:
 f.append(Rectangle(start=[-5.7,-5.55],end=[13.2,5.55],layer=layer,width=.05))
f.append(Pad(number=1,type=Pad.TYPE_SMT,shape=Pad.SHAPE_RECT,at=[-2.6,0],size=[5.2,1.5],layers=Pad.LAYERS_SMT))
for y in [-4.25,4.25]:
 for layers in [Pad.LAYERS_SMT,['B.Cu','B.Paste','B.Mask']]:
  f.append(Pad(number=2,type=Pad.TYPE_SMT,shape=Pad.SHAPE_RECT,at=[-2.75,y],size=[4.9,1.6],layers=layers))
f.append(Model(filename='${KIPRJMOD}/models/SMA_Amphenol_132289_EdgeMount.step',at=[-2.54,0,0]))
KicadFileHandler(f).writeFile(outputs[5])
report[f.name]={'source':'https://www.amphenolrf.com/en-us/assets/file/4065786470/',
 'revision':'132289 Rev B 2011-11-30','review':'Manufacturer drawing visually inspected in browser 2026-09-06.',
 'origin':'PCB edge at x=0, RF centreline y=0; connector projects +X',
 'signal_pad_mm':[5.2,1.5],'ground_pad_mm':[4.9,1.6],'ground_centres_y_mm':[-4.25,4.25],
 'ground_setback_from_edge_mm':.3,'maximum_finished_board_thickness_mm':1.57,
 'body_width_mm':9.52,'body_front_projection_mm':12.7,'panel_hole_mm':6.6,'maximum_panel_thickness_mm':3.5,
 'comparison':'Installed standard footprint has5.08x1.5 ground pads; this footprint follows current available manufacturer drawing instead.',
 'model':'KiCad exact 132289 STEP; x offset -2.54 mm aligns native board-edge plane to our origin. Slot spans z=-1.73..0 mm.'}
outputs[2].write_text(json.dumps(report,indent=2)+'\n')
f=Footprint('M2_B_Amphenol_MDT420_1A',FootprintType.SMD)
f.description='Amphenol CMDT420X0X411 Rev A released2022-11-08 page2, key B,4.2mm height. Origin at midpoint of locating holes. Card extends +Y. Power contacts1A per SMDT005 at25C.'
f.append(Property(name='Reference',text='REF**',at=[0,-7.4],layer='F.SilkS',size=[1,1],thickness=.15))
f.append(Property(name='Value',text='MDT420B01411',at=[0,4.2],layer='F.Fab',size=[.8,.8],thickness=.1))
f.append(Rectangle(start=[-11,-6.05],end=[11,3.05],layer='F.Fab',width=.1))
f.append(Rectangle(start=[-11.5,-6.55],end=[11.5,3.55],layer='F.CrtYd',width=.05))
for n in list(range(1,12,2))+list(range(21,76,2)):
 x=-9.25+(n-1)*.25
 f.append(Pad(number=n,type=Pad.TYPE_SMT,shape=Pad.SHAPE_RECT,at=[x,-5.275],size=[.30,1.55],layers=Pad.LAYERS_SMT))
for n in list(range(2,11,2))+list(range(20,75,2)):
 x=-9+(n-2)*.25
 f.append(Pad(number=n,type=Pad.TYPE_SMT,shape=Pad.SHAPE_RECT,at=[x,2.275],size=[.30,1.55],layers=Pad.LAYERS_SMT))
for n,x in [(76,-10.35),(77,10.35)]:
 f.append(Pad(number=n,type=Pad.TYPE_SMT,shape=Pad.SHAPE_RECT,at=[x,-4.5],size=[1.20,2.75],layers=Pad.LAYERS_SMT))
for x,d in [(-10,1.1),(10,1.6)]:
 f.append(Pad(number='',type=Pad.TYPE_NPTH,shape=Pad.SHAPE_CIRCLE,at=[x,0],size=[d,d],drill=d,layers=Pad.LAYERS_NPTH))
KicadFileHandler(f).writeFile(outputs[6])
report[f.name]={'source':'https://cdn.amphenol-cs.com/media/wysiwyg/files/drawing/cmdt420x0x411.pdf',
 'local_source':'compact/reference/amphenol-mdt420.pdf','revision':'CMDT420X0X411 Rev A 2022-11-08',
 'review':'Manufacturer PDF page2 visually inspected, including enlarged land-pattern dimensions.',
 'origin':'midpoint of locating holes; card extends +Y','signal_pad_mm':[.30,1.55],
 'odd_row_y_mm':-5.275,'even_row_y_mm':2.275,'hole_x_mm':[-10,10],'hole_diameter_mm':[1.1,1.6],
 'shell_pad_mm':[1.2,2.75],'shell_pad_centres_mm':[[-10.35,-4.5],[10.35,-4.5]],
 'pin_mapping':'Standard B-key1..11,20..75; mechanical solder tabs assigned76/77 GND by carrier convention.',
 'electrical':'SMDT005 section5.4:1A per power contact continuous at25C still air,30C max rise; hot assembly qualification remains required.',
 'availability':'No exact DigiKey keyword result2026-09-06; sourcing gate remains open.'}
outputs[2].write_text(json.dumps(report,indent=2)+'\n')
f=Footprint('IPEX_MHF4_20449_001E_03',FootprintType.SMD)
f.description='I-PEX20449 Rev22 2025-09-17 page4. Signal1, shell2 by carrier convention. Includes manufacturer central front-copper/resist exclusion; no vias.'
f.append(Property(name='Reference',text='REF**',at=[0,-2.1],layer='F.SilkS',size=[.8,.8],thickness=.12))
f.append(Property(name='Value',text='20449-001E-03',at=[0,2.2],layer='F.Fab',size=[.6,.6],thickness=.1))
f.append(Rectangle(start=[-1,-1],end=[1,1],layer='F.Fab',width=.1))
f.append(Rectangle(start=[-1.5,-1.5],end=[1.5,1.5],layer='F.CrtYd',width=.05))
f.append(Pad(number=1,type=Pad.TYPE_SMT,shape=Pad.SHAPE_RECT,at=[0,.9],size=[.6,.7],layers=['F.Cu','F.Mask']))
f.append(Pad(number=2,type=Pad.TYPE_SMT,shape=Pad.SHAPE_RECT,at=[0,-.875],size=[.5,.75],layers=['F.Cu','F.Mask']))
left=[[-1.25,-.79],[-.67,-.79],[-.67,-.27],[-.75,-.19],[-.75,.19],[-.67,.27],[-.67,.79],[-1.25,.79]]
for mirror in [1,-1]:
 center=[-1*mirror,0]
 points=[[mirror*x-center[0],y] for x,y in left]
 f.append(Pad(number=2,type=Pad.TYPE_SMT,shape=Pad.SHAPE_CUSTOM,at=center,size=[.2,.2],layers=['F.Cu','F.Mask'],primitives=[Polygon(points,width=0,fill=True)]))
# Manufacturer 0.12mm stencil recommendations, separate from copper geometry.
for x,y,w,h in [(0,1.02,.36,.36),(0,-1.01,.38,.38),(-1,0,.5,.9),(1,0,.5,.9)]:
 f.append(Pad(number='',type=Pad.TYPE_SMT,shape=Pad.SHAPE_RECT,at=[x,y],size=[w,h],layers=['F.Paste']))
exclude=[[-.67,-.79],[-.25,-.79],[-.25,-.5],[.25,-.5],[.25,-.79],[.67,-.79],[.67,-.27],[.75,-.19],[.75,.19],[.67,.27],[.67,.79],[.3,.79],[.3,.55],[-.3,.55],[-.3,.79],[-.67,.79],[-.67,.27],[-.75,.19],[-.75,-.19],[-.67,-.27]]
f.append(Polygon(exclude,layer='F.Mask',width=0,fill=True))
KicadFileHandler(f).writeFile(outputs[7])
data=outputs[7].read_text().rstrip().replace('(attr smd)', '(attr smd allow_soldermask_bridges)')
pts=' '.join(f'(xy {x} {y})' for x,y in exclude)
data=data[:-1]+f'\n(zone (net 0) (net_name "") (layer "F.Cu") (hatch edge 0.5) (connect_pads (clearance 0)) (min_thickness 0.05) (keepout (tracks not_allowed) (vias not_allowed) (pads not_allowed) (copperpour not_allowed) (footprints allowed)) (polygon (pts {pts})))\n)\n'
outputs[7].write_text(data)
report[f.name]={'source':'https://www.i-pex.com/sites/default/files/downloads/pdf/2D_MHF_4_RECEPTACLE_1_20449C22.pdf',
 'revision':'20449 Rev22 2025-09-17 p4','review':'Manufacturer copper, stencil and exclusion drawings visually inspected at enlarged resolution.',
 'pin_mapping':{'1':'centre contact','2':'all three ground contacts'},'signal_pad_mm':[.6,.7],
 'left_ground_polygon_mm':left,'right_ground':'mirror X','front_copper_and_resist_exclusion_polygon_mm':exclude,
 'stencil_mm':.12,'maximum_unmated_height_mm':.7,'mated_height_1_13mm_MHF4L_mm':1.4,
 'assembly_clearance':'Reserve diameter7.6mm around carrier receptacle for service access; conservative envelope from manufacturer locked-harness jig drawing, not a claim this cable has a lock.',
 'thermal_vias':0}
outputs[2].write_text(json.dumps(report,indent=2)+'\n')
f=Footprint('IDC_3M_N2520_6002_RB',FootprintType.THT)
f.description='3M 78-5100-0770-7 Rev U 2026-03-04 sheet2. N2520-6002-RB, 20 contacts, pin1 origin, odd pins extend +X, even row at Y=-2.54. No optional locating peg.'
f.append(Property(name='Reference',text='REF**',at=[11.43,-7],layer='F.SilkS',size=[1,1],thickness=.15))
f.append(Property(name='Value',text='N2520-6002-RB',at=[11.43,4.5],layer='F.Fab',size=[.8,.8],thickness=.1))
f.append(Rectangle(start=[-4.93,-5.565],end=[27.79,3.025],layer='F.Fab',width=.1))
f.append(Rectangle(start=[9.335,1.925],end=[13.525,3.025],layer='F.Fab',width=.1))
f.append(Rectangle(start=[-5.5,-6.15],end=[28.35,3.6],layer='F.CrtYd',width=.05))
for n in range(1,21):
 f.append(Pad(number=n,type=Pad.TYPE_THT,shape=Pad.SHAPE_RECT if n==1 else Pad.SHAPE_CIRCLE,at=[((n-1)//2)*2.54,0 if n%2 else -2.54],size=[1.7,1.7],drill=.89,layers=Pad.LAYERS_THT))
KicadFileHandler(f).writeFile(outputs[8])
report[f.name]={'source':'https://multimedia.3m.com/mws/media/330367O/3m-four-wall-header-2500-series-ts-0770.pdf','revision':'78-5100-0770-7 Rev U 2026-03-04 sheet2','body_mm':[32.72,8.59,9.91],'hole_finished_mm':.89,'land_diameter_mm':1.7,'review':'Component-side manufacturer drawing visually reviewed; pin1 beside notch side, odd row y0, even row y-2.54. Pad annulus is engineering choice. No optional peg fitted.','mating_socket':'89120-0101HA','availability':'DigiKey exact header19891 and socket2279 at2026-09-06; snapshot is not procurement.'}
outputs[2].write_text(json.dumps(report,indent=2)+'\n')
f=Footprint('Littelfuse_SMF_SOD123FL',FootprintType.SMD)
f.description='Littelfuse SMF200W datasheet revised2023-11-02 p5. Pads1.3x1.4mm, gap1.6mm. Pin1 cathode at negativeX.'
f.append(Property(name='Reference',text='REF**',at=[0,-1.8],layer='F.SilkS',size=[.8,.8],thickness=.12))
f.append(Property(name='Value',text='SMF6.0A',at=[0,1.8],layer='F.Fab',size=[.7,.7],thickness=.1))
f.append(Rectangle(start=[-1.55,-1],end=[1.55,1],layer='F.Fab',width=.1))
f.append(Rectangle(start=[-1.35,-.9],end=[-1.15,.9],layer='F.Fab',width=.1))
f.append(Rectangle(start=[-2.35,-1.25],end=[2.35,1.25],layer='F.CrtYd',width=.05))
for n,x in [(1,-1.45),(2,1.45)]:
 f.append(Pad(number=n,type=Pad.TYPE_SMT,shape=Pad.SHAPE_RECT,at=[x,0],size=[1.3,1.4],layers=Pad.LAYERS_SMT))
KicadFileHandler(f).writeFile(outputs[9])
report[f.name]={'source':'https://www.littelfuse.com/assetdocs/tvs-diodes-smf-datasheet?assetguid=7eb8a5b6-bdd0-4561-8f19-0c3cc6f9b2af','revision':'SMF200W revised2023-11-02 p5','review':'Manufacturer recommended mounting pad drawing visually inspected at120% browser zoom. Standard KiCad SOD123F1.1mm pads replaced by manufacturer1.3x1.4mm pads.','pad_size_mm':[1.3,1.4],'pad_gap_mm':1.6,'body_max_mm':[3.1,2,1.1],'terminal_span_max_mm':3.9,'polarity':'1 cathode stripe,2 anode'}
outputs[2].write_text(json.dumps(report,indent=2)+'\n')
record(P,'carrier-footprints',outputs)
print('LQFN18 land pattern generated from manufacturer drawing')
