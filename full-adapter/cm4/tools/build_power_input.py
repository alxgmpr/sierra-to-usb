"""USB-C power negotiation, voltage qualification and two-input arbitration."""
import json
from cad import ROOT,Sheet

PARTS={}
for file in ['initial-parts.json','power-input-parts.json']:
    for entry in json.loads((ROOT/'research'/file).read_text())['parts']:
        for p in entry.get('results',[entry]):PARTS[p['model']]=p


def part(s,sym,ref,mpn,fp,x,y,value=None,angle=0):
    p=PARTS[mpn]
    return s.place(sym,ref,x,y,value=value or mpn,angle=angle,fields={
        'MPN':mpn,'Manufacturer':p['manufacturer'],'LCSC':p['lcsc'],
        'Footprint':fp,'Datasheet':p.get('datasheet','')})


def resistor(s,ref,value,x,y,net1,net2,precise=False):
    mpn=({'453k':'RT0603BRD07453KL','523k':'RT0603BRD07523KL',
        '6.8k':'RT0603BRD076K8L','10k':'RT0603BRD0710KL'} if precise else {
        '1k':'0402WGF1001TCE','4.7k':'0402WGF4701TCE',
        '10k':'0402WGF1002TCE','100k':'0402WGF1003TCE','22.6k':'0402WGF2262TCE',
        '22.1k':'0402WGF2212TCE','49.9k':'0402WGF4992TCE','120k':'0402WGF1203TCE'})[value]
    fp='Resistor_SMD:R_0603_1608Metric' if precise else 'Resistor_SMD:R_0402_1005Metric'
    p=part(s,'Device:R_Small_US',ref,mpn,fp,x,y,value+' '+('0.1%' if precise else '1%'))
    if net1 is not None:s.connect(ref,'1',net1,global_net=True)
    if net2 is not None:s.connect(ref,'2',net2,global_net=True)
    return p


def cap(s,ref,value,x,y,net,voltage=16):
    mpn,fp={'100nF':('CC0402KRX7R9BB104','C_0402_1005Metric'),
            '1uF':('CL10A105KO8NNNC','C_0603_1608Metric'),
            '2.2uF':('CL21A225KBQNNNE','C_0805_2012Metric')}[value]
    p=part(s,'Device:C',ref,mpn,'Capacitor_SMD:'+fp,x,y,value+(' 50V' if value!='1uF' else ' 16V'))
    s.wire(p['1'],(x,y-10.16));s.label(net,(x,y-10.16),0,True)
    s.wire(p['2'],(x,y+10.16));s.power('GND',(x,y+10.16))
    return p


def r_body(s,ref,value,x,y,precise=False):
    return resistor(s,ref,value,x,y,None,None,precise)


def vertical_divider(s,values,x,ys,top,sense,sense_after):
    ps=[r_body(s,ref,val,x,y,precise) for (ref,val,precise),y in zip(values,ys)]
    s.wire(ps[0]['1'],(x,ys[0]-12.7));s.label(top,(x,ys[0]-12.7),0,True)
    for a,b in zip(ps,ps[1:]):s.wire(a['2'],b['1'])
    y=(ps[sense_after]['2'][1]+ps[sense_after+1]['1'][1])/2
    s.label(sense,(x,y),0,True)
    s.wire(ps[-1]['2'],(x,ys[-1]+12.7));s.power('GND',(x,ys[-1]+12.7))
    return ps


