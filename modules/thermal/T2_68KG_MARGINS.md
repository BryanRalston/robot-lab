# T2 68.0 kg condition (561eb35): actuator thermal margins at 68.0 kg + 20 kg carry (RL Thermal, 2026-10-21)
**Scaling** (hand calc on the existing D68/R1/Controls/Actuators results):
- Leg joint torque ∝ (body + 20 kg). Baselines are on the 66.2 kg basis (D68/R1, Controls R-096, Actuators r069 trim).
- (88.0/86.2)² = **+4.2 % copper**. Winding rise × (1 + 0.042·f_cu·1.1 hot-copper feedback), with f_cu ≈ 0.85 (iron loss doesn't scale).
- Vs 67.1 kg (R-118) this is +2.1 % copper, ≈ +1–1.5 K.
- Arm joints carry the fixed 20 kg and are unchanged by body mass.

**Limits:**
- **120 °C design** (derate trip 130); **150 °C torque-off** (TBM2G abs 155).
- "R-077 limit" = the R-096 revised duty: ≤ 40 % carry, bouts ≤ 5 min.
- "h 8 / h 12" = effective housing h, W/m²K (h 8 ≈ the closed-cover/poor-ducting floor, R077_KNEE_H).

| joint (worst side), P-042 carry × 1.1, 35 °C | h 12, continuous | h 12, R-077 duty | h 8, continuous | h 8, R-077 duty | verdict |
|---|---|---|---|---|---|
| **knee** (rev B, drives off) | 97.6 (Actuators r069 basis; Controls' h 12 "pass" case) | ≈ 90 | **133.7 (η 1.0) / 155.5 (η 0.7)** | **115.3** | **PASS under R-077 duty** (4.7 K design margin at h 8, ≥ 30 K at h 12). Continuous at h 8: **FAIL design**, and FAIL torque-off at η 0.7 |
| **hip_pitch** | 135 (R1 open-equivalent h 12, ×1.042) | ≈ 110 | runaway (h_min 10.1 for 155 °C) | ≈ 138 | **PASS only with the A35 vents (h ≥ 15: ≈ 108 continuous)**. At h 12 continuous: FAIL design (pass torque-off, 15 K). At h 8: FAIL design even under duty (12 K under torque-off) |
| ankle | 107 | ≈ 98 | 121 (≈ covered/boot case) | ≈ 104 | PASS (h 8 continuous 1 K over design, pass torque-off by 29 K) |
| shoulder_pitch (P-042 band ≤ 53.75 N·m) | ≈ 105 | ≈ 95 | ≈ 130 | ≈ 110 | PASS (h 8 continuous over design, pass torque-off by 20 K); unchanged by body mass |
| elbow (P-042 ≤ 15 N·m) | ≈ 70 | ≈ 65 | ≈ 80 | ≈ 70 | PASS, large margin; unchanged |

**Bond** (EA 9396, A38 R-110 table + hip case +4 %, ≈ +0.9 K; L62 ≈ 10.6 K/W):
- design 55.1 / 61.6 °C (R_col 8 / 14);
- worst 59.5 / **67.6 °C** vs the 70 °C rule: **PASS** (2.4 K).
- The design-point ≤ 60 °C is met only at R_col ≤ ~12, which was already the J-T1 gate. No new failure.

**R-120 shoulder pad** (CRBH 7013 A + stand-off): arm load is unchanged. Pad bond ≈ 49 °C walking / 56 °C still air vs 60: **PASS**, 4 K.

## Condition verdict
**MET, conditionally.** At 68.0 kg + 20 kg every joint stays ≤ 120 °C under the R-077/R-096 carry duty when the A35 vents perform (h ≥ 12 knee, ≥ 15 hip). The binding margin is the knee, 4.7 K at h 8.
- What 68 kg costs vs 67.1: ≈ +1–1.5 K everywhere. No joint flips from pass to fail at the duty limit.
- **Unchanged pre-existing fails, not caused by 68 kg:**
  - continuous carry at h 8 (knee 134–156, hip runaway);
  - hip_pitch continuous at h 12 (135).
- These remain covered by: the R-096 duty limit + the model remaining-time limit; the vents (A35/A36); J-T1/G5 h measurement. The 130 °C derate is the backstop.
