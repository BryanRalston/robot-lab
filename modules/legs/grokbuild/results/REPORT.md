# WBC walk 1.2 m/s — forward-sim results

The 20 s / 1.15 m/s gate was not met. The whole-body controller walks the looped `walk_1p2_r2` cruise, then the stance foot loses corners, yaw and roll grow, and the pelvis upright check trips. Numbers below are from the runs on 2026-10-13. Nothing here is filled in by hand from a target.

Code: `modules/legs/wbc/`. Model: `gait_lib.load()`, `LEGS_MASS=65`, `LEGS_LIMITS=r1` (CONTRACTS R1.2 torque limits). Sim timestep 0.001 s. QP (OSQP) at 1 kHz. Decision variables are the 36 generalized accelerations and a 6-D wrench on each foot. Hard constraints: floating-base dynamics, R1.2 torque limits, wrench cone μ = 0.8 with the center of pressure inside the sole and `|Mz| ≤ 0.05 Fz`, and the avail-ω joint speed limits from `results/r2/requirements.md`. The cost tracks the planned inverse-dynamics torque plus joint PD. A light centroidal linear task and a light pelvis orientation task are in the same QP. At 100 Hz a LIPM capture error shifts the swing foot laterally by up to 4 cm (that is the step-width adaptation) and yaws it by up to 0.08 rad. Playback rate stays at 1. Toe-roll timing is the plan's ankle trajectory and sole CoP, not a separate clock. The plan file is 9.325 s, so the controller loops a 1.000 s cruise slice (pelvis travel 1.1997 m per cycle, seam joint error 0.0005 rad) that starts at plan t = 4.41 s. Pelvis x is shifted so the slice starts at x = 0. Mean speed is pelvis x / time, the same definition as `fsim.py`.

CoP margin is the clearance from the measured contact CoP to the nearest edge of the sole, in mm. The value reported is the minimum over every loaded foot (negative means the CoP was outside the sole). Saturation is `|commanded τ| ≥ 0.99 × R1.2 limit`. Solve time on this machine averaged 2.3 ms, so the 1 kHz QP is not realtime here. `qp_fail` was 0 on every run.

## Baseline (fsim, not this controller)

Reproduced with `LEGS_OUT=r2`, `LEGS_MASS=65`, `LEGS_LIMITS=r1`, `fsim.py walk_1p2_r2 --kc 10 --kr 8`. Recorded in `modules/legs/results/r2/fsim/walk_1p2_r2_fb1_kr8.json`.

