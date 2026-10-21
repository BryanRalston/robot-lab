# Side-fall frontal-plane tube bending: femur 50 × 1.5, tibia 45 × 1.7 (T&R, 2026-10-21)
Allowable: 7050-T73511 fall limit **393 MPa** (R-127). Z: tibia 45 × 1.7 = **2412 mm³**, femur 50 × 1.5 = **2691 mm³**. Hand calcs [EST] unless cited.

## Inputs from the repo
- Geometry (model_v4 / sim v3): hip roll axis z 1045, hip pitch 920, knee 500, ankle 80. Foot box 240 × 100 mm, sole ≈ 86 mm below the ankle, **half-width 50 mm**.
- Masses (sim v3): thigh 2.38, shank 3.16, foot 2.65 kg; robot 68.42 kg.
- **Hip roll:** TBM2G-08508A + CSG-25-100, **peak avail 204 N·m** (CONTRACTS); joint-side armature 0.441 kg·m² (sim). ROM −12…15° is a sim limit. **No hardware hip-roll stop is defined.**
- **Ankle roll:** shared screw pair, avail 177 N·m; **±18° rigid 7075 block hard stop** (Legs L29).
- Side falls: T-030 tuck B, shoulder pad 9.17 kN gate, impact ≈ 6.4 m/s at ≈ 1.5 m (T030_BRIEF). Knee pads: front only (P-158 thigh-front 3.9 kN plateau [EST]). **No lateral knee or shank pad exists.**

## Key load-path result
The leg has no lateral load between hip and foot (the knee joint is rigid in the frontal plane), so the frontal moment varies linearly between the two ends. **|M_tube| ≤ max(|M_hip end|, |M_ankle end|) + leg-inertia terms.** It is capped by the joint/foot capacities, not by the ground force, **unless a contact lands mid-leg** (scenario S2).

## S1: side fall, foot planted, leg loaded laterally
- **Ankle end:** past the rigid ±18° stop, the moment is set by the foot rolling on its edge.
  - Lever ≈ 0.05 cos 18° + 0.086 sin 18° ≈ 74 mm. Fz ≤ 2 mg ≈ 1.34 kN [EST impact factor] and Fy ≤ μ·Fz (μ 1.0, sim) at ≈ 70 mm height.
  - M_ankle ≈ 1.34 × 0.074 + 1.34 × 0.07 ≈ **193 N·m**. The rigid stop passes it straight through. The ankle actuator (177) is not the cap; the foot edge is.
- **Hip end:** hip roll motor peak 204 + rotor inertia (0.441 kg·m² × α; α ≈ Δω/t_r ≈ 4 rad/s / 20–50 ms ≈ 80–200 rad/s² [EST]) ≈ 35–88 → **≤ 292 N·m**. It is capped only while the strain-wave gear and drive yield/backdrive. **No hip-roll hard stop is defined.** If a rigid stop or a thigh-pelvis contact is added, this cap must be redone (as for the knee).
- **DLF:** contact rise 20–50 ms vs leg frontal mode T_n ≈ 10–30 ms [EST] → t_r/T_n ≥ 1 → ramp DLF = 1 + |sin(π t_r/T_n)|/(π t_r/T_n) ≤ **1.3** at t_r/T_n ≥ 1 (bounding the 1–1.5 band at ≤ 1.21 plus margin).
- **Design moment: 292 × 1.3 ≈ 380 N·m.** Tibia σ 157 → **SF 2.50**; femur σ 141 → **SF 2.78**. **PASS.**

## S2: side impact on the knee/shank directly onto the floor (mid-leg contact)
- **S2a, topple from standing, fall-side stance leg:** the foot is the pivot (v ≈ 0), hip/shoulder land first (tuck B), and the knee lands at ≈ ω × 0.5 ≈ (6.4/1.5) × 0.5 ≈ 2.1 m/s. The shank is supported at the knee and near the foot → short span, small bending. Not governing.
- **S2b, side tip from kneel (failed R-146 kneel):**
  - Femur: upper-body load enters at the hip, the knee/thigh is on the floor, and the hip-end moment is capped by hip roll ≤ 292 (×1.3 = 380 N·m) → **same as S1, PASS**, again conditional on no rigid hip-roll stop.
  - Tibia: lies on the floor, so negligible.
