export type GapInputs={loadMw:number;pue:number;isIt:boolean;phase:number;gridMw:number;alternativeMw:number;competition:number;capture:number;derate:number;spares:number;unitMw:number;capacity:number;asp:number;need:string;grid:string;siteReady:string;equipmentReady:string;permit:boolean;gas:boolean;excluded:boolean};
const monthIndex=(s:string)=>{if(!/^\d{4}-\d{2}-\d{2}$/.test(s))return null;const [y,m,day]=s.split('-').map(Number);const d=new Date(Date.UTC(y,m-1,day));return d.getUTCFullYear()===y&&d.getUTCMonth()===m-1&&d.getUTCDate()===day?y*12+m-1:null;};
export function gapModel(p:GapInputs){
 const start=monthIndex(p.need),end=monthIndex(p.grid),site=monthIndex(p.siteReady),equipment=monthIndex(p.equipmentReady);
 const electricalMw=p.loadMw*(p.isIt?p.pue:1)*p.phase;
 const shortfallMw=Math.max(0,electricalMw-p.gridMw-p.alternativeMw);
 const openMw=shortfallMw*(1-p.competition);
 const ready=start===null||site===null||equipment===null?null:Math.max(start,site,equipment);
 const months=ready===null||end===null?null:Math.max(0,end-ready);
 const unitNetMw=p.unitMw*(1-p.derate);
 const fullRequirement=unitNetMw>0?Math.ceil(shortfallMw/unitNetMw*(1+p.spares)):null;
 const potential=unitNetMw>0?Math.ceil(openMw*p.capture/unitNetMw*(1+p.spares)):null;
 const permitted=p.permit&&p.gas&&!p.excluded;
 // Unknown dates produce unknown timing/output. A verified incompatible design is always excluded.
 const units=p.excluded||!permitted?0:months===null?null:months===0?0:potential===null?null:Math.min(Math.floor(p.capacity),potential);
 const timeline=[];
 if(start!==null&&end!==null&&end-start<=120&&end>=start){for(let m=start;m<end;m++)timeline.push({month:`${Math.floor(m/12)}-${String(m%12+1).padStart(2,'0')}`,shortfallMw,commissionable:ready!==null&&m>=ready,assumed:true});}
 return {electricalMw,shortfallMw,openMw,months,fullRequirement,units,feasibleMw:permitted?openMw:0,mwMonths:months===null?null:openMw*months,ftaiSales:units===null?null:units*p.asp,timeline};
}
export type ScaleInputs={target:number;candidates:number;yield:number;moduleCapacity:number;realization:number;aviationModules:number;slots:number;sharedEngineCapacity:number;powerShare:number;testing:number;packaging:number;rampMonths:number;rampMonthly:number;steadyMonthly:number};
export const scaleDefaults:ScaleInputs={target:100,candidates:200,yield:.7,moduleCapacity:3000,realization:.85,aviationModules:1700,slots:3,sharedEngineCapacity:650,powerShare:.25,testing:120,packaging:120,rampMonths:3,rampMonthly:5,steadyMonthly:12};
export function scaleModel(p:ScaleInputs){
 const feedstock=Math.floor(p.candidates*p.yield),moduleHeadroom=Math.max(0,p.moduleCapacity*p.realization-p.aviationModules);
 const moduleOutputs=p.slots>0?Math.floor(moduleHeadroom/p.slots):0,repair=Math.floor(p.sharedEngineCapacity*p.powerShare*p.realization),testing=Math.floor(p.testing*p.realization),packaging=Math.floor(p.packaging*p.realization);
 const rampMonths=Math.max(0,Math.min(12,Math.floor(p.rampMonths)));
 const ramp=Math.floor(rampMonths*p.rampMonthly+(12-rampMonths)*p.steadyMonthly);
 const constraints={feedstock,moduleOutputs,repair,testing,packaging,ramp};const achievable=Math.min(...Object.values(constraints));
 return {constraints,achievable,deliveries:Math.min(Math.floor(p.target),achievable),moduleHeadroom,requiredCandidates:p.yield>0?Math.ceil(p.target/p.yield):null,requiredMonthly:12-rampMonths>0?Math.max(0,(p.target-rampMonths*p.rampMonthly)/(12-rampMonths)):null,requiredModules:p.aviationModules+p.target*p.slots,expansionVsQ2RunRate:(p.aviationModules+p.target*p.slots)/(296*4)-1};
}
export function earningsHurdle(target:number,units:number,opex:number,otherProfit:number,asp:number){const gross=target+opex-otherProfit;return {gross,perUnit:units>0?gross/units:null,margin:units>0&&asp>0?gross/(units*asp):null};}
export function demandHurdle(units:number,capturePct:number,deratePct:number,reservePct:number){
 const usable=Math.floor(Math.max(0,units))*25*(1-Math.max(0,Math.min(100,deratePct))/100)/(1+Math.max(0,reservePct)/100);
 return {usable,required:capturePct>0?usable/(Math.min(100,capturePct)/100):null};
}
