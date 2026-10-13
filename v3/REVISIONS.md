# v3 revision log

Every failure found in the v3 hardening loop and what was done about it. "it" = iteration of `analysis/v3.py` (0 = v2 design with catalog parts substituted 1:1). CAD/FEA/sim entries were found by `cad/clash.py`, `cad/knee_sweep.py`, `cad/fea_v3.py` and `sim/v3/balance_v3.py`.

## A. Analysis loop (analysis/v3.py)

| it | area | failure | fix |
|---|---|---|---|
| 0 | v3.0 = v2 with catalog parts substituted 1:1 | output-bearing-static hip_yaw: CRBH 5013 A fs=2.23 | (see later iterations) |
| 0 | v3.0 = v2 with catalog parts substituted 1:1 | speed hip_pitch: 3.9 < 4 rad/s at 30 % torque, 44 V bus | (see later iterations) |
| 0 | v3.0 = v2 with catalog parts substituted 1:1 | speed knee: 5.6 < 8 rad/s at 30 % torque, 44 V bus | (see later iterations) |
| 0 | v3.0 = v2 with catalog parts substituted 1:1 | thermal ankle_pitch: winding ΔT 320 K > 100 K (air, R_h-a 2.99 K/W) | (see later iterations) |
| 0 | v3.0 = v2 with catalog parts substituted 1:1 | speed shoulder_pitch: 3.2 < 4 rad/s at 30 % torque, 44 V bus | (see later iterations) |
| 0 | v3.0 = v2 with catalog parts substituted 1:1 | speed shoulder_roll: 3.2 < 4 rad/s at 30 % torque, 44 V bus | (see later iterations) |
| 0 | v3.0 = v2 with catalog parts substituted 1:1 | speed elbow: 5.1 < 6 rad/s at 30 % torque, 44 V bus | (see later iterations) |
| 0 | v3.0 = v2 with catalog parts substituted 1:1 | fall-shoulder-gear: 4984 N·m > momentary peak 369 (ratcheting 650) | (see later iterations) |
| 0 | v3.0 = v2 with catalog parts substituted 1:1 | bolted hip-pitch flexspline → output flange (momentary peak by friction): separation_or_slip | (see later iterations) |
| 0 | v3.0 = v2 with catalog parts substituted 1:1 | bolted shoulder actuator → torso frame (side-fall impact): separation_or_slip, fatigue | (see later iterations) |
| 0 | v3.0 = v2 with catalog parts substituted 1:1 | tendon-fatigue-UNVERIFIABLE: needs 1.75e+06 bend cycles; published evidence ≤ 5e4 (D/d 4, 150 N) | (see later iterations) |
| 0 | v3.0 = v2 with catalog parts substituted 1:1 | FEA-convergence knee_clevis: last refinement changed peak 11 % | (see later iterations) |
| 0 | v3.0 = v2 with catalog parts substituted 1:1 | mass-target: 76.8 kg > 65 kg | (see later iterations) |
| 1 | actuator ankle_pitch | thermal ankle_pitch (winding ΔT 320 K > 100 K (air, R_h-a 2.99 K/W)) | TBM2G-06013C + RV12x4 arm 50 mm [air; ] → TBM2G-06813D + RV12x4 arm 65 mm [air; ] |
| 1 | actuator elbow | speed elbow (5.1 < 6 rad/s at 30 % torque, 44 V bus) | TBM2G-06013C + CSG-20-100 [air; CRBH 5013 A] → TBM2G-05013C + CSG-20-100 [air; CRBH 3010 A] |
| 1 | actuator hip_pitch | speed hip_pitch (3.9 < 4 rad/s at 30 % torque, 44 V bus) | TBM2G-11513C + CSG-25-100 [air; CRBH 9016 A] → TBM2G-07608C + CSG-25-100 [air; CRBH 7013 A] |
| 1 | actuator hip_yaw | output-bearing-static hip_yaw (CRBH 5013 A fs=2.23) | TBM2G-06013C + CSG-20-100 [air; CRBH 5013 A] → TBM2G-05008A + CSG-14-100 [air; CRBH 7013 A] |
| 1 | actuator knee | speed knee (5.6 < 8 rad/s at 30 % torque, 44 V bus) | TBM2G-08513C + RV12x5 arm 45 mm [air; ] → TBM2G-07613D + RV12x5 arm 58 mm [air_fins; ] |
| 1 | actuator shoulder_pitch | speed shoulder_pitch (3.2 < 4 rad/s at 30 % torque, 44 V bus) | TBM2G-08513C + CSG-25-100 [air; CRBH 9016 A] → TBM2G-07608C + CSG-25-100 [air; CRBH 8016 A] |
| 1 | actuator shoulder_roll | speed shoulder_roll (3.2 < 4 rad/s at 30 % torque, 44 V bus) | TBM2G-08513C + CSG-25-100 [air; CRBH 9016 A] → TBM2G-06813C + CSG-25-100 [air; CRBH 4010 A] |
| 1 | side fall | fall-shoulder-gear: 4984 N·m > momentary peak 369 (ratcheting 650) | friction overload clutch at shoulder-roll output (slip 300 N·m < 369 N·m momentary peak) + 30 mm EPP pads on shoulder/hip |
| 1 | bolted joint | bolted hip-pitch flexspline → output flange (momentary peak by friction): separation_or_slip | 8×M4 → 8×M5 (12.9) |
| 1 | bolted joint | bolted shoulder actuator → torso frame (side-fall impact): separation_or_slip, fatigue | 6×M5 → 6×M6 (12.9) |
| 2 | bolted joint | bolted hip-pitch flexspline → output flange (momentary peak by friction): separation_or_slip | 8×M5 → 8×M6 (12.9) |
| 2 | bolted joint | bolted shoulder actuator → torso frame (side-fall impact): separation_or_slip | 6×M6 → 6×M8 (12.9) |
| 3 | actuator hip_yaw (mass reduction) | passing but oversized; robot 70.5 kg | TBM2G-05008A + CSG-14-100 [air; CRBH 7013 A] → TBM2G-05008A + CSG-14-100 [air; CRBH 6013 A] (−0.21 kg) |
| 3 | actuator hip_roll (mass reduction) | passing but oversized; robot 70.3 kg | TBM2G-11513C + CSG-25-100 [air; CRBH 9016 A] → TBM2G-07608C + CSG-25-100 [air; CRBH 6013 A] (−2.72 kg) |
| 3 | actuator hip_pitch (mass reduction) | passing but oversized; robot 67.6 kg | TBM2G-07608C + CSG-25-100 [air; CRBH 7013 A] → TBM2G-07608C + CSG-25-100 [air; CRBH 6013 A] (−0.21 kg) |
| 3 | actuator ankle_pitch (mass reduction) | passing but oversized; robot 67.4 kg | TBM2G-06813D + RV12x4 arm 65 mm [air; ] → TBM2G-06013D + RV12x4 arm 70 mm [air_fins; ] (−0.18 kg) |
| 3 | actuator waist_yaw (mass reduction) | passing but oversized; robot 67.2 kg | TBM2G-06013C + CSG-20-100 [air; CRBH 5013 A] → TBM2G-06008A + CSG-17-100 [air; CRBH 5013 A] (−0.21 kg) |
| 3 | actuator waist_pitch (mass reduction) | passing but oversized; robot 67.0 kg | TBM2G-08513C + CSG-25-100 [air; CRBH 9016 A] → TBM2G-07608A + CSG-25-100 [air; CRBH 5013 A] (−1.02 kg) |
| 3 | actuator shoulder_pitch (mass reduction) | passing but oversized; robot 66.0 kg | TBM2G-07608C + CSG-25-100 [air; CRBH 8016 A] → TBM2G-07608C + CSG-25-100 [air; CRBH 6013 A] (−1.20 kg) |
| 3 | actuator shoulder_yaw (mass reduction) | passing but oversized; robot 64.8 kg | TBM2G-06013C + CSG-20-100 [air; CRBH 5013 A] → TBM2G-06008C + CSG-17-100 [air; CRBH 4010 A] (−0.84 kg) |
| 3 | actuator wrist_roll (mass reduction) | passing but oversized; robot 64.0 kg | TBM2G-05008C + CSG-14-100 [air; CRBH 5013 A] → TBM2G-05008C + CSG-14-100 [air; CRBH 208 A] (−0.78 kg) |
| 3 | actuator neck_yaw (mass reduction) | passing but oversized; robot 63.2 kg | TBM2G-05008C + CSG-14-100 [air; CRBH 5013 A] → TBM2G-05008A + CSG-14-100 [air; CRBH 208 A] (−0.39 kg) |
| 3 | actuator neck_pitch (mass reduction) | passing but oversized; robot 62.8 kg | TBM2G-05008C + CSG-14-100 [air; CRBH 5013 A] → TBM2G-05008A + CSG-14-100 [air; CRBH 208 A] (−0.39 kg) |
| 4 | actuator knee (mass reduction) | passing but oversized; robot 62.4 kg | TBM2G-07613D + RV12x5 arm 58 mm [air_fins; ] → TBM2G-06813D + RV12x4 arm 58 mm [air; ] (−0.20 kg) |
| 4 | actuator waist_pitch (mass reduction) | passing but oversized; robot 62.2 kg | TBM2G-07608A + CSG-25-100 [air; CRBH 5013 A] → TBM2G-06808A + CSG-25-100 [air; CRBH 5013 A] (−0.05 kg) |
| 4 | actuator shoulder_pitch (mass reduction) | passing but oversized; robot 62.2 kg | TBM2G-07608C + CSG-25-100 [air; CRBH 6013 A] → TBM2G-07608C + CSG-25-100 [air; CRBH 5013 A] (−0.19 kg) |

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
| Knee > 120°: 5 clashes at 125°, 10 at 130°, 18 at 140° | **Not fixed.** At 125° the rod end hits the femur collar (a linkage knee could fix this), but at 130° the knee actuator body hits the ankle actuator bodies on the calf; a linkage does not change that. >135° needs the ankle actuators moved off the back of the shank (e.g. into the foot). Knee stays 0–120°. |
| After fixes: clash check of standing + 14 range-extreme poses | **0 clashes** |

