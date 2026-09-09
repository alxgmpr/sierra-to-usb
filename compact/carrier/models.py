"""Dimensioned envelope models, explicitly not detailed manufacturer solids.
Input boxes use footprint +Y downward; CAD/VRML output negates Y.
All dimensions in mm. Mechanical models are additional board-only envelopes.
"""
from pathlib import Path
import json,sys,math,re
from OCP.gp import gp_Pnt, gp_Ax2, gp_Dir
from OCP.BRepPrimAPI import BRepPrimAPI_MakeBox, BRepPrimAPI_MakeCylinder
from OCP.BRep import BRep_Builder
from OCP.TopoDS import TopoDS_Compound
from OCP.STEPControl import STEPControl_Writer,STEPControl_AsIs
P=Path(__file__).resolve().parent
sys.path.insert(0,str(P.parent/'tools'))
from generation_guard import preflight,record
out=P/'models';out.mkdir(exist_ok=True)
# xmin,ymin,zmin,xmax,ymax,zmax. Envelope dimensions are source-referenced in the report.
def box(x,y,z,w,d,h):return [x,y,z,x+w,y+d,z+h]
data={
 'JS102011SAQN_envelope':{'boxes':[box(-4.5,-1.8,0,9,3.6,3.5),box(-1.775,1.8,1.5,3.55,2,1.5)],'source':'C&K JS2016-06-29 pI-52; nominal body and swept2mm actuator travel; terminals/pegs omitted','color':[.25,.25,.25]},
 'SOT523_envelope':{'boxes':[box(-.875,-.85,0,1.75,1.7,.9)],'source':'Diodes DMG1012T SOT523 maximum lead/body envelope; A1+A2 height; lead detail omitted','color':[.15,.15,.15]},
 'RSE10_envelope':{'boxes':[box(-.775,-1.025,0,1.55,2.05,.6)],'source':'TI RSE0010A maximum dimensions; lead detail omitted','color':[.15,.15,.15]},
 'LTC3310S_envelope':{'boxes':[box(-1.5,-1.5,0,3,3,1.03)],'source':'ADI05-08-1548RevD','color':[.15,.15,.15]},
 'XEL4030_envelope':{'boxes':[box(-2.15,-2.15,0,4.3,4.3,3.1)],'source':'Coilcraft1321-3,2026-02-19','color':[.22,.22,.22]},
 'CSM2512_envelope':{'boxes':[box(-3.302,-1.715,0,6.604,3.43,.889)],'source':'VPG4138-ENRev2025-07-08; H0.635 plus0.254 tolerance; solder height additional','color':[.65,.65,.6]},
 'T530_D_envelope':{'boxes':[box(-3.8,-2.3,0,7.6,4.6,3.1)],'source':'KEMETT2076T52X-530caseD; maximum body7.6x4.6x3.1','color':[.2,.16,.1]},
 'MHF4_envelope':{'boxes':[box(-1,-1,0,2,2,.7)],'source':'IPEX20449Rev22 unmated envelope; tool/mated envelope separate','color':[.75,.65,.2]},
 'SMF_envelope':{'boxes':[box(-1.55,-1,0,3.1,2,1.1)],'source':'LittelfuseSMFRev2023-11-02','color':[.1,.1,.1]},
 'MDT420_envelope':{'boxes':[box(-11,-5.7,0,22,7.2,4.2)],'source':'AmphenolCMDT420RevA, housing envelope; mating cavity not modeled','color':[.15,.15,.15],'transparency':.45},
 'N2520_envelope':{'boxes':[box(-4.93,-5.565,0,32.72,8.59,9.91)],'source':'3M78-5100-0770-7RevU; connector cavities omitted','color':[.15,.15,.15],'transparency':.3},
 'Module_EM9190_max_envelope':{'boxes':[box(-15.225,-26.15,2.49,30.45,52.30,.88),box(-14,-21,3.37,28,44,1.5)],'source':'Sierra41113174Rev8; board maximum outline and upper component-height envelope. Shield XY is an envelope, not an exact shield drawing.','color':[.7,.72,.75],'transparency':.25},
 'Heatsink_envelope':{'boxes':[box(-25,-25,5.12,50,50,25)],'source':'FischerICK S50x50x25 manufacturer print; outside envelope ONLY, no invented fin pattern','color':[.2,.5,.8],'transparency':.8},
 'TIM_8810':{'boxes':[box(-10,-15,4.87,20,30,.25)],'source':'3M8810July2015; custom cut patch, actual shield fit must be verified','color':[.85,.85,.85]},
 'Retention_frame':{'boxes':[box(-32,-25,31,6,50,2),box(26,-25,31,6,50,2),box(-26,-25,31,52,6,2),box(-26,19,31,52,6,2)],'source':'CustomHN03mechanical-review.md; holes omitted from envelope','color':[.45,.48,.5]},
 'Profile_service_envelope':{'boxes':[box(-4.93,-5.565,9.91,32.72,8.59,12.09)],'source':'22mm assembly service reservation; NOT manufacturer mated-height model','color':[.85,.5,.2],'transparency':.75}
}
data.update({
 'SMA132289_clearance_envelope':{'boxes':[box(-4.75,-5.1,-7.5,17.45,10.2,15)],'source':'Amphenol132289RevB:4.75mm rear,12.7mm front,10.2mm washer. Engineering vertical reservation±7.5mm exceeds nominal washer radius plus1.73mm slot; not a panel-axis model.','color':[.8,.65,.2],'transparency':.45},
 'Module_support':{'boxes':[],'cylinders':[[0,0,0,2.5,2.49]],'source':'CustomHN01; bore omitted in clearance model','color':[.7,.6,.25]},
 'Retention_post':{'boxes':[],'cylinders':[[0,0,0,3,31]],'source':'CustomHN02; threaded bores omitted in clearance model','color':[.5,.5,.5]}
})
# TI RPW0010A, drawing 4225183/A: nominal 2 x 2 body, 1 mm max height.
# Simplified exposed copper, using package dimensions (not expanded PCB lands).
rpw_boxes=[box(-1,-1,.1,2,2,.9)]
for side in [-1,1]:
 for y in [-.7,-.225,.225,.7]:
  rpw_boxes.append(box(-1 if side<0 else .6,y-(.15 if abs(y)>.5 else .125),0,.4,.3 if abs(y)>.5 else .25,.1))
 for sign in [-1,1]:
  rpw_boxes.append(box(-.85 if side<0 else .6,-1 if sign<0 else .55,0,.25,.45,.1))
