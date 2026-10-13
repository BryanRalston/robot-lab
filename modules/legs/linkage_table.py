"""ONE non-overlapping leg linkage table (R-013), Legs + Actuators. Reads Actuators' CAD masses (modules/actuators/results/cad_mass.json, read-only)
and evaluates Actuators' own lever() CadQuery solid at the thigh-mounted spacing dy=69 mm (DECISIONS L10). Writes LINKAGE_TABLE.md/.json in modules/legs/."""
import json,os
H=os.path.dirname(os.path.abspath(__file__)); A=os.path.join(H,'..','actuators')
C=json.load(open(os.path.join(A,'results','cad_mass.json')))
src=open(os.path.join(A,'cad_mass.py')).read(); g={'__file__':os.path.join(A,'cad_mass.py'),'__name__':'x'}; exec(src[:src.index('OUT={}')],g)
hip69=g['kg'](g['lever'](50,dy=69),'7075')
rows=[  # part, owner (design / mass line), kg each, count per leg, basis
 ('hip_pitch lever r50, thigh-mounted twin screw dy 69 mm (L10)','Legs integrates / Actuators line',hip69,1,'Actuators lever(50,dy=69) CadQuery solid, 7075; replaces the dy 45 part (0.137); crossbar re-size pending (SF ~1.37 by linear scaling)'),
 ('knee lever r47.5 (crossbar + 2 cheeks)','Legs integrates / Actuators line',C['knee_lever_r47p5']['mass'],1,'Actuators CAD. Counted IN FULL: Legs structure 4.85 kg excludes all lever solids (L8), so the −0.167 v3-lever credit in cad_mass.py per_leg must be dropped'),
 ('nut-rotor hub','Actuators',C['nut_rotor_hub_x1']['mass'],6,'Actuators CAD, one per screw: hip 2 + knee 2 + ankle 2 (= 12 both legs, R-013 count; already 6/leg in cad_mass.py)'),
 ('trunnion pin pair (ø16/ø9 hollow steel)','Actuators',C['trunnion_pins_pair']['mass'],4,'Actuators CAD count 4/leg'),
 ('trunnion pin pair, screws 5-6 (if every screw has its own trunnion pair)','Actuators (open)',C['trunnion_pins_pair']['mass'],2,'RISK line: 6 screws/leg vs 4 pairs counted; Actuators to confirm'),
 ('ankle rod-end lugs on foot instep (2)','Legs',0.042/1,1,'Legs parametric solid 2 × 15×20×25 mm 7075 (structure.py); not in Actuators table'),
 ('rod-end spherical bearings at the levers (6)','Actuators (open)',None,6,'no CAD/datasheet mass in either table: OPEN'),
 ('hip pitch pivot bearing + seat (was the rotary CRBH output bearing in v3)','UNOWNED (open)',None,1,'no mass in any line (L10c): OPEN, owner to be assigned'),
 ('thigh trunnion clamp for the hip_pitch screws (config B)','Legs (open)',None,1,'replaces the pelvis bracket of config A; not sized: OPEN')]
L=['# Leg linkage table, Legs + Actuators (R-013): one table, no overlaps','','Source of truth for both modules. Actuators masses come from `modules/actuators/results/cad_mass.json` (read-only here); regenerate with `python3 modules/legs/linkage_table.py`.','',
   '| part | owner | kg each | per leg | kg per leg | basis |','|---|---|---|---|---|---|']
known=0; risk=0
for p,o,m,n,b in rows:
    kpl=None if m is None else m*n
    if m is not None and 'RISK' not in b: known+=kpl
    if m is not None and 'RISK' in b: risk+=kpl
    L.append(f"| {p} | {o} | {'—' if m is None else f'{m:.4f}'} | {n} | {'OPEN' if kpl is None else f'{kpl:.4f}'} | {b} |")
L+=['',f'**Counted: {known:.4f} kg per leg = {2*known:.3f} kg both legs** (target ≤ 0.65 kg; contract 0.609). Risk line: +{2*risk:.3f} kg. Open lines without a mass: rod-end bearings, hip pivot bearing (unowned), thigh trunnion clamp.',
    '',f"Reconciliation with cad_mass.py per_leg linkage {C['per_leg']['linkage']:.4f}: + hip lever dy 69 instead of 45 ({hip69-C['hip_pitch_lever_r50']['mass']:+.4f}), + drop the v3 knee-lever credit (+{C['knee_lever_r58p5_v3']['mass']:.4f}), + ankle instep lugs (+0.0420) = {C['per_leg']['linkage']+hip69-C['hip_pitch_lever_r50']['mass']+C['knee_lever_r58p5_v3']['mass']+0.042:.4f} kg per leg.",
    'No part appears both here and in Legs structure (structure_mass.md: lugs, tubes, clevis, tongue without lever, fork, foot plate) or in Actuators housings.']
open(os.path.join(H,'LINKAGE_TABLE.md'),'w').write('\n'.join(L)+'\n')
json.dump(dict(rows=[dict(part=p,owner=o,kg_each=m,count_per_leg=n,basis=b) for p,o,m,n,b in rows],counted_per_leg=known,counted_both=2*known,risk_both=2*risk),open(os.path.join(H,'LINKAGE_TABLE.json'),'w'),indent=1)
print('\n'.join(L[-5:]))
