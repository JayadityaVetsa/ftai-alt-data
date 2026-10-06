"""Build thesis-linked release 3 from reviewed records and existing public datasets."""
from pathlib import Path
import csv,json,re
R=Path(__file__).resolve().parents[1];P=R/'public/data'
d=json.loads((R/'data/workspace_curated.json').read_text(encoding='utf-8'))
old=json.loads((P/'expansion.json').read_text(encoding='utf-8'))
main=json.loads((P/'research.json').read_text(encoding='utf-8'))
ledger={s['id']:s for s in main['sources']+old['sources']}
manifest={}
if (R/'data/workspace_manifest.json').exists():manifest={s['id']:s for s in json.loads((R/'data/workspace_manifest.json').read_text(encoding='utf-8'))}
for s in d['sources']:ledger[s['id']]={**manifest.get(s['id'],{}),**s,'accessed':d['asOf'],'status':manifest.get(s['id'],{}).get('status','Public source reviewed; raw capture unavailable')}
d['sources']=list(ledger.values())
# Structured posting dates are more reliable than relative ages in search results.
for role in d['hiring']:
 f=R/'data/raw'/f"workspace_{role['source']}.html"
 if not f.exists():continue
 for block in re.findall(r'<script[^>]*type=[\"\x27]application/ld\+json[\"\x27][^>]*>(.*?)</script>',f.read_text(encoding='utf-8',errors='replace'),re.S):
  try:obj=json.loads(block)
  except (ValueError,TypeError):continue
  objs=obj if isinstance(obj,list) else [obj]
  for item in objs:
   if not isinstance(item,dict) or item.get('@type') not in ['JobPosting','SocialMediaPosting']:continue
   date=item.get('datePosted') or item.get('datePublished')
   if date:
    role['posted']=date;role['dateBasis']='Cached source JSON-LD; posting date, not date hire completed'
    ledger[role['source']]['published']=date[:10]
for row in d['ap']:
 row['margin']=row['ebitda']/row['revenue']
 row['grossProfit']=None if row['cogs'] is None else row['revenue']-row['cogs']
 row['grossMargin']=None if row['grossProfit'] is None else row['grossProfit']/row['revenue']
 row['opexRatio']=None if row['opex'] is None else row['opex']/row['revenue']
 row['mreShare']=None if row['mre'] is None else row['mre']/row['revenue']
a,b=d['ap'][0],d['ap'][-1]
d['apBridge']=dict(oldMargin=a['margin'],newMargin=b['margin'],marginPp=(b['margin']-a['margin'])*100,volume=(b['revenue']-a['revenue'])*a['margin'],residual=b['ebitda']-b['revenue']*a['margin'],incrementalMargin=(b['ebitda']-a['ebitda'])/(b['revenue']-a['revenue']),grossGrowth=b['grossProfit']/a['grossProfit']-1,revenueGrowth=b['revenue']/a['revenue']-1,earningsGrowth=b['ebitda']/a['ebitda']-1)
d['sites']=old['sites'];d['inventory']=old['inventory'];d['market']=old['market']
modelSites=[s for s in d['sites'] if s['id'] in ['microsoft_abilene','frontier']]
d['demandPresets']=[]
for label,phase,competitor,capture in [('Low',.25,.7,.1),('Base',.5,.5,.25),('High',1,.3,.4)]:
 electrical=sum(s['loadMw']*1.2*phase for s in modelSites)
 available=sum(s['knownAlternativeMw'] or 0 for s in modelSites)
 gross=sum(max(0,s['loadMw']*1.2*phase-(s['knownAlternativeMw'] or 0)) for s in modelSites)
 import math
 d['demandPresets'].append(dict(label=label,phase=phase,pue=1.2,competitorShare=competitor,capture=capture,electricalMw=electrical,knownAvailableMw=available,grossMw=gross,openMw=gross*(1-competitor),capturedMw=gross*(1-competitor)*capture,units=math.ceil(gross*(1-competitor)*capture/22.5*1.1),months=12,basis='Conditional scenario; two named leads, assumed 2027 readiness and 12-month gap; no verified grid dates'))
