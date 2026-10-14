# Grok Build brief: score RL walk policies on the G4 CPU gates (RL Controls, 2026-10-14)
Run on Bryan's **bryan** PC only (never DESKTOP-B115PVV). Queue position: after job 4 (RL train), 5 (lever FEA), 6 (structure r2), unless Robot Lab says otherwise. Do not touch a running job or its run folder. CPU only; no GPU, no jax needed.

## What to score
| policy | source |
|---|---|
| walk_a | `modules/legs/rl/policy_walk_a.npz` (commit 5132740) |
| walk_b | `modules/legs/rl/policy_walk_b.npz` (commit 63927d4) |
| job 4 checkpoints | every `policy_<step>.npz` job 4 pushed to the repo, plus `modules/legs/rl/logs/<stage>_policy_latest.npz` if present. Copy, do not move, anything from `$RL_RUNS`. |

## Setup
```
cd <robot-lab repo on bryan PC>
git pull --ff-only
python -m venv .venv-score          # or reuse the repo venv
.venv-score\Scripts\pip install numpy mujoco imageio   # eval_box imports numpy + mujoco only (imageio for --gif)
```

## Commands (one policy at a time, sequential)
`eval_box.py` always writes to `modules/legs/rl/results/`; move each set out before the next run.
```
cd modules/legs/rl
for each P in policy_walk_a.npz policy_walk_b.npz <job4 checkpoints>:
  python eval_box.py --policy P
  move results\*.json -> ..\..\controls\results\r1_rl_gates\<name>\
```
Runtime: about 1–3 min per policy on CPU (4 episodes: 20 s walk, 8 s lateral push, 3 s forward push, 20 s carry).

## Expected stdout (one line per gate)
```
mass_scale <k> mass 65.0
WALK <True|False> speed <m/s> fwd <..> x/t <..> fell <s|None> <why>
LATERAL <True|False> fell <s|None> <note> min_up <..>
FORWARD <True|False> fell <..> final_v <..> up <..>
carry mass 85.0 scale <k>
CARRY <True|False> speed <m/s> fell <s|None>
wrote .../results
```
Files per policy: `walk.json` (incl. per-leg peak/RMS torque and saturation), `push_lateral.json`, `push_forward.json`, `carry.json`.

## Gates (from eval_box.py)
- WALK: 20 s at 1.2 m/s cmd, mean horizontal pelvis speed ≥ 1.15, no fall.
- LATERAL: 300 N × 0.2 s = 60 N·s +Y on torso at t = 4 s during the 1.2 m/s walk; no fall through t = 6.
- FORWARD: +0.6 m/s COM kick at t = 1 from stand; upright (up ≥ 0.72) and horizontal speed < 0.5 at t = 3.
- CARRY: 20 kg at (0.25, 0, 0.10), 0.8 m/s cmd, 20 s, mean speed ≥ 0.8, no fall.

## Caveats to record
- eval_box loads `sim/v3/humanoid_v3.xml`, which since 8a03242 has the P-019/A26 neck (2× XM430, ±4.1 Nm). walk_a/walk_b were trained on the old neck (±36 Nm). Note this; do not edit the model.
- If `actuator order mismatch` appears, stop and report; do not regenerate gains (RL Controls owns `make_model.py` regen after job 4).

## Deliverable
Commit `modules/controls/results/r1_rl_gates/<policy>/*.json` plus `modules/controls/results/r1_rl_gates/SUMMARY.md` (table: policy, WALK/LATERAL/FORWARD/CARRY pass, walk speed, fall times, carry speed, max leg peak/avail). Message: `RL Controls scoring: <policies> on eval_box gates`. Push to main.
