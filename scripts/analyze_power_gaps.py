"""Reconcile all 50 records; write research files only, not website assets."""
import json,csv,collections
from pathlib import Path
R=Path(__file__).resolve().parents[1]
d=json.loads((R/'data/datacenter_study.json').read_text(encoding='utf-8'))
notes=json.loads((R/'data/power_gap_audit_notes.json').read_text(encoding='utf-8'))
assert set(notes)=={r['id'] for r in d['rows']}
credits={'frontier':115,'abilene_original':200,'saline':1400,'iren_sw1':1400,'iren_sw2':600,'iren_childress':750,'kiowa':1600,'river_bend':330,'pf1':100,'lake_mariner':102,'justified':482,'muskie':500,'barber':300,'black_pearl':300,'colchis':1000,'ulysses':200}
gross={'river_bend':330,'beacon':1000,'df1':430,'justified':482}
def electrical(r,pue):
 if r['id'] in gross:return gross[r['id']]
 if r['mw'] is None:return None
 if r['basis']=='IT':return r['mw']*pue
 return r['mw'] if r['basis']=='electrical' else None
rows=[]
for old in d['rows']:
 r=dict(old);id=r['id']
 r.update(originalStatus=old['status'],originallyExcluded=not old['modelEligible'],auditNote=notes[id]['note'],extraSourceUrls=notes[id].get('urls',[]))
 if id=='ms_abilene':r.update(mw=672,basis='IT')
 if id=='milam':r.update(mw=750,basis='unspecified',firstYear=2027,lastYear=None)
 if id=='muskie':r.update(mw=500,readyWindow='First 500 MW ramps in 2028; next 500 MW in 2029')
 if id=='tcdc':r.update(mw=1000,basis='at_least_unresolved',firstYear=None,lastYear=None)
 load=electrical(r,1.2)
 if r['mw'] is None:reason='Load MW missing'
 elif r['basis']=='generation':reason='Generation scope, not customer load'
 elif load is None:reason='Capacity definition unresolved'
 elif r['firstYear'] is None or r['firstYear']>2028:reason='No reviewed first-service window by 2028'
 else:reason='Included: known load scope and first-service window by 2028'
 included=reason.startswith('Included');credit=credits.get(id,0)
 r.update(boundIncluded=included,boundInclusionReason=reason,electricalScopeMwAtPue12=load,creditedSupplyMw=credit,creditType=notes[id].get('creditType','No numeric credit found; NOT proof of no contract'),verifiedUncontractedMinimumMw=0,contractCoverageCeilingMw=max(0,load-credit) if included else None,actualGapLowerMw=None,actualGapUpperMw=None,firmOnTimeSupplyMw=None,shortageMonths=None)
 r['sourceUrls']=[s['url'] for s in d['sources'] if s['id'] in r['sources']]+r['extraSourceUrls']
 rows.append(r)
def summary(pue):
 a=[r for r in rows if r['boundIncluded']];load=sum(electrical(r,pue) for r in a);credit=sum(min(electrical(r,pue),r['creditedSupplyMw']) for r in a)
 return dict(pue=pue,records=len(a),electricalScopeMw=load,creditedSupplyMw=credit,verifiedUncontractedFloorMw=0,conditionalAllocationCeilingMw=load-credit,positiveCeilingRecords=sum(electrical(r,pue)>r['creditedSupplyMw'] for r in a))
