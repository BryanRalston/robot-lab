# Arm self-collision supervisor — RL Controls, 2026-10-21

`self_collision.py` (module), `tests/test_self_collision.py` (9 tests), `self_collision_sweep.py` → `self_collision_sweep_y150.json`
(closed-loop), `self_collision_reach.py` → `self_collision_reach.json` (open-loop + reach cost). Config: `controller_config.json`
→ `arm_self_collision`. Supersedes the 63 mm basis of ARM_KNEE_SHROUD_CLEARANCE.md (T&R 925d72e withdrew it).

## What it does (each 1 kHz cycle)
1. **Forward kinematics** (`mj_kinematics`) of sim/v3. The keep-outs are extra geoms with contype=conaffinity=0, so they are
   never part of physics.
2. **Convex distances** (`mj_geomDistance`; capsule/box/convex hull) from the forearm capsule and hand box of each arm to
   every keep-out. Pairs beyond target + influence (50 mm) + 50 mm are culled. Python reference: ~80 µs/cycle for 20 pairs;
   the C++ port is the runtime.
3. **Velocity damping.** Per pair, J_d = nᵀ(J_arm_point − J_obstacle_point) over all dofs, and d_dot ≥ −ξ(d − target)/influence,
   so the approach speed goes to zero at the aim point (target + aim_offset). Inside it the constraint becomes a push-out at
   ξ_in(aim − d)/aim. The correction is a minimum-norm change on the **arm dofs only**. Leg and waist motion, e.g. hip flexion
   lifting the shroud, counts in d_dot, so the arm gets out of the way.
   **Tuned 2026-10-21 (Controls call): influence 50 → 100 mm, ξ_in 3 → 8 m/s, aim_offset 4 mm, ξ = 1.0 m/s, 6 passes.**
   With 0 / 2 / 6 mm offsets the stand worst case gave 15.4 / 17.2 / 19.0 mm. 4 mm was the smallest that held every case at
   ≥ target + 1 mm. No shoulder-outward bias (that needs a ruling).
4. **Repulsive null-space tasks.** `repulsive_tasks(hook)` passes rows plus a desired d_dot to the WBC through the `WBCHook`
   interface (`add_nullspace_task(name, row, rate, weight)`). This is an interface only; the WBC null-space wiring is still open.
5. **Warn/trip events** are logged per pair (T&R: count contacts, target 0/km).

## Keep-outs
| keep-out | geometry | thresholds target / warn / trip |
|---|---|---|
| Chest pad (Arms R18 bf228b1) | torso-frame box x 0…+0.185, y ±0.061, z 0.159–0.281 (116 core + 10 mm gate inside the box); hand box moves with the wrist joints, so wrist flexion is included | 0 / 0 / 0 (gate already in the box) |
| Knee shroud N1, **ID P-156 rev 6b (baad131) — FINAL, valid through rev 8** (ID confirmed the chamfer; z 840 final, Thermal PASS 5fd6a54), both thighs | convex hull, thigh-fixed (follows hip yaw/roll/pitch): x −100…−20, y 86–150, z 840–904; top slopes 861.5 (front) → 904 (aft); 40° chamfer with a 15 mm face on the outboard-top edge; R10 blends not modelled (conservative); +2 mm skin (T&R) | walk / carry / stand **15 / 10 / 5 mm**; crouch / sit / kneel / lowering **20 / 15 / 10 mm** (T&R 925d72e) |
| Carry payload P-042 (carry mode) | torso-frame box at (0.32, 0, 0.415), 212 × 274 × 212 mm. The sim has no payload geom, so the size is **derived from the sim inertia** (20 kg, diag 0.2/0.15/0.2). Torso-fixed, so it is monitored (warn/trip events) and not arm-corrected. **Hook: no geometry in the repo; placeholder, PENDING T&R.** | 15 / 10 / 5 mm to the shroud, zero plume entry |
| K_plume (T&R 925d72e (a)), both thighs | box aft of the aft-wall openings: 30 mm offset + 60 mm, widened by 15° half-angle (46 mm each side/up/down) [EST box hull of the prism] | entry = d ≤ 0. Walk: transit allowed **≤ 0.5 s per pass and ≤ 20 % of any 10 s window** (`TransitTimer`, 1 ms ring buffer). Entry is admitted only if a full pass still fits the window; after 0.30 s inside, the plume becomes a keep-out (push-out) so the pass ends before 0.5 s. **Every other mode: zero entry** (5/2/0 mm). |

**Fall mode:** `filter(..., fall_mode=True, fall_target=pose)` bypasses the supervisor **only** if `fall_pose_clear(pose)`
shows every chest/shroud pair ≥ the crouch-class trip (10 mm) at the current leg pose. Otherwise the supervisor stays on.
After MO=0 the supervisor is off: passive end poses need the geometry check (T&R).

