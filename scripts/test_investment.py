"""Financial scope, missingness and source-reconciliation checks."""
import unittest,json,csv,re
from pathlib import Path
R=Path(__file__).resolve().parents[1];P=R/'public/data'
d=json.loads((P/'investment.json').read_text(encoding='utf-8'))
class InvestmentTests(unittest.TestCase):
 def test_actual_and_guidance_do_not_double_count(self):
  s=d['summary'];self.assertEqual(s['powerFYInvestmentGuidance'],s['powerH1InventoryUse']+s['powerImpliedRemainingGuidance'])
  self.assertEqual(s['powerImpliedRemainingGuidance'],204)
  self.assertIn('do not add',next(r['note'] for r in d['capital'] if r['id']=='power_fy').lower())
 def test_unobserved_monetization_is_null(self):
  for key in ['acceptedMod1Units','realizedPowerEbitda','depositUsdMillion','empiricalLeadMonths']:self.assertIsNone(d['summary'][key])
 def test_monthly_sample_counts_only_dated_unique_roles(self):
  self.assertEqual(len({j['id'] for j in d['hiring']}),len(d['hiring']))
  self.assertEqual(sum(r['datedPostings'] for r in d['postingMonths']),sum(bool(j['posted']) for j in d['hiring']))
  self.assertEqual(d['summary']['datedPostingRecords']+d['summary']['undatedPostingRecords'],len(d['hiring']))
  self.assertEqual([r['month'] for r in d['postingMonths']],['2026-08','2026-09','2026-10'])
 def test_inventory_not_labelled_as_power_stock(self):
  self.assertEqual(len(d['inventory']),5)
  self.assertTrue(all('Consolidated' in r['inventoryScope'] for r in d['inventory']))
  self.assertAlmostEqual(d['summary']['inventoryH1Increase'],350.819)
  self.assertAlmostEqual(d['summary']['inventoryYoYGrowth'],1544.592/752.866-1)
 def test_table_matches_chart_input(self):
  with (P/'investment_inventory.csv').open(encoding='utf-8') as f:r=list(csv.DictReader(f))
  self.assertEqual([float(x['usdMillion']) for x in r],[x['usdMillion'] for x in d['inventory']])
  self.assertEqual([float(x['moduleOutput']) for x in r],[x['moduleOutput'] for x in d['inventory']])
 def test_funding_threshold_is_gross_not_ftai_cash(self):
  for r in d['fundingThresholds']:
   self.assertAlmostEqual(r['orderPercentage'],r['amountMillion']/1465*100)
   self.assertIn('allocation undisclosed',r['basis'])
 def test_source_references_and_dates_resolve(self):
  ids={r['id'] for r in d['sources']}
  for k in ['inventory','capital','events','translations','hiring']:
   for r in d[k]:self.assertIn(r['source'],ids)
  self.assertEqual([r['date'] for r in d['events']],sorted(r['date'] for r in d['events']))
 def test_original_chinese_receipt_not_only_payment_terms(self):
  raw=R/'data/extracted/jereh_update.txt'
  if not raw.exists():self.skipTest('Raw originals remain local')
  t=re.sub(r'\s+','',raw.read_text(encoding='utf-8'))
  for r in d['translations']:
   if r['source']=='update':self.assertIn(re.sub(r'\s+','',r['original']),t)
 def test_source_native_inventory_figures(self):
  # Original captures distinguish HTML/PDF dollar-thousands from published millions.
  for quarter,stem in [('Q2 2025','investment_q225.html'),('Q3 2025','investment_q325.txt'),('Q1 2026','investment_q1.html')]:
   path=R/('data/extracted' if stem.endswith('.txt') else 'data/raw')/stem
   if not path.exists():continue
   value=next(r['usdMillion'] for r in d['inventory'] if r['quarter']==quarter)
   self.assertIn(f'{round(value*1000):,}',path.read_text(encoding='utf-8'))
 def test_memo_published_identically(self):
  self.assertEqual((P/'investment_memo.md').read_bytes(),(R/'research/investment-before-monetization-2026-10-07.md').read_bytes())
if __name__=='__main__':unittest.main()
