import json,csv,unittest,xml.etree.ElementTree as ET
from pathlib import Path
R=Path(__file__).resolve().parents[1];P=R/'public/data'
d=json.loads((R/'data/power_gap_audit.json').read_text(encoding='utf-8'))
class PublicationTests(unittest.TestCase):
 def test_published_inputs_match(self):
  for name in ['power_gap_audit.json','power_gap_audit.csv','power_gap_audit_notes.json','gap_audit_acquisition.json']:
   self.assertEqual((R/'data'/name).read_bytes(),(P/name).read_bytes())
 def test_bridge_chart_reconciles(self):
  with (P/'power_gap_bridge.csv').open(encoding='utf-8-sig') as f:r=list(csv.DictReader(f))
  values=[float(v['mw']) for v in r];self.assertEqual(values,[18560,9379,9181]);self.assertEqual(values[0]-values[1],values[2])
 def test_twelve_case_chart_reconciles(self):
  with (P/'power_gap_ceiling_cases.csv').open(encoding='utf-8-sig') as f:r=list(csv.DictReader(f))
  self.assertEqual(len(r),12);self.assertAlmostEqual(sum(float(v['ceilingMw']) for v in r),9181)
 def test_exclusion_chart_accounts_fifty(self):
  with (P/'power_gap_coverage.csv').open(encoding='utf-8-sig') as f:r=list(csv.DictReader(f))
  self.assertEqual(sum(int(v['records']) for v in r),50)
 def test_source_native_image_has_units_and_limits(self):
  svg=ET.parse(R/'public/graphics/power-gap-audit.svg');text=' '.join(svg.getroot().itertext())
  for term in ['9.18','9.38','18.56','366 MW','not a verified shortage','26 held out']:self.assertIn(term,text)
  self.assertTrue((R/'public/graphics/power-gap-audit.png').stat().st_size>10000)
 def test_memo_and_current_page_use_new_audit(self):
  self.assertEqual((P/'power_gap_audit_memo.md').read_bytes(),(R/'research/power-gap-audit-2026-10-06.md').read_bytes())
  source=(R/'src/Workspace.tsx').read_text(encoding='utf-8');self.assertIn('<PowerGapAudit/>',source);self.assertNotIn('<DataCenterStudy/>',source);self.assertNotIn('defaultStudyResult',source)
 def test_all_sources_have_readable_metadata(self):
  index=json.loads((P/'power_gap_source_index.json').read_text(encoding='utf-8'))
  for row in d['rows']:
   for url in row['sourceUrls']:self.assertIn(url,index);self.assertTrue(index[url]['title']);self.assertTrue(index[url]['locator'])
if __name__=='__main__':unittest.main()
