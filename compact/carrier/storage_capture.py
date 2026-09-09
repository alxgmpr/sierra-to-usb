"""Low-ESR local storage across the live regulator output."""

def capture(c):
    c.reset_sheet('storage')
    c.box('LOCAL STORAGE / LIVE SOURCE REMAINS CONNECTED',12.7,15.24,182.88,88.9)
    refs=['C405','C406','C415','C416'];xs=[30.48,76.2,121.92,167.64]
    for ref,x in zip(refs,xs):
        c.place('Device:C_Polarized',ref,'220u / 6.3V',x,63.5,
            foot='carrier:KEMET_D_7343_Median',
            fields={'MPN':'T530D227M006ATE005','Manufacturer':'KEMET / Yageo',
                    'Datasheet':'https://content.kemet.com/datasheets/kem_t2076_t52x-530.pdf',
                    'Status':'Selected from 2026-08-20 manufacturer table; current manufacturer median land pattern; assembly/stencil review pending'})
    for pin,net,y in [(1,'MODEM_VCC',45.72),(2,'GND',83.82)]:
        for ref,x in zip(refs,xs):
            c.wire(c.placed[ref][str(pin)][:2],(x,y))
            c.nets.setdefault(net,[]).append([ref,str(pin)])
        c.wire((xs[0],y),(xs[-1],y));c.label(net,(xs[0],y),180)
        for x in xs[1:-1]:
            c.items.append(f'(junction (at {x} {y}) (diameter 0) (color 0 0 0 0) (uuid {c.q(c.uid(net+str(x)+"storage"))}))')
    c.text('Anode marking faces MODEM_VCC. No series storage switch.\nThe buck supplies the load continuously; these capacitors\nsupply only the temporary difference during a load step.',20.32,114.3,1.5)
    c.text('Bank: 880 uF nominal, 704 uF at -20% initial tolerance.\nAt -20% endurance change: 563.2 uF (before temperature).\nESR: 5 mOhm each maximum initially; bank 1.25 mOhm.\nAt 2x endurance ESR: bank 2.5 mOhm (before temperature).\n\nThese are specified qualification-test limits, not an\nunlimited lifetime guarantee. See replacement power budget.\nConfirm effective C/ESR at operating temperature and\nfrequency, total module capacitance and both control loops.',20.32,149.86,1.5)
    c.text('Local 22 uF ceramics remain on the regulator sheet.\nPlace the polymer bank close to the M.2 VCC distribution,\nwith short, broad supply and return connections.\nNo routing, filled copper or thermal vias are generated.',20.32,180.34,1.5)
    return c.save_sheet('storage','Local transient storage',paper='A4')