for x in [-.25,.25]:rpw_boxes.append(box(x-.15,-1,0,.3,2,.1))
data['TI_RPW0010A']={'boxes':rpw_boxes,'cylinders':[[-.7,-.7,.999,.1,.001]],
 'source':'TI TPS25947 Rev C, RPW0010A drawing4225183/A 08/2019: nominal2x2mm,1mm max height,10 contacts. Reconstructed package model; corner lead radii and mold draft omitted. Pin1 dot is illustrative.',
 'color':[.12,.12,.12], 'box_colors':[[.12,.12,.12]]+[[.7,.7,.72]]*(len(rpw_boxes)-1)}
# Removed assembly hardware; adhesive cooling is intentionally unmodeled.
for name in ['Heatsink_envelope','TIM_8810','Retention_frame','Retention_post','Profile_service_envelope']:
 data.pop(name)
outputs=[out/(name+ext) for name in data for ext in ['.wrl','.step']]+[P/'build/model-register.json']
preflight(P,'carrier-models',outputs)
for name,d in data.items():
 compound=TopoDS_Compound();builder=BRep_Builder();builder.MakeCompound(compound)
 text='#VRML V2.0 utf8\n# DIMENSIONED ENVELOPE: '+d['source']+'\n'
 for index,a in enumerate(d['boxes']):
  x,y,z,X,Y,Z=a;builder.Add(compound,BRepPrimAPI_MakeBox(gp_Pnt(x,-Y,z),X-x,Y-y,Z-z).Shape())
  # KiCad VRML unit is2.54mm; STEP remains in mm.
  center=' '.join(str(v/2.54) for v in [(x+X)/2,-(y+Y)/2,(z+Z)/2])
  dims=' '.join(str(v/2.54) for v in [X-x,Y-y,Z-z])
  color=' '.join(map(str,d.get('box_colors',[d['color']]*len(d['boxes']))[index]))
  text+=f'Transform {{ translation {center} children [ Shape {{ appearance Appearance {{ material Material {{ diffuseColor {color} transparency {d.get("transparency",0)} }} }} geometry Box {{ size {dims} }} }} ] }}\n'
 for x,y,z,r,h in d.get('cylinders',[]):
  builder.Add(compound,BRepPrimAPI_MakeCylinder(gp_Ax2(gp_Pnt(x,-y,z),gp_Dir(0,0,1)),r,h).Shape())
  color=' '.join(map(str,d['color']))
  vertices=[[(x+r*math.cos(i*math.pi/16))/2.54,(-y+r*math.sin(i*math.pi/16))/2.54,(z+level*h)/2.54] for level in [0,1] for i in range(32)]
  faces=[[i,(i+1)%32,(i+1)%32+32,i+32] for i in range(32)]+[list(range(31,-1,-1)),list(range(32,64))]
  points=', '.join(' '.join(map(str,v)) for v in vertices)
  indices=', '.join(' '.join(map(str,f+[-1])) for f in faces)
  text+=f'Shape {{ appearance Appearance {{ material Material {{ diffuseColor {color} }} }} geometry IndexedFaceSet {{ coord Coordinate {{ point [ {points} ] }} coordIndex [ {indices} ] solid TRUE }} }}\n'
 (out/(name+'.wrl')).write_text(text)
 writer=STEPControl_Writer();writer.Transfer(compound,STEPControl_AsIs);writer.Write(str(out/(name+'.step')))
 step=out/(name+'.step');step.write_text(re.sub(r"(FILE_NAME\('[^']*',')([^']+)",r"\g<1>2026-09-06T00:00:00",step.read_text()))
outputs[-1].write_text(json.dumps({'status':'Dimensioned envelopes; details/cavities omitted as individually stated. Not manufacturer CAD.','models':data},indent=2)+'\n')
record(P,'carrier-models',outputs)
