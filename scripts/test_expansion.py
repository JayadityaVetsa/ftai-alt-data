import csv,json,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];P=ROOT/'public/data';d=json.loads((P/'expansion.json').read_text(encoding='utf-8'))
class ExpansionTests(unittest.TestCase):
 def test_unique_cases_and_source_ids(self):
  self.assertEqual(len(d['sites']),len({r['id'] for r in d['sites']}))
  self.assertEqual(len(d['sources']),len({r['id'] for r in d['sources']}))
 def test_case_sources_resolve(self):
  ids={s['id'] for s in d['sources']}
  for r in d['sites']:
   for s in r['sources']:self.assertIn(s,ids)
  for r in d['evidence']+d['context']+d['procurements']:self.assertIn(r['source'],ids)
 def test_no_unknown_gap_fabricated(self):self.assertTrue(all(r['verifiedGapMw'] is None for r in d['sites']))
 def test_adjacent_abilene_sites_distinct(self):
  r={s['id']:s for s in d['sites']};self.assertNotEqual(r['microsoft_abilene']['group'],r['stargate_existing']['group'])
 def test_current_lighthouse_capacity_not_old_round_number(self):self.assertEqual(next(r for r in d['sites'] if r['id']=='lighthouse')['loadMw'],902)
 def test_jupiter_competitor_exclusion(self):self.assertTrue(next(r for r in d['sites'] if r['id']=='jupiter')['excluded'])
 def test_module_growth_comparison(self):
  a=d['moduleProduction'];self.assertEqual(a[-1]['modules'],296);self.assertEqual(a[0]['modules'],184);self.assertAlmostEqual((296/184-1)*100,60.869565,places=5)
 def test_inventory_source_control(self):
  rr=d['inventory']['parts'];s=d['inventory']['summary'];self.assertEqual(sum(r['includedQuantity'] for r in rr if r['includedQuantity'] is not None),4638);self.assertEqual(len(rr),217);self.assertEqual(s['sourceQuantity']-s['includedQuantity'],1714)
 def test_null_exclusions_and_zero_stock_distinct(self):
  rr=d['inventory']['parts'];self.assertTrue(any(r['includedQuantity']==0 for r in rr));self.assertTrue(any(r['includedQuantity'] is None for r in rr))
  for r in rr:
   if r['treatment']!='Include':self.assertIsNone(r['includedQuantity'])
 def test_all_part_duplicates_excluded(self):
  rr={r['sheetRow']:r for r in d['inventory']['parts']}
  for duplicate in d['inventory']['summary']['duplicates']:
   for row in duplicate['sheetRows']:self.assertIsNone(rr[row]['includedQuantity'])
 def test_stock_date_and_power_eligibility_not_inferred(self):
  self.assertIsNone(d['inventory']['summary']['stockDate']);self.assertEqual(d['inventory']['summary']['completeEngineRows'],0)
  for r in d['inventory']['parts']:self.assertIsNone(r['stockDate']);self.assertTrue(r['powerEligibility'].startswith('Unknown'))
 def test_area_chart_reconciles(self):self.assertEqual(sum(r['includedQuantity'] for r in d['inventory']['byArea']),4638)
 def test_inventory_csv_reconciles_to_json(self):
  with (P/'inventory_parts.csv').open(encoding='utf-8') as f:rr=list(csv.DictReader(f))
  self.assertEqual(len(rr),217);self.assertEqual(sum(int(r['includedQuantity']) for r in rr if r['includedQuantity']),4638)
 def test_part_numbers_preserved_as_text(self):
  rr=d['inventory']['parts'];self.assertTrue(all(isinstance(r['partNumber'],str) for r in rr));self.assertEqual(rr[0]['partNumber'],'338-001-906-0')
 def test_scope_of_cumulative_shop_visits(self):self.assertIn('cumulative',next(r for r in d['evidence'] if r['id']=='safran_additional')['unit'])
 def test_quote_not_labeled_consensus(self):self.assertIsNone(d['market']['consensus']);self.assertEqual(d['market']['localDate'],'2026-10-05')
if __name__=='__main__':unittest.main()
