# M.2 compatibility matrix

2026-09-05. Document-level audit, not qualification of a physical module. No electrically released configuration exists yet. RM520N-GL is the audited candidate, not an inferred regional choice. RM551E-GL is excluded; every pin remains unknown. Hardware revision markings and firmware builds of actual modules are unrecorded.

Sierra basis: 41113174 Rev 8, May 2023, Table 3-1 pp25-29. Quectel basis: RM520N-GL Hardware Design V1.0, released 2022-07-15, Table 5 pp19-23. Source URLs and hashes: source-register.json. Asterisks retain Quectel’s under-development markers.

**Critical revision correction:** Sierra Rev 8 restricts the optional-NC note on 24/38/68 to EM7690. Connect all eight VCC pins for EM9190. Do not reuse the earlier optional-Sierra-pin instruction. These three connections must be physically isolated for RM520N-GL. A low-driving MOSFET is not isolation.

| Pin | EM9190 Rev8 | RM520N-GL V1.0 | Compact disposition |
|---:|---|---|---|
| 1 | CONFIG_3 / reserved | CONFIG_3 / internally NC | OMIT: leave unconnected in both USB / one-SIM / sub-6 profiles |
| 2 | VCC | VCC | COMMON switched MODEM_VCC |
| 3 | GND | GND | COMMON GND |
| 4 | VCC | VCC | COMMON switched MODEM_VCC |
| 5 | GND | GND | COMMON GND |
| 6 | Full_Card_Power_Off# | FULL_CARD_POWER_OFF# | COMMON control: module-derived gated high, default low; sequence review required |
| 7 | USB_D+ | USB_DP | COMMON USB D+; connector A6=B6 |
| 8 | W_DISABLE# | W_DISABLE1# | COMMON open-drain RF disable; no host pull-up |
| 9 | USB_D- | USB_DM | COMMON USB D-; connector A7=B7 |
| 10 | WWAN_LED# | LED_WWAN# | Omit optional LED load; no external connection |
| 11 | GND | GND | COMMON GND |
| 12 | KEY / no contact | KEY / no contact | No pad/contact |
| 13 | KEY / no contact | KEY / no contact | No pad/contact |
| 14 | KEY / no contact | KEY / no contact | No pad/contact |
| 15 | KEY / no contact | KEY / no contact | No pad/contact |
| 16 | KEY / no contact | KEY / no contact | No pad/contact |
| 17 | KEY / no contact | KEY / no contact | No pad/contact |
| 18 | KEY / no contact | KEY / no contact | No pad/contact |
| 19 | KEY / no contact | KEY / no contact | No pad/contact |
| 20 | PCIE_DIS | RESERVED | SIERRA ONLY 1.8V USB strap; physically open on Quectel |
| 21 | CONFIG_0 / reserved | CONFIG_0 / internally NC | OMIT: leave unconnected in both USB / one-SIM / sub-6 profiles |
| 22 | VBUS_SENSE | RESERVED | SIERRA ONLY host-presence; physically open on Quectel |
| 23 | WAKE_ON_WAN# | WAKE_ON_WAN# | Omit optional wake; no host pull-up |
| 24 | VCC | VDDIO_1V8 / output 50mA max | SIERRA VCC REQUIRED; physically open on Quectel output |
| 25 | DPR | DPR* | Leave unused; SAR firmware/configuration gate remains |
| 26 | GPS_DISABLE# | W_DISABLE2#* | Omit optional GNSS disable; leave open |
| 27 | GND | GND | COMMON GND |
| 28 | PLA_S2# | RESERVED | Sierra-only status through keyed profile 17–18; Quectel isolated |
| 29 | USB3_TXM | USB_SS_TX_M | COMMON module TX- to host RX-; module owns TX coupling |
| 30 | UIM1_RESET | USIM1_RST | COMMON SIM1 reset; module SIM voltage domain |
| 31 | USB3_TXP | USB_SS_TX_P | COMMON module TX+ to host RX+; module owns TX coupling |
| 32 | UIM1_CLK | USIM1_CLK | COMMON SIM1 clock; module SIM voltage domain |
| 33 | GND | GND | COMMON GND |
| 34 | UIM1_DATA | USIM1_DATA | COMMON SIM1 bidirectional data; module SIM voltage domain |
| 35 | USB3_RXM | USB_SS_RX_M | COMMON module RX- from host TX-; audit mux bias and coupling |
| 36 | UIM1_PWR | USIM1_VDD | COMMON SIM1 power OUTPUT; never host 3.3V |
| 37 | USB3_RXP | USB_SS_RX_P | COMMON module RX+ from host TX+; audit mux bias and coupling |
| 38 | VCC | WLAN_TX_EN* | SIERRA VCC REQUIRED; physically open on Quectel WLAN input |
| 39 | GND | GND | COMMON GND |
| 40 | QTM0_PON | USIM2_DET | OMIT: leave unconnected in both USB / one-SIM / sub-6 profiles |
| 41 | PCIE_TXM0 | PCIE_TX_M | OMIT: leave unconnected in both USB / one-SIM / sub-6 profiles |
| 42 | QTM1_PON | USIM2_DATA | OMIT: leave unconnected in both USB / one-SIM / sub-6 profiles |
| 43 | PCIE_TXP0 | PCIE_TX_P | OMIT: leave unconnected in both USB / one-SIM / sub-6 profiles |
| 44 | QTM2_PON | USIM2_CLK | OMIT: leave unconnected in both USB / one-SIM / sub-6 profiles |
| 45 | GND | GND | COMMON GND |
| 46 | QTM3_PON | USIM2_RST | OMIT: leave unconnected in both USB / one-SIM / sub-6 profiles |
| 47 | PCIE_RXM0 | PCIE_RX_M | OMIT: leave unconnected in both USB / one-SIM / sub-6 profiles |
| 48 | QTM_IO_1.9V | USIM2_VDD | OMIT: leave unconnected in both USB / one-SIM / sub-6 profiles |
| 49 | PCIE_RXP0 | PCIE_RX_P | OMIT: leave unconnected in both USB / one-SIM / sub-6 profiles |
| 50 | PCIE_PERST_N | PCIE_RST_N | OMIT: leave unconnected in both USB / one-SIM / sub-6 profiles |
| 51 | GND | GND | COMMON GND |
| 52 | PCIE_CLKREQ_N | PCIE_CLKREQ_N | OMIT: leave unconnected in both USB / one-SIM / sub-6 profiles |
| 53 | PCIE_REFCLKM | PCIE_REFCLK_M | OMIT: leave unconnected in both USB / one-SIM / sub-6 profiles |
| 54 | PCIE_PEWAKE_N | PCIE_WAKE_N | OMIT: leave unconnected in both USB / one-SIM / sub-6 profiles |
| 55 | PCIE_REFCLKP | PCIE_REFCLK_P | OMIT: leave unconnected in both USB / one-SIM / sub-6 profiles |
| 56 | NC / reserved | RFFE_CLK* | OMIT: leave unconnected in both USB / one-SIM / sub-6 profiles |
| 57 | GND | GND | COMMON GND |
| 58 | NC / reserved | RFFE_DATA* | OMIT: leave unconnected in both USB / one-SIM / sub-6 profiles |
| 59 | ANT_CTRL0 | RESERVED | OMIT: leave unconnected in both USB / one-SIM / sub-6 profiles |
| 60 | Reserved | N79_TX_EN* | OMIT: leave unconnected in both USB / one-SIM / sub-6 profiles |
| 61 | ANT_CTRL1 / EM92xx compatibility reserved | RESERVED | OMIT: leave unconnected in both USB / one-SIM / sub-6 profiles |
| 62 | Reserved | COEX_RXD* | OMIT: leave unconnected in both USB / one-SIM / sub-6 profiles |
| 63 | ANT_CTRL2 / EM92xx compatibility reserved | RESERVED | OMIT: leave unconnected in both USB / one-SIM / sub-6 profiles |
| 64 | Reserved | COEX_TXD* | OMIT: leave unconnected in both USB / one-SIM / sub-6 profiles |
| 65 | ANT_CTRL3 / EM92xx compatibility reserved | RESERVED | OMIT: leave unconnected in both USB / one-SIM / sub-6 profiles |
| 66 | SIM1_DETECT | USIM1_DET | COMMON SIM detect contact; firmware polarity/configuration differs |
| 67 | RESET# | RESET# | COMMON reset open-drain/button only; 1.8V, vendor-specific timing |
| 68 | VCC | RESERVED / optional IPQ status | SIERRA VCC REQUIRED; physically open on Quectel reserved pin |
| 69 | CONFIG_1 / reserved | CONFIG_1 / internally GND | OMIT: leave unconnected in both USB / one-SIM / sub-6 profiles |
| 70 | VCC | VCC | COMMON switched MODEM_VCC |
| 71 | GND | GND | COMMON GND |
| 72 | VCC | VCC | COMMON switched MODEM_VCC |
| 73 | GND | GND | COMMON GND |
| 74 | VCC | VCC | COMMON switched MODEM_VCC |
| 75 | CONFIG_2 / reserved | CONFIG_2 / internally NC | OMIT: leave unconnected in both USB / one-SIM / sub-6 profiles |

The CSV additionally contains the root net assignment, logic domain and power-off rule for every contact. RM551E has no inferred shared contacts, power mapping, antenna count, reserved-pin treatment or current requirement.

Hardware profile requirement: one mechanically keyed profile assembly must set isolation and enable authorization together. No assembly / conflicting code / unknown code must force supply disabled. Independent solder jumpers plus a label do not enforce this invariant. Manual selection still cannot detect a wrongly inserted module; prevent module swaps under power and verify the label before insertion. A fully implemented interlock remains a design gate.
