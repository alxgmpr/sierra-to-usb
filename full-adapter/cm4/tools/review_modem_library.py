"""Generate a clearly labelled library review fixture, never a carrier PCB."""
from pathlib import Path
import subprocess
import sexpdata as sx
from cad import ROOT, nodes, one

KICAD='/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli'
OUT=ROOT/'build/modem-library'
OUT.mkdir(exist_ok=True)
names=['Amphenol_MDT420B01411','Xunpu_SMN303_ARP7','TI_DPY0002_TPD1E05U06']
header='''(kicad_pcb (version 20260206) (generator "cm4-library-review")
  (general (thickness 1.6)) (paper "A4")
  (layers (0 "F.Cu" signal) (2 "B.Cu" signal) (1 "F.Mask" user)
    (3 "B.Mask" user) (5 "F.SilkS" user) (7 "B.SilkS" user)
    (13 "F.Paste" user) (15 "B.Paste" user) (17 "Dwgs.User" user)
    (19 "Cmts.User" user) (25 "Edge.Cuts" user) (31 "F.CrtYd" user)
    (29 "B.CrtYd" user) (35 "F.Fab" user) (33 "B.Fab" user))
  (setup (pad_to_mask_clearance 0)))'''
board=sx.loads(header)
for i,(name,x,y) in enumerate(zip(names,[25,59,85],[25,19,25])):
    path=ROOT/'lib/cm4.pretty'/(name+'.kicad_mod')
    f=sx.loads(path.read_text());f[1]='cm4:'+name
    f.append([sx.Symbol('at'),x,y,0])
    next(p for p in nodes(f,'property') if p[1]=='Reference')[2]=['J200','J201','D230'][i]
    for model in nodes(f,'model'):
        model[1]=model[1].replace('${KIPRJMOD}/../lib',str(ROOT/'lib'))
    board.append(f)
    subprocess.run([KICAD,'fp','export','svg','--layers','F.Cu,F.Fab,F.CrtYd,Dwgs.User',
        '--sketch-pads-on-fab-layers','--sketch-pad-numbers','--footprint',name,'-o',str(OUT),str(path.parent)],check=True)
for a,b in [((5,5),(110,5)),((110,5),(110,40)),((110,40),(5,40)),((5,40),(5,5))]:
    board.append(sx.loads(f'(gr_line (start {a[0]} {a[1]}) (end {b[0]} {b[1]}) (stroke (width .1) (type default)) (layer "Edge.Cuts"))'))
board.append(sx.loads('(gr_text "LIBRARY REVIEW ONLY - NOT THE CARRIER" (at 58 9) (layer "F.SilkS") (effects (font (size 1 1) (thickness .15))))'))
path=OUT/'library-review-only.kicad_pcb';path.write_text(sx.dumps(board))
subprocess.run([KICAD,'pcb','render','--width','1800','--height','1100','--background','opaque',
    '--rotate','-35,0,15','--floor','-o',str(OUT/'library-models.png'),str(path)],check=True)
print('Library fixture is ignored review output and contains no carrier circuitry.')
