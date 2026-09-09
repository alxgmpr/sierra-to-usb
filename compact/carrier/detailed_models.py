"""Reconstructed, opaque assembly CAD from the source drawings in model-sources.md.
Coordinates: footprint X right, Y down; exported CAD Y is negated.
This is source-dimensioned visualization, not manufacturer-distributed CAD.
"""
from pathlib import Path
import json,sys,math
from OCP.gp import gp_Pnt,gp_Ax2,gp_Dir,gp_Trsf,gp_Vec
from OCP.BRepPrimAPI import BRepPrimAPI_MakeBox,BRepPrimAPI_MakeCylinder,BRepPrimAPI_MakeCone
from OCP.BRepAlgoAPI import BRepAlgoAPI_Cut
from OCP.BRepMesh import BRepMesh_IncrementalMesh
from OCP.BRep import BRep_Tool
from OCP.TopExp import TopExp_Explorer
from OCP.TopAbs import TopAbs_FACE,TopAbs_REVERSED
from OCP.TopoDS import TopoDS
from OCP.TopLoc import TopLoc_Location
from OCP.STEPCAFControl import STEPCAFControl_Writer
from OCP.STEPControl import STEPControl_AsIs
from OCP.TDocStd import TDocStd_Document
from OCP.TCollection import TCollection_ExtendedString
from OCP.XCAFDoc import XCAFDoc_DocumentTool,XCAFDoc_ColorGen
from OCP.Quantity import Quantity_Color,Quantity_TOC_RGB
from OCP.Bnd import Bnd_Box
from OCP.BRepBndLib import BRepBndLib
P=Path(__file__).resolve().parent
sys.path.insert(0,str(P.parent/'tools'))
from generation_guard import preflight,record
BLACK=(.055,.06,.065);GOLD=(.78,.62,.24);SILVER=(.62,.65,.68);GREEN=(.06,.21,.14);WHITE=(.91,.91,.88)
def box(x,y,z,w,d,h):return BRepPrimAPI_MakeBox(gp_Pnt(x,-y-d,z),w,d,h).Shape()
def cyl(x,y,z,r,h):return BRepPrimAPI_MakeCylinder(gp_Ax2(gp_Pnt(x,-y,z),gp_Dir(0,0,1)),r,h).Shape()
def cut(a,b):return BRepAlgoAPI_Cut(a,b).Shape()
def ring(x,y,z,r,R,h):return cut(cyl(x,y,z,R,h),cyl(x,y,z-.01,r,h+.02))
models={}
# 3M 78-5100-0770-7 Rev U, sheet2. Pin1=(0,0); row2 is y=-2.54.
housing=box(-4.93,-5.565,1.1,32.72,8.59,8.81)
housing=cut(housing,box(-3.91,-4.445,3.48,30.68,6.35,6.6))
# Centre polarization slot and secondary notches, according to drawing.
housing=cut(housing,box(9.335,1.9,2.7,4.19,1.2,7.3))
for x in [1.09,19.23]:housing=cut(housing,box(x,1.9,8.5,2.54,1.2,1.5))
parts=[(housing,BLACK)]
for x in [0,22.86]:parts.append((box(x-1.1,-5.565,0,2.2,8.59,1.1),BLACK))
for i in range(10):
 for y in [0,-2.54]:parts.append((box(i*2.54-.32,y-.32,-2.84,.64,.64,12.49),GOLD))
models['IDC_3M_N2520_Detailed']=parts
# Amphenol CMDT420X0X411 RevA: slot centre2.89, boardstop y=1.75.
housing=box(-11,-5.7,.1,22,7.2,4.1)
housing=cut(housing,box(-9.925,-1.75,2.49,19.85,3.3,.8))
# Stepped card entry. Key B stays inside slot at pins12..19.
housing=cut(housing,box(-9.925,.2,3.29,19.85,1.4,1))
parts=[(housing,BLACK),(box(-6.25,-1.75,2.49,2.5,3.25,.8),BLACK)]
for n in list(range(1,12,2))+list(range(21,76,2)):
 x=-9.25+(n-1)*.25
 parts.extend([(box(x-.15,-6.05,0,.30,1.55,.15),GOLD),(box(x-.15,-4.5,.1,.30,.25,3.3),GOLD),(box(x-.15,-4.3,3.29,.30,4.9,.15),GOLD)])
for n in list(range(2,11,2))+list(range(20,75,2)):
 x=-9+(n-2)*.25
 parts.extend([(box(x-.15,1.5,0,.30,1.55,.15),GOLD),(box(x-.15,1.5,.1,.30,.25,2.3),GOLD),(box(x-.15,-1.7,2.34,.30,3.4,.15),GOLD)])
