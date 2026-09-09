"""Safety-relevant connector and timing topology checks against exported nets."""
from pathlib import Path
import unittest
import xml.etree.ElementTree as ET

class CarrierControls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        tree=ET.parse(Path(__file__).resolve().parents[1]/'carrier/build/carrier.xml')
        cls.nets={(p.attrib['ref'],p.attrib['pin']):n.attrib['name'].lstrip('/')
                  for n in tree.findall('.//nets/net') for p in n.findall('node')}

    def pins(self,ref,expected):
        for pin,net in expected.items():
            self.assertEqual(self.nets.get((ref,str(pin))),net,(ref,pin))

    def test_power_requires_source_profile_and_manual_request(self):
        self.pins('U501',{1:'USB_3A_OK',2:'PROFILE_OK',4:'POWER_PERMIT'})
        self.pins('U502',{1:'POWER_PERMIT',2:'POWER_REQUEST',4:'BUCK_ENABLE'})

    def test_control_supply_and_run_are_delayed_after_rail(self):
        self.pins('U503',{1:'MODEM_VCC',2:'GND',3:'BUCK_ENABLE',4:'AUX_3V3',5:'RAIL_DELAY_CT',6:'DRIVE_ALLOWED'})
        self.pins('U504',{1:'MODEM_VCC',2:'GND',3:'DRIVE_ALLOWED',5:'MODEM_CTRL_1V8'})
        self.pins('U506',{1:'MODEM_VCC',3:'RUN_PERMIT',5:'RUN_DELAY_CT',6:'RUN_ALLOWED'})
        self.pins('U507',{2:'RUN_ALLOWED',4:'USB_MUX_OFF'})

    def test_fcpo_and_reset_only_have_open_drain_host_drivers(self):
        self.pins('Q501',{1:'USB_MUX_OFF',2:'GND',3:'FCPO_N'})
        self.pins('Q502',{1:'RESET_PULSE',2:'GND',3:'MODEM_RESET_N'})
        self.pins('U508',{1:'RESET_BUTTON_N',2:'GND',3:'RESET_RSET',4:'RESET_DIV',5:'AUX_3V3',6:'RESET_PULSE'})

    def test_sierra_shutdown_status_is_profile_isolated(self):
        self.pins('J201',{28:'PROFILE_PIN28'})
        self.pins('J202',{17:'PROFILE_PIN28',18:'SIERRA_PLA_STATUS'})

if __name__=='__main__':
    unittest.main()
