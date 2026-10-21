# Arm envelope vs knee rear-outlet shroud (T&R R-143 B2 condition) — RL Controls, 2026-10-21

**Ask:** T&R 2e9b25c (R143_TOUCH_BURN.md, B2 PASS with conditions) / bec3b82: confirm that in all controller poses the
hand stays **≥ 63 mm** from the knee shroud, with the shroud outboard edge at or inside **y 176**.
T&R's written condition is "no arm pose in stand/walk/carry/prone brings the hand within 30 mm"; both thresholds are reported.

**Verdict: FAIL as a whole-envelope statement. PASS only for the nominal static poses.**
- Nominal hanging arm, standing (and every fixed controller pose: P-042 carry, tuck B, LB fallback, all crouch/kneel/prone
  waypoints): **min 63.1 mm at y 176 (68.1 mm at ID's drawn y 171)**. That is the T&R 63 mm figure with ~0 mm margin.
- Sampled sweep over the arm soft-limit ranges × leg/waist ranges: **min −67.2 mm (interpenetration)**. Worst pose (left
  hand, y 176): shoulder pitch −30.6°, roll −14.0° (adduction), yaw −119.6°, elbow −12.6°, wrist roll 2.5°/pitch −25.9°/
  yaw −16.9°; hip yaw 6.2°, hip roll −11.4°, hip pitch −64.8°, knee 13.9°; waist yaw 52.5°, pitch 21.4°.
- Even the walk-policy residual alone (±0.25 rad about the hanging arm) reaches the shroud: −65 mm at y 176.

## Method
`arm_knee_shroud_clearance.py` (+ `arm_knee_shroud_clearance.json`). MuJoCo 3.15 CPU, `mj_kinematics` +
`mj_geomDistance` only, sim/v3 `humanoid_v3.xml` @ this commit. Base fixed upright, pelvis z 1.16.
- **Hand:** sim/v3 hand box (±16 × ±43 × ±70 mm at −100 mm on the hand body). Hanging inboard face y 0.239 — matches T&R.
- **Shroud:** ID HANDLING_MAP N1, P-156 rev 6 / Option B box x −76…−20, y 89…171, z 860…882 mm (standing frame), attached
  rigidly to `L_thigh` (moves with hip yaw/roll/pitch; the knee does not move it). Envelope case: outboard edge at y 176.
  ID's rev 6 drawn edge (171) **is** inside y 176 — that part of the condition passes.
- **Distance:** surface-to-surface, mm; negative = interpenetration. Left hand → left shroud, and right hand reaching
  across → left shroud (right side by mirror symmetry).
- **Arm ranges:** MJCF ranges with shoulder roll capped at the R-133 127° abduction soft limit; adduction is MJCF 15°.
- **Leg/waist ranges:** full MJCF ranges of hip yaw/roll/pitch, knee, waist yaw/pitch, sampled independently.
- **Policy ranges [ASSUMED]:** the walk/carry policy arm action is a ±0.25 rad residual about fixed offsets
  (RETRAIN_PLAN_J10.md); the offsets are not in this repo, so walk = hanging arm (all 0) ±0.25 and carry = P-042 ±0.25.
- Random sampling (20 000 full-range, 5 000 per policy case) + 1 500-step local refinement from the worst sample.
  A sweep minimum is an upper bound on the true minimum.

## Results (min hand–shroud distance, mm)
| case | y 171 L / R | y 176 L / R |
|---|---|---|
| hanging arm, all waypoint leg poses | 68.1 / 328 | **63.1** / 328 |
| P-042 carry (−60/0/0/−110) | 592 / 674 | 592 / 674 |
| fall tuck B (+5/0/0/0) | 68.0 / 328 | 63.0 / 328 |
| LB fallback +30/−15/+30/−75 | 168 / 405 | 163 / 405 |
| crouch/kneel/prone waypoint arms (KNEEL_W1, POSE_KNEEL, POSE_HANDS, POSE_PRONE)* | ≥ 198 / ≥ 377 | ≥ 197 / ≥ 377 |
| carry policy P-042 ±0.25 × full legs/waist | 218 / 260 | 193 / 224 |
| walk policy hanging ±0.25 × full legs/waist | −67 / −61 | −65 / −44 |
| walk policy ±0.25, waist fixed 0 | −66 / 39 | −69 / 40 |
| full soft-limit range × full legs/waist | −66 / −67 | **−67** / −65 |
*POSE_PRONE elbow 1.8 rad is outside the MJCF elbow range (−140…0°) and was clipped to 0.

Single-joint ±14.3° from the hanging arm, standing, y 176 (left hand): shoulder roll adduction −14.3° → **4.0 mm**;
wrist yaw −14.3° → 49 mm; shoulder yaw +14.3° / wrist roll +14.3° → 62 mm; the rest ≥ 63.

Proposal check (left hand, y 176, policy ±0.25 rad, waist 0): adduction limited to 0° and hip roll/yaw 0 → 2.6 mm
(worst at hip pitch −50°, the thigh lifts the shroud toward the hanging hand); also wrist yaw ±5° → 17.7 mm;
hip roll/yaw ±5° → −4.2 mm. **No joint-space arm soft limit reaches 63 mm** while the hip is allowed to flex.

## Why it fails
1. T&R's 63 mm is a **lateral** gap for a hanging arm and a straight leg (239 − 176). Any arm adduction or inward wrist yaw
   eats it directly (−14° roll → 4 mm).
2. The shroud rides on the thigh: hip flexion (crouch, step, kneel entry) lifts it from z 0.86 toward the hand at z
   0.76–0.90, and hip abduction moves it outboard. T&R's statement "arm swing moves the hand in x, not inboard" holds
   only for the shoulder-pitch swing.

## Proposed fix (no ruling changed; for Robot Lab / Arbiter / T&R)
- **(a) Controls, preferred:** a Cartesian keep-out in the WBC/arm supervisor: hand-box to shroud-box distance ≥ 63 mm
  (or ≥ 30 mm if T&R confirms the 30 mm written condition), as an inequality constraint/clamp computed from the same FK
  every cycle, both hands, all modes. The joint soft limits can't express a constraint that depends on hip pitch.
- **(b) Soft limit, belt-and-braces:** shoulder-roll adduction 15° → 0° (no adduction) while standing/walking; alone it
  is insufficient (2.6 mm above).
- **(c) For T&R/ID:** re-state the B2 condition as a hand-path distance with the leg flexed (not the 239 − 176 lateral
  figure), or move the shroud further inboard/aft. Stand-up, walk and P-042 static poses pass; the risk is
  dynamic/residual arm motion and crouched legs.
- Open: the policy arm offsets (not in repo); TP-G5-15 measures it on hardware.
