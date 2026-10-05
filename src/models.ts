/** Monetary inputs use USD millions unless a label explicitly says otherwise. */
export type Deployment = {mw:number;derate:number;availability:number;utilization:number;gas:number;heat:number;competitorHeat:number;maintenance:number;competitorMaintenance:number;capexPerMw:number;competitorCapexPerMw:number;controlPerMw:number;competitorControlPerMw:number;redundancy:number;fastMonths:number;slowMonths:number;readinessMonths:number;years:number;discount:number;contribution:number;gridMonths:number;gridRate:number};
export const deploymentDefaults:Deployment={mw:100,derate:0.1,availability:0.95,utilization:0.85,gas:4,heat:11000,competitorHeat:8669,maintenance:8,competitorMaintenance:6,capexPerMw:0.85,competitorCapexPerMw:0.9,controlPerMw:0.08,competitorControlPerMw:0.08,redundancy:0.1,fastMonths:6,slowMonths:18,readinessMonths:4,years:5,discount:0.1,contribution:100000,gridMonths:24,gridRate:80};
export function deployment(p:Deployment){
 const fast=Math.max(p.fastMonths,p.readinessMonths),slow=Math.max(p.slowMonths,p.readinessMonths),grid=Math.max(p.gridMonths,p.readinessMonths);
 const usable=p.mw*(1-p.derate)/(1+p.redundancy), hours=8760*p.availability*p.utilization, mwh=usable*hours;
 const fastCost=p.gas*p.heat/1000+p.maintenance,slowCost=p.gas*p.competitorHeat/1000+p.competitorMaintenance;
 const fastCapex=p.mw*(p.capexPerMw+p.controlPerMw),slowCapex=p.mw*(p.competitorCapexPerMw+p.competitorControlPerMw);
 // Monthly discounted cash costs and energized MW-months over a common horizon.
 let fastPv=0,slowPv=0,gridPv=0,fastMwMonths=0,slowMwMonths=0,gridMwMonths=0;
 for(let m=1;m<=Math.round(p.years*12);m++){
  const df=(1+p.discount)**(-m/12);
  if(m===Math.max(1,Math.ceil(fast)))fastPv+=fastCapex*1e6*df;
  if(m===Math.max(1,Math.ceil(slow)))slowPv+=slowCapex*1e6*df;
  if(m>fast){fastPv+=mwh/12*fastCost*df;fastMwMonths+=usable*p.availability*p.utilization*df;}
  if(m>slow){slowPv+=mwh/12*slowCost*df;slowMwMonths+=usable*p.availability*p.utilization*df;}
  if(m>grid){gridPv+=mwh/12*p.gridRate*df;gridMwMonths+=usable*p.availability*p.utilization*df;}
 }
 const extra=fastMwMonths-slowMwMonths,gridExtra=fastMwMonths-gridMwMonths;
 return {fast,slow,grid,usable,mwh,fastCost,slowCost,fastCapex,slowCapex,fastPv,slowPv,gridPv,extra,breakEven:extra>0?Math.max(0,(fastPv-slowPv)/extra):null,gridBreakEven:gridExtra>0?Math.max(0,(fastPv-gridPv)/gridExtra):null,advantage:extra*p.contribution-(fastPv-slowPv),npv:[fastMwMonths*p.contribution-fastPv,slowMwMonths*p.contribution-slowPv,gridMwMonths*p.contribution-gridPv]};
}
export type Engine = {sale:number;acquisition:number;conversion:number;testing:number;workingCapital:number;yield:number;aviationNpv:number;parts:number;maintenanceNpv:number;eligible:number;repairCapacity:number;packageCapacity:number;target:number};
export const engineDefaults:Engine={sale:6,acquisition:1.5,conversion:2,testing:0.3,workingCapital:0.2,yield:0.7,aviationNpv:2.5,parts:1.6,maintenanceNpv:0.4,eligible:200,repairCapacity:150,packageCapacity:100,target:100};
export function engine(p:Engine){
 const feedstockCost=p.acquisition/p.yield;
 const conversionValue=p.sale+p.maintenanceNpv-feedstockCost-p.conversion-p.testing-p.workingCapital;
 const aviationValue=p.aviationNpv-p.acquisition,partsValue=p.parts-p.acquisition;
 const bestAlternative=Math.max(aviationValue,partsValue);
 return {feedstockCost,conversionValue,aviationValue,partsValue,incremental:conversionValue-bestAlternative,output:Math.min(Math.floor(p.eligible*p.yield),p.repairCapacity,p.packageCapacity,p.target),feedstockNeeded:Math.ceil(p.target/p.yield)};
}
export type Power={units:number;capacity:number;eligible:number;yield:number;asp:number;margin:number;packagingProfit:number;jvShare:number;serviceUnits:number;serviceRevenue:number;serviceMargin:number;opex:number;tax:number;capex:number;workingCapital:number;advance:number;advanceReleased:number;depreciation:number;inHorizon:number;deliveryPenalty:number;performancePenalty:number;order:number;advancePct:number;productionPct:number};
export const powerDefaults:Power={units:80,capacity:100,eligible:200,yield:0.7,asp:6,margin:0.35,packagingProfit:0,jvShare:0,serviceUnits:20,serviceRevenue:0.15,serviceMargin:0.4,opex:30,tax:0.2,capex:80,workingCapital:40,advance:0,advanceReleased:0,depreciation:10,inHorizon:0.65,deliveryPenalty:0,performancePenalty:0,order:1465,advancePct:0.15,productionPct:0.65};
export function power(p:Power){
 const deliveries=Math.min(p.units,p.capacity,Math.floor(p.eligible*p.yield)), turbineRevenue=deliveries*p.asp;
 const profit=turbineRevenue*p.margin-turbineRevenue*(p.deliveryPenalty+p.performancePenalty);
 const packaging=p.packagingProfit*p.jvShare, service=p.serviceUnits*p.serviceRevenue*p.serviceMargin;
 const operatingEbitda=profit+service-p.opex, attributable=operatingEbitda+packaging;
 const taxes=Math.max(0,operatingEbitda-p.depreciation)*p.tax;
 const operatingFcf=operatingEbitda-taxes-p.capex-p.workingCapital+p.advance-p.advanceReleased;
 return {deliveries,turbineRevenue,profit,packaging,service,operatingEbitda,attributable,taxes,operatingFcf,horizonContribution:attributable*p.inHorizon,jvCash:[p.order*p.advancePct,p.order*p.productionPct,p.order*(1-p.advancePct-p.productionPct)]};
}
export type Valuation={aerospace:number;aerospaceMultiple:number;leasingEv:number;sciEquity:number;powerMultiple:number;corporateCost:number;corporateMultiple:number;debt:number;cash:number;preferred:number;shares:number;price:number|null};
export const valuationDefaults:Valuation={aerospace:1300,aerospaceMultiple:16,leasingEv:1500,sciEquity:401.803,powerMultiple:14,corporateCost:50,corporateMultiple:12,debt:3496.38,cash:337.195,preferred:65,shares:104.044113,price:null};
export function valuation(v:Valuation,powerEbitda:number){
 const aerospaceEv=v.aerospace*v.aerospaceMultiple, powerEv=powerEbitda*v.powerMultiple,corporateEv=v.corporateCost*v.corporateMultiple;
 const equity=aerospaceEv+v.leasingEv+v.sciEquity+powerEv-corporateEv-v.debt+v.cash-v.preferred;
 const requiredPowerEv=v.price===null?null:v.price*v.shares+v.debt-v.cash+v.preferred-aerospaceEv-v.leasingEv-v.sciEquity+corporateEv;
 return {aerospaceEv,powerEv,corporateEv,equity,target:equity/v.shares,requiredPowerEv,requiredPowerEbitda:requiredPowerEv===null?null:requiredPowerEv/v.powerMultiple,upside:v.price===null?null:equity/v.shares/v.price-1};
}
