# v3 revision log

Every failure found in the v3 hardening loop and what was done about it. "it" = iteration of `analysis/v3.py` (0 = v2 design with catalog parts substituted 1:1). CAD/FEA/sim entries were found by `cad/clash.py`, `cad/knee_sweep.py`, `cad/fea_v3.py` and `sim/v3/balance_v3.py`.

## A. Analysis loop (analysis/v3.py)

| it | area | failure | fix |
|---|---|---|---|
| 0 | v3.0 = v2 with catalog parts substituted 1:1 | output-bearing-static hip_yaw: CRBH 5013 A fs=2.14 | (see later iterations) |
| 0 | v3.0 = v2 with catalog parts substituted 1:1 | speed hip_pitch: 3.9 < 4 rad/s at 30 % torque, 44 V bus | (see later iterations) |
| 0 | v3.0 = v2 with catalog parts substituted 1:1 | torque knee: 212 < 291 N·m | (see later iterations) |
| 0 | v3.0 = v2 with catalog parts substituted 1:1 | speed knee: 5.6 < 8 rad/s at 30 % torque, 44 V bus | (see later iterations) |
| 0 | v3.0 = v2 with catalog parts substituted 1:1 | thermal ankle_pitch: winding ΔT 348 K > 100 K (air, R_h-a 2.99 K/W) | (see later iterations) |
| 0 | v3.0 = v2 with catalog parts substituted 1:1 | speed shoulder_pitch: 3.2 < 4 rad/s at 30 % torque, 44 V bus | (see later iterations) |
| 0 | v3.0 = v2 with catalog parts substituted 1:1 | speed shoulder_roll: 3.2 < 4 rad/s at 30 % torque, 44 V bus | (see later iterations) |
| 0 | v3.0 = v2 with catalog parts substituted 1:1 | speed elbow: 5.1 < 6 rad/s at 30 % torque, 44 V bus | (see later iterations) |
| 0 | v3.0 = v2 with catalog parts substituted 1:1 | fall-shoulder-gear: 5200 N·m > momentary peak 369 (ratcheting 650) | (see later iterations) |
| 0 | v3.0 = v2 with catalog parts substituted 1:1 | bolted hip-pitch flexspline → output flange (momentary peak by friction): separation_or_slip | (see later iterations) |
| 0 | v3.0 = v2 with catalog parts substituted 1:1 | bolted shoulder actuator → torso frame (side-fall impact): separation_or_slip, fatigue | (see later iterations) |
| 0 | v3.0 = v2 with catalog parts substituted 1:1 | tendon-fatigue-UNVERIFIABLE: needs 1.75e+06 bend cycles; published evidence ≤ 5e4 (D/d 4, 150 N) | (see later iterations) |
| 0 | v3.0 = v2 with catalog parts substituted 1:1 | mass-target: 80.1 kg > 65 kg | (see later iterations) |
| 1 | actuator ankle_pitch | thermal ankle_pitch (winding ΔT 348 K > 100 K (air, R_h-a 2.99 K/W)) | TBM2G-06013C + RV12x4 arm 50 mm [air; ] → TBM2G-06813D + RV12x4 arm 65 mm [air; ] |
| 1 | actuator elbow | speed elbow (5.1 < 6 rad/s at 30 % torque, 44 V bus) | TBM2G-06013C + CSG-20-100 [air; CRBH 5013 A] → TBM2G-05013C + CSG-20-100 [air; CRBH 3010 A] |
| 1 | actuator hip_pitch | speed hip_pitch (3.9 < 4 rad/s at 30 % torque, 44 V bus) | TBM2G-11513C + CSG-25-100 [air; CRBH 9016 A] → TBM2G-07608C + CSG-25-100 [air_fins; CRBH 7013 A] |
| 1 | actuator hip_yaw | output-bearing-static hip_yaw (CRBH 5013 A fs=2.14) | TBM2G-06013C + CSG-20-100 [air; CRBH 5013 A] → TBM2G-05008A + CSG-14-100 [air; CRBH 7013 A] |
| 1 | actuator knee | torque knee (212 < 291 N·m); speed knee (5.6 < 8 rad/s at 30 % torque, 44 V bus) | TBM2G-08513C + RV12x5 arm 45 mm [air; ] → TBM2G-06813D + RV12x4 arm 52 mm [air; ] |
| 1 | actuator shoulder_pitch | speed shoulder_pitch (3.2 < 4 rad/s at 30 % torque, 44 V bus) | TBM2G-08513C + CSG-25-100 [air; CRBH 9016 A] → TBM2G-07608C + CSG-25-100 [air; CRBH 8016 A] |
| 1 | actuator shoulder_roll | speed shoulder_roll (3.2 < 4 rad/s at 30 % torque, 44 V bus) | TBM2G-08513C + CSG-25-100 [air; CRBH 9016 A] → TBM2G-06813C + CSG-25-100 [air; CRBH 4010 A] |
| 1 | side fall | fall-shoulder-gear: 5200 N·m > momentary peak 369 (ratcheting 650) | friction overload clutch at shoulder-roll output (slip 300 N·m < 369 N·m momentary peak) + 30 mm EPP pads on shoulder/hip |
| 1 | bolted joint | bolted hip-pitch flexspline → output flange (momentary peak by friction): separation_or_slip | 8×M4 → 8×M5 (12.9) |
| 1 | bolted joint | bolted shoulder actuator → torso frame (side-fall impact): separation_or_slip, fatigue | 6×M5 → 6×M6 (12.9) |
| 2 | bolted joint | bolted hip-pitch flexspline → output flange (momentary peak by friction): separation_or_slip | 8×M5 → 8×M6 (12.9) |
| 2 | bolted joint | bolted shoulder actuator → torso frame (side-fall impact): separation_or_slip | 6×M6 → 6×M8 (12.9) |
| 3 | bolted joint | bolted shoulder actuator → torso frame (side-fall impact): separation_or_slip | 6×M8 → 8×M8 (12.9) |
| 4 | actuator hip_roll (mass reduction) | passing but oversized; robot 75.8 kg | TBM2G-11513C + CSG-25-100 [air; CRBH 9016 A] → TBM2G-07608C + CSG-25-100 [air; CRBH 7013 A] (−2.50 kg) |
| 4 | actuator ankle_pitch (mass reduction) | passing but oversized; robot 73.3 kg | TBM2G-06813D + RV12x4 arm 65 mm [air; ] → TBM2G-06808D + RV12x4 arm 70 mm [air_fins; ] (−0.29 kg) |
| 4 | actuator waist_yaw (mass reduction) | passing but oversized; robot 73.0 kg | TBM2G-06013C + CSG-20-100 [air; CRBH 5013 A] → TBM2G-06008A + CSG-17-100 [air; CRBH 5013 A] (−0.21 kg) |
| 4 | actuator waist_pitch (mass reduction) | passing but oversized; robot 72.8 kg | TBM2G-08513C + CSG-25-100 [air; CRBH 9016 A] → TBM2G-07608A + CSG-25-100 [air; CRBH 5013 A] (−1.02 kg) |
| 4 | actuator shoulder_pitch (mass reduction) | passing but oversized; robot 71.8 kg | TBM2G-07608C + CSG-25-100 [air; CRBH 8016 A] → TBM2G-07608C + CSG-25-100 [air; CRBH 6013 A] (−1.20 kg) |
| 4 | actuator shoulder_yaw (mass reduction) | passing but oversized; robot 70.6 kg | TBM2G-06013C + CSG-20-100 [air; CRBH 5013 A] → TBM2G-06008C + CSG-17-100 [air; CRBH 4010 A] (−0.84 kg) |
| 4 | actuator wrist_roll (mass reduction) | passing but oversized; robot 69.7 kg | TBM2G-05008C + CSG-14-100 [air; CRBH 5013 A] → TBM2G-05008C + CSG-14-100 [air; CRBH 208 A] (−0.78 kg) |
| 4 | actuator neck_yaw (mass reduction) | passing but oversized; robot 69.0 kg | TBM2G-05008C + CSG-14-100 [air; CRBH 5013 A] → TBM2G-05008A + CSG-14-100 [air; CRBH 208 A] (−0.39 kg) |
| 4 | actuator neck_pitch (mass reduction) | passing but oversized; robot 68.6 kg | TBM2G-05008C + CSG-14-100 [air; CRBH 5013 A] → TBM2G-05008A + CSG-14-100 [air; CRBH 208 A] (−0.39 kg) |
| 4 | battery (mass reduction) | runtime 2.9 h > 2 h; robot 68.2 kg | 13S10P → 13S9P (−1.14 kg, runtime 2.7 h) |
| 4 | battery (mass reduction) | runtime 2.7 h > 2 h; robot 67.0 kg | 13S9P → 13S8P (−1.14 kg, runtime 2.4 h) |
| 4 | battery (mass reduction) | runtime 2.4 h > 2 h; robot 65.9 kg | 13S8P → 13S7P (−1.14 kg, runtime 2.1 h) |
| 5 | actuator hip_yaw (mass reduction) | passing but oversized; robot 64.8 kg | TBM2G-05008A + CSG-14-100 [air; CRBH 7013 A] → TBM2G-05008A + CSG-14-100 [air; CRBH 6013 A] (−0.21 kg) |
| 5 | actuator hip_roll (mass reduction) | passing but oversized; robot 64.6 kg | TBM2G-07608C + CSG-25-100 [air; CRBH 7013 A] → TBM2G-07608C + CSG-25-100 [air; CRBH 6013 A] (−0.21 kg) |
| 5 | actuator hip_pitch (mass reduction) | passing but oversized; robot 64.4 kg | TBM2G-07608C + CSG-25-100 [air_fins; CRBH 7013 A] → TBM2G-07608C + CSG-25-100 [air; CRBH 6013 A] (−0.21 kg) |
| 5 | actuator knee (mass reduction) | passing but oversized; robot 64.1 kg | TBM2G-06813D + RV12x4 arm 52 mm [air; ] → TBM2G-06808D + RV12x4 arm 58 mm [air; ] (−0.29 kg) |
| 5 | actuator waist_pitch (mass reduction) | passing but oversized; robot 63.8 kg | TBM2G-07608A + CSG-25-100 [air; CRBH 5013 A] → TBM2G-06013A + CSG-25-100 [air; CRBH 5013 A] (−0.03 kg) |
| 6 | actuator waist_pitch (mass reduction) | passing but oversized; robot 63.8 kg | TBM2G-06013A + CSG-25-100 [air; CRBH 5013 A] → TBM2G-06808A + CSG-25-100 [air; CRBH 5013 A] (−0.02 kg) |

