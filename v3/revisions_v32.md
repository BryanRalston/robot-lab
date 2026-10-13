## F. v3.2 round (continued after the previous worker crashed)

| failure found | fix | result |
|---|---|---|
| Sim text said "CAD centre of mass 20–35 mm behind the ankles". Re-measured: CAD COM is 1.4 mm behind the ankle axis standing straight and 13 mm **ahead** of it in the sim's crouched stance; foot centre is +60 mm. The plain-PD fall is a controller-stiffness problem (joint gains capped at 600 N·m/rad in series hip/knee/ankle < m·g·h), not a COM-geometry problem. The old text was wrong. | Ankle actuators still moved from the back of the shank to the **front** (x −62 → +90 mm, lever on the instep, foot lever 50 → 70 mm to match the 70 mm arm the analysis sized for; the CAD had 50 mm, which was a hidden mismatch). | COM moves forward (see mass.md). The ankle bodies no longer sit behind the calf, so they stop limiting knee flexion. |
| CAD ankle lever was 50 mm but the actuator check assumed 70 mm | CAD lever = 70 mm | consistent |
| **Knee torque collapsed at deep flexion.** The CAD comment claimed "arm ≥ 45 mm for 30–120°". The real slider-crank arm was 34 mm at 0°, 32 mm at 100° and **14 mm at 120°**, so 120° had only about 41 N·m available. Constant-arm sizing hid it. | New `cad/knee_linkage.py` searches lever clock angle, radius and trunnion position with constraints for rod-end clearance to the femur, arm ≤ 59 mm over 0–80° (swing speed) and the torque needed at each angle [EST profile]. Best single-screw geometry still reaches only 0.76 of the need at 135°. `v3.py` now divides the knee need by the geometry factor k = 0.71, so the single screw fails torque/speed (212 < 228 N·m, 5.6 < 8 rad/s). **Fix: twin parallel RV12×4 screws (TBM2G-06013D each)** at y ±45 mm on a crossbar lever clocked 10°, r 58.5 mm, trunnions at x −125 mm with spherical top bearings. | Knee torque and speed pass over 0–135°. CAD is clash-free to 145° (stops set at 135°). |
| Twin knee actuators at ±36 mm: fins/trunnions overlapped, rods hit the thigh clevis, central lever web and square tongue hit the femur collar at 135° | dy 45 mm, spherical tops, crossbar + outboard cheeks, tongue rounded R32 and trimmed, knee cable drum moved outboard | 0 clashes in all range poses, including deep squat (hip −100°, knee 135°) |
| Roller-screw stroke was never checked | New `cad/stroke.py`: shortest pin-to-pin length ≥ motor + nut + bearings + retracted screw + rod end | knee 276 ≥ 247 mm, ankle 263 ≥ 253 mm: pass |
| **Analysis bug: 2-screw pairs (ankle, wrist) were weighed as ONE actuator** | mass × 2 for linear2 | robot mass rises from the under-counted 62.0 kg to 67.1 kg, so the 65 kg target now FAILS (see below) |
| v3.py crashed on an FEA case with one mesh level; fall cases only needed SF ≥ 1.0 | Fixed. Fall cases now need SF ≥ 2 (repeated falls over the robot's life) | |
| **fall_torso_panel SF 1.34 < 2** (3 mm CFRP side wall carries 50 % of a side-fall shoulder impact) | 4 mm CFRP doubler ring (OD 200 / ID 100) bonded inside each side wall around the shoulder pass-through (local wall 7 mm, +~0.15 kg) | peak 138 MPa, **SF 2.89**, 2 mesh levels Δ 5 % (third level hit the memory cap) |

## G. v3.2 close-out (this round)

| item | result |
|---|---|
| Knee lever rotate/translate had been left inside a code comment (lever modelled un-clocked at the origin) | Fixed in model.py; all clash checks re-run on the corrected geometry |
| Clash check, v3.2 geometry | **0 clashes** at standing + 15 range-extreme poses incl. deep squat (hip −100°, knee 135°); knee clash-free to 145° (stops 135°); single-leg adduction −6° OK, −8° ankle actuators touch (pelvis shift used for −12°) |
| Roller-screw stroke / cable bend radius | re-run, pass |
| FEA fall_torso_panel (with 4 mm doubler ring) | 138 MPa, **SF 2.89 ≥ 2**, 2 mesh levels Δ 5.0 % (third level exceeds the box's memory) |
| FEA knee_clevis | half model on the symmetry plane: 50 MPa, **SF 10.1, converged** (Δ 3.5 %) |
| FEA tibia_full | half model converged Δ 2.1 %, SF 6.2 (max-element stress is a re-entrant-corner singularity, not used); full model OOMs at 1 GB free |
| CAD centre of mass (v3.2, ankle actuators on shank front) | **+4.4 mm ahead of the ankle axis** standing straight (+21 mm in sim crouch); foot −60…+180 mm, so COM is well inside the support polygon |
| Sim, balance ON | stands 10 s, recovers from 125 N / 0.2 s pushes forward and sideways |
| Sim, balance OFF | **does not stand**: holds ~4 s then falls before 10 s. Cause: capped joint PD gains (series hip/knee/ankle softer than m·g·h); not geometry. Logged as FAIL on the dashboard |
| Mass | 63.8 kg catalog rollup (battery mass-down pass 2.1 h runtime) ≤ 65 kg target: pass. CAD solids 56.3 kg (no harness/covers) |
| Exports | GLB (283 parts), STEP assembly, MuJoCo humanoid_v3.xml regenerated |
