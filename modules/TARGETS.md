# TARGETS.md: whole-robot targets — **APPROVED (Bryan, 2026-10-13)**
Written by RL Arbiter, 2026-10-13. Approved by Bryan via Robot Lab on 2026-10-13. Arbiter rulings against this file are final. Interpretations: see RULINGS.md (R-003 clarifies T5 carry speed).

## Important caveat about the benchmark
Tesla has **never published an Optimus datasheet**. Most numbers that circulate (173 cm, 57 kg, 20 kg payload, 2.3 kWh) trace back to AI Day 2021/2022 slides for the first-generation concept/prototype and are often relabelled as Gen 2 or Gen 3 [S1][S2][S3]. Tesla's own Gen 2 claims (Dec 2023 video) are relative: −10 kg, +30 % walking speed, 2-DoF neck, 11-DoF tactile hands, foot F/T sensing [S1][S4]. Gen 3's only firm hardware disclosure is the hand/forearm: 22 DoF per hand, 25 actuators per forearm+hand (23 hand linear + 2 wrist linear), tendon driven [S2][S5]. Each benchmark below is labelled **Tesla** (Tesla statement or patent), **2nd** (secondary/unverified), or **[EST]**.

## Targets

| # | metric | Optimus benchmark (label, source) | v3 today (source) | target (v4 module program) | weight |
|---|---|---|---|---|---|
| T1 | Height | ~1.73 m, Gen 1 figure (Tesla AI Day, via [S1]); no Gen 2/3 figure [S3] | not stated in v3; sim pelvis origin at 1.160 m (`sim/v3/humanoid_v3.xml`) → stature ≈1.7–1.8 m [EST] | 1.70–1.78 m [EST]; Torso/Head module to state actual value | 0.03 |
| T2 | Mass (incl. battery, hands) | Gen 2 "10 kg lighter" than predecessor (Tesla [S4]); 57 kg / 63 kg figures (2nd [S6][S7]) | 63.8 kg catalog rollup (`v3/analysis/results/v3_checks.md`); CAD solids 56.3 kg w/o harness/covers (`v3/REVISIONS.md` §G) | ≤ 65 kg hard; stretch ≤ 60 kg | 0.15 |
| T3 | Body DoF (excl. hands) | 28 (Gen 1) / 30 with 2-DoF neck (Gen 2) ([S1][S8], Tesla-derived); 37 joints for V3 (2nd [S3]) | 30: legs 2×6, waist 2, arms 2×7 (shoulder 3, elbow, wrist 3), neck 2 (`v3/analysis/v3.py` joint list) | 30 (keep) | 0.05 |
| T4 | Hand capability | Gen 2: 11 DoF, tactile fingertips, egg pick (Tesla [S4]); Gen 3: 22 DoF, 25 forearm actuators, tendon (Tesla patent [S5]) | 11 drives/hand (6 flexor + 5 small), 38.2 N continuous fingertip, 0.74 s full close; no tactile sensing specified (`v3_checks.md` Hand drive) | ≥ 11 actuated DoF, ≥ 30 N fingertip continuous [EST], ≤ 1 s close, fingertip tactile; tendon life demonstrated by test (see AUDIT A1) | 0.12 |
| T5 | Payload (carry, two hands, at waist) | 20 kg (2nd; AI Day 2021 concept slide [S2][S6]) | not checked in v3 (arm torque needs from v2 `req`, no payload case found) | 20 kg two-handed carry at walking; 10 kg [EST] one-hand at full reach | 0.12 |
| T6 | Walking speed | no absolute Tesla figure; "+30 %" vs prior only (Tesla [S4]); 1.2 m/s for V3 (2nd [S3]) | not verified by gait sim; power model assumes 1.2 m/s with cost of transport 0.25 [EST] (`v3.py` line 200: mech = 0.25·m·g·1.2·1.3), 1 stride/s, joint speeds [EST, v2] | ≥ 1.2 m/s sustained on flat [EST], verified in sim with joint torque/speed limits from CONTRACTS | 0.10 |
| T7 | Runtime | 2.3 kWh pack (Gen 1, 2nd [S2]); "8–10 h" claims unverified (2nd, [S9]) | 2.1 h walking, 1474 Wh, 622 W (`v3_checks.md` Power) | ≥ 2 h continuous walking hard; ≥ 4 h mixed work (50 % stand/manipulate) [EST]; swappable pack [EST] | 0.10 |
| T8 | Fall survival | no Tesla figure | side fall from standing passes static/FEA checks with clutch + 30 mm EPP pads (`v3_checks.md`, `REVISIONS.md` §G); sim cannot yet stand without balance controller | survive ≥ 100 side/back/front falls from standing without structural damage [EST]; ≥ 1 fall/day for life on pads/covers (replaceable) [EST] | 0.13 |
| T9 | Service life | no Tesla figure | 5 y × 365 d × 8 h = 14 600 h walking design life (`v3.py` LIFE_H) | 14 600 h L10 for all actuators/bearings at walking duty; wear parts (pads, tendons) replaceable with stated intervals | 0.10 |
| T10 | Manufacturability / BOM | Tesla target ~$20–30k at volume (Tesla statements, 2nd) — not used for ruling | catalog parts (Kollmorgen frameless, Harmonic Drive, Rollvis) — high cost [EST] | every part catalog or drawing-ready; cost tracked per module [EST] | 0.10 |

**Status 2026-10-13 R2:** T2 mass 65.79 kg (NOT MET; 64.49 kg if R-001 Legs −0.50 / Torso −0.80 land). T7 runtime 1.81 h at weighted evidence, 2.19 h modeled (NOT MET, R-009). T6 NOT DEMONSTRATED (G4).

