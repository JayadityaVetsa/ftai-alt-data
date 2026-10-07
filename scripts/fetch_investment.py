"""Manual free-source refresh. Preserve originals locally and log failed acquisitions."""
from pathlib import Path
import json,hashlib,urllib.request
from datetime import datetime,timezone
from pypdf import PdfReader
R=Path(__file__).resolve().parents[1]
d=json.loads((R/'data/investment_curated.json').read_text(encoding='utf-8'))
raw=R/'data/raw';ex=R/'data/extracted';raw.mkdir(exist_ok=True);ex.mkdir(exist_ok=True)
rows=[]
for s in d['sources']:
 f=raw/s['file'];row={**s,'accessed':datetime.now(timezone.utc).isoformat()}
 try:
  if not f.exists():
   req=urllib.request.Request(s['url'],headers={'User-Agent':'FTAI public-source research team contact via github.com/JayadityaVetsa/ftai-alt-data'})
   with urllib.request.urlopen(req,timeout=25) as res:b=res.read()
   if s['file'].endswith('.pdf') and not b.startswith(b'%PDF'):raise ValueError('Not a PDF response')
   f.write_bytes(b)
  b=f.read_bytes();row.update(status='Local original retained',bytes=len(b),sha256=hashlib.sha256(b).hexdigest(),file=str(f.relative_to(R)))
  if f.suffix=='.pdf':
   reader=PdfReader(f);row['pages']=len(reader.pages)
   (ex/(f.stem+'.txt')).write_text('\n'.join(f'--- PAGE {i+1} ---\n{p.extract_text()}' for i,p in enumerate(reader.pages)),encoding='utf-8')
 except Exception as e:row.update(status='Acquisition failed; browser review retained',error=str(e))
 rows.append(row)
(R/'data/investment_acquisition.json').write_text(json.dumps(rows,indent=2,ensure_ascii=False),encoding='utf-8')
print([(r['id'],r['status']) for r in rows])