def aux_usbc():
    s=Sheet('aux-usbc','USB-C: connector and protection')
    s.box('J150 / 5 A contacts / power-only port',10.16,15.24,157.48,185.42)
    s.place('cm4:USB4105-GF-A-120','J150',86.36,88.9)
    for n in ['A4','A9','B4','B9']:
        p=s.pins['J150',n];s.wire(p,(p[0],40.64))
    xs=sorted(s.pins['J150',n][0] for n in ['A4','A9','B4','B9'])
    s.wire((xs[0],40.64),(xs[-1],40.64))
    for x in xs[1:-1]:s.junction((x,40.64))
    s.label('AUX_VBUS',(xs[-1],40.64),0,True)
    s.place('power:PWR_FLAG','#FLG150',xs[0],40.64)
    for n in ['A1','A12','B1','B12','SH']:
        p=s.pins['J150',n];s.wire(p,(p[0],157.48))
    xs=sorted(s.pins['J150',n][0] for n in ['A1','A12','B1','B12','SH'])
    s.wire((xs[0],157.48),(xs[-1],157.48))
    for x in xs[1:-1]:s.junction((x,157.48))
    s.power('GND',(xs[-1],157.48));s.place('power:PWR_FLAG','#FLG151',xs[0],157.48)
    for n,net in [('A5','AUX_CC1_PORT'),('B5','AUX_CC2_PORT')]:s.connect('J150',n,net,global_net=True)
    for n in ['A6','B6','A7','B7','A8','B8']:s.connect('J150',n,None)
    s.text('No data connection at this port.\nUse a USB PD supply offering 20 V / 3 A.\nExternal source flags are at J150;\nno internal supply is presumed here.',17.78,175.26)
    s.box('20 V short-to-VBUS and IEC ESD protection',180.34,15.24,223.52,137.16)
    s.place('cm4:TPD6S300RUKR','U151',287.02,91.44)
    for pin,net in [('4','AUX_CC1_PORT'),('7','AUX_CC1_PORT'),('5','AUX_CC2_PORT'),('6','AUX_CC2_PORT'),
                    ('12','AUX_CC1'),('11','AUX_CC2'),('9','AUX_WINDOW_OK')]:s.connect('U151',pin,net,global_net=True)
    p=s.pins['U151','10'];s.wire(p,(p[0],43.18));s.label('AUX_3V3',(p[0],43.18),180,True)
    p=s.pins['U151','3'];s.wire(p,(p[0],33.02));s.label('AUX_CC_VBIAS',(p[0],33.02),0,True)
    for n in ['8','13','18','21']:
        p=s.pins['U151',n];s.wire(p,(p[0],134.62))
    xs=sorted(s.pins['U151',n][0] for n in ['8','13','18','21'])
    s.wire((xs[0],134.62),(xs[-1],134.62))
    for x in xs[1:-1]:s.junction((x,134.62))
    s.power('GND',(xs[-1],134.62))
    s.box('Unused protection channels / local bypass',180.34,165.1,223.52,86.36)
    s.place('cm4:TPD6S300RUKR','U151',236.22,218.44,unit=2)
    ends=[]
    for n in ['1','2','14','15','16','17','19','20']:
        p=s.pins['U151',n];end=(193.04,p[1]);s.wire(p,end);ends.append(end)
    ends.sort(key=lambda p:p[1])
    s.wire(ends[0],(193.04,246.38))
    for p in ends[1:]:s.junction(p)
    s.power('GND',(193.04,246.38))
    cap(s,'C150','100nF',327.66,203.2,'AUX_CC_VBIAS',50)
    cap(s,'C151','1uF',378.46,203.2,'AUX_3V3')
    s.text('RPD_Gx are tied to port CCx for cold start.\nHUSB238 has permanent sink Rd, including unpowered.\nUnused U151 channels are grounded per TI guidance.',294.64,233.68,1.1)
    return s