**Inward shoulder-roll soft limit 0°: NOT applied.** Open loop it helps the walk residual (min −72.3 → +39.7 mm). But it
breaks the LB fallback (+30/**−15**/+30/−75), and R18's hands-together-at-chest (−60/**−15**/…) and P-042 close-carry (roll −10)
poses. The brief allowed it only if it doesn't hurt carry or tuck, so the config keeps `shoulder_roll_inward_soft_limit_deg: null`.
Option for Arbiter/Arms: a **walk-mode-only** 0° inward limit (it would not touch fall/carry).

## Results (rev 6b geometry; left arm, right by mirror; kinematic, 1 kHz, arm ≤ 3 rad/s commanded, legs ≤ 2 rad/s)
**Open loop (no supervisor), sampled:**
- full arm soft-limit range × full leg/waist range (20 000): **min −59.4 mm** (interference). 0.24 % of samples are < 15 mm.
- walk residual ±0.25 rad about the hanging arm × walk legs (hip −60…+20, roll ±5, yaw ±10, waist ±15 [ASSUMED walk
  ranges]) (10 000): **min −72.3 mm**, 11.5 % < 15 mm. Worst pose: shoulder pitch +14.1 (swing back), roll −12.9
  (inward), yaw 14.1, wrist yaw −12.6, knee 56.6, waist −12.8. Moving the shroud to y ≤ 150 does not remove the
  swing-back-and-inward hit: the hand reaches the shroud's aft/top.
- hanging arm, straight leg: 87.0 mm (was 63.1 at y 176).

**Closed loop, commanded straight at the worst poses, tuned (shroud min, mm; without → with supervisor):**
| case (mode) | without | **with** | target (+1) |
|---|---|---|---|
| full-range worst (stand) | −58.9 | **17.2** | 15 (16) ✔ |
| walk-residual worst (walk) | −34.7 | **20.0** | 15 (16) ✔ |
| walk swing 12 s, hip −60…+20 @ 1 Hz, arm pushed aft/inward (walk) | −21.0 | **21.2** | 15 (16) ✔ |
| adduction −15 + wrist/yaw −14 + hip flex 50 (walk) | −33.5 | **19.0** | 15 (16) ✔ |
| adduction −14.3 (stand) | 2.0 | **19.0** | ✔ |
| hanging + crouch hip −105 (crouch) | 87.0 | 87.0 | 20 (21) ✔ |
| random ×12 walk / carry / stand / crouch | 23.1 / 87.0 / 57.3 / 87.0 | 23.1 / 87.0 / 64.2 / 87.0 | ✔ |
| chest: wrist-flexed fold (stand) | −46.6 | **4.0** | 0 (gate in box) ✔ |
| chest: hands together at chest (carry) | 0.1 | 4.0 | ✔ |
- **Minimum with the supervisor: 17.2 mm walk/stand/carry class** (full-range stand worst); crouch class 87.0 mm.
- **Plume:** walk swing max pass **0.30 s**, max window **17.8 %** (limits 0.5 s / 20 %). Stand random 14.9 mm (zero entry held).
- **Payload P-042 vs shroud:** min **630.6 mm** over hip −105…+20 and knee 0…135 (5 000 samples), so it passes with a large margin.

**Tracking cost in normal arm motion** (`self_collision_reach.json`; random ±1 rad/s arm command at each sampled pose):
- **Walk set, 10 000 samples** (walk residual ±0.25 rad × assumed walk legs):
  - **11.2 % (1 122) of the sampled poses lie inside the 15 mm target.** With the supervisor these are never reached, so that is the reach cost.
  - From the 8 878 clear poses: **5.7 % of commands are attenuated at all**, mean attenuation 0.8 %, p95 1.4 %, p99 24.5 %, and **0.18 % lose > 50 %**.
- **Carry set, 10 000 samples** (P-042 ±0.25 rad): **0 % attenuated** (no sample comes near a keep-out).

**Fall poses (`fall_pose_clear`, crouch trip 10 mm):** tuck B and LB fallback are **clear** at stand, crouch hip −105,
POSE_PRONE, KNEEL_W1 and side-fall hip roll +15. Minimum slack 24.2 mm (tuck B, side fall, hip roll +15), otherwise
≥ 77 mm. Override is allowed for these poses.

**Reach cost (left arm, standing, wrists 0, 10°/5°/15°/10° grid, 56 479 feasible poses after removing 3 371 torso-box self-collisions):**
| | blocked poses | of which cross-body (hand y < 0; 3 764 total) |
|---|---|---|
| chest keep-out (supervisor) | **291** | **115 (3.1 %)** |
| R18 joint-coupled yaw band (fallback) | 1 338 | 501 (13.3 %) |
- The keep-out blocks 81 poses the band allows, and the band blocks 1 128 poses the keep-out allows. The supervisor costs about
  4.4× less cross-body reach than the joint-space band. (The band is approximated as yaw < the per-elbow bound for pitch
  −120…−10, el ≤ −90.)

