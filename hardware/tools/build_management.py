#!/usr/bin/env python3
"""Capture the 2026-11-22 bring-up additions as four new sheets.

aux-power:   auxiliary 12 V input, ideal-diode OR with the flyback, INA226 bus monitor.
management:  SoC <-> STM32 UART link, MCU-driven status LEDs, rail/current/NTC sensing.
boot-media:  1.8 V SPI flash (NOR fitted, SPI NAND drop-in), DNP microSD, DNP MFF2 eSIM.
test-points: bare probe pads on resets, enables, power-goods and rails.

Existing sheets are edited natively (pin labels on U201/U801/J2001); this script only
writes the four new sheet files and the MFF2 symbol.
"""
import re
from capture import ROOT, Sheet, stock, block, grouped, children

R0603 = 'Resistor_SMD:R_0603_1608Metric_Pad0.98x0.95mm_HandSolder'
C0603 = 'Capacitor_SMD:C_0603_1608Metric_Pad1.08x0.95mm_HandSolder'
C1206 = 'Capacitor_SMD:C_1206_3216Metric_Pad1.33x1.80mm_HandSolder'
LED = 'LED_SMD:LED_0603_1608Metric_Pad1.05x0.95mm_HandSolder'
SAMSUNG, YAGEO, TI = 'Samsung Electro-Mechanics', 'Yageo', 'Texas Instruments'
RES = {'100kR': 'RC0603FR-07100KL', '10kR': 'RC0603FR-0710KL', '4.7kR': 'RC0603FR-074K7L',
       '1kR': 'RC0603FR-071KL', '22R': 'RC0603FR-0722RL', '0R': 'RC0603JR-070RL'}
CAP = {'100nF': ('CL10B104KA8NNNC', C0603, SAMSUNG, '25V'), '1nF': ('C1608X7R2A102K', C0603, 'TDK', '100V'),
       '4.7uF': ('CL10A475KA8NQNC', C0603, SAMSUNG, '25V'), '10uF': ('CL31B106KBHNNNE', C1206, SAMSUNG, '50V')}


def lib_body(sheet, lib_id):
    text = (ROOT / sheet).read_text()
    return block(text, text.index(f'(symbol "{lib_id}"'))


def dnp(s, *refs):
    for i, item in enumerate(s.items):
        if item.startswith('(symbol (lib_id') and any(f'(property "Reference" "{r}"' in item for r in refs):
            s.items[i] = item.replace('(dnp no)', '(dnp yes)', 1)


def res(s, ref, value, x, y, a, b, horizontal=False):
    return s.passive('R', ref, value, x, y, a, b, RES[value], R0603, YAGEO,
                     {'Tolerance': '5%' if value == '0R' else '1%', 'Power Rating': '0.1W'}, horizontal)


def cap(s, ref, value, x, y, a, b='GND'):
    mpn, fp, maker, volts = CAP[value]
    return s.passive('C', ref, value, x, y, a, b, mpn, fp, maker, {'Voltage Rating': volts})


def part(s, lib, name, ref, value, x, y, fp, fields, nets, body=None):
    pins = s.symbol(f'{lib}:{name}', body or stock(lib, name), ref, value, x, y, fp, fields)
    s.attach(pins, nets)
    return pins


