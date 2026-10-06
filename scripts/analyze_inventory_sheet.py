"""Normalize the supplied compilation and preserve its overlap/exclusion policy."""
from pathlib import Path
import csv,json,re,collections,hashlib
ROOT=Path(__file__).resolve().parents[1];PUB=ROOT/'public/data';RAW=ROOT/'data/raw'
sheet=list(csv.reader((RAW/'inventory_sheet.csv').open(encoding='utf-8-sig',newline='')))
header=next(i for i,row in enumerate(sheet) if 'Quantity for totals' in row and 'Part number (text)' in row)
def number(value):
 if not value.strip():return None
 value=value.replace(',','').strip()
 if not re.fullmatch(r'\d+(?:\.\d+)?',value):raise ValueError(f'Unexpected numeric value {value!r}')
 return int(float(value)) if float(value).is_integer() else float(value)
rows=[]
for sheetrow,values in enumerate(sheet[header+1:],start=header+2):
 row=dict(zip(sheet[header],values))
 if not row.get('Engine result'):continue
 rows.append(dict(id=f'sheet-row-{sheetrow}',sheetRow=sheetrow,family=row['Engine result'],category=row['Part category'],area=row['Module area'],description=row['Part description'],partNumber=row['Part number (text)'],condition=row['Condition'],sourceQuantity=number(row['Source quantity (do not sum)']),engineSerial=row['ESN (text)'] or None,cyclesRemaining=number(row['Cycles remaining']),sourceTable=row['Source table'],sourceRow=row['Source row'],note=row['Data note'],sourceImage=row['Source image URL'],includedQuantity=number(row['Quantity for totals']),treatment=row['Counting treatment'],stockDate=None,observed='2026-10-05',powerEligibility='Unknown; individual parts are not complete cores'))
assert len({r['id'] for r in rows})==len(rows)
control=number(sheet[header-1][13]);total=sum(r['includedQuantity'] for r in rows if r['includedQuantity'] is not None)
if total!=control:raise ValueError(f'Supplied sheet control {control} does not reconcile to {total}')
groups=[]
for area in sorted({r['area'] for r in rows}):
 rr=[r for r in rows if r['area']==area]
 groups.append(dict(area=area,rows=len(rr),includedRows=sum(r['includedQuantity'] is not None for r in rr),includedQuantity=sum(r['includedQuantity'] for r in rr if r['includedQuantity'] is not None),notCountedSourceQuantity=sum(r['sourceQuantity'] or 0 for r in rr if r['includedQuantity'] is None),uniquePartNumbers=len({r['partNumber'] for r in rr if r['partNumber']})))
keyed=collections.defaultdict(list)
for r in rows:keyed[(r['partNumber'],r['condition'],r['engineSerial'])].append(r)
duplicates=[dict(partNumber=k[0],condition=k[1],engineSerial=k[2],sheetRows=[r['sheetRow'] for r in rr],treatments=[r['treatment'] for r in rr]) for k,rr in keyed.items() if len(rr)>1]
summary=dict(rowCount=len(rows),includedRows=sum(r['includedQuantity'] is not None for r in rows),includedQuantity=total,sourceQuantity=sum(r['sourceQuantity'] or 0 for r in rows),notCountedSourceQuantity=sum(r['sourceQuantity'] or 0 for r in rows if r['includedQuantity'] is None),uniquePartNumbers=len({r['partNumber'] for r in rows if r['partNumber']}),donorEngineSerials=len({r['engineSerial'] for r in rows if r['engineSerial']}),sourceImageCount=len({r['sourceImage'] for r in rows}),excludedRows=sum(r['treatment']=='Overlap excluded' for r in rows),unresolvedIdentifierRows=sum(r['treatment']=='Identifier unresolved' for r in rows),duplicates=duplicates,completeEngineRows=0,completeModuleRows=0,stockDate=None,captureDate='2026-10-05',note='User-supplied compilation of displayed stock images. Column N controls included quantity; 14 possible-overlap rows and 2 unresolved identifier rows are not counted. Stock dates, ownership and Power qualification are not established. An ESN attached to LLPs identifies provenance, not a complete available engine. Original images not independently visually reconciled in this release.')
review=json.loads((ROOT/'data/inventory_review.json').read_text(encoding='utf-8'))
review_matches=review['sha256']==hashlib.sha256((RAW/'inventory_sheet.csv').read_bytes()).hexdigest()
summary['note']=summary['note'].replace('Original images not independently visually reconciled in this release.', 'Two of 12 source images spot-checked: 5B LPT material and Core LLPs; full transcription reconciliation outstanding.' if review_matches else 'Compilation changed: previous visual review stale; repeat image checks.')

def out(name,rr):
 keys=list(dict.fromkeys(k for r in rr for k in r))
 with (PUB/f'{name}.csv').open('w',encoding='utf-8',newline='') as f:
  w=csv.DictWriter(f,fieldnames=keys);w.writeheader()
  for r in rr:w.writerow({k:json.dumps(v,ensure_ascii=False) if isinstance(v,(list,dict)) else v for k,v in r.items()})
out('inventory_parts',rows);out('inventory_by_area',groups);out('inventory_summary',[summary]);out('inventory_duplicate_audit',duplicates)
d=json.loads((PUB/'expansion.json').read_text(encoding='utf-8'))
d['inventory'].update(status='Public part-level compilation acquired',parts=rows,byArea=groups,summary=summary,sheetUrl='https://docs.google.com/spreadsheets/d/17v30PxGEzR5UNq8yL1Gxf-IGMwjgZEvrmreZQnM9N_U/edit?gid=1561108781',note=summary['note'])
d['inventory']['sourceImageChecks']=review['checks'] if review_matches else []
manifest=json.loads((ROOT/'data/sheet_manifest.json').read_text(encoding='utf-8'))
s={**manifest[0],'url':d['inventory']['sheetUrl'],'locator':'gid 1561108781, header row 4; quantities in N; control N3','published':None,'review':summary['note'],'browserReviewed':False}
d['sources']=[r for r in d['sources'] if r['id']!='inventory_sheet']+[s]
(PUB/'expansion.json').write_text(json.dumps(d,ensure_ascii=False,indent=2,allow_nan=False),encoding='utf-8');out('expansion_sources',d['sources'])
main=json.loads((PUB/'research.json').read_text(encoding='utf-8'));main['sources']=[r for r in main['sources'] if r['id']!='inventory_sheet']+[s];(PUB/'research.json').write_text(json.dumps(main,ensure_ascii=False,indent=2,allow_nan=False),encoding='utf-8');out('sources',main['sources'])
print(json.dumps(summary,ensure_ascii=False));print('BY AREA',json.dumps(groups,ensure_ascii=False))
