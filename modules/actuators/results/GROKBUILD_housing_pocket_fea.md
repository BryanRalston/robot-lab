# Grok Build brief G4: actuator housing pocketing FEA (R-077). Run on the bryan PC / Grok Build, NOT the box
**Why not on the box:** gmsh can't load on the box (libGLU.so.1 missing), and converged P2 meshes need several GB (see G3). The box has about 4 GB free out of 15 GB.

Tags: **[CITED]** = a datasheet or repo result (source given); **[ASSUMPTION]** = chosen for this brief and not yet backed. Report any result that depends on an [ASSUMPTION] as conditional on it.

## 1. Geometry (exact STEP paths; all valid; measured on the box with CadQuery, 2026-10-14)
| Part | STEP | Solids | Volume mm³ | Mass @ 2.81 g/cm³ | Count on robot | Robot mass |
|---|---|---|---|---|---|---|
| hip yaw housing (TBM2G-06008A + CSG-17-100 + CRBH 6013 A) | `modules/actuators/cad/hip_yaw_housing.step` | 2 | 76,333 | 0.2145 | 2 | 0.429 |
| hip roll housing (TBM2G-08508A + CSG-25-100 + CRBH 6013 A) | `modules/actuators/cad/hip_roll_housing.step` | 2 | 80,582 | 0.2264 | 2 | 0.453 |
| hip pitch screw body (TBM2G-07613D + RV12x4, twin) | `modules/actuators/cad/hip_pitch_body_x1.step` | 1 | 50,717 | 0.1425 | 4 | 0.570 |
| ankle screw body (TBM2G-06013D + RV12x4, GE 12 C eye lug) | `modules/actuators/cad/ankle_body_x1.step` | 1 | 68,452 | 0.1924 | 4 | 0.769 |
| **Sum (one of each ≈ 0.78 kg)** | | | | **0.776** | | **2.221** |

- Generator: `modules/actuators/cad_mass.py` (`rotary()`, `linear_body()`). The geometry is parametric, and the dimensions there are authoritative.
- **Rotary housings (yaw, roll):** these are made up of:
  - a tube of OD D = max(stator OD, 90) + 6, wall 2.0;
  - a 2.5 mm rear cap with a 0.35·D bore;
  - the CRBH 6013 A outer-ring seat (Ø90 bore, 13 mm deep, 4 mm radial);
  - a 4 mm output flange (D + 14) with 8 × Ø5.5 holes on the D + 7 circle;
  - a 4 mm stator bond land.

  The 2 solids are the seat ring and the body. Mesh them as one bonded part (fuse them first). **[ASSUMPTION]** the 2-solid split is a CAD artefact, not a separate part.
- **Screw bodies (hip pitch, ankle):** these are made up of:
  - a motor can (stator OD + 6, wall 2.0) with a 2.5 mm rear cap;
  - a 6 mm cone down to the nut section (Ø41, wall 2.0, 56 mm long: RV12 nut 36 + 2 × 7202 angular-contact bearings);
  - a 3 mm front cap (Ø14 bore).

  The ankle also has a GE 12 C eye lug (10 mm thick, Ø22 bore, centre 15 mm behind the rear cap) and 4 × 3 mm ring fins.
- **Already at the machining minimum:** cad_mass.py sets the 2.0 mm wall from machining, not strength (line 14). **Do not thin the 2.0 mm cylindrical walls.** Pocketing is limited to the regions in §5.

## 2. Material
**R-128 update (D87):** stock is 7075-T7351 plate, 3.5 in (hip yaw/roll axis ∥ ST; screw bodies axis ∥ L). The values below are kept for stiffness; strength gates are in the Pass criteria (§ "Static") per housing.
**[CITED]** 7075-T6, as used by G3 and cad_mass.py:
- ρ 2.81 g/cm³ (cad_mass.py RHO);
- E 70 GPa, ν 0.33 (R-123(a); 71.7 acceptable for stress-only load-controlled solves, 70 for deflection gates);
- Sy 480 MPa, Su 560 MPa (R-123(a), MATERIALS_DB typical, not A/B-basis; plate > 25 mm needs a Materials product-form allowable before sign-off);
- endurance Se 87 MPa (fully reversed; the R-031 §6 / G3 basis).

## 3. Load cases
Peak torques are from the HD CSG Table 3 (`datasheets/hd_csf_csg_catalog.txt` l.413–432) **[CITED]**:

| Gear | Rated | Repeated peak | Average | Momentary |
|---|---|---|---|---|
| CSG-17-100 | 31 | 70 | 51 | 143 N·m |
| CSG-25-100 | 87 | 204 | 140 | 369 N·m |

Bearing data: CRBH 6013 A, C0 24.3 kN, C 18.8 kN (IKO, `datasheets/iko_crb_catalog.txt` l.802) **[CITED]**. Robot mass is 66.054 kg (official credible rollup) **[CITED]**, so BW = 648 N.

