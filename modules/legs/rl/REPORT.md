# RL walk — CPU gate report

All four gates fail on `policy_walk_a.npz`, `policy_walk_b.npz`, and `policy_carry.npz`.

The numbers below are from `eval_box.py` on the unmodified `sim/v3/humanoid_v3.xml`, CPU MuJoCo, noise off. Untagged files in `results/` are the carry policy. Tagged files are the other two. `walk.gif` is the carry policy's 1.2 m/s attempt, frames from 0 to 8 s.

## Gate table

| Policy | Walk 20 s at 1.2 m/s, mean ≥ 1.15 | Lateral 60 N·s | Forward push | 20 kg carry, ≥ 0.8 m/s for 20 s |
|---|---|---|---|---|
| walk_a | Fail. Fell at 0.62 s (airborne). Mean horizontal speed 0.982 m/s over 1.16 s. | Fail. Fell at 0.62 s, before the push at 4.0 s. | Fail. Fell at 1.22 s (kick was at 1.0 s). | Fail. Fell at 0.54 s. |
| walk_b | Fail. Fell at 0.70 s (pelvis). Mean horizontal speed 1.074 m/s over 1.24 s. | Fail. Fell at 0.70 s, before the push. | Fail. Fell at 1.70 s. | Fail. Fell at 0.62 s. |
| carry | Fail. No fall in 20.0 s. Mean horizontal speed 1.127 m/s. | Fail. Fell at 5.20 s, inside the 2 s recovery window. | Fail. Fell at 1.98 s. | Fail. No fall in 20.0 s. Mean horizontal speed 0.722 m/s. |

Mean horizontal speed is the mean of `hypot(world vx, world vy)` over the recorded steps. A fall also ends the episode 0.5 s later, so the means for walk_a and walk_b include that short tail.

## Carry policy (the final weights)

`policy_carry.npz`. This is the policy the later stages were training, and the one in the untagged JSON and in `walk.gif`.

Walk, command `(1.2, 0, 0)`, 20.0 s, no fall. Pelvis stayed up: minimum up-vector 0.987, minimum z 1.009 m, final up-vector 0.996. Mean body-forward speed 1.120 m/s. Mean world vx 0.913 m/s, mean world vy 0.588 m/s, net x/t 0.913 m/s. The heading drifts, so the world-frame forward progress is well below the command. Both the gate speed (1.127) and the body-forward speed (1.120) are under 1.15. Double support (both feet Fz > 40 N) 0.236. Flight (both Fz < 20 N) 0. Ankle-roll peaks 10.20° and 6.75°, under the ±18° stop.

Lateral push: 300 N along +Y on the torso for t in [4.0, 4.2), which is 60 N·s, during the 1.2 m/s walk. The robot was still up at 4 s. It fell at 5.20 s (pelvis), 1.2 s after the push started and 1.0 s after it ended. The recovery window runs through 6.0 s. Minimum up-vector −0.038. Ankle-roll peaks on this episode 14.21° and 10.68°.

Forward push: from the settled stand, world vx += 0.6 m/s at t = 1.0. Impulse 0.6 × 65.0 kg = 39.0 N·s. Fell at 1.98 s (pelvis). At the end of the clip, up-vector 0.137 and horizontal speed 0.339 m/s. The gate wants the robot still up at 3.0 s with horizontal speed under 0.5 m/s.

Carry: 20 kg payload inserted in memory at `(0.25, 0, 0.10)` with diaginertia `0.2 0.15 0.2`, command 0.8 m/s, 20.0 s, no fall. Total mass 85.0 kg. Minimum up-vector 0.990, final up-vector 0.995. Mean horizontal speed 0.722 m/s, body-forward 0.705 m/s, world vx 0.677 m/s, world vy −0.141 m/s, net x/t 0.677 m/s. Double support 0.228, flight 0. Ankle-roll peaks 8.32° and 8.73°.

Leg peaks on the 20 s walk, after the torque-speed clip. Torque cannot read above the limit because the clip is applied before the peak is stored. Saturation is the fraction of control steps with `|tau| > 0.95` times the speed-derated limit. Speed is the joint velocity, which is not clipped.

