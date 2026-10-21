# Controls soft / software joint limits (RL Controls)

## Shoulder roll abduction (interim, Arms R7 / R-076)
- **Soft limit: |shoulder_roll| ≤ 115°** (left +115, right −115 by mirror). **R-127 (5c203ad)**: ID babab4a sweep shows contact at 132°; R15 coarse torso-cover penetration ≥ ~118°. Was 135° interim. Hard MJCF range −15…180° unchanged. Back to 135° only on ID torso-cover evidence (≥ 3 mm).
- Reason: with the shoulder pad on the roll-yaw link, above ≈135° the pad face turns toward the head. Head/cap clearance is not yet verified (Arms Job 1 head sweep pending).
- Hardware MJCF range stays (−15, 180) L / mirrored R. This is a **controls soft stop**, not a hard-stop change.
- Config: `soft_limits.json` → `shoulder_roll_abduction_deg: 115`. Runtime helper: `soft_limits.py` (`clamp_q`, `roll_soft_limit_rad`).

## Elbow torque (Arbiter R-080 / R-085)
Two distinct limits — both real; do not collapse them:

| limit | value | kind | source |
|---|---|---|---|
| **Software hard torque cap** | **≤ 69 N·m** | instantaneous command / effort | R-080 (rated 76 N·m; 75.5/76 = 1.01× was too thin) |
| **Thermal short-time hold** | **≤ 40 N·m for ≤ 3 min, then ≤ 28 N·m** | continuous / I²t | Thermal O-A2 / P-043; R1 carry pose static was 40.1 N·m |

- P-042 carry (elbow 14.51 N·m after forearm +15 mm) is well inside both (pose rule ≤ 15 N·m; vs 69: margin **4.76×**).
- Full-reach 10 kg (0.665 m): static 42.41 N·m. With R1 α = 20 rad/s² [EST] inertial ≈ 31.1 N·m → total ≈ 73.5 > 69.
- **R-085:** keep 10 kg payload; when payload > 8.5 kg **and** reach is near full, scale arm acceleration to **≤ 84 % of the R1 profile (R-102; 0.85 overshoots 69 Nm at 287 mm forearm)**, blended smoothly with reach (no step). See `elbow_accel_limit.py`.
- At 287 mm forearm: static 42.62 + inertial 31.06. Scale 0.85 → 69.02 > 69; **implemented 0.84 → 68.71 Nm**. Time +9.1% on accel-limited segments (was +7.2% at 0.87). Flag to Arbiter (R-102 asked 0.85).

## Config files
- `soft_limits.json` — numeric soft stops and elbow caps
- `soft_limits.py` — clamp helpers
- `elbow_accel_limit.py` — R-085 reach/payload accel scale

## R-085 timing vs O-T5 (light estimate)
- Accel scale 0.87 → time on accel-limited segments scales ≈ 1/√0.87 ≈ **+7.2 %**.
- O-T5 A3 pick/place = 6 s each [EST]. If ≈ 2 s of each is full-reach 10 kg accel-limited, +0.14 s per phase → +0.28 s on T-A pick+place.
- T-A cycle 52 s → **+0.5 %**; T-D (16 picks) → +2.2 s on 307 s ≈ **+0.7 %**. Carry-walk and stand phases unchanged (P-042 elbow 14.5 N·m, no accel cap).
- **Verdict: timing still acceptable** at the [EST] O-T5 fidelity; no cycle-time target is broken. Revisit when the RL pick policy has measured timings.

## R-102 elbow scale (2026-10-14)
- Forearm 287 mm (Arms R10 EXT 17): static **42.62**, R1 inertial **31.06**.
- 0.87 → 69.64; **0.85 → 69.02 > 69**; **0.84 → 68.71** (margin 0.29). Config uses **0.84**.
- O-T5: time scale 1/√0.84 ≈ **+9.1%** on accel-limited segments. T-A pick+place ≈ +0.36 s on 52 s (**+0.7%**); T-D ≈ +2.9 s on 307 s (**+0.9%**). Still acceptable [EST].