## B. Earlier analysis-code defects (found while iterating)

| failure | fix |
|---|---|
| First full run: robot mass 94.6 kg; shoulder actuators 4.5 kg each | Fall moment was applied to all three shoulder joints with fs ≥ 3. Now applied only to shoulder pitch (where the side-fall load enters) with fs ≥ 1 (accidental one-off load, no brinelling beyond C0); other joints use fs ≥ 3 on operating/landing loads. |
| Ankle and wrist differential screw pairs counted twice (pitch and roll each sized their own pair) | One shared pair per joint (`SHARED`), mass counted once, both DoF checked on the same hardware. |
| Smallest CRBH in table was 3010 → neck/wrist got 0.12–0.29 kg bearings | Added IKO CRBH 208 / 258 rows from the catalog. |
| Passing joints were never down-sized (only failing joints were re-selected) | Added a mass-reduction pass: every joint re-selected as the lightest passing catalog combination, then all checks re-run (mass changes the loads). 70.5 → 62.0 kg. |
| Lever-arm search compounded ×1.3 per iteration (knee arm reached 101 mm, ankle 110 mm) | Arms capped at CAD packaging limits: knee 60 mm, ankle 70 mm, wrist 30 mm. |

## C. CAD (cad/model.py, clash.py)

| failure | fix |
|---|---|
| v3.0 CAD with catalog envelopes: 100 clashes at standing | — (individual fixes below) |
| Hip-yaw housing (now carries a CRBH 6013, Ø90) and hip bracket webs hit the 300 mm pelvis side walls | Pelvis width follows hip_y: 2×(hip_y+55) = 370 mm; hip openings follow housing OD |
| Single-leg hip adduction −12° (v2 only checked both legs together): legs cross (14 clashes) | hip_y 100 → 115 (still 7 clashes at −6°) → 130 mm. Single-leg adduction clash-free to −6° (−8° hits the other ankle actuators); −12° only with pelvis shift (both hips), which is how it is used in gait. |
| Finned ankle actuator bodies (fin OD 86) overlapped each other | ankle_act_dy 37 → 45 mm |
| 17 hand motors in a 40×40 box (v2) not real; first v3 placement had drives overlapping each other and the wrist | 6 flexor drives (DCX22S+GPX22HP) in one ring r = 23 mm in a Ø76/72 forearm; 5 small drives (DCX16S+GPX16) in the palm; tendons as one Ø6 bundle through the hollow wrist-roll bore (all rotary housings now have a through-bore) |
| Catalog neck-yaw housing hit the compute bay; neck pitch hit neck yaw and the head shell | torso_top 1556 → 1590; neck pitch tt+48 → tt+60; head opening Ø118; head centre +15 mm |
| 2.1 kWh P45B pack is 5.9 L, v2 box was 5.0 L → hit shoulder housings and spine | Pack box 185×220×144 mm, moved forward; compute bay raised |
| Upper-arm tube ran into the (longer) catalog shoulder-yaw housing | Tube length derived from the housing length |
| Hip abduction 20° with arms hanging: hand touches the thigh | Limit 15° with arms hanging (functional need is 15°); 20° needs the arm moved |
| Knee > 120°: 0 clashes at 125°, 0 at 130°, 0 at 140° | v3.1: not fixed (rod end vs femur collar at 125°, knee body vs ankle actuators at 130°). **v3.2: fixed**, see section F (ankle actuators to the shank front, twin knee screws, re-clocked lever). Knee is now 0–135°, clash-free to 145°. |
| After fixes: clash check of standing + 14 range-extreme poses | **0 clashes** |

