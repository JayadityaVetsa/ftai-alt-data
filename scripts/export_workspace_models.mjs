import {writeFile} from 'node:fs/promises';
import {monthlyRamp,rampDefaults,requiredStart} from '../src/workspaceModels.ts';
const dir=new URL('../public/data/',import.meta.url);
const rows=[],months=[],inputs=[];
for(const [scenario,startQuarter,growth,acceptanceLag] of [['Slow',10,.1,2],['Base',15,.15,1],['Fast',20,.2,0]]){
 const p={...rampDefaults,startQuarter,growth,acceptanceLag},r=monthlyRamp(p);
 rows.push({scenario,acceptedNov:r.acceptedNov,accepted2027:r.accepted2027,revenue:r.revenue,attributable:r.attributable,cash:r.cash,requiredStartingQuarter:requiredStart(p),basis:'Team scenario; not observed output',...p});
 months.push(...r.months.map(m=>({scenario,...m,basis:'Team scenario; not reported units'})));
 inputs.push({scenario,...p,unit:'USD million except units, fractions and month lag'});
}
async function csv(name,rows){const keys=[...new Set(rows.flatMap(Object.keys))],q=v=>'"'+String(v??'').replaceAll('"','""')+'"';await writeFile(new URL(name,dir),[keys,...rows.map(r=>keys.map(k=>r[k]))].map(row=>row.map(q).join(',')).join('\r\n')+'\r\n');}
await csv('power_delivery_scenarios.csv',rows);await csv('power_monthly_defaults.csv',months);await csv('model_assumptions.csv',inputs);
await writeFile(new URL('power_delivery_defaults.json',dir),JSON.stringify(rows,null,2)+'\n');
console.log('Published default scenario tables from the website model functions');
