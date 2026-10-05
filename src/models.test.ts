import {describe,it,expect} from 'vitest';
import {deployment,deploymentDefaults,engine,engineDefaults,power,powerDefaults,valuation,valuationDefaults} from './models';
describe('Customer economics',()=>{
 it('converts Btu/kWh and USD/MMBtu to USD/MWh',()=>{expect(deployment({...deploymentDefaults,heat:10000,gas:4,maintenance:0}).fastCost).toBe(40);});
 it('does not treat equipment arrival as commissioning',()=>{const r=deployment({...deploymentDefaults,fastMonths:2,slowMonths:12,readinessMonths:20});expect(r.fast).toBe(20);expect(r.slow).toBe(20);expect(r.breakEven).toBeNull();});
 it('redundancy and derating reduce usable load',()=>{expect(deployment({...deploymentDefaults,mw:110,derate:0.1,redundancy:0.1}).usable).toBeCloseTo(90);});
 it('equal technology and equal timing produce equal NPVs',()=>{const p={...deploymentDefaults,slowMonths:6,competitorCapexPerMw:0.85,competitorControlPerMw:0.08,competitorMaintenance:8,competitorHeat:11000};const r=deployment(p);expect(r.npv[0]).toBeCloseTo(r.npv[1]);});
 it('break-even contribution makes the two alternatives indifferent',()=>{const first=deployment(deploymentDefaults);const r=deployment({...deploymentDefaults,contribution:first.breakEven!});expect(r.advantage).toBeCloseTo(0,4);});
 it('higher gas price raises break-even when assumed Mod-1 is less efficient',()=>{expect(deployment({...deploymentDefaults,gas:8}).breakEven!).toBeGreaterThan(deployment({...deploymentDefaults,gas:2}).breakEven!);});
 it('no operating utilization leaves the threshold unavailable',()=>{expect(deployment({...deploymentDefaults,utilization:0}).breakEven).toBeNull();});
});
describe('Engine allocation',()=>{
 it('charges unsuccessful acquisition cost to successful output',()=>{const r=engine({...engineDefaults,acquisition:2,yield:0.5});expect(r.feedstockCost).toBe(4);});
 it('does not convert the installed population directly into units',()=>{expect(engine({...engineDefaults,eligible:10,yield:0.65}).output).toBe(6);});
 it('the packaging bottleneck limits output',()=>{expect(engine({...engineDefaults,packageCapacity:20}).output).toBe(20);});
 it('measures incremental value over the best alternative',()=>{const r=engine(engineDefaults);expect(r.incremental).toBeCloseTo(0.757142857);});
});
describe('Power earnings and cash',()=>{
 it('uses independent turbine ASP instead of entire JV order',()=>{const r=power(powerDefaults);expect(r.turbineRevenue).toBe(480);expect(r.turbineRevenue).not.toBe(powerDefaults.order);});
 it('leaves unknown JV attribution at zero',()=>{expect(power(powerDefaults).packaging).toBe(0);});
 it('does not tax a loss into a positive cash credit',()=>{expect(power({...powerDefaults,units:0,serviceUnits:0}).taxes).toBe(0);});
 it('separates equipment collections from operating revenue',()=>{const r=power({...powerDefaults,advance:30});expect(r.turbineRevenue).toBe(480);expect(r.operatingFcf-power(powerDefaults).operatingFcf).toBe(30);});
 it('JV milestone collections reconcile to the disclosed order',()=>{expect(power(powerDefaults).jvCash.reduce((a,b)=>a+b,0)).toBeCloseTo(1465);});
 it('constrains requested deliveries by qualifying feedstock',()=>{expect(power({...powerDefaults,eligible:50,yield:0.6}).deliveries).toBe(30);});
});
describe('Valuation bridge',()=>{
 it('subtracts consolidated debt and preferred once',()=>{const v={...valuationDefaults,aerospace:0,leasingEv:0,sciEquity:0,corporateCost:0,debt:100,cash:10,preferred:20,shares:10};expect(valuation(v,0).target).toBe(-11);});
 it('does not fabricate a market comparison without a quote',()=>{expect(valuation(valuationDefaults,100).requiredPowerEv).toBeNull();});
 it('reverse valuation reconciles at scenario per-share value',()=>{const r=valuation(valuationDefaults,100);expect(valuation({...valuationDefaults,price:r.target},100).requiredPowerEbitda).toBeCloseTo(100);});
});
