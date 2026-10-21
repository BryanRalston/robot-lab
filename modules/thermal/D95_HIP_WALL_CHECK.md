# D95 check: hip-pitch Elmo plates on the pelvis rear wall (Actuators 27afe00, Torso 5abcd56) — 2026-10-21 EDT
Script d95_hip_wall.py (lumped [EST]). Basis: 4 plates 84 × 84 on G10 8.5 mm at x −85, z 1136–1220; pelvis shell 7075 4 mm, 170 × 370 × 104, open top and bottom; no battery behind the wall (Torso). Drive loss 3.0 W duty / 6.2 W continuous (R131 loss table). Back gap h 5.6 + rad 6 (R131 rev 2 b). Hip-yaw winding ≤ 58 °C duty / ≤ 68 °C worst (R1_BUDGET), heat into the wall by radiation + mount conduction 2–5 W/side [EST]. 35 °C ambient, 68 kg duty.

| case | wall (inner ≈ outer, 7075 spreads) | drive base |
|---|---|---|
| standing duty, h 8 | **41 °C** | 60–69 °C (69 = R131 rev 2 b at 45 °C structure) PASS |
| walking duty, h 15 (vents) | 39 °C | 53 °C PASS |
| standing continuous, h 8 | 47 °C | **87 °C FAIL → firmware derate (as R131)** |
| walking continuous, h 15 | 42 °C | 71 °C PASS |
| worst: continuous h 8 + hip-yaw conduction 5 W/side | **49 °C** | 88 °C (derate) |

- **Wall ≤ 50 °C: PASS** in every case; worst 49 °C (thin, 1 K) only at continuous standing with worst hip-yaw conduction [EST].
- **Hip-yaw housings:** the wall (≤ 49 °C) is cooler than their skin (≈ 55–65 °C [EST]), so the housings still reject heat to it; the plates add ≤ +1 K to hip yaw [EST]. Hip-yaw winding margin unchanged (≤ 68 vs 120). PASS.
- **Shield:** not required. Recommended cheap fallback if TP-G5 thermocouples show wall > 47 °C: Al foil (ε ≤ 0.05) on the wall inner face opposite the hip-yaw housings (y ±130), ≈ 2 × 110 × 104 mm, +0.005 kg [EST]; cuts radiation input ≈ 80 % → worst ≈ 46–47 °C.
- Conditions: G10 standoffs with no metal contact (Torso tapped M3 OK); hip-pitch vents h ≥ 15 when walking; continuous standing relies on the 75 °C derate.
