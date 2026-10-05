# FTAI Alt-Data Research Lab

Public, free-source research for the Point72 pitch competition. Research snapshot: **October 4, 2026**. Investment horizon ends October 4, 2027. A provisional long thesis is tested, not presumed proven.

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

20 model tests cover units, timing, indifference thresholds, yield/capacity constraints, cash attribution and valuation. Dataset tests cover duplicates, source references, null handling, CSV reconciliation, fleet-age control totals and generator identity. Browser checks cover responsive layouts, navigation, filters, input changes and chart rendering. Workbook formulas are recalculated, scenario selectors checked and all five sheets visually reviewed.

Freeze a reviewed snapshot by October 11 using a dated Git tag. October 7/10/11 milestones require further manual evidence review; this repository does not schedule unattended research or certify future completeness.
