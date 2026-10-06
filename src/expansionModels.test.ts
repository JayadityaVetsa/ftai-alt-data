import {describe,it,expect} from 'vitest';
import {demandHurdle} from './expansionModels';
describe('Accessible demand needed to absorb deliveries',()=>{
 it('converts 100 units into derated reserve-adjusted demand',()=>expect(demandHurdle(100,25,10,10).required).toBeCloseTo(8181.818));
 it('preserves unavailable finite demand at zero capture',()=>expect(demandHurdle(100,0,10,10).required).toBeNull());
 it('uses whole delivered units',()=>expect(demandHurdle(1.9,100,0,0).usable).toBe(25));
 it('does not produce capacity without units',()=>expect(demandHurdle(0,25,10,10).required).toBe(0));
});
import {gapModel,scaleModel,scaleDefaults,earningsHurdle,type GapInputs} from './expansionModels';
const p:GapInputs={loadMw:100,pue:1.2,isIt:true,phase:.5,gridMw:10,alternativeMw:5,competition:.2,capture:.5,derate:.1,spares:.1,unitMw:25,capacity:100,asp:6,need:'2027-07-01',grid:'2028-07-01',siteReady:'2027-09-01',equipmentReady:'2027-07-01',permit:true,gas:true,excluded:false};
describe('Dated customer opportunity',()=>{
 it('converts IT load and phase before subtracting supply',()=>expect(gapModel(p).shortfallMw).toBe(45));
 it('uses complete site readiness to shorten the bridge',()=>expect(gapModel(p).months).toBe(10));
 it('prices open MW-months and rounded reserve units consistently',()=>{const r=gapModel(p);expect(r.mwMonths).toBe(360);expect(r.units).toBe(1);expect(r.ftaiSales).toBe(6);});
 it('preserves unknown grid dates',()=>{const r=gapModel({...p,grid:''});expect(r.months).toBeNull();expect(r.units).toBeNull();});
 it('rejects invalid calendar dates',()=>expect(gapModel({...p,grid:'2028-02-31'}).months).toBeNull());
 it('retains technology exclusions even if scenarios assume permitting',()=>expect(gapModel({...p,excluded:true}).units).toBe(0));
 it('requires gas and primary air permission in the modeled feasibility gate',()=>expect(gapModel({...p,gas:false}).units).toBe(0));
 it('does not generate negative shortage from surplus power',()=>expect(gapModel({...p,gridMw:1000}).shortfallMw).toBe(0));
 it('caps potential sales by allocated annual production',()=>expect(gapModel({...p,loadMw:10000,capacity:2}).units).toBe(2));
 it('only counts whole allocated turbine outputs',()=>expect(gapModel({...p,loadMw:10000,capacity:2.5}).units).toBe(2));
 it('no bridge remains after late delivery',()=>expect(gapModel({...p,equipmentReady:'2029-01-01'}).units).toBe(0));
 it('keeps electrical loads separate from IT PUE',()=>expect(gapModel({...p,isIt:false}).electricalMw).toBe(50));
});
describe('Production and earnings feasibility',()=>{
 it('reports each bottleneck and minimum',()=>{const r=scaleModel(scaleDefaults);expect(r.achievable).toBe(102);expect(r.deliveries).toBe(100);expect(r.requiredCandidates).toBe(143);});
 it('does not report a fractional completed unit',()=>expect(scaleModel({...scaleDefaults,target:99.5}).deliveries).toBe(99));
 it('protects aviation allocation when module headroom is exhausted',()=>expect(scaleModel({...scaleDefaults,aviationModules:3000}).deliveries).toBe(0));
 it('does not confuse historical 60 modules with eligible cores',()=>expect(scaleModel({...scaleDefaults,candidates:0}).deliveries).toBe(0));
 it('limits output when packaging cannot keep pace',()=>expect(scaleModel({...scaleDefaults,packaging:50}).deliveries).toBe(42));
 it('counts start-up months in annual production',()=>expect(scaleModel({...scaleDefaults,rampMonths:12,rampMonthly:5}).deliveries).toBe(60));
 it('solves the contribution needed to reach the disclosed earnings benchmark',()=>{const r=earningsHurdle(450,100,30,1.2,6);expect(r.perUnit).toBeCloseTo(4.788);expect(r.margin).toBeCloseTo(.798);});
 it('undefined per-unit economics stay unavailable at zero volume',()=>expect(earningsHurdle(450,0,30,0,6).margin).toBeNull());
});
