import csv,json,unittest
from pathlib import Path
R=Path(__file__).resolve().parents[1];P=R/'public/data'
d=json.loads((P/'datacenters.json').read_text(encoding='utf-8'))
class CampusTests(unittest.TestCase):
 def test_fifty_unique_records(self):
  self.assertEqual(len(d['rows']),50);self.assertEqual(len({s['id'] for s in d['rows']}),50)
 def test_sources_and_dates(self):
  sources={s['id']:s for s in d['sources']};self.assertEqual(len(sources),len(d['sources']))
  for r in d['rows']:
   for s in r['sources']:self.assertIn(s,sources)
  for s in sources.values():
   if s['published']:self.assertLessEqual(s['published'][:10],d['asOf'])
 def test_csv_identity_and_capacity(self):
  with (P/'datacenter_announcements.csv').open(encoding='utf-8') as f:rows=list(csv.DictReader(f))
  self.assertEqual([r['id'] for r in rows],[r['id'] for r in d['rows']])
  for a,b in zip(rows,d['rows']):self.assertEqual(float(a['mw']) if a['mw'] else None,b['mw'])
 def test_unknown_supply_not_zero(self):
  for s in d['rows']:
   self.assertIsNone(s['verifiedOpenMw']);self.assertIsNone(s['durationMonths'])
  self.assertTrue(any(s['confirmedSupplyMw'] is None for s in d['rows']))
 def test_no_parent_double_count(self):
  ids={s['id'] for s in d['rows']};self.assertNotIn('sweetwater_total',ids)
  self.assertEqual(sum(s['mw'] for s in d['rows'] if s['id'] in ['iren_sw1','iren_sw2']),2000)
  self.assertTrue({'iren_childress','crusoe_childress'}<=ids)
 def test_scenario_exports_reconcile(self):
  for r in d['scenarios']:
   with (P/f"datacenter_{r['year']}_{r['scenario'].lower()}_model.csv").open(encoding='utf-8') as f:rows=list(csv.DictReader(f))
   self.assertAlmostEqual(sum(float(s['openMw']) for s in rows),r['openMw'])
   self.assertLessEqual(r['potentialFtaiUnits'],r['annualUnits'])
 def test_control_is_not_new_demand(self):
  s=next(s for s in d['rows'] if s['id']=='va2_control');self.assertFalse(s['modelEligible']);self.assertEqual(s['basis'],'generation');self.assertEqual(s['mw'],8*16.5)
 def test_local_geo_and_downloads(self):
  self.assertGreater((R/'public/geo/usa_110m.json').stat().st_size,10000)
  for file in ['datacenter_research_memo.md','datacenter_supplemental.csv','datacenter_sources.csv','datacenter_acquisition.json']:self.assertTrue((P/file).exists(),file)
if __name__=='__main__':unittest.main()
