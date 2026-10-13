# WBC r6 closed-loop re-sim

Date of these runs: 2026-10-13. Machine: Windows, Python 3.12, repo venv, CPU. `LEGS_MASS=65`, `LEGS_LIMITS=r1`, `LEGS_CONTACT` unset. Contact is the default model: condim 3, box feet 240×100 (geom half-size 0.120×0.05). No change to `CONTRACTS.md` or actuator selections.

Controller: `modules/legs/wbc/`. The plan path is still the 1 kHz QP on a 1 s slice of `walk_1p2_r2` (carry uses `carry_20kg_r2`). `_plan_mpc` is no longer open-loop playback:

- Sagittal and lateral foot placement from the DCM error against the slice. Lateral step is clipped to ±40 mm and slews at 4 mm per 10 ms. Sagittal only lengthens, up to 30 mm. Shortening the step on this torque tracker ran away in earlier trials, so a slow COM is not stepped shorter.
- Step timing is a playback rate around `rate_nom = cruise / v_plan`, clipped to about 0.98–1.03 of `rate_nom` on the 1.2 m/s walk. The slice is not slowed: slowing it pitched the robot over.
- Stance yaw is `yaw_off` (heading error, a fraction of stance-foot yaw error, and a small leaky integral). The swing hip yaw tracks `0.30 * yaw_off` (±0.08 rad). Stance hip-yaw torque uses `yaw_off`, clipped to ±12 N·m so the yaw moment does not consume the whole sole cone (`|Mz| ≤ 0.05 Fz`).
- `--cruise` scales the slice: joint velocity `*= rate`, acceleration `*= rate²`, feedforward `= g + rate_nom² * (τ_plan − g)`. Step positions are not scaled.
- The trail foot is held after the slice unloads it, and the landing asks for a slower vertical speed. That did not produce the contact-time change below.

Pass criteria are not met. Numbers below are this run, not the previous report.

CoP margin is the clearance of the measured contact CoP to the sole rectangle, in mm. The minimum over the run is reported (0 means the CoP reached the boundary). Peak CoP offset is the distance from the sole center `(0.06, 0)` to the measured CoP. 130 mm is a sole corner. Speed is pelvis x / time, the same definition as `fsim.py`. Double support is the fraction of 1 kHz samples with both feet `fz > 40 N`. Airborne is both feet `fz < 20 N`. Saturated means `|τ| ≥ 0.99` times the R1.2 peak. QP failures: 0 in every run. Mean QP time is about 2.4 ms.

Prior r6 open-loop baseline (DECISIONS L28, same mass and limits): walk fell at 5.039 s. `--cruise 0.5` and `0.8` were the same run (both fell at 4.317 s, mean 1.13 m/s). Realized double support on that baseline was 3.3% and the airborne fraction was about 7%.

## Walk (`walk_1p2_r2`, cruise 1.2)

Fail. Fell at 5.676 s (pelvis), short of 20 s. Mean speed 1.082 m/s, short of 1.15 m/s. From the half-second log, forward speed stayed between 1.20 and 1.34 m/s until 4.5 s, then collapsed (0.69 m/s at 5.0 s, 0.24 m/s at 5.5 s). The scored mean includes that collapse.

- Fall time: 5.676 s (trigger pelvis, z = 0.757 m)
- Sim time: 5.676 s (commanded 20 s)
- Pelvis x at the fall: 6.1413 m
- Mean speed (pelvis x / t): 1.082 m/s
- Mean COM vx over the second half: 0.9699 m/s
- Touchdowns: 10
- Double support (`both fz > 40`): 2.41%
- Airborne (`both fz < 20`): 9.81%
- Minimum CoP margin: 0.0 mm (log value −0.0)
- Peak CoP offset from sole center: 130.0 mm
- Pelvis yaw: −7.72° to +15.68° (`walk_yaw_roll.png`)
- Pelvis roll: −2.38° to +43.65° (the +43.7° is the fall)
- Pelvis pitch: −17.22° to +6.34°
- QP ok / fail: 5676 / 0
- Mean QP time: 2.398 ms
- Wall time: 14.83 s
- `rate_nom`: 1.0002 (`v_plan` 1.1997 m/s)
- GIF: `media/progress/2026-10-13_legs_wbc_walk1p2.gif`

