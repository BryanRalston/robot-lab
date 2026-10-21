# RL walk retrain plan, job 10 (RL Controls, 2026-10-20)

Input: job 4 QC fail (119c2d7, `modules/legs/rl/REPORT.md`). Line numbers marked `@119c2d7` refer to the files at that commit.
Box work was CPU MuJoCo replay only (numpy + mujoco 3.15, a few seconds per run). No JAX or MJX ran on the box.
`[EST]` = estimate, not measured. Measured box numbers are in `results_j4_rescore/*.json` (re-scored with the fixed harness and the regenerated gains).

## 1. Summary

| Failure | Root cause (evidence below) | Fix in job 10 |
|---|---|---|
| walk_a / walk_b fall in < 1 s | **Eval obs mismatch, not training.** The harness fed `payload_frac = 0.0`, but training saw 5e-5 with a normalizer std of 1e-6, so the input was −50 σ. | Harness fixed (auto empty-payload value plus a t=0 obs z-check). Env now emits exactly 0 for the placeholder. |
| Lateral drift (1.127 m/s gate speed but 0.913 m/s net) | No heading feedback. Yaw is only rewarded as gyro rate with σ² = 0.25, so a slow turn costs almost nothing. The policy never observes heading error. | Heading-error observation (obs 109), heading reward, tracking σ 0.25 → 0.10, plus a no-drift gate in eval. |
| Fell under both pushes | The 60 N·s gate was never trained (max ≈ 30 N·s; gate prob 0). Standing kicks were rare. The ±0.25 rad residual limits recovery steps. | Push curriculum up to 350 N × 0.1–0.2 s with a 30 % gate impulse. Stand prob 0.25 in the push stage. Leg residual 0.40 rad. |
| 20 kg carry 0.722 vs 0.8 m/s | The carry stage never converged (MJX fall rate 0.78–0.94, still 0.875 at the end). Payload and rough terrain were added in the same stage. Loose tracking σ. Heading drift (−56° over 20 s). | Carry on flat first (0–22 kg) from a push-trained policy, then a short rough-terrain fine-tune. Tighter tracking and heading terms. |
| (setup) Train ≠ eval model | Training MJX was built before sim/v3 got arm_inertials_r3 and the torso split (forearm 1.988 vs 4.415 kg, torso 19.12 vs 16.63 kg). | `make_model.py` regenerated on current sim/v3 (MJX 65.001 kg; eval scales to 65.0). Neck now XM430 4.1 N·m. |

## 2. Root causes with evidence

### 2.1 walk_a / walk_b < 1 s falls: eval harness, payload_frac
- Training: `joystick.py:187-189 @119c2d7` gives `payload_frac = clip(m_payload/20)`. walk_a and walk_b use `carry: [0.001, 0.001]` (`train_cfg.yaml:39,53`), so the value was always 5.0e-5.
- Policy normalizer: `policy_walk_a.npz` and `policy_walk_b.npz` have `norm__mean__state[12] = 5.0e-5` and `norm__std__state[12] = 1.0e-6` (the Brax std floor). Brax does not clip normalized obs.
- Eval: `eval_box.py` main passed `payload_frac=0.0` for walk and push, which is a **−50 σ** input on one channel. The carry policy trained with 0–20 kg (std 0.284), so 0.0 is in-distribution for it, which is why only carry walked.
- Proof (box CPU replay on the unmodified v3, same harness, only payload_frac changed to 5e-5):
  - walk_a at 1.2 m/s: no fall in 20 s, horizontal speed 1.224 m/s (was a fall at 0.62 s).
  - walk_b at 1.2 m/s: no fall in 20 s, 1.251 m/s (was a fall at 0.70 s).
- With 0.0 they fall at every command tried (0.6/1.0/1.2, gait and stand starts), with flight fraction 0.75–0.88 and min up-vector < 0. So it is not a speed-range or train/eval model issue: walk_a also falls at 0.58 s on the MJX training model itself with 0.0.
- Ruled out: speed range (walk_a was trained to 1.05 only but also fails at 1.0), model mismatch (falls on both models), and the stricter eval fall criterion (the robots really go down to z ≈ 0.13 m).
- Fixed walk_a and walk_b still **fail** the gates: drift (walk_b ends 150° off heading, net x/t 0.22–0.38 m/s), and both pushes (falls at 4.6–5.0 s and 2.1–2.5 s). They cannot do carry (payload is not in their training distribution, and the harness now records that instead of crashing).