### Hip yaw / hip roll (rotary)
| Case | Load | Source | Use |
|---|---|---|---|
| R1 static | Momentary gear torque: yaw 143, roll 369 N·m, reacted housing → output | CSG Table 3 [CITED]. The momentary limit is the most the gear can pass. | static |
| R2 static | Bearing seat: 3 BW = 1944 N radial + 1944 N axial + moment 3 BW × 60 mm = 117 N·m on the CRBH 6013 A seat, combined with R1 | 3 BW is the Legs structure basis (legs/DECISIONS.md l.50, 164) [CITED basis]. The 60 mm arm, and applying it to the hip housings, are **[ASSUMPTION]** (no hip-housing load path is cited). | static |
| R3 fatigue | Repeated peak torque fully reversed: yaw 70, roll 204 N·m | CSG Table 3 [CITED]. Treating it as R = −1 is conservative **[ASSUMPTION]**. | fatigue |
| R4 fatigue | 1.5 BW bearing radial + axial, fully reversed, with R3 | **[ASSUMPTION]** (gait-level hip force; the gait ID in legs/results has no hip-housing forces extracted) | fatigue |

### Hip pitch screw body (one of the twin pair)
| Case | Load | Source | Use |
|---|---|---|---|
| P1 static | Axial 4542 N (454.2 N·m / 0.050 / 2), screw nut ↔ rear mount, pulled and pushed | sizing.json sel.hip_pitch T_out 454.2, arm 0.050 [CITED]. Same as G3 case 1. | static |
| P2 static | One-screw fault: 9084 N on one body | hp_bearing.json "one-screw fault case" [CITED concept]. The 2× factor is **[ASSUMPTION]**. | static, SF ≥ 1.2 only |
| P3 fatigue | 2030 N fully reversed | G3 Amendment 1 / R-031 §6 [CITED] | fatigue |
| P4 static | Motor reaction torque 2 × TBM2G-07613D stall into the can; take T_out/ratio-equivalent ≈ 454.2 / 78.54 / 2 ≈ 2.9 N·m per body | sizing.json ratio 78.54 [CITED]. Splitting it between the bodies is **[ASSUMPTION]**. | static, combine with P1 |

### Ankle screw body
| Case | Load | Source | Use |
|---|---|---|---|
| A1 static | Axial 4433 N: pitch 311 N·m / 0.070 / 2 = 2221 N plus roll 177 / 0.040 / 2 = 2212 N on the same screw | sizing.md ankle_pitch/roll available torques and levers [CITED]. Adding the two on one screw (differential worst case) is **[ASSUMPTION]**. | static |
| A2 static | GE 12 C eye lug: A1 force at up to 20.8° misalignment (bottom) / 2.8° (top), lug bore radial | ankle_v4.json bottom_misalign_max 20.8°, top_tilt 2.8° [CITED] | static |
| A3 fatigue | Gait peak 1735 N fully reversed (walk 1.0 F_peak) | ankle_v4.json life.cases [CITED]. R = −1 is conservative **[ASSUMPTION]**. | fatigue |
| A4 static (fall) | 6 BW (3888 N) foot fall is cited for the foot (legs/DECISIONS.md l.61). How much of it reaches the screw is not cited. **Use 1.0 × C0a-limited RV12 or 6 BW, whichever is lower.** If RV12 C0a isn't extracted, run 3888 N axial. | **[ASSUMPTION]** load share | static, SF ≥ 1.2 |

Falls: the side fall (11.5 kN shoulder, D71) is a shoulder case and doesn't load these housings. **No cited hip or ankle housing fall load exists.** P2 and A4 are the overload stand-ins.

## 4. Boundary conditions (all **[ASSUMPTION]** unless noted)
- **Rotary:**
  - Fix the output-flange 8 × Ø5.5 bolt holes. Apply bonded pins on the hole walls, and contact or a fixed ring on the flange face over the D + 7 bolt circle ±4 mm.
  - Apply torque as a tangential traction on the CSG circular-spline mounting face. If that face isn't modelled, apply it on the stator bond land, which is the conservative path through the full tube.
  - Apply bearing loads as cosine-distributed pressure over ±60° on the Ø90 seat bore, plus axial pressure on the seat shoulder.
- **Screw bodies:**
  - Hip pitch: fix the rear-cap mount, the axial eye per v4 D62 (rear-cap face, a ring of Ø (0.35·D…D) [ASSUMPTION]).
  - Ankle: fix the GE 12 C lug bore with a cosine pressure, misaligned per A2.
  - Apply axial load on the front cap / bearing-shoulder face (the 7202 pair seat at the nut-section front).
  - Motor torque goes on the stator land.