The sole was flat (4 contacts, CoP margin 19–49 mm) through 3.5 s. At 4.00 s the stance foot was already on two contacts with CoP margin 0, with the DCM error near zero and the foot offset at 0. The ±40 mm step did not have an error to correct yet. The foot then stayed on the edge, yaw grew to +15.7°, roll went to +43.7°, and the pelvis fell.

| joint | peak Nm | RMS Nm | R1.2 avail Nm | peak/avail | saturated % |
|---|---:|---:|---:|---:|---:|
| l_hip_yaw | 39.73 | 12.70 | 70 | 0.568 | 0.00 |
| l_hip_roll | 128.28 | 56.39 | 204 | 0.629 | 0.00 |
| l_hip_pitch | 232.84 | 91.38 | 350 | 0.665 | 0.00 |
| l_knee | 204.74 | 95.59 | 258 | 0.794 | 0.00 |
| l_ankle_pitch | 259.33 | 54.75 | 311 | 0.834 | 0.00 |
| l_ankle_roll | 53.09 | 14.06 | 177 | 0.300 | 0.00 |
| r_hip_yaw | 59.29 | 15.08 | 70 | 0.847 | 0.00 |
| r_hip_roll | 168.12 | 66.24 | 204 | 0.824 | 0.00 |
| r_hip_pitch | 232.25 | 98.69 | 350 | 0.664 | 0.00 |
| r_knee | 258.00 | 117.92 | 258 | 1.000 | 3.28 |
| r_ankle_pitch | 260.10 | 66.03 | 311 | 0.836 | 0.00 |
| r_ankle_roll | 56.82 | 13.24 | 177 | 0.321 | 0.00 |

## Push (60 N·s lateral)

Fail. The impulse was applied, and the robot fell 0.695 s later. It did not recover.

300 N along +Y on the torso for 0.2 s (impulse 60.0 N·s) at t = 4.059 s, during left swing (phase 0.06). COM vy went from 0.0156 m/s to 1.4113 m/s (`dvy` = 1.3957 m/s). At the sample before the push (t = 4.00 s) the foot was already on two contacts with CoP margin 0, so the push landed on a step that was already rolling. Lateral DCM error after the push was about 0.78 m. The ±40 mm step cannot cover that. Wider steps (8–14 cm) were tried in earlier smokes and rolled the sole sooner on the unpushed walk, so the cap was left at 40 mm.

- Fall time: 4.754 s (trigger pelvis)
- Sim time: 4.754 s
- Pelvis x: 5.7003 m
- Mean speed (pelvis x / t): 1.1991 m/s
- Mean COM vx over the second half: 1.2167 m/s
- Touchdowns: 8
- Double support: 1.11%
- Airborne: 7.78%
- Minimum CoP margin: 0.0 mm
- Peak CoP offset from sole center: 130.0 mm
- Pelvis yaw: −7.72° to +7.60° (`push_yaw_roll.png`)
- Pelvis roll: −43.90° to +5.24°
- Pelvis pitch: −4.99° to +3.05°
- QP ok / fail: 4754 / 0
- Mean QP time: 2.377 ms
- Wall time: 12.32 s

| joint | peak Nm | RMS Nm | R1.2 avail Nm | peak/avail | saturated % |
|---|---:|---:|---:|---:|---:|
| l_hip_yaw | 32.63 | 12.46 | 70 | 0.466 | 0.00 |
| l_hip_roll | 128.28 | 58.88 | 204 | 0.629 | 0.00 |
| l_hip_pitch | 232.84 | 91.93 | 350 | 0.665 | 0.00 |
| l_knee | 204.74 | 103.94 | 258 | 0.794 | 0.00 |
| l_ankle_pitch | 259.33 | 58.09 | 311 | 0.834 | 0.00 |
| l_ankle_roll | 53.09 | 12.96 | 177 | 0.300 | 0.00 |
| r_hip_yaw | 32.83 | 12.08 | 70 | 0.469 | 0.00 |
| r_hip_roll | 120.64 | 57.19 | 204 | 0.591 | 0.00 |
| r_hip_pitch | 232.77 | 92.10 | 350 | 0.665 | 0.00 |
| r_knee | 206.18 | 101.76 | 258 | 0.799 | 0.00 |
| r_ankle_pitch | 259.74 | 62.94 | 311 | 0.835 | 0.00 |
| r_ankle_roll | 32.14 | 9.01 | 177 | 0.182 | 0.00 |

No joint saturated on the push run.

## Carry 20 kg (`carry_20kg_r2`)

