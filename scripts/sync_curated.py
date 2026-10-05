"""Refresh curated observations/manifests without reprocessing unchanged bulk snapshots."""
import csv,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];PUB=ROOT/'public/data'
d=json.loads((PUB/'research.json').read_text(encoding='utf-8'))
c=json.loads((ROOT/'data/curated.json').read_text(encoding='utf-8'))
d.update(c)
sources={r['id']:r for r in d['sources']}
for name in ['source_manifest.json','extra_manifest.json']:
 for r in json.loads((ROOT/'data'/name).read_text(encoding='utf-8')):
  sources[r['id']]={**sources.get(r['id'],{}),**r}
d['sources']=list(sources.values())
eligible=[p for p in d['projects'] if p['eligible'] and p['mw'] is not None]
d['coverage'].update(candidates=len(d['projects']),knownCapacity=sum(p['mw'] is not None for p in d['projects']),eligibleSites=len(eligible),eligibleMw=sum(p['mw'] for p in eligible))
for key in ['projects','facts','sources','translations','catalysts']:
 rows=d[key];cols=list(dict.fromkeys(k for r in rows for k in r))
 with (PUB/f'{key}.csv').open('w',encoding='utf-8',newline='') as f:
  w=csv.DictWriter(f,fieldnames=cols);w.writeheader();w.writerows(rows)
(PUB/'research.json').write_text(json.dumps(d,ensure_ascii=False,indent=2,allow_nan=False),encoding='utf-8')
print('FAA records',d['fleet']['count'],'Missing year',d['fleet']['missingYear'],'EIA observations',len(d['eia']['rows']),'changes',len(d['eia']['changes']))
