# PROPOSALS.md
Any change to CONTRACTS.md or TARGETS.md, or to another module's files, starts here. Append; never edit someone else's entry (add a comment line instead). IDs: P-NNN, sequential.

## Template
```
### P-NNN: <short title>
- Date: YYYY-MM-DD
- Module / proposer: <module> / <agent>
- Affected owners: <modules>
- Change: <exact contract/target line, old → new>
- Impact on contracts: <mass Δ kg, power Δ W, envelope, mounting, bus, torque/speed>
- Impact on targets: <T# and Δ, with weights>
- Evidence: <check script + result file, datasheet URL, sim log; mark [EST] for estimates>
- Affected owner response: <agree / disagree + reason>  (date)
- Status: open | agreed | disputed → R-NNN | withdrawn
```

## Proposals

### P-001: Leg joint torque requirements from gait inverse dynamics (replace v2 mass-scaled values)
- Date: 2026-10-13
- Module / proposer: Legs / RL Legs
- Affected owners: Actuators (selection, mass, thermal), Arbiter (T5/T6 trade)
- Change (CONTRACTS §1a "need peak N·m" for leg rows, need = 1.5 × gait-ID envelope peak, per the existing margin rule): hip_yaw 24.0 → 86; hip_roll 122.1 → 184; hip_pitch 114.8 → 398; knee 231.9 → 266; ankle_pitch 153.2 → 359; ankle_roll 57.5 → 61. Also add a continuous (RMS) torque line for thermal sizing (envelope RMS, one side): hip_yaw 16, hip_roll 50, hip_pitch 100, knee 77, ankle_pitch 55, ankle_roll 17 N·m.
- Governing case: 20 kg carry while walking at 1.2 m/s, for hip_yaw, hip_roll, hip_pitch, knee and ankle_pitch peaks. Without the carry, walk 1.2 m/s alone gives peaks 40 / 96 / 203 / 154 / 203 / 26 N·m (→ needs 60 / 144 / 305 / 231 / 305 / 39). Walk 0.8 m/s gives 34 / 93 / 134 / 131 / 183 / 28.
- Impact on contracts: v3 available peak torque (36 / 167 / 167 / 238 / 284 / 163) fails the proposed need at hip_yaw, hip_roll, hip_pitch, knee and ankle_pitch. hip_yaw (57 > 36) and hip_pitch (265 > 167) fail even without margin. Actuator mass and copper loss will rise. The size is for Actuators to quantify; Legs does not choose selections.
- Impact on targets: T6 (1.2 m/s) and T5 (20 kg carry at walking speed) as written drive these numbers. If the Arbiter limits T5 to slower carry speed, the carry case must be re-run (not done; no number claimed). T2 mass risk via the actuators.
- Evidence: `modules/legs/scenarios.py`, `envelope.py`; `modules/legs/results/requirements.md`, `envelope.json`; plots in `modules/legs/plots/`. Caveats in `modules/legs/README.md` (one gait family: bent-knee ZMP, no arm swing; base-wrench residual p99 ≤ 53 N).
- Affected owner response: **Actuators: agree for the walk/stairs/push/sit cases; carry treated as stretch** (2026-10-13). Sized to need = 1.5 × max(walk 0.8–1.2, stairs, push, sit): hip_yaw 66, hip_roll 177, hip_pitch 331, knee 231, ankle_pitch 305, ankle_roll 61 N·m, with RMS 14/45/86/72/44/7 N·m for thermal. All pass with the selections in P-005. The carry-governed values (86/184/398/266/359) are not adopted until T5 is ruled. Carry torque margin on the selections is 1.22–1.67× (`modules/actuators/results/sizing.md`). Mass consequence: robot 67.6 kg > 65 kg (see P-005).
- Status: agreed (amended) → R-004 (Arbiter, 2026-10-13)

