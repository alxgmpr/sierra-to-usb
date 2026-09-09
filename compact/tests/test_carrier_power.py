"""Independent numeric pin assertions against KiCad's exported netlist."""
from pathlib import Path
import unittest
import xml.etree.ElementTree as ET


class CarrierPower(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        root = ET.parse(Path(__file__).resolve().parents[1] / 'carrier/build/carrier.xml')
        cls.nets = {
            (n.attrib['ref'], n.attrib['pin']): net.attrib['name'].lstrip('/')
            for net in root.findall('.//nets/net') for n in net.findall('node')
        }

    def test_protected_auxiliary_supply(self):
        # TPS259470 RPW pin table; TPS7A2033 DBV pin table.
        for endpoint, net in {
            ('U301', '5'): 'USB_VBUS', ('U301', '6'): 'PROTECTED_VBUS',
            ('U301', '8'): 'GND', ('U302', '1'): 'SENSED_VBUS',
            ('U302', '2'): 'GND', ('U302', '3'): 'SENSED_VBUS',
            ('U302', '5'): 'AUX_3V3',
        }.items():
            with self.subTest(endpoint=endpoint):
                self.assertEqual(self.nets.get(endpoint), net)

    def test_input_current_sense_polarity(self):
        # INA190A1 DCK, SBOS863D p3: REF/GND/VS/IN+/IN-/OUT.
        expected = {1:'GND',2:'GND',3:'AUX_3V3',4:'INPUT_SENSE_P',
                    5:'INPUT_SENSE_N',6:'INPUT_CURRENT_MON'}
        for pin, net in expected.items():
            with self.subTest(pin=pin):
                self.assertEqual(self.nets.get(('U303',str(pin))),net)

    def test_buck_power_pins_and_passive_current_override(self):
        # ADI LTC3310S Rev F p10; ITH is the current-command node.
        for pin in (3,4,11,12):
            self.assertEqual(self.nets.get(('U401',str(pin))),'SENSED_VBUS')
        for pin in (5,10,19):
            self.assertEqual(self.nets.get(('U401',str(pin))),'GND')
        for pin in (6,7,8,9):
            self.assertEqual(self.nets.get(('U401',str(pin))),'BUCK_SW')
        self.assertEqual(self.nets.get(('U401','1')),'BUCK_ENABLE')
        self.assertEqual(self.nets.get(('U401','17')),'BUCK_ITH')
        self.assertEqual(self.nets.get(('D401','2')),'BUCK_ITH')
        self.assertEqual(self.nets.get(('D401','1')),'CURRENT_CLAMP')


class KelvinShunt(unittest.TestCase):
    def test_sense_paths_do_not_share_force_nets(self):
        tree=ET.parse(Path(__file__).resolve().parents[1]/'carrier/build/carrier.xml')
        nets={(p.attrib['ref'],p.attrib['pin']):n.attrib['name'].lstrip('/')
              for n in tree.findall('.//nets/net') for p in n.findall('node')}
        for pin,net in {1:'PROTECTED_VBUS',2:'SENSED_VBUS',3:'INPUT_SENSE_P',4:'INPUT_SENSE_N'}.items():
            self.assertEqual(nets.get(('R307',str(pin))),net)
        self.assertEqual(nets[('U303','4')],'INPUT_SENSE_P')
        self.assertEqual(nets[('U303','5')],'INPUT_SENSE_N')

if __name__ == '__main__':
    unittest.main()
