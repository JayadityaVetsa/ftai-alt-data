"""Publish the reviewed audit and a deterministic slide graphic; no live refresh."""
import json,csv,shutil
from pathlib import Path
R=Path(__file__).resolve().parents[1];P=R/'public/data';G=R/'public/graphics';G.mkdir(exist_ok=True)
d=json.loads((R/'data/power_gap_audit.json').read_text(encoding='utf-8'));s=d['summary']
for file in ['power_gap_audit.json','power_gap_audit.csv','power_gap_audit_notes.json','gap_audit_acquisition.json']:shutil.copyfile(R/'data'/file,P/file)
shutil.copyfile(R/'research/power-gap-audit-2026-10-06.md',P/'power_gap_audit_memo.md')
def csvfile(name,rows):
 with (P/name).open('w',newline='',encoding='utf-8-sig') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
csvfile('power_gap_bridge.csv',[dict(stage='Electrical scope in 24 records',mw=s['electricalScopeMw'],classification='Published scope; IT conversion assumes 1.2 PUE'),dict(stage='Numeric supply and operating credits',mw=s['creditedSupplyMw'],classification='Mixed contract/allocation/minimum operating evidence; not unconditional on-time supply'),dict(stage='Conditional allocation ceiling',mw=s['conditionalAllocationCeilingMw'],classification='Unmatched numerical supply; not confirmed uncontracted demand')])
csvfile('power_gap_coverage.csv',[dict(reason=k,records=v) for k,v in d['coverage'].items()])
csvfile('power_gap_ceiling_cases.csv',[dict(id=r['id'],name=r['name'],electricalScopeMw=r['electricalScopeMwAtPue12'],creditedSupplyMw=r['creditedSupplyMw'],ceilingMw=r['contractCoverageCeilingMw'],creditType=r['creditType'],note=r['auditNote']) for r in d['rows'] if r['boundIncluded'] and r['contractCoverageCeilingMw']>0])
original=json.loads((R/'data/datacenter_study.json').read_text(encoding='utf-8'))
index={s['url']:dict(title=s['title'],published=s.get('published'),locator=s.get('locator',''),reviewed=d['asOf']) for s in original['sources']}
extra={
 'd12401d424b4.htm':('ERock IPO prospectus','2026-06-09','Business case studies, p.146; Meta/EPE bridge project'),
 'Issue_Brief_U_21990':('MPSC Saline contract issue brief','2025-12-18','pp.1–2 supply agreement; pp.4–6 approval conditions'),
 '2026/01/09/attorney-general':('Michigan AG Saline contract review','2026-01-09','Approximately 1.4GW customer load and contract challenge'),
 'iren-20251231.htm':('IREN Q2 FY26 Form 10-Q','2026-02-05','p.42 Oklahoma contractual power rights; Note12 connection rights'),
 'energization-sweetwater-1':('IREN Sweetwater 1 energization','2026-05-01','Substation energized; customer power delivery is phased'),
 'apld-20260531.htm':('Applied Digital FY2026 Form 10-K',None,'pp.5–7 campus portfolio and land/utility agreement wording'),
 'detail/145/kentucky':('Justified 482MW service agreement','2026-08-24','Retail Electric Service Agreement approved August21'),
 'detail/146/terawulf':('Muskie amended service agreement','2026-10-05','500MW first phase in2028; next500MW in2029'),
 'data-centers/river-bend':('Hut 8 River Bend project',None,'330MW utility scope supporting245MW IT'),
 'hut-8-signs-15-year':('Hut 8 River Bend lease and power arrangement',None,'Initial330MW utility capacity secured with Entergy'),
 'data-centers/beacon-point':('Hut 8 Beacon Point project',None,'1,000MW utility/interconnection approvals; two phases'),
 'milamdc.com':('SB Energy Milam project',None,'First operations target2027; capacity basis unresolved'),
 'third-quarter-2025-business':('Cipher Colchis executed connection agreement','2025-11-03','1GW executed AEP Direct Connect Agreement'),
 'acquisition-200-mw-site-ohio':('Cipher Ulysses capacity acquisition',None,'200MW secured capacity from AEP Ohio'),
 'ea028197201ex99-1.htm':('New Era March2026 business update','2026-03-17','Slides8–10;1+GW campus and200/450/350MW pathway'),
}
for r in d['rows']:
 for url in r['sourceUrls']:
  if url not in index:
   hit=next((v for k,v in extra.items() if k in url),None)
   index[url]=dict(title=hit[0] if hit else 'Additional primary source',published=hit[1] if hit else None,locator=hit[2] if hit else 'See row audit note',reviewed=d['asOf'])