### P-002: Leg joint speed requirements from gait inverse dynamics
- Date: 2026-10-13
- Module / proposer: Legs / RL Legs
- Affected owners: Actuators
- Change (CONTRACTS §1a "need speed rad/s (at 30 % torque)", gait value = max ω while |τ| ≥ 30 % of peak, envelope): hip_pitch 4 → 8.1 (walk 1.2); knee 8 → 13.3 (stairs 18 cm); ankle_pitch 6 → 6.9 (stairs; peak ω 9.4). hip_yaw (3), hip_roll (3) and ankle_roll (4) stay unchanged: the sim gives ≤ 1.2 rad/s, but turning and side-stepping were not simulated.
- Impact on contracts: v3 available speed fails at hip_pitch (4.9 < 8.1) and knee (12.1 < 13.3). Ankle_pitch passes (10.1).
- Impact on targets: T6. Hip-pitch speed scales with walking speed (5.1 rad/s at 0.8 m/s, 6.6 at 1.0, 8.1 at 1.2).
- Evidence: as P-001.
- Affected owner response: **Actuators: agree** (2026-10-13). hip_pitch 8.1, knee 13.3, ankle_pitch 6.9 rad/s adopted. The v3 knee could not meet 13.3 rad/s even in principle: it needs 11 646 rpm, above TBM2G Nmax 8000. Meeting these speeds drives the bus change to 20S and the knee lever change to 40 mm (P-005).
- Status: agreed → R-005 (Arbiter, 2026-10-13)

### P-003: Leg range of motion: ankle dorsiflexion and hip flexion
- Date: 2026-10-13
- Module / proposer: Legs / RL Legs
- Affected owners: Legs (own geometry), Actuators (ankle screw stroke, knee/ankle linkage)
- Change (CONTRACTS §2 "Range of motion"): ankle_pitch −45…40° → at least −60…40°. The gait used −56° at 1.2 m/s and −60° on stairs, where it hit the IK limit, so the real need may be larger. hip_pitch −105…40° → at least −120…40° (sit-to-stand from a 0.46 m seat hit −120° at the IK limit). Alternative to a larger ankle stroke: a passive or active toe joint. That alternative is not evaluated.
- Impact on contracts: ankle roller-screw stroke and pin-to-pin length (§1b, `cad/stroke.py`) must be re-checked by Actuators. Hip clash check by Legs.
- Impact on targets: T6, T5 (stairs and sit-to-stand capability).
- Evidence: `modules/legs/results/<scenario>.json` → metrics.*.qmin_deg; README "Range of motion used".
- Affected owner response: **Actuators: noted, partial** (2026-10-13). Ankle stroke and the hip_pitch twin screw (new in P-005) both need a linkage geometry study with Legs. No stroke number is claimed yet (open O1 in `modules/actuators/results/DECISIONS.md`).
- Status: agreed with conditions → R-006 (Arbiter, 2026-10-13)

### P-004: Walking mechanical power and the T6 verification status (information for Arbiter / Torso)
- Date: 2026-10-13
- Module / proposer: Legs / RL Legs
- Affected owners: Arbiter, Torso (battery, placeholder)
- Change (CONTRACTS §0 walking power budget, mech line 244 W [EST, CoT 0.25]): replace with the gait-ID value. Both legs, mean positive mechanical power: 426 W at 1.2 m/s, 303 W at 1.0 m/s, 196 W at 0.8 m/s, 434 W with the 20 kg carry. Peak summed leg power is 1016 W at 1.2 m/s and 1216 W with the carry, which bears on pack peak current (open Q3). No regeneration credit is assumed.
- Impact on targets: T7 (runtime ≥ 2 h) is at risk at 1.2 m/s for this gait. Runtime must be recomputed with motor/drive efficiency (not done here). T6: forward sim on v3 actuator limits walks the full plan at 0.8 m/s (16 steps, 5.1 m), falls after 14 steps at 1.0 m/s, and after about 10 steps at 1.2 m/s, even with 2× torque limits. **1.2 m/s is not yet demonstrated.**
- Evidence: `modules/legs/fsim.py`, `modules/legs/results/fsim/*.json`, power from `results/*.npz` (README).
- Affected owner response: **Actuators: agree the gap is real; numbers below** (2026-10-13). Electrical model (`modules/actuators/size.py`) built from the gait series with the P-005 actuators, drive η 0.98 [EST], CSG η 0.75, screw η 0.85, plus 254 W for the rest of the robot. Totals at 1.2 m/s: 772 W with no regen → 1.89 h on 1620 Wh (20S5P); 576 W with shared-bus netting → 2.53 h. At 1.0 m/s: 658 / 512 W → 2.22 / 2.85 h. 2 h at 1.2 m/s with no regen credit needs 1716 Wh. Peak electrical: both legs 1.61 kW (walk 1.2), 2.64 kW (stairs), 1.99 kW (carry); per limb 2.25 kW; per joint hip_pitch 1.33, knee 1.09, ankle_pitch 0.99 kW. Proposed pack limits: 60 A continuous, 100 A for 2 s, fuse 125 A (20 A per cell at 5P vs a 45 A rating). Recommendation to the Arbiter: T7 is met at 1.0 m/s outright; at 1.2 m/s only with bus netting (evidence ×0.5 until a drive/bus sim or test).
- Status: agreed → R-002, R-007 (Arbiter, 2026-10-13)

