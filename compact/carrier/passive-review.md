# Passive component review

Exact MPNs are assigned in `passive_parts.py` before schematic export. The generated BOM inherits those fields; it is not edited independently. Ordinary resistors are Yageo RC0603 1%, precision current/timer dividers use RT0603 0.1%/25ppm, and the main feedback uses Panasonic ERA0603 0.1%/10ppm with a402Ω RT0603 series correction. R401+R411=56.602kΩ, giving3.3301V nominal. Its weighted temperature coefficient is10.107ppm/°C; the power calculation includes that value rather than rounding it down to10ppm.

The highest continuous ordinary-resistor dissipation is the330Ω bleeder, approximately34.9mW. R410 therefore uses **RC1206FR-07330RL**,0.25W in1206. Derating from70°C to zero at155°C permits88.2mW at125°C. Keep it away from the regulator's hot area. The remaining signal/feedback resistors dissipate substantially less and retain0603 packages. The separate Kelvin shunt has its own1W rating and thermal review.

| Function | Selected part / package | Analysis requirement |
|---|---|---|
|100n decoupling, eFuse dVdt | TDK C2012X7R1H104K085AA,0805,50V,X7R,10% | Effective≥65nF; eFuse inrush must be measured |
|1u rails and soft start | TDK C3216X7R1H105K160AB,1206,50V,X7R,10% | Effective0.65…1.30uF |
|2.2u LDOs and RUN delay | TDK C3216X7R1H225K160AB,1206,50V,X7R,10% | Effective1.43…2.86uF; meets LDO1uF minimum |
|330n rail delay | TDK C2012X7R1H334K125AA,0805,50V,X7R,10% | Effective214.5…429nF |
|22u buck input/output ceramics | TDK C3225X7R1E226M250AB,1210,25V,X7R,20% | Each≥11uF at actual bias/hot/aged condition; polymers supply the counted storage |
|4.7n compensation | TDK C2012C0G1H472J060AA,0805,50V,5% | Stable C0G dielectric |
|10p SIM /15p feedback | KEMET C0805C100J5GACTU / C0805C150J5GACTU,0805,50V,5% | C0G; qualify SIM loading |
|22n current integrator | KEMET C0805C223J5GACTU,0805,50V,5% | C0G; nonlinear loop qualification remains |

The65…130% X7R operating envelope is an engineering acceptance requirement, not a manufacturer guaranteed combined bias/aging bound. Initial10% tolerance and X7R15% temperature limits alone yield76.5…126.5%; the lower65% limit reserves further bias and aging loss. TDK's exact2.2uF characterization curve was visually reviewed: capacitance changes little around the1.2V timing-node and3.3V LDO biases, but decreases strongly near rated voltage. Typical curves do not establish lot limits. Measure effective capacitance after assembly and at operating bias/temperature; reject parts outside these bounds. The22uF parts have a separate, wider50% floor and are not counted in the polymer minimum storage calculation.

With these limits, C503 contributes185.9…614.9ms and C5081.239…4.099s, using the supervisor charge-current/threshold extremes. Soft start becomes24.75…93.79ms. These changes retain the minimum100ms external-logic guard and allow approximately0.300A worst-case capacitor charging with2.2mF total load. They do not establish the module's boot time or a guaranteed shutdown interval.

Manufacturer sources: [Panasonic ERA](https://industrial.panasonic.com/cdbs/www-data/pdf/RDM0000/AOA0000C307.pdf), [Yageo RT](https://yageogroup.com/content/datasheet/asset/file/PYU-RT_1-TO-0-01_ROHS_L), [TDK2.2uF characterization](https://product.tdk.com/info/en/documents/chara_sheet/C3216X7R1H225K160AB.pdf), [TDK22uF specification](https://product.tdk.com/en/search/capacitor/ceramic/mlcc/info?part_no=C3225X7R1E226M250AB). Sanitized part/stock records are in `build/passive-stock-*.json` and `build/general-resistor-stock.json`. Availability is a dated observation, not a procurement commitment.
