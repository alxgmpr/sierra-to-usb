"""Five passive RF breakouts (four cellular, one optional GPS). Coax-to-module is a separate harness, not an M.2 net."""
def capture(c):
    c.reset_sheet('rf')
    c.text('FIVE PASSIVE 50 OHM ANTENNA BREAKOUTS',12.7,12.7,1.8)
    for i,y in enumerate([33.02,63.5,93.98,124.46,154.94]):
        mhf='J'+str(601+i*2);sma='J'+str(602+i*2);net='RF_GPS' if i==4 else 'RF'+str(i+1)
        c.place('Connector:Conn_Coaxial',mhf,'20449-001E-03',48.26,y,angle=180,
            foot='carrier:IPEX_MHF4_20449_001E_03',fields={'MPN':'20449-001E-03','Manufacturer':'I-PEX',
            'Datasheet':'https://www.i-pex.com/sites/default/files/downloads/pdf/2D_MHF_4_RECEPTACLE_1_20449C22.pdf'})
        c.place('Connector:Conn_Coaxial',sma,'132289',154.94,y,
            foot='carrier:SMA_Amphenol_132289_Manufacturer',fields={'MPN':'132289','Manufacturer':'Amphenol RF',
            'Datasheet':'https://www.amphenolrf.com/en-us/assets/file/4065786470/'})
        a=c.placed[mhf]['1'][:2];b=c.placed[sma]['1'][:2]
        midpoint=((a[0]+b[0])/2,y)
        labelpoint=(midpoint[0],y-5.08)
        c.wire(a,b);c.wire(midpoint,labelpoint);c.label(net,labelpoint,0)
        c.items.append(f'(junction (at {midpoint[0]} {midpoint[1]}) (diameter 0) (color 0 0 0 0) (uuid {c.q(c.uid(net+"junction"))}))')
        c.nets[net]=[[mhf,'1'],[sma,'1']]
        c.connect(mhf,2,'GND');c.connect(sma,2,'GND')
        c.text('50 ohm PCB launch',78.74,y+7.62)
    c.text('RF1..RF4 are neutral port IDs.\nConnect all four module antennas\nusing four CAB.01072 harnesses.\nGPS: fifth CAB.01072 only for\na dedicated module GNSS port.\n\nSierra mapping:\nRF1 MAIN / RF2 MIMO1\nRF3 MIMO2 / RF4 AUX\n\nQuectel mapping:\nRF1 ANT0 / RF2 ANT1\nRF3 ANT2 / RF4 ANT3\n\nNo active GNSS bias supply.\nNo mmWave IF paths.\nHarness loss and channel return\nloss require qualification.\nSee RF/mechanical routing review.',195.58,30.48)
    c.text('Coax harnesses terminate at module RF receptacles, not at M.2 edge contacts.',12.7,180.34)
    return c.save_sheet('rf','Four cellular and one GPS breakout',paper='A4')