def aux_power():
    s = Sheet('aux-power', 'Auxiliary 12 V input, ideal-diode OR and bus monitor', 'A2')
    s.rectangle('AUX 12 V INPUT AND IDEAL-DIODE OR WITH THE ISOLATED FLYBACK', 20.32, 20.32, 340.36, 160.02)
    ed555 = lib_body('poe-flyback.kicad_sch', 'PoE:TI_a05e59a08157')
    part(s, 'PoE', 'TI_a05e59a08157', 'J2101', 'ED555/2DS', 45.72, 81.28, 'PoE:TI_TERM_BLK_ED555-2DS',
         {'MPN': 'ED555/2DS', 'Manufacturer': 'On-Shore Technology',
          'Datasheet': 'http://on-shore.com/sites/default/files/manuals/ed555ds.pdf', 'Function': 'AUX 12 V IN, pin 1 +'},
         {'1': 'AUX_12V_IN', '2': 'GND'}, ed555)
    part(s, 'Device', 'D_TVS', 'D2101', 'SMBJ12CA', 83.82, 116.84, 'Diode_SMD:D_SMB_Handsoldering',
         {'MPN': 'SMBJ12CA', 'Manufacturer': 'Littelfuse', 'Datasheet': 'https://www.littelfuse.com/assetdocs/tvs-diodes-smbj-datasheet'},
         {'1': 'AUX_12V_IN', '2': 'GND'})
    cap(s, 'C2101', '10uF', 109.22, 116.84, 'AUX_12V_IN')
    s.flag('#FLG2101', 'AUX_12V_IN', 109.22, 60.96, 'Auxiliary 12 V terminal J2101')
    lm = stock('Power_Management', 'LM74700')
    fet = stock('Transistor_FET', 'CSD17577Q5A')
    lmf = {'MPN': 'LM74700QDBVRQ1', 'Manufacturer': TI, 'LCSC': 'C2941042',
           'Datasheet': 'https://www.ti.com/lit/ds/symlink/lm74700-q1.pdf'}
    fetf = {'MPN': 'CSD17577Q5A', 'Manufacturer': TI, 'LCSC': 'C475504',
            'Datasheet': 'https://www.ti.com/lit/ds/symlink/csd17577q5a.pdf'}
    for i, (src, tag) in enumerate([('AUX_12V_IN', 'AUX'), ('ISO_12V_PSU', 'PSU')]):
        y = 60.96 + 76.2 * i
        part(s, 'Transistor_FET', 'CSD17577Q5A', f'Q{2101+i}', 'CSD17577Q5A', 165.1, y, 'Package_TO_SOT_SMD:TDSON-8-1', fetf,
             {'1': src, '2': src, '3': src, '4': f'{tag}_DIODE_GATE', '5': 'ISO_12V_BUS'}, fet)
        part(s, 'Power_Management', 'LM74700', f'U{2101+i}', 'LM74700QDBVRQ1', 236.22, y, 'Package_TO_SOT_SMD:SOT-23-6_Handsoldering', lmf,
             {'1': f'{tag}_DIODE_VCAP', '2': 'GND', '3': src, '4': 'ISO_12V_BUS', '5': f'{tag}_DIODE_GATE', '6': src}, lm)
        cap(s, f'C{2102+i}', '100nF', 297.18, y, f'{tag}_DIODE_VCAP', src)
    cap(s, 'C2104', '10uF', 330.2, 60.96, 'ISO_12V_BUS')
    cap(s, 'C2105', '10uF', 330.2, 137.16, 'ISO_12V_BUS')
    s.note('Either source feeds ISO_12V_BUS through its own LM74700 ideal diode; the higher one carries the load.\n'
           'Aux input: 12 V nominal, 12.6 V max (SMBJ12CA starts conducting at 13.3 V; TPS54620 input limit 17 V).\n'
           'Reverse aux polarity: the TVS conducts and LM74700 blocks; fuse or current-limit the bench supply.\n'
           'Firmware: aux power gives no PoE grant (TPH_N/TPL_N/BT_N all high). Bypass the grant gate only\n'
           'while ADC_AUX_12V reads above 10.5 V, and re-apply it the moment aux falls away.', 25.4, 172.72)

    s.rectangle('12 V BUS CURRENT AND VOLTAGE MONITOR', 20.32, 200.66, 340.36, 132.08)
    s.passive('R', 'R2101', '10mR', 83.82, 251.46, 'ISO_12V_BUS', 'ISO_12V', 'PE2512FKE7W0R01L',
              'Resistor_SMD:R_2512_6332Metric_Pad1.40x3.35mm_HandSolder', YAGEO,
              {'Tolerance': '1%', 'Power Rating': '2W', 'LCSC': 'C875720', 'Placement': 'Kelvin-route Vin+/Vin- from the pad inner edges'})
    s.flag('#FLG2102', 'ISO_12V', 83.82, 297.18, 'Monitored 12 V bus after R2101')
    part(s, 'Sensor_Energy', 'INA226', 'U2103', 'INA226AIDGSR', 180.34, 259.08, 'Package_SO:MSOP-10_3x3mm_P0.5mm',
         {'MPN': 'INA226AIDGSR', 'Manufacturer': TI, 'LCSC': 'C49851', 'Datasheet': 'https://www.ti.com/lit/ds/symlink/ina226.pdf',
          'Function': 'I2C 0x40; 10 mOhm shunt: 2.5 uV/LSB = 0.25 mA/LSB, 8.2 A full scale'},
         {'1': 'GND', '2': 'GND', '3': 'MON_ALERT_N', '4': 'MON_I2C_SDA', '5': 'MON_I2C_SCL', '6': '+3V3', '7': 'GND',
          '8': 'ISO_12V', '9': 'ISO_12V', '10': 'ISO_12V_BUS'})
    cap(s, 'C2106', '100nF', 248.92, 223.52, '+3V3')
    res(s, 'R2102', '4.7kR', 276.86, 223.52, '+3V3', 'MON_I2C_SCL')
    res(s, 'R2103', '4.7kR', 297.18, 223.52, '+3V3', 'MON_I2C_SDA')
    res(s, 'R2104', '10kR', 317.5, 223.52, '+3V3', 'MON_ALERT_N')
    res(s, 'R2105', '100kR', 276.86, 289.56, 'AUX_12V_IN', 'ADC_AUX_12V')
    res(s, 'R2106', '10kR', 297.18, 289.56, 'ADC_AUX_12V', 'GND')
    cap(s, 'C2107', '100nF', 317.5, 289.56, 'ADC_AUX_12V')
    s.note('ADC_AUX_12V = AUX_12V_IN / 11 (12 V -> 1.09 V) on STM32 PA0. INA226 runs from the always-on 3.3 V.', 25.4, 325.12)
    s.save()


