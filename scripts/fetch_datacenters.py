"""Acquire reviewed primary originals with checksums; failures never become zero demand."""
from pathlib import Path
import json,hashlib,time,concurrent.futures,urllib.request
R=Path(__file__).resolve().parents[1];raw=R/'data/raw/datacenters';raw.mkdir(parents=True,exist_ok=True)
d=json.loads((R/'data/datacenter_study.json').read_text(encoding='utf-8'))
def fetch(s):
    id=s['id'];hit=list(raw.glob(id+'.*'))
    if hit:
        b=hit[0].read_bytes();return dict(id=id,url=s['url'],status='cached',bytes=len(b),sha256=hashlib.sha256(b).hexdigest(),path=str(hit[0].relative_to(R)),accessed='2026-10-06')
    try:
        req=urllib.request.Request(s['url'],headers={'User-Agent':'FTAIStudentResearch/1.0 public-source verification contact via repository JayadityaVetsa/ftai-alt-data'})
        with urllib.request.urlopen(req,timeout=12) as response:
            b=response.read(10_000_001);ct=response.headers.get('Content-Type','')
        if len(b)>10_000_000:raise ValueError('Document exceeds 10 MB acquisition limit')
        ext='.pdf' if b.startswith(b'%PDF') else '.html';f=raw/(id+ext);f.write_bytes(b)
        return dict(id=id,url=s['url'],status='downloaded',bytes=len(b),sha256=hashlib.sha256(b).hexdigest(),path=str(f.relative_to(R)),contentType=ct,accessed='2026-10-06')
    except Exception as e:return dict(id=id,url=s['url'],status='failed',error=str(e)[:250],accessed='2026-10-06')
with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
    results=list(pool.map(fetch,d['sources']))
(R/'data/datacenter_acquisition.json').write_text(json.dumps(results,indent=2)+'\n',encoding='utf-8')
# Plotly's Natural Earth derived geometry is stored locally for stable Pages maps.
geo=R/'public/geo';geo.mkdir(exist_ok=True)
try:
    with urllib.request.urlopen('https://cdn.plot.ly/un/usa_110m.json',timeout=15) as response:b=response.read()
    json.loads(b);(geo/'usa_110m.json').write_bytes(b)
    print('US map geometry acquired',len(b))
except Exception as e:print('US map geometry acquisition failed:',e)
print(json.dumps({'originals':len(results),'acquired':sum(r['status']!='failed' for r in results),'failed':sum(r['status']=='failed' for r in results)}))
