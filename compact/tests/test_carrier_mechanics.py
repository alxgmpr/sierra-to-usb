from pathlib import Path
import unittest
import sexpdata as sx

class CarrierMechanics(unittest.TestCase):
    def test_no_cooler_retention_or_service_placeholders(self):
        p=Path(__file__).resolve().parents[1]/'carrier/carrier.kicad_pcb'
        board=sx.loads(p.read_text())
        footprints=[x for x in board if isinstance(x,list) and str(x[0])=='footprint']
        refs={v[2] for f in footprints for v in f if isinstance(v,list) and str(v[0])=='property' and v[1]=='Reference'}
        self.assertFalse(refs & {'H6','H7','H8','H9','MECH2','MECH3','MECH4','MECH5'})
        self.assertTrue({'H1','H2','H3','H4','H5','J202'}.issubset(refs))
        for name in ['Heatsink_envelope','Retention_frame','Retention_post','Profile_service_envelope','TIM_8810']:
            self.assertNotIn(name,p.read_text())

    def test_rounded_outline_and_symmetric_corner_mounts(self):
        p=Path(__file__).resolve().parents[1]/'carrier/carrier.kicad_pcb'
        b=sx.loads(p.read_text())
        def nodes(a,k):return [x for x in a if isinstance(x,list) and str(x[0])==k]
        def node(a,k):return next(iter(nodes(a,k)),None)
        edges=[x for x in b if isinstance(x,list) and node(x,'layer')==[sx.Symbol('layer'),'Edge.Cuts']]
        self.assertEqual(sum(str(x[0])=='gr_arc' for x in edges),8)
        fps={next(v[2] for v in nodes(f,'property') if v[1]=='Reference'):f for f in nodes(b,'footprint')}
        for ref,xy in {'H1':[4,-3],'H2':[106,-3],'H3':[4,103],'H4':[106,103]}.items():
            self.assertEqual(node(fps[ref],'at')[1:3],xy)
        self.assertIn('H10',fps)
        self.assertEqual(node(fps['H10'],'at')[1:3],[55,35.75])
        self.assertFalse(nodes(fps['H10'],'model'),'Unused short-card support must not touch a longer card')

    def test_detailed_connector_card_and_support_models(self):
        p=Path(__file__).resolve().parents[1]/'carrier/carrier.kicad_pcb'
        s=p.read_text()
        for name in ['IDC_3M_N2520_Detailed','M2_MDT420_Detailed','RM520N_GL_Detailed','M2_support_assembly']:
            self.assertTrue(name in s,name)
        for name in ['N2520_envelope','MDT420_envelope','Module_EM9190_max_envelope','Module_support.wrl']:
            self.assertFalse(name in s,name)