Fail. Total mass 85.0 kg. Fell at 4.686 s, mean speed 0.9699 m/s. Shorter than the nominal walk. Yaw offset sat at its ±0.15 rad stop from about 2 s, and the lateral step sat at +40 mm from 2.5 s. The previous open-loop carry in the prior report lasted longer; this closed-loop carry did not.

- Fall time: 4.686 s (trigger pelvis, z = 0.790 m)
- Sim time: 4.686 s
- Pelvis x: 4.5452 m
- Mean speed (pelvis x / t): 0.9699 m/s
- Mean COM vx over the second half: 0.784 m/s
- Touchdowns: 8
- Double support: 4.29%
- Airborne: 1.90%
- Minimum CoP margin: 0.0 mm
- Peak CoP offset from sole center: 130.0 mm
- Pelvis yaw: −8.01° to +25.65° (`carry_yaw_roll.png`)
- Pelvis roll: −5.08° to +32.27°
- Pelvis pitch: −31.67° to +0.01°
- QP ok / fail: 4686 / 0
- Mean QP time: 2.366 ms
- Wall time: 12.11 s
- `v_plan`: 1.1996 m/s, `rate_nom`: 1.0003

Carry is the only one of the three runs with double support above 3.3% and airborne below 7%. It still fell.

| joint | peak Nm | RMS Nm | R1.2 avail Nm | peak/avail | saturated % |
|---|---:|---:|---:|---:|---:|
| l_hip_yaw | 41.56 | 16.84 | 70 | 0.594 | 0.00 |
| l_hip_roll | 183.87 | 65.22 | 204 | 0.901 | 0.00 |
| l_hip_pitch | 228.08 | 105.54 | 350 | 0.652 | 0.00 |
| l_knee | 258.00 | 118.74 | 258 | 1.000 | 3.59 |
| l_ankle_pitch | 299.47 | 56.44 | 311 | 0.963 | 0.00 |
| l_ankle_roll | 66.39 | 17.97 | 177 | 0.375 | 0.00 |
| r_hip_yaw | 49.95 | 18.27 | 70 | 0.714 | 0.00 |
| r_hip_roll | 156.73 | 69.60 | 204 | 0.768 | 0.00 |
| r_hip_pitch | 265.25 | 104.49 | 350 | 0.758 | 0.00 |
| r_knee | 258.00 | 122.21 | 258 | 1.000 | 4.89 |
| r_ankle_pitch | 295.45 | 61.16 | 311 | 0.950 | 0.00 |
| r_ankle_roll | 54.87 | 13.09 | 177 | 0.310 | 0.00 |

## Cruise scaling

`--cruise` now changes the slice. These two runs are not the same. Neither is a stable walk: playing the 1.2 m/s pose at a lower rate does not produce a slower gait, and both fell within 2 s. Logs: `cruise_0p5.json`, `cruise_0p8.json`.

| | cruise 0.5 | cruise 0.8 |
|---|---:|---:|
| `rate_nom` | 0.4168 | 0.6668 |
| vx at t = 0 | 0.53 m/s | 0.84 m/s |
| Fall time | 1.278 s | 1.730 s |
| Mean speed (pelvis x / t) | −0.1583 m/s | 0.4797 m/s |
| Touchdowns | 1 | 1 |
| Double support | 44.84% | 18.67% |
| Airborne | 1.02% | 0.06% |
| Min CoP margin | 0.0 mm | 0.0 mm |
| QP fail | 0 | 0 |

The double-support fractions here are high because the robot was in the trail-foot hold while it was already falling, not because it walked with a long double-support phase. The 1.2 m/s walk is the number that corresponds to the 3.3% bar, and that number is 2.41%.

## Criteria

| check | result |
|---|---|
| Walk ≥ 20 s and mean ≥ 1.15 m/s | Fail. 5.676 s, 1.082 m/s |
| Survive 60 N·s lateral push | Fail. Fell at 4.754 s, 0.695 s after the impulse |
| Carry 20 kg, same walk | Fail. 4.686 s, 0.9699 m/s |
| `--cruise` 0.5 and 0.8 differ | Met. `rate_nom` 0.4168 vs 0.6668, different fall times and speeds |
| Double support above 3.3% on the 1.2 m/s walk | Not met. 2.41% |
| Airborne bounce below ~7% on that walk | Not met. 9.81% |
| Default contact kept | Met. condim 3, 240×100 box, `LEGS_CONTACT` unset |
