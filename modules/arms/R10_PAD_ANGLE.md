# RL Arms & Hands R10: pad-normal impact angles (Controls 92f2cea), elbow accel at 287
Script: `pad_angle_r10.py`, results: `pad_angle_r10.json`.
- sim/v3 with the hand moved +17 mm (forearm 287).
- Pad normal = +y of the link after `l_shoulder_roll`.
- Ground normal: trunk tipped 85° toward the fall azimuth (az 90 = side, 45 = LF, 135 = LB).
- Clearances: torso, pelvis and thigh; forearm r 38, fairing sphere r 62, hand r 45.
- Fall torque: inertial [EST], as `tuck_r6`.
- **Calibration:** this model gives tuck B side 5°, where Controls' FK with crouch gives ~10°, and diagonals 45° where Controls gives ~63°. **Read angles as relative.** Controls should re-check the chosen poses in their FK.

**Pad geometry:** n = Ry(pitch) Rx(roll) ŷ = (sin r · sin p, cos r, sin r · cos p).
- The pad can only gain a fore-aft component through the roll × pitch product. Diagonals therefore need big roll **and** pitch near the limit, or a trunk (waist-yaw) turn.
- The pad centre ≤ 10 mm from the CRBH plane is a mount property (R7/R8 boss), so it is independent of pose ✓.

## (1) Side falls
| pose | angle | min gap | ahead of chest | τ fall [EST] |
|---|---|---|---|---|
| **tuck B (+5/0/0/0)** | **5° (Controls ~10)** | 59 mm | −97 | 351 ≤ 369 |
| R5 (−20/−5/−60/−110) | 61.7 | 8.7 ✗ | +145 ✗ | 152 |
| R5 with yaw 0, tight elbow (+60/−5/0/−125) | 5.0 | 26 | −1.1 | 165 |

- Recommend **tuck B for side falls** (it already passes). **Retire R5:** it fails R-065 projection and clearance anyway.
- The compact alternative (+60/−5/0/−125) is at the pitch ROM stop (+60) with only 1 mm behind the chest. **Not preferred.**
- **τ fall for tuck B is now ≈ 351 N·m [EST] at 287 (343 at 270): 5 % margin.** T-031 measures it.

## (2) Diagonals (LF az 45, LB az 135)
| option | LF | LB | notes |
|---|---|---|---|
| tuck B, no change | 45.2° ✗ | 45.2° ✗ | Controls ~63 |
| **tuck B + waist yaw into the fall** | **5.0° at wy −45; 15.8° at −30** | **5.0° at +45; 15.8° at +30** | Waist yaw range ±90 (sim/v3). The arm/torso relationship is unchanged, so the tuck clearances hold. The hand stays ≥ 0.18 m from the thigh at 45°. |
| arm-only per-direction pose | +60/+50/−30/0, 11°: arm abducted at the pitch stop ✗ | +30/−15/+30/−75, 14.5°, gap 22 mm, τ 283 | LB is usable but marginal. LF arm-only is not acceptable. |
| fixed pad-face wedge | — | — | **Rejected.** One wedge that aligns diagonals by ~45–60° de-aligns side falls by the same angle. You can't have one wedge per direction on one pad. |

- **Recommend a pose, no hardware:** tuck B + waist yaw ±45° toward the fall-side shoulder (LF: −45°, LB: +45°; mirror for the right).
- **Controls must verify timing.** CONTRACTS waist_yaw speed is 2 rad/s, so 45° takes ≥ 0.39 s plus accel, against the fall time. Also check the chest pad and the forward stop with the trunk turned.
- If waist yaw is too slow:
  - LB: use the arm pose +30/−15/+30/−75 (14.5°).
  - LF: stays open. Accept ≤ 30° (wy −15) with Materials' off-axis knockdown 0.73 at 25° → **flag to Materials/Arbiter**.
- No ID/Materials wedge request.

## (3) Elbow peak at full reach, 10 kg, forearm 287
- Static 42.62 N·m (`forearm_ext_r7.json`, EXT 17).
- Inertial at the R1 profile: 29.7 × 0.387/0.370 = 31.06.
- At 87 %: 42.62 + 27.02 = **69.64 > 69 ✗.**
- **Fraction for ≤ 69: (69 − 42.62)/31.06 = 0.849 → use 0.84** (68.7 N·m, 0.3 margin). Time penalty 1/√0.84 = +9.1 % on accel-limited segments (Controls had +7.2 % at 0.87).