**Status 2026-10-13 R3 (R-010..R-013):** T2 mass 65.79 kg CAD-supported (NOT MET); 64.43 kg if Legs structure (4.84, FEA pending) and Torso −0.80 land, 64.64 kg incl. +0.21 kg linkage risk. T7 MET provisionally at **1.0 m/s rating speed** (Arbiter deviation R-010; 2.09 h typical / 2.04 h binned pack, half regen credit), contingent on cell binning and usable-fraction evidence; **1.2 m/s tracked: 1.73 h (NOT MET)**. T6 target ≥ 1.2 m/s unchanged, NOT DEMONSTRATED (G4). T5 carry verified at 0.8 m/s provisionally (R-011); 1.2 m/s carry tracked at ankle 1.10× (fails 1.2×). Target values unchanged.

Weights sum to 1.00. **Hard constraints (cannot be traded): T2 ≤ 65 kg, T7 ≥ 2 h walking, T8 structural survival, safety.** Weights apply only to trades among soft margins.

## How the Arbiter uses the weights
For a disputed proposal: score Δ on each affected target as fraction of target (+ good, − bad), multiply by weight, sum. Ties or |score| < 0.01 → keep the contract as is. Any hard-constraint violation → reject regardless of score. Evidence quality multiplies the claimed Δ: check script/sim/datasheet ×1.0, [EST] ×0.5, unsupported ×0.

## Sources
- [S1] wujec.ai, Tesla Optimus Gen 2 profile — https://wujec.ai/en/entity/tesla-optimus-gen-2
- [S2] RoboZaps, "Tesla Optimus Gen 3" (Aug 2026) — https://blog.robozaps.com/b/tesla-optimus-gen-3
- [S3] Optimus Review, Gen 2 vs Gen 3 sourced reference — https://optimusreview.com/specs/
- [S4] iTechFAQs, "What the 2023 Demo Really Showed" (summarises Tesla's 13 Dec 2023 video) — https://www.itechfaqs.com/teslas-optimus-gen-2-demo-showed-faster-walking-and-more-capable-hands-but-not-a-finished-robot/
- [S5] Electric-Vehicles.com, Tesla Gen 3 forearm/hand patents (Apr 2026) — https://eletric-vehicles.com/tesla/tesla-files-patents-revealing-optimus-gen-3-mechanical-blueprint/
- [S6] Birdwave Atlas, Tesla Optimus — https://atlas.birdwave.io/products/tesla-optimus
- [S7] RobotHub, Optimus Gen 2 — https://www.robothub.app/en/robots/optimus-gen2
- [S8] Optimusk blog, actuators & DoF Gen 2 vs 3 — https://optimusk.blog/blog/tesla-optimus-degrees-of-freedom-actuators/
- [S9] Humanoid.press, Optimus 3 database entry (unverified claims) — https://humanoid.press/database/humanoid-press-database-tesla-optimus-3/
Primary Tesla documents (AI Day slides, 13 Dec 2023 video, patent numbers) were not fetched directly; an open action is to replace secondary citations with them.

## READY-FOR-BUILD gates (updated every round by the Arbiter)
The design is ready to build only when all five gates are PASS.

| # | gate | status | as of | evidence / what's missing |
|---|---|---|---|---|
| G1 | Every part is a catalog part number or has a drawing-ready spec (material, tolerances, process) | NOT MET | 2026-10-13 R1 | Leg actuators now catalog (TBM2G, CSG, RV12x4, Gold Twitter, AksIM-2; `actuators/results/sizing.md`). Housings are a parametric [EST ×1.25] model. Linkages (crossbar, trunnions, hubs) are [EST] masses only. Structure has no drawings. Placeholders (torso, arms, hands, head, brain) are unstaffed. |
| G2 | CAD assembly complete, zero clashes across full ROM | NOT MET | 2026-10-13 R1 | v3 CAD + `v3/cad/clash.py` cover v3 only. Twin-screw hip_pitch, 40 mm knee lever and the P-003 ROM (ankle −60°, hip −120°) are not in CAD. |
| G3 | Strength, fatigue, thermal and life checks pass with converged FEA | NOT MET | 2026-10-13 R3 (leg structure FEA pending, R-013) | v3 FEA (`v3/cad/out/fea_v3.md`) is for v3 loads/geometry. Actuator thermal is a lumped model (max ΔT 54 K walk/stairs, 66 K carry). Screw L10 at new levers not re-run (O4). |
| G4 | Walks 1.2 m/s, does 20 kg carry and push recovery in a domain-randomized sim with CONTRACTS limits | NOT MET | 2026-10-13 R1 | Forward sim (`legs/results/fsim/`) walks 0.8 m/s; falls after ~14 steps at 1.0 and ~10 at 1.2 m/s, even with 2× torque limits. No domain randomization yet. |
| G5 | Hardware test plan: single-actuator bench, then single-leg, with pass criteria | IN PROGRESS (plan drafted, `actuators/results/BENCH_TEST_PLAN.md`) | 2026-10-13 R3 | No plan exists. Must cover torque/speed envelope, thermal at gait RMS, screw life sample, and **(R-009/R-010, deadline end of round 4) net DC-bus energy per stride on walk_1p2: pass = steady robot draw ≤ usable Wh/2 h (729 W) i.e. ≥ 235 W realised regen; plus pack: cell binning ≥ 4400 mAh and usable fraction at 3.4 V/cell**. |
