"""Read-only DigiKey snapshot; credentials are never written to output."""
from pathlib import Path
import json, datetime, urllib.request, urllib.parse
root=Path(__file__).resolve().parents[2]
k={}
for line in (root/'.env.distributors').read_text().splitlines():
 if '=' in line and not line.lstrip().startswith('#'):
  a,b=line.split('=',1); k[a.strip()]=b.strip().strip('\"').strip("'")
def post(url,data,headers):
 return json.loads(urllib.request.urlopen(urllib.request.Request(url,data=data,headers=headers),timeout=25).read())
def main():
 token=post('https://api.digikey.com/v1/oauth2/token',urllib.parse.urlencode({'client_id':k['DIGIKEY_CLIENT_ID'],'client_secret':k['DIGIKEY_CLIENT_SECRET'],'grant_type':'client_credentials'}).encode(),{'Content-Type':'application/x-www-form-urlencoded'})['access_token']
 h={'Authorization':'Bearer '+token,'X-DIGIKEY-Client-Id':k['DIGIKEY_CLIENT_ID'],'X-DIGIKEY-Locale-Site':'US','X-DIGIKEY-Locale-Currency':'USD','Content-Type':'application/json'}
 results=[]
 for mpn in ['HV1020-2R7505-R','LTC3128IUFD','LTC3128IFE','TPS62816QWRWYRQ1','TPS259470LRPWR','XAL7030-332MEC','XAL4020-221MEC']:
  d=post('https://api.digikey.com/products/v4/search/keyword',json.dumps({'Keywords':mpn,'Limit':6}).encode(),h)
  products=[]
  for p in d.get('Products',[]):
   variants=[{'number':v.get('DigiKeyProductNumber'),'stock':v.get('QuantityAvailableforPackageType'),'pricing':v.get('StandardPricing')} for v in p.get('ProductVariations',[])]
   products.append({'mpn':p.get('ManufacturerProductNumber'),'datasheet':p.get('DatasheetUrl'),'variants':variants})
   print(p.get('ManufacturerProductNumber'),[(v['number'],v['stock']) for v in variants])
  results.append({'query':mpn,'products':products})
 (root/'compact/reference/stock-refresh.json').write_text(json.dumps({'checked_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'results':results},indent=2))
if __name__=='__main__':
 try: main()
 except Exception as e: print('Refresh failed:',type(e).__name__)
