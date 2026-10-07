#!/usr/bin/env python3
"""Full appliance ERC and native-netlist checks; output stays outside the repository."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent/'tools'))
from check_appliance_capture import main
if __name__=='__main__':main()