- **S2c, governing: knee strikes first with the foot still moving** (swing/crossing leg in a stumble side fall, or a kneel tip with the foot lifted). Knee arrested, foot+ankle (2.65 kg) at L ≈ 0.48 m behaves as a **cantilever tip-mass impact**: M = v √(k m) L, k = 3EI/L³ ≈ 1.05 × 10⁵ N/m. The tip-mass impact formula already includes the dynamics (no extra DLF); T_n ≈ 32 ms.
  - With no lateral knee pad (rigid cover contact, knee arrested ≪ T_n), it depends on the foot speed relative to the knee:

| foot speed rel. knee | M tibia (N·m) | σ (MPa) | SF 393 |
|---|---|---|---|
| 2.1 m/s (knee speed, foot co-moving) | 530 | 220 | **1.79** |
| 3.0 m/s | 758 | 314 | **1.25** |
| 4.2 m/s (leg swinging about the hip, foot ≈ 2 × knee) [EST] | ≈ 1060 | 440 | **0.89 FAIL** |

  - A femur analogue (thigh struck mid-span with the hip moving) is bounded by the hip roll cap as in S2b.
  - **Fix options:**
    - (i) a **lateral knee/shank pad** (crushable, like P-158) so the knee arrest time is ≥ T_n/2 ≈ 16 ms and the pad plateau ≤ ~3 kN. That roughly halves M [EST; to size with Controls velocities];
    - (ii) Controls fall-mode keeps the swing leg tucked to the body in side falls, so the knee never leads with the foot flying;
    - (iii) a 2.3 mm tibia (Z 3140 → SF ≈ 1.16 at 4.2 m/s).

## Verdicts
| scenario | governing moment | tibia 45×1.7 SF | femur 50×1.5 SF | verdict |
|---|---|---|---|---|
| S1 foot planted, lateral | 380 N·m (hip-roll capped, DLF 1.3) | 2.50 | 2.78 | **PASS** (if there is no rigid hip-roll stop) |
| S2a topple, stance leg knee contact | small | — | — | PASS |
| S2b side tip from kneel | 380 N·m | — | 2.78 | PASS (same condition) |
| S2c knee-first, foot moving | 530–1060 N·m | **1.79 → 0.89** | (hip-capped) | **CONDITIONAL**: needs the foot-relative velocity from sim; a lateral knee pad or a swing-leg tuck rule |

## Missing inputs (not invented)
- Hip roll **hardware stop** (none defined): its type/stiffness/location, and the CSG-25 momentary/ratcheting torque. If rigid, S1/S2b are no longer capped at 292 N·m.
- Side-fall sim outputs (Controls): knee and foot velocities at first leg contact, contact order, planted-foot Fz/Fy, hip-roll torque and angular acceleration. These replace the v and α estimates.
- Lateral knee/shank contact definition (the cover stiffness or a pad): none exists.
- Measured leg frontal T_n (tap test) and the shank f₁.
- Foot sole friction coefficient (sim 1.0).

## G5: TP-G5-19 (G5_TEST_PLAN.md)

# Rev B (2026-10-21 ~10:10 ET): hip-roll L39 PU bumper stop (Legs L39 / L80 data, all [EST])
**Correction:** rev A's 292 N·m hip cap assumed no rigid stop. L39 exists: a roll lug 12×12×26 at r 63 hits 2 PU 90A ø20 × 10 bumpers (one per direction), contact at −12°/+15°, rated 4 J (L39: "impact 0.76 J vs 4 J"). Legs L80 data [EST, no supplier curve]:
- E 45 MPa (30–60), Ec ≈ 1.5E → k ≈ 2.1 kN/mm (1.4–2.8) → **k_θ 8.4 kN·m/rad (5.6–11.1)**.
- Linear to 25 % strain (2.5 mm, 2.3°): **334 N·m (222–445), 6.6 J (4.4–8.8)**.
- Stiffens sharply above 30 %; **rigid bottom-out by 40 % (4 mm, 3.6°)**.

