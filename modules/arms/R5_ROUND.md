# RL Arms & Hands R5 (2026-10-14): palm drop, falls, tuck/pad, motor map, board fit, grip, D73/D74 length
All numbers come from repo files or from the scripts named. [EST] marks an assumption.

## 1. Palm wrist-plate drop (A42, Arms now owns the palm)
- `model/palm_7075.py` changes:
  - `DROP_MM = 12`: palm body moves down 12 mm, so the plate top is 27 mm below the pivot.
  - A 7075 neck, a 20 × 22 mm tube with 2 mm wall [EST], bridges the old lug face to the dropped plate.
  - The neck has |y| ≤ 11, inside the cheek inner face at 14 − 2 mm gap.
- CAD volume 44.34 vs 42.52 cm³ → **+0.0051 kg/hand, +0.010 both**. This is over the freeze and needs an offset (see §8).
- **Sheath clearance:** the outermost bore (x 11.7, r 1.25) clears the neck wall (x 10) by only 0.45 mm. Tight, so check it in CAD.
- **audit_v4:** run on the box and **killed after >5 min**. It rebuilds the full CAD; this is heavy. The wrist/palm clash sweep (`out/clash_v4.json`) is a separate, heavier job. **Both go to the bryan PC (Grok Interface brief, below).** Until they run, the JOINT_AUDIT wrist rows still show the old ±40/±25.
- **model_v4.py (Robot Lab) still needs updates:** fingers (zc wz−105 → wz−117), thumb z −12, and the wrist-lug box. Without them the fingers overlap the dropped palm. Ask filed; Arms did not edit model_v4.

## 2. Forward fall, shoulder_pitch (A45, D71)
- A hands-first brace puts the ground force at the hand, 0.61 m from the shoulder pitch axis (sim/v3 reach: sp −90, hand x 0.65 in the torso frame). The CSG-25-100 momentary limit of 369 N·m (parts.py) is reached at **F_hand = 369 / 0.61 ≈ 605 N**.
- A fall arrested at the hand with tens of mm of crush puts kN-level force there. A44 uses 11.5 kN on 24 mm of pad crush for the shoulder share. **The forward-fall pitch torque is ≫ 369 N·m** unless the arm is tucked.
- **Proposal: a ≤ 300 N·m slip clutch on shoulder_pitch**, like roll. The v3 roll clutch mass is folded into the 1.24 kg roll actuator line, not itemised. **Mass is not cited, so it can't be booked under the freeze.**
- Interim: Controls forward-fall mode = arms tucked (no hand brace). The load then enters through the torso/shoulder pads as bearing moment (D71), not gear torque.
- **D71 bearing recommendation:**

| option | fs at 690 N·m | fs at 716 N·m (R-039 mass) | fs at 550 N·m (A44 gate) | mass |
|---|---|---|---|---|
| CRBH 7013 A | 1.00 radial (D71) | **0.96, fails** | ≈ 1.25 [EST, linear in M] | +0.05/side |
| CRBH 8016 A | 1.72 radial (D71) | — | — | +0.41/side |

  - **Recommendation:** 7013 A, conditional on the A44 S3 strategy verifying ≤ 550 N·m (T-030, bryan PC).
  - If T-030 fails, use 8016 A, which needs Arbiter funding. The reserve is about 0.22, so 8016 would break the floor.

## 3. A44 arm tuck (Controls c6fbb85) and the 40 mm pad
- Tuck pose (sim/v3 kinematics, torso box 0.22 × 0.34 × 0.26 m centred z +0.18): shoulder_roll −5° (clash-free limit), shoulder_yaw −60°, shoulder_pitch −20°, elbow −110°.
- Forearm capsule (r 38 mm) to torso box: **8.6 mm clear**. The forearm lies across the chest with the hand at x +0.21, y −0.014, z +0.13 (torso frame).
- **Rejected tuck variants:** shoulder_yaw −90° (−38 mm, clash) and shoulder_pitch 0° (−13.6 mm, clash). Controls must use yaw ≈ −60°, pitch ≈ −20°.
- **Carry hardware:** the P-042 load (x +0.32, z +0.415) occupies the tuck volume. The fall mode must release the load first.
- **40 mm pad (R-042 approved, ID SHOULDER_PAD.md):** the lateral bulkhead face carries the shoulder_pitch housing OD 96 (model_v4: housing through the torso wall at shoulder_y − 5, output flange Ø80 × 6 at +42, roll bracket at +50).
  - A 105 × 105 pad centred 5 mm below the shoulder axis covers that housing and flange. **It only fits as a ring around the OD 96 housing** (4.5 mm margin, not viable) **or on the shoulder cap outboard of the roll housing**, at about y +0.30.
  - **Conflict, so CAD is needed.** Recommendation: mount on the shoulder-cap shell over the roll housing (it moves with shoulder pitch; abduction stays clear because the arm hangs below the cap).
  - The 10 mm extra thickness vs 30 mm affects only the lateral cap envelope. Arm-to-pad gap at roll −5° is about 32 mm [EST].

