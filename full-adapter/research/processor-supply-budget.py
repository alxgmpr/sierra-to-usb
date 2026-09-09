"""Partial rail budget from Rockchip HW Guide V1.2 documented domain peaks.

This is not a full-system power budget: IO, buck losses, peripheral loads and
simultaneous operating conditions still need closure before PoE selection.
"""
from pathlib import Path
import hashlib
import json

ROOT=Path(__file__).resolve().parents[1]


def main():
    domains = {
        'VDD0V9_PMU': {'V':.9,'rating_mA':100,'loads_mA':{'PMUPLL':10,'PMU_logic':50}},
        'VDD0V9_ANLG': {'V':.9,'rating_mA':400,'loads_mA':{'SYSPLL':30,'USB3_HS_PHY':5,'USB2_HS_PHY':5,'MULTI_PHY_shared':150}},
        'VCC1V8_ANLG': {'V':1.8,'rating_mA':400,'loads_mA':{'SYSPLL':18,'USB3_HS_PHY':30,'USB2_HS_PHY':30,'MULTI_PHY_shared':21,'SARADC':1.5}},
        'VCC1V8_PMU': {'V':1.8,'rating_mA':400,'loads_mA':{'PMUPLL':9},'additional_IO_load_unbounded':True},
    }
    for d in domains.values():
        d['documented_peak_sum_mA']=sum(d['loads_mA'].values())
        d['nominal_input_V']=3.3
        d['nominal_LDO_dissipation_W']=round((3.3-d['V'])*d['documented_peak_sum_mA']/1000,6)
        assert d['documented_peak_sum_mA'] < d['rating_mA']
    result = {
        'status':'PARTIAL_PROCESSOR_ANALOG_BUDGET_NOT_SYSTEM_QUALIFICATION',
        'source':{'document':'Rockchip RK3568 Hardware Design Guide EN V1.2, 2022-01-26',
                  'sections':['2.2.2.2','2.2.2.3','2.2.2.9','2.2.2.10','2.2.2.16','2.2.2.17'],
                  'sha256':hashlib.sha256((ROOT/'reference/Rockchip_RK3568_Hardware_Design_Guide_EN_V1.2_20220126_.pdf').read_bytes()).hexdigest()},
        'rail_peaks':domains,
        'nominal_LDO_dissipation_sum_W':round(sum(d['nominal_LDO_dissipation_W'] for d in domains.values()),6),
        'other_known_processor_domain_peaks':{'VCC3V3_S0_USB_PHY_mA':20,'VCC1V8_SYS_OTP_mA':59},
        'reference_reconciliation':
            'HW Guide recommends more than 200mA capacity for PLL supplies generally. The Rockchip tablet RK809-5 power diagram explicitly uses its 100mA low-noise LDO3 for PMUPLL 0.9V plus PMU logic. This capture follows that exact PMIC reference with a documented 60mA peak sum, not the generic capacity recommendation. PSRR/ripple and hot transient behavior require physical verification.',
        'usb_filter':{'part':'BLM18PG121SN1D','initial_DCR_max_ohm':.05,'after_tests_DCR_max_ohm':.10,
                      'rating_A_at_85C':2,'rating_A_at_125C':1,'load_mA_0v9':10,'load_mA_1v8':60,
                      'after_tests_drop_mV_0v9':1,'after_tests_drop_mV_1v8':6,
                      'note':'After-test DCR is specified at standard measurement conditions; it is not a guaranteed hot operating resistance. Hot voltage drop, filter resonance and ripple remain physical checks.'},
        'unclosed':['IO domain currents including PMUIO0/1/2, pull-ups and external loads',
                    'IO3 regulator dropout/current during SD operation',
                    'Complete PMIC self-consumption and simultaneous buck/LDO dissipation',
                    'Power trace drops, effective capacitance and hot load transients',
                    'PMIC cooling and maximum ambient',
                    'System power budget, conversion losses and PoE class'],
    }
    (ROOT/'research/processor-supply-budget.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))


if __name__=='__main__':main()
