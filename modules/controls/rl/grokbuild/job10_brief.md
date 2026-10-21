# Grok Build brief: job 10, RL walk retrain (bryan PC, RTX 5060, WSL2)

Owner: RL Controls. Plan and evidence: `modules/controls/rl/RETRAIN_PLAN_J10.md`. Use the same WSL venv and repo clone as job 4 (JAX 0.11.2, Playground 0.2.0, Brax 0.14.2, MuJoCo/MJX 3.15.0). Report honestly: no numbers you did not measure.

**Pinned inputs:**
- sim/v3 = **4115f6e** (J10 hardware update: forearm 287, knee rev B fins, fallback SP 67A 6 mm sole, chest pad, neck XM430; 64.827 kg). Robot mass per **Arbiter R-118**: nominal 67.1 kg, DR 65.0–68.5 kg in training, gates at 67.1 plus the 65.0/68.5 corners.
- Gates per **Arbiter R-117**.
- Usage MODE (`/workspace/usage/status.md`): **NORMAL**, both Grok Bot and the Grok subscription. The file was last updated 2026-10-14, so re-check the Grok Build log first; if the subscription is ≥ 75 % (CAUTION), ask Bryan via Robot Lab before starting the ~13 h run.

## 0. Sync and record inputs
```bash
cd <job-4 WSL clone of robot-lab> && git pull --rebase
git log -1 --format='%h %s' ; git log -1 --format='%h' -- sim/v3/humanoid_v3.xml
cd modules/legs/rl
export XLA_PYTHON_CLIENT_PREALLOCATE=false MUJOCO_GL=egl RL_RUNS=/root/rl-runs-j10
```
Record both hashes in the report. **If the sim/v3 hash is not 4115f6e, stop and report** (the model changed under the plan). Training inputs (make_model output, R-118 mass, randomize/eval_box) are pinned at **adcdd73**: `git merge-base --is-ancestor adcdd73 HEAD` must succeed, and `git diff adcdd73 HEAD -- modules/legs/rl sim/v3` must be empty except for this brief's own outputs. Use a new `RL_RUNS` dir so job-4 checkpoints are not picked up by `restore`.

## 1. Regenerate the MJX model from the current sim/v3 (CPU, ~1 min)
```bash
python make_model.py
```
Expect `mass 67.101` and `stand settle z 1.1495 up 0.999` (sim/v3 4115f6e, R-118). The files should be unchanged against the repo; if they differ, report the diff. Commit any diff in `humanoid_mjx*.xml`, `gains.npz` or `ref_cycle.npz` with the report.

## 2. Harness tests and smoke (must pass before training)
```bash
MUJOCO_GL=disable python -m pytest -q test_eval_box.py    # expect 10 passed
python train.py --smoke-step --stage j10_walk               # expect obs {'state': (109,), 'privileged_state': (149,)}, finite rewards
```
If the smoke fails, stop and report the traceback. Do not patch reward or obs semantics yourself. Fixing a typo or a shape bug is fine; note it.

## 3. Train (sequential, same terminal, log to file)
```bash
for s in j10_walk j10_push j10_carry j10_rough; do
  python train.py --stage $s 2>&1 | tee logs/$s.out
  cp logs/${s}_final.npz policy_$s.npz && cp logs/${s}_final.meta.json policy_$s.meta.json
  python eval_box.py --policy policy_$s.npz --tag $s --gif
done
```
Run the stop rules between stages (check `results/<stage>_*.json`):
- After **j10_walk**: if `walk` has a fall, or `net_x_over_t < 1.10`, or `drift_ok` is false, **stop** and report. Do not continue.
- During any stage: if `logs/<stage>.jsonl` shows the eval fall rate (`eval/episode_fell` mean / steps) ≥ 0.5 at ≥ 60 % of the steps, stop that stage and report the curve.
- If **j10_rough** scores worse than j10_carry on any gate, ship j10_carry.

Budget [EST from job-4 throughput]: j10_walk 5.1 h, j10_push 3.0 h, j10_carry 3.0 h, j10_rough 1.6 h, about 13 h total. Measured VRAM in job 4 was about 2.3 GB at 1024 envs, so keep 1024.

## 4. Ship
Copy the best passing stage to `policy_j10.npz` + `policy_j10.meta.json` and run `python eval_box.py --policy policy_j10.npz --tag j10 --gif`.

## 5. Gates (box CPU, eval_box.py): all on one policy
1. Walk at 1.2 m/s for 20 s: no fall, mean horizontal speed ≥ 1.15, net x/t ≥ 1.15, |final_y| ≤ 0.5 m, |final_heading_deg| ≤ 5.
2. Lateral 300 N × 0.2 s at 4 s: no fall through 6 s.
3. Forward +0.6 m/s from stand at 1 s: upright with speed < 0.5 at 3 s.
4. 20 kg carry, **INTERIM per R-117**, payload at **P-042 (0.32, 0, 0.415)** torso frame, 0.8 m/s for 20 s: no fall, speed and net x/t ≥ 0.8, same drift gate (`carry.json`). Also report `carry_legs.json` (Legs' point (0.25, 0, 0.10)), not gated. The final G4 carry gate follows TARGETS.md. The j10_carry/j10_rough stages randomize the payload position over x 0.24–0.33, y ±0.02, z 0.09–0.425 (R-117).

5. R-118 mass corners: walk and P-042 carry also pass at 65.0 and 68.5 kg. Ship only if `results/j10_gates_summary.json` has `all_pass: true`.

## 6. Deliverables (commit to main under modules/legs/rl/, commit before pull --rebase)
- `policy_j10*.npz` + `.meta.json` per stage, `results/j10*_*.json`, GIFs, `curves/j10_*.png`, `logs/j10_*.jsonl`
- `REPORT_J10.md` with:
  - the per-stage gate table, using the eval_box `pass` (and `pass_legacy`)
  - steps, wall clock, sps and VRAM per stage
  - the sim/v3 hash and model mass
  - knee_rms_nm vs 76.9 N·m, leg τ/ω peaks, obs_z_max_t0
  - anything you changed
