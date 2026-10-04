#!/usr/bin/env python3
"""Prepare an unregistered, partially typed derivative of the native processor model."""
from pathlib import Path
import csv
import re
import collections

root = Path(__file__).resolve().parents[1]
source = (root / 'reference/rk3566-native-candidate.kicad_sym').read_text()
manufacturer = {r['ball']: r['manufacturer_name'] for r in csv.DictReader((root / 'pinmaps/rk3566.csv').open())}
rows = []
alternate_rows = []
pattern = r'\(pin (\w+) (\w+).*?\(name "([^"]+)".*?\(number "([^"]+)"[^\n]*\n      \)'

def interface_type(name):
    function = name.split('/')[0]
    if function in {'ARM_JTAG_TCK', 'MCU_JTAG_TCK', 'MCU_JTAG_TRSTn', 'MCU_JTAG_TMS', 'MCU_JTAG_TDI', 'FLASH_RDY'}:
        return 'input'
    if function == 'ARM_JTAG_TMS' or function.startswith(('FSPI_', 'HDMITX_')) or function == 'HDMI_TX_HPDIN':
        return 'bidirectional'
    if function in {'MCU_JTAG_TDO', 'FLASH_ALE', 'FLASH_CLE', 'FLASH_WRn', 'FLASH_RDn', 'FLASH_CS0n', 'FLASH_CS1n', 'PMIC_SLEEP'} or function.startswith('TSADC_SHUT'):
        return 'output'
    if re.fullmatch(r'FLASH_D[0-7]', function) or function == 'FLASH_DQS':
        return 'bidirectional'
    if re.match(r'I2C\d+_(SCL|SDA)', function) or re.match(r'SPI\d+_', function) or function.startswith('PWM'):
        return 'bidirectional'
    if re.match(r'UART\d+_(RX|CTSn)', function):
        return 'input'
    if re.match(r'UART\d+_(TX|RTSn)', function):
        return 'output'
    if re.match(r'EMMC_(CMD|D[0-7])$', function) or re.match(r'SDMMC\d+_(CMD|D[0-3])(?:_M\d+)?$', function):
        return 'bidirectional'
    if function in {'EMMC_CLKOUT', 'EMMC_RSTn'} or re.match(r'SDMMC\d+_(CLK|PWREN)', function):
        return 'output'
    if function in {'EMMC_DATA_STROBE', 'FLASH_VOL_SEL', 'CLK32K_IN', 'PCIE20_BUTTONRSTn'} or re.match(r'SDMMC\d+_DET', function) or re.match(r'PCIE20_(CLKREQn|PERSTn)', function):
        return 'input'
    if function.startswith('PCIE20_WAKEn'):
        return 'bidirectional'
    if function.startswith('CLK32K_OUT') or function == 'REFCLK_OUT':
        return 'output'
    if re.match(r'I2S\d+_(SCLK|LRCK)', function):
        return 'bidirectional'
    if re.match(r'I2S\d+_(MCLK|SDO)', function) or function.startswith(('SPDIF_TX', 'PDM_CLK')):
        return 'output'
    if re.match(r'I2S\d+_SDI', function) or function.startswith('PDM_SDI'):
        return 'input'
    if function in {'SCR_CLK', 'SCR_RST'}:
        return 'output'
    if function == 'SCR_DET':
        return 'input'
    if function == 'SCR_IO':
        return 'bidirectional'
    if function.startswith('GMAC1_'):
        if re.match(r'GMAC1_(MCLKINOUT|MDIO)', function):
            return 'bidirectional'
        if re.match(r'GMAC1_(RXCLK|RXD|RXDV_CRS|RXER)', function):
            return 'input'
        if re.match(r'GMAC1_(TXCLK|MDC|TXD|TXEN)', function):
            return 'output'
    if function.startswith(('CIF_D', 'CIF_CLKIN', 'CIF_HREF', 'CIF_VSYNC', 'EDP_HPDIN')):
        return 'input'
    if function in {'CAM_CLKOUT0', 'CAM_CLKOUT1', 'CIF_CLKOUT'}:
        return 'output'
    if function.startswith(('DDR3_', 'DDR4_', 'LPDDR3_', 'LPDDR4_')):
        return 'bidirectional' if '_DQ' in function else 'output'
    if re.fullmatch(r'AC\d+', function):
        return 'output'
    if function.startswith(('DDR_DQ',)):
        return 'bidirectional'
    if function.startswith('DDR_DM'):
        return 'output'
    if function in {'DDR_RZQ', 'HDMI_TX_REXT'}:
        return 'passive'
    if function in {'DDR_VREFOUT', 'XOUT24M'}:
        return 'output'
    if function in {'XIN24M', 'nPOR_u', 'USB_OTG0_ID', 'USB_OTG0_VBUSDET'} or function.startswith('SARADC_VIN'):
        return 'input'
    if function.startswith('MIPI_CSI_RX_'):
        return 'input'
    if function.startswith(('MIPI_DSI_TX', 'LVDS_TX', 'HDMI_TX_D', 'HDMI_TX_CLK', 'EDP_TX_D', 'SATA1_TX', 'SATA2_TX')):
        return 'output'
    if function.startswith('EDP_TX_AUX') or function.startswith('PCIE20_REFCLK'):
        return 'bidirectional'
    if re.fullmatch(r'USB(?:3_HOST1|_HOST[23]|_OTG0)_D[PM]', function):
        return 'bidirectional'
    if function.startswith(('USB3_HOST1_SSTX', 'PCIE20_TX')):
        return 'output'
    if function.startswith(('USB3_HOST1_SSRX', 'PCIE20_RX', 'SATA1_RX', 'SATA2_RX')):
        return 'input'
    return 'unspecified'

