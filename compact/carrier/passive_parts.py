"""Exact passive BOM selections, applied in the schematic source before export."""
R_DS='https://yageogroup.com/content/datasheet/asset/file/PYU-RC_GROUP_51_ROHS_L'
RT_DS='https://yageogroup.com/content/datasheet/asset/file/PYU-RT_1-TO-0-01_ROHS_L'
ERA_DS='https://industrial.panasonic.com/cdbs/www-data/pdf/RDM0000/AOA0000C307.pdf'
TDK_DS='https://product.tdk.com/system/files/dam/doc/product/capacitor/ceramic/mlcc/catalog/mlcc_commercial_general_en.pdf'
GENERAL_R={'1.02k':'1K02','100R':'100R','100k':'100K','10k':'10K','15k':'15K','1M':'1M','1k':'1K','200k':'200K','22R':'22R','330R':'330R','340k':'340K','4.7k':'4K7','681k':'681K'}
SPECIAL_R={
 'R301':('ERJ-3EKF2003V','Panasonic','https://industrial.panasonic.com/cdbs/www-data/pdf/RDA0000/AOA0000C304.pdf'),
 'R205':('ERJ-3EKF22R0V','Panasonic','https://industrial.panasonic.com/cdbs/www-data/pdf/RDA0000/AOA0000C304.pdf'),
 'R206':('ERJ-3EKF22R0V','Panasonic','https://industrial.panasonic.com/cdbs/www-data/pdf/RDA0000/AOA0000C304.pdf'),
 'R207':('ERJ-3EKF22R0V','Panasonic','https://industrial.panasonic.com/cdbs/www-data/pdf/RDA0000/AOA0000C304.pdf'),
 'R410':('RC1206FR-07330RL','Yageo',R_DS),
 'R401':('ERA-3ARB5622V','Panasonic',ERA_DS),
 'R402':('ERA-3ARB103V','Panasonic',ERA_DS),
 'R411':('RT0603BRD07402RL','Yageo',RT_DS),
 'R406':('RT0603BRD0741K2L','Yageo',RT_DS),
 'R407':('RT0603BRD0756K2L','Yageo',RT_DS),
 'R507':('RT0603BRD0795K3L','Yageo',RT_DS),
}
C_PARTS={
 '100n':('C2012X7R1H104K085AA','TDK','0805_2012Metric'),
 '1u':('C3216X7R1H105K160AB','TDK','1206_3216Metric'),
 '2.2u':('C3216X7R1H225K160AB','TDK','1206_3216Metric'),
 '330n':('C2012X7R1H334K125AA','TDK','0805_2012Metric'),
 '22u':('C3225X7R1E226M250AB','TDK','1210_3225Metric'),
 '4.7n':('C2012C0G1H472J060AA','TDK','0805_2012Metric'),
 '15p':('C0805C150J5GACTU','KEMET','0805_2012Metric'),
 '10p':('C0805C100J5GACTU','KEMET','0805_2012Metric'),
 '22n':('C0805C223J5GACTU','KEMET','0805_2012Metric'),
}

def selection(kind,ref,value):
    base=value.split()[0]
    if kind=='R':
        if ref in SPECIAL_R:mpn,mfr,ds=SPECIAL_R[ref]
        elif base in GENERAL_R:mpn,mfr,ds='RC0603FR-07'+GENERAL_R[base]+'L','Yageo',R_DS
        else:return '',{}
        size='1206_3216Metric' if ref=='R410' else '0603_1608Metric'
        return 'Resistor_SMD:R_'+size,{'MPN':mpn,'Manufacturer':mfr,'Datasheet':ds}
    if kind=='C' and base in C_PARTS:
        mpn,mfr,size=C_PARTS[base]
        ds=TDK_DS if mfr=='TDK' else 'https://yageogroup.com/content/datasheet/asset/file/KEM_C1003_C0G_SMD'
        return 'Capacitor_SMD:C_'+size,{'MPN':mpn,'Manufacturer':mfr,'Datasheet':ds,'Qualification':'See passive-review.md for DC-bias and effective-capacitance acceptance limits'}
    return '',{}
