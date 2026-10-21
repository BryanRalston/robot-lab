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