## B1. Model
The hip-roll joint moment is motor (204 N·m peak, backdriving) **in parallel with** the bumper spring, with a rigid bottom-out. Tube moment ≤ joint moment × structural DLF; the tube-end logic of rev A still holds.
- The bumper event is a spring-mass hit: t_r = (π/2)√(I/k_θ) ≈ 14–54 ms for I 0.65–9.9 kg·m², vs leg frontal T_n 10–30 ms [EST]. The spring peak already contains the dynamics; the extra **structural DLF on the tubes is 1.1** (t_r/T_n ≳ 1.5 → ramp DLF ≤ 1.21 at 1.5; ≈ 1.1 at ≥ 2).
- **Energy into the stop:** E = ½ I_eff ω_c², where ω_c is the relative hip-roll speed at contact (after the motor's work) and I_eff is the relative-motion inertia incl. 0.441 kg·m² rotor armature (sim):
  - **S2b side tip from kneel:** the thigh keeps swinging when the torso lands. I_eff ≈ thigh about the knee ≈ 0.2 + rotor 0.44 ≈ **0.65 kg·m²** [EST].
  - **S1 foot planted:** the leg is pinned by the ground and the body swings relative to it. I_eff between the reduced inertia ≈ **2.3** and the upper body about the roll axis ≈ **9.9 kg·m²** [EST].

| I_eff (kg·m²) | ω_c 1 rad/s | 2 | 3 | 4 |
|---|---|---|---|---|
| 0.65 (S2b) | 0.3 J | 1.3 | 2.9 | 5.2 |
| 2.3 (S1 low) | 1.1 | 4.6 | 10.3 | 18.4 |
| 9.9 (S1 high) | 5.0 | 19.8 | 44.6 | 79 |
- Fall body rate ≈ 4 rad/s (T-030: 6.4 m/s at 1.5 m), but ω_c is the **relative** hip-roll speed. In a clean topple, leg and body rotate together (ω_c ≈ 0), and the shoulder pad stops the body. **ω_c is not in the repo (Controls sim needed).** The motor cannot brake it: stopping 4 rad/s on 9.9 kg·m² with 204 N·m needs 22° vs 12–15° of ROM.

## B2. Moments and SF (tibia 45×1.7 Z 2412, femur 50×1.5 Z 2691, 393 MPa)
| bumper state | joint moment | tube M (×1.1) | tibia SF | femur SF |
|---|---|---|---|---|
| at rated 4 J, k 5.6/8.4/11.1 | 204 + 212/259/298 | 457/510/552 | **2.07/1.86/1.72** | 2.31/2.08/1.92 |
| linear end 6.6 J, k 5.6/8.4/11.1 | 204 + 272/333/383 | 523/591/645 | **1.81/1.60/1.47** | 2.02/1.79/1.64 |
| stiffening 25–40 % (≈ 7–15 J [EST]) | 204 + ~500–900 [EST] | ~780–1210 | **~1.2–0.78** | ~1.36–0.87 |
| **bottomed (> ~15 J)**: rigid lug/bracket k_θ ~ 400 kN·m/rad [EST, steel/7075 parts] | M = √(2 E_res k_θ): 10 J residual → 2.8 kN·m | > 3 kN·m | **< 0.3 FAIL** | FAIL |
- **Tube capacity → allowable bumper moment:** tibia 393 × 2412 / 1.1 − 204 = **658 N·m**, femur 757.

## B3. Verdicts
- **S2b side tip from kneel:** E ≤ 5.2 J at ω_c ≤ 4 rad/s (I 0.65), which is ≤ 6.6 J linear but **> the 4 J rating at ω_c > 3.5**. Tube moment ≤ 591 N·m → **tibia SF ≥ 1.6, femur ≥ 1.79: PASS** (within the linear range). The bumper may exceed its rating, so inspect/replace it after the event.
- **S1 foot planted:** **CONDITIONAL.** PASS (SF ≥ 1.47) only if E ≤ 6.6 J, i.e. ω_c ≤ 2.4 rad/s (I 2.3) or ≤ 1.15 rad/s (I 9.9). Above ~15 J the bumper **bottoms → tube FAIL**. With realistic topple kinematics (body and leg co-rotating) ω_c is expected to be small, but it is **unproven**.
- **Rev A's S1 result (380 N·m, SF 2.5) is withdrawn**; it ignored the stop.

## B4. Bumper spec (if Controls' ω_c gives E > 6.6 J, or as margin now)
- **Requirement:**
  - bumper moment at the design energy **≤ 600 N·m** (tube tibia SF ≥ 1.07 incl. motor and DLF);
  - **linear energy ≥ 1.5 × E_design**;
  - bottom-out energy ≥ 2 × E_design;
  - k_θ 6–9 kN·m/rad.
- **Proposed [EST]:** PU 90A **ø24 × 16 mm** at r 63. k ≈ 1.5 × 45 × 452 / 16 ≈ 1.9 kN/mm → **k_θ ≈ 7.6 kN·m/rad**; linear to 4 mm (3.6°) → **481 N·m, 15.3 J**; bottom ≈ 6.4 mm (5.8°). This covers E_design ≈ 10 J (ω_c ≈ 2.9 rad/s at I 2.3). Mass ≈ +3 g/leg; needs 6 mm more bracket depth.
- **Consequence for the hip-skirt pinch check:** R_HIP_PINCH used +2.5° overtravel. The current bumper reaches **+3.6°** at bottom-out (the proposal 5.8°). The hem gap must be re-swept at roll −15.6°/+18.6° (current) or −17.8/+20.8 (proposal). Hem 28.3 mm at +2.5° will drop ≈ 1–2 mm [EST] → near 26 with tolerance → ID to re-run.
- **Alternative to a bigger bumper:** a Controls hip-roll soft limit + fall-mode roll damping that keeps ω_c ≤ 1 rad/s at contact. This is cheap if the sim shows that ω_c is driven by commands (tuck B roll −5°) rather than by the impact.

## B5. S2c (knee-first, foot moving)
**Pending the Controls side-fall sim.** Robot Lab prefers the **swing-leg tuck rule** (Controls keeps the swing leg tucked to the body in side falls so the knee never leads with the foot moving). Rev A's numbers (tibia SF 1.79 → 0.89 at 2.1 → 4.2 m/s) stand until the sim gives the velocities.

## B6. Missing inputs (Legs/Controls)
- **Legs:** a supplier PU 90A compression curve for ø20 × 10 (k, stiffening and bottom-out), bumper rating basis (4 J), lug/bracket stiffness when bottomed, and space for a ø24 × 16 bumper.
- **Controls:** relative hip-roll speed ω_c at stop contact and the hip-roll angle history in the side-fall set (S1 planted-foot, S2b kneel tip). The pass gate is E_stop ≤ 6.6 J (current) / ≤ 10 J (proposed).

# Rev C (2026-10-21 ~10:20 ET): Controls 464b25b sim moments, tibia 45 × 2.0
Source: controls/limits/SIDE_FALL.md, side_fall_results.json (54 runs/variant), hip-roll history. Swing-leg tuck **adopted** (Robot Lab). Hip-roll damping rejected (raises S1/S2b energy).

| scenario (tuck) | bumper E / ω_c | bumper peak / pen | hip motor peak | tube M = (bump + motor) × 1.1 | tibia 45×2.0 SF | femur 50×1.5 SF |
|---|---|---|---|---|---|---|
| S1 planted | 1.66 J / 0.58 | 120 N·m / 0.82° | 102 | 244 | **4.48** | **4.33** |
| S2b kneel tip | 3.65 J / 1.23 | 224 / 1.53° | 74 | 328 | **3.33** | **3.22** |
| S2c with tuck | 1.33 J / 0.85 | 147 / 1.0° | 102 | 274 | **4.00** | **3.87** |
| (S2c base, no tuck: for reference) | 10.62 J / 1.32 | 377 / 2.37° | 102 | 527 | 2.07 | 2.01 (but bumper over its linear 6.6 J and rated 4 J) |

**Verdicts:**
- **S1 PASS, S2b PASS, S2c PASS with the swing tuck** (0/54 bumper fails, feet always first).
- **S2c knee-first (walking stumble) is still pending** Controls' mid-gait stumble run (not reproduced from stand/kneel ICs: 0/216 knee-first).
- The bumper energy stays ≤ 4 J (rated) with the tuck in every case.
- **Bottom-out (3.6°) is never reached.** The max penetration is 2.37° (base) / 1.53° (tuck) **< the 2.5° overtravel used in R_HIP_PINCH**, so the hem gap 28.3 mm / 26.3 mm with tolerance stands for powered falls. A motors-off fault fall could exceed it (unknown). That is noted as a fault case and covered by inspection.
- The rev B ø24 × 16 bumper is **not needed** with the tuck. Keep it as the fallback if the stumble run exceeds 4–6.6 J.

## C-foot: swing-foot landing 1.40 → 1.70 m/s (tuck), foot/ankle/fasteners [EST]
- The repo has no landing-force output (the Controls rows log velocity only).
- Scaling for a contact-spring landing: F ∝ v → **×1.21**; energy ∝ v² → **×1.47** (≈ 33 → 49 J at m_eff ≈ 34 kg [EST: leg + half body]).
- With 20–40 mm of effective stroke (6 mm sole pad + backdriving ankle/knee screws [EST]): **F ≈ 1.2–2.5 kN**.
- **Existing foot load cases** (Legs STRUCTURE_FEA_REPORT): fall 3914 N (6 BW) at toe/heel; 3 BW 1957 N.
  - Fall heel SF 4.4 (yield).
  - Fall toe: element max 520 MPa (SF 0.97, singular, mesh-dependent) but 99th percentile 132.7 MPa (SF 3.79). **Open from R1: the toe/flange element maximum.**
- **Verdict: CONDITIONAL PASS.** The tucked landing is within the 3914 N fall case if the peak foot force is ≤ 3.9 kN (my bound is 2.5 kN, ×1.21 vs 1.40 m/s). The existing fall toe open item stays.
- **Ankle:**
  - Side landing onto the foot edge drives inversion into the rigid ±18° roll stop (L29, 2 × 7075 blocks 20×12×10, **M4 × 10, grade not stated** in BOM F5).
  - Roll moment ≈ F × 74 mm edge lever ≈ 90–185 N·m at 1.2–2.5 kN [EST] vs the ankle roll avail 177.
  - **Stop block bolts and lever radius are not in the repo, so this is unchecked (OPEN, Legs).** Pitch screws (C0a basis) see ≤ 2.5 kN × 0.18 m toe lever ≈ 450 N·m ankle pitch moment [EST] vs the contract 305 N·m need, so the screws backdrive. Fine for the screws (fuse); the pitch hard stop at −0.96 rad is not engaged in a flat landing.
- **Fasteners:**
  - foot F/T steel flange OD60 (bolt pattern in Legs CAD): covered by the 3914 N case if F ≤ 3.9 kN;
  - **ankle roll stop M4 × 10: OPEN** (grade unspecified, load ≈ 185 N·m / r_stop);
  - sole pad bond: Legs T8 drop test.
- **Needed:** Controls to log the peak foot contact force (normal + lateral) and the ankle roll angle/stop contact in the tuck runs. Legs to give the ankle roll stop radius and bolt grade.
- **G5:** TP-G5-19 item (e) below.

# Rev C.2 (2026-10-21 ~10:40 ET): Legs L80–L83 inputs (8e92b89 / 6a3d84c, DECISIONS L81/L83)
## Hip-roll bumper rating
- **ø20×10 PUR90A, cited curve (L81): 4.68 J at 25 % strain** (231 N·m, 5.8 kN·m/rad). This replaces the uncited L39 "4 J". 6.71 J at 30 % is [EST interp].
- Usage of the 4.68 J rating:
  - S1: 1.66 J (35 %);
  - **S2b: 3.65 J (78 %)**;
  - S2c with the tuck: 1.33 J (28 %).
  - All **PASS**.
- No-tuck S2c (10.6 J) still fails. The ø24×16 fallback (8.5 J) is held for the walking-stumble result.
- The cited k (5.8) is softer than the rev B estimate (8.4), so the peak moments in the rev C table are on the stiff, conservative side.
- **Inspect the bumpers after any event > 4.68 J** (INSPECTION_SCHEDULE F3).

## Ankle-roll stop M4 / dowel: CLOSED, PASS
**Inputs:**
- Stop face at r 45 mm (L83; a14.json).
- 2 × 7075 blocks 20×12×10, each with 1 × ISO 4762 M4 12.9 zinc-flake + Loctite 243 into a helicoil in the 7075 cross, plus a ø4 h6 hardened dowel (L83).
- One block engages per event.

**Block load:**
- **Tuck landing at 1.70 m/s:** edge-capped ankle roll moment ≈ 193 N·m [EST], giving F = 193/0.045 = **4.29 kN**. That is ≈ 2.5 kN × 74 mm edge, capped by the foot edge geometry.
- **Foot fall case / Legs stop design:** 3933 N hold × 1.5 dynamic [EST] = **5.9 kN** (265 N·m) per block.
  - This envelopes the 3914 N 6 BW fall case applied at the foot edge only if the moment is reduced to ≤ 265 N·m.
  - Full 3914 N at 74 mm would give 290 N·m / 6.4 kN [EST]. That is not credible together with the edge cap, but it is noted.

**Load sharing:**
- The dowel is h6 in reamed holes; the M4 sits in a ø4.5 clearance hole with 0.25 mm radial clearance. So the **dowel carries ~100 % of the tangential (shear) load**.
- Preload friction is ignored: 6.4 kN [EST, 75 % proof] × μ 0.15 ≈ 1.0 kN.
- The bolt carries only the prying tension from the face force acting ≈ 5 mm above the joint, about a heel ≈ 6 mm from the bolt [EST]: **T ≈ 0.83 F**.

| check | capacity | tuck 4.29 kN | fall 5.9 kN |
|---|---|---|---|
| dowel ø4 shear (Legs L83, ≈ 7.5 kN [EST, ~600 MPa]) | 7.5 kN | **SF 1.75** | **SF 1.27** |
| dowel bearing in 7075 (4 × 5 mm engagement [EST], 214/295 MPa vs ≈ 900 Fbru [EST]) | | 4.2 | 3.1 |
| M4 12.9 tension vs proof (As 8.78 × 970 = 8.5 kN; T 3.6/4.9 kN) | 8.5 kN | **2.36** | **1.73** |
| joint separation (preload 6.4 kN [EST]; separation ≈ preload/(1−Φ≈0.2) = 8 kN) | 8 kN | no separation | no separation |
| helicoil pull-out in the parent 7075 cross (STI major ≈ 5.0 mm, 1.5D = 6 mm, 0.6 thread shear-area factor → 56 mm²; Fsu ≈ 0.6 Ftu, T7351 462 → 277 MPa [EST: DB has no Fsu; the lower temper in AL7075T7351 is used] ≈ 15.7 kN) | 15.7 kN | **4.3** | **3.2** |
| bolt ultimate vs strip | 10.7 kN < 15.7 kN | the bolt fails before the threads strip (good) | |
| dowel lost, M4 shear alone (L83, 6.4 kN) | 6.4 kN | 1.49 | 1.08 (marginal) |

**Verdict:** **PASS** for the tuck landing and the foot-fall/stop design case. The dowel is the primary shear path, and the bolt, helicoil and parent material all have margin. With the dowel missing it is marginal (1.08), so dowel presence is an inspection and assembly item.

**[EST] / missing:**
- helicoil length and engagement depth (assumed 1.5D);
- block-to-cross heel geometry;
- cross temper (T6 vs T7351; the lower is used);
- dowel engagement depth;
- tightening torque/preload.
- Confirm the real foot contact force with Controls' foot-force logging (TP-G5-19 e).

**1.70 m/s landing, other parts** (Legs L81): ankle screws SF 1.72 (impulse) / 1.41 (energy) vs C0a. The cross, DU bushes and sole need Job 7 FEA proof-case SF ≥ 1.22 / 1.48 (OPEN, Legs).
