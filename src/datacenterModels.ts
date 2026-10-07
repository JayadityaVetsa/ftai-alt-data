export type PowerStatus='procurement'|'timing'|'secured'|'selected'|'unknown'|'later';
export type Campus={id:string;name:string;developer:string;customer:string;place:string;state:string;lat:number|null;lon:number|null;mw:number|null;basis:string;readyWindow:string;firstYear:number|null;lastYear:number|null;status:PowerStatus;power:string;stage:string;sources:string[];confirmedSupplyMw:number|null;supplyMeaning:string;gridWindow:string;gas:string;permit:string;fit:string;modelEligible:boolean;phase2027:number;phase2028:number;bridgeFraction:number;deductMw:number;note:string;coordinateBasis:string;reviewed:string;durationMonths:number|null;verifiedOpenMw:number|null;regulatoryNote:string};
export type StudyInputs={year:number;pue:number;competitorShare:number;capture:number;phaseScale:number;includeTiming:boolean;derate:number;reserve:number;annualUnits:number};
export type StudySource={id:string;title:string;url:string;published:string|null;accessed:string;locator?:string;status?:string};
export type CampusStudy={asOf:string;scope:string;rows:Campus[];sources:StudySource[];defaults:StudyInputs;limitations:string[];previous:{openMw:number;sites:number;scope:string}};
const fraction=(v:number)=>Math.max(0,Math.min(1,v));
export function electricMw(s:Campus,pue:number):number|null{
 if(s.mw===null)return null;
 if(s.basis==='IT')return s.mw*Math.max(1,pue);
 return s.basis==='electrical'?s.mw:null;
}
export function campusModel(s:Campus,p:StudyInputs){
 const normalized=electricMw(s,p.pue),phase=fraction((p.year===2027?s.phase2027:s.phase2028)*Math.max(0,p.phaseScale));
 const included=s.modelEligible&&normalized!==null&&(s.status!=='timing'||p.includeTiming);
 const electrical=included?normalized!*phase:0;
 // A timing-risk fraction is applied BEFORE deducted supply. It is not a measured outage.
 const potential=included?Math.max(0,electrical*fraction(s.bridgeFraction)-Math.max(0,s.deductMw)):0;
 const competitor=potential*fraction(p.competitorShare),open=potential-competitor;
 return {id:s.id,name:s.name,status:s.status,normalizedMw:normalized,included,phase,electricalMw:electrical,bridgeFraction:s.bridgeFraction,deductMw:included?s.deductMw:0,potentialMw:potential,competingAssumedMw:competitor,openMw:open,capturedMw:open*fraction(p.capture),year:p.year,scenario:true,executionQualified:false};
}
export function studyModel(sites:Campus[],p:StudyInputs){
 const rows=sites.map(s=>campusModel(s,p));
 const total=(key:'electricalMw'|'potentialMw'|'competingAssumedMw'|'openMw'|'capturedMw')=>rows.reduce((n,r)=>n+r[key],0);
 const open=total('openMw'),captured=total('capturedMw');
 const usable=25*(1-fraction(p.derate))/(1+Math.max(0,p.reserve));
 const equivalents=usable>0?Math.ceil(open/usable):null,requested=usable>0?Math.ceil(captured/usable):null;
 const capacity=Math.max(0,Math.floor(p.annualUnits));
 return {rows,electrical:total('electricalMw'),potential:total('potentialMw'),competing:total('competingAssumedMw'),open,captured,usable,equivalents,requested,units:requested===null?null:Math.min(capacity,requested),capacity,requiredShare:open>0?capacity*usable/open:null,requiredOpenMw:p.capture>0?capacity*usable/fraction(p.capture):null,included:rows.filter(r=>r.included).length,normalizedTotal:sites.reduce((n,s)=>n+(electricMw(s,p.pue)??0),0)};
}
export function capacityByBasis(sites:Campus[]){return ['IT','electrical','generation','unspecified'].map(basis=>({basis,mw:sites.filter(s=>s.basis===basis).reduce((n,s)=>n+(s.mw??0),0),count:sites.filter(s=>s.basis===basis&&s.mw!==null).length}));}