### P-005: Leg actuator family, 20S bus, Gold Twitter drives, EtherCAT (actuator re-size to P-001/P-002)
- Date: 2026-10-13
- Module / proposer: Actuators / RL Actuators
- Affected owners: Legs (hip_pitch twin-screw geometry, knee lever 58.5 → 40 mm, mass), Torso placeholder (battery 20S5P, BMS), Brain placeholder (EtherCAT master), Arbiter (T2, T7)
- Change:
  - CONTRACTS §0 DC bus: 13S 44.2…54.6 V → 20S 68.0…84.0 V (Molicel P45B 20S5P, 100 cells, 1620 Wh).
  - §0 Drive: Everest XCR → Elmo Gold Twitter R70/100 (legs) / R50/100 (others), EtherCAT, 49.5 / 35.3 A rms continuous, 95 V max, 22.2 g.
  - §0 Field bus: TBD → EtherCAT, 1 kHz DC-synchronised, one line per limb.
  - §0 Walking power budget: 622 W → 772 W at 1.2 m/s with no regen (576 W with bus netting).
  - §1a leg rows: hip_yaw TBM2G-06008A + CSG-17-100, 70 N·m, 1.11 kg. hip_roll TBM2G-08508A + CSG-25-100, 204 N·m, 1.56 kg. hip_pitch 2 × TBM2G-07613D + 2 × RV12x4 at 50 mm, 350 N·m worst-angle, 12.2 rad/s, 2.37 kg. knee 2 × TBM2G-07613D + 2 × RV12x4 at 40 mm, 258 N·m worst-angle, 15.2 rad/s, 2.37 kg. ankle_pitch/roll 2 × TBM2G-06013D + 2 × RV12x4 at 70/40 mm, 311/177 N·m, 1.89 kg. Needs per P-001 (walk/stairs) and P-002.
  - §1d: peak electrical per joint/limb as in the P-004 response. Pack limit 60 A continuous, 100 A for 2 s.
- Impact on contracts: leg actuator mass 15.36 → 18.60 kg (+3.24, incl. 1.30 [EST] linkage). Non-leg drives −0.22 kg. Battery +0.79 kg. **Robot 63.79 → 67.60 kg, over the 65 kg limit by 2.6 kg.** Leg copper at RMS: 184 W (both legs). Envelope: twin-screw units 82 × 101 mm motor/nut housing [v3 model EST]; hip_pitch moves from a rotary at the hip to a pelvis–thigh screw pair.
- Impact on targets: T6 is enabled actuator-side (1.2 m/s envelope met with ≥ 50 % speed margin). T7: 1.89–2.53 h at 1.2 m/s, 2.22–2.85 h at 1.0 m/s. **T2 is violated (hard).** The Arbiter must choose among: margin 1.3 (−0.52 kg); CAD check of the linkage allowance (up to −1.3 kg); structure/harness allowance (v3 CAD solids 56.3 kg vs 63.8 rollup).
- Evidence: `modules/actuators/size.py`, `results/sizing.md`, `results/sizing.json`, `results/sizing_m1.3.json`, `results/DECISIONS.md` (D1–D11); `media/progress/2026-10-13_actuators_torque_speed.png`. Datasheets: Kollmorgen TBM2G manual (v3 parts.py), Harmonic Drive CSG-2A rating table (harmonicdrive.net CSG-32-50-2A-GR, CSG-40-50-2A-GR), Rollvis RV tables, Elmo Gold Twitter (elmomc.com/product/gold-twitter).
- Affected owner response:
- Status: agreed with conditions → R-001, R-008 (Arbiter, 2026-10-13)