def management():
    s = Sheet('management', 'Supervisor link, status LEDs and sensing', 'A2')
    s.rectangle('POWERED-OFF-SAFE SOC <-> STM32 UART (SoC UART3_M0, MCU LPUART2)', 20.32, 20.32, 266.7, 114.3)
    buf = stock('74xGxx', 'SN74LVC1G125DCK')
    bf = {'MPN': 'SN74LVC1G125DCKR', 'Manufacturer': TI, 'LCSC': 'C7833',
          'Datasheet': 'https://www.ti.com/lit/ds/symlink/sn74lvc1g125.pdf', 'Qualification': 'Ioff: no back-power into an unpowered side'}
    for ref, y, inp, out, rail in [('U2201', 55.88, 'SOC_LINK_TX', 'MCU_LINK_RX', '+3V3'),
                                   ('U2202', 104.14, 'MCU_LINK_TX', 'SOC_LINK_RX', '3V3_MAIN')]:
        part(s, '74xGxx', 'SN74LVC1G125DCK', ref, 'SN74LVC1G125DCKR', 76.2, y, 'Package_TO_SOT_SMD:SOT-353_SC-70-5', bf,
             {'1': 'GND', '2': inp, '3': 'GND', '4': out, '5': rail}, buf)
    res(s, 'R2201', '100kR', 160.02, 55.88, '3V3_MAIN', 'SOC_LINK_TX')
    res(s, 'R2202', '100kR', 160.02, 104.14, '+3V3', 'MCU_LINK_TX')
    cap(s, 'C2201', '100nF', 205.74, 55.88, '+3V3')
    cap(s, 'C2202', '100nF', 205.74, 104.14, '3V3_MAIN')
    s.note('Each buffer is powered by its receiving side: SoC->MCU from +3V3, MCU->SoC from 3V3_MAIN.\n'
           'SoC: A22 UART3_RX_M0 / B22 UART3_TX_M0, VCCIO1 = 3V3_MAIN. MCU: PC7 LPUART2_RX / PC6 LPUART2_TX.\n'
           'Carries telemetry, LED overrides, power-cycle requests and reset-cause reporting.', 25.4, 129.54)

    s.rectangle('STATUS LEDS: MCU-DRIVEN, LINUX OVERRIDE OVER THE LINK', 302.26, 20.32, 254, 114.3)
    green = {'MPN': '150060GS75000', 'Manufacturer': 'Wurth Elektronik', 'LCSC': 'C5252984',
             'Datasheet': 'https://www.we-online.com/components/products/datasheet/150060GS75000.pdf'}
    yellow = {'MPN': '150060YS75000', 'Manufacturer': 'Wurth Elektronik',
              'Datasheet': 'http://katalog.we-online.de/led/datasheet/150060YS75000.pdf'}
    led = stock('Device', 'LED_Small')
    for i, (name, color, fields, pin) in enumerate([('PWR', 'Green', green, 'PA8'), ('SYS', 'Green', green, 'PA15'),
                                                    ('WAN', 'Green', green, 'PD0'), ('FAULT', 'Yellow', yellow, 'PD1')]):
        x = 330.2 + 55.88 * i
        res(s, f'R{2203+i}', '1kR', x, 55.88, '+3V3', f'LED_{name}_A')
        part(s, 'Device', 'LED_Small', f'D{2201+i}', color, x, 96.52, LED, {**fields, 'Function': f'{name}: MCU {pin} sinks, timer PWM'},
             {'1': f'LED_{name}_N', '2': f'LED_{name}_A'}, led)
    s.note('LEDs are off from MCU reset until firmware drives them; Linux can override each over the UART link.\n'
           '~1.3 mA each from 3.3 V through 1 kOhm.', 307.34, 129.54)

    s.rectangle('ANALOG MONITORS ON THE STM32 ADC (VREF+ = +3V3)', 20.32, 154.94, 536.94, 182.88)
    for i, (rail, adc) in enumerate([('5V_MAIN', 'ADC_5V_MAIN'), ('3V3_MAIN', 'ADC_3V3_MAIN'), ('MODEM_VCC', 'ADC_MODEM_VCC')]):
        x = 50.8 + 76.2 * i
        res(s, f'R{2207+2*i}', '100kR', x, 198.12, rail, adc)
        res(s, f'R{2208+2*i}', '100kR', x, 241.3, adc, 'GND')
        cap(s, f'C{2203+i}', '100nF', x + 25.4, 241.3, adc)
    res(s, 'R2213', '100kR', 279.4, 198.12, 'MODEM_FUSE_ILM', 'ADC_MODEM_ILM')
    cap(s, 'C2206', '1nF', 279.4, 241.3, 'ADC_MODEM_ILM')
    ntc = stock('Device', 'Thermistor_NTC')
    for i, (adc, where) in enumerate([('ADC_NTC_MODEM', 'M.2 module bay, under the card centre'),
                                      ('ADC_NTC_POWER', 'between T1702 secondary and U1901')]):
        x = 381 + 76.2 * i
        res(s, f'R{2214+i}', '10kR', x, 198.12, '+3V3', adc)
        part(s, 'Device', 'Thermistor_NTC', f'RT{2201+i}', '10k B3380', x, 241.3, R0603,
             {'MPN': 'NCP18XH103F03RB', 'Manufacturer': 'Murata', 'LCSC': 'C13564', 'Placement': where,
              'Datasheet': 'https://www.murata.com/en-us/products/productdata/8796836626462/NTHCG83.pdf'},
             {'1': adc, '2': 'GND'}, ntc)
        cap(s, f'C{2207+i}', '100nF', x + 25.4, 241.3, adc)
    s.note('PA1 ADC_5V_MAIN = 5V/2, PA4 ADC_3V3_MAIN = 3V3/2, PA5 ADC_MODEM_VCC = VCC/2, PA6 ADC_MODEM_ILM,\n'
           'PA7 ADC_NTC_MODEM, PB2 ADC_NTC_POWER (10k NTC to GND, 10k pull-up: ratiometric to VREF+).\n'
           'ILM: TPS25947 analog current monitor (V = I_OUT x G_IMON x R_ILM). Its pin must see < 50 pF:\n'
           'place R2213 at U1902 pin 9; C2206 sits at the MCU end. Calibrate gain against the INA226.', 25.4, 299.72)
    s.save()


