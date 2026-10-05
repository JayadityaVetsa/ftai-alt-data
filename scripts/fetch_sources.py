"""Download public primary sources to ignored raw storage, recording hashes and failures.
Run with --refresh to replace cached responses. No authenticated or paid endpoints.
"""
import argparse, concurrent.futures, hashlib, json, re, urllib.request, urllib.parse
from pathlib import Path
from datetime import datetime, timezone
ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / 'data/raw'
RAW.mkdir(parents=True, exist_ok=True)
SOURCES = [
 ('ftai_q2','FTAI Q2 2026 earnings supplement','https://ir.ftaiaviation.com/static-files/a8601ed2-7367-4a33-898f-5163eb8b212d','2026-07-29','pdf'),
 ('ftai_10q','FTAI Q2 2026 Form 10-Q','https://ir.ftaiaviation.com/static-files/bcc4dc23-f669-4f90-b681-db8e6365e93e','2026-07-31','pdf'),
 ('jereh_contract','Jereh contract announcement 2026-048','https://static.cninfo.com.cn/finalpage/2026-07-23/1225436739.PDF','2026-07-23','pdf'),
 ('jereh_update','Jereh public investor relations record 20260904','https://static.cninfo.com.cn/finalpage/2026-09-05/1225550221.PDF','2026-09-05','pdf'),
 ('ftai_contract','FTAI J&F contract announcement','https://ftandi.gcs-web.com/news-releases/news-release-details/ftai-announces-1465-billion-gas-turbine-generator-set-order','2026-07-22','html'),
 ('tceq_index','TCEQ pending Title V applications','https://www.tceq.texas.gov/assets/public/permitting/air/reports/applications/titlev-pending-permits.html',None,'html'),
 ('longhorn','TCEQ Longhorn technical application','https://www.tceq.texas.gov/assets/public/permitting/air/reports/applications/37589-tc.pdf',None,'pdf'),
 ('tceq_38510','TCEQ technical application 38510','https://www.tceq.texas.gov/assets/public/permitting/air/reports/applications/38510-tc.pdf',None,'pdf'),
 ('ge_specs','GE Vernova LM2500 product specifications','https://www.gevernova.com/gas-power/products/gas-turbines/lm2500.',None,'html'),
 ('crusoe_ge','Crusoe / GE 29-unit aeroderivative order','https://www.crusoe.ai/resources/newsroom/ge-vernova-and-crusoe-announce-major-29-unit-gas-turbine-deal','2025-07-22','html'),
 ('cloudburst','Energy Transfer / CloudBurst gas supply agreement','https://ir.energytransfer.com/news-releases/news-release-details/energy-transfer-and-cloudburst-sign-agreement-natural-gas-supply/','2025-02-10','html'),
 ('ercot','ERCOT public reports and large-load updates','https://www.ercot.com/news/presentations',None,'html'),
 ('eia860m','EIA monthly generator inventory','https://www.eia.gov/electricity/data/eia860m/',None,'html'),
 ('faa','FAA releasable aircraft registry documentation','https://www.faa.gov/licenses_certificates/aircraft_certification/aircraft_registry/releasable_aircraft_download',None,'html'),
 ('faa_zip','FAA current releasable aircraft registry','https://registry.faa.gov/database/ReleasableAircraft.zip',None,'zip'),
]
parser=argparse.ArgumentParser(); parser.add_argument('--refresh',action='store_true'); args=parser.parse_args()
def fetch(row):
 id,title,url,published,ext=row; path=RAW/f'{id}.{ext}'
 entry=dict(id=id,title=title,url=url,published=published,accessed='2026-10-04',file=str(path.relative_to(ROOT)).replace('\\','/'),status='unavailable')
 try:
  if not path.exists() or args.refresh:
   req=urllib.request.Request(url,headers={'User-Agent':'FTAI-Academic-Public-Research/1.0'})
   with urllib.request.urlopen(req,timeout=45) as response: body=response.read()
   if ext=='pdf' and not body.startswith(b'%PDF'): raise ValueError('Response is not a PDF')
   if ext=='zip' and not body.startswith(b'PK'): raise ValueError('Response is not a ZIP')
   path.write_bytes(body)
  body=path.read_bytes()
  entry.update(status='downloaded',bytes=len(body),sha256=hashlib.sha256(body).hexdigest(),retrieved_utc=datetime.now(timezone.utc).isoformat())
 except Exception as e: entry['error']=str(e)[:250]
 print(id,entry['status'],entry.get('bytes',entry.get('error')),flush=True)
 return entry
with concurrent.futures.ThreadPoolExecutor(max_workers=5) as pool: results=list(pool.map(fetch,SOURCES))
# Discover actual download URLs from source pages rather than guessing monthly filenames.
eia=RAW/'eia860m.html'
if eia.exists():
 html=eia.read_text(encoding='utf-8',errors='replace')
 links=re.findall(r'href=[\"\']([^\"\']+\.(?:xlsx|xls))[\"\']',html,re.I)
 for month in ['august_generator2026','december_generator2025','december_generator2024']:
  candidates=[x for x in links if month in x.lower()]
  if candidates: results.append(fetch((f'eia_{month}',f'EIA-860M {month}',urllib.parse.urljoin(SOURCES[12][2],candidates[0]),None,'xlsx')))
out=ROOT/'data/source_manifest.json'; out.parent.mkdir(exist_ok=True)
out.write_text(json.dumps(results,ensure_ascii=False,indent=2),encoding='utf-8')
# Extract text locally for page-specific review. PDFs are linked rather than redistributed.
from pypdf import PdfReader
extdir=ROOT/'data/extracted'; extdir.mkdir(exist_ok=True)
for entry in results:
 if entry['status']=='downloaded' and entry['file'].endswith('.pdf'):
  try:
   reader=PdfReader(ROOT/entry['file'])
   text='\n'.join(f'\n--- PAGE {i+1} ---\n{page.extract_text()}' for i,page in enumerate(reader.pages))
   (extdir/f"{entry['id']}.txt").write_text(text,encoding='utf-8')
  except Exception as e: print('Extraction failure',entry['id'],str(e)[:100])