eia=main['eia']['rows'];patterns=['abilene','longhorn','shackelford','frontier']
hits=[r for r in eia if any(p in r['name'].lower() for p in patterns)]
d['inventory']['familyDonors']=[dict(family=family,donorReferences=len({r['engineSerial'] for r in d['inventory']['parts'] if r['family']==family and r['engineSerial']})) for family in sorted({r['family'] for r in d['inventory']['parts']})]
d['lifecycleAcquisition']=dict(eiaScope=main['eia']['note'],eiaSnapshotRows=len(eia),eiaNameCandidates=hits,eiaNamedCandidateCount=len(hits),eiaIdentityMatchedUnits=0,epaMatchedTests=None,epaScope='ICIS-Air schema reviewed. No downloaded facility-to-unit test join; no stack-test coverage claim.',mapScope='Approximate campus/city points from existing screen. Not independently surveyed turbine pads; overlapping points do not identify the same project.')
d['findings']=[
 dict(id='power-demand',thesis='Power',headline='Customers are buying on-site power; our named open-gap estimate is conditional.',value=d['demandPresets'][1]['openMw'],unit='MW modeled open demand',status='Our estimate',meaning='Two 2027 campus leads at 50% buildout, after known supply and a 50% competing-supply haircut.',financial='At 25% capture, roughly seven 25-MW units; not enough evidence to fill 100 deliveries from this sample.',sources=['crusoe_microsoft','oracle_site_update','gev_capacity']),
 dict(id='ap-margin',thesis='AP',headline='Lower percentage margins have not stopped AP profit dollars growing.',value=d['apBridge']['grossGrowth']*100,unit='percent gross-profit growth',status='Calculated from filings',meaning='Higher sales/workload, growing gross profit and lower overhead intensity support growth-driven dilution.',financial='Sustainable cash returns and like-for-like unit economics still require validation.',sources=['ap_sec_q2','ftai_q2']),
 dict(id='hiring',thesis='Power',headline='The hiring signal is industrialization, not a headcount growth estimate.',value=3,unit='reviewed employer job descriptions',status='Public postings',meaning='Configuration, supplier development and factory testing map to actual ramp bottlenecks; a recruiter post adds planning evidence.',financial='Supports execution investment; does not establish hires completed or units per quarter.',sources=['ftai_configuration','gensystems_test','jereh_sourcing','gensystems_planning']),
 dict(id='sci-map',thesis='SCI II + AP',headline='WestJet separates externally owned service exposure from AP feedstock.',value=34,unit='SCI II installed-engine positions',status='Aircraft disclosure + configuration arithmetic',meaning='17 SCI aircraft imply 34 positions; ten separate AP aircraft imply twenty more positions.',financial='SCI II can create MRE opportunities without FTAI owning all airframes; prices and transaction-level own capital are undisclosed.',sources=['westjet','sci2_warehouse'])
]
def out(name,rows):
 if not rows:return
 keys=list(dict.fromkeys(k for r in rows for k in r))
 with (P/f'{name}.csv').open('w',encoding='utf-8',newline='') as f:
  w=csv.DictWriter(f,fieldnames=keys);w.writeheader()
  for r in rows:w.writerow({k:json.dumps(v,ensure_ascii=False) if isinstance(v,(list,dict)) else v for k,v in r.items()})
for key,name in [('ap','ap_scorecard'),('hiring','hiring_functions'),('sci','sci_transactions'),('suppliers','supplier_windows'),('lifecycle','power_lifecycle'),('demandPresets','demand_scenarios'),('findings','thesis_findings'),('sources','workspace_sources')]:out(name,d[key])
out('ap_margin_bridge',[d['apBridge']]);out('ap_cash_checks',d['cashFacts']);out('lifecycle_acquisition',[d['lifecycleAcquisition']])
(P/'workspace.json').write_text(json.dumps(d,indent=2,ensure_ascii=False,allow_nan=False),encoding='utf-8')
print('Release 3:',len(d['findings']),'thesis-linked findings;',len(d['hiring']),'role records;',len(hits),'EIA name candidates; identity matches unverified')
