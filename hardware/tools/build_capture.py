#!/usr/bin/env python3
"""Reproduce appliance capture and register all manufacturer-audited custom symbols."""
from pathlib import Path
import re
import subprocess
import sys
from capture import ROOT, block, register
names=['poe','poe_pd','poe_status','ingress','cpu_power','boot','host_interface','peripheral_power','nic','nic_power','nic_interface','ddr_power','pmic','processor','main3v3','main5v','always_on','modem_power','modem','phy_power']
for name in names:subprocess.run([sys.executable,str(ROOT/'tools'/f'build_{name}.py')],check=True)
symbols={}
for path in sorted((ROOT/'reference').glob('*-captured.kicad_sym')):
 raw=path.read_text()
 for match in re.finditer(r'\(symbol "([^"]+)"',raw):
  name=match[1]
  if re.search(r'_\d+_\d+$',name):continue
  body=block(raw,match.start())
  assert name not in symbols or symbols[name]==body
  symbols[name]=body
register(symbols.values())
subprocess.run([sys.executable,str(ROOT/'tools/build_appliance.py')],check=True)
print('Registered',len(symbols),'audited appliance symbols.')
