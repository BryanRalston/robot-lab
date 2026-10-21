# L60 knee trunnion bracket: fall load case (T&R, 2026-10-21, for Legs L74 af1b331)
Purpose: give Legs a fall load so they can book an SF on the L60 top plate, straps and notch, instead of a capacity. Hand derivation [EST]. Inputs: legs/DECISIONS.md L6/L25 (knee RV12x5, 7267 N = 345 N·m / 47.5 mm lever, twin screws, 8.66 kN design couple), sim/v3 masses, R146_PRONE_LANDING §9, T-031/T-030, Controls A44 knee drop.

## Load path
The L60 bracket only reacts **the twin knee roller-screw thrust** (trunnion pins → top plate → strut/straps → femur). Ground and pad forces at the knee pads go through the knee clevis/web, not through L60. They reach L60 only through the **knee joint moment** they create, which the screws carry. The bracket fall load is therefore **screw-line axial thrust = knee moment / 47.5 mm lever** (total of both screws).

## Candidate fall cases
| case | knee moment source | knee moment (N·m) | thrust at L60 (kN, both screws) |
|---|---|---|---|
| T-031 forward fall 1.03 kJ (straight-ish knee, chest pad) | shank+foot ≈ 4 kg decelerated at ≤ 38 g (pad plateau), arm ≈ 0.25 m | ≈ 370 | **7.9** |
| T-030 side fall / back fall (tuck, knee drop then hip/back contact) | knee drop lands on the feet in a squat: ground reaction × knee offset, **capped by the drive** (beyond its thrust the screw backdrives) | ≤ drive cap | **≤ 14.5** (2 × 7267 rated) |
| R-146 kneel / knee-pad impact (failed kneel or passive collapse onto the knee pads) | pad force acts ~50 mm ahead of the knee axis (sim pad box [EST]); collapse 0.91 → 0.67 m CoG = 161 J into an unspecified pad | pad F × 0.05; any F > 14 kN backdrives the screw | **≤ 14.5** (drive-capped) |
| R-146 L2/L3 prone tip | chest pad takes it; knees are the pivot, knee moment ≈ friction/drive hold | < 1 | ≈ 0 |
- **Governing: the knee-drop / knee-pad impact cases (side/back fall knee drop and the R-146 kneel collapse).** The screws are the fuse: they backdrive once the thrust exceeds what the drive can resist.
- **Quasi-static ceiling 14.5 kN** (2 × 7.27 kN rated thrust, Actuators' figure).
- **Dynamic factor 2.0**: an impulsive application in which the rotor's reflected inertia must be backdriven through 2π/5 mm lead. No backdrive-force data exists, so I use the sudden-load factor 2 for a step load on an elastic member [EST].
- **Fall design load: F_fall = 29 kN axial along the screw line**, split 14.5 kN per screw.

## Point of application and vector
- **At the two trunnion pins of the knee twin screws** (Legs model_v4 KNEE_G trunnion, thigh frame; the V5 note gives the trunnion at about x −130, z 770, y 130 ± 45 for the screw pair). Use Legs' exact pin coordinates.
- **Direction: along the screw axis** at the worst knee angle. Run the vector at both knee 90° (kneel, the governing pose) and knee 135° (stop), tension and compression, i.e. ±29 kN.
- **Load split:** equal per screw, plus an asymmetric case of 0.65/0.35 (one screw leading in a twisted landing) [EST].
- **Allowable:** fall limit 393 MPa (7075-T7351 ≤ 1.5 in, R-127/R-128), so book SF = 393/σ at 29 kN, ≥ 1.0 required.
- Also check the design couple (8.66 kN → 262) and fatigue (5.77 kN walk → 58 amplitude) as Legs already does.

## Excluded / missing (not invented)
- **Knee hard stop:** if the 135° stop is the end of the screw stroke (inside the actuator), a backdriven collapse into the stop puts the stop impact through L60, and this case is unbounded by the drive cap. Actuators/Legs must state where the stop is. If it is internal, add a stop-impact case (cf. L26 hip: 117.6 J needed a soft limit).
- Drive peak thrust (> rated?) and backdrive force: Actuators. If the peak is above 7.27 kN, scale F_fall linearly.
- Knee pad stiffness/stroke (pads are sim-only boxes): ID/Legs.
- No fall-sim knee-torque log exists. Controls should log knee joint torque and screw force in T-030/T-031/A44 runs to replace the DF 2.0 estimate.

## Sanity check of Legs' notch + twin straps (L74)
| item | Legs | T&R check |
|---|---|---|
| notch x −34.5…−61 × y 104–156, R8, ≈ 1320 mm² | ≥ 1200 | area OK. It lies exactly over the chimney: fins −53, baffle −57, release housing front −61. **Thermal re-check with 1320 instead of the 2080 they modelled:** T&R rerun of r131_optB.py gives Tb **71.3 °C** (vs 70.6), jet 80 °C → still PASS 80 |
| straps 2 × 20×8, 4.33 kN each design → 27 MPa, SF 9.7 | ✓ arithmetic | OK |
| walk 9.0 MPa amplitude × Kt 2.0 = 18 → SF 3.2 vs 58 | ✓ | OK |
| fall capacity 126 kN (2 × 160 × 393) | ✓ pure tension | **vs F_fall 29 kN → SF 4.3 (tension)**. In compression, Euler at pinned-pinned L ≈ 120 mm [EST]: σcr ≈ 255 MPa → 82 kN → SF 2.8. Still PASS. Legs to give the strap length and end fixity |
| strut removal | — | OK: the ligaments feed the straps in line. The notch removes the strut landing, so the strut must go |
- **Weak links not yet checked (the real fall SF lives here):**
  - the **strap-to-femur/clamp-ear joint** — bolted shear/bearing or a bonded saddle. DP490 is 9.5 MPa at 82 °C, so a bond needs an area ≥ 29 kN / (9.5/1.5) ≈ 4600 mm², or must be bolted;
  - strap-to-plate joint;
  - L58 band clamp slip under 29 kN;
  - the new **metal thermal path** across the L71 PEM/G10 break (Thermal);
  - strap clearance to the release housing (y 27.6–232, top at 814, 2 mm FLAG).
- **Verdict:** the proposal is sound on the strap and notch sections (SF 4.3 tension / 2.8 buckling at 29 kN [EST]). **Book SF at the joints, not the straps**; FEA (bryan PC, quadratic elements) is owed.

# Rev B (2026-10-21 ~10:05 ET): DLF basis revised, knee stop and tube moment (after Legs 916c57f / L78, Actuators D96/D97)
## B1. Two corrections to rev A's 29 kN
1. **7267 N is the motor peak for the screw PAIR** (Actuators D96: "K_PEAK = 1.0 (7267 N pair = motor peak)"), not per screw. Rev A doubled it. The quasi-static ceiling is **7.27 kN pair → 345 N·m knee**.
2. **"DF 2.0" was the step-load bound on an elastic member.** It doesn't apply this way: the drive is a current-limited actuator, not a suddenly applied external load. The real dynamic increment is the **reflected rotor inertia**, which Actuators quantified (D97): **1840–2590 N per screw** from rotor deceleration at the stop, i.e. ≤ 5.18 kN pair.

## B2. Structural DLF (half-sine/ramp response) [EST]
- **Load event:** knee stop crush (D97: PU k ≈ 8.6 kN·m/rad, peak at 6.9°). Effective inertia striking about the knee: the above-knee body and thigh ≈ 55 kg at ≈ 0.4 m → **I ≈ 8.8 kg·m²** (+0.2 reflected armature, sim/v3) [EST]. Load rise (quarter period) **t_r = (π/2)√(I/k) = (π/2)√(9.0/8600) ≈ 51 ms**.
- **Tube response:** shank first bending mode with the foot mass. 45 × 1.5 7050, L ≈ 0.38 m, foot+ankle ≈ 1.2–1.5 kg tip mass → f₁ ≈ 100–150 Hz [EST hand estimate] → **T_n ≈ 7–10 ms**.
- t_r / T_n ≈ 5–7. Ramp-response DLF = 1 + |sin(π t_r/T_n)|/(π t_r/T_n) ≤ **1.06**; half-sine of duration 2t_r ≈ 100 ms ≫ T_n → DLF ≈ 1.0–1.05. **Use DLF 1.05.**
- Phase 1 (foot impact suddenly flexing the knee, before the stop): contact rise ≈ 10–20 ms [EST, unmeasured ground/foot compliance] → t_r/T_n ≈ 1–3 → DLF ≤ 1.2. That applies only to the motor + rotor term below, and phase 1 does not govern.
- **Verdict on 2.0: REVISED to DLF 1.05 (1.2 in phase 1) on the structure, with the rotor-inertia force added explicitly.**

## B3. Does the r75 PU stop cap the tube moment?
- **Load path:** shank + foot free body. The moment in the tibia at the knee end equals the ground reaction moment about that section (F_ground × lever, minus shank inertia). That in turn equals the **net knee moment the thigh applies to the shank** = stop moment + screw (motor) moment ± rotor-inertia term. The ground force adjusts until it matches what the knee can resist (the knee flexes and the body descends otherwise). So **the tube moment is set by the knee's resisting moment, not by the ground lever**, until the knee's resistance exceeds what the ground lever can demand.
- **The stop does not bypass the tubes.** Pad (thigh clevis) → striker (shank tongue) puts the stop moment straight into femur and tibia as knee moment (Legs L78 is correct). **It acts in parallel with the drive**, not instead of it.
- **Phases:**
  - **Phase 1 (knee < 135°):** M_knee ≤ motor 345 + rotor resisting sudden flexion 246 (5.18 kN × 47.5 mm) = 591 → × 1.05 = **0.62 kN·m**.
  - **Phase 2 (on the stop):** M_knee = stop 830 (r75 at design energy) + motor 345 if fall mode still commands peak extension torque. The rotor term opposes here: the decelerating rotor drives flexion and is reacted by the stop, so it is excluded from the upper bound. → (830 + 345) × 1.05 = **1.23 kN·m**.
  - If Controls zero/limit the knee torque near the stop (≤ 50 N·m inside 125–145°, cf. hip L26 soft limit): (830 + 50) × 1.05 = **0.92 kN·m**.
- **The stop caps the moment only within its energy.** D97/r75 at design energy 62.7 J/knee, energy SF 1.54 → it bottoms at ≈ 97 J/knee, after which the moment is unbounded (PU solid, steel shims). The per-knee fall energy into the stop is Controls' basis (0fb7c0e). It must stay ≤ 62.7 J at the worst fall (G5 check).

## B4. Governing tube moment, SF, required wall (7050-T73511, R-127: design 262, **fall limit 393**; fall case → 393)
| case | M (kN·m) | tibia 45×1.5 σ / SF393 | femur 50×1.5 σ / SF393 | tibia wall for SF 1.0 | femur wall |
|---|---|---|---|---|---|
| Legs (rev A 29 kN) | 1.38 | 640 / 0.61 | 513 / 0.77 | 2.64 | 2.03 |
| phase 1, drive path | 0.62 | 288 / **1.37** | 231 / 1.70 | 1.07 | 1.0 |
| **phase 2, stop + motor peak (governing)** | **1.23** | 572 / **0.69** | 459 / **0.86** | **2.31** | **1.79** |
| phase 2 with Controls knee torque ≤ 50 N·m at the stop | 0.92 | 428 / **0.92** | 343 / **1.14** | **1.66** | 1.3 (OK as is) |
- Mass for a 0.38 m length per leg: tibia 1.5 → 2.31 ≈ +0.12 kg/leg; tibia → 1.66 ≈ +0.02 kg/leg; femur → 1.79 ≈ +0.05 kg/leg [EST].
- **The L60 bracket fall load (rev A 29 kN) is revised to 13.1 kN** = (7.27 + 5.18) × 1.05 along the screw line, pair total. Leading screw 0.65 → 8.5 kN vs C0a 27.3 kN (SF 3.2). Legs' strap and bracket SFs improve ×2.2. The stop moment does not pass through L60.

## B5. Verdict and actions
- **Legs:**
  - **book tube SF on 1.23 kN·m** (stop 830 + motor 345, DLF 1.05). **Tibia 45 × 1.5 FAILS (0.69) and femur FAILS (0.86).**
  - Either take the **tibia wall 2.3 mm / femur 1.8 mm** (≈ +0.17 kg/leg), or adopt the Controls torque limit → **tibia 1.7 mm, femur 1.5 mm OK** (≈ +0.02 kg/leg).
  - Do **not** use 2.5 mm/1.38 kN·m (based on the doubled thrust).
  - L60 bracket: 13.1 kN.
- **Controls (recommended, cheapest):** in fall/TUCK/R-146 states, limit knee extension torque to ≤ 50 N·m within 10° of the 135° stop. Also report the per-knee stop energy over the fall set (must be ≤ 62.7 J, never ≥ 97 J bottoming).
- **Actuators:** confirm r75 = 830 N·m at 62.7 J, the bottoming energy, and the rotor force sign/phase.
- **Missing [not invented]:** measured shank f₁ (modal tap test), foot/ground contact rise time, Controls fall-mode knee torque near the stop, per-knee stop energy distribution. Lateral/out-of-plane tube bending from side falls is a separate case, not covered here.
- **G5:** add to TP-G5 fall set: strain gauges on the tibia/femur near the knee and knee torque logged during stop-engaging falls; pass σ ≤ 393 MPa equivalent and stop energy ≤ 62.7 J.

## Decision recorded (Robot Lab, 2026-10-21 10:01 ET)
**Controls knee-torque cap ≤ 50 N·m within 10° of the 135° stop + tibia wall 1.7 mm** (femur 50 × 1.5 kept). Design knee moment 0.92 kN·m → tibia 45 × 1.7 SF ≈ 1.03 (393 fall), femur 1.14. L60 bracket fall load 13.1 kN. Stop energy ≤ 62.7 J/knee to be shown by Controls.

# Rev C (2026-10-21 ~10:20 ET): tibia 45 × 2.0, D98 interim, D99 checked in rev C.1 below
Robot Lab rulings:
- tibia wall **2.0 mm**;
- knee drives stay on through TUCK (knee cap ≤ 50 N·m within 10° of the stop);
- powered falls ≤ 40.1 J (Controls 3d1da26/464b25b);
- **D99 designed at 44 J** (40.1 × 1.1);
- motors-off falls up to 92.5 J are a **FAULT case** that may bottom the stop.

D98 is rejected for mass, and D99 is not in the repo yet, so the D98 curve is used as an interim.

Section moduli: tibia 45 × 2.0 **Z 2781 mm³**; femur 50 × 1.5 **Z 2691 mm³**. Structural DLF 1.05 (rev B).

## C1. Normal case (powered fall, 44 J)
- D98 (results/KNEE_STOP_PU_D98.md, DECISIONS D98): 815 N·m at 62.7 J, 834 at 66 J, bottoming 92.5 J / 143.6°. Effective secant k = 815²/(2 × 62.7) ≈ 5.3 kN·m/rad → **at 44 J: M_stop ≈ 683 N·m** (interim; a D99 sized for 44 J will have its own curve).
- **PU rate margin ×1.2 on moment** [EST, cast PU 90A at a fall strain rate; no rate data in the repo. Actuators' D98 ×1.4 is on energy, not moment]. → 820 N·m.
- Tube M = (820 + 50 cap) × 1.05 = **913 N·m** → **tibia σ 328, SF 1.20; femur σ 339, SF 1.16** (vs 393). Without the rate margin: 770 N·m → 1.42 / 1.37. **PASS.**

## C2. Fault case (motors off, bottoming at 92.5 J): no rupture
- Interim bottoming moment from D98: **978 N·m + 50 cap = 1028 N·m** (conservative: with motors off the cap moment is 0) × 1.05 = **1079 N·m**. Beyond 92.5 J the stop is rigid and the moment is unbounded, so the fault case is valid only up to the 92.5 J Robot Lab bound.
- **Allowables** (MATERIALS_DB AL7050_TUBE, MIL-HDBK-5H, 7050-T73511 extrusion): **Ftu S-basis L/LT 483/469 MPa** (the repo has no A-basis for T73511; S is used as given, and LT 469 is taken conservatively). The fall limit 393 = Fty-based.
- **Tibia 45 × 2.0:** σ = 1079e3 / 2781 = **388 MPa ≤ 393** (no yield). Rupture margin 469/388 = **1.21. PASS.**
- **Femur 50 × 1.5:** σ = 401 MPa. That is slight yield (> 393, permanent set possible) but ≤ Ftu 469, margin 1.17. **No rupture: PASS (inspect and replace).**
- **Local buckling / crippling in bending:**
  - Tibia D/t 22.5, femur 33.3; E/Fty = 71 000/393 ≈ 181.
  - Classical elastic local buckling σcr ≈ 0.6 E t/R ≈ 3800 MPa (tibia) / 2600 (femur). With a bending knockdown of ~0.3–0.5 [EST] it is still ≫ Fty, so the tubes yield before they buckle elastically.
  - Inelastic slenderness, using the AISC 360 round-HSS flexure limits as a proxy [uncertain for Al]: compact ≤ 0.07 E/Fy ≈ 12.7, noncompact ≤ 0.31 E/Fy ≈ 56. Both tubes are **noncompact**: they reach first yield (M_y), not the full plastic moment, before local buckling. The fault moments are ≤ ≈ M_y (tibia 0.99 M_y, femur 1.02 M_y), so **no local buckling expected**. Verify with the Al ADM round-tube formula in the Legs FEA (nonlinear, with imperfection).
- **Permanent set accepted for the fault case**, with inspect and replace: see INSPECTION_SCHEDULE.md item F1.

## C3. D99 inputs needed (to replace the interim)
1. Stop moment at the **44 J design energy** (quasi-static and at the fall rate);
2. stop moment and angle at the **bottoming energy** (and the bottoming energy itself; it must be ≥ 92.5 J for the fault case to stay bounded, else state the rigid-hit moment);
3. **PU rate factor** (moment, at the knee speed of the fall), from a supplier or a drop test;
4. the **Controls fall-mode knee speed cap** (rad/s at stop contact) used to set the 44 J;
5. striker/pad placement and mass (≤ 0.35 kg).

Pass gates for D99: (M_44J × rate + 50) × 1.05 ≤ 1093 N·m (tibia SF ≥ 1.0) and ≤ 1058 N·m (femur); bottoming moment × 1.05 ≤ 469 × Z (no rupture: tibia 1242 N·m, femur 1202 N·m).

# Rev C.1 (2026-10-21 ~10:25 ET): D99 check (Actuators 63f9a24, results/KNEE_STOP_PU_D99.md)
This replaces the D98 interim. Tibia 45×2.0 Z 2781 mm³; femur 50×1.5 Z 2691 mm³; DLF 1.05.
- **Contact at 130°.**
- **Normal, 44.1 J:** stop 544 N·m; with rate ×1.3 [EST, PUR90A, unmeasured]: (544×1.3 + 50)×1.05 = **795 N·m**. **Tibia SF 1.37, femur SF 1.33** vs 393. **PASS.**
- **Fault, bottoming at 95.8 J (motors off):** stop 789 N·m → **1077 N·m** in the tube. **Tibia 387 MPa** (≤ 393, no yield), **femur 400 MPa** (slight set). Both are ≤ Ftu S 469, so no rupture; D/t 22.5/33, no local buckling (rev C §C2). **PASS with inspection item F1.** Bottoming energy 95.8 ≥ 92.5 J, so the fault case is bounded.
- **Speed cap:** 5.58 rad/s at stop contact gives 44.1 J; **8.22 rad/s reaches bottoming**.
- **Mass: FAIL**, 0.484 kg vs 0.35 kg budget. Legs/Actuators to resolve; re-check the moments if the pad changes.
- The rate factor ×1.3 is still [EST], to be measured in TP-G5-20.
- **Rev C.2 (2026-10-21):**
  - **D99 mass: PASS by Robot Lab ruling.** The cap was raised to 0.49 kg; D99 is 0.484 kg (Legs L84 placement 0.487).
  - Femur 50×1.5 at bottoming: yield SF 0.98, accepted as slight set under F1 (Legs L79/L83, Robot Lab).
  - Legs strap SF 2.53 noted (13.1 kN, G10 bearing at 71 °C).
- **Rev C.3 (2026-10-21, Controls 976eca8, provisional):**
  - Knee TUCK stop energy: **0/90 runs over 44.1 J, max 38.5 J**. The powered case is under D99's 44.1 J design (normal SFs 1.37 / 1.33 hold).
  - **A tripped drive gives ≤ 81 J.** That is a **fault case** under the 95.8 J bottoming energy: no bottoming, no rupture, covered by the C.1 fault check (1077 N·m bound); **inspect per F1**.
