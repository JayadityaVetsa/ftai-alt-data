"""Acquire reviewed public-source URLs for the second research release."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import json,urllib.request,hashlib,time,sys
ROOT=Path(__file__).resolve().parents[1];RAW=ROOT/'data/raw';RAW.mkdir(exist_ok=True)
SOURCES=[
 ('ceros_inventory','FTAI / AAR CFM56 material experience','https://view.ceros.com/fortress-investment/cfm56material/p/1','html'),
 ('ftai_inventory_link','User-linked FTAI page','https://www.ftaiaviation.com/p/4','html'),
 ('safran_h1_2026','Safran H1 2026 results','https://www.safran-group.com/pressroom/safran-reports-its-first-half-2026-results-2026-07-28','html'),
 ('safran_outlook','Safran FY2025 / 2028 investor update','https://www.safran-group.com/download/media/450393','pdf'),
 ('dominion_gs5','Dominion large-load rate-class report','https://sustainability.dominionenergy.com/GS-5%20Large%20Load%20Rate%20Class%20Report.pdf','pdf'),
 ('dominion_apollo','Dominion Twin Creeks to Apollo application volume 3','https://www.dominionenergy.com/-/media/content/about/power-line-projects/nova/pdfs/application-documents/application-volume-3-of-3-2024.pdf','pdf'),
 ('crusoe_microsoft','Crusoe Microsoft Abilene 900 MW campus','https://www.crusoe.ai/resources/newsroom/crusoe-announces-new-900-mw-ai-factory-campus-in-abilene-texas-to-support-microsoft-ai-infrastructure','html'),
 ('crusoe_bergen','Crusoe Bergen 750 MW procurement','https://www.crusoe.ai/resources/newsroom/bergen-engines-signs-approx-750mw-u-s-power-agreement-with-crusoe-for-ai-data-centers','html'),
 ('crusoe_abilene','Crusoe original Abilene 1.2 GW campus','https://www.crusoe.ai/resources/newsroom/crusoe-expands-ai-data-center-campus-in-abilene-to-1-2-gigawatts','html'),
 ('oracle_jupiter','Oracle revised Project Jupiter power plan','https://www.oracle.com/news/announcement/public-review-opens-for-updated-project-jupiter-power-plan-2026-06-03/','html'),
 ('oracle_jupiter_rfp','Oracle New Mexico renewable RFP','https://www.oracle.com/news/announcement/oracle-issues-rfp-for-2gw-of-renewable-energy-2026-09-08/','html'),
 ('pjm_2026','PJM updated 2026 load outlook','https://insidelines.pjm.com/pjms-updated-20-year-forecast-continues-to-see-significant-long-term-load-growth/','html'),
]
def fetch(row):
 id,title,url,ext=row;p=RAW/f'{id}.{ext}';r=dict(id=id,title=title,url=url,accessed='2026-10-05',published=None,status='unavailable',file=str(p.relative_to(ROOT)).replace('\\','/'))
 try:
  if not p.exists():
   start=time.monotonic();chunks=[]
   with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0'}),timeout=15) as response:
    while True:
     chunk=response.read(64*1024)
     if not chunk:break
     chunks.append(chunk)
     if time.monotonic()-start>75:raise TimeoutError('Acquisition exceeded 75-second budget')
   body=b''.join(chunks)
   if ext=='pdf':
    from pypdf import PdfReader
    import io
    PdfReader(io.BytesIO(body))
   p.write_bytes(body)
  body=p.read_bytes();r.update(status='downloaded',bytes=len(body),sha256=hashlib.sha256(body).hexdigest())
  if ext=='pdf':
   from pypdf import PdfReader
   out=ROOT/'data/extracted';out.mkdir(exist_ok=True)
   (out/f'{id}.txt').write_text('\n'.join(f'\n--- PAGE {i+1} ---\n{pg.extract_text()}' for i,pg in enumerate(PdfReader(p).pages)),encoding='utf-8')
 except Exception as e:r.update(status='unavailable',error=str(e)[:200])
 print(id,r['status'],r.get('bytes',r.get('error')),flush=True);return r
with ThreadPoolExecutor(max_workers=8) as pool:rows=list(pool.map(fetch,SOURCES))
(ROOT/'data/expansion_manifest.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf-8')