- **Contact:** no contact; apply loads as distributed tractions. Report the peak away from the load-application patches (≥ 2 elements) and the patch peak separately.

## 5. Pocketing approach
**Keep-outs (do not remove material):**
- the CRBH 6013 A seat ring and shoulder, plus 3 mm;
- the CSG circular-spline register and its bolt circle, plus 3 mm (HD Table 8 dims: CSG-17 øA 60, CSG-25 øA 85);
- the output-flange bolt circle annulus (D + 7 ± 5.5);
- the stator bond land;
- the 7202 bearing seats and the RV12 nut flange seat;
- the GE 12 C lug bore ± 5 mm;
- the rear-cap cable/encoder bore rim, plus 3 mm;
- the 2.0 mm cylindrical walls (machining minimum).

**Candidates (allowed design space):**
- Rear caps (2.5 mm): radial-spoke windows, 4–6 spokes, ≥ 3 mm spokes, R2 fillets.
- Output flange (4 mm) between bolts: scallops to D + 2 between the 8 holes.
- Rotary tube between the stator land and the gear: windows ≤ 30 % of circumference. Leave them sealed by a 0.3 mm film cover **[ASSUMPTION; Thermal and contamination to accept]**, or skip them if Thermal objects.
- Screw-body cone/neck: lightening windows only if the static SF holds.
- Ankle eye lug: trim the outer profile to 3 mm ligament + R.
- Ankle ring fins: remove only if Thermal accepts (they are thermal parts; flag, don't decide).

**Method:**
1. Run SIMP topology optimisation (volume fraction sweep 0.7 / 0.5) inside the design space under the static and fatigue envelope.
2. Interpret the result as machinable pockets (min tool radius 1.5 mm, min ligament 2.0 mm).
3. Re-run a P2 verification on the trimmed STEP.

Don't use lattices.

## 6. Pass criteria (per housing, every case)
1. **Static (R-128/R-130, per housing; see `STOCK_GRAIN.md`):** 7075-T7351 plate. Hip yaw and hip roll (single path, axis ∥ ST): **≤ 239 MPa**. Hip-pitch and ankle bodies (multi path, axis ∥ L): **≤ 262 MPa**; ankle eye lug ≤ 239. (Was 320.) (R1, R2, P1, A1, A2). Overload/fault cases P2 and A4: ≤ min(A-basis band, Sy_typ/1.1) per R-128 §5 = **393 MPa** (T7351 A-basis 393).
2. **Fatigue:** hot-spot von Mises amplitude ≤ **Se / 1.5 = 58 MPa** (R3+R4, P3, A3). Same rule as G3.
3. **Stiffness [ASSUMPTION; no cited limit in the repo]:**
   - CRBH seat bore ovalisation ≤ 10 µm under R2 (bearing-housing tolerance class).
   - Circular-spline face tilt ≤ 0.05 mrad × size, else HD mounting accuracy. Use the HD catalog mounting-tolerance table if it can be extracted: say so if used.
   - Rotary torsional stiffness drop ≤ 5 % vs untrimmed.
   - Screw body axial stiffness drop ≤ 10 % vs untrimmed.
4. **Convergence:** as G3. Global h 4 → 3 → 2 with local refinement at pocket fillets, down to 0.6 mm. The peak must change by < 5 % over the last two levels, else declare and locate a singularity.
5. **Untrimmed baseline:** run all cases on the untrimmed STEPs first and report them. If a baseline already fails, stop on that housing and report it. Do not pocket it.

## 7. Deliverables (into `modules/actuators/results/g4_housing_pocket/` and `modules/actuators/cad/`)
- **Trimmed STEPs:** `cad/hip_yaw_housing_pk.step`, `cad/hip_roll_housing_pk.step`, `cad/hip_pitch_body_x1_pk.step`, `cad/ankle_body_x1_pk.step` (valid solids).
- **Mass saved per housing:** measured as CAD volume × 2.81 g/cm³, both per part and × count (2 / 2 / 4 / 4) for the robot.
- **Stress plots:** von Mises for the governing static and fatigue case, baseline and trimmed, with peak locations (PNG).
- **Summary JSON:** `results/g4_housing_pocket/summary.json` with, per housing:
  - volume and mass, baseline and trimmed;
  - Δmass per part and for the robot;
  - per case: peak MPa and location;
  - SF static and fatigue amplitude;
  - stiffness metrics;
  - convergence table;
  - a pass/fail flag;
  - the list of [ASSUMPTION]s each result depends on.

Also deliver the solver script used.

## 8. Open inputs (owners)
- Hip-housing hip-joint forces from gait ID (Legs). They would replace the R2/R4 assumptions.
- Ankle screw load share in the 6 BW fall (Legs).
- Thermal acceptance of tube windows and ankle fin removal (RL Thermal).
- HD mounting tolerances (Actuators, catalog extraction).
