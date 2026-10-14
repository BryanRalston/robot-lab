# RL Arms & Hands — R1 architecture (2026-10-14)
Owner: RL Arms & Hands (shoulder → fingertips, both sides). Status: proposal-level; nothing here changes CONTRACTS.md (changes go to PROPOSALS.md).
Inputs read: CHARTER, TARGETS (T3/T4/T5/T9/T2), CONTRACTS §0/§1a/§1b/§1c/§3/R1.1/R1.4, `model/JOINT_AUDIT.md` (v4: all 26 upper-body joints PLACEHOLDER), `design/V5_POLISH_PLAN.md` rows 6–7, `sim/v3/humanoid_v3.xml`, `v3/analysis/v3.py`, `v3/analysis/results/v3_checks.md`, `arbiter/mass_rollup_official.json`.

## 0. What the sim does and does not give us
- `sim/v3` has **no arm trajectories or logged arm torques** (balance_v3 is stand/push only). "Sim loads" below are computed from the sim/v3 **arm masses, inertias and geometry** with MuJoCo (`arm_loads_r1.py` → `arm_loads_r1.json`): gravity `qfrc_bias` + Jᵀ·F for the payload at the hand-box centre (hand origin −0.10 m).
- Payload cases come from **T5**: 10 kg one-hand at full reach; 20 kg two-hand = 10 kg/hand at waist (forearm horizontal pose [EST]).
- Dynamics: per-joint inertial term at α = 20 rad/s² [EST] (4 rad/s in 0.2 s) unloaded; loaded moves assumed ≤ 5 rad/s² [EST]. Arm **speed needs have no sim source**: v3 `SPEED` values (4/4/4/6/6/6/6 rad/s) are [EST, v2] and kept.
- sim/v3 arm mass is **5.95 kg/side** (shoulderP 1.379 + upper arm 1.806 + forearm 1.951 + hand 0.817) vs the catalog allocation **9.54 kg/side** (§3). The sim arm is ~3.6 kg/side light; loads below are therefore low on self-weight by ≈ 3.6 kg × ~0.3 m ≈ 10 N·m at the shoulder [EST]. Requested: Robot Lab/Arbiter update the sim arm masses after R2 (O-A1).

## 1. Loads (left arm; right mirrors), N·m — `arm_loads_r1.json`
| case (pose, deg) | sh_pitch | sh_roll | sh_yaw | elbow | wr_roll | wr_pitch | wr_yaw |
|---|---|---|---|---|---|---|---|
| reach fwd horizontal, 10 kg (sp −90) static | **82.2** | 0.0 | 0.1 | **40.1** | 0.0 | **7.4** | 0.0 |
| same + inertia @5 rad/s² loaded [EST] | 109.9 | — | — | 47.6 | — | 7.7 | — |
| carry at waist, 10 kg/hand (sp −30, el −60) static | 61.3 | 0.0 | 0.0 | 40.1 | 0.0 | 7.4 | 0.0 |
| upper arm fwd, forearm sideways, 10 kg (sp −90, sy 90, el −90) static | 42.1 | 0.0 | **40.1** | 0.0 | 0.0 | 0.0 | 7.4 |
| side abduction 90°, 10 kg (sr 90) static | 0.1 | **76.0** | 0.0 | 0.0 | 0.0 | 0.0 | **7.4** |
| reach horizontal, no load, static + 20 rad/s² | 44.7 | 20.7 | 2.9 | 11.0 | 1.6 | 0.9 | 0.3 |
Wrist roll: gravity load ≈ 0 (payload on axis); the v2 req 4.9 N·m (need 7.4) is kept for off-axis grasps [EST].

