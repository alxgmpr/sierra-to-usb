"""Build two physical 100-contact sockets from the reviewed CM4 pin table.

J100 uses CM4 pins 1..100. J101 contact n maps to CM4 pin n+100.
The electrical types describe the plugged-in module, not a generic connector.
"""
from collections import OrderedDict
from pathlib import Path
import copy
import json
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'tools'))
from build_core_symbols import make_symbol
from cad import ROOT, STD, nodes, one
import sexpdata as sx


def build():
    source = json.loads((ROOT / 'research/cm4-pins.json').read_text())['pins']
    all_symbols, manifest = [], {}
    for connector, offset in [('CM4_J1', 0), ('CM4_J2', 100)]:
        groups = OrderedDict((title, []) for title in (
            ['Power and ground', 'GPIO', 'microSD', 'Gigabit Ethernet', 'System control']
            if offset == 0 else ['PCIe and USB recovery', 'Ground', 'Unused CSI', 'Unused DSI', 'Unused HDMI and reserved']))
        for n in range(offset+1, offset+101):
            src = source[str(n)]
            name = src['datasheet_name'].replace(' (Input)', '').replace(' (Output)', '')
            name = {'+5V':'VCC5V_CM4', 'CM4_3.3V':'CM4_3V3', 'CM4_1.8V':'CM4_1V8'}.get(name, name)
            typ, side = 'bidirectional', 'R'
            if name == 'GND':
                typ, side = 'power_in', 'B'
            elif name == 'VCC5V_CM4' or name == 'GPIO_VREF':
                typ, side = 'power_in', 'T'
            elif name in ('CM4_3V3', 'CM4_1V8'):
                typ, side = 'power_out', 'R'
            elif name in ('nEXTRST', 'PCIe_nRST', 'SD_PWR_ON', 'Ethernet_SYNC_OUT', 'SD_CLK'):
                typ = 'output'
            elif name in ('GLOBAL_EN', 'nRPIBOOT', 'EEPROM_nWP', 'SD_VDD_OVERRIDE', 'USB_OTG_ID', 'PCIe_CLK_nREQ', 'Ethernet_SYNC_IN'):
                typ, side = 'input', 'L'
            elif name.startswith('PCIe_RX'):
                typ, side = 'input', 'L'
            elif name.startswith(('PCIe_TX', 'PCIe_CLK_')):
                typ = 'output'
            elif name.startswith(('Ethernet_Pair', 'USB_')):
                typ = 'passive'
            elif name.startswith('Ethernet_nLED') or name == 'Pi_nLED_Activity':
                typ = 'open_collector'
            elif name == 'Reserved':
                typ = 'passive'
            if offset == 0:
                if name in ('GND','VCC5V_CM4','GPIO_VREF','CM4_3V3','CM4_1V8'):
                    group = 'Power and ground'
                elif name.startswith('GPIO') or name in ('ID_SC','ID_SD'):
                    group = 'GPIO'
                elif name.startswith('SD_'):
                    group = 'microSD'
                elif name.startswith('Ethernet'):
                    group = 'Gigabit Ethernet'
                else:
                    group = 'System control'
            else:
                if name == 'GND': group = 'Ground'
                elif name.startswith(('PCIe','USB')): group = 'PCIe and USB recovery'
                elif name.startswith('CAM'): group = 'Unused CSI'
                elif name.startswith('DSI'): group = 'Unused DSI'
                else: group = 'Unused HDMI and reserved'
            # These internally pulled-up controls explicitly permit open circuit.
            if name in ('GLOBAL_EN','nRPIBOOT','EEPROM_nWP'):
                typ='passive'
            groups[group].append({'ball':str(n-offset), 'cm4_pin':n, 'name':name,
                'display_name':name, 'type':typ, 'side':side})
        # Avoid one long power-pin row, retaining each physical contact explicitly.
        for p in groups[next(iter(groups))]:
            if p['name']=='VCC5V_CM4': p['side']='L'
            if p['name']=='GPIO_VREF': p['side']='R'
        if not offset:
            group=groups['Power and ground']
            for net in ['VCC5V_CM4','CM4_3V3','CM4_1V8']:
                related=[p for p in group if p['name']==net]
                first=related[0]
                first['physical_pins']=[p['ball'] for p in related]
                first['ball']='['+','.join(first['physical_pins'])+']'
                group[:]=[p for p in group if p is first or p not in related]
        sym, units = make_symbol(connector, 'cm4:Hirose_DF40C-100DS-0.4V_2x50_P0.4mm',
            source_url, 'Hirose', 'C3642394',
            'DF40C-100DS-0.4V(58), CM4 socket; physical contact numbering', groups,
            keywords='CM4 Lite connector', footprint_filter='Hirose?DF40C?100DS*',side_pins_from_top=True)
        sym = sym.replace('(property "Reference" "U"', '(property "Reference" "J"')
        sym = sym.replace(f'(property "MPN" "{connector}"', '(property "MPN" "DF40C-100DS-0.4V(58)"')
        all_symbols.append(sym)
        manifest[connector]=units
    ps = [dict(ball=n,name=name,type=typ,side=side) for n,name,typ,side in [
        ('5','IN','power_in','L'),('4','EN','input','L'),
        ('1','OUT','power_out','R'),('3','~{FLG}','open_collector','R'),('2','GND','power_in','B')]]
    sym, units = make_symbol('RT9742GGJ5','Package_TO_SOT_SMD:TSOT-23-5',
        'https://www.richtek.com/assets/product_file/RT9742/DS9742-10.pdf',
        'Richtek','C250547','1 A active-high switch with output discharge',
        {'microSD power switch':ps},keywords='power switch',footprint_filter='TSOT*23*5*')
    all_symbols.append(sym);manifest['RT9742GGJ5']=units
    from ethernet_symbols import build as ethernet_symbols
    added, added_manifest = ethernet_symbols(make_symbol)
    all_symbols.extend(added)
    manifest.update(added_manifest)
    from power_input_symbols import build as power_input_symbols
    added, added_manifest = power_input_symbols(make_symbol)
    all_symbols.extend(added)
    manifest.update(added_manifest)
    # Positive rails use native KiCad power symbols, always oriented upwards.
    from modem_symbols import build as modem_symbols
    added, added_manifest = modem_symbols(make_symbol)
    all_symbols.extend(added)
    manifest.update(added_manifest)
    lib=sx.loads((STD/'power.kicad_sym').read_text())
    template=next(s for s in nodes(lib,'symbol') if s[1]=='VDD')
    for rail in ['VCC5V_CM4','CM4_3V3','CM4_1V8','SD_VDD']:
        s=copy.deepcopy(template);s[1]=rail
        for p in nodes(s,'property'):
            if p[1]=='Value':p[2]=rail
        for unit in nodes(s,'symbol'):unit[1]=unit[1].replace('VDD',rail)
        all_symbols.append(sx.dumps(s))
    (ROOT/'lib/cm4.kicad_sym').write_text('(kicad_symbol_lib (version 20251024) (generator "cm4_symbols")\n'+'\n'.join(all_symbols)+'\n)\n')
    (ROOT/'research/cm4-symbols.json').write_text(json.dumps(manifest,indent=2)+'\n')


source_url='https://datasheets.raspberrypi.com/cm4/cm4-datasheet.pdf'
if __name__=='__main__':build()
