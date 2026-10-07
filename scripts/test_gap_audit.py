import json,csv,unittest
from pathlib import Path
R=Path(__file__).resolve().parents[1];d=json.loads((R/'data/power_gap_audit.json').read_text(encoding='utf-8'))
class GapAuditTests(unittest.TestCase):
 def test_all_records_accounted(self):
  self.assertEqual(len(d['rows']),50);self.assertEqual(len({r['id'] for r in d['rows']}),50);self.assertEqual(sum(d['coverage'].values()),50)
 def test_bounds_reconcile(self):
  s=d['summary'];self.assertEqual(s['records'],24);self.assertEqual(s['positiveCeilingRecords'],12)
  self.assertAlmostEqual(s['electricalScopeMw'],18560);self.assertAlmostEqual(s['creditedSupplyMw'],9379);self.assertAlmostEqual(s['conditionalAllocationCeilingMw'],9181)
  self.assertAlmostEqual(sum(r['contractCoverageCeilingMw'] or 0 for r in d['rows']),9181)
 def test_unknowns_not_zero(self):
  self.assertEqual(sum(r['boundInclusionReason']=='Load MW missing' for r in d['rows']),16)
  self.assertTrue(all(r['contractCoverageCeilingMw'] is None for r in d['rows'] if not r['boundIncluded']))
  self.assertIsNone(d['fullFiftyGapUpperMw']);self.assertTrue(all(r['actualGapUpperMw'] is None for r in d['rows']))
 def test_no_ftai_or_competition_haircut(self):
  for key in ['ftaiCaptureApplied','competitionHaircutApplied','phaseHaircutApplied']:self.assertFalse(d[key])
 def test_horizon_and_units(self):
  r={r['id']:r for r in d['rows']};self.assertEqual(r['ms_abilene']['mw'],672);self.assertEqual(r['ms_abilene']['basis'],'IT');self.assertEqual(r['muskie']['mw'],500);self.assertEqual(r['justified']['creditedSupplyMw'],482)
  self.assertFalse(r['tcdc']['boundIncluded']);self.assertFalse(r['va2_control']['boundIncluded'])
 def test_old_exclusions_and_bridge_dedup(self):
  self.assertEqual(d['originalExclusions']['total'],46);self.assertEqual(d['originalExclusions']['byStatus']['unknown'],13);self.assertEqual(d['documentedPurchasedBridgeMw'],366)
 def test_exports_match(self):
  with (R/'data/power_gap_audit.csv').open(encoding='utf-8-sig') as f:rows=list(csv.DictReader(f))
  self.assertEqual([r['id'] for r in rows],[r['id'] for r in d['rows']]);self.assertAlmostEqual(sum(float(r['contractCoverageCeilingMw'] or 0) for r in rows),9181)
if __name__=='__main__':unittest.main()