| Joint | τ peak / limit (N·m) | fraction | ω peak / limit (rad/s) | fraction | sat |
|---|---|---|---|---|---|
| l_hip_yaw | 48.79 / 70 | 0.697 | 2.293 / 6.13 | 0.374 | 0 |
| l_hip_roll | 136.22 / 204 | 0.668 | 1.351 / 3.64 | 0.371 | 0 |
| l_hip_pitch | 217.12 / 350 | 0.620 | 6.830 / 12.16 | 0.562 | 0 |
| l_knee | 199.39 / 258 | 0.773 | 7.577 / 16.03 | 0.473 | 0 |
| l_ankle_pitch | 133.99 / 311 | 0.431 | 6.319 / 13.7 | 0.461 | 0 |
| l_ankle_roll | 44.15 / 177 | 0.249 | 2.359 / 13.7 | 0.172 | 0 |
| r_hip_yaw | 43.86 / 70 | 0.627 | 2.906 / 6.13 | 0.474 | 0 |
| r_hip_roll | 136.79 / 204 | 0.671 | 1.737 / 3.64 | 0.477 | 0 |
| r_hip_pitch | 238.64 / 350 | 0.682 | 6.888 / 12.16 | 0.566 | 0 |
| r_knee | 243.54 / 258 | 0.944 | 8.110 / 16.03 | 0.506 | 0.001 |
| r_ankle_pitch | 129.02 / 311 | 0.415 | 5.980 / 13.7 | 0.436 | 0 |
| r_ankle_roll | 61.02 / 177 | 0.345 | 2.932 / 13.7 | 0.214 | 0 |

On this walk every leg speed stays under its limit. The right knee is the hottest torque, 94% of 258 N·m, and it sat the derated limit on about 0.1% of control steps.

## walk_a and walk_b

Both fall in the first second of the 1.2 m/s walk, so the lateral push is never applied to a walking robot. walk_a goes airborne at 0.62 s (flight fraction 0.55 over the short clip). walk_b hits the pelvis fall test at 0.70 s (up-vector or height). Their 20 kg trials fall at 0.54 s and 0.62 s. The forward-push trials fall at 1.22 s and 1.70 s.

Those falls drive joints past the speed limit. On the walk_a walk clip, `l_hip_yaw` peaks at 10.04 rad/s against 6.13 (saturation 0.155) and `l_knee` torque fraction is 0.995 (saturation 0.172). On the walk_b walk clip, `r_hip_yaw` peaks at 13.38 rad/s against 6.13 (saturation 0.177). The 20 kg falls reach the ankle-roll stop: 18.02° and 18.03° against ±18°.

## Training

RTX 5060 Laptop, 8151 MiB, under WSL2 Ubuntu 24.04. JAX 0.11.2 sees the GPU (`CudaDevice`, device_kind `NVIDIA GeForce RTX 5060 Laptop GPU`). Training used MuJoCo Playground 0.2.0 with `impl='jax'` (Warp is installed and was not used), Brax 0.14.2 PPO, MuJoCo / MJX 3.15.0. One JAX 0.11 incompatibility is patched in `train.py`: `jax.device_put_replicated` is copied back from `jax._src.api` before `ppo.train`.

`XLA_PYTHON_CLIENT_PREALLOCATE=false` and `XLA_PYTHON_CLIENT_MEM_FRACTION=0.85`, set before importing JAX. A single 4–6 GiB preallocation failed on this card even when it was nearly empty. Stepping still ran. The desktop shares the GPU. Measured training VRAM stayed near 2.3 GB.

1024 envs, batch 32, 32 minibatches, unroll 20 (20480 env-steps per update), 4 epochs, discount 0.97, learning rate 3e-4, entropy 0.005, clip 0.2, network (512, 256, 128), swish, tanh-normal. 32 eval envs. Episode length 1000 control steps (20 s) at 50 Hz. Sim timestep 0.002 s, 10 substeps. Solver in the MJX copy: implicitfast, iterations 4, ls_iterations 8. The CPU gate loads stock v3, which is implicitfast, timestep 0.002, iterations 100, ls_iterations 50.

A 2048-env probe did not raise throughput (the GPU was already full near 2.3 GB). Euler was not faster than implicitfast. iterations=1 was faster in a probe and was not used, because the CPU gate uses the stock solver.