## D. Structure / FEA (cad/fea_v3.py)

| item | result |
|---|---|
| knee_clevis | peak 50 MPa (99.5 % element), SF yield 10.09, Goodman 11.52, mesh Δ 3.5 % → converged |
| fall_hip_bracket | peak 33 MPa (99.5 % element), SF yield 15.34, mesh Δ 2.7 % → converged |
| fall_shoulder_housing | peak 56 MPa (99.5 % element), SF yield 8.92, mesh Δ 0.5 % → converged |
| pelvis_hip | peak 44 MPa (99.5 % element), SF yield 11.37, Goodman 12.98, mesh Δ 1.7 % → converged |
| femur_full | peak 47 MPa (99.5 % element), SF yield 10.62, Goodman 12.13, mesh Δ 0.1 % → converged |
| fall_torso_panel | peak 138 MPa (99.5 % element), SF yield 2.89, mesh Δ 5.0 % → converged |
| tibia_full | peak 81 MPa (99.5 % element), SF yield 6.19, Goodman 7.06, mesh Δ 2.1 % → converged |
| pelvis_hip first run: stresses of 10⁴–10⁸ MPa, solver not converging | The hip-bracket flange sat 1 mm below the pelvis top wall (top = pelvis_top−5 vs wall inner face pelvis_top−4), so the bracket was floating. Flange now bears on the wall (bolted face contact); re-run. |
| Convergence metric | Peak = 99.5th-percentile element stress; Δ < 10 % between the last two meshes counts as converged. Max-element stress is also reported; it keeps rising at re-entrant corners (singularities) and is not used for SF. |
| FEA memory | First attempt at full-length P2 meshes: TetGen quality refinement gave 100k–970k tets regardless of max-volume (max_volume was ignored with an options string) and OOM. Fixed by setting fixedvolume/maxvolume explicitly, radius-edge 3.0 and AMG-preconditioned CG; single-threaded BLAS. |

## E. Simulation (sim/v3)

| failure | fix / status |
|---|---|
| v3 model with CAD mass properties: plain PD (balance off) does not stand 10 s | v3.1 blamed the CAD centre of mass sitting 20–35 mm behind the ankles. **That claim was wrong** (re-measured in v3.2: COM +4.4 mm ahead of the ankle axis, see section G). The fall comes from capped PD gains. With the COM ankle strategy it stands and rejects pushes. |

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
