# RL Legs decision log
## Round 2 (2026-10-13)
- L1. Model at final mass: all bodies scaled uniformly 63.794 → 65.00 kg (×1.0189), with masses and inertias (`gait_lib.load`, env LEGS_MASS=65). Uniform scaling slightly under-weights the legs, because the R-001 actuator growth sits in the legs. The leg actuators are +1.43 kg over v3 (sizing.json leg_act_new 16.79 vs 15.36), so the real leg/torso split puts more mass distally. Round-2 results live in `results/r2/`.
- L2. Torque limits for forward sim = CONTRACTS R1.2 available peak (70/204/350/258/311/177 N·m). The torque limits do not enter the ID.
- L3. Round-2 gait plan `walk_1p2_r2`:
  - 0.50 s steps (0.6 m), 15 % double support, pelvis 1.02 m
  - arm swing ±0.35 rad and pelvis yaw ±0.12 rad (waist counter-rotates)
  - Result: hip-yaw peak barely changed (41.8 vs 40 N·m), while hip_pitch, knee and ankle peaks rose (longer step). It is kept as an extra scenario, not as the reference gait.
- L4. Forward sim at 1.2 m/s is still not stable with time-indexed tracking. Tried, all falling at 4–6 s: VMC gains, capture-point foot placement, CoP-limited ankle torque, stronger yaw control, the r1 plan on R1.2 limits. The failure mode is an accumulating stance-foot yaw slip/roll after about 4 s of full speed. The next step needs online replanning (LIPM-MPC footsteps + whole-body QP). It is too heavy for this box/usage, so it goes to a Grok Build brief (`grokbuild/wbc_walk_1p2.md`).
- L5. Stairs ankle: with the IK ROM margin widened to 1.0 rad, the flat-swing-foot plan reaches −74° dorsiflexion, but only in SWING (stance max −36 to −42°; walking stance max −48°). Swing dorsiflexion is a plan artifact (swing foot held flat); the swing foot can pitch freely at < 90 N·m. → proposal P-006: loaded ankle ROM need −50°, not −60°; no toe joint needed.
- L6. Structure boundary for the 4.90 kg budget: thigh = upper lug + femur tube + collars + knee clevis; shank = tibia tube + collar + ankle fork; foot = foot plate (excl. instep lever). The linkages (knee tongue + twin lever, ankle instep lever + cross, hip_pitch lever + trunnions) are counted in the R-001 linkage line, not in structure.
- L7 (2026-10-13) Linkage
  - Knee lever 47.5 mm kept (sweep: ≥ 47.5 needed for speed; 42.5 best balanced). Informational only.
  - Hip_pitch packaged geometry A: clock 120°, trunnion x30 z300; gait ROM ratio 1.27.
  - Deep flexion (< −80°) is unsupported, so sit-to-stand must be re-planned (P-009).
- L8 (2026-10-13) Structure 4.84 kg both legs
  - The knee tongue is counted as structure: v3 0.447 kg minus 0.173 kg lever solids.
  - The foot cut grew from 18 % to 25 % to stay under 4.90.
  - FEA brief: grokbuild/structure_fea.md.
- L9 (2026-10-13) 65 kg forward sim on R1.2 limits
  - walk_0p8 completes the full plan (16 steps, 5.13 m, track error 2 mm).
  - walk_1p2_r2 falls at 5.45 s.
  - The 1.2 m/s work is handed to grokbuild/wbc_walk_1p2.md.
- L10 (2026-10-13) Actuators follow-up (cad_mass.py / sizing at main ca6992c)
  - (a) Knee lever 47.5 mm uses Actuators' parameters: RV12x5, F 7267 N = 345 N·m / 0.0475 m, screw speed 0.633 m/s.
    - v3-style angle-resolved factor k = min(arm(θ)/arm_nom ÷ need(θ)/need_peak) = torque_ratio_min 1.275 × need 235 / 345 = **0.87 ≥ 0.71**. Speed ratio 1.06.
    - The pure geometric arm minimum is 18.0 mm (0.38), at angles where the need is low.
  - (b) Hip_pitch lever, 137 g, Actuators' lever(): screws at y ±45, motor can ø82, nut housing ø41, pivot boss ø32. In v3 the hip yaw sits 240 mm above the pitch axis and the hip roll 125 mm above it.
    - Config A (trunnion x30 z300 above the pitch axis) **clashes**. Over −80…+40° the screw line crosses the roll-actuator band (z 79.5–170.5) at x −30…+6 mm, and the ø91 roll housing (y ±45.5) overlaps the nut housing (inner edge y 24.5) by 21 mm laterally. It also passes the ø81 yaw housing.
    - Config B (thigh-mounted mirror, same ratios 1.27) clashes with the femur tube: nut housing gap −0.5 mm, motor can −21 mm.
    - Pivot-boss clearance to the screw line is 2.7 mm (arm minimum 24.7 mm − boss 16 − RV12 rod 6).
    - Fix: config B with screw spacing dy ≥ 69 mm (femur 25 + can 41 + 3). Actuators' own lever() then weighs 0.167 kg (+0.029 kg; dy 90 for A gives 0.192 kg).
    - Crossbar root stress scales with dy: 240 × 69/45 = 368 MPa, SF ~1.37. This is a linear estimate; Actuators to re-size.
    - Mass stays in Actuators' linkage line. Legs structure 4.84 kg excludes all levers. The P-010 linkage table (0.588 kg) duplicates Actuators' line and is not additive.
  - (c) The v3 thigh has no separate hip_pitch flange part. The 8 × M6 interface is the "femur upper lug" (v3 0.265 kg, 0.212 kg after pocketing), and it stays as the pitch pivot boss and bearing seat.
    - Nothing comes off. The total stays **4.84 kg**.
    - Gap: the v3 hip pitch joint used the rotary actuator's CRBH output bearing. With the screw drive, that pitch bearing is in no mass line.
- L11 (2026-10-13, r3) 20 kg carry at 65 kg on R1.2 limits
  - **0.8 m/s:** ID peaks hip_yaw 32.7, hip_roll 110.8, hip_pitch 190.1, knee 147.4, ankle_pitch 219.8, ankle_roll 31.6 N·m. Ankle_pitch margin 311/219.8 = 1.41.
  - **1.0 m/s:** ID peaks 41.3 / 112.1 / 229.9 / 159.6 / 238.3 / 31.6 N·m. Ankle_pitch margin 311/238.3 = **1.31 ≥ 1.2**; lowest other margin hip_yaw 1.69.
  - Forward sim completes both: 16 touchdowns, final tracking error 1 mm, no torque saturation. 1.0 m/s is re-proposed in P-011.
- L12 (r3) Sit-to-stand re-planned per R-012
  - Forward lean comes from the waist (35°) with pelvis pitch 0°, so the lean adds no hip flexion. Standard 0.46 m seat, seat front 0.06 m behind the ankle.
  - Hip_pitch stays at or above −74.6° (limit −78°).
  - Peaks: hip_pitch 12.8, knee 103.5, ankle_pitch 13.4 N·m.
  - Angle-resolved minimum ratios: hip 20.6 (avail 261 at −74°), knee 2.35 (avail 240 at 116°).
  - Chair is in the scene (visual only, no contact). Thigh-to-seat gap at seat-off 0.6 mm, no robot geom penetrates the chair over the rise.
  - Inverse dynamics only, no forward sim. The rise starts at seat-off (no seat reaction modelled).
- L13 (r3) Structure check by hand methods, not FEA (box had under 0.5 GB free)
  - Clevis, tongue, lug and fork all pass, minimum SF 3.44 (fork net tension at 3 BW).
  - The r2 open-ribbed foot **fails** (SF 0.44 fall, Goodman 0.8). Switched to a closed 18 mm box section with 4 mm skins and 4 webs: SF 2.70 fall, Goodman 4.92.
  - Fork walls (4 mm) are no longer pocketed; only the top plate. Structure rises to 4.85 kg.
  - The hip pivot bore and ankle pin diameters are assumed (ø32 / ø12), so R-013 credit still needs the FEA brief.
- L14 (r3) One linkage table in modules/legs/LINKAGE_TABLE.md (Legs-owned file; Actuators reads it)
  - Counted 0.543 kg per leg, **1.086 kg both legs**, against the 0.65 target. The difference from the 0.609 contract is the hip lever at dy 69 (+0.029/leg), dropping Actuators' v3 knee-lever credit (+0.167/leg, since Legs structure excludes the lever) and the ankle lugs (+0.042/leg).
  - Open lines: rod-end bearings, hip pivot bearing (unowned), thigh trunnion clamp, and 2 possible extra trunnion pin pairs per leg (+0.104 kg both legs).
- L15 (r3) Export: exports/walk_0p8_fsim_65kg.csv/.json at 100 Hz, 9.3 s. Contains base pose, all hinge joints, leg qd, reference q and ID feed-forward torque.
- L16 (2026-10-13, r4) M2 baseline confirmed from R-015: 4.85 parametric + 0.20 clamp [EST] + 0.084 lugs = 5.134 kg both legs. Target ≤ 4.85 kg covers structure, thigh clamp and instep lugs.
  - Design reaches **4.792 kg** (margin +0.058; about +0.02 after ~0.04 kg of bolts and bumper [EST]). Files: results/r4/structure_m2.md, structure_r4.py.
  - **Foot:** closed box (3.5 mm skins, 6 mm skins under the sensor, 4 webs, hollow instep). 0.870 kg vs 1.093.
    - FEA P2 (half model, h 5): fall 6 BW at the toe gives p99.9 182 MPa (SF 2.77).
    - The peak, 322 MPa (SF 1.56), sits at the rigid sensor-ring edge and grows with refinement (singular). It needs a modelled flange.
    - Carry Goodman 4.81.
  - **Tubes:** 1.6 → 1.2 mm wall. Hand / v3-scaled SF: femur 6.56, tibia 3.84.
- L17 (r4) Femur bearing seat ø32 → ø80 H7×13 for the CRBH 5013, confirmed.
  - Ring OD 96 × 25 (|y| ≤ 12.5) plus neck: 0.226 kg (+0.014 vs the ø32 lug).
  - Hand check at 12.44 kN: net tension SF 5.39, shear-out SF 9.33, fatigue 3.28.
  - Hip hard stop at **−105°**: toggle at −114.5°, so 9.5° margin. The v3 model joint range is already −105…+40.
  - Conflict: R-012 keeps a −120° mechanical range for clash checks. That is now physically impossible, so P-014 asks for −105°.
- L18 (r4) Thigh trunnion clamp
  - A two-sided trunnion does not fit. The screw body's inner boss would sit at |y| 22–28, inside the femur (r25 at x18, trunnion x30).
  - Recommended form: a split collar on the femur plus one arm per side to y ±69, with an axial ø12 spherical eye at the body end (v3 'sphere' top).
  - FEA at 4542 N per screw: max 174 MPa (SF 2.90); walking fully reversed SF 1.76. Mass **0.237 kg/leg** vs the 0.10 [EST].
  - Needs Actuators to swap the 2 hip trunnion pin pairs per leg for the axial eye.
- L19 (r4) Ankle lugs counted once
  - The 0.042 kg/leg sits in the M2 line (this file) and in Actuators' LINKAGE_TABLE per_leg 1.263. The actuator all-in subtracts 0.084, so the rollup counts them once.
  - Anyone adding LINKAGE_TABLE both_legs (2.527) to the M2 line double-counts 0.084.
  - modules/legs/LINKAGE_TABLE.md is superseded by actuators/results/LINKAGE_TABLE.md (R-015).
- L20 (r4) Gait at 66.5 kg (the R-017 limit, worst case) on R1.2 limits; table in results/r4/requirements.md
  - **ankle_pitch need 314 > 311 avail (0.99×).** walk_1p0 peak is 209.3 N·m.
  - All other needs fit: hip_yaw 69/70, hip_pitch 338/350, knee 240/258, hip_roll 184/204.
  - Carry at 1.0 m/s: ankle 311/241.5 = 1.29 ≥ 1.2.
  - Forward sim: walk 0.8 and carry 1.0 complete (16 steps, no saturation); walk 1.0 falls at 5.1 s (not a new regression).
  - Sit-to-stand r3: hip ≥ −76°.
- L21 (2026-10-13, r5) O17: femur seat ø80 ring dropped. Tongue now has a ø35 press-fit bore for Actuators' needle straddle (D32 shaft ø35/ø30). The ø80/CRBH conflict is resolved toward the needle design.
  - Geometry: tongue OD 55 × 27 (|y| ≤ 13.5) + neck, 0.183 kg/leg (−0.043 vs the ring).
  - Hand checks at 10.06 kN + 192 N·m: net tension SF 9.0, shear-out 15.6, bearing incl. moment 9.0.
  - Press fit: 60 MPa contact (0.141 mm diametral interference); hoop 142 MPa (SF 3.55); 49 MPa left at +60 K; axial hold 21.9 kN; Goodman 2.74.
- L22 (r5) O22 thigh clamp: friction-only abandoned. Bonded collar (DP490-class, L 34 mm) plus a light 3 MPa split clamp (tube hoop 62.5 MPa).
  - Positive backup: internal 7075 sleeve (47.6/43.6 × 34, bonded) and 2 cross pins ø6 42CrMo4 through collar, tube and sleeve.
  - Bond (lap shear 31 MPa × 0.5 knock-down): SF static 9.4, one-screw fault 2.8; fatigue 7.3 (at 20 % of lap shear).
  - Backup alone (bond failed): pin shear SF 6.7, tube + sleeve bearing SF 4.41, fatigue 2.68.
  - Body FEA unchanged: SF 2.90, fatigue 1.76.
  - Eyes: maintenance-free GE 12 type (PTFE liner), mass in the Actuators line.
  - Clamp 0.295 kg/leg (+0.058 for sleeve, pins and adhesive).