for x in [-10.35,10.35]:parts.append((box(x-.6,-5.875,0,1.2,2.75,.15),SILVER))
for x,r in [(-10,.5),(10,.75)]:parts.append((cyl(x,0,-.65,r,.75),BLACK))
models['M2_MDT420_Detailed']=parts
# HN01 is a removable 2.49mm spacer; bore and through screw are now shown.
spacer=ring(0,0,0,1.1,2.5,2.49)
parts=[(spacer,GOLD),(cyl(0,0,-3.5,.95,7),SILVER),(ring(0,0,3.29,1.05,2.5,.3),SILVER)]
head=cyl(0,0,3.59,1.9,1.4)
head=cut(cut(head,box(-1.4,-.28,4.55,2.8,.56,.6)),box(-.28,-1.4,4.55,.56,2.8,.6))
parts.append((head,SILVER));parts.append((ring(0,0,-2.6,1,2.3,1.1),SILVER))
models['M2_support_assembly']=parts
# RM520N-GL 3052 outline, gold fingers and RF connectors from manufacturer p72.
# Origin at module top mounting notch. The inserted edge is y=52.
pcb=box(-15,0,2.49,30,48,.8)
pcb=cut(pcb,cyl(0,0,2.48,1.75,.83))
parts=[(pcb,GREEN),(box(-9.925,48,2.49,19.85,4,.8),GREEN)]
# B-key gap at the connector end; orientation follows the module top view.
parts[-1]=(cut(parts[-1][0],box(4.375,48.5,2.48,1.5,3.6,.83)),GREEN)
for x in [-8.925+.5*i for i in range(38)]:
 if 4.1<x<6:continue
 parts.append((box(x-.175,49,3.285,.35,2.8,.012),GOLD))
shield=box(-14.65,3.8,3.29,29.3,43.8,1.15)
# Inset top lid and seam; opaque silver rather than a clearance slab.
parts.extend([(shield,SILVER),(box(-14.3,4.1,4.44,28.6,43.2,.07),(.75,.77,.78)),(box(-12.5,8,4.51,25,29,.025),WHITE)])
for x in [-13.3,-8.8,-4.3,4.3,8.8,13.3]:
 parts.extend([(box(x-.9,1,3.29,1.8,1.8,.15),GOLD),(ring(x,1.9,3.44,.45,.75,.55),GOLD),(cyl(x,1.9,3.44,.18,.45),GOLD)])
# A restrained identity label; no fabricated serial number or regulatory marks.
# Vector block lettering is deliberately a visualization annotation, not an exact label.
font={'R':['1110','1001','1110','1010','1001'],'M':['10001','11011','10101','10001','10001'],'5':['1111','1000','1110','0001','1110'],'2':['1110','0001','0110','1000','1111'],'0':['0110','1001','1001','1001','0110'],'N':['1001','1101','1011','1001','1001'],'G':['0111','1000','1011','1001','0111'],'L':['1000','1000','1000','1000','1111'],'-':['000','000','111','000','000']}
x=-10.5
for ch in 'RM520N-GL':
 glyph=font[ch]
 for row,line in enumerate(glyph):
  for col,on in enumerate(line):
   if on=='1':parts.append((box(x+col*.4,12+row*.4,4.536,.35,.35,.015),BLACK))
 x+=(len(glyph[0])+1)*.4
models['RM520N_GL_Detailed']=parts
outputs=[P/'models'/(n+ext) for n in models for ext in ['.step','.wrl']]+[P/'build/detailed-model-register.json']
preflight(P,'carrier-detailed-models',outputs)
report={}
for name,parts in models.items():
 doc=TDocStd_Document(TCollection_ExtendedString('BinXCAF'))
 shape_tool=XCAFDoc_DocumentTool.ShapeTool_s(doc.Main());color_tool=XCAFDoc_DocumentTool.ColorTool_s(doc.Main())
 vrml=['#VRML V2.0 utf8\n# Reconstructed CAD; see model-sources.md.\n']
 bounds=Bnd_Box()
 for shape,color in parts:
  label=shape_tool.AddShape(shape,False);color_tool.SetColor(label,Quantity_Color(*color,Quantity_TOC_RGB),XCAFDoc_ColorGen)
  BRepBndLib.Add_s(shape,bounds);BRepMesh_IncrementalMesh(shape,.035,False,.25,True)
  ex=TopExp_Explorer(shape,TopAbs_FACE);vertices=[];faces=[]
  while ex.More():
   face=TopoDS.Face(ex.Current());loc=TopLoc_Location();mesh=BRep_Tool.Triangulation_s(face,loc)
   if mesh is not None:
    base=len(vertices)
    for i in range(1,mesh.NbNodes()+1):
     v=mesh.Node(i).Transformed(loc.Transformation());vertices.append([v.X()/2.54,v.Y()/2.54,v.Z()/2.54])
    for i in range(1,mesh.NbTriangles()+1):
     ids=list(mesh.Triangle(i).Get())
     if face.Orientation()==TopAbs_REVERSED:ids.reverse()
     faces.append([base+j-1 for j in ids])
   ex.Next()
  pts=', '.join(' '.join(f'{v:.6f}' for v in a) for a in vertices)
  inds=', '.join(' '.join(map(str,a+[-1])) for a in faces)
  vrml.append('Shape { appearance Appearance { material Material { diffuseColor '+' '.join(map(str,color))+' } } geometry IndexedFaceSet { coord Coordinate { point [ '+pts+' ] } coordIndex [ '+inds+' ] creaseAngle 0.6 solid TRUE } }\n')
 writer=STEPCAFControl_Writer();writer.SetColorMode(True);writer.Transfer(doc,STEPControl_AsIs);writer.Write(str(P/'models'/(name+'.step')))
 (P/'models'/(name+'.wrl')).write_text(''.join(vrml))
 lo,hi=bounds.CornerMin(),bounds.CornerMax();report[name]={'components':len(parts),'bounds_mm':[lo.X(),lo.Y(),lo.Z(),hi.X(),hi.Y(),hi.Z()],'provenance':'Reconstructed from source drawings; see model-sources.md'}
outputs[-1].write_text(json.dumps(report,indent=2)+'\n');record(P,'carrier-detailed-models',outputs)
print('Generated',len(models),'detailed assembly models')
