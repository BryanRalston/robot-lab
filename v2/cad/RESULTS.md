# v2 CAD: interference results
Model: `model.py` (CadQuery, parametric; ~161 parts). Check: `clash.py` (exact OCC boolean intersection, >1 mm³, intended mates whitelisted). Range sweep: `sweep.py` (5° steps).

**Standing pose:** 72 clashes in the first assembly → 0 after the fixes listed as `# FIX` comments in model.py (yaw/roll yoke rebuilt, pelvis enlarged to enclose the yaw actuators, knee tongue/lever merged, ankle top spherical bearings, torso openings, battery/compute repackaged, linear elbow → rotary, head/neck re-stacked, ankle fork narrowed, hip bracket ring resized).

**Range extremes (first sweep):** knee clash-free only 0..40° (need 0..120°) and hip roll only 0..15°. Fixes: femur axis 18 mm forward; knee clevis bridge moved in front of the pin; knee lever re-clocked to 30° behind straight down (r = 52 mm, effective arm 26 mm at full extension, ≥45 mm over 30–120° [EST]); tibia axis 14 mm forward. Hip adduction is checked with both hips rolled together (pelvis over the stance foot); single-leg adduction at the narrow 200 mm stance hits the other leg, which is a whole-body self-collision constraint for the controller.

**Final hard stops (all 0 clashes, plus sit pose hip −90°/knee 120°):**

| joint | clash-free (sweep) | functional need [EST] | hard stop |
|---|---|---|---|
| hip pitch | −105..40 | −100..30 | −105..40 |
| hip roll | 0..20 single leg; −12 both | −10..15 | −12..20 |
| hip yaw | −35..45 | −20..30 | −35..45 |
| knee | 0..120 (knee actuator body meets ankle actuators at 125) | 0..120 | 0..120 |
| ankle pitch | −45..40 | −35..30 | −45..40 |
| ankle roll | ±25 | ±20 | ±25 |

Note: knee 120° leaves no margin over the stated need; deep squats beyond 120° would need a linkage knee.