| Stage | Env-steps | Wall clock | VRAM | Steady throughput | Final MJX eval (not the gate) |
|---|---|---|---|---|---|
| walk_a | 40,038,400 | 14910.9 s (4.14 h) | 2318 / 8151 MiB | median 2756 env-steps/s | reward 105.2, body speed 0.673 vs command 0.681, fell 0.125, length 946 steps |
| walk_b | 30,003,200 | 11203.1 s (3.11 h) | 2318 / 8151 MiB | median 2774 env-steps/s | reward 87.9, body speed 0.600 vs command 0.611, fell 0.125, length 947 steps |
| carry | 32,051,200 | 19474.1 s (5.41 h) | 2386 / 8151 MiB | median 1711 env-steps/s | reward 52.2, body speed 0.622 vs command 0.656, fell 0.875, length 593 steps |

The step counts are the last logged PPO step. The yaml budgets are 40M, 30M, and 32M. The extra steps are the collection boundary. Carry is slower because that stage turns on the heightfield. Total of the three finished stages: 102,092,800 env-steps, 45588.1 s (12.66 h).

MJX eval samples a random command inside the stage range and is not the CPU gate. walk_a commands only go up to 1.05 m/s. The best walk_a fall rate was 0.031 at 24.0M steps (speed 0.689 vs command 0.703). The best walk_b fall rate was 0.031 at 24.0M steps, at a lower command (0.519 vs 0.540). Carry's MJX fall rate went 1.0, 0.78, 0.84, 0.94, 0.84, 0.88 and the mean episode length stayed near 12 s.

An earlier walk_b was stopped on purpose. It trained pushes of 50–300 N and, with probability 0.15, the 60 N·s impulse (300 N for 0.2 s). Eval fall rate stayed at 0.71875 from step 7,208,960 through step 21,626,880. The log's last row is step 22,077,440 at wall 8372.4 s. That checkpoint was not used. The restarted walk_b, and carry, use 50–150 N and `push_gate_prob: 0`. The 60 N·s lateral gate was therefore outside the training distribution. It failed, as the table says.

## Setup choices that the gates feel

- PD gains are not in the XML. v3 actuators are torque motors. `tau = kp * kp_scale * (q_target - q) - kd * kp_scale * qd`, then the torque-speed clip. `kp = clip(tau_limit / 0.25, 80, 2800)`, so the position authority of the action residual is ±0.25 rad on every joint. `kd = 2 * sqrt(kp * max(armature, 0.05)) + 0.015 * kp`. Kp and Kd share one scale, uniform on [0.85, 1.15], not two independent ±15% draws. Motor strength is a separate uniform draw on [0.85, 1.10].
- The reference cycles in `results/r7/ref_ds25/` are named for a 0.25 double-support fraction. On a 1.0 s window whose speed matches the file (t0 = 4.4 s), measured double support is 0.19, 0.19, and 0.20 for the 0.8, 1.0, and 1.2 m/s files, and flight is 0. The policy was tracked to that motion. The carry policy's own 20 s walk measured double support 0.236 and flight 0.
- Eval mass: the current v3 file sums to 64.298 kg. `eval_box.py` scales every non-payload body so the total is 65.0 kg (`k = 1.010918`) and sets leg actuator ranges to the R1 limits in memory. It does not write the file. The 20 kg body is added in memory. `gait_lib.py` uses the same rule when `LEGS_MASS` is set. Its comment still says the unscaled model is 63.794 kg; the file on disk at this eval is 64.298 kg.
- Policy observation is 107 numbers, with the training normalizer baked into the npz. The gate replays with noise level 0. Action is `tanh` of the first 30 MLP outputs.

## Artifacts

- `policy_walk_a.npz`, `policy_walk_b.npz`, `policy_carry.npz`, `obs_spec.json`, `train_cfg.yaml`
- `curves/walk_a.png`, `curves/walk_b.png`, `curves/carry.png`
- `results/walk.json`, `push_lateral.json`, `push_forward.json`, `carry.json` (carry policy)
- `results/walk_a_*.json`, `results/walk_b_*.json`, `results/carry_*.json`
- `walk.gif` and `carry_walk.gif` (same clip), `walk_a_walk.gif`, `walk_b_walk.gif`
