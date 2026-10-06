"""Download the user-supplied public Google Sheet; never request login or credentials."""
from pathlib import Path
import urllib.request,json,hashlib,csv,io
ROOT=Path(__file__).resolve().parents[1];RAW=ROOT/'data/raw'
ID='17v30PxGEzR5UNq8yL1Gxf-IGMwjgZEvrmreZQnM9N_U';GID='1561108781'
manifest=[]
for id,url,ext in [
 ('inventory_sheet',f'https://docs.google.com/spreadsheets/d/{ID}/export?format=csv&gid={GID}','csv'),
 ('inventory_sheet_html',f'https://docs.google.com/spreadsheets/d/{ID}/htmlview?gid={GID}','html'),
 ('inventory_sheet_xlsx',f'https://docs.google.com/spreadsheets/d/{ID}/export?format=xlsx','xlsx')
]:
 p=RAW/f'{id}.{ext}';r=dict(id=id,title='User-supplied FTAI inventory Google Sheet',url=url,accessed='2026-10-05',status='unavailable',published=None)
 try:
  with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0'}),timeout=25) as response:
   body=response.read();r['resolvedUrl']=response.url
  if ext=='csv':
   text=body.decode('utf-8-sig');rows=list(csv.reader(io.StringIO(text)))
   if '<html' in text[:200].lower():raise ValueError('HTML returned instead of public CSV')
   print('CSV row count',len(rows),'first 12 rows:',json.dumps(rows[:12],ensure_ascii=False),flush=True)
  p.write_bytes(body);r.update(status='downloaded',bytes=len(body),sha256=hashlib.sha256(body).hexdigest())
 except Exception as e:r['error']=str(e)[:200]
 manifest.append(r);print(id,r['status'],r.get('bytes',r.get('error')),flush=True)
(ROOT/'data/sheet_manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
