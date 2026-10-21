# Hands-first toe kneel at knee ≤ 125° (Robot Lab on 976eca8) — NOT achieved (2026-10-21 ~10:55 ET)
Files: `kneel_toe_wbc.py` (now: KNEE_MAX_RAD soft knee limit on q_des, H_SPEED_SCALE, knee cap 513a7d5/D99 ON by default (≥120° → 50 N·m), per-phase knee max incl. the chest lower), `kneel_toe_r125_sweep.py` → `kneel_toe_r125_sweep.json`. 68 kg, pad tc 0.02, R19 plant candidate (elbow −7.5°, wrist −55°, yaw 0), elbow caps 38 and 49 N·m [49 unruled].

## Result: 0/16 variants pass; the knee exceeds 125° in phase H (hand reach) in every one
| elbow | CoM z end A | hand ahead of toes | hand speed scale | fell | knee max A / H / K / chest | T (s, to S) | hand peak N (l/r) | hand speed m/s | chest m/s / N |
|---|---|---|---|---|---|---|---|---|---|
| 38 | 0.68 | 0.40 | 1.0 | – | 117 / **138** / 134 / 135 | 3.09 | 1433/1401 | 2.97 | no contact |
| 38 | 0.68 | 0.40 | 0.4 | – | 117 / **134** / 83 / 119 | 4.65 | 1960/2023 | 0.86 | 0.45 / 2598 |
| 38 | 0.68 | 0.55 | 1.0 | – | 117 / **136** / 120 / 130 | 3.54 | 1183/1136 | 0.87 | 0.26 / 1292 |
| 38 | 0.68 | 0.55 | 0.4 | K | 117 / **136** / 129 | 2.04 | 514/500 | 1.10 | – |
| 38 | 0.74 | 0.40 | 1.0 | K | 105 / **136** / 52 | 2.85 | 1198/1216 | 2.21 | – |
| 38 | 0.74 | 0.40 | 0.4 | – | 105 / **135** / 85 / 119 | 6.04 | 1964/1960 | 0.51 | 0.52 / 3544 |
| 38 | 0.74 | 0.55 | 1.0 | – | 105 / **137** / 135 / 136 | 4.04 | 1635/2497 | 4.4 | no contact |
| 38 | 0.74 | 0.55 | 0.4 | K | 105 / **136** / 120 | 3.28 | 1012/998 | 1.74 | – |
| 49 | same 8 variants | | | | H 134–138 in all | | ≥ 500, ≤ 2528 | ≥ 0.43 | best 0.24 m/s / 1050 N (no pass) |
Per-phase times are in the json. Gates: hand ≤ 875 N & ≈ 0.23 m/s, chest ≤ 0.1 m/s & ≤ 8.8 kN, knee ≤ 125°.

## Why (evidence, not a proof of infeasibility)
- In phase A the knee can be held ≤ 117° (CoM z 0.68) or ≤ 105° (0.74): the high-hip partial crouch works.
- In H (trunk pitches forward to reach the floor on toe support) the toe-supported legs must carry most of the body weight; the knee torque needed exceeds the **50 N·m cap** as soon as the knee passes 120°, so the knee **collapses past the q_des limit (119.7°) to 133–138°** (onto/through the D99 130° contact). The soft limit on q_des can't hold it because the cap removes the torque that would. Without the cap (KNEE_CAP=False) the same reach still reached 134–136°.
- Reaching the floor with the hands while the knee stays ≤ 120° needs either a deeper hip flexion than the −105° hip-pitch limit allows with the CoM over the toes, or hand support before the knee passes 120° — i.e. the hands must land from a higher posture (hand reach ≥ ~0.6 m below the shoulder from a ~105° knee). Not found in this sweep; a dedicated IK study (hip ≥ −105°, knee ≤ 120°, CoM over toes, hands at z 0) is the next step [not run].
- Hand plant never met 875 N / 0.23 m/s; slowing the hand guard (×0.4) lowered contact speed to 0.43–0.86 m/s but *raised* peak force (≈ 2 kN) because the body then falls onto the hands.

## 65 kg chest-lower "no result" bug (diagnosed)
With the R19 candidate at 65 kg the chest lower starts from a 0.47 m gap; the **head contacts the floor first** (`other_contact_geoms: ['head']`) and the chest stalls 26 mm above the pad, so no chest-contact speed is recorded (68 kg: gap 0.41, thighs touch, chest reaches 0). Fix needs neck pitch / head-clear posture in the lower; knee torque in that run also saturates at the 50 N·m cap.