## D. Structure / FEA (cad/fea_v3.py)

| item | result |
|---|---|
| knee_clevis | peak 42 MPa (99.5 % element), SF yield 11.94, Goodman 13.63, mesh Δ 10.6 % → NOT converged |
| fall_hip_bracket | peak 33 MPa (99.5 % element), SF yield 15.34, mesh Δ 2.7 % → converged |
| fall_shoulder_housing | peak 56 MPa (99.5 % element), SF yield 8.92, mesh Δ 0.5 % → converged |
| pelvis_hip | peak 44 MPa (99.5 % element), SF yield 11.37, Goodman 12.98, mesh Δ 1.7 % → converged |
| femur_full | peak 47 MPa (99.5 % element), SF yield 10.62, Goodman 12.13, mesh Δ 0.1 % → converged |
| fall_torso_panel | peak 298 MPa (99.5 % element), SF yield 1.34, mesh Δ 4.3 % → converged |
| pelvis_hip first run: stresses of 10⁴–10⁸ MPa, solver not converging | The hip-bracket flange sat 1 mm below the pelvis top wall (top = pelvis_top−5 vs wall inner face pelvis_top−4), so the bracket was floating. Flange now bears on the wall (bolted face contact); re-run. |
| Convergence metric | Peak = 99.5th-percentile element stress; Δ < 10 % between the last two meshes counts as converged. Max-element stress is also reported; it keeps rising at re-entrant corners (singularities) and is not used for SF. |
| FEA memory | First attempt at full-length P2 meshes: TetGen quality refinement gave 100k–970k tets regardless of max-volume (max_volume was ignored with an options string) and OOM. Fixed by setting fixedvolume/maxvolume explicitly, radius-edge 3.0 and AMG-preconditioned CG; single-threaded BLAS. |

## E. Simulation (sim/v3)

| failure | fix / status |
|---|---|
| v3 model with CAD mass properties: plain PD (balance off) falls backwards in ~2 s | CAD centre of mass sits 20–35 mm behind the ankles (knee/ankle actuators behind the legs). With the COM ankle strategy (balance ON) it stands and rejects 125 N / 0.2 s pushes forward and sideways (v2 capsule model: 175 N). Not fixed in hardware geometry; flagged. |
