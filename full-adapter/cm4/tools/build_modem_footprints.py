"""Manufacturer modem/SIM lands, using official KiCad Library Tools.

Models use maximum occupied envelopes, not invented detailed CAD.
The M.2 drawing origin is midway between its two locating holes.
"""
import cadquery as cq
from build_ethernet_footprints import base,write
from KicadModTree import FootprintType,Rectangle,Line,Pad,Text
from KicadModTree.nodes.base.Zone import Zone,Keepouts,Hatch
from cad import ROOT


def smd(f,n,x,y,w,h):
    f.append(Pad(number=str(n),type=Pad.TYPE_SMT,shape=Pad.SHAPE_RECT,
                 at=[x,y],size=[w,h],layers=Pad.LAYERS_SMT))


def keepout(f,name,x1,y1,x2,y2):
    f.append(Zone(layers=['F.Cu'],name=name,
        shape=[[x1,y1],[x2,y1],[x2,y2],[x1,y2]],
        keepouts=Keepouts(tracks=Keepouts.DENY,vias=Keepouts.DENY,
            copperpour=Keepouts.DENY,footprints=Keepouts.DENY),
        hatch=Hatch(style=Hatch.EDGE,pitch=.5)))


def build():
    name='Amphenol_MDT420B01411'
    f=base(name,FootprintType.SMD,'Amphenol CMDT420X0X411 A 2022-11-08 sheets1-2; key B; 1A/power contact; exact 0.30x1.55 lands',-7.2,4.2)
    f.append(Rectangle(start=[-11,-5.7],end=[11,1.5],layer='F.Fab',width=.1))
    f.append(Rectangle(start=[-11.5,-6.55],end=[11.5,3.55],layer='F.CrtYd',width=.05))
    for x in [-11.25,11.25]:f.append(Line(start=[x,-6.2],end=[x,3.2],layer='F.SilkS',width=.12))
    f.append(Line(start=[-9.6,-6.4],end=[-8.9,-6.4],layer='F.SilkS',width=.12))
    for n in range(1,76):
        if 12<=n<=19:continue
        x=-9.25+(n-1)*.25 if n%2 else -9+(n-2)*.25
        y=-5.275 if n%2 else 2.275
        smd(f,n,x,y,.3,1.55)
    for x in [-10.35,10.35]:smd(f,'SH',x,-4.5,1.2,2.75)
    for x,diam in [(-10,1.1),(10,1.6)]:
        f.append(Pad(number='',type=Pad.TYPE_NPTH,shape=Pad.SHAPE_CIRCLE,
                     at=[x,0],size=[diam,diam],drill=diam,layers=Pad.LAYERS_NPTH))
    f.append(Text(text='CARD INSERTION / +Y',at=[0,5],layer='Dwgs.User',size=[.8,.8],thickness=.12))
    model=cq.Workplane('XY').box(22,8.9,4.45,centered=(True,True,False)).translate((0,1.5,0))
    for x,diam in [(-10,1.05),(10,1.55)]:
        model=model.union(cq.Workplane('XY').circle(diam/2).extrude(.9).translate((x,0,-.9)))
    write(f,name,model)
    name='Xunpu_SMN303_ARP7'
    f=base(name,FootprintType.SMD,'SMN-303-ARP7 A: no locator posts, normally closed detect, 0.8x1.14 contact and 0.7x2.1 shield lands, 0.12mm stencil',-1.6,16)
    f.append(Rectangle(start=[-6.5,.57],end=[6.5,14.23],layer='F.Fab',width=.1))
    f.append(Rectangle(start=[-7.1,-.85],end=[7.1,14.8],layer='F.CrtYd',width=.05))
    for x in [-6.8,6.8]:f.append(Line(start=[x,3],end=[x,11.9],layer='F.SilkS',width=.12))
    for i,n in enumerate(['C3','C7','C2','C6','C1','C5']):smd(f,n,-4.83+1.27*i,0,.8,1.14)
    smd(f,'CD',2.47,0,.8,1.14)
    for x in [-6.5,6.5]:
        for y in [1.48,13.48]:smd(f,'SH',x,y,.7,2.1)
    # Entire interior is clear, stricter than the six moving-contact regions.
    keepout(f,'SIM moving contacts / no copper or vias',-5.95,.65,5.95,14.25)
    f.append(Rectangle(start=[-6.5,14.23],end=[6.5,24.23],layer='Dwgs.User',width=.1))
    f.append(Text(text='SIM EJECT / FINGER ACCESS',at=[0,20],layer='Dwgs.User',size=[.7,.7],thickness=.1))
    model=cq.Workplane('XY').box(13.35,14.07,1.52,centered=(True,True,False)).translate((0,-7.37,0))
    write(f,name,model)
    name='TI_DPY0002_TPD1E05U06'
    f=base(name,FootprintType.SMD,'TI DPY0002A 4224561/C 07/2024: 0.30x0.50 lands at0.70 pitch; IO1 GND2; NSMD option',-.85,.85)
    f.append(Rectangle(start=[-.525,-.325],end=[.525,.325],layer='F.Fab',width=.1))
    f.append(Rectangle(start=[-.75,-.55],end=[.75,.55],layer='F.CrtYd',width=.05))
    f.append(Line(start=[-.525,-.425],end=[0,-.425],layer='F.SilkS',width=.12))
    smd(f,1,-.35,0,.3,.5);smd(f,2,.35,0,.3,.5)
    write(f,name,cq.Workplane('XY').box(1.05,.65,.45,centered=(True,True,False)))
    for name in ['Amphenol_MDT420B01411','Xunpu_SMN303_ARP7','TI_DPY0002_TPD1E05U06']:
        p=ROOT/'lib/cm4.3dshapes'/(name+'.step')
        p.write_text('\n'.join(line.rstrip() for line in p.read_text().splitlines())+'\n')


if __name__=='__main__':build()
