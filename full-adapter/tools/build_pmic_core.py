"""RK809 LOGIC/GPU/NPU bucks with physical load-side Kelvin ties."""
import json
from schematic import ROOT, Sheet


def pmic_core():
    s=Sheet('pmic-core','LOGIC, GPU and NPU buck supplies')
    searches=json.loads((ROOT/'research/cpu-passives-search-2.json').read_text())
    cap22=next(p for p in searches[3]['result']['results'] if p['model']=='CL21A226MAYNNNE')
    parts={'22uF':cap22,
           '100nF':json.loads((ROOT/'research/ddr-passives-search.json').read_text())['searches'][6]['results'][0],
           '100R 1%':json.loads((ROOT/'research/cpu-control-resistors.json').read_text())[1]['result']['results'][0],
           '0.47uH':json.loads((ROOT/'research/pmic-buck-passives.json').read_text())['inductor']['results'][0]}

    def passive(ref,value,x,y,angle=0):
        part=parts[value]
        if ref.startswith('R'):lib,fp='Device:R_Small_US','Resistor_SMD:R_0402_1005Metric'
        elif ref.startswith('L'):lib,fp='Device:L','full-adapter:L_TDK_SPM5030'
        else:lib,fp='Device:C','Capacitor_SMD:C_'+('0805_2012' if value=='22uF' else '0402_1005')+'Metric'
        return s.place(lib,ref,x,y,value=value,angle=angle,fields={
            'Footprint':fp,'Manufacturer':part['manufacturer'],'MPN':part['model'],'LCSC':part['lcsc']})

    groups=[(1,'11','12','13','VDD_LOGIC','0.9V startup, slot 1; 2.5A maximum'),
            (2,'10','9','8','VDD_GPU','0.9V startup, slot 2; 2.5A maximum'),
            (4,'66','65','64','VDD_NPU','OFF at startup; 1.5A maximum')]
    for row,(unit,vin,sw,fb,rail,note) in enumerate(groups):
        y=45.72+row*76.2
        s.box(f'BUCK{unit} — {rail}: {note}',10.16,y-30.48,396.24,73.66)
        u=s.place('full-adapter:RK809-5','U5',147.32,y,unit=unit)
        for i,x in enumerate([35.56,66.04]):
            c=passive(f'C{430+row*10+i}','22uF',x,y+12.7)
            s.wire((x,y-2.54),c['1']);s.wire(c['2'],(x,y+20.32))
        s.wire((35.56,y-2.54),u[vin]);s.junction((66.04,y-2.54))
        s.wire((35.56,y+20.32),(66.04,y+20.32));s.power('GND',(66.04,y+20.32))
        s.wire((35.56,y-2.54),(35.56,y-10.16));s.junction((35.56,y-2.54))
        s.power('VCC3V3_SYS',(35.56,y-10.16))
        l=passive(f'L{430+row}','0.47uH',193.04,y-2.54,angle=90)
        a,b=sorted(l.values(),key=lambda p:p[0]);s.wire(u[sw],a);s.wire(b,(391.16,y-2.54))
        s.power(rail,(375.92,y-2.54));s.junction((375.92,y-2.54))
        s.place('power:PWR_FLAG',f'#FLGcore{row}',391.16,y-2.54)
        for i,x in enumerate([264.16,297.18,330.2,363.22]):
            c=passive(f'C{432+row*10+i}','22uF' if i<3 else '100nF',x,y+12.7)
            s.wire((x,y-2.54),c['1']);s.junction((x,y-2.54))
            s.wire(c['2'],(x,y+22.86))
            if i:s.wire((x-33.02,y+22.86),(x,y+22.86))
            if 0<i<3:s.junction((x,y+22.86))
        s.power('GND',(363.22,y+22.86))
        r=passive(f'R{430+row}','100R 1%',228.6,y+12.7)
        s.wire((228.6,y-2.54),r['1']);s.junction((228.6,y-2.54))
        s.wire(r['2'],(228.6,y+35.56))
        s.wire(u[fb],(116.84,y));s.wire((116.84,y),(116.84,y+35.56))
        s.wire((116.84,y+35.56),(228.6,y+35.56))
        s.label(rail+'_FB',(228.6,y+35.56),global_net=True)
        # Copper-only tie at the processor, not an assembly part. Its separate
        # sense net forces a dedicated return trace to the PMIC feedback pin.
        nt=s.place('Device:NetTie_2',f'NT{430+row}',66.04,y+35.56,
                   fields={'Footprint':'NetTie:NetTie-2_SMD_Pad0.5mm'})
        s.wire(nt['1'],(40.64,y+35.56));s.power(rail,(40.64,y+35.56))
        s.wire(nt['2'],(81.28,y+35.56));s.label(rail+'_FB',(81.28,y+35.56),global_net=True)
    s.text('NT430 / NT431 / NT432: place at U1 supply pads. Copper ties, no assembled parts.\n100R resistors remain at the regulator output banks; route each FB trace separately from U1.\nKeep FB away from switching nodes. See Rockchip tablet reference p22.',15.24,254,1.27)
    s.text('2 x 22uF local input; 3 x 22uF + 100nF local output per buck. Processor bypass is separate.\nEnforce RK3568B2 voltage limits in firmware: LOGIC <=0.99V; GPU/NPU <=1.10V.',15.24,276.86,1.0)
    return s