## 4. Motor-map conflict
- **Authoritative:** CONTRACTS §1a and `v3/analysis/results/v3_checks.md` — shoulder_pitch 07608C, shoulder_roll 06813C, **shoulder_yaw 06008C, elbow 05013C, wrist_roll 05008C**. Arms R1 matches.
- `actuators/THERMAL_DATA_PACK.md` is wrong: it labels "elbow/forearm 06008C" and "wrist roll 05013C", and has no shoulder_yaw row. The labels are shifted by one.
- Thermal's elbow O-A2/7675c8b used **05013C**, which is correct. Controls followed Arms R1, also correct. No result changes.
- Actuators to fix the pack: add shoulder_yaw = 06008C row; elbow = 05013C values; wrist roll = 05008C (or the D74 unit if adopted).

## 5. Hand board in the forearm (R-046/R-047): fit check
- Bore Ø66 × 177 holds tiers A + B at 163.8 mm, leaving **13.2 mm spare**.
- Electronics stack: Ø60 × 12–13 mm, with side connectors adding about 3 mm radial.
  - **Length:** 13 ≤ 13.2, only 0.2 mm margin. That depends on the 10 mm/tier spool allowance [EST].
  - **Diameter:** 60 + 2 × 3 = 66 = bore, **0 clearance, FAIL as drawn.**
- **Conditions to fit:**
  - (a) connectors axial, not radial, so the board stays ≤ Ø62
  - (b) a **centre hole ≥ Ø21** for the 11 tendon sheaths heading to the wrist (the board sits at the distal end)
  - (c) stack ≤ 12.5 mm
  - (d) all wiring stays local, so no motor leads cross joints
- **RP40s:** they stay in the shoulder bay (R-047). Only the 24 V pair crosses the elbow (+0.077 booked). Arms agrees: RP40 + filter heat stays off the forearm.
- **Heat:** the board adds 2–4 W next to the flexors. Thermal A43C shows this is acceptable only with the mandatory derate ladder (§6).
- **Superseded by §8 (length).** The 13.2 mm slot exists only if D73 does not take the forearm's distal 112 mm.

## 6. Grip: continuous force vs targets; Thermal ladder
- **R-051:** sustained grip settles at about 22 N (0.70 A step). T4 says ≥ 30 N continuous [EST target]. Under derate it is **30 N peak only (≤ 14 min from cold, A43B)**.
- **T5 20 kg two-hand carry (P-042) needs a hook grasp (handles or bottom edge), not a pinch:**
  - 98 N per hand over 4 fingers = 24.5 N per finger, applied at the middle phalanx about 35 mm from the MCP [EST].
  - Equivalent tip force: 24.5 × 35 / 65 = **13.2 N per finger ≤ 22 N, 1.67× margin.**
  - A palm squeeze (friction carry) would need N = 196 / (2μ) per hand, which is 196 N at μ 0.5 [EST]. **That is not feasible**: shoulder adduction torque, and the fingers can't supply it. So the T5 carry is specified as hook/cradle, and P-042 gets a note.
- No other TARGETS item needs continuous > 22 N at the fingertip. T4's ≥ 30 N continuous [EST] is the only one, so **T4 needs Arbiter re-wording: 30 N peak, 22 N sustained.**
- **Grip-hold fix within the freeze:**
  1. Clamp the flexor motors to the Al shell with paste. They already sit 0.5 mm from the wall; Thermal allows 0.92 A.
  2. Firmware per-motor I²t (0.84 A RMS).
  3. Measure sheath friction. At ≤ 1.2 the 30 N hold needs 0.88 A ≤ 0.92, so it is allowed.
  - **Tendon lock option:** a spool pawl per flexor. No cited part; about 5–10 g × 6 [EST]. It breaks the freeze, so it is not proposed.