## Open items
1. Shroud geometry is final (rev 6b through rev 8); R10 blends not modelled (conservative).
2. Closed: the warn-zone cases are fixed by tuning (min 17.2 mm). No outward bias was added.
3. WBC null-space wiring of `repulsive_tasks` (interface only), and the C++ 1 kHz port (Python is ~80 µs).
4. The walk policy arm offsets aren't in the repo; walk ranges here are assumed. No retrain (the supervisor is the backstop).
5. Payload box size is derived from the inertia (no P-042 box drawing); the **hook is PENDING T&R** (no geometry). The CAD hand replaces the sim/v3 hand box when available.
6. The plume prism is modelled as its bounding box (conservative).

## Chest keep-out from the real STEP (Arms 0a8a3cc)
Box in the torso frame: x ≤ +0.185, y ±0.085, z 0.135–0.305 m. It replaces the R18 box and is checked against the hand and forearm only.
- Pose (30, 127, 60, −140) with no supervisor: the sim hand capsule reaches **−23.9 mm** (penetrating). Arms measured 0.5 mm against the STEP; the gap comes from the larger hand placeholder in sim. With the supervisor: 4.0 mm (gate 0).
- Cross-body reach cost (56 479 grid poses): supervisor-blocked cross-body poses go from 115 to **148** of 3 764 (3.1% → 3.9%). All blocked poses go from 291 to 396 (0.52% → 0.70%), and this count also includes the knee plate.

## Knee-plate keep-out (Legs L77/L78, 916c57f)
The raised L60 top plate is x −175…−40, y 32–228, z 820–828 mm. The twin straps are one box, x −40…−8.5, y 84–176, which is conservative; the notch is ignored. Both are fixed to the thigh, mirrored to R, and use the mode shroud thresholds.
- Open-loop hand-to-plate gap: 26.4 mm at the zero pose and **−17.9 mm at both-leg yaw −35** (Legs reported 0.0). With the supervisor: **19.0 mm** in stand at yaw −35, and 18.7 mm in walk at yaw −35 with adduction −15. The plate is now the binding feature in most cases: full-range worst 17.2, walk ≥17.9.
- Reach cost: commands starting inside the walk target rise from 11.2% to 21.5%; attenuated commands rise from 5.7% to 8.8% (mean 0.8% → 1.25%, p95 1.4% → 7.1%). Carry stays at 0%.
- **Conflict:** with legs in side-fall (hip roll +15), fall pose tuck B puts the left hand 43.6 mm past trip into the plate, so `fall_pose_clear()` refuses the tuck B override there. LB fallback still clears (16.4 mm). Tuck B in stand and in prone has only 1.0 mm of slack.

## Hip-pinch keep-out (T&R ca68f3a/04c7199, ID rev 8b acb9bd5): hip_pinch.py
Gaps are measured rigid edge to rigid edge, ignoring the foam. Pairs: L↔R panel, and hem↔panel on each side. The geometry comes from ID's hip_skirt_r8 (hem R144) plus the r8_asym panel (y86, 40 mm chamfer). Thresholds: warn 35, limit 30, trip 28 mm. Below limit+10 the closing rate is damped to 0 at 30 mm; at trip the closing joint pair is stopped. It applies in every motors-on mode. The two backup rules are dropped.
Exact symmetric boundary (`hip_pinch_boundary.json`; grid pitch −105…40 step 5, roll −12…15 step 1, yaw ±45 step 2.5). The table gives, for each roll, the |yaw| at which trip starts and the pitch range affected:

| roll | trip at yaw ≥ | toe-in ≤ | pitch range |
|---|---|---|---|
| −12 | 17.5 | −17.5 | −15…40 at max yaw |
| −8 | 22.5 | −22.5 | −10…40 |
| −4 | 27.5 | −30 | 0…40 |
| 0 | 32.5 | −35 | 10…40 |
| +4 | 37.5 | — | 20…40 |
| +8 | 42.5 | — | 30…40 |
| ≥ +12 | none | none | |

Compared with T&R's rough rule (roll > −4 and yaw < 15 is safe; closure from roll −12, and at yaw ≥ 22 with roll ≤ 0), the exact boundary depends on pitch (closure needs extension) and moves to larger yaw as roll increases. T&R's rough rule is therefore conservative everywhere except that closures continue up to roll +11 at large yaw.
- Single-leg hem minimum: 32.5 mm at (40, 0, −30). This is warn only and never trips.
- 4000 asymmetric random samples: 0.1% below trip, minimum 11.5 mm.
- T&R 0.77 mm case (+23/+40, yaw 38/46): this model gives **21.6 mm** (L↔R). It is below trip, so the test asserts a trip. The 21 mm difference from T&R is unresolved.
- Controller poses (stand, kneel, R-146, lowering, sit, fall) are all ≥ 104 mm, except hip extension +40 at the limit (32.9, warn).
- Assumed walk/carry: ≥ 75 mm. Job 10 action space (ref_cycle ± 0.25 rad, 600 samples each): uniform 57.4 mm, corners 43.6 mm, with no warn and no trip. Stand corners: 30.5 mm, 6 warn, 0 trip. **Job 10 needs no pose limit.** These are sampled results.