def boot_media():
    s = Sheet('boot-media', 'SPI boot flash, microSD and eSIM options', 'A2')
    s.rectangle('1.8 V SPI FLASH ON FSPI (VCCIO2 = VCC_1V8): NOR FITTED, SPI NAND DROP-IN', 20.32, 20.32, 248.92, 132.08)
    part(s, 'Memory_Flash', 'W25Q128JVE', 'U2301', 'W25Q128JWEIQ', 83.82, 76.2, 'Package_SON:WSON-8-1EP_8x6mm_P1.27mm_EP3.4x4.3mm',
         {'MPN': 'W25Q128JWEIQ', 'Manufacturer': 'Winbond', 'Datasheet': 'https://www.winbond.com/hq/product/code-storage-flash-memory/serial-nor-flash/',
          'Alternate': 'W25N01GWZEIG 1.8 V SPI NAND, same WSON-8 8x6 footprint and pinout',
          'Qualification': 'Stock and RK3566 bootrom FSPI support to confirm before order'},
         {'1': 'FSPI_CS0_N', '2': 'FSPI_D1', '3': 'FSPI_WP_N', '4': 'GND', '5': 'FSPI_D0', '6': 'FSPI_CLK',
          '7': 'FSPI_D3', '8': 'VCC_1V8', '9': 'GND'})
    res(s, 'R2301', '10kR', 165.1, 50.8, 'VCC_1V8', 'FSPI_CS0_N')
    res(s, 'R2302', '10kR', 185.42, 50.8, 'VCC_1V8', 'FSPI_WP_N')
    res(s, 'R2303', '10kR', 205.74, 50.8, 'VCC_1V8', 'FSPI_D3')
    cap(s, 'C2301', '100nF', 226.06, 50.8, 'VCC_1V8')
    s.note('FSPI_D2 shares ball 1B16 with EMMC_RESET_N, so the flash runs x1/x2: WP# is pulled up, not wired.\n'
           'FSPI_D3 reaches HOLD#/IO3 for a later quad rework. Blank flash falls through to eMMC.', 25.4, 144.78)

    s.rectangle('MICROSD (DNP): SDMMC0 ON VCCIO3 = VCCIO_SD, 3.3/1.8 V SWITCHED BY RK809', 284.48, 20.32, 279.4, 177.8)
    sd = stock('Connector', 'Micro_SD_Card_Det2')
    part(s, 'Connector', 'Micro_SD_Card_Det2', 'J2301', 'DM3AT-SF-PEJM5', 330.2, 81.28, 'Connector_Card:microSD_HC_Hirose_DM3AT-SF-PEJM5',
         {'MPN': 'DM3AT-SF-PEJM5', 'Manufacturer': 'Hirose', 'LCSC': 'C114218',
          'Datasheet': 'https://www.hirose.com/product/document?clcode=CL0609-0033-6-00&productname=DM3AT-SF-PEJM5'},
         {'1': 'SD_D2', '2': 'SD_D3', '3': 'SD_CMD', '4': 'SD_VDD', '5': 'SD_CLK', '6': 'GND', '7': 'SD_D0', '8': 'SD_D1',
          '9': 'SDMMC0_DET', '10': 'GND', 'SH': 'GND'}, sd)
    res(s, 'R2304', '22R', 431.8, 45.72, 'SD_CLK_SOC', 'SD_CLK', horizontal=True)
    for i, net in enumerate(['SD_CMD', 'SD_D0', 'SD_D1', 'SD_D2', 'SD_D3']):
        res(s, f'R{2305+i}', '10kR', 431.8 + 20.32 * i, 81.28, 'VCCIO_SD', net)
    tps = lib_body('nic-power.kicad_sch', 'Appliance:TPS22965_DSG')
    part(s, 'Appliance', 'TPS22965_DSG', 'U2302', 'TPS22965DSGR', 345.44, 157.48, 'Package_SON:Texas_DSG0008A_WSON-8-1EP_2x2mm_P0.5mm_EP0.9x1.6mm',
         {'MPN': 'TPS22965DSGR', 'Manufacturer': TI, 'LCSC': 'C122837', 'Datasheet': 'https://www.ti.com/lit/ds/symlink/tps22965.pdf'},
         {'1': '3V3_MAIN', '2': '3V3_MAIN', '3': 'SD_PWR_EN', '4': '5V_MAIN', '5': 'GND', '6': 'SD_SWITCH_CT',
          '7': 'SD_VDD', '8': 'SD_VDD', '9': 'GND'}, tps)
    res(s, 'R2310', '100kR', 431.8, 157.48, 'SD_PWR_EN', 'GND')
    cap(s, 'C2302', '1nF', 452.12, 157.48, 'SD_SWITCH_CT')
    cap(s, 'C2303', '4.7uF', 472.44, 157.48, 'SD_VDD')
    cap(s, 'C2304', '100nF', 492.76, 157.48, 'SD_VDD')
    esd = lib_body('modem-socket.kicad_sch', 'Appliance:TPD4E02B04_DQA')
    ef = {'MPN': 'TPD4E02B04DQAR', 'Manufacturer': TI, 'LCSC': 'C106794', 'Datasheet': 'https://www.ti.com/lit/ds/symlink/tpd4e02b04.pdf'}
    part(s, 'Appliance', 'TPD4E02B04_DQA', 'D2301', 'TPD4E02B04DQAR', 528.32, 63.5, 'Package_SON:USON-10_2.5x1.0mm_P0.5mm', ef,
         {'1': 'SD_CLK', '2': 'SD_CMD', '3': 'GND', '4': 'SD_D0', '5': 'SD_D1', '6': None, '7': None, '8': 'GND', '9': None, '10': None}, esd)
    part(s, 'Appliance', 'TPD4E02B04_DQA', 'D2302', 'TPD4E02B04DQAR', 528.32, 119.38, 'Package_SON:USON-10_2.5x1.0mm_P0.5mm', ef,
         {'1': 'SD_D2', '2': 'SD_D3', '3': 'GND', '4': None, '5': None, '6': None, '7': None, '8': 'GND', '9': None, '10': None}, esd)
    dnp(s, 'J2301', 'R2304', 'R2305', 'R2306', 'R2307', 'R2308', 'R2309', 'U2302', 'R2310', 'C2302', 'C2303', 'C2304', 'D2301', 'D2302')
    s.note('All DNP. Card detect closes DET_B to GND on insertion: SDMMC0_DET (R1202 pull-up) goes low = SD mode.\n'
           'SD_PWR_EN = GPIO0_A6 (PMUIO1, 3.3 V), pulled low: card power stays off until Linux enables it, which\n'
           'also lets UHS cards be power-cycled out of 1.8 V signalling.', 289.56, 190.5)

    s.rectangle('MFF2 eSIM (DNP) ON M.2 SIM2 CONTACTS 42/44/46/48', 20.32, 220.98, 340.36, 111.76)
    pins = {'1': 'VSS', '2': 'VPP/NC', '3': 'I/O', '4': 'NC', '5': 'NC', '6': 'CLK', '7': 'RST', '8': 'VCC', '9': 'EP'}
    mff2 = grouped('MFF2_eUICC', pins, [{'left': ['8', '7', '6', '3'], 'right': ['2', '4', '5', '9'], 'bottom': ['1']}],
                   {'1': 'power_in', '2': 'no_connect', '3': 'bidirectional', '4': 'no_connect', '5': 'no_connect',
                    '6': 'input', '7': 'input', '8': 'passive', '9': 'no_connect'})
    (ROOT / 'reference/mff2-euicc-captured.kicad_sym').write_text(
        '(kicad_symbol_lib (version 20211014) (generator eeschema) ' + mff2 + ')\n')
    for i, (pin, net) in enumerate([('48', 'ESIM_VDD'), ('46', 'ESIM_RST'), ('44', 'ESIM_CLK'), ('42', 'ESIM_IO')]):
        s.passive('R', f'R{2311+i}', '0R ESIM / DNP', 50.8 + 25.4 * i, 264.16, f'M2_PIN{pin}', net, RES['0R'], R0603, YAGEO,
                  {'Tolerance': '5%', 'Power Rating': '0.1W', 'Placement': 'At J2001; Quectel eSIM-variant modules need 40-48 open'})
    part(s, 'Appliance', 'MFF2_eUICC', 'U2303', 'MFF2 eUICC', 220.98, 271.78, 'Package_SON:WSON-8-1EP_6x5mm_P1.27mm_EP3.4x4.3mm',
         {'MPN': 'MFF2-EUICC-TBD', 'Manufacturer': 'TBD (select per carrier/eUICC vendor)',
          'Qualification': 'Placeholder land: pin 1 VSS(C5), 3 I/O(C7), 6 CLK(C3), 7 RST(C2), 8 VCC(C1), EP not connected. Verify against the chosen eUICC drawing before fitting.'},
         {'1': 'GND', '2': None, '3': 'ESIM_IO', '4': None, '5': None, '6': 'ESIM_CLK', '7': 'ESIM_RST', '8': 'ESIM_VDD', '9': None}, mff2)
    cap(s, 'C2305', '100nF', 297.18, 271.78, 'ESIM_VDD')
    dnp(s, 'R2311', 'R2312', 'R2313', 'R2314', 'U2303', 'C2305')
    s.note('SIM2 contacts per EM92xx PTS r1 and RM520N-GL HW guide 4.1.6: 40 detect, 42 data, 44 clk, 46 reset, 48 VDD.\n'
           'All DNP, so every profile keeps 42-48 open. Fitting needs the module SIM2 enable and an LPA (e.g. lpac).', 25.4, 325.12)
    s.save()


