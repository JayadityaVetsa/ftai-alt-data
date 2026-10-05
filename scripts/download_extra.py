"""Fetch discovered research documents and resume a large FAA download."""
import concurrent.futures, hashlib, json, re, urllib.request, urllib.parse, time
from pathlib import Path
from pypdf import PdfReader
ROOT=Path(__file__).resolve().parents[1]; RAW=ROOT/'data/raw'; RAW.mkdir(parents=True,exist_ok=True)
rows=[('comptroller','Texas registered qualifying data-center projects','https://comptroller.texas.gov/taxes/data-centers/data-center-lists.php','html'),('childress','Childress Title V application','https://www.tceq.texas.gov/assets/public/permitting/air/reports/applications/40835-ac.pdf','pdf'),('sharka','Sharka Title V application','https://www.tceq.texas.gov/assets/public/permitting/air/reports/applications/39571-ac.pdf','pdf'),('cyrusone','CyrusOne DFW Title V application','https://www.tceq.texas.gov/assets/public/permitting/air/reports/applications/40584-ac.pdf','pdf'),('vantage11','Vantage TX11 technical application','https://www.tceq.texas.gov/assets/public/permitting/air/reports/applications/38602-tc.pdf','pdf'),('vantage21','Vantage TX21 technical application','https://www.tceq.texas.gov/assets/public/permitting/air/reports/applications/38600-tc.pdf','pdf'),('ftai_sec','FTAI Q2 2026 SEC filing','https://www.sec.gov/Archives/edgar/data/1590364/000162828026051412/ftai-20260630.htm','html'),('longhorn_record','Longhorn original NSR application','https://records.tceq.texas.gov/cs/idcplg?IdcService=TCEQ_EXTERNAL_SEARCH_GET_FILE&Rendition=Web&dID=8117448','pdf'),('longhorn','Longhorn current technical application','https://www.tceq.texas.gov/assets/public/permitting/air/reports/applications/37589-tc.pdf','pdf'),('faa_zip','FAA releasable aircraft database','https://registry.faa.gov/database/ReleasableAircraft.zip','zip')]
def run(row):
 id,title,url,ext=row; p=RAW/f'{id}.{ext}'; entry=dict(id=id,title=title,url=url,published=None,accessed='2026-10-04',file=str(p.relative_to(ROOT)).replace('\\','/'),status='unavailable')
 try:
  if not p.exists():
   part=p.with_suffix(p.suffix+'.part')
   # Stream each chunk to disk. Retry whole file if the server cannot support ranges.
   for attempt in range(2):
    try:
     headers={'User-Agent':'Mozilla/5.0'}
     offset=part.stat().st_size if part.exists() else 0
     if offset: headers['Range']=f'bytes={offset}-'
     with urllib.request.urlopen(urllib.request.Request(url,headers=headers),timeout=30) as response:
      append=offset>0 and response.status==206
      with part.open('ab' if append else 'wb') as out:
       while chunk:=response.read(256*1024): out.write(chunk)
     body=part.read_bytes()
     if ext=='pdf' and not body.startswith(b'%PDF'): raise ValueError('Not PDF')
     if ext=='zip':
      import zipfile
      with zipfile.ZipFile(part) as z: assert 'MASTER.txt' in z.namelist()
     part.replace(p); break
    except Exception:
     if attempt==1: raise
  body=p.read_bytes(); entry.update(status='downloaded',bytes=len(body),sha256=hashlib.sha256(body).hexdigest())
  if ext=='pdf':
   target=ROOT/'data/extracted'; target.mkdir(exist_ok=True)
   text='\n'.join(f'\n--- PAGE {i+1} ---\n{pg.extract_text()}' for i,pg in enumerate(PdfReader(p).pages))
   (target/f'{id}.txt').write_text(text,encoding='utf-8')
 except Exception as e: entry['error']=str(e)[:200]; entry['status']='unavailable' if not p.exists() else 'acquired; parsing failed'
 print(id,entry['status'],entry.get('bytes',entry.get('error')),flush=True); return entry
with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool: results=list(pool.map(run,rows))
(ROOT/'data/extra_manifest.json').write_text(json.dumps(results,ensure_ascii=False,indent=2),encoding='utf-8')