## 2. Joint-by-joint actuator choice (need = 1.5 × max static, CONTRACTS torque rule)
| joint | max static | need (R1) | v3 contract need | selection (R1 = keep v3 catalog unless noted) | avail peak | avail/need | avail/static | speed need [EST v2] / v3 avail | max mass kg |
|---|---|---|---|---|---|---|---|---|---|
| shoulder_pitch | 82.2 | 123.4 | 148.2 | TBM2G-07608C + CSG-25-100 | 167 | 1.35 | 2.03 | 4 / 4.9 | 1.52 |
| shoulder_roll | 76.0 | 114.0 | 148.2 | TBM2G-06813C + CSG-25-100 + 300 N·m slip clutch (fall, v3) | 164 | 1.44 | 2.16 | 4 / 4.1 | 1.24 |
| shoulder_yaw | 40.1 | 60.2 | 59.2 | TBM2G-06008C + CSG-17-100 | 70 | **1.16** | 1.74 | 4 / 7.6 | 0.81 |
| elbow | 40.1 | 60.2 | 73.5 | TBM2G-05013C + CSG-20-100 | 76 | 1.26 | 1.90 | 6 / 7.6 | 0.90 |
| wrist_roll | ~0 | 7.4 (v2) | 7.4 | TBM2G-05008C + CSG-14-100 | 36 | 4.9 | — | 6 / 11.8 | 0.55 |
| wrist_pitch | 7.4 | 11.1 | 14.7 | **change proposed:** 2-screw differential pair stays, but downsized [EST] (see below) | 48 (v3 RV12x4) | 4.3 | 6.5 | 6 / 30.1 | 1.55 → ≤ 0.90 target |
| wrist_yaw | 7.4 | 11.1 | 8.9 | shared with wrist_pitch | 48 | 4.3 | 6.5 | 6 / 30.1 | 0 (shared) |
Findings:
- The sim-based needs are **at or below** the v3 contract needs for every joint except shoulder_yaw (60.2 vs 59.2, +1.7 %): keep v3 shoulder_yaw but it is the thin joint (1.16×). If the sim arm mass is raised to catalog (O-A1), shoulder_yaw/elbow needs rise ≈ +4–6 N·m [EST] → shoulder_yaw drops to ≈ 1.06×. Fallback: CSG-20-100 on shoulder_yaw (same frame as elbow, +≈0.1 kg [EST]); decided in R2 after O-A1.
- Shoulder pitch/roll: v3 sized for 148 N·m; sim says 114–123. No downsizing in R1 (fall loads enter via shoulder_pitch bearing and roll clutch per v3.py; side-fall shoulder housing FEA SF 8.9 in v3 only).
- **Wrist pair is 4.3× oversized** (RV12x4, 1.55 kg for 11 N·m). Proposal to RL Actuators: smaller screw/motor pair sized to 11.1 N·m @ 6 rad/s at 25 mm arm → 444 N per screw pair-equivalent; target ≤ 0.90 kg/side [EST, no datasheet yet]. Saving ≤ 0.65 kg/side, 1.30 kg both. Not credited until Actuators cite parts.
- Continuous/RMS: arm duty is not in any sim; v3 copper W arm rows ≤ 0.7 W walking. Carry 20 kg holding (61 N·m sh_pitch, 40 N·m elbow) for minutes is the thermal case → Actuators to check ΔT ≤ 100 K at those holding torques (O-A2).
- ROM: audit clash-free shoulder_roll −5…175 (need −15…180), elbow −115…0 (need −140…0), wrist_pitch ±40 (need ±70), wrist_yaw ±25 (need ±40). R2 geometry must recover these or the hard stops sit at clash-free limits; −140 elbow and ±70 wrist look unnecessary for T5 → proposed ROM: elbow −125…0, wrist_pitch ±60, wrist_yaw ±30 [EST].

## 3. Hand concept
**Tendon-driven, 11 actuated DoF per hand, all drives in the forearm** (v3 drive set kept: 6 flexors maxon DCX 22 S + GPX 22 HP 111:1, 5 small DCX 16 S + GPX 16 LN 103:1; spring return extension). 15 phalanx joints (3/finger) → 11 actuated: per finger 1 flexor (coupled PIP/DIP, MCP via second flexor on index + thumb), abduction/thumb rotation on the small drives.
Why tendon over direct drive: (1) T4 needs ≥ 11 DoF; 11 finger motors in the hand put ≈ 1.2 kg [EST from v3 hand_one] 0.10–0.19 m further out → +≈ 7 N·m wrist, +≈ 7 N·m elbow, +≈ 14 N·m shoulder at full reach for no capability gain; (2) finger envelope (human-size ≈ 18–20 mm) cannot hold a DCX 16 + gearhead per joint; (3) matches the V5 plan and Optimus Gen 3 direction (tendon, forearm actuators, TARGETS [S5]).
Why 11 and not 22 DoF: T4 minimum is 11; 22 DoF ≈ doubles drives, forearm volume and tendon count (wear parts, T9) with no target that needs it. 22-DoF stays a later option (V5 plan: separate Hands agent only then).
Numbers (v3_checks, unchanged): 38.2 N continuous fingertip (≥ 30 N T4 ✓), 0.74 s full close (≤ 1 s ✓), LIROS D-Pro 1 mm tendon static SF 7.1.
Gaps vs T4/T9: **no tactile sensing selected** (T4 requires fingertip tactile) — R2 picks a part; **tendon bend fatigue 1.75e6 grasps/5 y vs ≤ 5e4 published** → tendon is a wear part with a replacement interval set by test (AUDIT A1, G5 bench). Forearm packaging: 6 × Ø22 + 5 × Ø16 drives inside the sim forearm capsule (r 38 mm) is not yet shown to fit (O-A3).
Palm: machined 7075 (R-027, +0.144 both), CF backplate, silicone pads cast in machined moulds (V5 row 7).

