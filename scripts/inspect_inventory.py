from pathlib import Path
from html.parser import HTMLParser
import json,re,urllib.request,hashlib
ROOT=Path(__file__).resolve().parents[1];RAW=ROOT/'data/raw'
html=(RAW/'ceros_inventory.html').read_text(encoding='utf-8')
class Links(HTMLParser):
 def handle_starttag(self,t,a):
  for k,v in a:
   if k in ['href','src'] and v and not any(x in v for x in ['ceros.com/','media-s3','googletag','google.com','fonts.']):print('LINK',v)
Links().feed(html)
match=re.search(r'committedJsonUrl":("[^"]+")',html)
url=json.loads(match[1]).replace('http:','https:')
manifest=[]
for id,title,target,ext in [
 ('ceros_payload','Public Ceros experience payload',url,'js'),
 ('wayback_ceros','Wayback CDX inventory history','https://web.archive.org/cdx/search/cdx?url=view.ceros.com%2Ffortress-investment%2Fcfm56material%2Fp%2F1&output=json&filter=statuscode%3A200&collapse=timestamp%3A6&limit=12','json'),
 ('ftai_q2_release','FTAI Q2 2026 results','https://ftandi.gcs-web.com/news-releases/news-release-details/ftai-aviation-ltd-reports-second-quarter-2026-results-increases','html'),
 ('dominion_apollo1','Dominion Twin Creeks to Apollo volume 1','https://www2.dominionenergy.com/-/media/pdfs/global/projects-and-facilities/electric-projects/power-line-projects/nova/twin-creeks-to-apollo/application-volume-1-of-3-2024.pdf?hash=648A8EC17A44CFF5D2DCD6E59C6F4908&rev=0bf55ec94cea4523b115632387166e87','pdf'),
]:
 p=RAW/f'{id}.{ext}';r=dict(id=id,title=title,url=target,accessed='2026-10-05',status='unavailable',published=None)
 try:
  if not p.exists():
   with urllib.request.urlopen(urllib.request.Request(target,headers={'User-Agent':'Mozilla/5.0'}),timeout=20) as response:body=response.read()
   p.write_bytes(body)
  body=p.read_bytes();r.update(status='downloaded',sha256=hashlib.sha256(body).hexdigest(),bytes=len(body),file=str(p.relative_to(ROOT)).replace('\\','/'))
  if ext=='js':
   text=body.decode('utf-8');urls=sorted(set(re.findall(r'https?[^\s"\\<>]+',text)))
   print('PAYLOAD URLS',json.dumps([u for u in urls if not any(x in u for x in ['media.ceros','media-s3','fonts','ceros.com/'])]),flush=True)
   for m in re.finditer(r'module|inventory|iframe|\.csv|\.xlsx|\.pdf',text,re.I):
    if any(x in text[max(0,m.start()-80):m.end()+100].lower() for x in ['url','href','src','iframe']):print(text[max(0,m.start()-100):m.end()+180],flush=True)
  if ext=='pdf':
   from pypdf import PdfReader
   (ROOT/f'data/extracted/{id}.txt').write_text('\n'.join(f'\n--- PAGE {i+1} ---\n{pg.extract_text()}' for i,pg in enumerate(PdfReader(p).pages)),encoding='utf-8')
 except Exception as e:r['error']=str(e)[:200]
 manifest.append(r);print(id,r['status'],r.get('error',''),flush=True)
(ROOT/'data/inventory_manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
