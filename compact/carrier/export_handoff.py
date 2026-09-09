"""Read-only design checks and review exports; never routes or fills the PCB."""
from pathlib import Path
import json,os,subprocess,sys
P=Path(__file__).resolve().parent
B=P/'build';K='/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli'
def run(args,log=None,env=None):
 if log:
  with (B/log).open('w') as out:subprocess.run(list(map(str,args)),check=True,stdout=out,stderr=subprocess.STDOUT,env=env)
 else:subprocess.run(list(map(str,args)),check=True,env=env)
run([sys.executable,P/'export_review.py'],'schematic-export.log')
run([sys.executable,'-m','unittest','discover','-s',P.parent/'tests'],'unit-tests.log')
run([K,'pcb','drc','--format','json','--schematic-parity','-o',B/'placement-drc.json',P/'carrier.kicad_pcb'])
run([sys.executable,P/'check_board.py'])
run([sys.executable,P/'check_models.py'])
run([sys.executable,P/'stackup.py'])
for name in ['replacement-power-budget.py','carrier-auxiliary-budget.py','carrier-buck-loss-envelope.py','carrier-loop-model.py']:
 run([sys.executable,P.parent/'review'/name],name+'.log')
run([K,'pcb','export','pdf','--layers','F.Fab,F.CrtYd,F.Cu,Edge.Cuts,Dwgs.User,User.1','--mode-single','--scale','2','-o',B/'placement-drawing.pdf',P/'carrier.kicad_pcb'])
run([K,'pcb','export','svg','--layers','F.Cu,F.SilkS,Edge.Cuts','--fit-page-to-board','--exclude-drawing-sheet','-o',B/'board-svg',P/'carrier.kicad_pcb'])
run([K,'pcb','export','pos','--format','csv','--units','mm','-o',B/'component-positions.csv',P/'carrier.kicad_pcb'])
run([K,'pcb','export','step','--force','--subst-models','-o',B/'assembly-envelopes.step',P/'carrier.kicad_pcb'],'step-export.log')
assert 'Could not add 3D model' not in (B/'step-export.log').read_text()
env=dict(os.environ,KICAD_CONFIG_HOME=str(B/'viewer-config'))
for name,extra in [('isometric',['--rotate','315,0,30','--zoom','.75']),('top',['--side','top','--zoom','.85'])]:
 run([K,'pcb','render','--preset','follow_pcb_editor','--width','1800','--height','1400','--quality','high',*extra,'-o',B/f'assembly-3d-{name}.png',P/'carrier.kicad_pcb'],f'render-{name}.log',env)
print('Review exports and checks complete. Visual review and final summary remain separate.')