## 4. Mass: arms + hands vs current upper-body allowance
Allowance = CONTRACTS §1a arm rows + §3 Arms + §3 Hands + R-027 palm (no separate "upper body" line exists in TARGETS; T2 66.5 kg governs the robot).
| line | allowance both sides kg | R1 estimate kg | basis |
|---|---|---|---|
| arm actuators (sp 1.52, sr 1.24, sy 0.81, el 0.90, wr 0.55, wrist pair 1.55) ×2 | 13.14 | 13.14 (11.84 if wrist pair ≤ 0.90 lands) | CONTRACTS §1a; wrist [EST] |
| arm structure | 1.60 | 1.60 | CONTRACTS §3 (v3), no new design yet |
| hands (11 drives, tendons, palm) | 4.20 | 4.20 | v3.json hands |
| palm 7075 (R-027) | 0.144 | 0.144 | rollup line 5 |
| **total** | **19.08** | **19.08 credible / 17.78 if wrist pair lands [EST]** | |
Result: **on budget (0.00 kg) at credible evidence; −1.30 kg potential** (would go to the Arbiter reserve, 1.329 kg today). No mass increase requested. Unbudgeted risk: tactile sensors + fingertip harness (≈ 0.05–0.10 kg both [EST]); arm harness is in the Actuators harness line (1.286 kg) — confirm it includes arms/hands (O-A4).

## 5. Interfaces
### RL Actuators
- I-1 Per-joint contract rows for shoulder/elbow/wrist: R1 loads above; proposal to keep v3 rows except wrist pair (downsize, ≤ 0.90 kg) and shoulder_yaw note (P-0xx to file in PROPOSALS.md after Actuators review).
- I-2 Flange drawings (PCD, pilot, bolts) for CSG-25/-20/-17/-14 frames; shoulder → torso 8 × M8 12.9 (§1c) stays.
- I-3 Holding-thermal check at carry torques (sp 61, el 40 N·m, ≥ 5 min) (O-A2).
- I-4 Hand drives (DCX 22 S / DCX 16 S) — who owns them: proposed Arms & Hands owns hand drives, Actuators owns joint actuators; drives' power/bus via Gold Twitter R50/100 or a hand-board (TBD, O-A5).
- I-5 Harness: arm + hand runs through shoulder_yaw ±150° and wrist_roll ±170° (service loop / slip-ring decision, O-A4).
### RL Legs
- I-6 Arm swing / carry loads into gait: 20 kg carry COM and arm mass per side (9.54 kg allocation vs 5.95 in sim) affect Legs' carry sims (R-014). Hand them updated arm inertials after O-A1.
- I-7 Hand-vs-leg contacts in the v4 sweep (hip_yaw, hip_roll, waist_yaw) — treat as a control/pose constraint (arm-swing envelope), not geometry; agree an exclusion zone.
### RL Arbiter
- I-8 Mass line "arms + hands" 19.08 kg allowance; R1 asks no change; credits only on cited parts.
- I-9 Rulings needed: proposed ROM reductions (elbow −125, wrist ±60/±30) vs T3/T5; tendon as wear part vs T9 (interval from test); tactile requirement part selection (T4).
- I-10 Sim arm mass correction (O-A1) for the official model.

## 6. Open questions / assumptions
- O-A1 sim/v3 arm masses 3.6 kg/side below catalog — update model? (affects loads ≈ +10 N·m shoulder [EST]).
- O-A2 Arm thermal/holding duty — no sim data; carry hold time assumed ≥ 5 min [EST].
- O-A3 Forearm fit of 11 hand drives in r 38 mm capsule — not checked.
- O-A4 Arm/hand harness inside 1.286 kg line? Slip ring vs service loop.
- O-A5 Hand drive electronics/bus.
- Speed needs are [EST, v2]; no arm motion sim exists.

R3 (P-028): carry is done in chest-carry pose sp −60°/el −110° (elbow 6.95, shoulder 43.45 N·m); see `carry_pose_r3.json`, which supersedes the R1 carry pose for thermal.

Artifacts: `arm_loads_r1.py`, `arm_loads_r1.json`, `plot_r1.py`, `R1_arm_layout_torque.png` (copy: `media/progress/2026-10-14_arms_R1_layout_torque.png`).