### 2.2 Lateral drift
- Reward `tracking_ang = exp(-(gyro_z - cmd_yaw)^2 / 0.25)` (`joystick.py:379 @119c2d7`). A constant 0.05 rad/s turn (57° per 20 s) scores 0.99. There is no world-heading term, and the policy obs has no heading (`obs_spec.json` 107 entries).
- Measured (fixed harness, box): carry policy walk ends at y = 14.2 m and heading +62.7°. Carry trial ends at −56.1°. walk_b ends at −150°.
- The legacy gate uses `hypot(vx, vy)`, so it rewards drift. The body-forward speed is fine (walk_b 1.26 m/s). The robot walks fast, just not straight.

### 2.3 Push failures
- Trained pushes: 50–150 N for 5–10 control steps (`joystick.py:413-420 @119c2d7`), ≤ 150 × 0.2 = 30 N·s, with `push_gate_prob: 0` in every used stage (`train_cfg.yaml:37,51,65`). The gate is 60 N·s lateral during a walk, plus a +0.6 m/s (≈ 39 N·s) kick from stand.
- REPORT §Training: the 50–300 N attempt plateaued at a 72 % fall rate and was dropped. Cause [EST]: it went from 0 straight to the full range, with the policy still at 12 % falls on plain walking. Job 10 adds pushes after walking converges and ramps the range.
- Stand mode freezes the phase and targets `home_q` (`joystick.py:194-199`). Recovery steps must come from the ±0.25 rad residual (`gains.npz action_scale`; `kp = tau_lim/0.25`). That residual is too small for a step on hip pitch and knee. stand_prob was 0.08–0.12, so standing kicks were rare.

### 2.4 Carry 0.722 m/s
- The carry stage never stabilized: MJX fall rate 1.0 → 0.78 → 0.84 → 0.94 → 0.84 → 0.88, with episodes around 12 s (REPORT:72). The final weights came from a run still falling 87.5 % of MJX episodes, and rough terrain was enabled in the same stage (`train_cfg.yaml:68`).
- Speed: MJX tracking 0.622 vs 0.656 commanded (95 %). At a 0.8 m/s command, 95 % undershoot alone gives about 0.76. Heading drift then cut net x/t to 0.651.
- Knee: 20 s walk r_knee peak 243.5 / 258 N·m (94 %). The knee rev B continuous rating is 76.9 N·m, and nothing in training sees it. Job 10 adds a ~10 s EMA RMS penalty above 76.9 N·m, and eval now reports knee RMS (`knee_rms_nm`).

### 2.5 Other mismatches found (smaller)
- Train vs eval model: MJX `humanoid_mjx.xml` was 64.668 kg with the old arms and torso. Eval loads current sim/v3 (forearm 4.415 kg, torso 16.625 kg) scaled to 65.0. The carry policy walked similarly on both (1.07–1.11 m/s at 4 s), so this is secondary. It is fixed by the regen.
- Solver: training uses iterations 4 / ls 8, eval uses 100 / 50. This is kept on purpose (REPORT). It is a sim-to-sim robustness check.
- The forward-push impulse in the REPORT uses 65.0 kg, and the eval mass is 65.0. Consistent.
- Not yet in sim/v3: the 287 mm forearm (R8b), knee rev B inertia/armature, sole pad, chest pad (64.3 kg). Body positions still show forearm 0.26 / hand 0.25 m. `make_model.py` reads sim/v3, so whatever sim/v3 holds when job 10 starts is what trains and what is scored. The brief records the sim/v3 hash. That update is a separate Controls sim/v3 task: no ruling needed, but job 10 is only as current as sim/v3.

## 3. Changes made in this commit
- `modules/legs/rl/eval_box.py`:
  - Empty-payload obs now matches training: it reads `<policy>.meta.json`, and for legacy policies infers it from the normalizer when std < 1e-3.
  - t=0 normalized-obs check (> 8 σ aborts and names the channel).
  - Support for 109-dim heading obs and `leg_action_mult`.
  - New fields `final_y`, `final_heading_deg`, `obs_z_max_t0`, `knee_rms_nm`.
  - **Walk/carry `pass` now also needs net x/t ≥ target and the drift gate** (|y| ≤ 0.5 m, |heading| ≤ 5°). The legacy result is kept as `pass_legacy`.
  - `--xml` option. A carry trial with an OOD payload is recorded, not crashed.
