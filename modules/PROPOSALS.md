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
- Affected owner response:
- Status: open

### P-002: Leg joint speed requirements from gait inverse dynamics
- Date: 2026-10-13
- Module / proposer: Legs / RL Legs
- Affected owners: Actuators
- Change (CONTRACTS §1a "need speed rad/s (at 30 % torque)", gait value = max ω while |τ| ≥ 30 % of peak, envelope): hip_pitch 4 → 8.1 (walk 1.2); knee 8 → 13.3 (stairs 18 cm); ankle_pitch 6 → 6.9 (stairs; peak ω 9.4). hip_yaw (3), hip_roll (3) and ankle_roll (4) stay unchanged: the sim gives ≤ 1.2 rad/s, but turning and side-stepping were not simulated.
- Impact on contracts: v3 available speed fails at hip_pitch (4.9 < 8.1) and knee (12.1 < 13.3). Ankle_pitch passes (10.1).
- Impact on targets: T6. Hip-pitch speed scales with walking speed (5.1 rad/s at 0.8 m/s, 6.6 at 1.0, 8.1 at 1.2).
- Evidence: as P-001.
- Affected owner response:
- Status: open

### P-003: Leg range of motion: ankle dorsiflexion and hip flexion
- Date: 2026-10-13
- Module / proposer: Legs / RL Legs
- Affected owners: Legs (own geometry), Actuators (ankle screw stroke, knee/ankle linkage)
- Change (CONTRACTS §2 "Range of motion"): ankle_pitch −45…40° → at least −60…40°. The gait used −56° at 1.2 m/s and −60° on stairs, where it hit the IK limit, so the real need may be larger. hip_pitch −105…40° → at least −120…40° (sit-to-stand from a 0.46 m seat hit −120° at the IK limit). Alternative to a larger ankle stroke: a passive or active toe joint. That alternative is not evaluated.
- Impact on contracts: ankle roller-screw stroke and pin-to-pin length (§1b, `cad/stroke.py`) must be re-checked by Actuators. Hip clash check by Legs.
- Impact on targets: T6, T5 (stairs and sit-to-stand capability).
- Evidence: `modules/legs/results/<scenario>.json` → metrics.*.qmin_deg; README "Range of motion used".
- Affected owner response:
- Status: open

### P-004: Walking mechanical power and the T6 verification status (information for Arbiter / Torso)
- Date: 2026-10-13
- Module / proposer: Legs / RL Legs
- Affected owners: Arbiter, Torso (battery, placeholder)
- Change (CONTRACTS §0 walking power budget, mech line 244 W [EST, CoT 0.25]): replace with the gait-ID value. Both legs, mean positive mechanical power: 426 W at 1.2 m/s, 303 W at 1.0 m/s, 196 W at 0.8 m/s, 434 W with the 20 kg carry. Peak summed leg power is 1016 W at 1.2 m/s and 1216 W with the carry, which bears on pack peak current (open Q3). No regeneration credit is assumed.
- Impact on targets: T7 (runtime ≥ 2 h) is at risk at 1.2 m/s for this gait. Runtime must be recomputed with motor/drive efficiency (not done here). T6: forward sim on v3 actuator limits walks the full plan at 0.8 m/s (16 steps, 5.1 m), falls after 14 steps at 1.0 m/s, and after about 10 steps at 1.2 m/s, even with 2× torque limits. **1.2 m/s is not yet demonstrated.**
- Evidence: `modules/legs/fsim.py`, `modules/legs/results/fsim/*.json`, power from `results/*.npz` (README).
- Affected owner response:
- Status: open
