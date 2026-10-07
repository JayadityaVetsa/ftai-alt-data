import {describe,it,expect} from 'vitest';
import data from '../public/data/datacenters.json';
import {electricMw,campusModel,studyModel,capacityByBasis,type CampusStudy} from './datacenterModels';
const d=data as unknown as CampusStudy,p=d.defaults;
describe('data-center addressability model',()=>{
 it('keeps generation and unresolved MW out of electrical demand',()=>{for(const s of d.rows.filter(s=>!['IT','electrical'].includes(s.basis)))expect(electricMw(s,1.2)).toBeNull();});
 it('normalizes IT once and preserves electrical ratings',()=>{const s=d.rows.find(s=>s.id==='frontier')!;expect(electricMw(s,1.2)).toBe(1680);expect(electricMw(d.rows[0],1.2)).toBe(900);});
 it('deducts available Frontier power after phasing, without negative gaps',()=>{const s=d.rows.find(s=>s.id==='frontier')!;expect(campusModel(s,p).potentialMw).toBe(1145);expect(campusModel(s,{...p,phaseScale:0}).potentialMw).toBe(0);});
 it('reconciles the default model and all site contributions',()=>{const r=studyModel(d.rows,p);expect(r.normalizedTotal).toBeCloseTo(21291.6);expect(r.open).toBeCloseTo(1112.945);expect(r.included).toBe(4);expect(r.units).toBe(14);expect(r.equivalents).toBe(55);expect(r.requiredOpenMw).toBeCloseTo(8181.8181818);expect(r.rows.reduce((n,s)=>n+s.openMw,0)).toBeCloseTo(r.open);});
 it('does not silently include contracted utility timing cases',()=>{const r=studyModel(d.rows,{...p,includeTiming:false});expect(r.included).toBe(2);expect(r.rows.filter(s=>s.status==='timing').every(s=>s.openMw===0)).toBe(true);});
 it('handles zero capture and zero capacity',()=>{expect(studyModel(d.rows,{...p,capture:0}).units).toBe(0);expect(studyModel(d.rows,{...p,capture:0}).requiredOpenMw).toBeNull();expect(studyModel(d.rows,{...p,annualUnits:0}).units).toBe(0);});
 it('caps physical units without pretending the captured MW were delivered',()=>{const r=studyModel(d.rows,{...p,capture:1,competitorShare:0,annualUnits:10});expect(r.units).toBe(10);expect(r.requested).toBeGreaterThan(10);});
 it('clamps phases, competition and capture to physical fractions',()=>{const r=studyModel(d.rows,{...p,phaseScale:20,competitorShare:2,capture:2});expect(r.open).toBe(0);expect(r.rows.every(s=>s.phase<=1)).toBe(true);});
 it('marks degenerate usable capacity unavailable',()=>{const r=studyModel(d.rows,{...p,derate:1});expect(r.equivalents).toBeNull();expect(r.units).toBeNull();});
 it('retains four separate capacity bases',()=>{expect(capacityByBasis(d.rows).map(s=>s.basis)).toEqual(['IT','electrical','generation','unspecified']);});
});