- `modules/legs/rl/test_eval_box.py`: 7 light tests (legacy payload inference, −50 σ regression abort, walk_a stays up 3 s with matched obs, drift gate, heading obs). `MUJOCO_GL=disable python3 -m pytest -q` → 7 passed.
- `modules/legs/rl/joystick.py`:
  - Placeholder payload gives exactly 0.
  - `heading_obs` (sin/cos heading error, ref = reset yaw + ∫cmd_yaw).
  - `heading` reward.
  - `tracking_sigma`.
  - `leg_action_mult` (hip roll/pitch, knee, ankle).
  - `knee_thermal` reward (10 s EMA RMS vs `knee_cont_nm` 76.9).
  - All new knobs default to job-4 behaviour. **Not executed on the box (no JAX). Job 10 step 2 smoke-tests it on the PC.**
- `modules/legs/rl/train.py`: passes the J10 stage knobs and `rewards:` overrides. Writes `<npz>.meta.json` (obs dim, heading_obs, leg_action_mult, payload_empty_frac, xml, mass) for final and mid-run checkpoints. `--smoke-step --stage j10_*` smokes that stage's env.
- `modules/legs/rl/train_cfg.yaml`: new stages `j10_walk`, `j10_push`, `j10_carry`, `j10_rough`. The job-4 stages are unchanged.
- `make_model.py` regen (owned by Controls after job 4): `humanoid_mjx.xml`, `humanoid_mjx_rough.xml`, `gains.npz` (neck kp 80 / τ 4.1 / scale 0.051). `ref_cycle.npz` is unchanged.

## 4. Job 10 training plan (RTX 5060 Laptop, 8 GB)
From scratch: the obs is now 109 and the leg residual is 0.40 rad, so job-4 checkpoints cannot be restored.

| Stage | Steps | Key settings | Throughput basis | Wall [EST] |
|---|---|---|---|---|
| j10_walk | 50M | flat, vx 0.3–1.35, pushes 50–150 N, ref_weight 0.6, heading on | 2750 sps (job-4 flat median) | 5.1 h |
| j10_push | 30M | pushes 50–350 N, gate impulse 30 %, stand 0.25 | 2750 | 3.0 h |
| j10_carry | 30M | flat, payload 0–22 kg, pushes ≤ 300 N, gate 15 % | 2750 [EST; job-4 carry ran on rough] | 3.0 h |
| j10_rough | 10M | ±1 cm heightfield fine-tune | 1711 (job-4 rough median) | 1.6 h |
| Total | 120M | | | **≈ 12.7 h + ~0.5 h compile/eval [EST]** |

Common settings: 1024 envs, the same PPO hyperparameters as job 4, `tracking_sigma` 0.10, rewards `tracking_lin 2.0, tracking_ang 1.0, heading 1.0, knee_thermal 0.5`.

Stop rules (save PC time):
- After j10_walk, if the CPU walk gate fails (fall, or net x/t < 1.10, or drift fail), stop and report. Don't run push/carry on a bad base.
- If the MJX eval fall rate is ≥ 0.5 at 60 % of a stage, stop the stage and report the curve.
- If j10_rough lowers any gate vs j10_carry, ship j10_carry.

## 5. QC gates (box CPU, `eval_box.py`, unmodified sim/v3, noise 0)
1. Walk: command 1.2 m/s, 20 s, no fall, mean horizontal speed ≥ 1.15 **and** net x/t ≥ 1.15, |y_final| ≤ 0.5 m, |heading_final| ≤ 5°.
2. Lateral push: 300 N × 0.2 s (+Y) at 4 s during the 1.2 m/s walk, no fall through 6 s.
3. Forward push: +0.6 m/s at 1 s from stand, upright with speed < 0.5 m/s at 3 s.
4. Carry: 20 kg at (0.25, 0, 0.10), command 0.8 m/s, 20 s, no fall, mean speed and net x/t ≥ 0.8, same drift gate.
5. Report (not gated): leg τ/ω peaks and saturation, knee RMS vs 76.9 N·m, ankle roll vs ±18°, DS/flight, obs_z_max_t0 < 8.

Success = 1–4 pass on one policy file (the shipped `policy_j10.npz`).

## 6. Open items
- **Arbiter:** the numeric drift gate (|y| ≤ 0.5 m, |heading| ≤ 5° over 20 s, plus net x/t) is my proposal. The QC text only says "no drift".
- **Arbiter:** the carry gate payload location. The gate uses Legs' (0.25, 0, 0.10), while the P-042 pose puts the payload at (0.32, 0, 0.415) (R1_STATUS: COM 107 vs 92 mm ahead of the ankle). Training randomizes mass, not position. If P-042 is the gate, add payload-position DR before job 10.
- Not covered by RL: the elbow 0.84 accel scale, WBC_COP_M 16 mm, and the carry bout limits. They are runtime limits on arms, WBC and supervisor, not the walk policy. The policy holds the arms near the carry pose (the residual on arms is ±0.25 rad around fixed offsets).
