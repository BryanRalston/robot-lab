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
5. Report knee saturation to Actuators/Legs as a contract risk (1.2 m/s needs margin above 258 Nm or a gait with less knee flexion).

## Neck change (P-019 / A26): 2× Dynamixel XM430-W350-R, 4.1 Nm peak
- `sim/v3/humanoid_v3.xml` already carries the P-019 neck in Robot Lab's working tree (uncommitted, not mine; masses 0.349/0.461 kg, armature 0.0005, ctrlrange ±4.1 Nm). Left for Robot Lab to commit.
- **Legs-owned files, minimal edit (this commit):** `modules/legs/rl/humanoid_mjx.xml` and `humanoid_mjx_rough.xml` neck bodies set to the same values times the existing mass scale (0.499263/0.490 = 1.01891): neckY 0.3556 kg, head 0.4697 kg, inertias scaled, armature 0.079 → 0.0005, neck ctrlrange ±36 → ±4.1 Nm. Model mass 65.0 → 64.668 kg.
- Not regenerated: `make_model.py` outputs (`gains.npz`, `ref_cycle.npz`) and the 65 kg renormalization, to avoid changing inputs mid job 4. Regenerate after job 4 completes. Checkpoints walk_a/walk_b were trained on the old neck (±36 Nm); expect negligible effect (head gravity torque < 1 Nm) but re-score.

## Decisions (Robot Lab, 2026-10-14)
- Scoring and all heavy work (training, sims) run on the bryan PC via Grok Interface; never DESKTOP-B115PVV; box is light work only.
- Queue is sequential: job 4 → 5 → 6 → RL retrain + scoring.
- RL Controls owns `make_model.py` regeneration after job 4 finishes (not before).
- sim/v3 neck (A26) is on main via Legs 8a03242; the MJX neck edit is in eac9a46.
