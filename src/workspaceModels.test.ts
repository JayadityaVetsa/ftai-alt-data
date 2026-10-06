import {describe,it,expect} from 'vitest';
import forecasts from '../public/data/power_delivery_defaults.json';
import {apBridge,workloadMix,siteDemand,monthlyRamp,requiredStart,rampDefaults,type ApPeriod} from './workspaceModels';
const old:ApPeriod={quarter:'old',revenue:490.271,ebitda:164.864,products:420.686,mre:69.585,cogs:317.469,opex:8.989,modules:184,source:'s'};
const now:ApPeriod={quarter:'new',revenue:875.028,ebitda:249.716,products:692.229,mre:182.799,cogs:614.529,opex:10.997,modules:296,source:'s'};
describe('AP economics separate dollars from margins',()=>{
 it('reconciles the earnings bridge exactly',()=>{const r=apBridge(old,now);expect(old.ebitda+r.volume+r.residual).toBeCloseTo(now.ebitda,9)});
 it('computes segment gross profit and a percentage-point change',()=>{const r=apBridge(old,now);expect(r.newGross).toBeCloseTo(260.499);expect(r.grossGrowth).toBeCloseTo(.5074999);expect(r.marginPp).toBeCloseTo(-5.089058)});
 it('preserves unavailable component costs',()=>expect(apBridge({...old,cogs:null},now).grossGrowth).toBeNull());
 it('demonstrates percentage dilution at unchanged contribution per job',()=>{const a=workloadMix(.25,6,2.5,9,2.5,100),b=workloadMix(.65,6,2.5,9,2.5,100);expect(b.profit).toBe(a.profit);expect(b.margin!).toBeLessThan(a.margin!)});
 it('exposes deteriorating heavy-job contribution rather than hiding it',()=>expect(workloadMix(.65,6,2.5,9,1,100).profit).toBeLessThan(workloadMix(.65,6,2.5,9,2.5,100).profit));
});
describe('Quarterly ramp and acceptance',()=>{
 it('published default forecasts reconcile to the website calculator',()=>{const rows=forecasts;for(const row of rows){const r=monthlyRamp(row);expect(r.acceptedNov).toBe(row.acceptedNov);expect(r.accepted2027).toBe(row.accepted2027);expect(r.cash).toBeCloseTo(row.cash)}});
 it('starts October 2026 and ends March 2028',()=>{const r=monthlyRamp(rampDefaults);expect(r.months[0].month).toBe('2026-10');expect(r.months.at(-1)!.month).toBe('2028-03')});
 it('never accepts a unit before its production month plus lag',()=>{const r=monthlyRamp({...rampDefaults,acceptanceLag:2});expect(r.months[0].accepted).toBe(0);expect(r.months[1].accepted).toBe(0);r.months.slice(2).forEach((m,i)=>expect(m.accepted).toBe(r.months[i].produced))});
 it('produces and accepts whole units',()=>monthlyRamp(rampDefaults).months.forEach(m=>{expect(Number.isInteger(m.produced)).toBe(true);expect(Number.isInteger(m.accepted)).toBe(true)}));
 it('caps total successful output by candidates times yield',()=>{const r=monthlyRamp({...rampDefaults,candidates:10,yield:.7,startQuarter:100});expect(r.months.reduce((n,m)=>n+m.produced,0)).toBeLessThanOrEqual(7)});
 it('keeps cores nonnegative',()=>monthlyRamp({...rampDefaults,candidates:1}).months.forEach(m=>expect(m.coresRemaining).toBeGreaterThanOrEqual(0)));
 it('has no output without eligibility yield',()=>expect(monthlyRamp({...rampDefaults,yield:0}).accepted2027).toBe(0));
 it('reports November separately from full Q4',()=>{const r=monthlyRamp(rampDefaults);expect(r.acceptedNov).toBe(r.months.filter(m=>m.month<='2027-11').reduce((n,m)=>n+m.accepted,0))});
 it('separates FY2027 from cumulative including 2026',()=>{const r=monthlyRamp(rampDefaults);expect(r.accepted2027).toBe(r.months.filter(m=>m.month.startsWith('2027')).reduce((n,m)=>n+m.accepted,0))});
 it('does not pretend a starting-rate increase fixes zero packaging capacity',()=>expect(requiredStart({...rampDefaults,packagesPerQuarter:0})).toBeNull());
 it('required start reaches the target under ample feedstock',()=>{const p={...rampDefaults,candidates:1000};const start=requiredStart(p)!;expect(monthlyRamp({...p,startQuarter:start+1e-5}).accepted2027).toBeGreaterThanOrEqual(100)});
 it('does not add JV earnings to operating cash without distribution evidence',()=>{const a=monthlyRamp(rampDefaults),b=monthlyRamp({...rampDefaults,jvProfit:20});expect(b.attributable-a.attributable).toBe(20);expect(b.cash).toBe(a.cash)});
});
describe('Named-site demand',()=>{
 const sites=[{id:'m',loadMw:672,isIt:true,availableMw:0,included:true},{id:'f',loadMw:1400,isIt:true,availableMw:115,included:true}];
 const p={phase:.5,pue:1.2,competitorShare:.5,capture:.25,derate:.1,reserve:.1,months:12,capacity:100};
 it('converts the phased electrical load before deductions',()=>{const r=siteDemand(sites,p);expect(r.gross).toBeCloseTo(1128.2);expect(r.open).toBeCloseTo(564.1);expect(r.units).toBe(7)});
 it('does not create a negative gap with excess supply',()=>expect(siteDemand([{...sites[0],availableMw:10000}],p).open).toBe(0));
 it('excludes unavailable and selected competing projects from capture inputs',()=>expect(siteDemand(sites.map(s=>({...s,included:false})),p).units).toBe(0));
 it('caps units by allocated output and closes the gap at zero duration',()=>{expect(siteDemand(sites,{...p,capacity:3}).units).toBe(3);expect(siteDemand(sites,{...p,months:0}).units).toBe(0)});
});
