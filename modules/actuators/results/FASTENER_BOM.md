# Actuators module BOM: fasteners per actuator unit (R-122 support for RL Materials Ti pricing), D82, 2026-10-21
Script `r122_actuators.py` → `results/fastener_bom.json`, table below (`results/fastener_bom_table.md`).
- **Counts/sizes cited:** HD CSF/CSG catalog Table 24 (flexspline bolts: CSG-14 6×M4, -17 6×M5, -20 8×M5, -25 8×M6) and Table 27 (circular spline: -14 8×M3, -17/-20 16×M3, -25 16×M4); HD note 2: "JIS B 1176 socket head cap screw, strength JIS B 1051 over 12.9". `cad_mass.py` patterns: 8×M5×16 output flange, 6×M3 rear cap, 4×M4 linear front cap; RV12 nut flange 6×M5 (Rollvis p.25, via `cad_mass.py hub()`). Elmo Gold Twitter install guide l.770–773: 4×M2, A2 stainless.
- **[EST]:** all lengths except M5×16; crossed-roller clamp ring 8×M3 (not drawn); AksIM-2 readhead 2×M2 (ring is press-fit, RLS MBD01); M4×12 output flange on CSG-14/-20 units. Arm/waist/wrist housings have no CAD in this module, so their patterns follow the HD tables + the leg pattern [EST].
- **Units counted:** 32 driven units (Electronics R1 l.170: 8/leg, 7/arm, 2 waist); hip_yaw is CSG-17 per `cad/hip_yaw_housing.step` (CONTRACTS §1a still says CSG-14, v3). Neck (CONTRACTS §1a, 2 × CSG-14) is excluded: not in the 32-drive set; Head to confirm owner.
- **Mass:** ISO 4762 nominal geometry, steel 7.85, Ti-6Al-4V 4.43 (ratio 0.564) [CALC, ~+5–10 % vs ISO mass tables].

## Totals (robot)
| | count | steel kg | Ti64 kg | saving kg |
|---|---:|---:|---:|---:|
| all actuator fasteners | 1234 | 2.083 | — | — |
| **non-structural only (Ti candidates)** | **384** | **0.209** | **0.118** | **−0.091** [CALC/EST] |
- Structural = in a torque, bearing-retention or joint load path. Those stay 12.9 steel: HD specifies ≥ 12.9 and Ti-6Al-4V (~900–1000 MPa UTS) is ~class 8.8–10.9, so a Ti swap would need re-rating (more/larger bolts), not a like-for-like swap.
- Non-structural Ti candidates: rear caps/encoder covers (6×M3), AksIM-2 readheads (2×M2), Elmo drive mounts (4×M2 A2). **Drive-mount screws double as a heat-sink clamp: Thermal must accept Ti** (k ~7 vs ~16 W/m·K for A2; clamp force, not screw conduction, dominates [EST]). Ti in 7075 needs anti-galling/anti-seize (Materials).
- Without the drive mounts (if Thermal objects): candidates 256, steel 0.169 → Ti 0.095, saving −0.074 kg.

## Under-booking flag (not a booking; for the Arbiter's R13 regen)
`cad_mass.py` books 0.0348 kg screws per leg rotary unit and 0.0136 kg per linear unit (plus connector allowance). Counted here: CSG-25 rotary 0.122, CSG-17 0.079, linear 0.035 kg per unit. **Legs alone: counted ≈ 0.82 kg vs booked ≈ 0.30 kg → ≈ +0.5 kg possible under-booking [CALC/EST lengths]** (the HD component-set weights exclude bolts). Arm/waist unit lines (e.g. `d70_wrist_rotary.py` fasteners_EST 0.015) are similarly low. Needs a measured/CAD fastener count before it is booked; it works against R-122.

