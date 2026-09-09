from pathlib import Path
import math, unittest
import sexpdata as sx
class CarrierOrientation(unittest.TestCase):
    def test_usb_and_power_banks_face_their_destinations(self):
        b=sx.loads((Path(__file__).resolve().parents[1]/'carrier/carrier.kicad_pcb').read_text())
        def nodes(a,k):return [v for v in a if isinstance(v,list) and str(v[0])==k]
        def node(a,k):return next(iter(nodes(a,k)),None)
        fps={next(v[2] for v in nodes(f,'property') if v[1]=='Reference'):f for f in nodes(b,'footprint')}
        def y(ref,pin):
            f=fps[ref];at=node(f,'at');a=math.radians(at[3]);pads=[p for p in nodes(f,'pad') if str(p[1])==str(pin)]
            return sum(at[2]-node(p,'at')[1]*math.sin(a)+node(p,'at')[2]*math.cos(a) for p in pads)/len(pads)
        self.assertLess(y('U104',3),y('U104',19),'Common USB bank should face M.2 above mux')
        self.assertLess(y('U301',6),y('U301',5),'eFuse output should face shunt/buck above it')
        self.assertGreater(y('U401',6),y('U401',18),'SW faces inductor; FB faces quiet divider')
