# Side-fall frontal-plane tube bending: femur 50 × 1.5, tibia 45 × 1.7 (T&R, 2026-10-21)
Allowable: 7050-T73511 fall limit **393 MPa** (R-127). Z: tibia 45 × 1.7 = **2412 mm³**, femur 50 × 1.5 = **2691 mm³**. Hand calcs [EST] unless cited.

## Inputs from the repo
- Geometry (model_v4 / sim v3): hip roll axis z 1045, hip pitch 920, knee 500, ankle 80. Foot box 240 × 100 mm, sole ≈ 86 mm below the ankle, **half-width 50 mm**.
- Masses (sim v3): thigh 2.38, shank 3.16, foot 2.65 kg; robot 68.42 kg.
- **Hip roll:** TBM2G-08508A + CSG-25-100, **peak avail 204 N·m** (CONTRACTS); joint-side armature 0.441 kg·m² (sim). ROM −12…15° is a sim limit. **No hardware hip-roll stop is defined.**
- **Ankle roll:** shared screw pair, avail 177 N·m; **±18° rigid 7075 block hard stop** (Legs L29).
- Side falls: T-030 tuck B, shoulder pad 9.17 kN gate, impact ≈ 6.4 m/s at ≈ 1.5 m (T030_BRIEF). Knee pads: front only (P-158 thigh-front 3.9 kN plateau [EST]). **No lateral knee or shank pad exists.**

## Key load-path result
The leg has no lateral load between hip and foot (the knee joint is rigid in the frontal plane), so the frontal moment varies linearly between the two ends. **|M_tube| ≤ max(|M_hip end|, |M_ankle end|) + leg-inertia terms.** It is capped by the joint/foot capacities, not by the ground force, **unless a contact lands mid-leg** (scenario S2).

## S1: side fall, foot planted, leg loaded laterally
- **Ankle end:** past the rigid ±18° stop, the moment is set by the foot rolling on its edge.
  - Lever ≈ 0.05 cos 18° + 0.086 sin 18° ≈ 74 mm. Fz ≤ 2 mg ≈ 1.34 kN [EST impact factor] and Fy ≤ μ·Fz (μ 1.0, sim) at ≈ 70 mm height.
  - M_ankle ≈ 1.34 × 0.074 + 1.34 × 0.07 ≈ **193 N·m**. The rigid stop passes it straight through. The ankle actuator (177) is not the cap; the foot edge is.
- **Hip end:** hip roll motor peak 204 + rotor inertia (0.441 kg·m² × α; α ≈ Δω/t_r ≈ 4 rad/s / 20–50 ms ≈ 80–200 rad/s² [EST]) ≈ 35–88 → **≤ 292 N·m**. It is capped only while the strain-wave gear and drive yield/backdrive. **No hip-roll hard stop is defined.** If a rigid stop or a thigh-pelvis contact is added, this cap must be redone (as for the knee).
- **DLF:** contact rise 20–50 ms vs leg frontal mode T_n ≈ 10–30 ms [EST] → t_r/T_n ≥ 1 → ramp DLF = 1 + |sin(π t_r/T_n)|/(π t_r/T_n) ≤ **1.3** at t_r/T_n ≥ 1 (bounding the 1–1.5 band at ≤ 1.21 plus margin).
- **Design moment: 292 × 1.3 ≈ 380 N·m.** Tibia σ 157 → **SF 2.50**; femur σ 141 → **SF 2.78**. **PASS.**

## S2: side impact on the knee/shank directly onto the floor (mid-leg contact)
- **S2a, topple from standing, fall-side stance leg:** the foot is the pivot (v ≈ 0), hip/shoulder land first (tuck B), and the knee lands at ≈ ω × 0.5 ≈ (6.4/1.5) × 0.5 ≈ 2.1 m/s. The shank is supported at the knee and near the foot → short span, small bending. Not governing.
- **S2b, side tip from kneel (failed R-146 kneel):**
  - Femur: upper-body load enters at the hip, the knee/thigh is on the floor, and the hip-end moment is capped by hip roll ≤ 292 (×1.3 = 380 N·m) → **same as S1, PASS**, again conditional on no rigid hip-roll stop.
  - Tibia: lies on the floor, so negligible.
- **S2c, governing: knee strikes first with the foot still moving** (swing/crossing leg in a stumble side fall, or a kneel tip with the foot lifted). Knee arrested, foot+ankle (2.65 kg) at L ≈ 0.48 m behaves as a **cantilever tip-mass impact**: M = v √(k m) L, k = 3EI/L³ ≈ 1.05 × 10⁵ N/m. The tip-mass impact formula already includes the dynamics (no extra DLF); T_n ≈ 32 ms.
  - With no lateral knee pad (rigid cover contact, knee arrested ≪ T_n), it depends on the foot speed relative to the knee:

| foot speed rel. knee | M tibia (N·m) | σ (MPa) | SF 393 |
|---|---|---|---|
| 2.1 m/s (knee speed, foot co-moving) | 530 | 220 | **1.79** |
| 3.0 m/s | 758 | 314 | **1.25** |
| 4.2 m/s (leg swinging about the hip, foot ≈ 2 × knee) [EST] | ≈ 1060 | 440 | **0.89 FAIL** |

  - A femur analogue (thigh struck mid-span with the hip moving) is bounded by the hip roll cap as in S2b.
  - **Fix options:**
    - (i) a **lateral knee/shank pad** (crushable, like P-158) so the knee arrest time is ≥ T_n/2 ≈ 16 ms and the pad plateau ≤ ~3 kN. That roughly halves M [EST; to size with Controls velocities];
    - (ii) Controls fall-mode keeps the swing leg tucked to the body in side falls, so the knee never leads with the foot flying;
    - (iii) a 2.3 mm tibia (Z 3140 → SF ≈ 1.16 at 4.2 m/s).

## Verdicts
| scenario | governing moment | tibia 45×1.7 SF | femur 50×1.5 SF | verdict |
|---|---|---|---|---|
| S1 foot planted, lateral | 380 N·m (hip-roll capped, DLF 1.3) | 2.50 | 2.78 | **PASS** (if there is no rigid hip-roll stop) |
| S2a topple, stance leg knee contact | small | — | — | PASS |
| S2b side tip from kneel | 380 N·m | — | 2.78 | PASS (same condition) |
| S2c knee-first, foot moving | 530–1060 N·m | **1.79 → 0.89** | (hip-capped) | **CONDITIONAL**: needs the foot-relative velocity from sim; a lateral knee pad or a swing-leg tuck rule |

## Missing inputs (not invented)
- Hip roll **hardware stop** (none defined): its type/stiffness/location, and the CSG-25 momentary/ratcheting torque. If rigid, S1/S2b are no longer capped at 292 N·m.
- Side-fall sim outputs (Controls): knee and foot velocities at first leg contact, contact order, planted-foot Fz/Fy, hip-roll torque and angular acceleration. These replace the v and α estimates.
- Lateral knee/shank contact definition (the cover stiffness or a pad): none exists.
- Measured leg frontal T_n (tap test) and the shank f₁.
- Foot sole friction coefficient (sim 1.0).

## G5: TP-G5-19 (G5_TEST_PLAN.md)
