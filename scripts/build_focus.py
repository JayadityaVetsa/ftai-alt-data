"""Publish the reviewed supplier and hiring ledger; no live refresh in CI."""
from pathlib import Path
import csv,json
R=Path(__file__).resolve().parents[1]; P=R/'public/data'
observed='2026-10-05'
gev='https://www.gevernova.com/news/articles/ge-vernova-releases-second-quarter-2026-financial-results'
pressure=[dict(supplier='GE Vernova',indicator=indicator,value=value,unit=unit,period=period,basis=basis,source=gev,observed=observed,unallocated2027_28Mw=None) for indicator,value,unit,period,basis in [
 ('Gas equipment backlog plus slot reservations',100,'GW','Q1 2026','Global stock; reservations include future years'),
 ('Gas equipment backlog plus slot reservations',116,'GW','Q2 2026','Global stock; not US data-center shortages'),
 ('Annual turbine production pace',20,'GW/year','Starting Q3 2026','Management production guidance; not free slots'),
 ('Annual turbine production plan',24,'GW/year','2028','Management guidance; all global Gas Power')]]
hirings=[dict(employer='Jereh',role='Senior Strategic Sourcing Manager – Power Generation (Gas Turbines)',postingId='4469616069',posted=None,observed=observed,status='Employer-posted public description reviewed',specificity='Gas turbine sourcing; not exclusive to Mod-1',url='https://www.linkedin.com/jobs/view/senior-strategic-sourcing-manager-%E2%80%93-power-generation-gas-turbines-at-jereh-north-america-group-4469616069',historicalMatchedCount=None),
 dict(employer='Jereh',role='Senior controls engineer',postingId='4450528560',posted=None,observed=observed,status='Expired redirect; not counted as current',specificity='Search-index lead only',url='https://www.linkedin.com/jobs/view/senior-engineer-at-jereh-north-america-group-4450528560',historicalMatchedCount=None),
 dict(employer='FTAI',role='Power Technician',postingId=None,posted=None,observed=observed,status='Secondary mirror; employer ATS corroboration unavailable',specificity='Power commissioning / service lead, excluded from verified count',url='https://www.tealhq.com/job/power-technician_7ea1a574692149504c263c9480f00886b657d',historicalMatchedCount=None)]
for title in ['Senior HR Recruiter','Global Supply Chain Director','Sales Support Specialist','Account Director (Canada)','Sr. Account Manager – NexGen Frac & Mobile Power Solutions','Director of Engineering']:
 hirings.append(dict(employer='Jereh',role=title,postingId=None,posted='2025-07 (month only)',observed=observed,status='Displayed on official careers page; no unique requisition ID',specificity='Group-wide; not dedicated Mod-1 throughput',url='https://www.jereh-nag.com/careers/careers.jsp',historicalMatchedCount=None))
def out(name,rows):
 with (P/f'{name}.csv').open('w',encoding='utf-8',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
out('supply_pressure',pressure);out('hiring_evidence',hirings)
sources=[('gev_capacity','GE Vernova Q2 2026 supply guidance',gev,'2026-07-22','Results highlights and CEO statement','Global supply pressure; free 2027–28 slots undisclosed'),('jereh_careers','Jereh official careers page','https://www.jereh-nag.com/careers/careers.jsp',None,'Six displayed titles; release labels July 2025','Historical matched opening counts unavailable'),('jereh_sourcing','Jereh gas-turbine sourcing role',hirings[0]['url'],None,'Employer-posted description, ID 4469616069','Exact posting date unknown; capability signal only'),('faa_llp','FAA engine life-limited parts guidance','https://www.faa.gov/documentLibrary/media/Advisory_Circular/AC_33_70-1_Chg_1.pdf','2017-02-24','AC 33.70-1 Change 1','Operating limits and records; aircraft age is not engine eligibility'),('ftai_recruiting','FTAI company recruiting campaign','https://www.linkedin.com/posts/ftai-aviation-llc_ftaiaviation-powerfortheaftermarket-ftaipower-activity-7456058491481464832-uGku',None,'Company post indexed with FTAI Power tag','Exact posting date unverified; not a job-count series')]
for filename,csvname in [('expansion.json','expansion_sources'),('research.json','sources')]:
 d=json.loads((P/filename).read_text(encoding='utf-8'));ledger={s['id']:s for s in d['sources']}
 for id,title,url,published,locator,review in sources:
  ledger[id]=dict(id=id,title=title,url=url,published=published,locator=locator,review=review,status='Browser-reviewed public source; raw capture unavailable',accessed=observed)
 d['sources']=list(ledger.values())
 (P/filename).write_text(json.dumps(d,indent=2,ensure_ascii=False,allow_nan=False),encoding='utf-8')
 keys=list(dict.fromkeys(k for r in d['sources'] for k in r))
 with (P/f'{csvname}.csv').open('w',encoding='utf-8',newline='') as f:
  w=csv.DictWriter(f,fieldnames=keys);w.writeheader();w.writerows(d['sources'])
print('Published supplier pressure and hiring evidence ledgers')