out=dict(asOf=d['asOf'],scope='All 50 original records audited. Conditional public contract-coverage ceilings, not actual shortages or full-market bounds.',rows=rows,summary=summary(1.2),pueSensitivities=[summary(v) for v in [1.1,1.2,1.4]],coverage=dict(collections.Counter(r['boundInclusionReason'] for r in rows)),originalExclusions=dict(total=sum(r['originallyExcluded'] for r in rows),byStatus=dict(collections.Counter(r['originalStatus'] for r in rows if r['originallyExcluded']))),documentedPurchasedBridgeMw=366,fullFiftyGapLowerMw=None,fullFiftyGapUpperMw=None,ftaiCaptureApplied=False,competitionHaircutApplied=False,phaseHaircutApplied=False)
(R/'data/power_gap_audit.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
fields=['id','name','customer','originalStatus','originallyExcluded','mw','basis','readyWindow','boundIncluded','boundInclusionReason','electricalScopeMwAtPue12','creditedSupplyMw','creditType','verifiedUncontractedMinimumMw','contractCoverageCeilingMw','actualGapLowerMw','actualGapUpperMw','firmOnTimeSupplyMw','shortageMonths','auditNote','sourceUrls']
with (R/'data/power_gap_audit.csv').open('w',newline='',encoding='utf-8-sig') as f:
 w=csv.DictWriter(f,fieldnames=fields);w.writeheader()
 for r in rows:w.writerow({k:' | '.join(r[k]) if isinstance(r.get(k),list) else r.get(k) for k in fields})
print(json.dumps({k:out[k] for k in ['summary','pueSensitivities','coverage','originalExclusions']},indent=2))

report=R/'research';report.mkdir(exist_ok=True)
a=out['summary']
text=f'''# Power gap audit: answers for the team
Evidence cutoff October 6, 2026. All 50 original records audited. Published on the Power page October 7, 2026.

## The number and what it means
The public-record audit gives a **conditional 0–{a['conditionalAllocationCeilingMw']/1000:.2f} GW contract-coverage range for 24 measurable records**. This is not a forecast of actual shortages. At 1.2 assumed PUE, the cohort has {a['electricalScopeMw']/1000:.2f} GW of published electrical scope, against {a['creditedSupplyMw']/1000:.3f} GW of usable numeric supply/allocation credits. Twelve records retain a positive ceiling; twelve have sufficient numerical credits for their stated scope.

The floor is zero because public disclosures do not prove any particular quantified portion is uncontracted: private/portfolio/undisclosed arrangements may fill every residual. It does not mean the real market has zero need. The ceiling treats unresolved supplier volumes as potentially uncovered, uses full published scopes when phases are missing, and assumes credited arrangements perform. It is an upper screening envelope, not a central estimate. IT-to-electricity conversion is an assumption. Upper-ceiling sensitivity is {out['pueSensitivities'][0]['conditionalAllocationCeilingMw']/1000:.2f} GW at 1.1 PUE and {out['pueSensitivities'][2]['conditionalAllocationCeilingMw']/1000:.2f} GW at 1.4 PUE. These are alternative ceilings, not a positive shortage interval.

There is **no defensible finite numerical upper bound for all 50** from the reviewed documents: 16 records lack load MW, six have unresolved capacity definitions, one lacks a service window, and three are generation-only/control records. Unknown values remain unknown; they are not zero. Grid-timing gaps are separate and are not measured by subtracting eventual contract capacity. Connections, approvals and capacity rights are not unconditional firm-hour energy guarantees.

No assumed competing supplier wins, FTAI capture, turbine units, production growth or arbitrary campus-phase haircut enters this calculation. No open tender, firm gas supply or turbine permission is inferred from a residual.

## What the previous screen excluded
The old model included four records and excluded 46: 25 utility-strategy records, eight selected-solution records and 13 explicitly unresolved records. This did not establish that those 46 had all their power needs met.

The 13 explicitly unresolved records were: Claude, Milam, Meta El Paso, Meta Lebanon, Meta Tulsa, AWS Salem, AWS Falls, AWS Madison, AWS Warren, AWS Hinds, Google Muskogee, Google Stillwater, and Microsoft La Porte. The earlier model's 17 missing-MW records overlap those categories; they are not an additional exclusion bucket. Milam is now ~750 MW but remains outside the numerical bound because the capacity basis is unclear.

## Thesis connection: words that can be used in a pitch
Customers already buy power to bridge grid delays: Enchanted Rock's SEC filing identifies a signed 366 MW purchase for Meta/El Paso Electric and describes multiple years of bridge use while a substation is built. Our 50-record audit flags up to {a['conditionalAllocationCeilingMw']/1000:.1f} GW in a measurable subset for site-level supply reconciliation, rather than treating every announced gigawatt as an open order. FTAI's opportunity is to compete where electricity is needed before existing arrangements can deliver it; the next proof is matching delivery dates and available supply to those customer phases.

The 366 MW is purchased bridge capacity, not 366 MW open for FTAI. It appears twice in the SEC filing's case studies but is counted once. The 57 Duke bridge engines for AWS Richmond independently support the mechanism, but their unverified electric MW are not added to this subtotal.

## Important corrections
- Microsoft Abilene: 900 MW is plant nameplate; customer buildings are two × 336 MW IT. At 1.2 PUE, the demand-equivalent scope is 806.4 MW.
- Justified: August-approved 482 MW Retail Electric Service Agreement replaces vague power-advantaged wording.
- Muskie: October 5 agreement allocates 500 MW starting to ramp in 2028 and another 500 MW in 2029. The full 1 GW is not treated as 2028 load or availability.
- TCDC: old 1.4 GW source now fails acquisition. March SEC material supports a 1+ GW ambition and separate 200/450/350 MW development stages; finite 2028 load is unreconciled and excluded.
- Applied Digital leases contract IT/customer demand. Its portfolio grid scope and 'land and/or utility agreements' wording do not establish a numeric campus-by-campus electricity allocation.
- Crusoe/GE, Vantage/VoltaGrid and Oracle/VoltaGrid portfolio orders cannot be subtracted wholly from one campus or repeatedly from several campuses.

## Twelve positive ceiling cases
These are document-reconciliation residuals. Several have selected utility/equipment providers; they are not twelve verified open procurements.

| Record | Electrical scope MW | Numeric credit MW | Conditional ceiling MW | Why not a measured shortage |
|---|---:|---:|---:|---|
'''
for r in rows:
 if r['boundIncluded'] and r['contractCoverageCeilingMw']>0:
  text+=f"| {r['name']} | {r['electricalScopeMwAtPue12']:,.1f} | {r['creditedSupplyMw']:,.0f} | {r['contractCoverageCeilingMw']:,.1f} | {r['auditNote']} |\n"
text+='\n## Every exclusion from the new numerical bound\n'
for reason in out['coverage']:
 if not reason.startswith('Included'):
  names='; '.join(r['name'] for r in rows if r['boundInclusionReason']==reason)
  text+=f"\n**{reason} ({out['coverage'][reason]}):** {names}.\n"
text+='\n## Full 50-record source ledger\n\n| Record | Numerical treatment | Credit type | Audit finding and sources |\n|---|---|---|---|\n'
for r in rows:
 refs=' '.join(f'[source {i+1}]({url})' for i,url in enumerate(r['sourceUrls']))
 text+=f"| {r['name']} | {r['boundInclusionReason']} | {r['creditType']} | {r['auditNote']} {refs} |\n"
text+='''
## Evidence and reproducibility
This combines the existing primary-source ledger with additional publisher/regulator/SEC checks. Direct downloads are distinct from browser-readable text: see data/gap_audit_acquisition.json for new successes, failures and hashes. An inaccessible original is not silently treated as zero supply. Raw originals remain local and are not redistributed. The ERock public SEC text is readable through the research browser despite direct-download 403.

Reproduce: `python scripts/analyze_power_gaps.py`. Inputs: original data/datacenter_study.json and manually reviewed data/power_gap_audit_notes.json. Outputs: data/power_gap_audit.json, data/power_gap_audit.csv and this memo. The current Power page publishes this audit; older assumption-based datasets are historical files, not the current contract-coverage estimate.
'''
(report/'power-gap-audit-2026-10-06.md').write_text(text,encoding='utf-8')
