"""Cache public originals where accessible; retain access failures separately from review."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import urllib.request,json,hashlib,time
R=Path(__file__).resolve().parents[1];raw=R/'data/raw';raw.mkdir(exist_ok=True)
d=json.loads((R/'data/workspace_curated.json').read_text(encoding='utf-8'))
def fetch(s):
 ext='pdf' if '.pdf' in s['url'].lower() else 'html';p=raw/f"workspace_{s['id']}.{ext}"
 row=dict(id=s['id'],url=s['url'],accessed=d['asOf'],file=str(p.relative_to(R)).replace('\\','/'),status='unavailable')
 try:
  if not p.exists():
   started=time.monotonic();chunks=[]
   with urllib.request.urlopen(urllib.request.Request(s['url'],headers={'User-Agent':'Mozilla/5.0'}),timeout=10) as response:
    while True:
     chunk=response.read(65536)
     if not chunk:break
     chunks.append(chunk)
     if time.monotonic()-started>30:raise TimeoutError('Source exceeded 30-second acquisition budget')
   p.write_bytes(b''.join(chunks))
  body=p.read_bytes();row.update(status='downloaded',bytes=len(body),sha256=hashlib.sha256(body).hexdigest())
 except Exception as e:row['error']=str(e)
 return row
with ThreadPoolExecutor(max_workers=4) as pool:rows=list(pool.map(fetch,d['sources']))
(R/'data/workspace_manifest.json').write_text(json.dumps(rows,indent=2),encoding='utf-8')
print('Cached',sum(r['status']=='downloaded' for r in rows),'of',len(rows),'public sources; failures recorded')
