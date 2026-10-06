import {describe,it,expect} from 'vitest';
import {resolveRoute} from './Workspace';
describe('Existing links and new thesis routes',()=>{
 it('keeps customer and production links in Power',()=>{expect(resolveRoute('#customer-power-gaps').group).toBe('power');expect(resolveRoute('#production-readiness').group).toBe('power')});
 it('opens old valuation and engine tools in Other',()=>{expect(resolveRoute('#valuation')).toEqual({group:'other',tool:4});expect(resolveRoute('#engine-supply')).toEqual({group:'other',tool:3})});
 it('maps the old aviation cross-check to AP',()=>expect(resolveRoute('#aviation-resilience').group).toBe('ap'));
 it('keeps Power section jumps in Power and unknown links on a useful default',()=>{expect(resolveRoute('#power-hiring').group).toBe('power');expect(resolveRoute('#unrecognized').group).toBe('power')});
});
