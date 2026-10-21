# R-145 §1: does anything hold a crouch after MO=0? (RL Actuators, 2026-10-21)
**Answer: NO.** No hip pitch, knee or ankle has a brake, and all three twin roller-screw units backdrive easily. With MO=0 the crouch collapses. The R-145 rule (MO=0 only after kneel contact with the CoM supported) is **required, not just conservative**.

**Evidence:**
- **Transmissions:** all three are direct-drive twin roller screws (motor on the nut-rotor, no gear stage). Sources: BENCH_TEST_PLAN.md l.23, DECISIONS D7/D12.
  - Joint ratio N = 2πr/lead: hip pitch RV12x4 on r 50 mm, N = 78.5 (× worst arm factor 0.77 = 60.5, D7); knee RV12x5 on r 47.5, N = 59.7 (D12); ankle RV12x4 on r 73 (L-ankle 70 → 73), N = 114.7.
- **Backdrive:** Rollvis RV12 indirect (backdrive) efficiency 0.88 × 0.95 ≈ **0.84** (rollvis_rv_tables.pdf p.24; DECISIONS D19). A screw with η' > 0 is not self-locking; only 16 % of the load torque is lost to screw friction.
  - The RV12 preload torque Mv is listed per nut in the table (p.24), but the PDF text extraction is unreadable. Under 0.1 N·m [EST] at the single nut.
- **Motor holding:** TBM2G static friction Tf (hysteresis + cogging) is defined in tbm2g_manual p.~30, but no Tf value is tabulated for 07613D or 06013D. Taken as ≤ 0.05 N·m per motor [EST, generous]. No brake option on the frameless TBM2G is used (manual §9.1.2 brake terms only).
- **No brake part** anywhere in the repo BOM/CONTRACTS ("brake" only means the DC-bus brake chopper).

| joint | N | friction hold at joint, ≈ 2 × Tf × N / 0.84 (+ Mv) | gravity torque in crouch | holds? |
|---|---:|---:|---:|---|
| hip pitch | 60.5–78.5 | ≈ 7–9 N·m [EST] | ~30–45 N·m (crouch, [EST]; no Controls figure on file) | **no** |
| knee | 59.7 | ≈ 7 N·m [EST] | **64.4 N·m** (Controls R1_STATUS l.113, carry crouch 66.6°) | **no** (×9 short) |
| ankle | 114.7 | ≈ 8 N·m [EST] | ~25–35 N·m [EST] | **no** |

Even if Tf were 4× higher, nothing would hold. The motor-side backdrive torque at the knee is 64.4 / 59.7 × 0.84 = 0.91 N·m across 2 motors, against ~0.1 N·m of friction.

**What is needed:**
1. **Recommended (no mass):** the R-145 path. Kneel to ground contact so the CoM rests on the knees/shins and feet, then MO=0. In a supported kneel the joints carry no gravity torque, so friction doesn't matter. Controls must verify the kneel pose is torque-free in sim, i.e. the CoM sits over the knee-shin/foot support polygon with no joint needing torque to stay put. The deep seated sit (R-145 §3) is not this path.
2. **Only if a stand-still hold with power off is ever required:** a spring-applied, power-off brake on one motor per joint.
   - Brake sizing at the knee: ≥ 0.91 × 2 (SF) ≈ **1.8 N·m** on a single nut-rotor, or 1 N·m on each motor. Hip pitch ~1.5 N·m, ankle ~0.6 N·m.
   - A ~1–2 N·m permanent-magnet or spring brake of Ø40–50 mm class [EST, no catalogue cited in repo] is about 0.10–0.20 kg and 6–10 W release power each.
   - × 6 per robot (hip pitch, knee, ankle × 2 legs) = **+0.6–1.2 kg, 36–60 W continuous** while powered, plus axial length on each unit.
   - **Not recommended** against T2 (68.4 vs 66.5 kg). It needs a cited brake datasheet before any booking.