- Fall time: 5.452 s
- Mean speed: 0.761 m/s
- Touchdowns: 11
- Pelvis x: 4.147 m (reference x 4.571 m, track error −0.424 m)
- Saturated fraction of time (fsim's own log, not peak/RMS): l_hip_yaw 0.111, l_hip_roll 0.053, l_hip_pitch 0.010, l_knee 0.080, l_ankle_pitch 0.084, l_ankle_roll 0.155, r_hip_yaw 0.107, r_hip_roll 0.084, r_hip_pitch 0.025, r_knee 0.103, r_ankle_pitch 0.150, r_ankle_roll 0.134, waist_yaw 0.050

That file previously stored a 5.832 s / 12 touchdown / 0.733 m/s run. The numbers above are the re-run.

## Nominal walk (`walk_1p2_r2` cruise loop)

- Fall time: 4.915 s (trigger `pelvis`: upright factor reached 0.72; pelvis z was 0.864 m, still above the height gate)
- Sim time: 4.915 s of 20 s commanded. Not completed.
- Mean speed (pelvis x / t): 1.1329 m/s
- Mean COM vx over the whole run (shorter than 4 s, so the second-half window is the full run): 1.0642 m/s
- Pelvis x: 5.568 m
- Touchdowns: 10
- Minimum CoP margin: 0.0 mm
- Peak CoP distance from the sole center: 130.0 mm (the sole corner)
- Mass: 65.0 kg. QP ok/fail: 4915 / 0. Mean solve: 2.293 ms. Wall: 12.25 s.
- GIF: `media/progress/2026-10-13_legs_wbc_walk1p2.gif`

| joint | peak Nm | RMS Nm | R1.2 avail Nm | peak/avail | saturated % |
|---|---:|---:|---:|---:|---:|
| l_hip_yaw | 38.93 | 14.21 | 70 | 0.556 | 0.00 |
| l_hip_roll | 139.16 | 64.81 | 204 | 0.682 | 0.00 |
| l_hip_pitch | 247.73 | 96.63 | 350 | 0.708 | 0.00 |
| l_knee | 248.37 | 112.91 | 258 | 0.963 | 0.00 |
| l_ankle_pitch | 260.50 | 69.90 | 311 | 0.838 | 0.00 |
| l_ankle_roll | 57.65 | 16.67 | 177 | 0.326 | 0.00 |
| r_hip_yaw | 44.23 | 14.18 | 70 | 0.632 | 0.00 |
| r_hip_roll | 182.86 | 61.69 | 204 | 0.896 | 0.00 |
| r_hip_pitch | 249.59 | 94.45 | 350 | 0.713 | 0.00 |
| r_knee | 242.88 | 107.73 | 258 | 0.941 | 0.00 |
| r_ankle_pitch | 260.31 | 75.37 | 311 | 0.837 | 0.00 |
| r_ankle_roll | 55.56 | 16.90 | 177 | 0.314 | 0.00 |

Speed stays near 1.2 m/s for the first 3 s (COM vx 1.13 to 1.31). By t = 2.5 s the measured contact count is 2 and the CoP margin is 0 mm. Yaw then swings through about −18° and roll through −14°, and the upright check trips at 4.915 s. The planned cruise CoP itself reaches the sole boundary on about 20% of loaded frames (median clearance about 45 mm), so the tracker has no spare lateral margin once the foot starts to roll.

## Lateral push (60 N·s)

Same unladen walk. At the first left-swing mid-stance after 3.5 s the torso got 300 N along +Y for 0.2 s.

- Push time: 4.060 s, swing foot `l`, phase 0.06
- Commanded impulse: 60.0 N·s (the full 0.2 s was applied)
- Pelvis `qvel[1]`: −0.0491 m/s before, +1.6354 m/s after, Δ +1.6845 m/s
- Subtree COM vy over that same 0.2 s window: −0.023 m/s to +1.417 m/s, Δ +1.440 m/s
- A 65 kg body that did not push back on the ground would gain 60/65 = 0.923 m/s. The measured change is larger. At the push the foot was already down to one contact and the pelvis was at y = −0.21 m, so this Δv includes the roll, not a pure impulse response.
- Fall time: 4.491 s (0.231 s after the force ended). Trigger `pelvis`, upright factor 0.72, pelvis z 0.841 m. Did not survive.
- Mean speed (pelvis x / t): 1.1376 m/s
- Mean COM vx: 1.0907 m/s
- Pelvis x: 5.109 m
- Touchdowns: 9
- Minimum CoP margin: 0.0 mm
- Peak CoP distance from the sole center: 130.0 mm
- QP ok/fail: 4491 / 0. Mean solve: 2.225 ms. Wall: 10.86 s.

| joint | peak Nm | RMS Nm | R1.2 avail Nm | peak/avail | saturated % |
|---|---:|---:|---:|---:|---:|
| l_hip_yaw | 34.51 | 13.33 | 70 | 0.493 | 0.00 |
| l_hip_roll | 139.16 | 62.15 | 204 | 0.682 | 0.00 |
| l_hip_pitch | 247.73 | 97.06 | 350 | 0.708 | 0.00 |
| l_knee | 248.37 | 106.92 | 258 | 0.963 | 0.00 |
| l_ankle_pitch | 260.50 | 68.49 | 311 | 0.838 | 0.00 |
| l_ankle_roll | 57.65 | 16.31 | 177 | 0.326 | 0.00 |
| r_hip_yaw | 46.44 | 14.48 | 70 | 0.663 | 0.00 |
| r_hip_roll | 191.16 | 64.54 | 204 | 0.937 | 0.00 |
| r_hip_pitch | 233.45 | 96.25 | 350 | 0.667 | 0.00 |
| r_knee | 242.88 | 110.99 | 258 | 0.941 | 0.00 |
| r_ankle_pitch | 260.31 | 78.27 | 311 | 0.837 | 0.00 |
| r_ankle_roll | 55.56 | 17.26 | 177 | 0.314 | 0.00 |

## 20 kg carry (`carry_20kg_r2`)

`gait_lib.load(20 kg)` then the same controller on that plan's cruise slice. Total mass 85.0 kg, COM height 1.0485 m.

- Fall time: 7.733 s (trigger `pelvis`, upright factor 0.72, pelvis z 0.858 m). Not completed.
- Mean speed (pelvis x / t): 1.1866 m/s
- Mean COM vx over the second half: 1.1751 m/s
- Pelvis x: 9.176 m
- Touchdowns: 14
- Minimum CoP margin: −0.01 mm
- Peak CoP distance from the sole center: 130.0 mm
- QP ok/fail: 7733 / 0. Mean solve: 2.293 ms. Wall: 19.33 s.

| joint | peak Nm | RMS Nm | R1.2 avail Nm | peak/avail | saturated % |
|---|---:|---:|---:|---:|---:|
| l_hip_yaw | 45.67 | 18.16 | 70 | 0.652 | 0.00 |
| l_hip_roll | 141.03 | 58.61 | 204 | 0.691 | 0.00 |
| l_hip_pitch | 230.20 | 103.12 | 350 | 0.658 | 0.00 |
| l_knee | 227.92 | 100.81 | 258 | 0.883 | 0.00 |
| l_ankle_pitch | 259.94 | 71.33 | 311 | 0.836 | 0.00 |
| l_ankle_roll | 44.68 | 17.62 | 177 | 0.252 | 0.00 |
| r_hip_yaw | 54.76 | 19.01 | 70 | 0.782 | 0.00 |
| r_hip_roll | 129.30 | 66.79 | 204 | 0.634 | 0.00 |
| r_hip_pitch | 243.28 | 103.44 | 350 | 0.695 | 0.00 |
| r_knee | 258.00 | 117.82 | 258 | 1.000 | 2.87 |
| r_ankle_pitch | 259.35 | 71.11 | 311 | 0.834 | 0.00 |
| r_ankle_roll | 56.83 | 16.63 | 177 | 0.321 | 0.00 |

The carry stays near 1.2 m/s longer than the unladen walk. Lateral position and yaw still run away (pelvis y about 1.1 m and yaw about 28° by t = 7 s), the foot drops to two contacts, and it falls at 7.733 s. The right knee is the only leg joint that saturates (2.87% of the run, peak equal to the 258 N·m limit).

## What this does not claim

The nominal walk is under 1.15 m/s on average (1.133 m/s) and it falls at 4.915 s. The push does not recover. The carry falls at 7.733 s. No run reached 20 s.
