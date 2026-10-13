# RL Legs: gait-derived leg joint requirements (round 1)
Owner: RL Legs. Date: 2026-10-13. Addresses AUDIT A2 (no walking sim) and A3 (leg torque and speed requirements were v2 estimates).
Everything here is produced by the scripts in this folder. Nothing was edited in CONTRACTS.md, and no actuator selection was changed. Requirement changes are proposed in `modules/PROPOSALS.md` (P-001 to P-004).

## Files
| file | what it does |
|---|---|
| `gait_lib.py` | LIPM ZMP preview control (Kajita 2003), whole-leg IK, multibody ZMP, floating-base inverse dynamics (`mj_inverse`) with a foot-wrench QP |
| `scenarios.py` | builds the reference trajectories and runs ID for each scenario → `results/<scenario>.json/.npz` |
| `envelope.py` | per-joint metrics, envelope, comparison with CONTRACTS rev 0 §1a → `results/requirements.md`, `results/envelope.json` |
| `plots.py` | `plots/<scenario>.png` (torque, speed, power, angle, GRF vs time) and `plots/envelope_vs_contract.png` |
| `fsim.py` | forward-dynamics walking with a model-based controller → `results/fsim/*.json` |
Reproduce: `python3 scenarios.py <name>` (one scenario per process, under 150 MB RAM, 2 to 40 s each), then `python3 envelope.py`, then `python3 fsim.py walk_0p8 --kc 10 --kr 4`.

## Model and masses
- `sim/v3/humanoid_v3.xml`, used unmodified. Total mass is 63.794 kg, which equals the v3 catalog rollup (63.8 kg).
- Mass check against CAD: `gen_v3.py` takes per-segment mass, COM and inertia from `v3/cad/out/mass.json` (CAD total 56.293 kg). It then scales every segment by 63.8/56.293 = 1.1334, so the harness, covers and so on (in the rollup but not in CAD) are spread pro rata. Each body in the MJCF equals CAD segment × 1.1334 (e.g. L_shank 2.788 → 3.160 kg, L_foot 2.249 → 2.549 kg). The model therefore matches CAD distribution at catalog total mass, so no mass fix was needed. This is conservative for the legs, because some harness and cover mass that really sits in the torso is placed on the legs.
- Knee and ankle are roller-screw linkages, modelled as rotary joints with reflected armature. All torques below are joint-output torques. They include reflected rotor inertia (armature); the `peak τ w/o armature` column in `results/requirements.md` shows that it adds under 2 %.
- Leg ID with the 20 kg carry: a 20 kg rigid payload sits on the torso 0.25 m ahead of the waist axis, with the trunk leaned back 0.25 rad at the waist. Arm joint loads are not evaluated (Arms module).

## Method
1. **Reference trajectories.**
   - Walking: footstep plan with flat-foot stance, 20 % double support, and 25° heel-off (toe roll) of the trailing foot in late double support. Swing apex is 7 cm, with zero velocity and acceleration at lift-off and touchdown.
   - COM: ZMP preview control on a LIPM at the model's COM height (0.943 m). Pelvis height is 1.04 m and held level.
   - Dynamic consistency: two-stage ZMP correction. The multibody ZMP error from `mj_inverse` is fed back through the preview controller (7 iterations). For walk 1.2 m/s the ZMP error fell from 0.525 m max / 0.156 m rms to 0.028 m max / 0.004 m rms.
   - Joint angles: damped-least-squares IK, foot error < 4 µm. The IK may exceed model ROM by up to 15°, so ROM needs can be reported.
2. **Scenarios.**
   - walk 1.2 m/s: 0.45 s steps, 0.54 m step length, ramped start and stop.
   - walk 1.0 m/s (0.47 s) and 0.8 m/s (0.5 s), for sensitivity.
   - stairs: 18 cm rise, 30 cm tread, 0.9 s steps, step-over-step, 6 cm clearance.
   - 20 kg carry while walking at 1.2 m/s.
   - sit-to-stand from a 0.46 m seat in 1.2 s, starting at seat-off. Trunk lean is 38°, the most the hip ROM (+15° IK margin) allows. The COM starts +50 mm ahead of the ankle, so this is a quasi-static strategy.
   - push step: 0.6 m/s COM velocity at t = 0 (38 N·s, which is 1.5× the impulse of the v3 125 N × 0.2 s test). Ankle reaction for 0.1 s, then a capture-point step in 0.35 s to (0.40, −0.36) m, then capture-point control to rest (final COM speed 0.04 m/s).
