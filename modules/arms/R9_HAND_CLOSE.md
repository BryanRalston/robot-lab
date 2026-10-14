# RL Arms & Hands R9 (R-091): T4 loaded close at 1.50 A summed per rail + stagger
Script: `hand_close_r9.py`, results: `hand_close_r9.json`. Basis: `hand_close_r4.py` (cited maxon DCX22S 24 V + GPX22HP 103:1, η 0.65).
- **T4 limit:** **≤ 1 s close** (TARGETS T4).
- **Grip floor:** ≥ 22 N (R-076/R-081). TARGETS still says ≥ 30 N continuous [EST].

**Setup:**
- Rail limit 1.50 A × 24 V = 36 W bus. Per-flexor motor cap 1.66 A.
- Small drives hold at I_nom: 1.72 W each [worst].
- Finished flexors hold the contact load.
- Equal power share among closing flexors. Ideal converter, no droop [EST].
- **Rail A:** F1–F3, S1, S2, board logic **4.6 W hot** (Thermal A43C R-089). Split: MCU 1.2 W [Thermal], drivers/encoders/aux 3.4 W [EST split]. All of it is on A.
- **Rail B:** F4–F6, S3–S5.

**Close time (s), rail A / rail B, 30 N tip contact load (217 N tendon, the R4 [EST] basis):**
| stagger | nominal | hot R ×1.5 | η 0.50 | friction ×1.6 | worst (all three) |
|---|---|---|---|---|---|
| 0 ms | 0.656 / 0.648 | 0.667 / 0.659 | 0.728 / 0.696 | 0.699 / 0.678 | **stalls (fail)** |
| 50 ms | 0.737 / 0.734 | 0.749 / 0.744 | 0.789 / 0.763 | 0.766 / 0.749 | **stalls** |
| 100 ms | 0.837 / 0.834 | 0.848 / 0.844 | 0.859 / 0.842 | 0.845 / 0.839 | stalls |
| 150 ms | 0.937 / 0.934 | 0.948 / 0.944 | 0.951 / 0.942 | 0.944 / 0.939 | stalls |
| 200 ms | 1.037 (fail) | 1.048 | 1.051 | 1.044 | stalls |

Bus peak 1.506–1.515 A (the 0.01 overshoot is Euler step granularity; firmware regulates to 1.50).

**Findings:**
- **Stagger does not help timing.** Under a summed power cap with equal sharing, it only adds delay. Its job is RP40 inrush protection.
- **Recommended stagger: 50 ms.** All single corners pass at ≤ 0.79 s. A stagger of ≥ 200 ms breaks T4 even at nominal.
- **Combined worst corner, 30 N load: FAIL.** The holding current alone is 347 N × 4 mm / (103 × 0.5) / Kt + I0 = **1.50 A/flexor**. A 28 W share over 3 flexors at R 5.5 Ω gives only 1.30 A, so the flexors stall before full stroke.
  - **Rail current needed: 2.08 A/rail** (≈ 50 W) at 0–50 ms stagger, t = 0.93–1.00 s. 2.12 A at 100 ms.
- **Combined worst corner, 22 N load (T4 grip floor, 159 N tendon): PASS at 1.50 A.**
  - Rail A 0.80 s / rail B 0.77 s at 50 ms stagger (0.73 / 0.695 at 0 ms).
- **Decision for Arbiter:**
  - If the loaded-close basis is the 22 N grip floor, **no upsizing.**
  - If it is the 30 N TARGETS figure, **Electronics needs ≥ 2.08 A/rail, ≈ 50 W per rail** (RP40 is 40 W).