CONTROL = ['RK_RESET_N', 'PMIC_PWRON_N', 'PMIC_SLEEP', 'PMIC_INT_N', 'PMIC_CPU_EN', 'MCU_PWRON_KICK',
           'MCU_PROCESSOR_RESET_ASSERT', 'MCU_PROCESSOR_RECOVERY_ASSERT', 'SARADC_BOOT_KEY', 'TSADC_SHUTDOWN',
           'SOC_HEALTH', 'MCU_HEALTH_IN', 'EMMC_RESET_N', 'LPDDR4_RESETn', 'DDR_VDDQ_EN', 'OSC_ENABLE',
           'MCU_MAIN5V_EN', 'MAIN5V_GOOD', 'MAIN3V3_EN', 'MAIN3V3_GOOD', 'MCU_ETH_POWER_EN', 'ETH_SWITCH_EN',
           'ETH_3V3_GOOD', 'ETH_CORE_EN', 'ETH_PERST_N', 'ETH_CLOCK_OE_N', 'PCIE_PERST_SOC_N', 'PCIE_CLKREQ_N',
           'PCIE_WAKE_N', 'MCU_MODEM_POWER_EN', 'MODEM_BUCK_EN', 'MODEM_BUCK_GOOD', 'MODEM_FUSE_EN',
           'MODEM_SWITCH_GOOD', 'MODEM_RAIL_GOOD', 'MODEM_RESET_N', 'MODEM_OFF_N', 'MODEM_USB_OE_N',
           'MODEM_USB_VALID', 'POE_TPH_N', 'POE_TPL_N', 'POE_BT_N', 'SD_PWR_EN', 'MON_ALERT_N']
