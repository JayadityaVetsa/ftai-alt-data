import csv,json,unittest
from pathlib import Path
P=Path(__file__).resolve().parents[1]/'public/data';d=json.loads((P/'workspace.json').read_text(encoding='utf-8'))
class WorkspaceTests(unittest.TestCase):
 def test_sources_resolve(self):
  ids={s['id'] for s in d['sources']}
  for group in ['ap','hiring','suppliers','sci','cashFacts']:
   for r in d[group]:self.assertIn(r['source'],ids)
  for r in d['lifecycle']+d['findings']:
   for s in r['sources']:self.assertIn(s,ids)
 def test_ap_total_and_scope(self):
  for r in d['ap']:
   if r['products'] is not None:self.assertAlmostEqual(r['products']+r['mre'],r['revenue'],places=6)
  self.assertAlmostEqual(d['ap'][-1]['grossProfit'],260.499)
 def test_bridge_reconciles(self):
  self.assertAlmostEqual(d['ap'][0]['ebitda']+d['apBridge']['volume']+d['apBridge']['residual'],d['ap'][-1]['ebitda'],places=8)
 def test_sci_no_subset_double_count(self):
  self.assertEqual(sum(s['aircraft'] for s in d['sci']),27);self.assertEqual(sum(s['engineExposure'] for s in d['sci']),54)
  self.assertTrue(all(s['capital'] is None for s in d['sci']))
 def test_no_acceptance_invented(self):
  self.assertEqual(d['lifecycleAcquisition']['eiaIdentityMatchedUnits'],0)
  self.assertIsNone(d['lifecycleAcquisition']['epaMatchedTests'])
 def test_expired_role_not_counted_current(self):self.assertFalse(next(j for j in d['hiring'] if j['id']=='4432280973')['current'])
 def test_hiring_dates_have_specific_metadata_basis(self):
  for j in d['hiring']:
   if j['posted']:self.assertIn('JSON-LD',j['dateBasis'])
 def test_explicit_5b_refs_not_full_engines(self):
  self.assertEqual(next(r for r in d['inventory']['familyDonors'] if r['family']=='CFM56-5B')['donorReferences'],9)
  self.assertEqual(d['inventory']['summary']['completeEngineRows'],0)
 def test_preset_arithmetic(self):
  r=d['demandPresets'][1];self.assertAlmostEqual(r['openMw'],564.1);self.assertEqual(r['units'],7)
 def test_downloaded_scorecard_matches_site(self):
  with (P/'ap_scorecard.csv').open(encoding='utf-8') as f:rows=list(csv.DictReader(f))
  self.assertEqual(len(rows),len(d['ap']));self.assertEqual(float(rows[-1]['revenue']),d['ap'][-1]['revenue'])
 def test_unique_sources_and_jobs(self):
  self.assertEqual(len(d['sources']),len({s['id'] for s in d['sources']}));self.assertEqual(len(d['hiring']),len({j['id'] for j in d['hiring']}))
if __name__=='__main__':unittest.main()
