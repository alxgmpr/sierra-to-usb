from pathlib import Path
import unittest
import xml.etree.ElementTree as ET


class CarrierInterfaces(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        root=ET.parse(Path(__file__).resolve().parents[1]/'carrier/build/carrier.xml')
        cls.nets={(n.attrib['ref'],n.attrib['pin']):net.attrib['name'].lstrip('/')
                  for net in root.findall('.//nets/net') for n in net.findall('node')}

    def test_usb2_switch_has_separate_host_and_modem_ports(self):
        for pin,net in {1:'MOD_USB_D_P',2:'MOD_USB_D_N',5:'GND',6:'USB_MUX_OFF',
                        7:'USB_D_N',8:'USB_D_P',9:'GND',10:'AUX_3V3'}.items():
            self.assertEqual(self.nets.get(('U105',str(pin))),net)

    def test_sim_protection_is_in_module_voltage_domain(self):
        for pin,net in {1:'SIM_VDD',2:'SIM_SOCKET_RST',3:'GND',4:'SIM_SOCKET_CLK',
                        5:'SIM_SOCKET_DATA',8:'GND'}.items():
            self.assertEqual(self.nets.get(('D203',str(pin))),net)

    def test_five_independent_antenna_paths(self):
        for i in range(5):
            net = 'RF_GPS' if i == 4 else f'RF{i+1}'
            mhf, sma = f'J{601+2*i}', f'J{602+2*i}'
            self.assertEqual({p for p, n in self.nets.items() if n == net},
                             {(mhf, '1'), (sma, '1')})
            self.assertEqual(self.nets.get((mhf, '2')), 'GND')
            self.assertEqual(self.nets.get((sma, '2')), 'GND')

    def test_programming_clock_is_accessible(self):
        self.assertEqual(self.nets.get(('J102','3')),'CC_SCL')
        self.assertEqual(self.nets.get(('J102','4')),'CC_SDA')


if __name__=='__main__':
    unittest.main()
