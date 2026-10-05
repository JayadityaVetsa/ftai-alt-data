"""Rebuild published data from curated evidence and downloaded FAA/EIA snapshots.
No fabricated records, fleet ages, generator changes or missing-value substitutions.
"""
import csv, io, json, re, zipfile, shutil
from pathlib import Path
from datetime import date
import pandas as pd
ROOT=Path(__file__).resolve().parents[1]; PUB=ROOT/'public/data'; PUB.mkdir(parents=True,exist_ok=True)
data=json.loads((ROOT/'data/curated.json').read_text(encoding='utf-8'))
def csv_out(name,rows):
 if not rows: return
 cols=list(dict.fromkeys(k for r in rows for k in r))
 with (PUB/f'{name}.csv').open('w',encoding='utf-8',newline='') as f:
  w=csv.DictWriter(f,fieldnames=cols);w.writeheader();w.writerows(rows)
sources={}
for filename in ['source_manifest.json','extra_manifest.json']:
 p=ROOT/'data'/filename
 if p.exists():
  for r in json.loads(p.read_text(encoding='utf-8')): sources[r['id']]=r
# Browser-verified evidence remains available if a bulk HTTP download fails.
for id,url,title in [
 ('ftai_q2','https://ir.ftaiaviation.com/static-files/a8601ed2-7367-4a33-898f-5163eb8b212d','FTAI Q2 2026 supplement'),
 ('ftai_10q','https://www.sec.gov/Archives/edgar/data/1590364/000162828026051412/ftai-20260630.htm','FTAI Q2 2026 SEC filing'),
 ('cloudburst','https://ir.energytransfer.com/news-releases/news-release-details/energy-transfer-and-cloudburst-sign-agreement-natural-gas-supply/','Energy Transfer CloudBurst announcement'),
 ('longhorn','https://www.tceq.texas.gov/assets/public/permitting/air/reports/applications/37589-tc.pdf','Longhorn technical application'),
 ('comptroller','https://comptroller.texas.gov/taxes/data-centers/data-center-lists.php','Texas qualifying data-center register'),
 ('childress','https://www.tceq.texas.gov/assets/public/permitting/air/reports/applications/40835-ac.pdf','Childress operating-permit application'),
 ('sharka','https://www.tceq.texas.gov/assets/public/permitting/air/reports/applications/39571-ac.pdf','Sharka operating-permit application'),
 ('cyrusone','https://www.tceq.texas.gov/assets/public/permitting/air/reports/applications/40584-ac.pdf','CyrusOne grouped-campus application'),
 ('vantage11','https://www.tceq.texas.gov/assets/public/permitting/air/reports/applications/38602-tc.pdf','Vantage TX11 technical application'),
 ('vantage21','https://www.tceq.texas.gov/assets/public/permitting/air/reports/applications/38600-tc.pdf','Vantage TX21 technical application')]:
  sources.setdefault(id,dict(id=id,url=url,title=title,published=None,accessed=data['asOf'],status='browser evidence',file=None))
  sources[id]['evidence']='Browser-reviewed numeric disclosure or listing; detailed review limits are recorded in each project.'
data['sources']=list(sources.values())
data['fleet']={'status':'Unavailable','rows':[],'age':[],'count':None,'missingYear':None,'missingEngine':None,'note':'FAA registry acquisition incomplete. No fleet chart is manufactured.'}
faa=ROOT/'data/raw/faa_zip.zip'
if faa.exists():
 try:
  with zipfile.ZipFile(faa) as z:
   def read(name):
    d=pd.read_csv(z.open(name),dtype=str,encoding='utf-8-sig',encoding_errors='replace',keep_default_na=False);d.columns=d.columns.str.strip();return d.apply(lambda s:s.str.strip())
   master=read('MASTER.txt'); eng=read('ENGINE.txt'); aircraft=read('ACFTREF.txt')
   assert eng['CODE'].is_unique and aircraft['CODE'].is_unique
   joined=master.merge(eng[['CODE','MFR','MODEL']],left_on='ENG MFR MDL',right_on='CODE',how='left',validate='many_to_one',suffixes=('','_engine'))
   # Names in ENGINE establish type evidence in the registry, not individual engine serials.
   exact=joined[joined['MODEL'].fillna('').str.contains('CFM56',case=False,regex=False)].copy()
   years=pd.to_numeric(exact['YEAR MFR'],errors='coerce'); ages=2026-years
   valid=ages[(ages>=0)&(ages<=100)]
   bins=[0,10,15,20,25,30,100]; labels=['0–9','10–14','15–19','20–24','25–29','30+']
   bucket=pd.cut(valid,bins=bins,right=False,labels=labels).value_counts(sort=False)
   age=[{'bucket':str(k),'count':int(v)} for k,v in bucket.items()]
   rows=exact[['N-NUMBER','MFR','MODEL','YEAR MFR','STATUS CODE']].rename(columns={'N-NUMBER':'registration','MFR':'engineManufacturer','MODEL':'engineModel','YEAR MFR':'aircraftYear','STATUS CODE':'registrationStatus'}).to_dict('records')
   data['fleet']=dict(status='Downloaded registry analysis',rows=rows,age=age,count=len(rows),missingYear=int(len(exact)-len(valid)),missingEngine=int(joined['MODEL'].isna().sum()),note='US registered-aircraft snapshot; includes all registry status codes, not a verified active fleet. Aircraft age is not engine age. Engine-type codes do not prove serial-level feedstock eligibility. Owner PII omitted.')
   csv_out('faa_cfm56_records',rows);csv_out('fleet_age',age)
 except Exception as e: data['fleet']['note']=f'FAA parsing failed: {e}. No inferred counts published.'
