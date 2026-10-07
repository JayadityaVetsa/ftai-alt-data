"""Cache additional public originals for the contract-coverage audit; no website writes."""
import json,hashlib,urllib.request,concurrent.futures
from pathlib import Path
R=Path(__file__).resolve().parents[1];P=R/'data/raw/gap_audit';P.mkdir(parents=True,exist_ok=True)
sources={
 'erock_prospectus':'https://www.sec.gov/Archives/edgar/data/2110029/000119312526265898/d12401d424b4.htm',
 'cipher_q1':'https://investors.cipherdigital.com/static-files/6e976283-0e50-4f21-ab70-d3c6d5f1275e',
 'tcdc_update':'https://www.newerainfra.ai/_resources/First%20Quarter%20FY26%20Business%20Update.pdf?v=052106',
 'saline_issue_brief':'https://www.michigan.gov/mpsc/-/media/Project/Websites/mpsc/consumer/info/briefs/Issue_Brief_U_21990_DTE_12_18_25-%28002%29.pdf?rev=380b26f1884f44cf95f0fbe40c214204',
 'va2_assessment':'https://www.deq.virginia.gov/home/showpublisheddocument/35701/639128956440930000',
 'frontier_datasheet':'https://vantage-dc.com/wp-content/uploads/2025/08/VDC_DataSheet_Frontier.pdf',
 'iren_10k':'https://www.sec.gov/Archives/edgar/data/1878848/000187884826000052/iren-20260630.htm',
 'apld_10k':'https://ir.applieddigital.com/sec-filings/all-sec-filings/content/0001144879-26-000048/apld-20260531.htm',
 'milam_project':'https://milamdc.com/',
 'iren_sw1_energized':'https://iren.gcs-web.com/news-releases/news-release-details/iren-announces-successful-energization-sweetwater-1',
}
def get(item):
 id,url=item
 try:
  req=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0 StudentResearch public-source audit'})
  with urllib.request.urlopen(req,timeout=15) as res:b=res.read(25_000_001)
  if len(b)>25_000_000:raise ValueError('Exceeded 25MB limit')
  file=P/(id+('.pdf' if b.startswith(b'%PDF') else '.html'));file.write_bytes(b)
  return dict(id=id,url=url,status='downloaded',bytes=len(b),sha256=hashlib.sha256(b).hexdigest(),path=str(file.relative_to(R)),accessed='2026-10-06')
 except Exception as e:return dict(id=id,url=url,status='failed',error=str(e)[:200],accessed='2026-10-06')
with concurrent.futures.ThreadPoolExecutor(max_workers=5) as pool:results=list(pool.map(get,sources.items()))
(R/'data/gap_audit_acquisition.json').write_text(json.dumps(results,indent=2)+'\n')
print(json.dumps([{k:v for k,v in x.items() if k in ['id','status','bytes','error']} for x in results]))
