#!/usr/bin/env python3
"""Extract Rockchip's native PDF pin table without dropping wrapped pin names.

Requires pdfplumber; available in the bundled Codex document Python runtime.
Run with --check to compare the saved review table rather than overwrite it.
"""
import argparse
import csv
from io import StringIO
from pathlib import Path
import re
import pdfplumber

p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--check',action='store_true')
a=p.parse_args()
root=Path(__file__).resolve().parents[1]
rows=[]
with pdfplumber.open(root/'reference/rk3566-datasheet-v1.2.pdf') as pdf:
    for page_number in range(24,31):
        tables=pdf.pages[page_number-1].extract_tables()
        table=next(t for t in tables if t[0]==['Pin Name','PIN','Pin Name','PIN'])
        for row in table[1:]:
            for index in [0,2]:
                name,ball=row[index:index+2]
                if not ball:
                    continue
                if not name or not re.fullmatch(r'1?[A-Z]{1,2}\d+',ball):
                    raise RuntimeError(f'Invalid pin on page {page_number}: {row}')
                rows.append([ball,name.replace('\n','').replace(' ',''),page_number])
if len(rows)!=565 or len({row[0] for row in rows})!=565:
    raise RuntimeError('Expected exactly 565 unique package balls')
buffer=StringIO(newline='')
writer=csv.writer(buffer,lineterminator='\n')
writer.writerow(['ball','manufacturer_name','datasheet_page'])
writer.writerows(rows)
output=root/'pinmaps/rk3566.csv'
if a.check:
    if output.read_text()!=buffer.getvalue():
        raise RuntimeError('Saved pin table differs from manufacturer PDF extraction')
else:
    output.write_text(buffer.getvalue())
print('PASS: all 565 ball/name pairs match the native PDF table; symbol approval remains separate.')