- **Thermal ladder (A43C):**
  - 60/80/90 → 0.84/0.70/0.5/0 A gives **22 N sustained** (still air 80 °C shell, 10 K margin): **OK, recommended baseline.**
  - The tuned 55/70/80/88 ladder settles at 0.5 A ≈ 15 N in still air. That still passes the 13.2 N hook carry (1.15×). **OK as the still-air/4 W option only.**

## 7. Encoders and finger position sensing (Electronics question)
- **Decision: ENX 22 EASY INT on the 6 flexors.**
  - D68: 70.9 mm with the encoder vs 72.4 without, so **no length penalty**. Mass not cited.
  - Leads are local in the forearm (board in the forearm), so nothing crosses a joint.
  - Needed for tendon position control, roll-twist compensation (§A42 3.2 mm) and Controls' P-043 I²t.
- **No encoder on the 5 DCX 16 small drives** (ENX16 adds 8.5 mm each). They run on back-EMF/current estimation plus the fingertip tactile and joint-angle sensing.
- Finger joint sensing beyond that is TBD with Controls. Their repo has no explicit finger-position spec.
- The 22-conductor 1.7 m bay → forearm harness (0.45 kg) is **void** now that the board is in the forearm (R-046).

## 8. BLOCKER: forearm length with D73 + D74
- Forearm, elbow axis to wrist pivot: 270 mm (model_v4). Uses:

| item | length mm | source |
|---|---|---|
| elbow housing zone | 36 | model_v4 |
| hand-drive tiers A + B | 163.8 | §5 |
| board | 13 | §5 |
| D73 pitch/yaw units above the pivot | 112 | D73: z 56 … 140 incl. links; counted 112 per Actuators |
| wrist roll: D74 SHG-20-100-2SH (OD 90 × 42, 0.89 kg) or solid TBM2G-05008C + CSG-14 (56 × 67, 0.55) | 42–67 | D74 / CONTRACTS |

  Sum ≈ **367–392 mm vs 270: 97–122 mm over.** D74 is also **OD 90 > Ø70 forearm**, and +0.34 kg vs the 0.55 roll booking breaks the freeze.
- **Options (Actuators / ID / Arbiter decide):**
  1. Move the wrist roll to the elbow end (pronation in the forearm, the whole forearm rolls). Tendons no longer twist, so **no hollow roll is needed**: keep the solid 05008C + CSG-14 at 0.55 kg and drop D74. Length still about +97 over.
  2. Move the 5 DCX 16 small drives into the palm (5 × Ø17 = 85 ≤ 86 wide, 29 inner thickness, 61 mm length ≤ ~70 inner height [EST]). This drives abduction/thumb directly and removes those tendons from the wrist. Then pack the 6 flexors as one zero-gap ring bonded to the shell (6 × Ø22 at R 22 = ID 66; also serves the Thermal clamp). Forearm: 36 + 67 (roll at the elbow) + 81.9 + 13 + 112 = **309.9 mm, still 40 over.**
  3. Accept a 310 mm forearm (+40) or shorten D73 by 40 mm. The second needs Actuators.

  **Arms recommends 1 + 2 together.** The remaining 40 mm goes to Actuators (D73 compaction) and ID/Arbiter (forearm length vs proportions; T1).
- Mass: option 2 moves 0.265 kg distally, so wrist torque rises about 0.2 N·m (negligible). The palm will need a redesign (CAD).

## 9. Sheath part
- No Ø2.5 sheath with a cited minimum bend radius is in the repo, and none was fetched this round. Candidates (to cite): a PTFE-lined steel-coil Bowden sheath Ø2.5 or a PTFE tube 1.5/2.5.
- Need: min bend radius ≤ 35 mm (used 37.6). **Open, assigned to Materials** with Arms.

## 10. Mass and freeze
- Palm drop +0.010.
- One filter per hand (Electronics): 2 × 0.028 = 0.056 vs 0.060 booked → −0.004.
- **Net +0.006.** The offset is a small trim of the palm windows (owned by Arms, R6), or Arbiter acceptance inside the 0.02 cap.
- Pending: shoulder_pitch clutch (uncited), D71 7013 A +0.10 both, D74 +0.68 both (recommend not adopting, §8.1).

## Bryan PC brief (heavy, not run on the box)
1. `cd modules/model && python3 audit_v4.py` after a full `model_v4` rebuild with the palm DROP. Also regenerate `out/clash_v4.json` with the wrist pitch ±60 × yaw ±30 grid and the A44 tuck pose. Return JOINT_AUDIT.md + clash_v4.json.
2. T-030 (Controls A44 S3) side/forward fall batch for the D71 decision.
