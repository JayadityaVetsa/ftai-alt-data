"""Publish the reviewed investment/monetization ledger without inventing missing quarters."""
from pathlib import Path
import csv,json
from collections import Counter
from html import escape
R=Path(__file__).resolve().parents[1];P=R/'public/data';G=R/'public/graphics'
d=json.loads((R/'data/investment_curated.json').read_text(encoding='utf-8'))
w=json.loads((P/'workspace.json').read_text(encoding='utf-8'))
acquisition=json.loads((R/'data/investment_acquisition.json').read_text(encoding='utf-8')) if (R/'data/investment_acquisition.json').exists() else []
d['acquisition']=acquisition
d['hiring']=w['hiring']
source_ids={s['id'] for s in d['sources']}
for j in d['hiring']:
 s=next(s for s in w['sources'] if s['id']==j['source'])
 if s['id'] not in source_ids:
  d['sources'].append(dict(id=s['id'],title=s['title'],url=s['url'],date=s.get('published'),locator=s.get('locator'),file=None));source_ids.add(s['id'])
 for_date=j.get('posted')
 if for_date:
  d['events'].append(dict(date=for_date[:10],lane='Production readiness',title=j['role'],detail=j['signal'],basis=j['dateBasis'],source=j['source'],locator='Unique reviewed posting; not a hire'))
d['events'].sort(key=lambda e:e['date'])
c=Counter(j['posted'][:7] for j in d['hiring'] if j.get('posted'))
d['postingMonths']=[dict(month=m,datedPostings=n,basis='Dated records in reviewed sample; not total openings or hires') for m,n in sorted(c.items())]
for r in d['inventory']:
 a=next(a for a in w['ap'] if a['quarter']==r['quarter'])
 r.update(apRevenue=a['revenue'],apEbitda=a['ebitda'],moduleOutput=a['modules'],apSource=a['source'],inventoryScope='Consolidated ending net inventory; not AP-only or Power-only')
first,last=d['inventory'][0],d['inventory'][-1]
d['summary']=dict(powerH1InventoryUse=46,powerFYInvestmentGuidance=250,powerImpliedRemainingGuidance=250-46,
 inventoryYoYGrowth=last['usdMillion']/first['usdMillion']-1,inventoryH1Increase=last['usdMillion']-d['inventory'][2]['usdMillion'],
 apEbitdaYoYGrowth=last['apEbitda']/first['apEbitda']-1,modulesYoYGrowth=last['moduleOutput']/first['moduleOutput']-1,
 datedPostingRecords=sum(c.values()),undatedPostingRecords=len(d['hiring'])-sum(c.values()),
 acceptedMod1Units=None,realizedPowerEbitda=None,depositUsdMillion=None,empiricalLeadMonths=None,
 powerGuidanceEbitda2027=450,mod1Target2027=100)
# Show thresholds, never claim an unknown advance covers FTAI's working capital.
d['fundingThresholds']=[dict(amountMillion=n,orderValueMillion=1465,orderPercentage=n/1465*100,
 scope=scope,basis='Threshold arithmetic only; advance amount, use restrictions and FTAI allocation undisclosed')
 for n,scope in [(46,'H1 Power inventory cash use'),(204,'Implied remainder of FY2026 Power investment outlook'),(250,'FY2026 Power investment outlook')]]
def out(name,rows):
 if not rows:return
 keys=list(dict.fromkeys(k for r in rows for k in r))
 with (P/f'{name}.csv').open('w',encoding='utf-8',newline='') as f:
  wr=csv.DictWriter(f,fieldnames=keys);wr.writeheader()
  for r in rows:wr.writerow({k:json.dumps(v,ensure_ascii=False) if isinstance(v,(list,dict)) else v for k,v in r.items()})
