"""Read-only, sanitized DigiKey part queries; never log request credentials."""
import datetime
import json
import sys
import urllib.parse
from pathlib import Path
import refresh_stock as s

def main():
    target=Path(sys.argv[1])
    token=s.post('https://api.digikey.com/v1/oauth2/token',urllib.parse.urlencode({
        'client_id':s.k['DIGIKEY_CLIENT_ID'],'client_secret':s.k['DIGIKEY_CLIENT_SECRET'],
        'grant_type':'client_credentials'}).encode(),{'Content-Type':'application/x-www-form-urlencoded'})['access_token']
    headers={'Authorization':'Bearer '+token,'X-DIGIKEY-Client-Id':s.k['DIGIKEY_CLIENT_ID'],
        'X-DIGIKEY-Locale-Site':'US','Content-Type':'application/json'}
    results=[]
    for query in sys.argv[2:]:
        response=s.post('https://api.digikey.com/products/v4/search/keyword',json.dumps({'Keywords':query,'Limit':5}).encode(),headers)
        products=[]
        for p in response.get('Products',[]):
            products.append({'mpn':p.get('ManufacturerProductNumber'),'datasheet':p.get('DatasheetUrl'),
                'description':p.get('Description'),'parameters':p.get('Parameters'),
                'variants':[{'number':v.get('DigiKeyProductNumber'),'stock':v.get('QuantityAvailableforPackageType')}
                    for v in p.get('ProductVariations',[])]})
        results.append({'query':query,'products':products})
        target.write_text(json.dumps({'checked_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'results':results},indent=2)+'\n')
        print(query,[(p['mpn'],p['variants']) for p in products],flush=True)

if __name__=='__main__':
    try: main()
    except Exception as exc:
        print('Read-only stock query failed:',type(exc).__name__)
        sys.exit(1)
