import csv,json,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];P=ROOT/'public/data';d=json.loads((P/'research.json').read_text(encoding='utf-8'))
class EvidenceTests(unittest.TestCase):
 def test_unique_projects(self): self.assertEqual(len(d['projects']),len({p['id'] for p in d['projects']}))
 def test_sources_resolve(self):
  ids={s['id'] for s in d['sources']}
  for row in d['projects']+d['facts']+d['translations']: self.assertIn(row['source'],ids)
 def test_capacity_funnel(self): self.assertEqual(d['coverage']['eligibleMw'],sum(p['mw'] for p in d['projects'] if p['eligible'] and p['mw'] is not None))
 def test_unknown_is_not_zero(self): self.assertTrue(any(p['mw'] is None for p in d['projects']))
 def test_csv_matches_json(self):
  with (P/'projects.csv').open(encoding='utf-8') as f: rows=list(csv.DictReader(f))
  self.assertEqual([r['id'] for r in rows],[r['id'] for r in d['projects']])
 def test_fleet_age_control(self):
  if d['fleet']['count'] is not None:self.assertEqual(sum(r['count'] for r in d['fleet']['age'])+d['fleet']['missingYear'],d['fleet']['count'])
 def test_eia_unique_generator_snapshot(self):
  rows=d['eia']['rows']; keys=[(r['snapshot'],r['plantId'],r['generatorId']) for r in rows]
  self.assertEqual(len(keys),len(set(keys)))
 def test_no_attributed_orders(self):self.assertEqual(d['coverage']['explicitFtaiSites'],0)
if __name__=='__main__':unittest.main()
