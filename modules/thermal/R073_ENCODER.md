# R-073: maxon ENX 22 encoder end on the DCX 22 flexors (≤ 90 °C required, rated 100 °C) (RL Thermal, 2026-10-14)
Model: `a43c_board` 6-flexor forearm, 4.3 W board, 35 °C, 30 N hold from cold (0.952 A demand) through the ladder transients, 4 h. **Peaks over the whole run, not just steady state.** Script `r073_encoder.py`, `results/r073_encoder.json`.
Encoder end [EST]: T_enc = T_housing + 0.3·(T_wind − T_housing) (rear bearing/flange) + 0.15 W × 15 K/W self-heat.
Encoder clamped to the shell (fix): T_enc = T_shell + 0.5·(T_housing − T_shell) + self-heat.
Grip scales with current: 30 N at 0.952 A (friction 1.3) or 0.88 A (friction 1.2). Walking and carry share the walking shell-to-air path (1.4 K/W); still air is 2.4 K/W.

| ladder | motor mount | env | encoder peak | encoder peak, encoder end clamped | winding peak | shell | sustained I | grip N (fric 1.3 / 1.2) |
|---|---|---|---|---|---|---|---|---|
| adopted 55/70/80/88 | clamped | walk/carry | **75.5** | 66.4 | 89 | 60 | 0.70 | 22.1 / 23.9 |
| adopted | clamped | still | **85.6** | 76.5 | 95 | 70 | 0.50 | 15.8 / 17.0 |
| adopted | loose | walk/carry | 86.9 | 71.7 | 101 | 60 | 0.70 | 22.1 / 23.9 |
| adopted | loose | still | **94.6 FAIL** | 81.0 | 104 | 70 | 0.50 | 15.8 / 17.0 |
| tight 50/60/70/80 (0.80/0.70/0.55/0.40/0) | loose | still | 82.4 | 72.9 | 91 | 65 | 0.55 | 17.3 / 18.8 |
| tight | loose | walk | 85.3 | 71.4 | 94 | 60 | **0.55** | **17.3 / 18.8 FAIL T4** |
| **B 55/82/88 (0.84/0.70/0.50/0)** | **clamped + encoder clamped** | walk | — | **66.4** | 89 | 60 | 0.70 | **22.1 / 23.9** |
| **B** | **clamped + encoder clamped** | still | — | **86.3** | 105 | 79 | 0.70 | **22.1 / 23.9** |

## Verdict
- **Adopted ladder + motors clamped (Arms fix): encoder ≤ 90 °C in every case. PASS** (peak 85.6 still air, 75.5 walk/carry).
- **Loose mount fails in still air (94.6 °C).** So the paste-clamped mount is **mandatory**, not optional.
- **A tighter ladder is not the answer.** It passes the encoder but drops walking grip to ~17–19 N, below the T4 22 N.
- **T4 ≥ 22 N sustained:**
  - Walking/carry passes on the adopted ladder (22.1 N at friction 1.3, 23.9 at 1.2).
  - **Still air fails (16–17 N)**, because the 70 °C step drops the current to 0.5 A.
- **Fix for both:** clamp the motor **and** the encoder end to the Al shell (paste or gap pad on the ENX cap, ≈ +2 g) and use ladder **B: 55/82/88 °C → 0.84/0.70/0.50/0 A**.
  - Encoder 86 °C in still air (4 K margin), 66 °C walking.
  - Holds 0.70 A (≥ 22 N) in both environments.
  - Board ≈ 87 °C, ≥ 23 K below the 110 °C NTC.
- If the encoder end cannot be clamped, keep the adopted ladder and accept 16–17 N in still air (T4 waiver), or measure friction ≤ 1.0.
- G5: thermocouple on one ENX cap.
