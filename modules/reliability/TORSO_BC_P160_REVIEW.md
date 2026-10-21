# Torso BC / LC1 basis / chest plateau / P-160 review (T&R, 2026-10-21 ~11:20 ET)
Triggers:
- Torso & Power request on b3811cc (job 3c rev E: +2.63 kg, robot ≈ 72.1 kg).
- Robot Lab PRIORITY: item (1) first.
- Arbiter R-157 (0d9a3f9): plateau study + T-031 gate.

**Status:** (1), (A) and (B) are complete. P-160 (2) is partial (inputs list).

Sources:
- CHEST_DESIGN_LOAD.md (b1fe48f), R146_PRONE_LANDING.md;
- torso/DIAGNOSIS.md 3c rev E;
- PROPOSALS P-160;
- torso/T031_chest_contact(_r2).md;
- RULINGS l.1530;
- mass properties from modules/legs/rl/humanoid_mjx.xml (68.0 kg sim model; it lags the 72.1 kg robot, so the load ratios are used).

Script: torso_bc_inertia_relief.py.

## 1. Fixed-pelvis BC: wrong for LC1. Use inertia relief.
**Physics:**
- In a chest-first landing (R-146 L2/L3, T-031) the floor touches only the chest pad (plus, in the kneel tip, the knees).
- The pad force decelerates the whole body. The pelvis and legs (≈ 34 of 68 kg) are **inertial mass, not ground**.
- The waist transmits only the force and moment needed to decelerate the parts below it.
- A fixed pelvis at the hip-yaw interface makes the waist react the **full 29 kN and 29 × 0.150 = 4.36 kN·m**. That puts the whole pad load through the waist, yoke and pelvis, which never happens physically in this fall.
- The chest land, bulkhead and socket still see the full 29 kN locally, under either BC.

