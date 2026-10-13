# Grok Build brief: RL walking policy (bryan PC, RTX 5060)

Context: the model-based WBC fails the walk gate. Box r7 (DECISIONS L32): the best run is 0.8 m/s for 20 s with a DS 0.25 reference. 1.0 falls at 7.1 s and 1.2 at 4.8 s. Train a learned locomotion policy in parallel.

## Framework: MuJoCo Playground (MJX/JAX, Brax PPO)
Why: it uses the same MJCF as the box (`sim/v3/humanoid_v3.xml`), with no USD conversion and no Isaac Sim install. The policy then replays on the box in plain CPU MuJoCo (1 GB RAM OK), so QC can verify it here. Isaac Lab would need a URDF/USD port, a ~30 GB Isaac Sim install and a second physics engine, and would make box replay a sim-to-sim transfer.

Setup (the PC is Windows; JAX GPU needs Linux, so use WSL2 Ubuntu 22.04/24.04):
1. Update the NVIDIA Windows driver to one that supports Blackwell (RTX 50) with CUDA ≥ 12.8. Inside WSL, run `nvidia-smi` to confirm.
2. `python3.12 -m venv rl && . rl/bin/activate && pip install -U "jax[cuda12]" mujoco mujoco-mjx playground brax`. Verify that `jax.devices()` shows the GPU. If sm_120 isn't supported by the jaxlib wheel, use the newest jaxlib and report the error.
3. Clone the repo into WSL. Make an MJX-friendly copy under `modules/legs/rl/` (do not edit `sim/v3`): convert the mesh/box feet to boxes, use condim 3, set `<option iterations="4" ls_iterations="8">`, and add a `<key>` stance pose. Start from Playground's `BerkeleyHumanoid`/`G1` joystick env.

## Model and limits
- Mass 65 kg nominal, randomized up to 66.5 kg (R-017 cap; official rollup 66.054). Use the gait_lib `LEGS_MASS` scaling.
- ankle_roll range ±18° (sim/v3 93cb518, stiff limit).
- Torque limits are the R1.2 available torques (gait_lib `LIM_R1`): hip_yaw 70, hip_roll 204, hip_pitch 350, knee 258, ankle_pitch 311, ankle_roll 177 N·m. Upper body uses the MJCF ctrlrange.
- Speed limits are the contract available ω (wbc VEL_LIM): hip_yaw 6.13, hip_roll 3.64, hip_pitch 12.16, knee 16.03, ankle_pitch/roll 13.7 rad/s. Implement a torque–speed clip: τ_max scales linearly to 0 at 1.2 × ω_avail. Penalize exceeding ω_avail.
- Action: PD position targets at 50 Hz, physics dt 0.002 (as v3). Kp/Kd per joint, with τ clipped to the limits above.

## Domain randomization (per episode)
- Mass ±5 % per link, plus the torso payload 0–20 kg for the carry curriculum, with CoM ±2 cm.
- Friction 0.5–1.2.
- Motor strength 0.85–1.10 × limits.
- Kp/Kd ±15 %.
- Action latency 0–20 ms; observation noise (IMU, joint) at standard Playground levels.
- Pushes: random 50–150 N for 0.1–0.2 s every 3–6 s, in any horizontal direction.
- Floor: flat plus a mild height field (±1 cm) in the last 30 % of training.

## Reference / reward shaping
- Use the model-based gait as a soft reference:
  - `results/r7/ref_ds25/walk_{0p8,1p0,1p2}_r7.npz` (Q, V, FZ, 1 s cycle, DS 0.25), the walk slices in `results/r2/`, and `exports/walk_0p8_fsim_65kg.csv/json`.
  - Reward joint-pose tracking against the phase-indexed reference (weight decays to 0.2× by the end), plus foot-contact timing that matches the reference's contact flags.
- Standard terms: velocity tracking (vx command 0–1.3 m/s, plus yaw rate), upright, pelvis height, feet air time ≥ 0.25 s, a no-flight penalty (both fz < 20 N), and torque/energy, action rate and joint-limit penalties.
- Curriculum: 0.6 → 1.3 m/s; pushes on after 30 %; carry 0 → 20 kg after the walk converges.

## Pass gates (same as WBC; evaluated on the box in CPU MuJoCo with the unmodified `sim/v3` XML)
1. Walk ≥ 20 s at 1.2 m/s command, mean pelvis speed ≥ 1.15 m/s, no fall.
2. Push recovery: the 60 N·s lateral push of `wbc/run.py --mode push` and the forward push of `push_recover`; recover within 2 s.
3. 20 kg carry (torso payload, as `carry_20kg_r2`) at ≥ 0.8 m/s for ≥ 20 s.
4. Report the torque and ω peaks against the limits above, the saturation %, DS/flight fraction, and the ankle_roll peaks (stop at ±18°).

## Compute estimate [EST, not measured]
RTX 5060 8 GB: 2048–4096 MJX envs at about 3–5 GB VRAM. PPO for 150–300 M steps takes about 2–6 h for the walk, plus about 2–4 h of fine-tuning for pushes and carry. If VRAM runs out, halve the envs. Report the actual numbers.

## Outputs (commit under `modules/legs/rl/`)
- `policy.onnx` (or a `.npz` of the MLP weights) plus `obs_spec.json` (order, scaling, PD gains, action scale, control rate).
- `eval_box.py`: pure numpy plus mujoco, no JAX. It loads `sim/v3/humanoid_v3.xml` with the gait_lib mass and limits, runs the gates above on CPU at ~1 GB RAM, and writes `rl/results/*.json` and a GIF.
- `train_cfg.yaml`, training curves (PNG), and `REPORT.md` with honest pass/fail per gate.
