"""Read back STEP bounds and check the drawn assembly's physical reservations."""
from pathlib import Path
import json
from OCP.STEPControl import STEPControl_Reader
from OCP.Bnd import Bnd_Box
from OCP.BRepBndLib import BRepBndLib
P=Path(__file__).resolve().parent
r=json.loads((P/'build/model-register.json').read_text());results=[]
for name,d in r['models'].items():
 reader=STEPControl_Reader();assert int(reader.ReadFile(str(P/'models'/(name+'.step'))))==1
 reader.TransferRoots();b=Bnd_Box();BRepBndLib.Add_s(reader.OneShape(),b)
 lo,hi=b.CornerMin(),b.CornerMax();actual=[lo.X(),lo.Y(),lo.Z(),hi.X(),hi.Y(),hi.Z()];parts=[]
 for x,y,z,X,Y,Z in d['boxes']:parts.append([x,-Y,z,X,-y,Z])
 for x,y,z,radius,height in d.get('cylinders',[]):parts.append([x-radius,-y-radius,z,x+radius,-y+radius,z+height])
 expected=[min(v[i] for v in parts) if i<3 else max(v[i] for v in parts) for i in range(6)]
 err=max(abs(a-e) for a,e in zip(actual,expected));assert err<1e-5,(name,actual,expected)
 results.append({'model':name,'STEP_bounds_mm':actual,'expected_bounds_mm':expected,'max_error_mm':err})
# Re-read the detailed STEP files independently of the generator.
from OCP.BRepCheck import BRepCheck_Analyzer
for name,d in json.loads((P/'build/detailed-model-register.json').read_text()).items():
 reader=STEPControl_Reader();assert int(reader.ReadFile(str(P/'models'/(name+'.step'))))==1
 reader.TransferRoots();shape=reader.OneShape();assert BRepCheck_Analyzer(shape).IsValid(),name
 b=Bnd_Box();BRepBndLib.Add_s(shape,b);lo,hi=b.CornerMin(),b.CornerMax()
 actual=[lo.X(),lo.Y(),lo.Z(),hi.X(),hi.Y(),hi.Z()]
 err=max(abs(a-e) for a,e in zip(actual,d['bounds_mm']));assert err<1e-5,(name,err)
 results.append({'model':name,'STEP_bounds_mm':actual,'max_error_mm':err,'valid_BRep':True,'provenance':d['provenance']})
report={'status':'PASS STEP bounds readback and detailed model BRep validity; not assembly interference certification','models':results,'limitations':['Register includes inactive legacy envelopes as well as active detailed reconstructed models. See model-sources.md for active assignments.','Detailed geometry simplifies contact spring shapes, threads and molding. Actual socket insertion, screw seating and support height require first-article checks.','Adhesive heatsink and coax cables are unmodeled.','Standard KiCad package models are outside these custom-model checks.']}
(P/'build/model-checks.json').write_text(json.dumps(report,indent=2)+'\n')
print('Read-back bounds verified for',len(results),'custom STEP files, including four detailed valid models.')
