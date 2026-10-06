"""Publish reviewed customer cases, inventory provenance and aviation observations."""
from pathlib import Path
import csv,json,re
ROOT=Path(__file__).resolve().parents[1];PUB=ROOT/'public/data';RAW=ROOT/'data/raw'
d=json.loads((ROOT/'data/expansion_curated.json').read_text(encoding='utf-8'))
manifest={}
for file in ['source_manifest.json','extra_manifest.json','expansion_manifest.json','inventory_manifest.json','followup_manifest.json']:
 p=ROOT/'data'/file
 if p.exists():
  for r in json.loads(p.read_text(encoding='utf-8')):manifest[r['id']]=r
for source in d['sources']:
 acquired=manifest.get(source['id'],{})
 source.update({k:v for k,v in acquired.items() if k in ['status','sha256','bytes','error','resolvedUrl']})
 source.setdefault('status','Browser reviewed; no bulk snapshot')
 source['accessed']='2026-10-05'
 source['browserReviewed']=source['id'] not in ['module_store','market_quote']
def publication(text):
 m=re.search(r'lastPublishedDate":("[^"]+")',text)
 return json.loads(m[1]) if m else None
html=(RAW/'ceros_inventory.html').read_text(encoding='utf-8')
issue=re.search(r'issue:\s*(\{[^\n]+\})',html)
metadata=json.loads(issue[1]) if issue else {}
captures=json.loads((RAW/'wayback_ceros.json').read_text(encoding='utf-8'))
history=[]
for id in ['archive_'+captures[1][1],'archive_'+captures[-1][1]] if len(captures)>1 else []:
 p=RAW/f'{id}.html';row=dict(capture=id.replace('archive_',''),sourceUrl=manifest.get(id,{}).get('url'),embeddedPublished=None,status='Unavailable',stockCount=None)
 if p.exists():row.update(embeddedPublished=publication(p.read_text(encoding='utf-8',errors='replace')),status='Captured HTML reviewed')
 history.append(row)
history.append(dict(capture='2026-10-05 live acquisition',sourceUrl='https://view.ceros.com/fortress-investment/cfm56material/p/1',embeddedPublished=metadata.get('lastPublishedDate'),status='Current HTML reviewed',stockCount=None))
catalog=[dict(family=f,category=c,partNumber=None,serialNumber=None,quantity=None,condition=None,powerEligibility='Unverified',leadTimeDays=None,basis='Historical program capability; not a stock listing',source='ceros_inventory') for f in ['CFM56-5B','CFM56-7B'] for c in ['Fan','Core','LPT']]
payload=(RAW/'ceros_payload.js').read_text(encoding='utf-8')
urls=sorted(set(json.loads('"'+m+'"') for m in re.findall(r'"url":"((?:\\.|[^"\\])*)"',payload)))
d['inventory']=dict(status='Public serial-level list not located',published=metadata.get('lastPublishedDate'),historicalShelfClaim=60,historicalShelfClaimBasis='Undated stock assertion on a February 2024 publication; not verified October 2026 quantity',moduleStoreLinks=[u for u in urls if 'modulestore' in u.lower()],history=history,catalog=catalog,captureIndexCount=max(0,len(captures)-1),captureCoverage='First 12 monthly-collapsed captures returned by CDX; first and last of that set inspected. No claim of complete archive coverage.',serialRows=[],note='Same embedded publication in sampled archive captures and current page does not prove unchanged physical inventory. No inventory additions, removals, excess by module type or delivery times inferred.')
def out(name,rows):
 if not rows:return
 keys=list(dict.fromkeys(k for row in rows for k in row))
 with (PUB/f'{name}.csv').open('w',encoding='utf-8',newline='') as f:
  w=csv.DictWriter(f,fieldnames=keys);w.writeheader()
  for r in rows:w.writerow({k:json.dumps(v,ensure_ascii=False) if isinstance(v,(dict,list)) else v for k,v in r.items()})
for key,name in [('sites','customer_sites'),('context','demand_context'),('procurements','supplier_procurement'),('moduleProduction','module_production'),('aviationEarnings','aviation_results'),('evidence','expansion_evidence'),('sources','expansion_sources')]:out(name,d[key])
out('inventory_history',history);out('inventory_catalog',catalog);out('market_observation',[d['market']])
(PUB/'expansion.json').write_text(json.dumps(d,ensure_ascii=False,indent=2,allow_nan=False),encoding='utf-8')
# Main source ledger gets the new original-source records as well.
main=json.loads((PUB/'research.json').read_text(encoding='utf-8'));ledger={s['id']:s for s in main['sources']}
for s in d['sources']:ledger[s['id']]={**ledger.get(s['id'],{}),**s}

for c in main['catalysts']:
 if c['event']=='12-month investment horizon ends':c['date']=d['horizonEnd']
main['sources']=list(ledger.values());main['asOf']=d['asOf'];main['release']='Customer and production studies v2; retained permit observations keep their original dates.'
(PUB/'research.json').write_text(json.dumps(main,ensure_ascii=False,indent=2,allow_nan=False),encoding='utf-8');out('sources',main['sources'])
print('Published',len(d['sites']),'customer case studies;',len(history),'inventory provenance snapshots;',len(d['moduleProduction']),'module output observations')
