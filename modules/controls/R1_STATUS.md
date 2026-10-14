# RL Controls — Round 1 status (2026-10-14)
Owner: RL Controls. Took handoff of `modules/legs/wbc/` and the RL walk work (`modules/legs/rl/`) from RL Legs. Grok Build job 4 (RL walk training on Bryan's PC) was left alone; only pushed results are read here.

## Gate G4 (TARGETS.md): walk 1.2 m/s, 20 kg carry, push recovery, domain-randomized sim, CONTRACTS limits — **NOT MET**

| gate (eval_box.py) | WBC r6 closed loop (`legs/grokbuild/results/REPORT.md`, 2026-10-13) | RL (pushed checkpoints, MJX training env eval) |
|---|---|---|
| Walk 20 s @ 1.2 m/s cmd, mean ≥ 1.15 m/s, no fall | FAIL: fell 5.676 s, mean 1.082 m/s (1.20–1.34 m/s until 4.5 s); r_knee hit 258 Nm (1.000 of R1.2, 3.28 % saturated) | walk_a 40M steps (5132740): 0.67 m/s vs 0.68 cmd, 12.5 % episodes fell, up 0.995. **CPU gates not scored.** |
| Lateral push 60 N·s @ t=4, no fall to t=6 | FAIL: fell 4.754 s (0.695 s after push), lateral DCM err ≈ 0.78 m vs ±40 mm step cap | walk_b 30M (63927d4), 50–150 N pushes: 0.60 m/s vs 0.61 cmd, 12.5 % fell, ep len 18.9 s. CPU gate not scored. |
| Forward push +0.6 m/s | not run in r6 | not scored |
| 20 kg carry @ 0.8 m/s 20 s | r6 carry result in `carry.json` (WBC); earlier R-014 nominal forward-sims pass at 0.8/1.0 m/s, no randomization | training from walk_b (in progress, job 4) |
| Domain randomization | none on WBC | `rl/randomize.py` in training |

## Root causes (from repo evidence)
1. **Foot edge roll before the error is visible (WBC).** Sole was flat through 3.5 s, then CoP margin 0 at 4.00 s with DCM error ≈ 0; yaw grew to 15.7°, roll to 43.7°. Realized double support 2.41 % (design 15 %), airborne 9.81 %: the reference gait has a flight-like phase at 1.2 m/s, so the toe-off CoP sits at the sole corner (peak offset 130 mm).
2. **Step-placement authority too small for pushes.** ±40 mm lateral cap vs ≈0.78 m DCM error; wider steps rolled the sole sooner (REPORT.md).
3. **Knee torque margin at 1.2 m/s is zero** (r_knee 258/258 Nm), so the tracker has no reserve for correction.
4. **RL is under-commanded and unscored.** walk_a/walk_b were trained/evaluated at ~0.6–0.7 m/s mean command with 12.5 % falls; no CPU replay against the eval_box gates yet, so nothing counts toward G4.

## Plan
1. Score walk_a, walk_b and job 4 checkpoints on the CPU gates with `rl/eval_box.py` **on the bryan PC via Grok Build** (`controls/SCORING_BRIEF.md`). Not on the box: the box froze from low RAM (crew rule 2026-10-14), so no jax and no sims there. No scores exist yet.
2. RL curriculum to the gate: raise command distribution to 1.2–1.3 m/s, add fall-rate < 1 % and sole-edge (CoP margin) penalty terms, keep CONTRACTS R1.2 torque/velocity limits in the MJX model. RL retrain is queued after jobs 4 (RL train), 5 (lever FEA), 6 (structure r2), via Grok Interface; no job is started by Controls.
3. WBC as fallback/teacher: implement contact-gated unloading (the `WBC_GATE` path already in controller.py) and a reference with ≥ 10 % double support; allow sagittal step shortening via timing, not length; raise lateral step cap with an ankle-roll-aware CoP constraint.
4. Push recovery: add stepping-strategy (capture point) to WBC and push curriculum to 60 N·s lateral in RL.
5. **RL retrain gait with lower knee torque** (Robot Lab, 2026-10-14): reward/penalty on knee RMS and peak torque (target knee RMS ≤ τ_cont, D69 141 N·m at 130 °C; WBC r6 cruise is 105–108 N·m RMS), straighter-knee stance and a reference with longer double support. Add the A40 winding model (`controls/thermal/`) as the torque clip and a Tw > 120 °C penalty. Also watch hip_pitch: with drive loss it hits 120 °C at about 27–29 min of 1.2 m/s cruise.
6. Report knee saturation to Actuators/Legs as a contract risk (1.2 m/s needs margin above 258 Nm or a gait with less knee flexion).

## Neck change (P-019 / A26): 2× Dynamixel XM430-W350-R, 4.1 Nm peak
- `sim/v3/humanoid_v3.xml` already carries the P-019 neck in Robot Lab's working tree (uncommitted, not mine; masses 0.349/0.461 kg, armature 0.0005, ctrlrange ±4.1 Nm). Left for Robot Lab to commit.
- **Legs-owned files, minimal edit (this commit):** `modules/legs/rl/humanoid_mjx.xml` and `humanoid_mjx_rough.xml` neck bodies set to the same values times the existing mass scale (0.499263/0.490 = 1.01891): neckY 0.3556 kg, head 0.4697 kg, inertias scaled, armature 0.079 → 0.0005, neck ctrlrange ±36 → ±4.1 Nm. Model mass 65.0 → 64.668 kg.
- Not regenerated: `make_model.py` outputs (`gains.npz`, `ref_cycle.npz`) and the 65 kg renormalization, to avoid changing inputs mid job 4. Regenerate after job 4 completes. Checkpoints walk_a/walk_b were trained on the old neck (±36 Nm); expect negligible effect (head gravity torque < 1 Nm) but re-score.

## Decisions (Robot Lab, 2026-10-14)
- Scoring and all heavy work (training, sims) run on the bryan PC via Grok Interface; never DESKTOP-B115PVV; box is light work only.
- Queue is sequential: job 4 → 5 → 6 → RL retrain + scoring.
- RL Controls owns `make_model.py` regeneration after job 4 finishes (not before).
- sim/v3 neck (A26) is on main via Legs 8a03242; the MJX neck edit is in eac9a46.

## Thermal layer (A40) status, 2026-10-14
- Limits per RL Thermal 26412c7: derate 130 → 145 °C, torque-off 150 °C (PT1000), 155 °C absolute, design target ≤ 120 °C at 35 °C.
- Drives off housings (P-027); knee drives on the shank saddle (D69).
- 1.2 m/s 60 min: every leg joint is ≤ 115 °C. hip_pitch 113/115 is the closest to the target; with drives on the housing it would be 134/136.
- P-042 carry pose and P-043 hold limits are wired into `thermal/winding_model.py`.

## Arms inertials + P-042 carry (2026-10-14)
- `sim/v3/humanoid_v3.xml`: applied `arms/arm_inertials_r3.json` (a618ce0) to L/R shoulderP, upper_arm, forearm and hand (mass, COM, fullinertia; right side mirrored in y, ixy/iyz sign flipped). The 2 × 1.52 kg shoulder_pitch actuators are merged into the torso body by parallel axis: 18.762 → 21.802 kg, no separate body, so nothing is counted twice inside the sim.
  - Sim total 63.467 → **69.475 kg** (arm 7.437 kg/side moving). The sim torso 18.762 is still the v3 lump, not Torso's re-split (O-T7; bd02c23 has no sim numbers). When Torso re-splits, the 3.04 kg at the shoulders must come out of the lump. Until then the sim overstates mass vs the official rollup (credible ~65.2 kg). gait_lib/eval_box/make_model rescale to 65 kg anyway.
  - This was a direct XML edit; `sim/v3/gen_v3.py` will overwrite it unless the same data is put there.
- **Not propagated to the RL MJX models** (job 4 inputs). Folded into the make_model regen after job 4. `eval_box.py` reads sim/v3 directly, so future scoring sees the new arms.
- P-042 carry primitive + P-043 hold limits: `controls/thermal/winding_model.py` (`CARRY_POSE`, `CARRY_BAND`, `HoldLimiter`).
- Carry static balance (`controls/carry/carry_balance_r1.py`, 65 + 20 kg, feet flat): payload (0.32, 0, 0.415) at the P-042 pose puts the COM 107 mm ahead of the ankle (toe margin 73 mm, ankle 44.6 N·m/leg static) vs 92 mm / 88 mm for Legs' (0.25, 0, 0.10). With Legs' −0.25 rad waist lean-back it is 63 mm (toe margin 117 mm). Static is fine; the dynamic margin (R-014 ankle 1.31× at 1.0 m/s) needs a carry plan regen at the new payload position (Legs/Controls, light WBC run after the plan exists).

## A40 knee on Legs ID plans (2026-10-14, `controls/thermal/knee_id_r1.py` → `knee_id_r1.json`)
35 °C, open housing, drives off housing, Thermal 26412c7 limits; each plan looped for 60 min; iron loss from the plan's own knee speed. τ_cont at 130 °C: 07613D 83.2, D69 141.2 N·m. Winding °C at 60 min, L/R (minutes to 120 / 130 °C):

| trace | knee RMS N·m | 2× 07613D | D69 |
|---|---|---|---|
| walk 1.2 ID r7 ref_ds25 (RL reference) | 74.6 / 73.4 | 115.5 / 113.2 | 63.7 / 63.2 |
| walk 1.2 ID r4 | 74.5 / 73.2 | 115.2 / 112.6 | 63.7 / 63.1 |
| walk 1.2 ID r2 plan (WBC source) | 77.9 / 76.9 | 123.3 / 120.9 (45 / 54 min) | 65.5 / 64.9 |
| carry 20 kg 1.0 ID r4 (R-014, payload 0.25 m) | 78.1 / 75.5 | 123.0 / 116.4 (45 / –) | 65.1 / 63.5 |
| carry 20 kg ID r2 plan (WBC carry source) | 84.4 / 82.3 | **143.0 / 137.2 (23 / 32 min to 130)** | 70.8 / 69.5 |
| WBC r6 closed-loop 1.2 (earlier) | 105 / 108 | runaway (120 at 7–9 min) | 89 / 92 |

Recommendation: the representative 1.2 m/s trace is **walk_1p2_r7 (ref_ds25)**, the reference RL trains on, with r4 agreeing within 0.5 K. The 20 kg carry trace is **r4 carry_20kg_1p0**, the R-014 basis. Re-generate it at the P-042 payload position (x 0.32 / z 0.415), which will raise knee torque. The WBC r6 trace comes from a failing controller (falls, knee saturation) and is an upper bound, not a duty cycle.
- **07613D:** meets the ≤120 °C target on the walk with only 4.5–7 K margin. It fails the target on the r4 carry (L 123 °C) and on the r2 carry plan, which reaches the 130 °C derate at 32 min. It also rests on [EST] Cw/Rwh, no cover penalty, and ideal ID tracking.
- **D69:** about 50–55 K of margin everywhere.
- **D69 is needed** for the 20 kg carry and for a robust 1.2 m/s walk under the 120 °C design target. 07613D is only acceptable if the carry duty is time-limited or Thermal accepts operation inside the derate band.

## O-T5 walk/stand split
**No task simulation exists in the repo.** Controls has no measured or simulated walk/stand time split, so the 20/80 split stays [EST]; I have not produced one. Proposed derivation:
1. Define 3–5 reference tasks with Torso/Robot Lab: tote transfer AMR→conveyor at 5/10/20 m spacing, shelf pick, sit-to-stand.
2. Use public time-motion sources for station layouts, e.g. Agility/GXO videos, timed by frame.
3. Run a light task-level timeline (walk segments at 1.0 m/s from distances; stand/manipulate from the P-042 pick/place cycle times) to get the walk fraction per task.
4. Replace it with logged sim/hardware duty once the RL policy can do the tasks.
