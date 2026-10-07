# FTAI Alt-Data Research Lab

Public, free-source research for the Point72 pitch competition. Research snapshot: **October 5, 2026**. Investment horizon ends October 5, 2027. A provisional long thesis is tested, not presumed proven.

Live website: https://jayadityavetsa.github.io/ftai-alt-data/

## Run the website

Node 22 or later:

```sh
npm ci
npm run dev
npm test
npm run build
```

Open the development server at `/ftai-alt-data/`. Vite uses that base path for GitHub Pages. Navigation uses hashes so direct research-section links need no backend.

## Reproduce public datasets

Python 3.12 or later:

```sh
python -m pip install -r requirements.txt
python scripts/fetch_sources.py
python scripts/download_extra.py
python scripts/build_data.py
python scripts/test_data.py
python scripts/fetch_expansion.py
python scripts/inspect_inventory.py
python scripts/fetch_followup.py
python scripts/fetch_inventory_sheet.py
python scripts/build_expansion.py
python scripts/analyze_inventory_sheet.py
python scripts/build_focus.py
python scripts/test_expansion.py
```

Downloads use public HTTP endpoints, record failures and SHA-256 hashes, and cache originals in ignored `data/raw/`. Add `--refresh` to the initial acquisition script to redownload its sources. FAA ZIP streaming uses the additional acquisition script. The EIA script discovers available workbook links from the EIA source page. Manual refreshes may change live-source content: update the snapshot date, inspect changes, and verify all headline claims before publishing.

`data/curated.json` holds manually reviewed observations with document locators. `public/data/` contains normalized CSVs, website JSON, the Excel model and research memo. Raw PDFs, extracted text, owner names and FAA owner addresses are not published. Downloaded FAA engine-type codes are joined by an exact code match, not inferred from aircraft model. Aircraft manufacture year is not engine age. Registry status codes are retained; this is not an active commercial fleet census.

EIA-860M analysis selects Texas natural-gas generators from three monthly snapshots and compares generator IDs and status. It does not identify customer load-connection dates or establish FTAI exposure. Site screening is purposive, not exhaustive; missing capacity remains blank.

## Models and research standards

`src/models.ts` contains independently testable deployment, engine alternative-use, Power profit/cash and SOTP calculations. Commercial values are editable assumptions. The JV generator-set contract is never booked wholesale as FTAI revenue. JV collections do not enter FTAI cash automatically. Operating EBITDA and equity-method profit are shown separately; their sum is an attribution proxy, not consolidated EBITDA. Net debt and preferred equity are deducted once. Investment book value is an explicitly provisional equity proxy, not a Strategic Capital fair-value estimate.

The spreadsheet contains formulas, a Bear/Base/Bull selector, monthly discounted customer economics, engine allocation and reverse valuation. The builder `artifacts/build_workbook.mjs` uses `@oai/artifact-tool` from the Codex bundled spreadsheet runtime; it is optional and not required to build or serve the site. Link/install that dependency in the artifact directory before running the builder. The committed workbook is the reviewed competition snapshot.

## Deploy

The GitHub Actions workflow tests the committed dataset and models, builds Vite, and deploys the resulting static files. Configure repository Settings → Pages → Source → GitHub Actions. Push to `main` or run the workflow manually. No API keys or paid data are required. CI does not refresh live research sources.

## Outstanding research

The memo prioritizes unresolved site commissioning, Mod-1 performance, engine eligibility, turbine transfer pricing, JV ownership/economics, accounting and dated market expectations. No statistically unsupported confidence intervals or invented market-price observations are published. Chinese translations are checked against the original text, with independent human translation review outstanding. This first version does not establish that FTAI is mispriced.

## Validation

69 model tests cover units, timing, indifference thresholds, yield/capacity constraints, cash attribution and valuation. 35 dataset tests cover duplicates, source references, null handling, CSV reconciliation, fleet-age control totals and generator identity. Browser checks cover responsive layouts, navigation, filters, input changes and chart rendering. Workbook formulas are recalculated, scenario selectors checked and all five sheets visually reviewed.