## Per-line table
| unit | item | size | n/unit | n/robot | grade | structural | reason | basis | steel g (robot) | Ti64 g (robot) |
|---|---|---|---:|---:|---|---|---|---|---:|---:|
| hip_yaw (CSG-17) | flexspline -> output hub | M5x12 | 6 | 12 | 12.9 steel | YES | gear torque path; HD requires >= 12.9 | HD Table 24; L [EST] | 40.6 | — |
| hip_yaw (CSG-17) | circular spline -> housing | M3x10 | 16 | 32 | 12.9 steel | YES | gear torque reaction | HD Table 27; L [EST] | 28.3 | — |
| hip_yaw (CSG-17) | output flange -> customer | M5x16 | 8 | 16 | 12.9 steel | YES | joint load path (interface, CONTRACTS 1c) | cad_mass.py 8 x M5x16 (legs); M4x12 on CSG-14/20 [EST] | 63.9 | — |
| hip_yaw (CSG-17) | crossed-roller clamp ring | M3x8 | 8 | 16 | 12.9 steel | YES | retains bearing outer ring axially (fall/impact load) | [EST] (Arms R13 clamp ring, count not drawn) | 12.4 | — |
| hip_yaw (CSG-17) | rear cap / encoder cover | M3x8 | 6 | 12 | 12.9 steel | no | cover only; motor reaction goes via stator bond land to tube | cad_mass.py 6 x M3; L [EST] | 9.3 | 5.2 |
| hip_yaw (CSG-17) | AksIM-2 readhead | M2x6 | 2 | 4 | A2 | no | locates readhead, no load; ring is press-fit | [EST] (RLS MBD01: ring press-fit) | 1.3 | 0.7 |
| hip_yaw (CSG-17) | Elmo drive mount | M2x6 | 4 | 8 | A2 | no | board/heat-sink mount; thermal contact (Thermal to OK Ti) | Elmo install guide l.770-773 (4 x M2 A2); L [EST] | 2.5 | 1.4 |
| hip_roll (CSG-25) | flexspline -> output hub | M6x14 | 8 | 16 | 12.9 steel | YES | gear torque path; HD requires >= 12.9 | HD Table 24; L [EST] | 92.0 | — |
| hip_roll (CSG-25) | circular spline -> housing | M4x12 | 16 | 32 | 12.9 steel | YES | gear torque reaction | HD Table 27; L [EST] | 62.9 | — |
| hip_roll (CSG-25) | output flange -> customer | M5x16 | 8 | 16 | 12.9 steel | YES | joint load path (interface, CONTRACTS 1c) | cad_mass.py 8 x M5x16 (legs); M4x12 on CSG-14/20 [EST] | 63.9 | — |
| hip_roll (CSG-25) | crossed-roller clamp ring | M3x8 | 8 | 16 | 12.9 steel | YES | retains bearing outer ring axially (fall/impact load) | [EST] (Arms R13 clamp ring, count not drawn) | 12.4 | — |
| hip_roll (CSG-25) | rear cap / encoder cover | M3x8 | 6 | 12 | 12.9 steel | no | cover only; motor reaction goes via stator bond land to tube | cad_mass.py 6 x M3; L [EST] | 9.3 | 5.2 |
| hip_roll (CSG-25) | AksIM-2 readhead | M2x6 | 2 | 4 | A2 | no | locates readhead, no load; ring is press-fit | [EST] (RLS MBD01: ring press-fit) | 1.3 | 0.7 |
| hip_roll (CSG-25) | Elmo drive mount | M2x6 | 4 | 8 | A2 | no | board/heat-sink mount; thermal contact (Thermal to OK Ti) | Elmo install guide l.770-773 (4 x M2 A2); L [EST] | 2.5 | 1.4 |
| waist_yaw (CSG-17) | flexspline -> output hub | M5x12 | 6 | 6 | 12.9 steel | YES | gear torque path; HD requires >= 12.9 | HD Table 24; L [EST] | 20.3 | — |
| waist_yaw (CSG-17) | circular spline -> housing | M3x10 | 16 | 16 | 12.9 steel | YES | gear torque reaction | HD Table 27; L [EST] | 14.2 | — |
| waist_yaw (CSG-17) | output flange -> customer | M5x16 | 8 | 8 | 12.9 steel | YES | joint load path (interface, CONTRACTS 1c) | cad_mass.py 8 x M5x16 (legs); M4x12 on CSG-14/20 [EST] | 32.0 | — |
| waist_yaw (CSG-17) | crossed-roller clamp ring | M3x8 | 8 | 8 | 12.9 steel | YES | retains bearing outer ring axially (fall/impact load) | [EST] (Arms R13 clamp ring, count not drawn) | 6.2 | — |
| waist_yaw (CSG-17) | rear cap / encoder cover | M3x8 | 6 | 6 | 12.9 steel | no | cover only; motor reaction goes via stator bond land to tube | cad_mass.py 6 x M3; L [EST] | 4.6 | 2.6 |
| waist_yaw (CSG-17) | AksIM-2 readhead | M2x6 | 2 | 2 | A2 | no | locates readhead, no load; ring is press-fit | [EST] (RLS MBD01: ring press-fit) | 0.6 | 0.4 |
| waist_yaw (CSG-17) | Elmo drive mount | M2x6 | 4 | 4 | A2 | no | board/heat-sink mount; thermal contact (Thermal to OK Ti) | Elmo install guide l.770-773 (4 x M2 A2); L [EST] | 1.3 | 0.7 |
| waist_pitch (CSG-25) | flexspline -> output hub | M6x14 | 8 | 8 | 12.9 steel | YES | gear torque path; HD requires >= 12.9 | HD Table 24; L [EST] | 46.0 | — |
| waist_pitch (CSG-25) | circular spline -> housing | M4x12 | 16 | 16 | 12.9 steel | YES | gear torque reaction | HD Table 27; L [EST] | 31.5 | — |
| waist_pitch (CSG-25) | output flange -> customer | M5x16 | 8 | 8 | 12.9 steel | YES | joint load path (interface, CONTRACTS 1c) | cad_mass.py 8 x M5x16 (legs); M4x12 on CSG-14/20 [EST] | 32.0 | — |
| waist_pitch (CSG-25) | crossed-roller clamp ring | M3x8 | 8 | 8 | 12.9 steel | YES | retains bearing outer ring axially (fall/impact load) | [EST] (Arms R13 clamp ring, count not drawn) | 6.2 | — |
| waist_pitch (CSG-25) | rear cap / encoder cover | M3x8 | 6 | 6 | 12.9 steel | no | cover only; motor reaction goes via stator bond land to tube | cad_mass.py 6 x M3; L [EST] | 4.6 | 2.6 |
| waist_pitch (CSG-25) | AksIM-2 readhead | M2x6 | 2 | 2 | A2 | no | locates readhead, no load; ring is press-fit | [EST] (RLS MBD01: ring press-fit) | 0.6 | 0.4 |
| waist_pitch (CSG-25) | Elmo drive mount | M2x6 | 4 | 4 | A2 | no | board/heat-sink mount; thermal contact (Thermal to OK Ti) | Elmo install guide l.770-773 (4 x M2 A2); L [EST] | 1.3 | 0.7 |
| shoulder_pitch (CSG-25) | flexspline -> output hub | M6x14 | 8 | 16 | 12.9 steel | YES | gear torque path; HD requires >= 12.9 | HD Table 24; L [EST] | 92.0 | — |
| shoulder_pitch (CSG-25) | circular spline -> housing | M4x12 | 16 | 32 | 12.9 steel | YES | gear torque reaction | HD Table 27; L [EST] | 62.9 | — |
| shoulder_pitch (CSG-25) | output flange -> customer | M5x16 | 8 | 16 | 12.9 steel | YES | joint load path (interface, CONTRACTS 1c) | cad_mass.py 8 x M5x16 (legs); M4x12 on CSG-14/20 [EST] | 63.9 | — |
| shoulder_pitch (CSG-25) | crossed-roller clamp ring | M3x8 | 8 | 16 | 12.9 steel | YES | retains bearing outer ring axially (fall/impact load) | [EST] (Arms R13 clamp ring, count not drawn) | 12.4 | — |
| shoulder_pitch (CSG-25) | rear cap / encoder cover | M3x8 | 6 | 12 | 12.9 steel | no | cover only; motor reaction goes via stator bond land to tube | cad_mass.py 6 x M3; L [EST] | 9.3 | 5.2 |
| shoulder_pitch (CSG-25) | AksIM-2 readhead | M2x6 | 2 | 4 | A2 | no | locates readhead, no load; ring is press-fit | [EST] (RLS MBD01: ring press-fit) | 1.3 | 0.7 |
| shoulder_pitch (CSG-25) | Elmo drive mount | M2x6 | 4 | 8 | A2 | no | board/heat-sink mount; thermal contact (Thermal to OK Ti) | Elmo install guide l.770-773 (4 x M2 A2); L [EST] | 2.5 | 1.4 |
| shoulder_roll (CSG-25) | flexspline -> output hub | M6x14 | 8 | 16 | 12.9 steel | YES | gear torque path; HD requires >= 12.9 | HD Table 24; L [EST] | 92.0 | — |
| shoulder_roll (CSG-25) | circular spline -> housing | M4x12 | 16 | 32 | 12.9 steel | YES | gear torque reaction | HD Table 27; L [EST] | 62.9 | — |
| shoulder_roll (CSG-25) | output flange -> customer | M5x16 | 8 | 16 | 12.9 steel | YES | joint load path (interface, CONTRACTS 1c) | cad_mass.py 8 x M5x16 (legs); M4x12 on CSG-14/20 [EST] | 63.9 | — |
| shoulder_roll (CSG-25) | crossed-roller clamp ring | M3x8 | 8 | 16 | 12.9 steel | YES | retains bearing outer ring axially (fall/impact load) | [EST] (Arms R13 clamp ring, count not drawn) | 12.4 | — |
| shoulder_roll (CSG-25) | rear cap / encoder cover | M3x8 | 6 | 12 | 12.9 steel | no | cover only; motor reaction goes via stator bond land to tube | cad_mass.py 6 x M3; L [EST] | 9.3 | 5.2 |
| shoulder_roll (CSG-25) | AksIM-2 readhead | M2x6 | 2 | 4 | A2 | no | locates readhead, no load; ring is press-fit | [EST] (RLS MBD01: ring press-fit) | 1.3 | 0.7 |
| shoulder_roll (CSG-25) | Elmo drive mount | M2x6 | 4 | 8 | A2 | no | board/heat-sink mount; thermal contact (Thermal to OK Ti) | Elmo install guide l.770-773 (4 x M2 A2); L [EST] | 2.5 | 1.4 |
| shoulder_yaw (CSG-17) | flexspline -> output hub | M5x12 | 6 | 12 | 12.9 steel | YES | gear torque path; HD requires >= 12.9 | HD Table 24; L [EST] | 40.6 | — |
| shoulder_yaw (CSG-17) | circular spline -> housing | M3x10 | 16 | 32 | 12.9 steel | YES | gear torque reaction | HD Table 27; L [EST] | 28.3 | — |
| shoulder_yaw (CSG-17) | output flange -> customer | M5x16 | 8 | 16 | 12.9 steel | YES | joint load path (interface, CONTRACTS 1c) | cad_mass.py 8 x M5x16 (legs); M4x12 on CSG-14/20 [EST] | 63.9 | — |
| shoulder_yaw (CSG-17) | crossed-roller clamp ring | M3x8 | 8 | 16 | 12.9 steel | YES | retains bearing outer ring axially (fall/impact load) | [EST] (Arms R13 clamp ring, count not drawn) | 12.4 | — |
| shoulder_yaw (CSG-17) | rear cap / encoder cover | M3x8 | 6 | 12 | 12.9 steel | no | cover only; motor reaction goes via stator bond land to tube | cad_mass.py 6 x M3; L [EST] | 9.3 | 5.2 |
| shoulder_yaw (CSG-17) | AksIM-2 readhead | M2x6 | 2 | 4 | A2 | no | locates readhead, no load; ring is press-fit | [EST] (RLS MBD01: ring press-fit) | 1.3 | 0.7 |
| shoulder_yaw (CSG-17) | Elmo drive mount | M2x6 | 4 | 8 | A2 | no | board/heat-sink mount; thermal contact (Thermal to OK Ti) | Elmo install guide l.770-773 (4 x M2 A2); L [EST] | 2.5 | 1.4 |
| elbow (CSG-20) | flexspline -> output hub | M5x12 | 8 | 16 | 12.9 steel | YES | gear torque path; HD requires >= 12.9 | HD Table 24; L [EST] | 54.1 | — |
| elbow (CSG-20) | circular spline -> housing | M3x10 | 16 | 32 | 12.9 steel | YES | gear torque reaction | HD Table 27; L [EST] | 28.3 | — |
| elbow (CSG-20) | output flange -> customer | M4x12 | 8 | 16 | 12.9 steel | YES | joint load path (interface, CONTRACTS 1c) | cad_mass.py 8 x M5x16 (legs); M4x12 on CSG-14/20 [EST] | 31.5 | — |
| elbow (CSG-20) | crossed-roller clamp ring | M3x8 | 8 | 16 | 12.9 steel | YES | retains bearing outer ring axially (fall/impact load) | [EST] (Arms R13 clamp ring, count not drawn) | 12.4 | — |
| elbow (CSG-20) | rear cap / encoder cover | M3x8 | 6 | 12 | 12.9 steel | no | cover only; motor reaction goes via stator bond land to tube | cad_mass.py 6 x M3; L [EST] | 9.3 | 5.2 |
| elbow (CSG-20) | AksIM-2 readhead | M2x6 | 2 | 4 | A2 | no | locates readhead, no load; ring is press-fit | [EST] (RLS MBD01: ring press-fit) | 1.3 | 0.7 |
| elbow (CSG-20) | Elmo drive mount | M2x6 | 4 | 8 | A2 | no | board/heat-sink mount; thermal contact (Thermal to OK Ti) | Elmo install guide l.770-773 (4 x M2 A2); L [EST] | 2.5 | 1.4 |
| wrist_roll (CSG-14) | flexspline -> output hub | M4x10 | 6 | 12 | 12.9 steel | YES | gear torque path; HD requires >= 12.9 | HD Table 24; L [EST] | 21.2 | — |
| wrist_roll (CSG-14) | circular spline -> housing | M3x10 | 8 | 16 | 12.9 steel | YES | gear torque reaction | HD Table 27; L [EST] | 14.2 | — |
| wrist_roll (CSG-14) | output flange -> customer | M4x12 | 8 | 16 | 12.9 steel | YES | joint load path (interface, CONTRACTS 1c) | cad_mass.py 8 x M5x16 (legs); M4x12 on CSG-14/20 [EST] | 31.5 | — |
| wrist_roll (CSG-14) | crossed-roller clamp ring | M3x8 | 8 | 16 | 12.9 steel | YES | retains bearing outer ring axially (fall/impact load) | [EST] (Arms R13 clamp ring, count not drawn) | 12.4 | — |
| wrist_roll (CSG-14) | rear cap / encoder cover | M3x8 | 6 | 12 | 12.9 steel | no | cover only; motor reaction goes via stator bond land to tube | cad_mass.py 6 x M3; L [EST] | 9.3 | 5.2 |
| wrist_roll (CSG-14) | AksIM-2 readhead | M2x6 | 2 | 4 | A2 | no | locates readhead, no load; ring is press-fit | [EST] (RLS MBD01: ring press-fit) | 1.3 | 0.7 |
| wrist_roll (CSG-14) | Elmo drive mount | M2x6 | 4 | 8 | A2 | no | board/heat-sink mount; thermal contact (Thermal to OK Ti) | Elmo install guide l.770-773 (4 x M2 A2); L [EST] | 2.5 | 1.4 |
| wrist_pitch (CSG-14, D76) | flexspline -> output hub | M4x10 | 6 | 12 | 12.9 steel | YES | gear torque path; HD requires >= 12.9 | HD Table 24; L [EST] | 21.2 | — |
| wrist_pitch (CSG-14, D76) | circular spline -> housing | M3x10 | 8 | 16 | 12.9 steel | YES | gear torque reaction | HD Table 27; L [EST] | 14.2 | — |
| wrist_pitch (CSG-14, D76) | output flange -> customer | M4x12 | 8 | 16 | 12.9 steel | YES | joint load path (interface, CONTRACTS 1c) | cad_mass.py 8 x M5x16 (legs); M4x12 on CSG-14/20 [EST] | 31.5 | — |
| wrist_pitch (CSG-14, D76) | crossed-roller clamp ring | M3x8 | 8 | 16 | 12.9 steel | YES | retains bearing outer ring axially (fall/impact load) | [EST] (Arms R13 clamp ring, count not drawn) | 12.4 | — |
| wrist_pitch (CSG-14, D76) | rear cap / encoder cover | M3x8 | 6 | 12 | 12.9 steel | no | cover only; motor reaction goes via stator bond land to tube | cad_mass.py 6 x M3; L [EST] | 9.3 | 5.2 |
| wrist_pitch (CSG-14, D76) | AksIM-2 readhead | M2x6 | 2 | 4 | A2 | no | locates readhead, no load; ring is press-fit | [EST] (RLS MBD01: ring press-fit) | 1.3 | 0.7 |
| wrist_pitch (CSG-14, D76) | Elmo drive mount | M2x6 | 4 | 8 | A2 | no | board/heat-sink mount; thermal contact (Thermal to OK Ti) | Elmo install guide l.770-773 (4 x M2 A2); L [EST] | 2.5 | 1.4 |
| wrist_yaw (CSG-14, D76) | flexspline -> output hub | M4x10 | 6 | 12 | 12.9 steel | YES | gear torque path; HD requires >= 12.9 | HD Table 24; L [EST] | 21.2 | — |
| wrist_yaw (CSG-14, D76) | circular spline -> housing | M3x10 | 8 | 16 | 12.9 steel | YES | gear torque reaction | HD Table 27; L [EST] | 14.2 | — |
| wrist_yaw (CSG-14, D76) | output flange -> customer | M4x12 | 8 | 16 | 12.9 steel | YES | joint load path (interface, CONTRACTS 1c) | cad_mass.py 8 x M5x16 (legs); M4x12 on CSG-14/20 [EST] | 31.5 | — |
| wrist_yaw (CSG-14, D76) | crossed-roller clamp ring | M3x8 | 8 | 16 | 12.9 steel | YES | retains bearing outer ring axially (fall/impact load) | [EST] (Arms R13 clamp ring, count not drawn) | 12.4 | — |
| wrist_yaw (CSG-14, D76) | rear cap / encoder cover | M3x8 | 6 | 12 | 12.9 steel | no | cover only; motor reaction goes via stator bond land to tube | cad_mass.py 6 x M3; L [EST] | 9.3 | 5.2 |
| wrist_yaw (CSG-14, D76) | AksIM-2 readhead | M2x6 | 2 | 4 | A2 | no | locates readhead, no load; ring is press-fit | [EST] (RLS MBD01: ring press-fit) | 1.3 | 0.7 |
| wrist_yaw (CSG-14, D76) | Elmo drive mount | M2x6 | 4 | 8 | A2 | no | board/heat-sink mount; thermal contact (Thermal to OK Ti) | Elmo install guide l.770-773 (4 x M2 A2); L [EST] | 2.5 | 1.4 |
| hip_pitch screw (RV12) | RV12 nut flange -> rotor hub | M5x12 | 6 | 24 | 12.9 steel | YES | full screw axial force | Rollvis p.25 via cad_mass.py hub(); L [EST] | 81.1 | — |
| hip_pitch screw (RV12) | front cap / 7202 bearing retainer | M4x12 | 4 | 16 | 12.9 steel | YES | carries angular-contact preload and axial force | cad_mass.py 4 x M4; L [EST] | 31.5 | — |
| hip_pitch screw (RV12) | rear cap / encoder cover | M3x8 | 6 | 24 | 12.9 steel | no | cover only | cad_mass.py 6 x M3; L [EST] | 18.6 | 10.5 |
| hip_pitch screw (RV12) | AksIM-2 readhead | M2x6 | 2 | 8 | A2 | no | no load | [EST] | 2.5 | 1.4 |
| hip_pitch screw (RV12) | Elmo drive mount | M2x6 | 4 | 16 | A2 | no | board mount; thermal contact (Thermal to OK Ti) | Elmo install guide (4 x M2 A2) | 5.0 | 2.8 |
| knee screw (RV12) | RV12 nut flange -> rotor hub | M5x12 | 6 | 24 | 12.9 steel | YES | full screw axial force | Rollvis p.25 via cad_mass.py hub(); L [EST] | 81.1 | — |
| knee screw (RV12) | front cap / 7202 bearing retainer | M4x12 | 4 | 16 | 12.9 steel | YES | carries angular-contact preload and axial force | cad_mass.py 4 x M4; L [EST] | 31.5 | — |
| knee screw (RV12) | rear cap / encoder cover | M3x8 | 6 | 24 | 12.9 steel | no | cover only | cad_mass.py 6 x M3; L [EST] | 18.6 | 10.5 |
| knee screw (RV12) | AksIM-2 readhead | M2x6 | 2 | 8 | A2 | no | no load | [EST] | 2.5 | 1.4 |
| knee screw (RV12) | Elmo drive mount | M2x6 | 4 | 16 | A2 | no | board mount; thermal contact (Thermal to OK Ti) | Elmo install guide (4 x M2 A2) | 5.0 | 2.8 |
| ankle screw (RV12) | RV12 nut flange -> rotor hub | M5x12 | 6 | 24 | 12.9 steel | YES | full screw axial force | Rollvis p.25 via cad_mass.py hub(); L [EST] | 81.1 | — |
| ankle screw (RV12) | front cap / 7202 bearing retainer | M4x12 | 4 | 16 | 12.9 steel | YES | carries angular-contact preload and axial force | cad_mass.py 4 x M4; L [EST] | 31.5 | — |
| ankle screw (RV12) | rear cap / encoder cover | M3x8 | 6 | 24 | 12.9 steel | no | cover only | cad_mass.py 6 x M3; L [EST] | 18.6 | 10.5 |
| ankle screw (RV12) | AksIM-2 readhead | M2x6 | 2 | 8 | A2 | no | no load | [EST] | 2.5 | 1.4 |
| ankle screw (RV12) | Elmo drive mount | M2x6 | 4 | 16 | A2 | no | board mount; thermal contact (Thermal to OK Ti) | Elmo install guide (4 x M2 A2) | 5.0 | 2.8 |