data['eia']={'status':'Unavailable','rows':[],'changes':[],'note':'Monthly generator snapshots not acquired or parsed. This inventory is not a load-interconnection dataset.'}
raw=ROOT/'data/raw'; files=list(raw.glob('eia_*generator*.xlsx')); generators=[]
for file in files:
 try:
  book=pd.ExcelFile(file)
  for sheet in book.sheet_names:
   if not any(k in sheet.lower() for k in ['operat','planned','retired','canceled']):continue
   rawsheet=book.parse(sheet,header=None); first=rawsheet.head(10)
   header=next((i for i,row in first.iterrows() if any(str(x).strip()=='Plant ID' for x in row)),None)
   if header is None:continue
   df=rawsheet.iloc[header+1:].copy();df.columns=rawsheet.iloc[header].tolist();df.columns=[re.sub(r'\s+',' ',str(x)).strip() for x in df.columns]
   state=next((x for x in df.columns if x in ['State','Plant State']),None);fuel=next((x for x in df.columns if x in ['Energy Source Code','Energy Source 1']),None)
   if not state or not fuel:continue
   df=df[(df[state]=='TX')&(df[fuel]=='NG')]
   for _,r in df.iterrows():
    def value(*keys):
     for k in keys:
      if k in r and pd.notna(r[k]):return r[k].item() if hasattr(r[k],'item') else r[k]
     return None
    match=re.search(r'(august|december)_generator(\d{4})',file.stem)
    snapshot=f"{match[2]}-{'08' if match[1]=='august' else '12'}" if match else file.stem
    generators.append(dict(snapshot=snapshot,plantId=value('Plant ID'),generatorId=str(value('Generator ID')),name=value('Plant Name'),mw=value('Nameplate Capacity (MW)'),primeMover=value('Prime Mover Code','Prime Mover'),status=value('Status'),sheet=sheet))
 except Exception as e: print('EIA parse failed',file.name,str(e))
if generators:
 data['eia']=dict(status='Downloaded inventory analysis',rows=generators,changes=[],note='Texas natural-gas generator inventory; includes utility generation and does not establish data-center or FTAI exposure.')
 snaps=sorted(set(r['snapshot'] for r in generators))
 if len(snaps)>1:
  before={(r['plantId'],r['generatorId']):r for r in generators if r['snapshot']==snaps[0]};after={(r['plantId'],r['generatorId']):r for r in generators if r['snapshot']==snaps[-1]}
  for key,a in after.items():
   b=before.get(key)
   if b and (a['status']!=b['status'] or a['sheet']!=b['sheet']):data['eia']['changes'].append(dict(plantId=key[0],generatorId=key[1],name=a['name'],mw=a['mw'],before=b['status'],after=a['status'],beforeSheet=b['sheet'],afterSheet=a['sheet']))
 csv_out('eia_tx_gas_generators',generators);csv_out('eia_status_changes',data['eia']['changes'])
# Public outputs carry no raw PDFs or person names/addresses.
for key in ['projects','facts','sources','translations','catalysts']:csv_out(key,data[key])
csv_out('data_dictionary',[{'dataset':'projects','field':'mw','meaning':'Documented electrical capacity, not captured demand. Blank means unknown.'},{'dataset':'projects','field':'eligible','meaning':'Verified primary gas need with uncommitted compatible equipment and execution evidence. None currently verified.'},{'dataset':'projects','field':'date','meaning':'Application received, tax effective or announcement date depending on status; never automatically a commissioning date.'},{'dataset':'fleet','field':'aircraftYear','meaning':'Aircraft manufacture year. Does not establish engine age, retirement or availability.'},{'dataset':'sources','field':'status','meaning':'Bulk acquisition status. Browser evidence may exist despite a download failure.'}])
eligible=[p for p in data['projects'] if p['eligible'] and p['mw'] is not None]
data['coverage']=dict(candidates=len(data['projects']),knownCapacity=sum(p['mw'] is not None for p in data['projects']),eligibleSites=len(eligible),eligibleMw=sum(p['mw'] for p in eligible),explicitFtaiSites=0,note='Purposive 15-record screen, not a census or statistical sample. Zero verified eligible MW means evidence is insufficient, not zero market demand.')
(PUB/'research.json').write_text(json.dumps(data,ensure_ascii=False,indent=2,allow_nan=False),encoding='utf-8')
print('Published',data['coverage'],'FAA:',data['fleet']['status'],'EIA:',data['eia']['status'])
