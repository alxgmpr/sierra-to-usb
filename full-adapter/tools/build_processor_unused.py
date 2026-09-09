"""Explicit terminations for unpowered display/camera and PCIe3 interfaces."""
import json
from schematic import ROOT, Sheet


def processor_unused():
    s = Sheet('processor-unused','Unused processor display, camera and PCIe3 interfaces')
    manifest = json.loads((ROOT/'research/core-symbols.json').read_text())['RK3568B2']
    locations = {42:(81.28,73.66),18:(220.98,73.66),26:(350.52,73.66),
                 33:(81.28,167.64),36:(220.98,167.64),37:(350.52,167.64),39:(81.28,246.38)}
    for unit,(x,y) in locations.items():
        s.place('full-adapter:RK3568B2','U1',x,y,unit=unit)
        pins = manifest[unit-1]['pins']
        if unit == 42:
            positions = sorted([s.pins['U1',p['ball']] for p in pins],key=lambda p:p[1])
            bus = [(25.4,p[1]) for p in positions]
            for pin,end in zip(positions,bus):s.wire(pin,end)
            for a,b in zip(bus,bus[1:]):s.wire(a,b)
            for p in bus[1:-1]:s.junction(p)
            s.power('GND',bus[-1])
        else:
            for pin in pins:s.connect('U1',pin['ball'],None)
    s.text('Unused interfaces — no external signals may drive these pins.\nRockchip HW Guide V1.2 sections 2.2.2.11–2.2.2.15 recommend grounding unused PHY supplies.\nAll 14 dedicated supply balls connect to GND; signal balls have explicit no-connect markers.\nDisable PCIe3, CSI, DSI0/1, eDP and HDMI PHY/controller nodes in the device tree.\nUnpowered peripherals left enabled in DTS can hang kernel initialization (HW Guide p38).\nUSB3 and the independent PCIe2 Ethernet path use the powered combo PHYs on the preceding page.',162.56,231.14,1.15)
    return s