for key in ['inventory','capital','events','hiring','postingMonths','translations','coverage','sources','fundingThresholds']:out('investment_'+key,d[key])
(P/'investment.json').write_text(json.dumps(d,ensure_ascii=False,indent=2,allow_nan=False),encoding='utf-8')
memo='''# Capital before monetization — October 7, 2026

FTAI reported $46m of Power inventory working-capital use in H1 2026. Its FY2026 Power investment outlook is $250m, including that H1 amount; $204m is implied remaining guidance, not spending already observed. The separately announced $180m additional allocation overlaps the outlook and must not be added. R&D is an additional expense category; the inventory cash-use figure is not all Power cost.

The stronger independent check is the other party's disclosure. Jereh's September 4 meeting record confirms receipt of the first advance for the same $1.465bn accepted J&F order, with no 2026 earnings impact expected from that order. The July contract links further payments to production and acceptance testing, then commissioning, with final payment no later than 90 days after arrival. The advance amount and FTAI's economic share are undisclosed. This is evidence of customer-funded execution beginning, not proof that all FTAI investment is covered or that order value equals FTAI revenue.

The original Chinese contract says batch deliveries before November 2027; FTAI's slide says through November. Both are future schedules; preserve that discrepancy. One hundred units and $450m FY2027 Power Adjusted EBITDA are management targets. No verified customer-accepted unit count or standalone realized Power EBITDA series was found. A measured 6–18-month lead cannot yet be established: a forecast endpoint is not an observed outcome.

Production evidence triangulates conversion configuration in Montreal with production planning and FAT/testing in Houston. There are five reviewed role leads, three dated records (one each August, September and October 2026), two undated, and no historical matched monthly census. The October sample is partial. These are job/post dates, not hires, vacancies outstanding or proof of acceleration. Montreal's expansion map and Jereh's reported factory expansion/rental support readiness, not a measured Mod-1 quarterly capacity. Jereh serves multiple engine suppliers and programs.

## Connection to the AP thesis

AP quarterly module output grew 61% and EBITDA about 51% year over year. Consolidated net inventory grew about 105%, to $1.545bn, and company-reported H1 Aerospace inventory cash use was $407m. These measures have different scopes and cannot produce AP ROIC or inventory turns. The larger earnings pool is real; improving capital productivity remains a proposition to test.

Inventory purchases reduce cash before their sale; capitalized inventory does not automatically reduce current EBITDA margin. Power expenses are included in Corporate & Other, not an automatic explanation of AP margin dilution. Proof that AP dilution is temporary requires workscope-adjusted contribution and repeat cash returns, not merely higher Power spending. The November 2025 tour also targeted 40%+ 2026 margin; the lower current margin deserves explicit reconciliation rather than being dismissed.

## Pitch wording

“FTAI is already funding the Power ramp: $46m of inventory cash use in H1 precedes scheduled 2027 deliveries. Jereh confirms the anchor customer has paid the first advance, and later payments are tied to production and testing. That makes the ramp more tangible than an unfunded capacity announcement; customer acceptance and FTAI-attributable cash earnings are the next proof points.”

## What would strengthen or falsify this

Track actual production tests and customer-accepted shipments; follow-on milestone receipts; inventory release and replenishment; AP comparable-work contribution and own-capital returns. Missed acceptance, persistent inventory accumulation without cash release, repeated performance discounts or increased capital per repeat transaction weaken the long. Public-source coverage and all unavailable metrics are in investment_coverage.csv. No LinkedIn employee-growth series or matched Mod-1 imports/serial shipments is claimed.

Reproduce: fetch_investment.py (optional manual source refresh), build_investment.py, render_investment.mjs. The reviewed inputs are data/investment_curated.json; raw originals stay local. All monetary chart amounts are USD millions and all forecast periods are explicitly labelled.
'''
(P/'investment_memo.md').write_text(memo,encoding='utf-8');(R/'research/investment-before-monetization-2026-10-07.md').write_text(memo,encoding='utf-8')
# A slide-native figure with separate units / scopes, no synthetic combined index.
parts=['<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="820" viewBox="0 0 1200 820">',
'<rect width="1200" height="820" fill="#f6f4ef"/><style>text{font-family:Arial,sans-serif;fill:#14253d}.muted{fill:#617080}.green{fill:#457764}.small{font-size:14px}.label{font-size:17px}.big{font-size:34px;font-weight:700}</style>']
def txt(x,y,t,cls='label'):parts.append(f'<text x="{x}" y="{y}" class="{cls}">{escape(t)}</text>')
txt(48,46,'FTAI | CAPITAL BEFORE MONETIZATION','small');txt(48,92,'Spending is real. The customer has started paying.','big')
txt(48,122,'2027 delivery / earnings targets follow. Milestone spacing is illustrative; evidence through October 7, 2026.','label')
for x,value,title,note in [(48,'$46m','H1 Power inventory cash use','Company-reported; actual period'),(420,'$250m','FY2026 Power investment','Management outlook; includes $46m'),(792,'Advance received','Anchor order first payment','Jereh disclosure; amount unknown')]:
 parts.append(f'<rect x="{x}" y="155" width="350" height="125" rx="10" fill="white"/>');txt(x+18,200,value,'big');txt(x+18,231,title);txt(x+18,258,note,'small')
txt(48,330,'Investment / readiness: 2026 evidence','label');txt(740,330,'Monetization: 2027 targets','label')
parts.append('<path d="M 76 420 H 1115" stroke="#ccd3d5" stroke-width="4"/><path d="M 740 355 V 550" stroke="#dd7955" stroke-dasharray="5 5"/>')
for x,date,title,note in [(90,'H1 2026','$46m inventory','Actual cash-use disclosure'),(310,'July 2026','$1.465bn order','Accepted J&F order'),(535,'Sept. 4, 2026','Advance received','Factory expansion reported'),(800,'Before Nov. 2027','Batch deliveries','Contract schedule'),(1035,'FY2027','100 / $450m','Units / Power EBITDA target')]:
 parts.append(f'<circle cx="{x}" cy="420" r="9" fill="{"#457764" if x<740 else "#dd7955"}"/>');txt(max(48,x-75),385,date,'small');txt(max(48,x-75),462,title.replace('&amp;','&'),'label');txt(max(48,x-75),490,note,'small')
txt(48,560,'AP capital-return check: do not confuse more inventory with better productivity.','label')
for x,v,t in [(48,'+105%','Consolidated inventory, Q2 YoY'),(420,'+61%','AP module output, Q2 YoY'),(792,'+51%','AP Adjusted EBITDA, Q2 YoY')]:
 txt(x,618,v,'big');txt(x,645,t,'small')
txt(48,695,'Hiring: 3 dated posting records + 2 undated leads; no measured monthly hiring-growth series.','small')
txt(48,723,'Deposit size / FTAI share unknown. No observed accepted-unit or standalone Power EBITDA series.','small')
txt(48,751,'This establishes a sequence before planned delivery, not an empirically measured 6–18-month lag.','small')
txt(48,790,'Sources: FTAI Q2 supplement slides 6–7, 13, 22, 29; Jereh July contract pp. 1–3 / September record pp. 2–3.','small')
parts.append('</svg>');G.mkdir(exist_ok=True);(G/'investment-before-monetization.svg').write_text('\n'.join(parts),encoding='utf-8')
print('Published investment timeline, 5-quarter inventory series, funding thresholds and source ledger.')