(R/'data/power_gap_source_index.json').write_text(json.dumps(index,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
(P/'power_gap_source_index.json').write_text(json.dumps(index,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
csvfile('power_gap_sources.csv',[dict(url=k,**v) for k,v in index.items()])
total=s['electricalScopeMw']/1000;credit=s['creditedSupplyMw']/1000;gap=s['conditionalAllocationCeilingMw']/1000;split=1040*credit/total
svg=f'''<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="760" viewBox="0 0 1200 760" role="img" aria-labelledby="title desc">
<title id="title">50-record FTAI Power audit: conditional 0 to {gap:.1f} GW coverage range</title><desc id="desc">24 measurable records have {total:.2f} GW electrical scope. Subtract {credit:.3f} GW credited supply and operating capacity to get {gap:.3f} GW conditional ceiling. 26 records are excluded. Actual uncontracted demand and shortage duration remain unverified.</desc>
<rect width="1200" height="760" fill="#fbfcf8"/><g font-family="Arial, sans-serif" fill="#14253d">
<text x="65" y="48" font-size="15" font-weight="700" letter-spacing="2" fill="#457764">FTAI POWER · CUSTOMER DEMAND AUDIT</text>
<text x="65" y="105" font-size="38" font-weight="700">Earlier electricity has a customer.</text>
<text x="65" y="143" font-size="18" fill="#526475">50 US records reviewed · 2027–28 screen · Evidence cutoff October 6, 2026</text>
<rect x="65" y="178" width="1070" height="104" rx="12" fill="#14253d"/>
<text x="88" y="220" fill="#cce9d2" font-size="31" font-weight="700">0–{gap:.1f} GW</text>
<text x="88" y="252" fill="white" font-size="16">Conditional contract-coverage range</text>
<text x="548" y="219" fill="white" font-size="22" font-weight="700">24 measurable records</text>
<text x="548" y="250" fill="#d4dfde" font-size="16">26 held out · Full 50-record upper bound unavailable</text>
<text x="65" y="324" font-size="20" font-weight="700">{total:.2f} GW of announced electrical scope in the measurable subset</text>
<rect x="65" y="348" width="1040" height="78" rx="4" fill="#dbb678"/>
<path d="M69 348 H{65+split:.3f} V426 H69 Q65 426 65 422 V352 Q65 348 69 348" fill="#457764"/>
<text x="90" y="386" fill="white" font-size="27" font-weight="700">{credit:.2f} GW credited</text>
<text x="90" y="412" fill="white" font-size="15">Quantified arrangements + operating minimums</text>
<text x="{88+split:.3f}" y="386" font-size="27" font-weight="700">{gap:.2f} GW ceiling</text>
<text x="{88+split:.3f}" y="412" font-size="15">Numerical supply match still unresolved</text>
<text x="65" y="466" font-size="17" font-weight="700">A screening ceiling, not a verified shortage or an open order book.</text>
<text x="65" y="496" font-size="15" fill="#526475">Full campus scope where phases are undisclosed. Assumed 1.2 PUE where only IT load is available.</text>
<text x="65" y="521" font-size="15" fill="#526475">The zero floor reflects missing contract evidence. It does not establish zero customer need.</text>
<line x1="65" x2="1135" y1="549" y2="549" stroke="#d9e2d5"/>
<text x="65" y="604" font-size="37" font-weight="700" fill="#267867">366 MW</text>
<text x="300" y="592" font-size="19" font-weight="700">Meta / El Paso Electric purchased multi-year bridge power</text>
<text x="300" y="622" font-size="16" fill="#526475">ERock SEC prospectus, p. 146 · Already supplier-selected; not open FTAI demand</text>
<text x="65" y="675" font-size="16" font-weight="700">FTAI's opening: deliver when customer schedules run ahead of available electricity.</text>
<text x="65" y="708" font-size="13" fill="#65736e">Source: 50-record public-source audit; power_gap_bridge.csv and power_gap_audit.csv.</text>
<text x="65" y="730" font-size="13" fill="#65736e">No FTAI capture or competition haircut. Grid-timing gaps remain separate and unquantified.</text>
</g></svg>'''
(G/'power-gap-audit.svg').write_text(svg,encoding='utf-8')
print('Published audit JSON, CSVs, memo and SVG graphic.')
