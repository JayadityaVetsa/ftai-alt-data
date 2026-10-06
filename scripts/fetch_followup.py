"""Follow discovered official links and two indexed archive captures; no login/outreach."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import json,urllib.request,hashlib,re,time
ROOT=Path(__file__).resolve().parents[1];RAW=ROOT/'data/raw'
cdx=json.loads((RAW/'wayback_ceros.json').read_text())
captures=[cdx[1],cdx[-1]] if len(cdx)>1 else []
rows=[
 ('module_store','FTAI Module Store registration destination','https://ftaiaviation.force.com/modulestore/s/login/SelfRegister','html'),
 ('oracle_site_update','Oracle five-site progress update','https://blogs.oracle.com/ceo/from-the-q4-earnings-call','html'),
 ('vantage_frontier','Vantage Frontier campus announcement','https://vantage-dc.com/news/vantage-data-centers-unveils-plans-for-frontier-a-25b-mega-campus-in-texas-to-meet-unprecedented-ai-demand/','html'),
 ('meta_generation','Entergy Meta-serving generation construction','https://www.entergy.com/news/entergy-louisiana-breaks-ground-on-new-state-of-the-art-generation-facilities-to-power-reliability-growth-and-innovation','html'),
 ('safran_fy25','Safran FY2025 and updated ambitions','https://www.safran-group.com/pressroom/safran-reports-excellent-financial-performance-2025-and-raises-its-2028-ambitions-2026-02-13','html'),
 ('ftai_q2','FTAI Q2 2026 supplement','https://ir.ftaiaviation.com/static-files/a8601ed2-7367-4a33-898f-5163eb8b212d','pdf'),
 ('voltagrid_oracle','VoltaGrid Oracle 2300 MW agreement','https://www.globenewswire.com/news-release/2025/10/15/3167053/0/en/voltagrid-collaborates-with-oracle-to-power-next-gen-ai-data-centers.html','html'),
]+[(f'archive_{r[1]}',f'Archived Ceros page {r[1]}',f'https://web.archive.org/web/{r[1]}id_/{r[2]}','html') for r in captures]
def fetch(row):
 id,title,url,ext=row;p=RAW/f'{id}.{ext}';r=dict(id=id,title=title,url=url,accessed='2026-10-05',status='unavailable',published=None)
 try:
  if not p.exists():
   start=time.monotonic();chunks=[]
   with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0'}),timeout=15) as response:
    r['resolvedUrl']=response.url
    while True:
     b=response.read(64*1024)
     if not b:break
     chunks.append(b)
     if time.monotonic()-start>60:raise TimeoutError('60-second acquisition deadline')
   body=b''.join(chunks)
   if ext=='pdf':
    from pypdf import PdfReader
    import io
    PdfReader(io.BytesIO(body))
   p.write_bytes(body)
  body=p.read_bytes();r.update(status='downloaded',bytes=len(body),sha256=hashlib.sha256(body).hexdigest(),file=str(p.relative_to(ROOT)).replace('\\','/'))
  if ext=='pdf':
   from pypdf import PdfReader
   (ROOT/f'data/extracted/{id}.txt').write_text('\n'.join(f'\n--- PAGE {i+1} ---\n{pg.extract_text()}' for i,pg in enumerate(PdfReader(p).pages)),encoding='utf-8')
  if id.startswith('archive_'):
   matches=re.findall(r'lastPublishedDate[^,]+',body.decode('utf-8',errors='replace'));r['embeddedPublication']=matches;print('ARCHIVE',id,matches,flush=True)
 except Exception as e:r['error']=str(e)[:200]
 print(id,r['status'],r.get('bytes',r.get('error')),flush=True);return r
with ThreadPoolExecutor(max_workers=6) as pool:out=list(pool.map(fetch,rows))
(ROOT/'data/followup_manifest.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