**Free-body (d'Alembert) waist loads per 29 kN pad force**, normal to the chest, pad 150 mm above the waist-pitch axis [EST, the P-160 lever]. Waist pitch is locked (on its stop); quasi-static inertia relief. The cartridge plateau has a ≈ 0.2 mm rise and the torso's mode 1 is 207 Hz, so DAF ≈ 1 [EST].

| reaction model | waist shear | waist pitch moment | vs fixed |
|---|---|---|---|
| fixed pelvis (Torso 3c) | 29.0 kN | 4.36 kN·m | 1.00 |
| V1: whole body rigid (all joints locked, upper bound on leg participation) | 5.9 kN | 2.00 kN·m | 0.20 / 0.46 |
| V2: legs on hip pins (backdrivable hips; leg mass lumped at the hips) | 7.2 kN | 0.67 kN·m | 0.25 / 0.15 |
| V3: kneel tip, knees grounded (pelvis pinned at the hip-pitch axis, legs excluded) | 4.7 kN | 0.51 kN·m | 0.16 / 0.12 |

**Envelope** = max shear 7.2 kN and max moment 2.0 kN·m, × 1.25 for mass-property and articulation uncertainty [EST] (the sim model has 68 vs 72 kg, a different mass split, and hip motor torque transmitted in V2/V3):
- **Waist design loads: shear 9.0 kN, pitch moment 2.5 kN·m (limit); ultimate × 1.5 = 13.5 kN / 3.75 kN·m.**
- That is **≈ −69 % shear, −43 % moment** vs fixed.
- Expected stress reduction in the waist-path members (waistY, yoke cheeks, pelvis, hip-yaw interface) ≈ 40–70 % [EST]. Pelvis LC1 SF 1.04–1.26 → ≈ 1.8–3 [EST]; waistY 1.14–1.77 → ≈ 2–3 [EST].
- The bulkhead/land/socket results are unchanged (local load).

### Ruling-ready recommendation (LC1-IR, ready to run)
- **BC: inertia relief** (Abaqus *INERTIA RELIEF / Nastran PARAM,INREL,-2 / CalculiX equivalent) on the full torso + pelvis model with a **lumped-mass representation of the rest of the robot**:
  - head + neck 0.85 kg at the neck interface;
  - each arm 7.82 kg at the shoulder-pitch interface;
  - **each leg 12.68 kg as a point mass at the hip-yaw interface, joined by RBE3/coupling** (legs on hip pins, no moment: V2), with the waistY pitch DOF tied to the stop (locked).
  - Scale the model mass to 72.1 kg (current credible).
  - If the solver has no inertia relief: free-free with a soft spring BC (k ≤ 1e-4 of the structural stiffness), or the **envelope spring fallback** below.
- **Loads** (unchanged from CHEST_DESIGN_LOAD §4, until the A/B result below is ruled):
  - LC1a: 29.0 kN uniform, normal, on the 101 × 101 land;
  - LC1b: ±25 mm offsets;
  - LC1c: 25°, 21.2 N + 9.9 T;
  - ultimate 43.5 kN.
  - Factors: limit vs the fall allowable min(A-basis, Sy/1.1); ultimate no rupture; buckling ≥ 1.5 at limit; k_land ≥ 5.3 MN/m. No extra SF.
- **Envelope check run (one additional case):**
  - fixed pelvis, but **the applied load replaced at the waist by V = 9.0 kN, M = 2.5 kN·m** (limit) for the waist path;
  - plus the full LC1 on the land with the waist-pitch cheek as support, for the bulkhead.
  - This brackets the IR result if the solver's IR is suspect.
- **Rerun request** (heavy, to the bryan PC via Grok Interface; Torso to file):
  - job 3d = 3c rev E geometry with LC1a/b/c/u under IR (+ the envelope check);
  - then a mass-optimization pass on the pelvis reinforcement, waistY, yoke cheeks/spacers and the RB7013 bearing choice.
  - Report the waist-section force/moment from the IR run to confirm ≤ 9.0 kN / 2.5 kN·m.
- **Mass opportunity [EST]:**
  - of the 2.2 kg "honest floor", the waist-path items (yoke 1.42 + waistY 0.41 + pelvis 0.6 ≈ 2.4 kg gross) scale with the waist moment;
  - at 0.57 × moment, expect **≈ −1.0 to −1.4 kg**, so net ≈ **+1.2–1.6 kg** at LC1 29 kN.
  - The P-160 stop load also drops.

## B. T-031 1.03 kJ gate: NOT traceable to a defined fall, so cut it (RULINGS l.1530 rule)
**Origin** (torso/T031_chest_contact.md, _r2.md):
- "full robot 65.4 kg × 38 g × 42 mm = 1.02 kJ, the Controls gate basis".
- This is an **assumed force × stroke (pad sizing heuristic)**, not a fall energy.
- TARGETS T8 defines falls from standing but gives no energy. No T8 fall case in the repo produces 1.03 kJ.

**Defined falls:**
- R-146 L3, uncontrolled tip from standing, **527 J** to the pad (ΔPE 549 J);
- L2: 368 J.

**Governing energy per RULINGS: worst defined fall × 1.5 = 527 × 1.5 = 791 J.** Using ΔPE 549 × 1.5 = **824 J** is the conservative variant, used below for sizing.

**Reduced LC1:**
- Keeping the current core (116 mm, 81.2 mm usable, ≥ 10 % margin → 73.8 mm), the minimum plateau at the weakest corner (quasi-static, 15°) is 824 J / 73.8 mm = **11.2 kN** (vs 18.1 now).
- The ratio of the upper-bound dynamic plateau to the weakest corner (lot spread 22.3/19.5, rate 1.30, 15° 0.93) is 29.0/18.1 = 1.60.
- So **LC1 limit = 11.2 × 1.60 = 17.9 kN, ultimate 26.9 kN** (−38 %).
- With 791 J: 10.7 kN → LC1 17.1 kN.

## A. Plateau study (core stroke fixed at 116 mm = 73.8 mm usable with 10 % margin; governing energy 824 J)
LC1 = 1.60 × the weakest plateau. Mass delta [EST] is scaled from b3811cc +2.63 kg.
- **Fixed-BC column:** linear with LC1.
- **IR column:** waist-path 2.4 kg gross scaled by the IR moment (0.57 × LC1/29); the box/bulkhead/land share ≈ 0.2–0.5 kg scaled with LC1. All crude.

| weakest plateau (15°, QS) | stroke used for 824 J | stroke margin | LC1 limit / ult | Δmass fixed BC [EST] | Δmass IR BC [EST] | feasible |
|---|---|---|---|---|---|---|
| 18.1 kN (now) | 45.5 mm | 1.78× | 29.0 / 43.5 kN | +2.63 | +1.2–1.6 | yes |
| 14.0 | 58.9 | 1.38× | 22.4 / 33.6 | +2.0 | +0.8–1.2 | yes |
| 12.0 | 68.7 | 1.18× | 19.2 / 28.8 | +1.7 | +0.6–1.0 | yes |
| **11.2** | **73.6** | **1.10× (limit)** | **17.9 / 26.9** | **+1.6** | **+0.5–0.9** | **yes, lightest** |
| 10.0 | 82.4 | < 1.0 (> 81.2) | 16.0 / 24.0 | — | — | no (needs a 130 mm core, outside the envelope) |

**Pick (lightest feasible inside the repo pad envelope, 116 mm core / 101 × 101 land):**
- **plateau ≥ 11.2 kN weakest-corner QS (≈ 12.1 kN nominal-lot 0° QS min) → LC1 17.9 kN limit / 26.9 ult, with the IR BC.**
- **How to get it:**
  - a lower-crush core at the same area, e.g. a lower-density 5052 grade (≈ 0.6× the 4.5 pcf crush);
  - **Materials to select from the HexWeb catalog and give a cited crush strength + lot spread + rate factor.** No value is invented here.
  - If the spread or rate differ, recompute the 1.60 ratio.
- **Side effects:**
  - pack/torso g drop ≈ 38 % (good: R146 pack shock);
  - L3 crush ≈ 527/11.2 = 47 mm vs the ≈ 70 mm head gap, needing ≥ 47 + 11 = 58 mm → **PASS (ID to confirm)**;
  - L1 elastic gate unaffected;
  - 25° off-axis ×0.73 is still within the stroke? 824/(11.2×0.73)=101 mm > 81 → **at 25° the defined falls go to the shoulder pad / LC2 (R-146 basis). Confirm with Controls that the 25° L3 does not land on the chest alone.** OPEN.
- **Not recommended:** making the core thicker (envelope, ID bulge 65 mm already).

**Recommendation to rule:**
1. Adopt the **IR BC** now (independent of the plateau).
2. Cut the T-031 1.03 kJ gate in favour of **824 J (L3 ΔPE × 1.5)**.
3. Re-spec the core to a **weakest plateau 11.2–12 kN**, giving **LC1 18–19 kN**.

Until the Materials core data exist, Torso reruns with IR at LC1 29 kN (job 3d); the LC1 reduction is a second step (job 3e) after the core is chosen.

## 2. P-160 waist-pitch hard stop: PARTIAL
- **Moment basis:**
  - 4.36 / 6.54 kN·m comes from the fixed-pelvis BC and is **not physical** (§1).
  - IR envelope: **2.5 kN·m limit / 3.75 ult** at LC1 29 kN. With LC1 17.9 kN: **1.55 / 2.3 kN·m** [EST].
  - These need confirmation from the job 3d IR waist-section output.
- **In parallel with the actuator:** yes, by design (cheek-to-cheek, bypassing gear and bearing): correct.
  - The **gear sees torque until the stop closes**: T_gear = k_gear × engagement gap.
  - **Need from Actuators:**
    - gear (CSG/strain-wave or planetary?) torsional stiffness;
    - **repeated-peak and momentary torque ratings**;
    - backlash;
    - motor 116 N·m and the drive's fall-mode behaviour.
  - Check: k_gear × gap + motor ≤ momentary rating. Choose the stop gap so the gear windup at contact is ≤ the repeated-peak rating.
  - The "engage ≤ 2° before the soft limit" draft must be expressed against the gear windup.
- **Energy:**
  - In a chest fall, torso and pelvis decelerate together, so the relative waist-pitch rotation energy is small. The stop sees the inertial moment of the lower body (≤ 2.5 kN·m), not an impact.
  - Waist-pitch impact energy for a **fall with the waist moving** (e.g. a fall during a bend) is not in the repo. **Controls to log waist-pitch speed at stop contact in the T-031/R-146 sims.**
  - Elastomer sizing waits on that.
- **Fall cases:**
  - prone/R-146: covered by the IR moment;
  - **backward fall** (back/pack contact, +60° side) has no defined case: OPEN; needs a Controls sim of back-fall waist moment and speed;
  - side falls go to the hip-roll bumpers (SIDE_FALL), not the waist pitch.
- **Stiffness/bottoming:**
  - A rigid metal stop is fine for a quasi-static inertial moment.
  - If elastomer-faced, Actuators to give k and the bottoming angle. The gear windup at bottoming must stay ≤ the momentary rating.
- **Structure SF:**
  - stop lug force at r 60 mm: 2.5 kN·m → 42 kN limit total, i.e. **10.4 kN per lug** (2 lugs per side, 4 total) [EST], vs 73 kN in P-160;
  - the lug/cheek SF must come from Torso's job 3d (stop lugs in the model).
- **Inputs Actuators must supply:**
  - gear type and torsional stiffness;
  - repeated-peak / momentary / ratcheting torque;
  - backlash and windup;
  - stop geometry within the housing (lever r, lug count);
  - stop face material and k/bottoming;
  - output bearing moment rating;
  - whether a torque limiter is needed.
- **Verdict:** **CONDITIONAL**. Keep the stop concept (parallel, cheek-to-cheek); **re-rate it to the IR moment (2.5 / 3.75 kN·m at LC1 29 kN)** pending job 3d and the Actuators inputs above.

## Missing inputs
- Current mass properties (72.1 kg CAD split; the sim model is 68 kg);
- the real pad-to-waist-axis lever (150 mm assumed);
- Materials' lower-crush core data;
- Controls: 25° L3 contact and waist-pitch stop speeds; backward-fall case;
- Actuators: the P-160 list above.

## A.1 Core selected (Materials b359af8, modules/materials/CHEST_PAD_CORE.md), 2026-10-21 ~11:10 ET
**Core: HexWeb CR III 5/32-5052-3.8, pre-crushed**, on the 101 × 101 land, 116 mm.

| item | value | gate | result |
|---|---|---|---|
| nominal plateau, 0° QS | 13.0 kN | — | — |
| weakest corner, 15° QS | 11.7 kN | ≥ 11.2 kN | PASS |
| dynamic upper bound | 17.4 kN | ≤ LC1 17.9 kN | PASS |
| energy over 73.8 mm usable (10 % margin) | 864 J | ≥ 824 J (L3 ΔPE × 1.5) | PASS |
| ratio of upper dynamic to weakest | 1.49 | (1.60 assumed in §A) | better |

**Verdict: CONDITIONAL on the lot spread.**
- The ±3 % lot spread is [EST].
- At ±10 % the weakest corner is 10.9 kN < 11.2, so it **FAILS**.
- The lot spread must be proven per lot by **TP-G5-21** (incoming inspection).
- **Fallback for a soft lot: the 104 × 104 land** (+6 % area). Its upper bound must still be ≤ 17.9 kN, so it is used only for low lots.

LC1 for job 3e stays **17.9 kN limit / 26.9 kN ultimate** with the IR BC.
