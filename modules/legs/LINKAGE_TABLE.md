# Leg linkage table, Legs + Actuators (R-013): one table, no overlaps

Source of truth for both modules. Actuators masses come from `modules/actuators/results/cad_mass.json` (read-only here); regenerate with `python3 modules/legs/linkage_table.py`.

| part | owner | kg each | per leg | kg per leg | basis |
|---|---|---|---|---|---|
| hip_pitch lever r50, thigh-mounted twin screw dy 69 mm (L10) | Legs integrates / Actuators line | 0.1666 | 1 | 0.1666 | Actuators lever(50,dy=69) CadQuery solid, 7075; replaces the dy 45 part (0.137); crossbar re-size pending (SF ~1.37 by linear scaling) |
| knee lever r47.5 (crossbar + 2 cheeks) | Legs integrates / Actuators line | 0.1346 | 1 | 0.1346 | Actuators CAD. Counted IN FULL: Legs structure 4.85 kg excludes all lever solids (L8), so the −0.167 v3-lever credit in cad_mass.py per_leg must be dropped |
| nut-rotor hub | Actuators | 0.0160 | 6 | 0.0960 | Actuators CAD, one per screw: hip 2 + knee 2 + ankle 2 (= 12 both legs, R-013 count; already 6/leg in cad_mass.py) |
| trunnion pin pair (ø16/ø9 hollow steel) | Actuators | 0.0259 | 4 | 0.1036 | Actuators CAD count 4/leg |
| trunnion pin pair, screws 5-6 (if every screw has its own trunnion pair) | Actuators (open) | 0.0259 | 2 | 0.0518 | RISK line: 6 screws/leg vs 4 pairs counted; Actuators to confirm |
| ankle rod-end lugs on foot instep (2) | Legs | 0.0420 | 1 | 0.0420 | Legs parametric solid 2 × 15×20×25 mm 7075 (structure.py); not in Actuators table |
| rod-end spherical bearings at the levers (6) | Actuators (open) | — | 6 | OPEN | no CAD/datasheet mass in either table: OPEN |
| hip pitch pivot bearing + seat (was the rotary CRBH output bearing in v3) | UNOWNED (open) | — | 1 | OPEN | no mass in any line (L10c): OPEN, owner to be assigned |
| thigh trunnion clamp for the hip_pitch screws (config B) | Legs (open) | — | 1 | OPEN | replaces the pelvis bracket of config A; not sized: OPEN |

**Counted: 0.5428 kg per leg = 1.086 kg both legs** (target ≤ 0.65 kg; contract 0.609). Risk line: +0.104 kg. Open lines without a mass: rod-end bearings, hip pivot bearing (unowned), thigh trunnion clamp.

Reconciliation with cad_mass.py per_leg linkage 0.3043: + hip lever dy 69 instead of 45 (+0.0292), + drop the v3 knee-lever credit (+0.1673), + ankle instep lugs (+0.0420) = 0.5428 kg per leg.
No part appears both here and in Legs structure (structure_mass.md: lugs, tubes, clevis, tongue without lever, fork, foot plate) or in Actuators housings.