def transform(match):
    original_type, shape, native_name, ball = match.groups()
    name = manufacturer[ball]
    primary = native_name
    if native_name.startswith('DDR_VDDQ'):
        primary = native_name.replace('DDR_', 'DDRPHY_', 1)
    elif native_name in {'USB_HOST1_DP', 'USB_HOST1_DM'}:
        primary = native_name.replace('USB_HOST1', 'USB3_HOST1')
    functions = name.split('/')
    shorthand = re.fullmatch(r'(MIPI_DSI_TX0)/(LVDS_TX0)(_AVDD_[01]V[89])', name)
    if shorthand:
        functions = [shorthand[1] + shorthand[3], shorthand[2] + shorthand[3]]
        primary = functions[0]
    elif '/' in primary:
        primary = functions[0]
    pin_type = original_type
    evidence = 'Unresolved: functional and mux-direction review required'
    if re.fullmatch(r'(?:VSS|AVSS|AVSS1)_\d+', name) or name in {'DDR_AVSS', 'PMUPLL_AVSS', 'SYSPLL_AVSS'}:
        pin_type = 'power_in'
        evidence = 'RK3566 Rev 1.2 Table 2-2 ground groups, pages 30-31'
    elif ('VDD' in name or name.startswith('VCCIO') or name in {'PMUIO1', 'PMUIO2', 'OTP_VCC18'}):
        pin_type = 'power_in'
        evidence = 'RK3566 Rev 1.2 supply groups / recommended operating conditions, pages 31-32 and 53-54'
    elif primary.startswith('GPIO'):
        pin_type = 'bidirectional'
        evidence = 'RK3566 Rev 1.2 GPIO pad capabilities / mux table; not a reset-direction claim'
    elif interface_type(primary) != 'unspecified':
        pin_type = interface_type(primary)
        evidence = 'RK3566 Rev 1.2 Table 2-4 interface directions; DDR analog roles additionally guide 2.1.9.5-6'
    rows.append({'ball': ball, 'primary_name': primary, 'manufacturer_name': name,
                 'electrical_type': pin_type, 'evidence': evidence})
    desired_shape = 'line' if pin_type != 'unspecified' else shape
    result = match.group(0).replace('(pin ' + original_type + ' ' + shape, '(pin ' + pin_type + ' ' + desired_shape, 1)
    result = result.replace('(name "' + native_name + '"', '(name "' + primary + '"', 1)
    if len(functions) > 1:
        alternates = list(dict.fromkeys(n for n in functions if n not in {primary, '-'}))
        alternate_types = {}
        for alternate in alternates:
            direction = 'power_in' if shorthand else interface_type(alternate)
            alternate_types[alternate] = direction
            alternate_rows.append({'ball': ball, 'function': alternate, 'electrical_type': direction,
                                   'evidence': 'Direction review pending' if direction == 'unspecified' else 'RK3566 Rev 1.2 Table 2-4; FSPI data guide Table 2-7; shutdown/sleep guide 2.2; shared supply alias'})
        result = result[:-1] + ''.join(f'(alternate "{n}" {alternate_types[n]} line)' for n in alternates) + ')'
    return result

review = re.sub(pattern, transform, source, flags=re.S)
review = re.sub(r'\s*\(circle\s+\(center [^)]*\)\s+\(radius [^)]*\)\s+\(stroke .*?\(fill \(type none\)\)\s*\)', '', review, flags=re.S)
assert len(rows) == 565 and len({r['ball'] for r in rows}) == 565
assert {r['ball'] for r in rows} == set(manufacturer)
(root / 'reference/rk3566-electrical-review.kicad_sym').write_text(review)
with (root / 'pinmaps/rk3566-electrical-review.csv').open('w') as handle:
    writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator='\n')
    writer.writeheader()
    writer.writerows(rows)
with (root / 'pinmaps/rk3566-mux-review.csv').open('w') as handle:
    writer = csv.DictWriter(handle, fieldnames=['ball', 'function', 'electrical_type', 'evidence'], lineterminator='\n')
    writer.writeheader()
    writer.writerows(alternate_rows)
print('Prepared unregistered native derivative:', dict(collections.Counter(r['electrical_type'] for r in rows)))
print('Alternate functions preserved:', len(alternate_rows))
print('Remaining unspecified pins are explicit; this is not a qualified processor symbol.')