3. **Inverse dynamics.**
   - `mj_inverse` runs with contacts, joint limits and friction loss disabled. Joint damping stays on.
   - The 6 floating-base rows must come from the feet. Foot wrenches are solved per frame by a QP with these constraints: CoP inside the sole (−60…+180 mm, ±50 mm; toe-edge line contact during heel-off), friction pyramid μ = 0.8, Fz ≥ 0, load share following the plan. Among feasible splits it picks the least joint torque, so there is no internal squeeze.
   - Joint torque = qfrc_inverse − Σ Jᵀw.
   - Any base wrench the feet cannot supply is reported as a residual. Walk 1.2 has a 99th percentile of 36 N (5.8 % of body weight), in short windows at single-support start. Stairs: 33 N. Carry: 46 N. Push: 53 N. Sit-to-stand: 1.6 N. CoP stays inside the sole in every scenario.
4. **Metrics** (one side, worst of left/right, over the scenario minus 0.3 s start-up edges):
   - peak |τ|, 99th-percentile |τ|, RMS τ
   - peak |ω|; ω while |τ| ≥ 30 % of peak (the contract's speed definition)
   - peak |τω|, mean |τω|
   - duty: fraction of time with |τ| ≥ 50 % of that scenario's peak

## Requirement table (envelope over all 7 scenarios; governing scenario in brackets)
| joint | peak τ N·m | RMS τ N·m | peak ω rad/s | ω @ ≥30 % τ rad/s | peak power W | duty (≥50 % peak) |
|---|---|---|---|---|---|---|
| hip_yaw | 57 [carry] | 16 [carry] | 0.57 [walk 1.2] | 0.24 [walk 1.2] | 3 [carry] | 0.21 (walk 1.2) |
| hip_roll | 122 [carry] | 50 [carry] | 1.23 [push] | 1.16 [push] | 55 [push] | 0.33 (carry) |
| hip_pitch | 265 [carry] | 100 [carry] | 8.11 [walk 1.2] | 8.09 [walk 1.2] | 1017 [walk 1.2] | 0.21 (carry) |
| knee | 178 [carry] | 77 [carry] | 13.33 [stairs] | 13.27 [stairs] | 865 [stairs] | 0.27 (carry) |
| ankle_pitch | 239 [carry] | 55 [push] | 9.43 [stairs] | 6.92 [stairs] | 828 [carry] | 0.04 (carry) |
| ankle_roll | 41 [push] | 17 [push] | 1.23 [push] | 0.83 [push] | 32 [push] | 0.29 (push) |
Duty is shown for the scenario that governs peak torque. Sit-to-stand has the highest duty (it stays near its own low peak), which is not meaningful for sizing. Per-scenario tables are in `results/requirements.md`.

Per-scenario peak τ / RMS τ (N·m) / peak ω (rad/s):
| joint | walk 1.2 | walk 1.0 | walk 0.8 | stairs 18 cm | carry 20 kg | sit-to-stand | push step |
|---|---|---|---|---|---|---|---|
| hip_yaw | 40/14/0.6 | 38/13/0.6 | 34/11/0.5 | 44/13/0.5 | 57/16/0.6 | 0/0/0 | 23/10/0.0 |
| hip_roll | 96/43/0.4 | 95/43/0.4 | 93/42/0.4 | 118/45/0.5 | 122/50/0.4 | 0/0/0 | 104/36/1.2 |
| hip_pitch | 203/86/8.1 | 180/70/6.6 | 134/52/5.1 | 220/46/6.3 | 265/100/7.6 | 74/45/2.7 | 94/32/3.3 |
| knee | 154/72/9.1 | 142/69/7.1 | 131/67/5.9 | 139/64/13.3 | 178/77/11.9 | 56/44/2.4 | 126/48/3.6 |
| ankle_pitch | 203/44/8.8 | 203/42/7.3 | 183/40/6.2 | 171/37/9.4 | 239/51/9.2 | 27/16/0.9 | 123/55/3.5 |
| ankle_roll | 26/7/0.5 | 26/7/0.5 | 28/7/0.5 | 25/7/0.5 | 31/9/0.5 | 0/0/0 | 41/17/1.2 |

Compared with CONTRACTS rev 0 (v3 req = need/1.5, mass-scaled v2): hip_yaw 16.0 → 57 (3.6×), hip_roll 81.4 → 122 (1.5×), hip_pitch 76.5 → 265 (3.5×), knee 154.6 → 178 (1.15×), ankle_pitch 102.1 → 239 (2.3×), ankle_roll 38.3 → 41 (1.06×). v3 available peak torque is exceeded by the gait peak itself, before the 1.5× margin, at hip_yaw (36), hip_pitch (167) and knee speed (12.1 rad/s available vs 13.3 needed). See `plots/envelope_vs_contract.png`.

Leg mechanical power, both legs, mid-walk window: 1.2 m/s gives 426 W mean positive (817 W mean |P|, 1016 W peak summed). 1.0 m/s gives 303 W. 0.8 m/s gives 196 W. Carry gives 434 W. The v3 power model assumes 244 W mechanical for the whole robot at 1.2 m/s (AUDIT A9).

Range of motion used (model ROM in brackets):
- Ankle dorsiflexion reached −56° (walk 1.2) and −60° (stairs, at the IK +15° margin, so the real need may be larger). Model ROM is −45°.
- Hip flexion reached −120° (sit-to-stand, at the IK margin). Model ROM is −105°.
- Knee reached 113° (sit-to-stand) and 110° (stairs). Model ROM is 135°, which is fine.

## Assumptions and limits (read before using the numbers)
- **This is one gait family:** bent-knee ZMP walking with level pelvis, flat-foot stance plus heel-off, no arm swing, no pelvis rotation, no turning.
  - No arm swing and no pelvis yaw mean the stance hip yaw must react the swing leg's yaw moment (40 to 57 N·m), and the foot is limited to |Mz| ≤ 0.05·Fz. Arm swing or torso counter-rotation would lower hip-yaw torque. That is not quantified here.
  - The bent knee (stance knee 34 to 86°) raises knee and hip torque compared with a human-like straight-knee gait. The 0.36 s swing at 1.2 m/s drives hip-pitch torque, speed and power: hip pitch drops from 203 to 134 N·m between 1.2 and 0.8 m/s.
- Hip-yaw and hip-roll speeds here come from straight walking only. Turning, side-stepping and lateral push steps were not run, so the current speed needs for those joints should not be lowered on this evidence.
- Sit-to-stand starts at seat-off and is quasi-static (COM already over the feet). A momentum-transfer rise from a lower seat would be harder.
- Contact loads: peak vertical GRF is 1.22 to 1.31 BW per foot (no impact model; touchdowns are planned at zero velocity). Landing and fall loads are not in these numbers.
- Torques are computed from kinematic plans, not measured from a stabilized forward sim. For walk at 0.8 m/s, forward sim with this feed-forward tracks within 2 mm at the end (see below), which supports the plan's dynamic consistency.
- 5 % body-weight residual windows: the QP could not fully realise the planned base wrench in those frames. The torque there is the best feasible split.

## Forward-sim walking (model-based, CPU only, no RL)
Controller (`fsim.py`), running at the 500 Hz sim step:
- inverse-dynamics feed-forward torque from the plan
- joint PD to the planned angles (kp ≤ 800 N·m/rad)
- virtual-model balance: a corrective wrench on the body from COM error (k = 10 s⁻²·m·g) and pelvis attitude error (kr = 4), mapped through the stance-leg Jacobians (τ = −Jᵀ·ΔW, weighted by planned load share)
Torques are clipped to the v3 catalog peaks (MJCF ctrlrange). Contacts are on, with friction 1.0.

| run | result |
|---|---|
| walk 0.8 m/s, v3 torque limits | **Completes the full plan:** 9.3 s, 16 touchdowns, 5.13 m, final x error −2 mm, saturation only l_hip_yaw 0.3 % of steps (`results/fsim/walk_0p8_fb1.json`) |
| walk 0.8 m/s, feed-forward + PD only (no balance) | falls at 2.8 s after 3 touchdowns |
| walk 1.0 m/s, v3 limits | falls at 7.0 s after 14 touchdowns, 5.06 m (kr = 8); kr = 4 falls at 5.3 s. Hip yaw saturated 13 to 17 % of steps |
| walk 1.2 m/s, v3 limits | falls at 4.0 to 4.1 s after 9 to 10 touchdowns, about 3.1 m; saturation 10 to 20 % on hip pitch, hip yaw, knee, ankle |
| walk 1.2 m/s, torque limits ×1.6 / ×2.0 | still falls (3.9 s / 4.6 s): at 1.2 m/s the controller is also a limit, not only the actuators |
| carry 20 kg at 1.2 m/s, v3 limits | falls at 2.8 s after 6 touchdowns |
| push step, sit-to-stand in forward sim | not achieved (push run falls at 1.14 s; the sit-to-stand run has no chair in the scene and is not valid). Reported only for completeness |
What works: CPU-only model-based walking on the v3 model at 0.8 m/s, with v3 actuator limits, for 16 steps and 5.1 m. What doesn't: 1.0 m/s holds for 14 steps, then falls. 1.2 m/s and the 20 kg carry fall within about 10 steps. The ID shows 1.2 m/s needs more hip-pitch and hip-yaw torque than v3 has. A better controller (whole-body QP with CoP constraints, online footstep adjustment) is the next step before anyone can claim 1.2 m/s on hardware limits.
