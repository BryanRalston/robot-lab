# Prone data for T&R (R-146 prone check, fef9348): RL Controls, 2026-10-21

Source: `prone_data.py`, raw output `prone_data_results.json`. Setup: sim/v3 4115f6e, 68 kg nominal, CPU MuJoCo at 1 kHz,
knee pads added for sim only (**[EST]** 50×100×80 mm boxes), legs at the 0.5 derate. The lowering is a **joint-PD
stand-in**, not the R-146b WBC sequence, which is not finished. Everything here is **[EST]**: not converged against the real
controller, and contact parameters are MuJoCo defaults.

## Controller requirements (implemented)
`drive_thermal_derate.ProneLowerGuard`, tested in `test_prone_lower_guard_speed_and_force`:
- chest descent speed limit: ≤ 0.10 m/s within 50 mm of contact, ramping to 0.40 m/s at 200 mm;
- `observe()` logs the contact speed and the peak chest-pad force, and flags > 0.10 m/s or > 8.8 kN.

**The sim stand-in does NOT meet the 0.10 m/s contact speed (it gives ~0.30 m/s).** The last ~0.1 m is a passive settle as
the arms slide out, so the trajectory throttle can't slow it. Meeting it needs the WBC to support the chest on the arms until
contact (R-146b work).

## 1. Kneel CoG height
| pose | CoG height |
|---|---|
| upright kneel, knee pads + toes, trunk upright (hip 0, knee 90°, ankle +0.70) | **0.674 m** [EST, kinematic] |

## 2. Prone static load split (after MO=0, joint friction = D94 holds, settled 1.5 s)
Nominal 68 kg (total measured 645 N vs 667 N weight, so ~3 % is still in transient or numerical, [EST]):

| contact group | N | % |
|---|---|---|
| chest pad | 412 | **64.0** |
| knee pads | 177 | **27.5** |
| hands/arms | 25 | 3.9 |
| feet | 30 | 4.7 |

Under DR the chest-pad share is 60.4–60.5 % at 65 kg and 45.9–48.0 % at 68.5 kg. The settled arm and leg posture changes
the split, so read the range as **chest pad 46–64 %** [EST].

## 3. Chest-pad contact speed and force in the controlled lower, small DR sweep (8 runs)
Mass 65 / 68.5 kg × floor friction 0.6 / 1.0 × chest-pad contact solref timeconst 0.005 / 0.02 s (stiff / soft):

| | contact speed (m/s) | peak chest-pad force (N) |
|---|---|---|
| mean | **0.304** | 1487 |
| max | **0.309** | 1742 (stiff pad) |
| nominal (68 kg) | 0.298 | 1234 |

- Peak force ≤ 8.8 kN: **pass**, with a large margin.
- Contact speed ≤ 0.1 m/s: **fail** with the stand-in (see above).
- The floor-friction DR had no effect: MuJoCo takes the max friction of the pair, and the robot geoms are 1.0. A real friction
  sweep needs the robot-side friction varied too (not done).

## 4. Kneel tip-over (failed kneel, MO=0 from an upright kneel, arms passive, D94 joint friction)
| initial lean | first upper-body contact | peak chest-pad force | torso peak accel (raw / 60 Hz MA) |
|---|---|---|---|
| 0.15 rad | chest pad | **13.3 kN** | 44 g / 24 g |
| 0.30 rad | hands/arms, then chest | **13.3 kN** | 43 g / 24 g |

- Above the 8.8 kN controlled-lower limit, and below the L2 22.35 kN crush limit.
- Torso acceleration 24–44 g sits in the low part of T&R's 38–104 g open range.
- The torso acceleration is a finite difference of the torso COM velocity, so it depends strongly on contact stiffness
  (MuJoCo default solref); the **[EST]** here is not converged. Use T&R's L2 drop test for the real number.