def aux_pd():
    s=Sheet('aux-pd','USB-C: PD and housekeeping')
    s.box('HUSB238_002DD / resistor configuration',10.16,15.24,187.96,236.22)
    s.place('cm4:HUSB238_002DD','U150',101.6,96.52)
    for pin,net in [('1','AUX_VBUS'),('4','AUX_CC1'),('5','AUX_CC2'),('10','AUX_PD_GATE_N')]:
        s.connect('U150',pin,net,global_net=True)
    s.connect('U150','11','GND',global_net=True)
    for n in ['2','3','6','7','8']:s.connect('U150',n,None)
    r=r_body(s,'R150','22.6k',152.4,193.04)
    p=s.pins['U150','9'];s.wire(p,(152.4,p[1]));s.wire((152.4,p[1]),r['1'])
    s.label('AUX_PD_ISET',(152.4,p[1]),0,True)
    s.wire(r['2'],(152.4,205.74));s.power('GND',(152.4,205.74))
    cap(s,'C152','2.2uF',48.26,193.04,'AUX_VBUS',50)
    s.text('VSET open requests 20 V; 22.6k sets 3 A.\nNo I2C override; D+/D- legacy detection unused.\nExact _002DD: Next PDO on mismatch, GATE at POR.\nGATE alone does not qualify available input power.\nVoltage window and fault gating are on the next sheet.',17.78,231.14,1.1)
    s.box('Housekeeping supply / alive before the power mux',210.82,15.24,193.04,116.84)
    d=part(s,'Device:D_Schottky_Dual_CommonCathode_AAK','D150','BAT54CLT1G',
        'Package_TO_SOT_SMD:SOT-23',307.34,38.1)
    s.field_position('D150','Reference',307.34,25.4);s.field_position('D150','Value',307.34,27.94)
    for pin,net in [('1','AUX_VBUS'),('2','AUX_3V3'),('3','AUX_LDO_IN')]:s.connect('D150',pin,net,global_net=True)
    s.place('cm4:TLV70433DBVR','U152',307.34,73.66)
    for pin,net in [('2','AUX_LDO_IN'),('3','AUX_3V3'),('1','GND')]:s.connect('U152',pin,net,global_net=True)
    for n in ['4','5']:s.connect('U152',n,None)
    cap(s,'C153','1uF',378.46,99.06,'AUX_3V3')
    cap(s,'C154','100nF',241.3,99.06,'AUX_LDO_IN',50)
    # External J150 power reaches this domain through passive diode D150.
    s.place('power:PWR_FLAG','#FLG152',241.3,88.9)
    s.text('D150: input isolation plus OUT-to-IN reverse-current bypass.',218.44,121.92,1.1)
    s.box('PD gate permission / disabled if the PD controller opens GATE',210.82,144.78,193.04,106.68)
    q=part(s,'Transistor_FET:Q_PMOS_GSD','Q150','DMP2035U-7','Package_TO_SOT_SMD:SOT-23',279.4,198.12,angle=180)
    s.field_position('Q150','Reference',266.7,193.04);s.field_position('Q150','Value',261.62,195.58)
    s.wire(q['2'],(q['2'][0],165.1));s.label('AUX_3V3',(q['2'][0],165.1),180,True)
    rb=r_body(s,'R152','10k',325.12,177.8)
    s.wire(rb['1'],(325.12,165.1));s.wire((325.12,165.1),(q['2'][0],165.1))
    s.junction((q['2'][0],165.1))
    rg=part(s,'Device:R_Small_US','R151','0402WGF1001TCE','Resistor_SMD:R_0402_1005Metric',355.6,q['1'][1],value='1k 1%',angle=90)
    s.wire(q['1'],rg['1']);s.wire(rb['2'],(325.12,q['1'][1]));s.junction((325.12,q['1'][1]))
    s.wire((307.34,q['1'][1]),(307.34,190.5));s.junction((307.34,q['1'][1]))
    s.label('AUX_PERMISSION_GATE',(307.34,190.5),180,True)
    s.wire(rg['2'],(381,q['1'][1]));s.label('AUX_PD_GATE_N',(381,q['1'][1]),0,True)
    rc=r_body(s,'R153','4.7k',q['3'][0],223.52)
    s.wire(q['3'],rc['1']);s.label('AUX_GATE_DRIVE',(q['3'][0],210.82),0,True)
    s.wire(rc['2'],(q['3'][0],233.68));s.label('AUX_WINDOW_OK',(q['3'][0],233.68),0,True)
    s.text('Q150 supplies the window-OK node only while GATE is low.\nU153 or U151 can clamp that node low to disconnect AUX.\nAll pull-ups here use AUX_3V3; no CM4 back-power path.',218.44,241.3,1.1)
    return s


