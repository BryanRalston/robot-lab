# L63: A38 collar cross-pin backup at the R-110 fault (29.6 kN)
RL Legs, 2026-10-14. Hand calc: `cross_pin_backup_l63.py` → `cross_pin_backup_l63.json`. [EST] = estimate.

**Inputs:** 7075-T6 collar (ID 50 × 34 mm, wall 6 mm), ø50 × 1.2 mm 7075 tube, 7075 sleeve 47.6/43.6 × 34. L22 pins are 2 × ø6 × 62 42CrMo4, through-diameter along x, at z ±8.5 from collar mid (a14_r7.py:23, layout [EST]). Load: 29.6 kN, conservatively all applied to the pins in the axial direction (R-110 §6). Allowables from MATERIALS_DB: 7075 Sy 480 / shear 330 / fatigue 160; 42CrMo4 Sy 990. Pin shear yield is 0.6·Sy. Bearing yield is 1.5·Sy = 720 [EST, same basis as R-110]. Hole Kt is 2.909 (FEA coupon, STRUCTURE_FEA_REPORT).

**Load path note:** the sleeve ends inside the collar (z 0–34), so it can't carry load out to the rest of the femur. All 29.6 kN must leave through the **tube** wall in bearing. R-110's 55 kN bearing figure added the sleeve, which isn't in that path.

## Current L22 (2 × ø6 through)
| check | stress MPa | SF | verdict |
|---|---|---|---|
| pin shear (4 planes) | 262 | 2.27 | pass |
| **tube bearing (4 faces × 6 × 1.2)** | **1028** | **0.70** | **FAIL** |
| collar tear-out (e 8.5, e/D 1.42) | 112 | 2.94 | pass (e/D below the 1.5 guideline) |
| tube net section | 191 | 2.52 | pass |
| walking fatigue at hole (bond failed) | 85 | 1.87 | pass |

## Proposed L63: 8 × ø7 radial pins (one wall each)
4 pins at 90° spacing in each of 2 rows at z 8.5 / 25.5. Each pin is ø7 × 10 (collar 6 + tube 1.2 + sleeve 2 + 0.8), press-fit in the collar and retained by the collar cover. Needs ≥ 61.7 mm² of tube bearing for SF 1.5; this layout gives 67.2 mm².
| check | MPa | SF |
|---|---|---|
| pin shear (8 single planes) | 96 | 6.18 |
| tube bearing | 441 | **1.63** |
| collar tear-out (e/D 1.21) | 62 | 5.35 |
| tube net section | 254 | 1.89 |
| walking fatigue at the holes [EST: coupon Kt, no hole interaction] | 114 | **1.41**, so a 3D FEA is owed |

Rejected: 4 × ø6 through pins staggered x/y give bearing SF 1.40. ø8 through pins need a collar of about 50 mm or more to stop the crossing pins clashing.

**Mass:** 8 × ø7 × 10 = 0.0240 kg/leg against 0.0273 for the L22 pins, a change of **−0.0066 kg for the robot**. Retention hardware is not included [EST ≤ +0.004]. Net is about 0 kg; book 0.

**Open:** 3D FEA of the 8-hole tube (fatigue and hole interaction). The pin retention detail. Thigh panel access (a14_r7) changes from a punch-through to radial access.

## Side item: knee trunnion cheek body
The trunnion cheeks and their outward bosses are **thigh (femur-side) parts**. knee_fin_sweep.py:4 lists them as "thigh parts outside the knee actuator asm (trunnion cheeks, bracket, clevis, femur)". knee_bracket_move_l60.py:1 moves the cheeks "+DZ up, thigh frame". So the boss does **not** rotate relative to the thigh shell. The knee housing rotates on its trunnion pins inside the cheeks.