- L23 (r5) Instep pin radius 70 → 73 mm. Clearance swept over pitch −60…+40° × roll ±25°.
  - Minimum gaps: rod vs tibia 8.5 mm, rod vs fork 16.3, eye vs fork 10.3, nut housing vs tibia 27.7, instep block vs fork 33.9 mm.
  - Sagittal arm minimum 31.7 mm (was 29.3 at 70). Foot mass unchanged.
- L24 (r5) M2 = 2.411 kg/leg, **4.822 kg both legs** (+0.028 vs 4.85). Including split-collar bolts + bumper (0.04 [EST]) it is 4.862, **0.012 over**.
  - Candidate trims: ø5 cross pins (−0.008), shorter collar (L 30 still gives bond SF 2.5 fault). Not taken without FEA.
- L25 (2026-10-13, r6) A7 bond spec: BOND_SPEC.md.
  - DP490 values cited from 3M datasheets [A]/[B]: 23 MPa sandblasted Al at 23 °C, 9.5 MPa at 82 °C. Fatigue and creep data are not available and are stated as not verified.
  - With 23 MPa × 0.5: one-screw fault bond SF 2.08 at 23 °C but **0.86 at 82 °C**. The pins are the retention when hot, and the bondline must stay ≤ 60 °C (G5 bench to measure).
  - Proof 13.1 kN (2.45 MPa), slip ≤ 0.01 mm, before pin drilling. Torque-seal and laser witness mark.
- L26 (r6) A6 hip stop at −105°.
  - A passive bumper cannot absorb a full-speed impact: 117.6 J at 8.11 rad/s (J = 3.575 kg·m² at 66.5 kg).
  - Required soft limit: decelerate from −86° (19.2° braking zone at 97.9 rad/s² from 350 N·m) to ≤ 1.6 rad/s at contact. Torque limit 150 N·m inside the stop zone.
  - Bumper: PU 90A Ø25 × 12 at r 80 mm (modulus [EST] 25 MPa, unverified). 4.6 J, k ≈ 1023 N/mm. Overtravel 2.15° bumper + 0.18° structure = 2.33° ≪ 9.5°.
  - Mass 0.015 kg/leg bumper + 0.016 collar bolts = 0.031/leg, **0.062 both legs vs 0.04 allowance (+0.022)**.
  - Open: an unpowered back-driven fall (screw backdrive speed unknown) needs a forward sim with the stop modelled.
