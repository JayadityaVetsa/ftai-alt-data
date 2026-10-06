export type ApPeriod={quarter:string;revenue:number;ebitda:number;products:number|null;mre:number|null;cogs:number|null;opex:number|null;modules:number;source:string};
export function apBridge(a:ApPeriod,b:ApPeriod){
 const oldMargin=a.ebitda/a.revenue,newMargin=b.ebitda/b.revenue,volume=(b.revenue-a.revenue)*oldMargin,residual=b.ebitda-b.revenue*oldMargin;
 const oldGross=a.cogs===null?null:a.revenue-a.cogs,newGross=b.cogs===null?null:b.revenue-b.cogs;
 return {oldMargin,newMargin,marginPp:(newMargin-oldMargin)*100,volume,residual,earningsGrowth:b.ebitda/a.ebitda-1,revenueGrowth:b.revenue/a.revenue-1,grossGrowth:oldGross===null||newGross===null?null:newGross/oldGross-1,oldGross,newGross,incrementalMargin:(b.ebitda-a.ebitda)/(b.revenue-a.revenue),oldOverhead:a.opex===null?null:a.opex/a.revenue,newOverhead:b.opex===null?null:b.opex/b.revenue};
}
export function workloadMix(heavyShare:number,lightSale:number,lightProfit:number,heavySale:number,heavyProfit:number,jobs:number){
 const share=Math.max(0,Math.min(1,heavyShare)),sales=(1-share)*lightSale+share*heavySale,profit=(1-share)*lightProfit+share*heavyProfit;
 return {salesPerJob:sales,profitPerJob:profit,margin:sales>0?profit/sales:null,revenue:sales*jobs,profit:profit*jobs};
}
export type SiteScenario={id:string;loadMw:number;isIt:boolean;availableMw:number;included:boolean};
export type DemandInputs={phase:number;pue:number;competitorShare:number;capture:number;derate:number;reserve:number;months:number;capacity:number};
export function siteDemand(sites:SiteScenario[],p:DemandInputs){
 const rows=sites.filter(s=>s.included).map(s=>{const electrical=s.loadMw*(s.isIt?p.pue:1)*p.phase;const gap=Math.max(0,electrical-s.availableMw);const open=gap*(1-p.competitorShare);return {id:s.id,electrical,gap,open,mwMonths:open*p.months};});
 const gross=rows.reduce((n,r)=>n+r.gap,0),open=rows.reduce((n,r)=>n+r.open,0),captured=open*p.capture,net=25*(1-p.derate);
 const units=p.months>0&&net>0?Math.ceil(captured/net*(1+p.reserve)):0;
 return {rows,gross,open,captured,mwMonths:open*p.months,units:Math.min(units,Math.floor(p.capacity)),marketUnits:net>0?Math.ceil(open/net*(1+p.reserve)):0};
}
export type RampInputs={startQuarter:number;growth:number;yield:number;candidates:number;replenishPerQuarter:number;conversionPerQuarter:number;testsPerQuarter:number;packagesPerQuarter:number;aviationCapacityPerQuarter:number;acceptanceLag:number;unitPrice:number;unitMargin:number;serviceProfit:number;jvProfit:number;opex:number;capex:number;workingCapital:number;tax:number};
export const rampDefaults:RampInputs={startQuarter:15,growth:.15,yield:.7,candidates:200,replenishPerQuarter:0,conversionPerQuarter:30,testsPerQuarter:25.5,packagesPerQuarter:25.5,aviationCapacityPerQuarter:34.5,acceptanceLag:1,unitPrice:6,unitMargin:.35,serviceProfit:1.2,jvProfit:0,opex:30,capex:80,workingCapital:40,tax:.2};
export function monthlyRamp(p:RampInputs){
 let cores=Math.max(0,p.candidates),carry=0;const months:{month:string;quarter:string;plan:number;produced:number;accepted:number;coresRemaining:number;binding:string}[]=[];
 for(let i=0;i<18;i++){
  const y=2026+Math.floor((9+i)/12),m=(9+i)%12+1,q=Math.floor(i/3),quarter=`Q${Math.floor((m-1)/3)+1} ${y}`;
  if(i>0&&i%3===0)cores+=Math.max(0,p.replenishPerQuarter);
  const plan=p.startQuarter*Math.pow(1+p.growth,q)/3;
  const constraints={ramp:plan,conversion:p.conversionPerQuarter/3,testing:p.testsPerQuarter/3,packaging:p.packagesPerQuarter/3,aviation:p.aviationCapacityPerQuarter/3,feedstock:cores*p.yield};
  const binding=Object.entries(constraints).sort((a,b)=>a[1]-b[1])[0][0],capacity=Math.max(0,Math.min(...Object.values(constraints)));
  const produced=Math.min(Math.floor(cores*p.yield+1e-8),Math.floor(capacity+carry+1e-8));
  // Fractional planning slots carry forward; feedstock remains a hard physical cap.
  carry=Math.max(0,Math.min(.999999,capacity+carry-produced));
  cores=Math.max(0,cores-(p.yield>0?produced/p.yield:0));
  const lag=Math.max(0,Math.floor(p.acceptanceLag));const accepted=lag===0?produced:i>=lag?months[i-lag].produced:0;
  months.push({month:`${y}-${String(m).padStart(2,'0')}`,quarter,plan,produced,accepted,coresRemaining:cores,binding});
 }
 const quarters=[...new Set(months.map(m=>m.quarter))].map(quarter=>{const rows=months.filter(m=>m.quarter===quarter);return {quarter,produced:rows.reduce((n,r)=>n+r.produced,0),accepted:rows.reduce((n,r)=>n+r.accepted,0),binding:[...new Set(rows.map(r=>r.binding))].join(', ')};});
 const acceptedNov=months.filter(m=>m.month<='2027-11').reduce((n,m)=>n+m.accepted,0),acceptedHorizon=months.filter(m=>m.month<='2027-10').reduce((n,m)=>n+m.accepted,0),accepted2027=months.filter(m=>m.month.startsWith('2027')).reduce((n,m)=>n+m.accepted,0);
 const revenue=accepted2027*p.unitPrice,turbineProfit=revenue*p.unitMargin,operating=turbineProfit+p.serviceProfit-p.opex,attributable=operating+p.jvProfit,cash=operating-Math.max(0,operating)*p.tax-p.capex-p.workingCapital;
 return {months,quarters,acceptedNov,acceptedHorizon,accepted2027,revenue,turbineProfit,operating,attributable,cash};
}
export function requiredStart(p:RampInputs,target=100){
 if(monthlyRamp({...p,startQuarter:500}).accepted2027<target)return null;
 let lo=0,hi=500;for(let i=0;i<30;i++){const mid=(lo+hi)/2;if(monthlyRamp({...p,startQuarter:mid}).accepted2027>=target)hi=mid;else lo=mid;}
 return hi;
}
