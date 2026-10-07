# FTAI Power: a 50-record US procurement screen
Research date: October 6, 2026. Thesis 2: Mod-1 commercialization and sustainable cash earnings.

## Answers for the team
The sample contains 50 named-campus or campus-program records, not 50 verified open tenders. It includes one operating modular-turbine control. Thirty-three records have a published capacity; seventeen do not. At an assumed 1.2 PUE, 5.368 GW of IT capacity plus 14.85 GW of electrical capacity becomes 21.292 GW of electrical design equivalent. This is a mixed-horizon pipeline, not an uncovered 2028 market. Generation ratings and unresolved capacity definitions are excluded.

The default 2028 screening scenario uses four cases: Microsoft Abilene, Frontier, Lighthouse and Saline. Campus phases and bridge fractions are assumptions. After Frontier's disclosed 115 MW available power and 50% assumed competing supply, the potentially contestable pool is 1.113 GW. At 25% FTAI capture, 25 MW nameplate, 10% derating and 10% reserve, this implies 14 units required to cover captured load, before commercial qualification. The low/high cases are approximately 0.330/1.996 GW contestable and 2/40 FTAI units. These are scenario ranges, not statistical confidence intervals or orders.

The former 564.1 MW model covered two campuses in 2027 under different scope and phasing. The new 2028 figure is not measured demand growth. In the expanded model, 2027 base contestable power is 530.325 MW.

## Insight 1: bridge demand is a demonstrated purchasing mechanism
[NC DEQ's August 28 final permits](https://content.govdelivery.com/accounts/NCDEQ/bulletins/427509e) approve 57 Duke non-emergency engines for the AWS Energy Way campus until grid service, retired within one year of operation. AWS's 588 emergency engines are separate. The record proves bridge-power demand but identifies an already-selected diesel solution, not open FTAI demand. No MW is inferred from engine count.

[Virginia DEQ's VA2 assessment, p. 3](https://www.deq.virginia.gov/home/showpublisheddocument/35701/639128956440930000) records eight Solar SMT130 turbines, 16.5 MWe each, operating as primary power since April 2024. This 132 MW installation is a real modular-gas operating precedent, already competitor-supplied.

[Wisconsin PSC's September 10 Ozaukee order](https://psc.wi.gov/Pages/CommissionActions/CasePages/OzaukeeTransmission.aspx) revokes completeness for ATC's transmission application. Lighthouse's target first customer delivery is 2H 2027. This creates a specific readiness question, but no revised grid date, permitted turbine bridge or verified shortage duration is established. The model's 25% bridge fraction is a stress assumption.

Financial connection: customers' willingness to buy earlier electricity can support equipment value and service income. Actual earnings require FTAI wins, acceptable delivery dates, customer acceptance and attributable turbine/JV economics. Demand MW alone does not establish sales price, margin or revenue recognition.

## Insight 2: test the 2.5 GW annual line from the customer side
100 units at 25 MW equals 2.5 GW nameplate output annually, not 2.5 GW usable site load. The derating/reserve assumptions imply 2.045 GW usable load. At 25% share of the post-competition pool, an 8.182 GW executable open pool is needed to sustain 100 annual units. The sampled default pool is smaller; the screen does not independently verify 100 annual FTAI orders and does not cap the national market.

GE Vernova's Q2 2026 global gas backlog plus slots is 116 GW, versus a 20 GW production pace starting Q3 2026 and 24 GW in 2028. Siemens described gas capacity sold out through FY2028; Wärtsilä still described some 2027–28 slots. These are different products and scopes. Subtracting global backlog from US campus announcements would manufacture a gap. Source URLs, dates and scope are in datacenter_sources.csv.

## Coverage and falsification
This is purposive public-source research across major hyperscalers, AI developers and colocation providers, not an exhaustive global registry or statistical meta-analysis. Fifty-eight sources are linked; the separate acquisition manifest records 45 downloaded originals and 13 failed retrievals. Download failure is distinct from public text review. Raw originals are cached locally and not redistributed. Approximate map coordinates represent cities/regions, not surveyed pads. Natural Earth map geometry is distributed via Plotly's public geography asset.

Utility capacity commitments, selected suppliers and unresolved allocations are separate classifications. Missing supplier disclosure does not establish an open tender. No record currently has independently verified execution-qualified open MW or shortage duration. Firm gas, emissions permission, load ramps, supply ramps and installation readiness must be matched before a scenario becomes qualified demand.

Priorities: reconcile Microsoft OEM allocation; Frontier's gas/permit and multi-site VoltaGrid allocation; Lighthouse's refile and bridge plan; Saline's monthly utility ramp; Claude's firm gas and air equipment; Meta El Paso's MW basis and supplier. The Texas September 21 TCEQ permit halt can delay on-site generation too; it does not establish an off-grid exemption.

Falsification: full timely utility/OEM supply at modeled cases; site delays beyond 2028; unavailable gas/permits; delivery or acceptance delays; weak FTAI capture; Power contributions failing to cover conversion, packaging, retained capital and forgone AP earnings. Inventory parts and hiring functions are supporting supply-chain evidence, not a verified completed-engine or annual line count.

## Reproduce
Run `python scripts/curate_datacenters.py`, optionally `python scripts/fetch_datacenters.py`, then `node --experimental-strip-types scripts/export_datacenters.mjs`. Fetching refreshes acquisition evidence; it does not independently update manual classifications. Run `python scripts/test_datacenters.py`, `npm test`, and `npm run build`. Downloads and interactive charts use the same pure calculation functions in src/datacenterModels.ts. Export the current interactive calculation to preserve changed assumptions.