RAILS = ['ISO_12V_PSU', 'AUX_12V_IN', 'ISO_12V_BUS', 'ISO_12V', '5V_MAIN', '3V3_MAIN', '+3V3', 'VCC3V3_PMU',
         'VCC_1V8', 'VCCA_1V8', 'VCCA1V8_PMU', 'VDDA_0V9', 'VDDA0V9_PMU', 'VDD_CPU', 'VDD_LOGIC', 'VDD_GPU',
         'VDD_NPU', 'VDD_DDR_1V1', 'VDD_DDR_0V6', 'VCCIO_SD', 'MODEM_3V7_RAW', 'MODEM_VCC', 'ETH_3V3',
         'ETH_0V95', 'USB_AVDD_0V9', 'MULTI_AVDD_0V9']


def test_points():
    s = Sheet('test-points', 'Bring-up test pads', 'A2')
    tp = stock('Connector', 'TestPoint')
    groups = [('RESETS, ENABLES AND POWER-GOODS', CONTROL), ('RAILS', RAILS), ('GROUND', ['GND'] * 10)]
    ref, y0 = 2401, 20.32
    for title, nets in groups:
        rows = (len(nets) + 7) // 8
        s.rectangle(title, 20.32, y0, 541.02, 25.4 * rows + 12.7)
        for i, net in enumerate(nets):
            x, y = 50.8 + 66.04 * (i % 8), y0 + 25.4 + 25.4 * (i // 8)
            pins = s.symbol('Connector:TestPoint', tp, f'TP{ref}', net, x, y, 'TestPoint:TestPoint_Pad_D1.0mm',
                            {'Placement Intent': 'bare 1.0 mm probe pad, top side where possible'})
            s.attach(pins, {'1': net})
            ref += 1
        y0 += 25.4 * rows + 25.4
    s.note('Bare pads: no BOM line. Local nets without a global label stay on headers: MCU_NRST_N and SWD on J201,\n'
           'POWER_FAULT_N / SERVICE UART / modem reset lines on J102.', 25.4, y0)
    s.save()


def register_mff2():
    """Append the MFF2 symbol to Appliance.kicad_sym, as build_capture.py would."""
    path = ROOT / 'Appliance.kicad_sym'
    text = path.read_text()
    body = (ROOT / 'reference/mff2-euicc-captured.kicad_sym').read_text()
    symbol = next(c for c in children(body) if c.startswith('(symbol "MFF2_eUICC"'))
    old = re.search(r'\(symbol "MFF2_eUICC"', text)
    text = text.replace(block(text, old.start()), symbol) if old else text.rstrip()[:-1] + symbol + ')\n'
    path.write_text(text)


if __name__ == '__main__':
    aux_power()
    management()
    boot_media()
    test_points()
    register_mff2()
    print('Generated aux-power, management, boot-media and test-points sheets.')