def aux_window():
    s=Sheet('aux-window','USB-C: voltage qualification')
    s.box('Undervoltage / nominal 18.52 V rising',10.16,15.24,119.38,157.48)
    vertical_divider(s,[('R154','453k',True),('R155','10k',True)],66.04,[71.12,137.16],'AUX_VBUS','AUX_UV_SENSE',0)
    s.box('1% reference / wired fault outputs',142.24,15.24,132.08,157.48)
    s.place('cm4:TPS3700DDCR','U153',208.28,91.44)
    for pin,net in [('3','AUX_UV_SENSE'),('4','AUX_OV_SENSE'),('5','AUX_3V3'),('2','GND'),('1','AUX_WINDOW_OK'),('6','AUX_WINDOW_OK')]:
        s.connect('U153',pin,net,global_net=True)
    cap(s,'C155','100nF',208.28,147.32,'AUX_3V3')
    s.box('Overvoltage / nominal 21.592 V rising',287.02,15.24,116.84,157.48)
    ps=vertical_divider(s,[('R156','523k',True),('R157','6.8k',True),('R158','10k',True)],345.44,[55.88,101.6,147.32],'AUX_VBUS','AUX_OV_SENSE',1)
    s.label('AUX_OV_UPPER',(345.44,78.74),0,True)
    s.box('Default disconnected / LOW on OV1 permits AUX',10.16,185.42,393.7,66.04)
    s.place('cm4:SN74LVC1G14DBVR','U154',210.82,218.44)
    s.field_position('U154','Reference',251.46,198.12);s.field_position('U154','Value',251.46,200.66)
    for pin,net in [('2','AUX_WINDOW_OK'),('4','AUX_MUX_DISABLE'),('5','AUX_3V3'),('3','GND')]:s.connect('U154',pin,net,global_net=True)
    s.connect('U154','1',None)
    resistor(s,'R159','100k',86.36,228.6,'AUX_WINDOW_OK','GND')
    resistor(s,'R160','100k',322.58,228.6,'AUX_3V3','AUX_MUX_DISABLE')
    cap(s,'C156','100nF',378.46,228.6,'AUX_3V3')
    return s


def input_mux():
    s=Sheet('input-mux','Power input arbitration')
    s.box('TPS2121 / highest qualified input wins',10.16,15.24,393.7,137.16)
    s.place('cm4:TPS2121RUXR','U160',210.82,88.9)
    for pin,net in [('7','AUX_VBUS'),('2','POE_12V'),('[1,8]','VIN_SYS'),
                    ('6','AUX_PRIORITY'),('3','POE_PRIORITY'),('5','AUX_MUX_DISABLE'),('4','POE_MUX_DISABLE'),
                    ('10','MUX_ILIM'),('11','MUX_SS'),('12','GND')]:s.connect('U160',pin,net,global_net=True)
    s.connect('U160','9','GND',global_net=True)
    vertical_divider(s,[('R161','49.9k',False),('R162','10k',False)],58.42,[66.04,121.92],'AUX_VBUS','AUX_PRIORITY',0)
    vertical_divider(s,[('R163','49.9k',False),('R164','10k',False)],360.68,[66.04,121.92],'POE_12V','POE_PRIORITY',0)
    s.box('Current limit, slow initial rise, local bypass',10.16,165.1,393.7,66.04)
    resistor(s,'R165','22.1k',50.8,200.66,'MUX_ILIM','GND')
    cap(s,'C160','1uF',134.62,200.66,'MUX_SS')
    cap(s,'C161','2.2uF',218.44,200.66,'POE_12V',50)
    cap(s,'C162','2.2uF',302.26,200.66,'VIN_SYS',50)
    cap(s,'C163','100nF',373.38,200.66,'VIN_SYS',50)
    s.text('22.1k: 4.5 A nominal limit, 4-5 A IC range before resistor tolerance.\n1 uF SS: about 0.09 V/ms initial rise; downstream converters must have input UVLO.\nPOE_12V and POE_MUX_DISABLE await PD/class circuitry. Main-bus bulk and transient closure remain open.\nBoth inputs invalid => high impedance. Full-load thermal budget and rail converters remain in progress.',17.78,241.3,1.1)
    return s