Freeze a reviewed snapshot by October 11 using a dated Git tag. October 7/10/11 milestones require further manual evidence review; this repository does not schedule unattended research or certify future completeness.


## Second research release

Customer Power Gaps, Production Readiness and Aviation Resilience are now the central research views. Seven customer cases distinguish IT load, electrical load, on-site plant capacity, customer delivery windows, supply procurement and unknown utility dates. No open gap is fabricated when scope/date/permission evidence is absent. The utility's 45 GW undated queue and PJM's system forecasts are overlapping contextual series, not additive turbine markets.

The user-supplied Google Sheet is read through its public CSV export, gid 1561108781. Preserve its column-N counting policy. There are 217 rows, 201 with included quantities, 14 possible-overlap rows and 2 unresolved-identifier rows. The 4,638 subtotal reconciles independently; 6,352 raw displayed items must not be summed as physical stock. An ESN on an LLP is donor provenance, not a available engine. No exact Mod-1 BOM or complete eligible-core count is established. The associated Typeform images remain linked, with two of twelve images spot-checked and full transcription review outstanding. No ownership or current-stock date is inferred.

Run build_expansion before analyze_inventory_sheet: the former publishes curated cases and metadata; the latter attaches the supplied parts audit. Both steps are deterministic with cached originals. Raw spreadsheets are ignored. CI tests committed CSV/JSON and does not access live Google Sheets. The old five-sheet Excel financial model is the October 4 snapshot; new customer/production/inventory models have their own CSV exports on the site.

A single dated FTAI quote-provider observation is available as an optional reverse-valuation input, with local date and UTC trade timestamp. The linked Yahoo page was rate-limited, so it is not independently corroborated. Management's FY2027 Power and Aerospace targets are explicit benchmarks; a free sell-side consensus series remains unavailable.

Supplier pressure and hiring ledgers are published by scripts/build_focus.py. Global OEM backlog and output are kept in different stock/flow scopes; uncommitted 2027–28 slots remain unknown. Hiring evidence is role-specific but historical matched counts remain unavailable. The site does not infer acceleration from mirrors or reposts.


## Research workspace release 3 — October 6

The current UI groups findings into AP productivity, Power execution, SCI II and Other research. It leads with thesis-linked answer cards and puts citations and audits in expandable drawers. Old links map to the appropriate group; original financial and engineering tools remain under Other research.

Rebuild after the previous dataset steps:

```powershell
python scripts/fetch_workspace.py
python scripts/build_workspace.py
python scripts/test_workspace.py
node --experimental-strip-types scripts/export_workspace_models.mjs
npm test
npm run build
```

fetch_workspace caches public originals and records failures. build_workspace deterministically reconstructs segment-specific AP metrics, matches cached job JSON-LD dates, exports the SCI transaction map, publishes conditional demand presets and audits existing EIA name matches. AP margin decomposition is arithmetic, not a measured mix attribution. Mod-1 quarter/start inputs remain analyst assumptions; the parts list does not establish a complete eligible-core baseline. Closed or mirrored jobs do not become additional hires. No empirical hiring growth is claimed.

New monthly production models live in src/workspaceModels.ts. Whole units, feedstock depletion/replenishment, capacity caps and acceptance delays constrain output from October 2026 through March 2028. FY2027 acceptances and cumulative November deliveries are different measures. Financial layers separate turbine earnings and assumed JV earnings; operating cash excludes automatic JV distributions. Power capacity and named customer demand are independent constraints, not proof that every produced unit has a buyer.

The AP scorecard uses AP revenue/cost of sales/operating expense with its existing non-GAAP segment EBITDA series. Cash notes show company-disclosed AP working-capital use alongside explicitly consolidated CFO and adjusted FCF. No AP ROIC is inferred from consolidated capital. See public/data/research-memo-v3.md for interpretation and falsification.

