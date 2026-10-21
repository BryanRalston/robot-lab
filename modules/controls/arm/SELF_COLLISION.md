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
   so the approach speed goes to zero at the target. Inside the target the constraint becomes a push-out at ξ_in(target − d)/target.
   The correction is a minimum-norm change on the **arm dofs only**. Leg and waist motion, e.g. hip flexion lifting the
   shroud, counts in d_dot, so the arm gets out of the way. ξ = 1.0 m/s, ξ_in = 3.0 m/s, 6 passes.
4. **Repulsive null-space tasks.** `repulsive_tasks(hook)` passes rows plus a desired d_dot to the WBC through the `WBCHook`
   interface (`add_nullspace_task(name, row, rate, weight)`). This is an interface only; the WBC null-space wiring is still open.
5. **Warn/trip events** are logged per pair (T&R: count contacts, target 0/km).

## Keep-outs
| keep-out | geometry | thresholds target / warn / trip |
|---|---|---|
| Chest pad (Arms R18 bf228b1) | torso-frame box x 0…+0.185, y ±0.061, z 0.159–0.281 (116 core + 10 mm gate inside the box); hand box moves with the wrist joints, so wrist flexion is included | 0 / 0 / 0 (gate already in the box) |
| Knee shroud N1, **ID P-156 rev 6b (baad131)**, both thighs | convex hull, thigh-fixed (follows hip yaw/roll/pitch): x −100…−20, y 86–150, z 840–904; top slopes 861.5 (front) → 904 (aft); **40° chamfer on the outboard-top edge, 15 mm wide [EST: ID gives the angle + R10, not the width; R10 ignored = conservative]**; +2 mm skin (T&R) | walk / carry / stand **15 / 10 / 5 mm**; crouch / sit / kneel / lowering **20 / 15 / 10 mm** (T&R 925d72e) |
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

**Closed loop, commanded straight at the worst poses (shroud min, mm; without → with supervisor):**
| case (mode) | without | **with** | vs target |
|---|---|---|---|
| walk-residual worst (walk) | −34.7 | **15.1** | ≥ 15 ✔ |
| walk swing 12 s, hip −60…+20 @ 1 Hz, arm pushed aft/inward (walk) | −21.0 | **15.6** | ≥ 15 ✔ |
| adduction −15 + wrist/yaw −14 + hip flex 50 (walk) | −33.5 | **13.7** | < 15 target, ≥ 10 warn |
| adduction −14.3 (stand) | 2.0 | **15.0** | ✔ |
| full-range worst (stand) | −58.9 | **11.3** | < 15 target, ≥ 10 warn |
| hanging + crouch hip −105 (crouch) | 87.0 | 87.0 | ✔ (≥ 20) |
| random ×12 per mode (walk/carry/stand/crouch) | 23.1 / 87.0 / 57.3 / 87.0 | 23.1 / 87.0 / 57.3 / 87.0 | ✔ |
| chest: wrist-flexed fold −60/−15/−100/−130, wrist pitch 70 | −46.6 | **0.0** (gate held) | ✔ |
| chest: hands together at chest (carry) | 0.1 | 0.1 | ✔ (R18 1.9 mm basis) |
- **Plume:** walk swing 12 s with the supervisor gives 2.81 s inside, **max pass 0.31 s (≤ 0.5)** and **max window 15.3 %
  (≤ 20 %)**. Stand random without the supervisor enters the plume (−14.9 mm); with it, 6.2 mm, so zero entry is held.
  Crouch/carry: no entry.
- **No case reaches trip (5 mm walk/stand, 10 mm crouch).** Two cases settle at 11–14 mm, between warn and target. The leg
  and waist motion drives the shroud into the hand faster than the damping band recovers. Fix options: bigger influence
  (50 → 80 mm) or ξ_in, or let the supervisor also bias shoulder roll outboard on warn (T&R's "trip = bias abduction").
  **Open.**

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
1. ID: chamfer width (modelled 15 mm) and the R10 blend; rev 6b stack top z 840 is pending Thermal.
2. Warn-zone cases at 11.3 / 13.7 mm. Tune the influence distance, or add an abduction bias on warn (T&R). Needs a ruling if
   it's a behaviour change.
3. WBC null-space wiring of `repulsive_tasks` (interface only), and the C++ 1 kHz port (Python is ~80 µs).
4. The walk policy arm offsets aren't in the repo; walk ranges here are assumed. No retrain (the supervisor is the backstop).
5. Payload/hook keep-out for carry (T&R) isn't modelled yet. The CAD hand replaces the sim/v3 hand box when available.
6. The plume prism is modelled as its bounding box (conservative).
