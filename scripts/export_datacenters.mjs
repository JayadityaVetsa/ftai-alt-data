import fs from 'node:fs';
import {studyModel,capacityByBasis} from '../src/datacenterModels.ts';
const d=JSON.parse(fs.readFileSync('data/datacenter_study.json','utf8'));
const csv=(name,rows)=>{if(!rows.length)return;const keys=[...new Set(rows.flatMap(Object.keys))],q=v=>'"'+String(v===null?'':typeof v==='object'?JSON.stringify(v):v??'').replaceAll('"','""')+'"';fs.writeFileSync(`public/data/${name}`,[keys,...rows.map(r=>keys.map(k=>r[k]))].map(r=>r.map(q).join(',')).join('\r\n')+'\r\n');};
const results=[];for(const year of [2027,2028])for(const [name,phaseScale,competitorShare,capture,includeTiming] of [['Low',.6,.7,.1,false],['Base',1,.5,.25,true],['High',1.4,.3,.4,true]]){
 const p={...d.defaults,year,phaseScale,competitorShare,capture,includeTiming},r=studyModel(d.rows,p);
 results.push({scenario:name,...p,includedSites:r.included,potentialMw:r.potential,openMw:r.open,capturedMw:r.captured,marketMod1Equivalents:r.equivalents,potentialFtaiUnits:r.units,uncappedRequestedUnits:r.requested,requiredShareForAnnualCapacity:r.requiredShare});
 csv(`datacenter_${year}_${name.toLowerCase()}_model.csv`,r.rows);
}
d.scenarios=results;d.basisTotals=capacityByBasis(d.rows);d.base=studyModel(d.rows,d.defaults);
fs.writeFileSync('public/data/datacenters.json',JSON.stringify(d,null,2)+'\n');
csv('datacenter_announcements.csv',d.rows);csv('datacenter_sources.csv',d.sources);csv('datacenter_scenarios.csv',results);csv('datacenter_capacity_basis.csv',d.basisTotals);
csv('datacenter_supplemental.csv',d.supplemental);
if(fs.existsSync('data/datacenter_acquisition.json'))fs.copyFileSync('data/datacenter_acquisition.json','public/data/datacenter_acquisition.json');
console.log(JSON.stringify({records:d.rows.length,bases:d.basisTotals,base:{normalized:rnd(d.base.normalizedTotal),potential:rnd(d.base.potential),open:rnd(d.base.open),units:d.base.units,equivalents:d.base.equivalents,requiredShare:rnd(d.base.requiredShare)},scenarios:results},null,2));
function rnd(n){return n===null?null:Math.round(n*10000)/10000;}