## Power procurement release 4 — October 6

The Power view now starts with a 50-record US campus/program screen, sourced from 58 public primary documents. The map, capacity-basis audit, supply-allocation bars, screening funnel, service-window plot and reverse-demand heatmap separate observed announcements from modeled procurement. Seventeen records have unknown MW. One operating turbine control and four supplemental leads are explicitly identified. Unknown supplier allocation is not an open order; no execution-qualified open MW is independently verified.

At default inputs, normalized IT/electrical design totals 21.292 GW across mixed horizons. Four conditional customer cases produce a 2028 contestable scenario of 1.113 GW; 25% capture implies 14 Mod-1 units required to cover modeled load. That does not independently support a 100-unit annual line. At the default derating/reserve and capture assumptions, 100 units require an 8.182 GW executable open pool. The prior 564.1 MW first-pass model is archived and not a comparable demand-growth observation.

Reproduce this release with `python scripts/curate_datacenters.py`, optional `python scripts/fetch_datacenters.py`, and `node --experimental-strip-types scripts/export_datacenters.mjs`. Run `python scripts/test_datacenters.py`, `npm test`, and `npm run build`. All published scenario tables use the same pure TypeScript calculations as the interface. Raw source originals stay locally ignored; the acquisition manifest publishes failures and checksums. CSVs and the research memo are in public/data. US map geometry is stored locally with provenance in public/geo/README.md.

## Current Power page: contract audit — October 7

The current Power view replaces the release4 scenario headline with the reviewed contract-coverage audit. Fifty original records are accounted for:24 enter the numerical bound and26 are held out with individual reasons. The measurable subset has18.560GW electrical scope,9.379GW numeric supply/operating credits and a conditional9.181GW ceiling at assumed1.2PUE. No competition, FTAI capture or phase haircut enters this arithmetic. This is not a verified shortage or a finite upper bound for all50 records; timing gaps remain separate. The366MW Meta/EPE bridge purchase is mechanism evidence already assigned to a competing supplier.

The main page now includes a downloadable2400×1520 PNG and source-native SVG, a12-case ceiling chart, searchable corrected ledger, exclusion lists and readable source titles/document references. Old assumption-based datasets remain historical files; the main Power page does not render the superseded DataCenterStudy or two-campus scenarios. AP, inventory, hiring and delivery models retain their separate roles.

Reproduce the snapshot with `python scripts/analyze_power_gaps.py`, `python scripts/publish_gap_audit.py`, and `node scripts/render_gap_graphic.mjs`. Rendering uses Sharp from the existing environment or the bundled desktop runtime; set `FTAI_GRAPHICS_NODE_MODULES` for another installed runtime. Published data and chart arithmetic are validated by `scripts/test_gap_audit.py` and `scripts/test_gap_publication.py`, both run in CI. The static SVG/PNG are generated from the same summary as the page and downloadable bridge CSV. No backend or paid API is needed.
# Investment before monetization — October 7 update

The Power page now connects reported inventory cash use, customer funding, factory / role evidence and scheduled deliveries. The AP page separately tests whether a larger engine pool improves capital returns. Three dated job records are a reviewed sample, not a historical opening census. Missing realized Mod-1 deliveries / Power EBITDA remain null; the timeline does not claim an observed 6–18-month lag.

Reviewed inputs: `data/investment_curated.json`. Optional original-document refresh: `scripts/fetch_investment.py`; failures are retained in `data/investment_acquisition.json`. Rebuild public CSV / JSON / memo / SVG with `scripts/build_investment.py`, then render the slide PNG with `node scripts/render_investment.mjs`. Run `python -m unittest discover -s scripts -p 'test_*.py'`, `npm test` and `npm run build`.

Downloads: `public/data/investment.json`, the `investment_*.csv` ledgers, `investment_memo.md`, and `public/graphics/investment-before-monetization.{svg,png}`. Raw originals remain local. This update prioritizes research and the laptop reading flow.
