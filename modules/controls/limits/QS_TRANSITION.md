# Quasi-static transition to pose (b) — NOT working yet (RL Controls decision 10:44, status ~10:52 ET)
`qs_transition.py`: task-space IK (kneel_toe_wbc tools) + derated PD + static ff with a pinned hand-force ramp (`ff_split`), knee hard-limited 120° in the IK and the 50 N·m cap ≥ 120° on the torque. Phases P1 crouch (CoM over feet, z → Z1) → P2 hands lowered under a speed governor (0.20 / 0.08 m/s), hands unloaded → P3 CoM shift + hand force ramp to 150 N/hand → P4 hold. 68 kg only; **no variant passed, so DR and the chest-lower join were not run.**

Probe results (all 68 kg, elbow 38 N·m, pass needs hand vz ≤ 0.23 m/s, ≤ 875 N, knee ≤ 120°, no fall):
| Z1 | CoM back of toe | trunk pitch target / rate / weight | hand x ahead | result |
|---|---|---|---|---|
| 0.62–0.76 | 0.04 | 1.25 / 0.5 / 2 | 0.30 | falls in P1 (CoM at the toe edge with flat feet → tips onto the head) |
| 0.62 | 0.08 | same | 0.30 | hands at 5.6 m/s, 830–970 N, fall in P3; knee 119.7° |
| 0.62 | 0.12 | same | 0.30 | knee collapses to 136° in P2, fall |
| 0.68 | 0.08 / 0.12 | same | 0.30 | P1 OK (knee 106–110°), **hands stall 50–70 mm above the floor** (no contact in 14 s) |
| 0.68 | 0.08 | 1.5–1.7 / 0.5 / 2 | 0.25–0.35 | trunk pitch overshoots (to 2.2 rad), hands hit 1.3–3.1 m/s, 440–1530 N, fall |
| 0.68 | 0.08 | 1.3–1.5 / 0.2–0.3 / 10–20 | 0.25–0.45 | stall then fall in P2, or hands 3.2–3.9 m/s / 1.3–1.4 kN in P3 |
- P1 (toe-line CoM crouch, knee ≤ 110°) works at Z1 0.68. The reach (P2) is the failing step: the IK cannot bring the hands the last 50–70 mm with the CoM held over the feet at knee ≤ 120° and hip ≥ −105° — it either stalls, or the trunk-pitch task drives the CoM off the feet and the body drops onto the hands. Static pose (b) has the CoM *between* feet and hands, i.e. it is **not reachable without loading the hands first**; "hands unloaded with CoM over the feet" until contact appears geometrically marginal here (hands short of the floor by ~5–7 cm at the feasible CoM). [Diagnosis from the probes, not a proof.]
- Next (not done): reach-feasibility IK for the exact P2 end state (hands at z 0, CoM over toes, knee ≤ 120, hip ≥ −105, waist/shoulder free) to confirm or refute that margin; if refuted, a P2 pitch/CoM schedule that tracks it.
