"""Review drawing; not a fabrication or machining release."""
from pathlib import Path
import json
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A3,landscape
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor
P=Path(__file__).resolve().parent
c=canvas.Canvas(str(P/'build/mechanical-drawing.pdf'),pagesize=landscape(A3))
W,H=landscape(A3)
def txt(x,y,t,size=9,color='#172c3c'):
 c.setFillColor(HexColor(color));c.setFont('Helvetica',size);c.drawString(x*mm,y*mm,t)
def line(x,y,X,Y,color='#617888',width=.5):
 c.setStrokeColor(HexColor(color));c.setLineWidth(width);c.line(x*mm,y*mm,X*mm,Y*mm)
def rect(x,y,w,h,color='#617888',fill=None):
 c.setStrokeColor(HexColor(color));c.setLineWidth(.6)
 if fill:c.setFillColor(HexColor(fill))
 c.rect(x*mm,y*mm,w*mm,h*mm,fill=bool(fill),stroke=1)
def title(t,n):
 txt(16,280,t,20);txt(16,271,'Compact USB-C modem carrier | 110 x 114 mm overall | 1.50 +/-0.05 mm PCB | UNROUTED',10)
 line(16,266,404,266);txt(16,12,'Review only. Verify mating stack, cooling and harness dressing on first article. All dimensions in mm.',9)
 txt(385,12,f'{n} / 1',9)
def para(x,y,lines):
 for t in lines:txt(x,y,t);y-=5
 return y

title('Mechanical plan and service access',1)
s=1.8;ox,oy=30,235
xy=lambda x,y:(ox+s*x,oy-s*y)
def brect(x,y,w,h,color,fill=None):
 X,Y=xy(x,y+h);rect(X,Y,w*s,h*s,color,fill)
def blabel(x,y,t,size=8):
 X,Y=xy(x,y);txt(X,Y,t,size)
# Rounded ear outline; circular arcs use cubic Bezier equivalents.
p=c.beginPath()
def move(x,y):
 X,Y=xy(x,y);p.moveTo(X*mm,Y*mm)
def edge(x,y):
 X,Y=xy(x,y);p.lineTo(X*mm,Y*mm)
def curve(a,b,end):
 pts=[xy(*v) for v in [a,b,end]];p.curveTo(*[z*mm for pt in pts for z in pt])
k=.5522847498
move(9,0);edge(101,0);curve((101+k,0),(102,-1+k),(102,-1));edge(102,-3)
curve((102,-3-4*k),(106-4*k,-7),(106,-7));curve((106+4*k,-7),(110,-3-4*k),(110,-3));edge(110,103)
curve((110,103+4*k),(106+4*k,107),(106,107));curve((106-4*k,107),(102,103+4*k),(102,103));edge(102,101)
curve((102,101-k),(101+k,100),(101,100));edge(9,100);curve((9-k,100),(8,101-k),(8,101));edge(8,103)
curve((8,103+4*k),(4+4*k,107),(4,107));curve((4-4*k,107),(0,103+4*k),(0,103));edge(0,-3)
curve((0,-3-4*k),(4-4*k,-7),(4,-7));curve((4+4*k,-7),(8,-3-4*k),(8,-3));edge(8,-1)
curve((8,-1+k),(9-k,0),(9,0));p.close()
c.setStrokeColor(HexColor('#223f50'));c.setFillColor(HexColor('#f6fafb'));c.drawPath(p,fill=1,stroke=1)
brect(39.775,25.6,30.45,52.3,'#576e7d','#e1e9ee')
for x in [15,35,55,75,95]:
 brect(x-5.1,-12.7,10.2,17.45,'#947322','#f6edc7')
 X,Y=xy(x,12);c.setStrokeColor(HexColor('#658caa'));c.circle(X*mm,Y*mm,3.8*s*mm)
 blabel(x-3,8,'GPS' if x==95 else 'RF'+str([15,35,55,75,95].index(x)+1))
for ref,x,y,d in [('H1',4,-3,2.7),('H2',106,-3,2.7),('H3',4,103,2.7),('H4',106,103,2.7),('H5',55,25.75,2.2),('H10',55,35.75,2.2)]:
 X,Y=xy(x,y);c.setStrokeColor(HexColor('#172c3c'));c.circle(X*mm,Y*mm,d/2*s*mm);txt(X+2,Y+1,ref,8)
brect(44,72.95,22,7.2,'#172c3c','#b7c6ce');blabel(46,76,'J201 / SOCKET')
brect(50.1,89.8,9.8,9.9,'#172c3c');blabel(49,103,'USB-C')
brect(.5,73,15,14,'#172c3c');blabel(2,90,'SIM -> LEFT')
brect(73.07,89.435,32.72,8.59,'#172c3c');blabel(77,94,'KEYED PROFILE')
for t,x,y in [('POWER',100,36),('RUN',100,50),('RESET',100,64),('RF OFF',100,75)]:
 X,Y=xy(x,y);rect(X-5,Y-3,10,6,'#526976');txt(X-4,Y+4,t,7)
blabel(43,45,'M.2 module envelope')
# Overall dimensions.
line(ox,oy-188,ox+198,oy-188);line(ox,oy-185,ox,oy-191);line(ox+198,oy-185,ox+198,oy-191);txt(ox+94,oy-194,'110',10)
line(ox-10,oy+12.6,ox-10,oy-192.6);line(ox-13,oy+12.6,ox-7,oy+12.6);line(ox-13,oy-192.6,ox-7,oy-192.6);txt(ox-23,oy-92,'114',10)
para(245,250,[
 'Datum: left edge / SMA launch line (0,0).',
 'All anchors are locked in the placement source.',
 'SMA axes: X15 / 35 / 55 / 75 / 95, Y0; pitch20.',
 'Reserve16 diameter coupling/wrench access per SMA.',
 'External antenna approach: at least25 beyond edge.',
 'MHF4 carrier tool-access circles: diameter7.6.',
 '',
 'Mounting-hole centres (X,Y), finished NPTH:',
 'H1 (4,-3), H2 (106,-3), H3 (4,103), H4 (106,103):2.7',
 'H5 3052 (55,25.75); H10 3042 (55,35.75):2.2',
 '',
 'Module support location follows the1.75 card stop',
 'setback and52 /42 card lengths. Verify actual seating.',
 'Nominal underside height2.49 above carrier.',
 '',
 'Adhesive heatsink: selected at assembly; not modeled.',
 'No carrier-mounted cooler frame or retention posts.',
 'Fit ONE removable support, H5 or H10; never both.',
 '',
 'Four cellular + optional fifth GPS CAB.01072,100 mm.',
 'Dress in open upper/side spaces; target radius>=15.',
 'This radius is an engineering target, not a cable rating.',
 'Keep coax clear of the adhesive heatsink attachment.',
 'Cable length and tool access: fit-test gates.',
 '',
 'Profile connector:22 mm total vertical reservation.',
 'Reserve25 mm tail/splice access outside bottom edge.',
 'USB plug approach:16 mm wide beyond bottom edge.',
 'SIM card approach:25 mm outside left edge.',
 'J202: standard keyed20-pin IDC profile connection.'
])
c.save()