- L27 (r6) A1': ø35 tongue and clamp pins/sleeve/bond added to grokbuild/structure_fea.md (items 6–7).
- L28 (r6) WBC QC failure diagnosis (box re-sim, osqp 1.1.3, LEGS_MASS=65, walk 10 s, results/r6/wbc/*):
  - Baseline reproduces: fell 5.039 s (Grok REPORT 4.915 s), qp_fail 0, CoP margin 0 mm.
  - Contact fixes, one at a time, all FAIL (fell earlier): condim 6 + torsion 0.02 → 4.505 s; elliptic cone impratio 10 → 4.320 s; foot half-width 60 mm → 4.329 s.
  - `--cruise 0.8` and `0.5` both give identical 4.317 s at 1.13 m/s mean, so the cruise arg doesn't reach the plan (bug; the 1 s cruise slice is fixed).
  - Torque saturation is 0 in the REPORT, so ankle_roll saturation is ruled out.
  - Root cause: `_plan_mpc` plays the fixed 1 s cruise slice back open-loop. `rate=1.0`, `yaw_off=0`, `foot_off[0]=0` mean there's no sagittal step, timing or yaw feedback, only a ±40 mm lateral nudge. Any error (accumulated drift, push, 20 kg carry) can only go into the CoP. The CoP saturates at the sole edge (about 20 % of frames), the foot rolls onto an edge (2 contacts), stance yaw twists to −17.6°, and the robot falls. Short double support (3.3 %) and impact bounce (7 % airborne) make it worse. This is a controller rework, owned by Grok Build: brief grokbuild/wbc_fix_r6.md.
- L29 (R-022 A14) ankle_roll ±18° hard stop. Model: `LEGS_AROLL=18` in gait_lib sets jnt_range ±18° with a stiff limit (solref 2·dt, solimp .95/.99). sim/v3 XML is not edited (not mine). Hardware: 2 × 7075 blocks 20×12×10 mm on the ankle cross at r 45 mm with 2 mm PU 95A faces [EST props]. Hold at 177 N·m is 3.93 kN, 16.4 MPa, 1.0° pad overtravel. Controller soft limit from ±16.1° (brakes 10.3 rad/s in 1.9°). Mass 0.017/leg, **0.033 both legs**, not yet in the rollup. Results: results/r7/a14.json, aroll_push.json.
  - Push at 66.054 kg. ID plan: ankle_roll q [−14, +9]°, so the stop is not hit. Peak 42.2 N·m; CoP inside the sole; friction ratio 1.13 and residual max 122.6 N are unchanged by the stop. fsim step-recover falls in both cases (pre-existing; 63.8 kg r2 run fell at 1.142 s): base falls at 1.016 s with roll peaks −35.1/+33.8° (soft ±25° range overrun). With the stop it falls at 1.048 s, roll peaks −19.9/+19.4°, stop hit from 0.408 s, overtravel 1.9°, so clearance margin 8.7 mm of the 10.9 mm.
- L30 (A14) thigh-clamp pin access. Removable front panel 60×70 mm (R8) at collar mid, 4 × M3 quarter-turn, plus a rear 40×50 exit window with 2 × M3. PA12-CF 1.5 mm, 0.018 kg/leg [EST]. Pins are pushed out to the rear with a ø5 punch L ≥ 72 mm. Pin axis and fairing clearances are layout assumptions [EST]: there is no thigh fairing CAD in the repo to check against.
- L31 (r6) WBC plan-path rework (`modules/legs/wbc/`, default contact, LEGS_MASS=65, LEGS_LIMITS=r1, LEGS_CONTACT unset). `_plan_mpc` is closed-loop: sagittal (lengthen-only) and lateral (±40 mm) DCM foot placement, playback rate around `cruise/v_plan`, `yaw_off` into stance hip yaw (±12 N·m) and swing-foot yaw. `--cruise` 0.5 and 0.8 now differ (`rate_nom` 0.4168 vs 0.6668; falls 1.278 s and 1.730 s). Pass criteria not met. Walk falls at 5.676 s, mean 1.082 m/s, 10 touchdowns, CoP margin 0 mm, double support 2.41%, airborne 9.81%, right knee saturated 3.28%. Push 60 N·s at 4.059 s, fall 4.754 s. Carry 85 kg falls at 4.686 s, mean 0.9699 m/s, both knees saturated (3.59% / 4.89%). Wider steps and a faster clock made the unpushed walk fall sooner. Report: grokbuild/results/REPORT.md.
- L31 (R-022) sim/v3: ankle_roll range ±18° with solreflimit 0.004 1 and solimplimit .95 .99 .001 (cleared by Robot Lab), commit 93cb518.
- L32 (r7) WBC r6 (c744739) QC diagnosis on the box (65 kg, r1 limits, osqp; results/r7/wbc_*):
  - Baseline reproduces: fell at 5.763 s, DS 2.6 %, flight 9.5 %.
  - The reference `walk_1p2_r2` itself plans the CoP within 5 mm of the sole edge on 26–28 % of loaded frames (heel −0.06, toe 0.18, |y| 0.05), so a 0 mm margin is planned, not a tracking error. The WBC CoP clip is also the full sole (no margin).
  - The reference has DS 25 % and zero flight, but in the realized gait the stance foot unloads 40–70 ms before the swing foot lands (contact sequence …R 0000 B L…). That flight is the bounce; the slice drops the trail load on schedule.
  - Test results, one at a time:
    - Plan CoP inset 15 mm (`LEGS_COP_INSET`, flat contacts) at 1.2: FAIL, 4.807 s. Toe-line phases still sit on the edge.
    - Speed-matched slice `walk_0p8_r7` at 0.8: FAIL, 8.773 s, flight 1.2 %.
    - Same with DS 0.25 at 0.8: **PASS 20 s**, DS 16 %, flight 0.01 %. Mean speed 0.73 m/s, under the 0.8 command.
    - PELZ 0.98 at 0.8: FAIL, 1.74 s.
    - DS 0.25 at 1.0: FAIL, 7.13 s. DS 0.35 at 1.0: FAIL, 6.95 s.
    - DS 0.25 at 1.2: FAIL, 4.784 s, flight 3.5 %.
  - Takeaway: a longer reference double support is the effective fix (it removes the flight). Above 0.8 m/s the toe-off edge CoP plus the stance unloading before touchdown still tip the foot. Contact-gated unloading (hold trail load until swing fz > 0) is the next WBC change. In parallel, RL brief grokbuild/rl_walk_brief.md (MuJoCo Playground/MJX: same MJCF, CPU replay on the box).
- L33 (r7b, approved by Robot Lab) WBC touchdown gate + margin references:
  - Gate (`WBC_GATE=1`, controller.py): while the plan is in DS and the landing foot fz < 60 N, the stance foot gets fz ≥ 0.85 mg in the QP and the clock runs at 0.3× rate_nom. After touchdown the hold ramps off over 50 ms. Timeout fallback releases after 0.2 s (initial 0.12 s / 0.5× was 10.19 s at 1.0).
  - References `results/r7/ref_m12/walk_{0p8,1p0,1p2}_r7.npz`: DS 0.25, flat CoP inset 12 mm (`LEGS_COP_INSET`), toe-rocker pivot inset 12 mm (`LEGS_TOE_MARGIN`). Plan min margin 12.0 mm, planned DS 32 %, flight 0.
  - Results, 20 s runs at 65 kg:

    | speed | fell at | DS | flight | measured CoP margin min / median | mean speed | result |
    |---|---|---|---|---|---|---|
    | 0.8 | — (20 s) | 17.8 % | 0.0 % | 0 / 18 mm | 0.733 | **PASS** survival; speed under command |
    | 1.0 | 10.19 s | 13.5 % | 0.33 % | 0 / 0.1 mm | 0.928 | FAIL |
    | 1.0, rate 0.3 + timeout 0.2 | 10.84 s | 14.5 % | 0.02 % | 0 / 5.1 mm | 0.943 | FAIL (best) |
    | 1.0, hold 0.95 + ramp 0.08 | 10.26 s | 14.4 % | 0.0 % | — | 0.958 | FAIL |
    | 1.0, + QP CoP margin 10 mm | 10.50 s | 14.0 % | 0.81 % | — | 0.930 | FAIL |
    | 1.2, best gate settings | 5.45 s | 14.8 % | 0.51 % | 0 / 0.0 mm | 1.059 | FAIL |

  - The gate removes the flight (9.5 % → ≤0.5 %) and lifts 1.0 m/s from 7.1 to 10.8 s. The measured CoP still rides the sole edge (50–66 % of loaded frames at 1.0–1.2) even with a 12 mm plan margin, so the remaining failure is CoP tracking (foot rolling onto an edge) at speed, not the plan or the bounce. Media: media/progress/2026-10-13_legs_wbc_r7_walk0p8.png.
- L34 (O13b, Actuators e582ba4) hip_pitch lever topology: **G2 (closed 5 mm cap, flat-slab arms)**.
  - Reason: our ø35/ø30 shaft (D32) is press-fit in the femur tongue (27 wide, |y| ≤ 13.5), and the 2 × TLA 3520 Z (20 wide) straddle it in the lever cheeks at |y| 13.5–33.5. The shaft is therefore 67 mm and ends at |y| 33.5. Nothing outboard supports it or passes through: the pivot load reacts tongue → shaft → needles → cheeks. Hold: the 60 MPa fit carries the axial load (L21).
  - Conditions: shaft length ≤ 66 mm, so the cap face clears the shaft end by ≥ 0.5 mm per side. The bore-corner R1.0 / 0.5×45° must suit the cup free end (check INA rs min). Service means the shaft can't be pressed out through the cap: removing the lever first, then pressing the shaft out of the tongue, is accepted.
  - G3 is not needed.
- L35 (O13b) G2 envelope |y| ≤ 38.5 accepted over hip_pitch −105…+40° (145° range, incl. the 2.33° bumper overtravel → −107.3°).
  - Rods (|y| 63–75): 24.5 mm ≥ 10. Actuators' sweep −120…+40 covers our range.
  - Cap (r ≤ 27, |y| 33.5–38.5) against our parts:
    - tongue: axial 33.5 − 13.5 = 20.0 mm. It's axisymmetric about the pivot, so the clearance is angle-independent.
    - clamp collar: collar centred 69 mm along the femur, L 34, OD ≈ 64 [EST], so its near end is at ≥ 52 mm from the pivot → radial 52 − 27 = 25 mm.
    - bumper: at r 80 → 80 − 27 = 53 mm radial.
    - femur tube (ø50, |y| ≤ 25): 33.5 − 25 = 8.5 mm axial only where the tube is within r ≤ 27 of the pivot. In our layout it isn't (the tongue neck sits there), so it's radial ≥ 25 mm as for the collar.
  - The lever is thigh-mounted, so tongue, femur, collar and bumper co-rotate with it. Those clearances don't change across −105…+40. Only the pelvis-side stop and the rods move relative to it, and those are covered above.
  - Open check (not verifiable without the v2 STEP): the G2 arm slabs reach r ≈ 61 at the ears (r 50 + ear boss). If the arms are clocked toward the femur axis, they overlap the collar radius band (52–86) at |y| 33.5+ against the collar |y| ≤ 32: 1.5 mm, below the 10 mm minimum. Require the arm clocking to be ≥ 30° off the femur axis, or verify it on `cad/hip_pitch_lever_B_v2.step`.
- L36 (r8, GB 48a9da0 structure FEA) fixes. Safety over mass, within the 0.45 kg reserve. Results in results/r8/structure_fixes_r8.json and r8/*.json (box re-solves via fea_r8.py on GB's fea_r5 loaders; the clevis h4 baseline reproduced GB's numbers exactly).
  - Clevis: +16 mm bridge pad over the cheeks + R6. Box h4 3BW+screw 549.7 → 147 MPa (SF 3.42, pulse Goodman 1.69). +0.028 kg/leg.
  - Clamp: arm depth 30 → 34, flush with the ring. Box h3 −24%, scaled rev Goodman 1.47 → ~1.95 (pending GB). +0.020/leg.
  - Femur tongue: 55 mm tangent neck + retaining compound. Box h4 press+fault 574 → 234 MPa (SF 2.15); fault-only 1.48; bore opening pending GB contact. +0.028/leg.
  - Foot: doubler collar r 30.2–45 × 3 mm. The box OOMed at h5, so hand only: SF ~2.55 at the flange edge, collar OD pending GB. +0.029/leg.
  - Tubes: bonded internal 0.5 × 100 mm doublers at mid-span. Hand SF ~1.65–1.72, pending GB. +0.042/leg (vs +0.175 for a full 1.9 mm wall).
  - Hip ring: artifact (tensile bonded bore traction) and obsolete geometry (ø80 CRBH, replaced by the ø35 tongue in L21). No change.
  - Total +0.146 kg/leg, **+0.292 kg both legs**. M2 4.822 → **5.114 kg** (5.154 incl. bolts/bumper), within the +0.45 reserve. The Arbiter should note it exceeds the old 4.85 cap. Re-check brief: grokbuild/structure_fea_r2.md. Hardware note: Actuators a64816e caps the hip bore corner at R0.6 (not R1.0), which affects the lever, not the tongue (shaft-in-tongue fit); noted for L34.
- L37 (v4 audit) Hip body vs thigh clamp: the 0.3 mm was hand-note text in audit_v4.py, not a measurement. Model v4 measures the body at ≥ 3.0 mm (femur tube 3.0, collar > 6) at stand, −60 and +40, consistent with Actuators D62. The note is corrected. The clamp arm's outer 13 mm (y 50–63) steps down from 34 to the 24 mm tine depth, so the eye-stub flange [EST] clears the root by more than its old 2.94 mm. −0.021 kg/leg. Clamp FEA re-check needed (added to structure_fea_r2).
- L38 (v4 audit, Actuators D60/D61 accepted) Ankle:
  - Top: two shank clevises at y±45, slot 11.95, PTFE washers, ø12 pins, trunnion z 410 → 450. They replace the cheeks, pins and centre plate.
  - Bottom: QA1 MGF12T 27° rod end with a 4.5 mm spacer from the ball face (y 53) to the lug, lug inner face 52.5 → 57.5, pin +5 mm.
  - Our foot is 100 mm wide, so lugs at y 57.5–72.5 sit outside it. Added an instep outrigger beam 20×145×10 on the instep tower (x 58–88, z 18–50 per fea_r5). +0.031/leg (pushback: noted, accepted).
  - Swept clear on pitch −45…+40 × roll ±18 (grid in results/r8/model_v4_legsweep.json). QA1 head-to-lug is 2.75 mm in the model (no spin); Actuators' 2.15 mm hand figure with spin governs.
  - Pitch −60 (asked) is outside the ±45/+40 range and the D60 stroke. It clashes: fork cheek × stop carrier [EST], body × clevis tine.
  - Net +0.024/leg (clevis + pins + outrigger), excluding Actuators' parts.
- L39 (v4 audit) Hip yaw/roll hard stops.
  - Yaw: tab 10×12×70 on the yoke plate at r64, pointing to the midline (to avoid the pelvis wall), via a 12×40×8 arm. It hits 2 PU 90A ø16×10 bumpers on brackets under the deck. Swept contact at −35/+45. Hold 70 N·m → 1.1 kN, 5.4 MPa. Gait-peak impact 0.07 J [EST J 0.13] ≪ bumper 1.2 J. 0.055/leg [EST].
  - Roll: lug 12×12×26 on the roll-output web at r63 hits 2 PU ø20×10 bumper blocks under the yaw yoke plate at −32/+28°. Swept contact at −12/+15. Hold 204 N·m → 3.2 kN. Impact 0.76 J [EST J 1.0] vs 4 J. 0.035/leg [EST].
  - Controller soft limits are required before both.
- L40 (v4 audit) [EST] → real Legs dimensions in model_v4:
  - knee clevis: cheeks 46×14×62 at |y| 21–35, rounded R23 about the pin below centre, rear-top trimmed 4 mm so the knee lever clears at 135°; bridge 40×70×22 + 16 mm pads (fea_r8)
  - foot: 240×100×18, steel F/T flange OD60×8, doubler collar r30.2–45×3, instep tower
  - Knee/ankle trunnion bracket plates and struts and the hip yoke brackets stay [EST]: there is no Legs design for them yet.
  - Clevis −0.024/leg; foot unchanged (FEA mass).
  - Knee: Actuators D59 twin housing placed as one part, so the standing clash is gone.
- Mass: Legs +0.100 kg/leg, **+0.200 both legs**. Plus Actuators D59–D62 +0.138 = **+0.338 vs reserve 0.375** (R-023). results/r8/model_v4_fix_mass.json.
- Audit rerun: BUILDABLE 6 / PLACEHOLDER 26 / FAIL 0. All 6 leg joints are swept clear over full range, with 0 standing clashes and 0 floating parts.
- L41 (Actuators D63, 3789f1d) Ankle top clevis tines: confirmed as built.
  - Spec: 7075-T6, 6 × 30 mm section, ø12 pin.
  - Edge distance: pin centre to the tine end is 12 mm in model_v4 (tine bottom at atz−12), which meets the ≥ 12 mm condition.
  - Tine root fillet R3 minimum to the bracket plate. This is a drawing note; the model has a sharp box joint, so the fillet is spec-only. The part name in model_v4 now carries "7075-T6 6x30 e12 rootR3 (D60/D63)".
  - Instep lugs stay outboard on the outrigger (agreed).
  - Pitch −60° is not a requirement (agreed); the range stays −45…+40.
- L42 (P-019) sim/v3 neck set to 2× XM430-W350-R, done just before the 1:41 PM ownership change (sim/WBC/RL now belongs to RL Controls, which may revert it).
  - neck_yaw/neck_pitch: armature 0.0790 → 0.0005 (PROPOSALS l.249), ctrlrange ±36 → ±4.1 N·m.
  - neckY 0.490→0.349 and head 0.647→0.461 kg (×0.7124, inertias scaled the same) to match the P-019 head+neck line of 0.810 kg (paper).
  - Static head moment ≈ 0.46·9.81·0.085 ≈ 0.38 N·m [calc], well under 4.1.
  - Handoff: modules/legs/HANDOFF_CONTROLS.md.
- L43 (v5 envelopes) Final keep-outs committed (c44da58, fa47eec). Convex hull + 5 mm over the full ranges. Re-sweep clips:
  - knee_cap: shank r ≤ 110 about the knee axis
  - hip_skirt: r ≤ 150 about the hip
  - foot_upper: no screws, z ≤ 165
  - Knee cap vs thigh keep-out: no overlap from 0 to 135°, minimum 10.2 mm at 135° (`knee_cap_vs_thigh_gap.json`).
  - Summary for ID: results/v5/ENVELOPES_FOR_ID.md.
- L44 (R-031) Hip lever section family and P-046…P-050 (R031_FIXES.md, hand checks):
  - Lever pick: 7075 b30/d0 36 with the cap notch removed, +0.09 kg robot. Fallback b35/d0 40, +0.18. Steel is not needed.
  - Femur tube material 7050-T7451 applied in model_v4. The P-047 1.6 mm walls are pending FEA.
  - T&R brief: grokbuild/r031_fatigue_fea_brief.md.
- L45 (D69 / Thermal 26412c7) Knee heat path is a clamp-on 6061 finned saddle at tibia z 320–415: no tube holes, front sector unfinned (ankle screw bodies at x ≥ 39.4).
  - The knee drives mount on the saddle. Housing to saddle needs a flexible strap across the trunnion (sized by Thermal/Actuators).
  - Tube hoop stress 35 MPa compressive, provided the conforming bore wraps ≥ 330°.
  - The lower shank stays uncovered. +0.32 kg/knee.
  - KNEE_THERMAL_NOTE.md. P-041 G10 bushes at the hip_pitch clamp eyes, +0.024 kg [EST]; not yet in model_v4.
- L46 (Materials Q) The ankle cross has no FEA and no pocketed CAD. model_v4 l.194 is a solid 30×46×30 Ti box; the 120 g booking (35 % pocketing) is unverified. It's added as a candidate to the next T&R FEA batch.
- L47 (R-031 / Actuators fbe0def) hip_pitch lever: **b30/d36 picked**, with the merged web and R8 blends. Basis: lever_l35_r031.py and lever_l35_model.py → results/r031/.
  - CAD: Actuators' G2 arms plus our full-depth web disc (r 30, |y| 33.5–38.5). The R8 blend built on both sections (4 web/arm edges); the solid is valid. STEP files: cad/hip_pitch_lever_r031_mw_b30_d36.step and _b35_d40.step. These are for checking, not release.
  - Mass per lever with the web: G2 0.405, b30/d36 0.464, b35/d40 0.527 kg. **Δ robot +0.118 (pick), +0.242 (fallback)**, which confirms Actuators' +0.123 / +0.252 to within the web. Our +0.09 hand estimate was low.
  - model_v4 sweep, hip_pitch −107.3…+40, lever swapped in (min distance to non-mate thigh parts):
    - femur tube: stock 17.6 mm, **b30/d36 11.0**, b35/d40 7.4, all at +40°. Everything is ≥ 26 mm at −107.3…0.
    - Tongue/neck: 0 mm distance with 0 overlap volume (the cheek face and tongue face are coplanar at |y| 13.5). It's identical with the stock lever: a modelled thrust face, not a clash.
    - Hip rods: 1.0 at all angles, identical to stock (the eye-region proxy). Rod sweep is from Actuators: 1.94 (pick) / 1.07 (fallback).
  - Envelope: max |y| inside r ≤ 27 is 50.2 (G2) / 54.0 / 56.4, and inside r 34 it's 54.9 / 57.7 / 59.5. So the L35 "|y| ≤ 38.5" figure covered only the cap: the arm roots already exceeded it on G2. In the assembly the pick's +3.8 mm moves nothing into contact (results above). L35 is restated as "no contact with ≥ 10 mm to the femur tube over the range". The pick meets that at 11.0 mm; the fallback (7.4) does not.
  - Fatigue amplitude is the hand estimate of about 26 MPa (allowable 58). T&R's converged FEA must confirm it.
- L48 (Thermal 9b9e169) **Tibia saddle dropped** (L45 superseded), and Actuators' femur spreader/strap is not adopted. The knee heat path is axial fins on the knee twin housing (D85 re-CAD).
  - Fin envelope: knee_fin_sweep.py → results/r031/knee_fin_envelope.json. Values: front 12 mm and rear 28 mm at the trunnion end, 37–57 mm at mid-length, none on the ±y flanks. KNEE_THERMAL_NOTE §0 has the details.
  - Mass booking: saddle removed. Knee is +0.254 kg/knee (+0.508 robot) with 0.05 fins [Thermal EST], −0.13 kg robot versus L45.
  - Industrial Design: the shin is coverable again. The no-cover zone moves to the thigh, over the housing's front and rear. The knee cap vs thigh gap is unchanged (housing ≥ 150 mm from the knee-cap keep-out).
- L47-R (R-066, lever reconciliation; corrects L47's +0.118) **Agreed delta: +0.430 kg robot (+0.215 per lever).**
  - Measured body: `actuators/cad/hip_pitch_lever_r031_mw_b30_d36_RC.step`, 2 valid solids, 155,055 mm³.
  - Mass rule (hp_lever_fea_v2): 7075 at 2.81 g/cm³, with the two ø12×25 pin stubs (5,655 mm³) taken as steel at 7.85.
  - Result: **0.4642 kg** (7075 0.4198 + pins 0.0444). Same value as Actuators and as our L47 figure.
  - Baseline: `actuators/cad/hip_pitch_lever_B_needle_sf15.step` (D33). This is the part model_v4 uses today, and the RC replaces it 1:1. By the same rule: 78,555 mm³ → **0.2492 kg**, which equals the 0.2491 in LINKAGE_TABLE.
  - Both bodies include the 2 lever halves (cheeks, arms, ears, bore relief) and the 2 integral ø12 pin stubs. Neither includes the TLA3520 needle bushes, the ø35 shaft, the GE12 eyes or the yoke bolts; those stay in their own lines.
  - L47's +0.118 used the wrong baseline. Its "0.405 G2" was our own in-memory body: the G2-as-briefed loft (Actuators lever_r031 b25/d30, 0.3318, `cad/hip_pitch_lever_r031_b25_d30.step`) plus our web disc, saved as `legs/cad/hip_pitch_lever_r031_mw_b25_d30.step`. It was never a booked or built part, so +0.118 is withdrawn.
  - Arbiter R-056's conservative +0.43 is correct, and no credit is due.
- L49 (A38 / R-053, A37 rev B) Thermal break at the clamp-eye tines (results/a38/A38_LEGS_REPLY.md).
  - Tine: e = 20 with a rounded end R15 at the ø20 sleeve bore. FEA: 185 MPa fault / 128 MPa walk, the same as today's ø12 tine; e12 with ø20 fails at 974 MPa.
  - Tines and pin unchanged in y. Flange lands are 0.85 mm high, inside ø17. Retention seats on PEI only.
  - Lever cheeks are not bolted to the collar, so no Ti limiters are needed.
  - Open for Thermal: the parallel path through rod, lever, shaft and femur is not broken.
  - Net +0.011 kg against the booked +0.017.
- L50 (Thermal D69C b785697/ceaf729) Knee fins as signed off: 12 rear fins, 25 × 1.0 mm, z 9–103 of the housing, front and sides bare.
  - Measured 0.0738 kg/knee (CAD, 6061 at 2.70): −0.035/knee and **−0.071 robot vs our 0.109 layout**. Fin area 0.061 m², at or above the 0.05 needed.
  - Clearances: fins ≥ 9.7 mm to the trunnion top plate [EST], ≥ 12.9 mm to the rods, ≥ 9.5 mm inside the v5 thigh fairing, ≥ 153 mm from the knee cap.
  - Actuators' knee_twin_housing_finned_revb.step put fins on the ±y flanks (bbox 184 → 204.8 mm, +10.4 per side, into the trunnion cheeks). That conflict is resolved by the bare sides.
- L51 (R-062) Knee drives on the femur rear: plate box 26 × 52 × 104 (drives 35 × 30 × 14.4 [MAN-G-TWI] on 6061 plate and standoffs), z 688–792, thigh frame.
  - Clearance: ≥ 6.3 mm to the hip screw body over the hip and knee ranges, with the finned housing included. Inside the fairing by ≥ 58 mm.
  - Excluded positions: lower (z 638) is 1.0 mm from the collar; z 800 hits our knee bracket strut [EST]; the front is outside the fairing by 10.9 mm; lateral hits the hip screw.
  - Wire length to the knee housing: 65 mm near / 157 mm far straight, 240 mm L-route upper bound. The housing pivot only changes this by ±1 mm.
  - Femur mount: 2 G10-lined band clamps, with low preload so hoop stress ≤ 16 MPa [EST]. No holes in the 1.6 mm wall.
- L52 (R-069) Ankle cross in 7075, pocketed (Robot Lab confirmed). FEA brief: grokbuild/ankle_cross_fea_brief.md, queued after L47-SO. Hand-model estimate −0.084 kg robot.
- L53 (R-077) Knee fins: converge on Actuators rev C (`actuators/cad/knee_twin_housing_finned_revc.step`, 6b86723). We built no further fin CAD; L50's own fin CAD is superseded as the reference.
  - **Mass:** rev C minus D59, with 6061 at 2.70 g/cm³, gives **0.0605 kg/knee**, confirming Actuators. That is −0.0485/knee and −0.097 robot vs our 0.109.
  - **Clash, fins only, knee 0–135** (knee_fins_revc_check.py):
    - trunnion bracket top plate [EST]: min 5.07 mm (at knee 0/135);
    - trunnion cheeks: 9.7 mm;
    - knee cap keep-out: ≥ 208 mm;
    - no other part within 39 mm.
    - Rev C stops at the ±92 planes, so it fits our L48 envelope with nothing on the outer flanks.
  - **v5 thigh fairing:** fins reach up to **4.7 mm beyond** the thigh keep-out hull (which is hardware + 5). The A35 grille over the housing must therefore sit at least 5 mm further out locally, or the grille opening must clear the fins by at least 5 mm. This is an ID change.
  - D69C remains the thermal baseline until Thermal and Controls pass rev C at h = 8.
- L54 (R-075, ID C2) Deleting the foot TOP shell: **accept with conditions.** Basis: model_v4 foot l.204–216, V5_COVER_SET, COVER_TRIMS_R069.
  - The top shell (PC, over the instep lugs and outrigger) carries no ground contact, impact or wear function. Those sit on the foot box sole skin (3.5 mm 7075, fea_r5) and the structure.
  - **Conditions:**
    - (1) The ankle boot hem re-anchors to the foot box through the existing M3 web inserts (keep the 4 inserts).
    - (2) The boot covers the instep rod ends and pins down to the foot top (debris and snag).
    - (3) Break edges R2 on the outrigger and lug ends that would be exposed.
  - **Existing gap, independent of C2:** no sole pad, toe bumper or heel bumper is defined or booked anywhere in the model, CONTRACTS or our requirements. The ground still contacts bare 7075. A sole pad line is needed for wear and impact whether or not C2 is taken.
- L53 update (2026-10-14): **rev C withdrawn** (Controls a5e14ff fails carry; Thermal f2da3ab keeps rev B). The rev C numbers above are superseded.
- L55 (rev B, Actuators cad/knee_twin_housing_finned_revb.step) Measured fin mass 0.0932 kg/knee (rev B minus D59, 6061 at 2.70) = −0.0158/knee, **−0.032 robot vs 0.109**.
  - Clash, fins only, knee 0–135 (knee_fins_revc_check.py REV=revb):
    - trunnion cheeks [EST] min 1.62 mm (knee 0; 1.88 at 135);
    - top plate [EST] min 2.04 mm;
    - knee cap ≥ 208 mm.
  - The overhang beyond ±92 is 4 fin pieces, 2 per side: local y 26.6–33.5 (10.4 mm out) and 37.8–42.2 (4.4 mm out), z 1–43. Alone they reach 1.84 mm to the cheeks (knee 0/135) and ≥ 11.0 mm to the top plate. **No trim is required** (≥ 1 mm). The 1.62 binding point is an in-plane fin, not an overhang.
  - We will move our EST cheeks and top plate to get ≥ 3 mm instead of trimming the fins.
  - v5 thigh fairing: fins are up to 4.7 mm outside the keep-out hull (overhang fins stay inside, −2.7). The A35 grille needs a **local bulge of 5 mm** over the housing.
- L56 (A37 rev D, Thermal bee2448) Thermal fix:
  - (1) Tine ø22 PEI, e = 22, R16 end (W32). 2D FEA at 3275 N/tine: **180 MPa fault / 125 MPa walk** (ø20 e20 W30: 185/128). The eye-stub flange clearance drops 4.0 → **2.0 mm** (the lug envelope is axisymmetric, R20 → 22).
    - Mass vs L49: 7075 tines +8.8 g robot at full-height W32 (+2.3 g if the root stays 30 wide), PEI 22/12 sleeves +5.4 g.
  - (2) Lever-end eye sleeve: the ear (ø26 × 12, single cantilever) can't take a ø20 bore. A ligament of 3 mm and e/D 0.65 fail. Needs ear OD ≥ 40 (e/D 1.0) × 16 long, grown inward (|y| 46–62) so the rod-eye position is unchanged.
    - The outer 4 mm at OD40 faces the rod start (r 15–20) at only 0.5 mm axially, so it must step to ≤ ø30 there or the washer stack gains +0.5 mm, to keep rod sweep ≥ 1.0.
    - ≈ +29 g/lever [hand], **+0.057 robot. Busts the freeze**, and it's an Actuators part, so they own it. A 14 mm pin changes the GE12 eye, which is also Actuators'.
  - (3) Knee: yes, it is an unbroken path to the femur. It runs **directly via the knee trunnion bracket strut/top plate to the femur**, and also via rod → knee lever → pin → clevis. The lever-eye fix alone would not break it.
    - Femur fin attenuation over about 160 mm to the collar is 0.19–0.28 (D69B §2). Thermal must quantify before adding +8.6 g.
- L57 (R-081) Sole pad spec: results/r081/SOLE_PAD_SPEC.md. Vibram Gumlite 6 mm 47A plus PU 60A corner bumpers, 0.093 kg/foot, **0.186 robot (computed)**, +6 mm height.
- L58 (ID 629dbed) Rear panel tabs on the drive band clamps at the 80×60 pocket corners: thigh frame (x −38 tip, y 100/160, z 700/780). Tabs 29.5 × 8 × 2 mm from the band (x −8.5) to x −38.
  - Clearance: ≥ 10.4 mm to the hip screw −y body over the hip range (knee_drive_bay_r062.py → results/r031/knee_drive_tabs_r062.json). Drive plate narrowed to y 106–154, so the tabs clear the drives by 2 mm.
  - Mass: integrated as extended clamp ears, ≈ 0.5 g each [EST] = **+0.004 robot**. Separate 6061 tabs would be +0.010.

## L59 — Sole pad (R-099 / R-102), 2026-10-14
Supersedes the R-099 "D 6 mm frame" pick. Chosen: 3 mm firm Vibram sheet (7373 TOP85 / 7663), ≥ 60A, 20 mm perimeter frame. 0.049 kg/foot, 0.098 robot (−0.088). Walk CoP margin 8.2–10.5 mm (sole_cop_r1 model). Gate: Materials Shore test ≥ 60A, else SP 67A 6 mm frame (0.098/foot). Plans need a 16 mm inset → Grok Build brief. Sim foot 18 → 21 mm.
## L60 — Trunnion cheeks / top plate moved off rev B fins, 2026-10-14
Cheeks moved 3.0 mm outward (+y/−y). The 1.5 mm trial gave only 2.33 mm. Top plate raised 1.5 mm in z. Min clearance over knee 0–135°: cheeks 3.04 mm, top plate 3.54 mm (≥ 3 ✓). Rev B fins untrimmed. Pin span +6 mm, mass ≈ +1 g/knee [EST]. knee_bracket_move_l60.py (DY=3.0, DZ=1.5).
## L61 — Trunnion thermal break, 2026-10-14
A bolted bracket break at ≥ 30 K/W is infeasible (slip and separation vs the 8.66 kN couple). Proposed: PEI trunnion-pin bushes ø9/13 × 12 + thrust washers, 43.8 K/W, +0.012 kg robot [EST] (FLAG: +3.7 g over Thermal's +8.6 g). See results/a38/TRUNNION_BREAK.md.
## L61 rev (R-106), 2026-10-14
PTFE-filled PEI bushes ø11/21×16 + 3 mm washers (15 % pads), hardened ground greased pin, boss ø26 grown outward. 14.4 MPa design, 31.9 K/W (k 0.231 cited; L61 used a wrong k of 0.12). Boss ≥ 9 mm from fins. +0.055 kg robot (FLAG, booked in full). PEEK HPV dropped (k 0.82).
## L59 note: sole Shore data (web only)
TOP85 compound = 85 ± 3 Shore A, density 1.15 (Vibram compound table: https://www.leffler.com.au/vibram-techdata/ and the Vibram 2021 aftermarket catalogue https://www.magmaonline.com.ar/wp-content/uploads/2024/05/VIBRAM-CATALOGO-2021-EN.pdf). Note: 7373 is listed only at 1.0–1.8 mm (Flli Chiesa, orthopaedie-schuhbedarf). The earlier 3 mm listing is unconfirmed. 7663 comes in 2–6 mm, "medium hardness", no Shore value published. The sole needs Materials' sample test, or a stack of two 1.5 mm 7373 layers.
## L61 final (R-106 + Materials 8fdce97), 2026-10-14
ULTEM 4001 bushes ø9/21×20 (k 0.26 SABIC TDS) + 3 mm washers with 10 % pads, ø9 HRC50 ground greased pin, boss ø26×20 grown outward. 14.0 MPa design. 33.1 K/W after the 0.2 mm wear allowance. +0.074 kg robot (FLAG, booked in full). Supersedes the ø11 R-106 rev.
## L59 Shore sources (accepted)
- 7373 TOP85, 85±3 A: Vibram US repair catalogue 2015 (Materials cite) and leffler.com.au/vibram-techdata. Sold in 3 mm: https://www.leffler.com.au/vibram-7373-tequilgemma-flint-91x58-18mm/ (Vibram AU distributor, lists 1/1.5/1.8/3/6 mm) and subaru-ec.com product_id=88. Caveat: a subaru-ec 3 mm cut-piece page (product_id=3956) lists 75A. Still ≥ 60A.
- 7663, 93 A, 1.17 g/cc: https://www.ciac-srl.com/en/articolo/508163/lastra-comp-7163-gemma (Vibram distributor page, not a lot certificate).

- 2026-10-14 L62 (R-111): thin-wall ULTEM 4001 knee trunnion bush alternate — ø12 pin, ø12/15.4×15 (1.7 wall), 14.0 MPa, 10.07 K/W worn joint, boss protrusion 9 mm, +0.030 kg robot (−0.044 vs L61, +0.026 vs pre-L61 0.004) [EST]. ø9 fallback +0.040. Adopt only if Materials qualifies bond ≥80 °C; L61 stays booked.
- L63 (R-110 backup) A38 cross pins at 29.6 kN: L22 2×ø6 through pins FAIL 1.2 tube bearing (SF 0.70; the sleeve isn't in the load path). Proposed 8×ø7 radial pins in 2 rows: bearing SF 1.63, shear 6.18, tear-out 5.35, net 1.89, fatigue 1.41 [EST, FEA owed]. Mass −0.0066 robot before retention; book 0. results/a38/CROSS_PIN_BACKUP.md.
- 2026-10-14 L63-R (Materials L63 conditions on R-115): rows moved to z 8.25/25.75 (17.5 = 2.5D) and row 2 staggered 45° (hole spacing 26.3 = 3.76D). In-row pitch 39.3 (5.6D). Tube-end e/D 2.89 [EST, tube extent from the fea_retain model, CAD unconfirmed], so 720 MPa static applies and bearing SF stays 1.63 (600 derate would give 1.36). Pins H7/m6 bonded, reamed after post-cure, Loctite 638/648. Bond 5033 mm², SF 1.49 at 82 °C / 1.37 at 95 °C [EST]. Mass 0 vs L63. If the tube is flush, no 34 mm collar layout passes fatigue (8×ø8 1.29, 10×ø7 1.21), so a tube stub or collar change would be needed. G3 3D FEA brief: grokbuild/l63_fea_brief.md.
- L64 (R-128, 2026-10-21) Job 7 limit NOT changed: R-128 308 is 7075-T651 LT A-basis/1.5 (1.001–2.0 in); ankle cross is T7351-only (393/1.5 = 262). Conflict in DRAWING_NOTES.md. Femur tube 7050-T73511 vs 262: fall bending 220.1 MPa band (235.6 hand) → SF 1.19 / 1.11 PASS; lateral dent 1.2 wall 469.3 FAIL (0.56), P-047 1.6 wall 318.4 FAIL (0.82), 2.0 wall 231.4 PASS (1.13); 262 reached at ≈1.86 mm wall [EST, linear interp]. DRAWING_NOTES.md added.
- L65 (R-130, 2026-10-21) Side dent: limit 393 (min S-basis 393, Sy/1.1 395). P-047 1.6 passes (1.23/1.20) but 1.5 mm uniform chosen (SF 1.13 femur / 1.10 tibia [EST interp]), +0.147 robot vs 1.2, −0.003 vs P-047 booking. Local step rejected (no defined impact zone, Kt). Inner sleeve OD must drop to ≤47.0. PROPOSALS L65.
- L66 (R-132 §2) Knee centre web: 7075-T7351, plate 3.501–4.0 in [EST], ST = web thickness/trunnion y [EST], sustained ST YES (bearing press + bolt preload) → 211 static / 317 fall. No web stress exists yet (JOB9-c) → margins TBD. DRAWING_NOTES + r031 brief item 7 updated.
- L67 (R-135 b8a2c69, 2026-10-21) P-152 sleeve OD 47.6 → 46.80 (BOND_SPEC §3 0.20 diametral; 46.9 rejected, 0.05 radial < 0.08); no CONTRACTS row holds the sleeve OD, new §1c row requested from Arbiter, Actuators co-sign. Knee web stock from CAD: one-piece housing 105.1 mm min → 4.25 in, exceeds 4.0 in → no permitted plate; 211 provisional / 317 fall; ST along screw axes. JOB9 b3 min-wall (1.37/1.40, SF ≥ 1.0 vs 393) request in r031_fatigue_fea_brief.md.
- L68 (R-137 §6 / R-138 dd1ef83, 2026-10-21) P-152 sleeve OD **46.80 ACCEPTED** (R-138; 0.20 diametral; fallback 46.60 with 1.6 wall tied to Job 9 b3); CONTRACTS §1c bonded femur row added, **pending Actuators co-sign**. Knee web: hand forging 7075-T7352/7050-T7452, allowable pending Materials citation, interim 211/317; split and shortening rejected.

## L69 G3 lever FAIL review (job 2, 334e848), 2026-10-21
Singular peak is the sharp upper arm/web edge at |y|=38.5 in Actuators' RC lever STEP (mesh artifact; near-field nominal ≈50 MPa design / 22.4 MPa walk amplitude [EST]). Peterson: R8 gives Kt≈1.45, Kf≈1.42 (q, a=0.635 mm), σa≈32 MPa [EST] ≤58; min R2 by hand calc. No thickening. Mass ≈+4.6 g robot (≈+9 g with lower edges) [EST]. Fits seats/bores/envelope; RV12 and femur clearance still to verify. Path: fold into L47 as candidate 0 (pending Arbiter). Details results/r031/g3_fail_review.md.
- L70 (R-144 6ff0bb4, 2026-10-21) L47-SO brief: combined run; candidate 0 (RC + R8 upper/lower arm edges, both sides) on its own converged ladder (<5 % peak AND amplitude, no singularities) is the only G3 route; every candidate and any fillet < R8 on its own ladder. Lever classed SINGLE-PATH (one lever per hip, sole member hip moment → bores; single-pin faults ≠ redundancy; STOCK_GRAIN.md r50 single). Stock undefined → STEP solid 60.0×61.5×93.0 + 3 mm [EST] = 2.5 in T651 [EST temper] → R-128 band 2.001–2.5: 294 LT design/fault (ST 271), replaces 320. 58 MPa amplitude [EST, Materials citation pending; G3 not final]. +0.009 booked.
## L71 — P-153 / D91 rev 3 knee window + P-154 guard (29.5 mm envelope), 2026-10-21
results/r031/p153_window_check.md, p153_guard_sweep.py/.json. ROM PASS: min 18.1 mm (ID placement x -34.5) / 13.3 mm (conservative x -40), knee twin housing at knee 145. ID 7.8 mm rods is conservative: model rods at y 130 ± 45 never reach the guard. Conditions: tab-to-plate 2.0 mm and tab-to-guard-wall ~1.5 mm [EST] < 3; guard inserts off the PA12 tab screw line, on ribbed bosses; guard sides 4.5 mm from the fins vs T&R's 10. Fall: shielded by the knee housing (envelope 48.6+ mm inside the thigh hull); guard sacrificial; bay stays closed via the plate. Fins yield at 256 N tip [EST]. Hip pitch / ankle plate positions: open (Actuators).

- L71 addendum (2026-10-21): knee drive plate mounting has no metal path. PEM studs thread into blind-tapped G10 standoffs; each standoff fixes to the L58 band clamp with a separate screw from the clamp side; the threads do not meet (G10 web of 3 mm or more). Fairing grille/vents per Thermal 389f91b (ID owns); they replace the P-154 guard.

## L72 — D94 drive plate placements + P-156 rev 4d vents vs CAD, 2026-10-21
results/r031/drive_plate_placement_check.md, drive_plate_sweep_l72.py/.json, p156_vent_check_l72.py/.json. Hip pitch plates (z 905) FAIL 0.0 mm into the hip pitch joint (lever hub, shaft, RV12/GE12, femur); no pelvis frame there (pelvis z 1126-1230, Torso's) → re-place on pelvis rear wall (Torso/Actuators). Ankle plates pass to knee 135 (AN1 8.7 mm fork bridge; back face tibia tube) but hit the knee housing at 140-145 → shin front [EST] or ROM limit. P-156: housing top 805.5 / front -79.4 (ID 815 / -66); L60 top plate + strut (z 816-824, x to -40/-45..5) block the chimney (0.0); hull rear x -94..-181 over the pocket (no skin at -82.5); skin-housing 2.6 mm @145 <3; hip skirt hem z 793 overlaps outlet 822-860.

## L73 — R-146 ankle dorsiflexion stop (results/r146/ankle_stop_extension.md, ankle_stop_r146.py/.json), 2026-10-21
Negative = dorsiflexion. −0.79 rad is the MJCF limit (contract mech −60/loaded −50). Kneel to pad contact at knee 145 with CoM over the toe edge needs ≈ −78° [EST]: not reachable — ankle screw toggles at ≈ −61° (arm 1.7 mm at −60°, 9.9 at −55°). Proposed limit −55° mech (−0.960 rad) / −52.5° controlled (−0.916), torque avail 44/62 N·m vs kneel 29 [EST]; screw 1465/1043 N < walk peak 1734 → allowables covered. Clearance: [EST] roll-stop carrier vs fork cheek 0.9 mm already at −45 → relieve carrier corners. PROPOSALS P-157.

## L74 — P-156 Option B (L60 top-plate cut-out) + D95 plate re-check, 2026-10-21
results/r031/p156_rev5_optionB.md/.json, l60_cutout_optB_l74.py, drive_plate_sweep_d95_l74.py/.json. Release housing (D95) x −184.1..−61.0, top **814.0 → 2.0 mm to the top plate (FLAG)**. ID 52×40 cut at x −40..−80 **FAIL**: severs the central strut (y 110-150) from the ligaments (SF 0); plain cut passes only with an 18 mm band (fatigue SF 1.45) at x ≤ −63, which is over the housing (2 mm air) → no flow. Proposed: twin 20×8 straps at y 84-104/156-176 + notch x −34.5..−61 × y 104-156 R8 (≈1320 mm²); straps SF 9.7 design / 3.2 fatigue [EST]; ≈ −0.029 kg pair [EST]; FEA + fall case + thermal-break check owed. Rev 5 side exit moot (T&R 7f12ce9). D95 plates: AN1/AN2 3.5 mm PASS incl. ankle −55 and knee 145; shin fairing 3.0 (at gate); HP1/HP2 leg parts ≥18.0 (pelvis shell 3.0 = Torso's).

## L75 — P-157 accepted; L74 twin-strap FEA brief; housing-plate gap; rev 6 skirt/shin gates, 2026-10-21
- **P-157 ACCEPTED (Robot Lab; Arbiter R-147 5deb2be):** ankle_pitch −0.960 rad mechanical / −0.916 rad controlled. The CONTRACTS row waits on Actuators' 3D CAD toggle/torque confirmation and the ankle-roll stop carrier relief.
- **L74 twin straps APPROVED conditional on FEA**; booked at **0 kg** until the FEA, fall case and thermal-break checks pass. Thermal 26cff58: notch passes at **71.1 °C standing**; minimum notch ≈ **500 mm²** for a 5 K margin. Brief: grokbuild/l74_twin_strap_fea_brief.md.
- Strap joint = L71 G10/PEM break: keyed 30×8 pad, 4 × M6 12.9 into G10 inserts + 4 separate M6 from the clamp side, 6 mm G10 web (13.8 K/W for 2 blocks, k 0.29 [EST]). Hand at the T&R fall load 29 kN (2e9b25c), couple 49.7 kN [EST, conservative scaling]: strap net SF 2.53 equal / 1.95 at 65/35, root (Kt 1.5) 1.69 / 1.30; no buckling (free 31.5 mm fixed, L/r 13.6; T&R's 120 mm pinned basis void); bolt shear 2.57, pad bearing 2.7 (455 tier e/D 2.0). **Clamp slip FAILS by friction** (needs 97 kN normal) → clamp ear on a positive shoulder of the L22 bonded collar. Knee stop location (internal stroke end?) not found → STOP_IMPACT_N from Actuators. l75_strap_checks.py/.json.
- **Housing-plate gap is NOT static:** the release twin housing pivots with the knee. True OCC gap (real fins) 2.04 @0, 7.12 @90, 2.90 @130, 2.12 @135, 1.31 @140, **0.48 mm @145**. Tolerance stack [EST] 0.72 worst / 0.33 RSS. **Fix: raise the L60 top plate + straps 4.0 mm (z 820–828)** → 4.48 nominal, 3.76 worst case at knee 145; cheeks +4 mm; ID's stack/shroud move up 4 mm. housing_plate_gap_l75.py/.json.
- **Hip skirt gate (≥ 15 mm, ID rev 6) FAILS:** outlet stack + shroud vs the v5 hip-skirt keep-out surface: 16.2 at zero pose, but **0.3–0.4 mm at hip pitch −60** (2.8 at −30) and 0.1 at roll 45. The thigh sweeps the outlet through the skirt shell in flexion → needs a skirt relief or cut-out over the outlet (ID; the +6 mm bulge is not enough). skirt_outlet_l75.py/.json (v5 keep-out; no rev 6 skirt solid in the repo).
- **Shin AN1/AN2:** plates and fairing are both shank-fixed, so the gap is static through knee/ankle ROM including −55° (the ankle moves only the foot). Gap to the v5 shin keep-out surface is 12.5 / 32.6 mm (+2 blister → 14.5 / 34.6). ID's 69.5 inner-face basis is tighter and governs: **5.0 mm** with the blister. shin_plate_l75.py/.json.

- L76 (2026-10-21): G10 allowables per Materials 6b04d2f. Fall-case pad bearing 112 MPa against 128 MPa at 71 C [EST]: margin 1.14, so pass. Sustained bearing is limited to half (64 MPa) until a G5 creep test. Thermal break: the 13.8 K/W assumed through-thickness k 0.288 (cited). In-plane k is 0.5-0.9 [EST], which would give only 4.4 K/W at k 0.9. Requirement added to the L74 strap joint: the G10 blocks are cut from plate so the strap-to-clamp heat path runs through the laminate thickness (flatwise), with no in-plane heat path shorter than 13.5 mm.

## L77 — r116b gap, raised plate, rev 6/8 skirt, P-157 3D, brief addendum, 2026-10-21 (results/r031/l77_l78_fit_checks.md)
- P-157 3D (Actuators D96): toggle −61.0° (roll 0) / −58.6° (roll ±18); kneel met at −52.5° any roll, −55° only |roll| ≤ ~12°; carrier −6 mm R3 → 4.6 mm at −55°/knee 145. Controls runtime (c3dca07): −52.5° any roll, to −54.7° only |roll| ≤ 10°. PROPOSALS P-157 text updated.
- r116b housing → plate z 816: 3.50 mm min @145 (4.92 @135); worst-case tol 2.78 @145 → keep the +4 mm raise unless RSS (3.17) is accepted; with +4: 7.5. Raised plate/straps knee+hip ROM PASS (min 7.5 housing, 8.07 hip rods). Stack 3.0 to plate, no strap hit.
- Rev 6 skirt superseded by rev 8. Rev 8: hem ↔ panel/shroud **0.1 mm** at (10,45,45) FAIL 3; cross-leg 0.0 at (−107.3,−20,−35); panel ↔ housing **1.2–1.4 FAIL**; air path open 1688–2300 mm²; lower panel inserts have no skin (33.5 mm).
- Brief addendum: K_PEAK 1.0; RV12x5 C0a 27.3 kN vs 18.9 kN (SF 1.44); no mechanical knee stop (contract 0–135 is sim); knee clearance basis 135 + crush, 145 = margin.
- Knee stop hand: 6.8 kN·m upper bound not survivable (tibia SF 0.12); T_allow 0.69 (45×1.2) / 0.85 (45×1.5) / 1.06 femur kN·m.

## L78 — knee PU stop (D97/P-159) + P-158 pad, 2026-10-21
D97 r60 1030 N·m: tibia 45×1.5 SF 0.82 FAIL; r75 fallback 830 N·m: tibia 1.02, femur 1.27, tongue 2.86, bolts 7.49, bearing 13.8 → **recommend r75** (pending Actuators energy/travel confirmation); brief T_STOP = 830 N·m. Stacks placed outboard of the cheeks clash the knee lever/rods/eyes (0.0) → Actuators to place. FLAG: 29 kN drive fall case = 1.38 kN·m → tibia SF 0.61 (governs tube walls). P-158 pad min 33.0 mm PASS.

## L79 — Robot Lab rulings; tibia 2.0 wall (R-152 CAD mass); straps at 13.1 kN; rev 8c skirt, 2026-10-21
- Rulings: knee stop = r75 fallback, 830 N·m; +4 mm plate raise KEPT (worst case, no RSS); knee ROM contract 135° + crush, top-out ≤ 143.6° (pending Arbiter) governs panel/shank gates, 145° margin; T&R L60 rev B (513a7d5) DF 1.05 → fall 13.1 kN (6.55 kN/screw); Controls cap ≤ 50 N·m within 10° of the stop → 0.92 kN·m design knee moment; **tibia wall 2.0 mm (Robot Lab, supersedes 1.7)**, femur 1.5; D98 (+0.807 kg) REJECTED (D99 ≤ 0.35 kg pending).
- **Tibia 45×2.0 (hand, 393 fall / 58 fatigue):** 0.92 kN·m SF 1.19; stop 830 SF 1.32; bottoming 1028 (978+50) SF 1.06; fatigue σa 42.2 → SF 1.37. Femur 50×1.5: 1.15 / 1.27 / 1.03 / 1.33. Doubler sleeve 0.5×100 OD 41.8 → **40.8** (ID 41.0 − 0.20 bond); P-152 46.80 is the femur sleeve, unchanged; tibia OD 45 unchanged.
- **R-152 mass from model_v4 CAD (tibia_mass_cad_l79.py):** tube ø45 × 314 (+ sleeve 0.5 × 100) per leg 0.1991 kg at 1.5 → 0.2562 kg at 2.0: **+0.0571 kg/leg, +0.1142 kg robot** vs the R-135 (1.5) booking; new femur+tibia wall booking **+0.264 robot** (R-135 +0.15 + 0.114).
- Straps at 13.1 kN (couple 22.5 kN): net SF 5.60 / 4.31 (65/35), root 3.73 / 2.87, bolts 7.38 / 5.68, pad bearing 7.78 / 5.99, G10 39.0 / 50.7 MPa vs 128 → 3.28 / 2.53; screw 8.52 kN vs C0a 27.3 → SF 3.21. Brief addendum L79.
- Rev 8b superseded by 8c before the sweep finished; rev 8c results in results/r031/skirt_r8c_sweep_l79.json (see L79b). The main r8c pelvis STL is EMPTY (84 B, 0 % fixed skirt retained), so the hem gate is run on the notched option.

## L80 — L39 hip-roll PU bumper stiffness to T&R side fall (3c73260) [all EST], 2026-10-21
PU 90A ø20×10 at r63, E 45 MPa (30–60), shape factor 0.5 → Ec ≈ 1.5E; k ≈ 2.1 kN/mm (1.4–2.8) = 8.4 kN·m/rad (5.6–11.1); linear to 25 % (2.5 mm, 2.3°) ≈ 334 N·m (222–445), ≈ 6.6 J; stiffens sharply > 30 %, rigid ≈ 40 % (4 mm, 3.6°). L39 rating 4 J. Needs a supplier curve + drop test. Hold the 2.3 mm tibia option; Robot Lab prefers the Controls swing-tuck rule. (Superseded by the cited L81 curve.)

## L81 — hip-roll bumper from the cited Freelin-Wade PUR90A curve (results/r031/hip_roll_bumper_l81.md), 2026-10-21
ø20×10: 3.66 kN / 231 N·m / 4.68 J at 25 %, 6.71 J at 30 % [EST interp]; 5.8 kN·m/rad. L39 "4 J" was uncited → replaced. Tuck case 1.33 J SF 3.5; no-tuck 10.6 J fails baseline; fallback ø24×16 8.5 J (25 %) / 12.2 J (30 %) held. Bottomed path 7.4 kN/mm = 29.4 kN·m/rad (fallback 18.1). R roll mirrored −15/+12. 1.70 m/s landing: ×1.214 (impulse) / ×1.474 (energy) on the proof case → ankle screws SF 1.72 / 1.41 vs C0a; cross/DU/sole need proof SF ≥ 1.22/1.48 from the Job 7 FEA.

## L83 — T&R 8c7ac56 items: tube local buckling at 1079 N·m; ankle-roll stop radius; M4 grade, 2026-10-21
- **Buckling (hand, tube_buckling_l83.py):** tibia 45×2.0 (D/t 22.5): σ 388 MPa → yield SF **1.01**; elastic local buckling σcr 3527 (SP-8007 knockdown) SF 9.1; Brazier 6.45 kN·m SF 6.0; noncompact (λp 12.8 < 22.5 < λr 56.6), inelastic Mn 1.28 kN·m → SF 1.19 [EST, AISC F8 analogue]. Femur 50×1.5 (D/t 33.3): σ 401 → yield SF **0.98 (FAIL, marginal)**; σcr 2272 SF 5.7; Brazier 4.09 SF 3.8; Mn 1.18 → SF 1.09. Buckling does not govern; femur yield at bottoming does — flag to Robot Lab (femur 1.6 wall → SF ≈ 1.04 [EST], or Controls/stop energy cap). FEA brief grokbuild/l83_tube_buckling_fea_brief.md (eigen + nonlinear with F1 bow imperfection).
- **Ankle-roll stop radius: r 45 mm** (contact face). Source: results/r7/a14.json (A14: "contact face at r 45 mm", hold 3933 N, 2 mm PU 95A pad) and model_v4 l.201 ("face r45"); L29 r 45. CONTRACTS R-022 gives the ±18° angle and the 10.9 mm pin-to-pin margin but no radius.
- **M4 (INSPECTION F6 "ankle roll stop blocks + M4"; BOM F5, M4×10, 1 per block + dowel):** specify **ISO 4762 M4×10 12.9, zinc-flake coated, Loctite 243, into a helicoil in the 7075 cross; ø4 h6 hardened dowel carries the shear.** Reason: 3933 N hold (5.9 kN at ×1.5 dynamic [EST]) per block; dowel shear capacity ≈ 7.5 kN [EST] → SF 1.9 / 1.28; if the dowel is lost, M4 12.9 shear (As 8.78, 0.6 × 1220) 6.4 kN → SF 1.63 / 1.09, whereas A4-80 gives 4.2 kN → SF 1.07 / 0.71 (FAIL dynamic). The other M4s (BOM F3 knee saddle, 8.8) are not in F1/F6.

## L84 (2026-10-21) D99 r75 PU knee stop, Legs side [EST; D99 STEP cad/knee_stop_pu_r75_d99.step not in the repo, so the geometry is a Legs envelope]
Numbered L84 because L83 already holds the tube local-buckling item. Scripts: knee_stop_d99_l84.py (sweep), knee_stop_d99_struct_l84.py (hand checks); results/r031/knee_stop_d99_*.json.
- Design: 2 striker lugs machined on the knee tongue-neck block (solid 7075, so no tibia bond slip), 10 x 18 x 31.5 mm, R5 root, behind the tibia at y 98-108/152-162, face at r~75. Seats are 20 x 8 x 28 compression struts integral with the existing ø64 thigh split collar (z 603 to 575). They add no new metal path to the femur bond: the collar is already on the femur, and the seats don't connect to the drive plate or L58 clamps.
- Contact: first touch between 125° (4.2 mm) and 130° (0.0) ✓.
- SF per side (3.65 kN design / 5.25 kN bottoming): striker root 1.55/1.62 net, 1.11/1.15 with Kt 1.4. Shear 20/29 MPa. Seat 7.2/7.5. ø64 collar DP490 bond at 2.85 MPa (82 °C) 2.09/1.45, 2× ø6 pins 4.65/3.23. Bearing at the PU face is not critical. Fatigue: root 237 MPa > 58, so this is OK only as a rare-event part (≤1e4 contacts). Needs 7075 S-N data if the kneel loads the stop every time.
- Tubes at 839 N·m bottoming: tibia 45x2.0 SF 1.30, femur 50x1.5 SF 1.26 ✓ (easier than 1079).
- Mass: lugs 31.9 g, seats 25.2 g, −4 g neck pocket, so +53 g per knee, +0.106 kg per robot (envelope volumes, not D99 CAD). D99 line 0.344 + 0.106 = 0.45 kg > 0.35 cap. **Breaks the cap.** Our share would have to be ≤6 g per robot, which no machined striker/seat can meet. Robot Lab needs to raise the cap to ~0.45 or find the saving elsewhere (Actuators pad/bracket).
- Sweep, 3 mm gate, knee 0-145 + hip -105/+40 + mirrored yaw ±35/45 + roll -12: **FAIL**. Striker to clevis bridge pad 0.0 at 140° (inside the bottoming travel to 143.6). Striker to knee lever 0.5 at 0°. Seat to ø64 collar 2.1 (integral by design, ignore). Striker to femur 2.3 at 145°. Moving the lugs outboard (y 84-94/166-176) hit the GE12 rod-end eyes (0.0), so that was rejected. Fix needed: notch the clevis-bridge pad rear corner ≥4 mm and trim the lever-side lug corner (or put contact at r~65). Needs the real D99 STEP to close.

### L84 rev 2 (supersedes the L84 envelope above), D99 STEP 63f9a24 + Actuators placement, knee_stop_d99_r2_l84.py → results/r031/knee_stop_d99_r2_l84.json
- **Chosen option:** the Actuators D99 placement (stacks outboard of the knee screws at y 46/214, contact 130°, t0 −20). The inboard L84 lugs, the bridge-pad notch, the lug trim and r65 contact are all dropped. The outboard placement avoids the clevis-bridge clash completely and needs no notch, so it is the lightest passing option.
- **Moving-part sweep:** Actuators' knee_stop_sweep_d99 (r116b, knee 0–145, ankle/hip poses, mirrored yaw). Min 10.3 mm pad to ankle screw; strikers ≥ 6.4; pad to striker 2.3 mm at 128° (approach to the 130° contact). PASS.
- **Same-segment pairs:** these were skipped in Actuators' sweep and are added here. Seat/bar to clamp arms 6.2. Striker to ankle screws 5.1 and ankle strut 6.7 (with the deepened arm). Bar lands on the ø64 collar/femur (0.0, the intended tie). PASS ≥ 3.
- **Moving-part margin not re-run:** the striker arms are now 6 mm deeper (t0−22), on the side away from the pad face. The moving-part margin for that growth comes from 6.4 [EST] and was not re-swept.
- **Striker arm:** cantilever from the tibia collar to the stack, 63 mm at 3.65/5.25 kN per side. As drawn (24×12) the root is 399 MPa: **FAIL**. Deepened to 24×18 (Z 1296): design 177 MPa, SF 1.48 net / 1.05 with Kt 1.4; bottoming 255 MPa, SF 1.54 / 1.10. Lug face bearing on the PU is not critical.
- **Tibia knee-end collar:** ring ø51×3 wall × 24 long, bonded and pinned with 2× ø6. A bond alone (3393 mm², 2.85 MPa) gives SF 1.33 design and **0.92 bottoming**, so the pins carry the load: SF 4.65 / 3.23. The ø64 thigh collar tie is SF 2.09 / 1.45 bond and 4.65 / 3.23 pins. No new metal path to the femur bond: the ø64 collar already sits on the femur, and the bar does not touch the drive plate or the L58 clamps (6.2 mm).
- **Fatigue:** rare-event stop. Controls kneel_pose knee 1.9 rad = 108.9° (kneel_w1 1.7 = 97.4°) is below the 130° contact (21° margin), so normal kneeling does not load the stop. Caveat: the R-146 heel-lift kneel at knee ~145° used for the skirt/floor gates would load the stop. Controls must keep any kneel ≤ ~125°, or the stop sees cycles; then the 58 MPa amplitude fails (root 248 MPa at Kt).
- **Legs collar growth (CAD/hand) per knee:** ring 28.7 g + arm deepening 38 g + ø64 tie boss 5 g [EST] = **72 g/knee, 0.143 kg robot**. D99 line 0.344 + 0.143 = **0.487 kg > 0.35: BREAKS THE CAP.** This is already the minimum: the arm depth is strength-bound and the ring is bond/pin-bound. Robot Lab has to choose: raise the cap to ~0.49, lower the fault energy (92.5→80 J saves ~10 g/knee of PU), or accept a lower SF on the arms.
- **Tubes at 839 N·m:** tibia 45×2.0 SF 1.30, femur 50×1.5 SF 1.26.

## L85 — Robot Lab rulings on D99/femur/skirt; D99 deepened-arm moving-part re-sweep, 2026-10-21
- Rulings: D99 cap raised to **0.49 kg** robot; 92.5 J kept; the 24×18 striker arm and the pinned tibia ring are APPROVED, so the D99 line is 0.487 kg ≤ 0.49 PASS. Femur stays **50×1.5**: bottoming is a motors-off fault, and T&R accepts slight set with F1 replacement (the L83 yield SF 0.98 is accepted). Skirt 8c is superseded (8f, 8g from ID pending) and the empty pelvis STL was removed in 8d, so the 8c sweep was killed (PID 1624404) and the 8c partial results are void.
- Re-sweep (knee_stop_d99_arm18_sweep_l85.py; Actuators' sweep with the arm t0−22..t0−4, i.e. 18 deep; t0 −20; r116b; knee 0–145 + ankle/hip poses + mirrored yaw L45/R−45, L−35/R35, ±both) → results/r031/knee_stop_d99_arm18_sweep_l85.json:
  **min 10.3 mm**, pad to ankle screw body at knee 145° / ankle pitch −45°; strikers **12.0 mm** to the R ankle trunnion top plate (yaw 45/45, knee 90°); rod-end eyes 21.1 (yaw L45/R−45, knee 130°). Pad to own striker 2.3 mm at 128° (approach to 130° contact, not gated). **PASS ≥ 3 mm.**

## L86 — T&R (via Robot Lab): standing-tuck landing case; M4 helicoil, cross temper, M4 torque, 2026-10-21
- **Job 7 brief (grokbuild/ankle_cross_fea_brief.md):** added a 2.7 kN standing-tuck landing case next to the 3,914 N case (cross, DU bushes, sole; same SF targets). Hand check: DU 9.4 MPa → SF 26; bush-OD bearing 8.0 MPa vs 295 → SF 37; 0.69 × the 3,914 N case, so it does not govern. Sole is left to the FEA.
- **Helicoil (M4 12.9 into the 7075-T7351 cross): free-running STI insert, length 1.5D = 6.0 mm** (e.g. Helicoil 1185-04CN-0060 / 3585-04CN-0060 [EST part no.]). Stripping calc (VDI 2230 approach): bolt breaking load As 8.78 × Rm 1220 = 10.7 kN. Parent shear area per mm ≈ π × 5.2 (insert OD, M4 STI major) × 0.75 = 12.25 mm²/mm. τ 7075-T7351 ≈ 0.6 × Ftu 476 (MIL-HDBK-5H A-basis plate) = 286 MPa, so the minimum L to match the bolt is 3.05 mm (0.76D). At 6.0 mm the parent strips at 21.0 kN = **1.96 × bolt UTS**, so the bolt breaks first. Insert-to-bolt stripping is not critical (steel insert, 6 mm engagement ≈ 1.5D, ISO 898-1 nut-equivalent). 2D (8 mm) is not needed and doesn't fit the M4×10 grip [EST].
- **Cross temper: 7075-T7351 plate** (MIL-HDBK-5H p.3-348; Materials 95436bf / a2bf811 ANKLE_CROSS_7075.md §1). The overaged T73 temper gives SCC resistance in short-transverse under the sustained press-fit hoop stress at the DU bores and the helicoil inserts; T6/T651 is prohibited (high SCC susceptibility, ST threshold ≈ 7 ksi vs ≈ 42 ksi for T73, MIL-HDBK-5H Table 3.7.1.0(a) [EST cite]). The ~10–15 % strength penalty is already in the 393/262/239 allowables.
- **M4 12.9 zinc-flake + Loctite 243 torque: 4.0 N·m** (±10 %), using **μ_total ≈ 0.12** (μG ≈ μK 0.12 for zinc-flake per ISO 10683/VDI 2230 table A5 class B; Loctite 243 uncured acts as a lubricant, K ≈ 0.15–0.17 per the Henkel TDS [EST]). Preload F = T/(K·d) = 4.0/(0.16 × 4) = **6.25 kN = 73 % of proof load** (ISO 898-1 M4 12.9 proof: 8.78 × 970 = 8.52 kN), within the 65–75 % target. Under-head bearing on the 7075 (head ø7 / hole ø4.5, 22.6 mm²) is 277 MPa < 7075-T7351 limiting surface pressure ~ 400 MPa (VDI 2230 table A9 [EST]), so no washer is needed; a hardened washer is optional. Range at μ 0.10–0.14: 5.4–7.4 kN (63–87 % proof): the upper end is high but below yield at 12.9.

## L87 — Hip yaw narrowed (Controls 2b92408); r7 gaits superseded, 2026-10-21
- **Hip yaw:** Controls' clash rerun (2b92408) shows the r116b knee housings collide at 45°. The new range is **left −35..+40°, right −40..+35° (mirrored)**, replacing the L39 45° end. Sweeps that used yaw ±45 (L84/L85 D99, L79 skirt) are conservative against the new range.
- **r7 reference gaits:** these exceeded the −0.916 rad (P-157 controlled) ankle bound. They are **superseded by Controls' regenerated gaits**. Anything derived from the r7 gaits (e.g. the Job 7 walking loads) must be re-derived from the regenerated set.

## L89 — D99 r75b (Actuators 8978a05/13eb4b0): flush arm, CAD mass reconciliation, tapered arm, 2026-10-21
- **Flush 24×18 arm accepted** (t0−18..t0); the Legs 6 mm extension is dropped. Re-sweep (knee_stop_d99_flush_sweep_l89.py → results/r031/knee_stop_d99_arm18flush_sweep_l89.json): **striker arm ↔ ankle screw body 4.5 mm at knee 145° / ankle −45° (PASS ≥ 3)**; pad ↔ ankle screw 10.3; rod-end eyes 21.4.
- **Correction to L85:** the L85 "t0−22" sweep did not apply the deeper arm (the sed pattern no longer matched Actuators' source), so its 12.0 mm striker figure was for the 12 mm arm. Actuators found 0.5 mm (FAIL) for t0−22; L85 is superseded by this entry.
- **CAD mass (d99_r75b_mass_taper_l89.py, OCC volume × density; STEP solid 0 81.03 cm³ = one stack side, solid 1 14.7 cm³ = ring + pins):** per side PU 36.3 g, shims/end plates 17.3, seat 24.3, lug 19.8, **arm 76.5**; ring 37.5 + 2× ø6 pins 10.7. **Per knee 395.5 g + collar bar 40 g [EST] = 435.5 g → 0.871 kg robot.** The arms alone are **0.306 kg robot** (confirms Actuators' ≈ 0.30).
- **Why 0.344 was wrong:** it came from Actuators' text estimate (0.484 − 2×70 g), which booked strikers + arms at 75 g/knee for the 24×12 arm with no ring. The CAD has 2× (lug 19.8 + arm 76.5) = 193 g/knee of strikers plus the 48 g ring. Actuators' script figure (0.682 kg) matches their analytic formula (it omits the ring and pins, about 0.096 kg robot, and uses seats 30×26×6). **The CAD number, 0.87 kg robot (0.79 without the EST bar), is the right one.** The D99 line is **far over the 0.49 cap**.
- **Tapered 7075-T7351 arm (hand beam):** tangential depth h = 18·√(x/63) from the tip, floor 9 mm (tip shear and lug), 24 mm radial, root 18 kept over the R5 fillet. Volume ×0.708 → **−0.089 kg robot** (inside the −0.08…−0.10 target). Bending stress is constant at the root value from x ≈ 15.8 mm to the root, and lower in the 9 mm tip zone.
  - Design 3.65 kN: 177 MPa, SF 1.48 net / 1.05 Kt.
  - Bottoming 5.25 kN: 255 MPa, 1.54 / 1.10.
  - T_STOP 830 N·m (5.53 kN/side): 269 MPa, 1.46 / 1.04.
  - Tip shear ≤ 38 MPa.
  - 92.5 J goes into the PU, with arm compliance not credited.
  - Fatigue: rare-event only (root 248 MPa at Kt > 58), since Controls' kneel at 108.9° is below the 130° contact.
  - An I-section pocket was not taken: the gates are at SF ≈ 1.04 with Kt, so the taper is the limit without FEA. A Grok Build FEA (Kt along the taper) is needed to confirm the 1.04, or to allow pocketing.
- **After the taper the robot total is ≈ 0.78 kg (CAD + EST bar), still over 0.49.** This goes to Robot Lab and Actuators.

## L88 — Torso 9700df9 pelvis reinforcement + battery vent vs legs, 2026-10-21 (pelvis_reinf_vent_l88.py → results/r031/pelvis_reinf_vent_l88.json)
- Reinforcement as modelled: 20×8 top lip inside the walls; 8 mm ribs at y ±(57…65) from the deck top (z 1206.6) to the pelvis top (1230); ring r55–66 at the waist-yaw seat. Swept against the hip-yaw drives/housings, L39/L80 yaw and roll bumpers/tabs and HP1/HP2 over hip yaw ±45 (covers L −35..+40 / R −40..+35, mirrored) × pitch −105/0/+40 × roll −14.5/0/+17.5, plus waist (yaw ±45, pitch −20/+30/+40).
- **Minimum 15.2 mm: +y rib ↔ L hip-yaw stop tab (L39), every pose (pelvis-fixed rib vs yaw-output tab; worst at yaw 0). PASS ≥ 3.** All leg-side parts sit below the 8 mm deck (z ≤ 1206.6).
- **Vent (x −107, z ≈ 1390, rearward; downstream box x −157..−107, |y| ≤ 50, z 1340–1440 [EST]): CLEAR of every leg part, cable and bumper.** Leg-side hardware sits ≥ 130 mm below the plume. The nearest objects are arm parts at waist yaw −45 / pitch −20: R shoulder-pitch flange 84 mm, roll bracket 90 mm. Those are outside the 50 mm flag and are Torso/Arms' call.

## L90 — ID 8g skirt (d8fb6f9/d7c9b0d), Robot Lab option (1): L↔R closure with narrowed yaw + hip adduction/yaw stop, 2026-10-21
- Built geometry (ID r8g panel inboard edge y ≥ 86 + rigid shroud; ID's lr2 method). Both legs adducted, mirrored, pitch −107.5..+42.5 × roll −15.6..+18.6 (incl. overtravel) × yaw −38.6..+43.6 (narrowed −35..+40 plus 3.6° bumper overtravel). Scripts: skirt_r8g_lr_l90.py, skirt_r8g_stop_l90.py → results/r031/skirt_r8g_lr_l90.json, skirt_r8g_stop_map_l90.json.
- **Still FAILS: L↔R panel 0.0 mm at (pitch 0, roll −12, yaw +40) both legs; shroud 0.0 at (30, −15.6, 43.6).** Yaw alone closes it: roll 0 / yaw +40 gives 0.2 mm, and yaw −38.6 gives 10.9. The narrowed yaw does not fix it.
- Gap map (min over pitch, mirrored pair, mm): roll 0: yaw −20 → +30 OK (+30: 31.9), +40: 0.2. Roll −3/−6: −20..+20 OK (+30: 20.0/7.2). Roll −9: ±20 at 28.4/28.5 (marginal). Roll −12: 0..+10 OK (−20: 10.6, +20: 10.5). Roll −15.6: none (yaw 0: 26.6).
- **Stop needed (sized [EST]):** each hip gets a combined yaw/adduction stop. It is an **angled PU 90A wedge bumper ø16×10 (L39 yaw-bumper size) on a ramp bracket under the deck, struck by the L39 yaw tab**. The ramp sets yaw contact as a function of hip roll:
  - Yaw stop (crushed end): **+28° / −18° at roll ≥ −3°**, closing linearly to **+10° / −5° at roll −12°**. The roll adduction stop moves from −12 to **−10° contact (−12.3° crushed)**. The crushed limit keeps the mirrored gap ≥ 30 mm on the map (worst point ≈ 31 mm at roll 0 / yaw +28 [interp.]).
  - **This cuts the Controls yaw contract (L −35..+40) to about −18..+28 for each leg, so Robot Lab / Controls must rule.** The alternative is ID's crushable shroud/panel zone.
  - **Force/torque curve for T&R** (ø16×10 PU90A, Freelin-Wade curve L81 scaled by area 0.64, at r64 tab): 10 % (1 mm, 0.9°): 0.60 kN / 38 N·m; 20 % (2 mm, 1.8°): 1.6 kN / 102 N·m; 25 % (2.5 mm, 2.24°): 2.34 kN / 150 N·m (≈ 3.0 J); 30 % (3 mm, 2.7°): 3.3 kN / 211 N·m (≈ 4.3 J); rigid by ~40 % (3.6°) [EST interpolation]. Ramp normal load ≈ force / cos(ramp 25°) on the bracket.
  - **Mass [EST]:** ramp bracket 7075 ≈ 18 g + PU wedge 3 g + 2× M4 2 g ≈ 23 g/hip, **+0.046 kg robot**.

## L91 — Robot Lab rulings: D99 reopened; 8g bumper on hold; integrated knee stop concept, 2026-10-21
- **D99:** the cap stays at **0.49 kg**, so the concept is reopened with Actuators. **The L89 taper is NOT PURSUED** (no taper FEA on the old concept).
- **8g angled bumper (L90): ON HOLD** pending Controls' yaw decision; otherwise ID opens the panels. The +0.046 kg booking is noted.
- **Concept study, results/r031/knee_stop_integrated_l91.md [EST]:** PU 62 cm³/knee is energy-bound (92.5 J at 25 %); torque ≈ 760 N·m ≤ 830 for any arm.
  - **A:** twin stacks in r116b lower-rear housing bosses at r60, striking pads on the tongue-neck block. 13.8 kN; boss SF 3.97 / 5.9. **0.36 kg robot.**
  - **B:** single 36×36×48 stack in a housing underside pocket (9 mm floor) at r50, striking the tongue-neck top. 16.6 kN; floor SF 1.31 / 1.96. **0.26 kg robot.** Needs a central sweep.
  - Both pass ≤ 0.49. B is recommended, with A as fallback. The housing changes for Actuators are listed in the study.
- **L91 addendum (Robot Lab, with Controls accepting): the L90 hip stop is FINAL. The 8g hold is CLEARED.** The angled PU 90A ø16×10 on a ramp bracket, struck by the L39 yaw tab, is booked at **+0.046 kg robot**. The coupled yaw/roll limit **replaces the hip yaw −35..+40 / −40..+35 (L87)**:
  - **Left leg:** yaw **−18..+28° for roll ≥ −3°**, linear to **−5..+10° at roll −12°**. Roll adduction contact at **−10°**, **−12.3° at full crush**.
  - **Right leg:** mirrored (yaw −28..+18 → −10..+5; roll contact +10°, +12.3° crushed).
  - The torque curve for T&R is as in L90.

## L92 — Final coupled hip yaw/roll limit (Controls clash check 1b44344), 2026-10-21
- **The L90 hip stop is approved and final** (already noted in the L91 addendum, c5917da): angled PU 90A ø16×10 on a ramp bracket, struck by the L39 yaw tab, **+0.046 kg robot**. The 8g hold is cleared.
- **Final limit, LEFT leg (it supersedes the L91 addendum's −18 inward end; together they replace L87's −35..+40 / −40..+35):**
  - Yaw **−12..+28° for roll ≥ −3°**.
  - For −12 ≤ roll < −3: **yaw_max = 28 − 2(−3 − r)**, **yaw_min = −12 + (7/9)(−3 − r)**, which gives **+10 / −5 at roll −12**.
  - Roll adduction contact at **−10°**, **−12.3° fully crushed**.
  - **RIGHT leg mirrored:** yaw −28..+12 → −10..+5 at roll +12; roll contact +10, +12.3 crushed.
- **Reasons (Controls 1b44344):**
  - The r116b knee housings touch at yaw ±40.
  - The right yaw tab is 0.31 mm from its bracket at −40.
  - The hanging hand is 0–1.65 mm from the thigh plate at inward yaw −15..−35.
  - The new limit also keeps the L90 8g L↔R gap ≥ 30 mm, since the inward end is tighter than L90's −18.
- **Ramp bracket:** the inward (−yaw) face moves so the crushed end sits at −12°. With 2.24° crush at 25 % strain, **PU contact is at −9.8° (roll ≥ −3)**, ramping to contact −2.8° / crushed −5° at roll −12. The outward face is unchanged (contact +25.8 / crushed +28 → +7.8 / +10).
  - Ramp slope: inward 7/9 °/° of roll, outward 2 °/°.
  - Bracket geometry is re-placed by angle only: same r64 tab radius, inward face rotated +6° from the L90 position. model_v4 L39 bumper placement update is pending (not swept; it needs a one-line angle change at model_v4 l.123).

## L93 — L91 VOID (D101 d409a93); L92 stop re-sweep; Controls b2f20d0 clash recheck; D99 taper FEA brief; clevis pocket fit, 2026-10-21
- **L91 integrated stop is VOID.** Robot Lab / Actuators D101: the r116b housing never comes within 162 mm of the strike zone. D99 stays at 92.5 J.
- **Roll sign (model_v4):** LEFT hip roll −10 moves the L foot from y 130 → −38.8, i.e. toward the midline, so **negative = adduction on the left**. RIGHT hip roll −10 moves the R foot −130 → −298.8, so negative = abduction on the right and **R adduction = +roll**. The convention is mirrored, consistent with L90–L92.
- **L92 coupled-stop re-sweep (model_v4_l92.py, legs copy; hip_stop_l92_sweep.py → results/r031/hip_stop_l92_sweep.json; boundary points, mirrored + crossed, knee 0/145):**
  - **L↔R knee housings 0.0 mm at L yaw +28 / R −28 (both toe-out), roll 0.** Housings: both legs toe-out, mirrored, knee 0 (yaw_housing_l93.json): roll 0: yaw 16 → 3.85 mm, ≥ 19 → 0.0; roll −3/−6: 0.0 already at yaw 16. Controls (2) is confirmed and is worse with both legs toed out.
  - Hand ↔ thigh 2.75 mm at yaw −12 (both sides) = Controls (4). **Arms/Controls item**, not a leg change.
  - Tab ↔ own brackets 3.56 mm (L). The R tab 0.0 is a **model artefact**: the legs copy places the R brackets at the L joint-angle values (−10/+26) and must mirror them to (−26/+10) for R. It is not a hardware clash.
  - 8g L↔R panel (skirt_r8g_l92.json): **27.5 mm at pitch 42.5 (overtravel), roll −3, yaw +28, both. FAILS 30 by 2.5 mm.** Shroud 51.3. Panel yaw scan at roll 0/−3: yaw 27 → 31.3, 26 → 35.2. **yaw_max 27 at roll ≥ −3 restores ≥ 30**, or accept 27.5 at overtravel pitch only (+40 contract gives more). Robot Lab to pick.
  - **Patch note for modules/model/model_v4.py l.122 (not edited: outside modules/legs):** `for lim in (-35,45)` → `for lim in ((-10,26) if s>0 else (-26,10))` (contact angles; crushed −12/+28 L, mirrored R). The ramp coupling with roll is enforced by the pose limits, not modelled as a ramp.
- **Controls b2f20d0 (branch repin-j10-r8, clash_hipyaw_clear_v4.json) recheck:** roll_clash_l93.py (hip-pitch screw bodies, ankle screws, knee housings vs adduction, single straight / double / walking stance + swing pitch ±25 with roll −3/+6.1). **Run not finished at push; results go to results/r031/roll_clash_l93.json when done (see L93b).** Proposed limit pending that run. The housing result above already requires **toe-out yaw ≤ +16° (L) / −16° (R) whenever both legs toe out**, or a coupled yaw cut at roll ≤ −3 (housings 0 at yaw 16, roll −3).
  - Items (4) palm 2.75 mm to the knee trunnion at yaw −12 and (5) wrist fork ↔ hip_pitch screw at abduction +15 / yaw −12 are **for Arms/Controls** (arm swing envelope), not leg changes.
- **D99 taper FEA brief:** grokbuild/d99_taper_arm_fea_brief.md. 7075-T7351 arm 18→9 × 24, L 63, R5 root; cases 3.65 / 5.25 / 5.53 kN (T_STOP 830) + one-arm 70/30 + fatigue; gates 262/393/58 + bearing tiers at the ø6 bores; mesh ladder to 0.125 mm local; Kt, SF, stiffness, mass outputs. Robot Lab to queue on the bryan PC.
- **Clevis-bridge PU pocket fit (clevis_pocket_fit_l93.py → results/r031/clevis_pocket_fit_l93.json):** stack 28×24 × 44/50/56 at r50/55/60 from the tongue-neck face at 130°, along the arc tangent (dir 0.643, 0.766).
  - **DOES NOT FIT.** The **knee lever r47.5 (Actuators) sweeps through the stack: 7.5 cm³ at r50, 5.8 at r55, 2.6 at r60**, plus the femur tube (≤ 0.6 cm³) and the tibia tube (0.6–0.9 cm³).
  - The tangent path also never reaches the clevis bridge (bridge is forward at x 3..43; stack ends x ≈ −10). The bridge cannot hold the seat without a ≥ 40 mm rearward extension that runs into the femur-tube end.
  - Free volume (stack minus non-neck clashes): 21–34 cm³ against a needed 62 cm³ PU, so it is also volume-short.
  - Best case r60 × 56: 33.8 cm³ free, lever clash 2.6 cm³.

### L93b — roll clash results (roll_clash_l93.json; L adduction = −roll, R adduction = +roll)
- **Reproduced (1).** One leg adducted, other leg straight at 0: hip_pitch screw bodies 40.0 mm at 0°, 19.4 at 3°, **0.0 at 6°** (≥ 3 mm up to ≈ 5.5° [interp]). Ankle screws 54.4 at 3°, 21.0 at 6°, **0.0 at 8°** (Controls (3): 10°). Knee housings 40.7 / 26.7 / 18.1 / 11.1 / 5.0 at 3/6/8/10/12°.
- **Double (both adducted, mirrored):** screws **0.0 at 3°**. **Max ≈ 2.8° each** for ≥ 3 mm [interp from 40.0 at 0].
- **Walking (stance L adducted; swing R at hip pitch ±25, knee 40, R roll −3 or +6.1):** every gap is **≥ 19.2 mm up to stance adduction 10°** (hip_pitch screws ≥ 19.7, knee housings ≥ 19.2, ankle ≥ 67). The swing-leg pitch offset separates the screws. Single stance at the measured −7.6..+6.1 passes with ≥ 24.7 mm.
- **Proposed final limit (Controls software coupling; the mechanical roll stop stays at contact −10 / −12.3 crushed):**
  - Let Δp = |L hip pitch − R hip pitch|.
  - **Δp < 10° (legs side by side):** adduction ≤ **5°** for the adducting leg with the other at ≤ 0 adduction; **≤ 2.5° each** if both adduct (double stance).
  - **Δp ≥ 20° (walking stance/swing):** adduction up to **10°** (the hardware stop).
  - Linear between Δp 10 and 20.
  - **Yaw cut for (2):** toe-out ≤ **16°** per leg when both legs are toed out and Δp < 10°; toe-out 0..16 at roll ≤ −3 (housings 0 at yaw 16, roll −3 mirrored). Otherwise the L92 limit stands.
- (4)/(5) palm and wrist-fork are handed to Arms/Controls.

## L94 — Robot Lab rulings, 2026-10-21
- The clevis pocket is CLOSED; D99 stays at **0.871 kg** (CAD).
- The pitch-coupled roll software limit (L93b) is ACCEPTED for now.
- The **27° toe-out cap** and the **≥ 30 mm** 8g L↔R gap are KEPT.
- The D99 taper FEA (grokbuild/d99_taper_arm_fea_brief.md) is QUEUED, waiting on Bryan's OK.
- Study started: limp first contact at the −10° adduction stop → results/r031/hip_screw_limp_l94.md.
- **L94 limp study (partial):** first contact at −10 limp is the **inboard hip_pitch screw bodies + eye-stub flange (body↔body)**, single and double, not housings or bumpers. The Legs-only interim is PU 95A pads on a clamp band around the inboard bodies (needs Actuators' OK). The final fix is an Actuators screw-line splay/clock. See results/r031/hip_screw_limp_l94.md.

## L95 — WBC walk_1p2_r2_heel070 pair gaps (wbc_pair_gaps_l95.py → results/r031/wbc_pair_gaps_l95.json), 2026-10-21
- The full 12-joint pair poses come from Q[:, qa]; the joint order (yaw, roll, pitch, knee, ankle pitch, ankle roll; L then R) is [EST] from controller.py.
- **Frame 118** (L roll −6.9 / R −7.4, L pitch −28.8 / R −38.8): hip_pitch screw bodies **34.35 mm**, ankle screw bodies 82.6, knee housings 56.7.
- **Frame 1718** (roll +6.0 / +6.0, pitch −35.6 / −35.4, double-support-like): 40.3 / 87.4 / 57.9.
- **Scan:** 6 frames (118, 1718 + the L−R roll extremes 173, 448–450); the full 1865-frame scan was NOT run (time). Worst is **frame 118 for all three**: 34.35 / 82.6 / 56.7, all ≥ 3 mm with large margin.
- **Note:** the real gait keeps ≥ 34 mm, where the static "other leg straight" check (L93b) gives 0 at 6°. **The limit should be pair-geometry based** (both legs' joint vectors, as L93b's Δp coupling approximates) rather than a single-leg roll cap. Controls should run the pair clearance check on the full plan set.
