# Grok Build brief: D99 tapered 7075-T7351 striker arm (Robot Lab, D101 d409a93; Legs L89/L93). Run on the bryan PC, NOT the box
**Status:** rev A, 2026-10-21. Robot Lab queues it. Same style as l74_twin_strap_fea_brief / ankle_cross_fea_brief.

## Geometry (from Actuators cad/knee_stop_pu_r75b_d99.step + Legs L89 taper)
- One arm per side, 2 per knee, 4 per robot. Cantilever from the tibia knee-end ring (bonded + 2× ø6 pins, L84 r2) out to the PU stack seat/lug at y 46 / 214 (L leg). Free length **L = 63 mm**, ring face to the lug centreline.
- Section: **24 mm radial (constant) × tangential depth h(x) = 18·√(x/63)** (x measured from the tip), **floor 9 mm** (x < 15.8 mm). The root keeps h = 18 over an **R5 fillet** into the ring. The lug (32×22×10) and the striker face are flush with the arm (Actuators r75b; t0−18…t0).
- Include the ring (ø51×3 wall × 24, 7075-T7351) with the **2× ø6 pin bores** and the pins (steel, bonded), plus a 60 mm stub of the tibia tube 45×2.0. Tie the ring to the tube through a 0.1 mm DP490 layer (E 2.5 GPa [EST]), or tied contact plus the pins.
- Parametrise: floor 8/9/10 mm, root fillet R3/R5/R8, taper exponent 0.5 (baseline) / 0.6.

## Material: 7075-T7351, single-path per R-127/R-128
E 70 GPa, ν 0.33, ρ 2.81. **Design ≤ 262 MPa (A-basis), fall/bottoming/T_STOP ≤ 393 MPa, fatigue amplitude ≤ 58 MPa** (R-031 §6; rare-event stop, so report only). Bearing at the ø6 pin bores by drawn e/D: **455 / 381 / 295 MPa** (e/D 2.0 / 1.5 / < 1.5).

## Load cases (force at the striker face centre, tangential to the r75 arc, i.e. normal to the PU face; plus the reaction couple at the tibia stub fixed end)
| Case | Per arm | Gate |
|---|---|---|
| C1 design (44.1 J ×1.3) | **3.65 kN** | σvM ≤ 262, bearing tier |
| C2 bottoming 92.5 J @ 143.6° | **5.25 kN** | ≤ 393 |
| C3 T_STOP 830 N·m (r75, two arms) | **5.53 kN** | ≤ 393 |
| C4 one-arm (stack misalignment 70/30) | 0.7 × 2 × C2 = 7.35 kN | ≤ 393, report |
| C5 fatigue | C1 amplitude, R = 0 | report vs 58 (rare-event) |
Add a ±3° load misalignment (out of plane) on C2 as a sensitivity.

## Mesh and method
- Quadratic tets (C3D10 or equivalent). **Convergence ladder** at the root fillet and the pin bores: global 2.0 / 1.0 / 0.5 mm, local fillet and bore 0.5 / 0.25 / 0.125 mm. Converged when peak σvM changes < 3 % between the last two levels. Report all levels.
- Linear static; for C2/C3 also run elastic-perfectly-plastic 7075 (Fty 393) if the linear peak > 393, and report the plastic strain (≤ 0.5 % acceptable for the fault case per T&R F1 rule).
- Pins: frictionless contact in the bores plus the bond. Also run pins-only (bond failed) for C2.

## Outputs (`legs/grokbuild/results/d99_taper_arm/`)
1. Peak σvM and section-averaged bending stress at the root fillet, x = 15.8 (taper/floor junction) and mid-taper, per case and mesh level; **Kt = peak / nominal** at the root and the bores.
2. SF against 262 / 393 / 58 and the bearing SF at each ø6 bore (tier from e/D).
3. Tip deflection and arm stiffness (N/mm). Confirm it is > 20× the PU stack stiffness (otherwise it eats stop travel).
4. CAD mass of the arm (baseline target −0.089 kg robot against the solid 24×18).
5. Best (lightest passing) parameter set; STEP to `legs/cad/d99_taper_arm.step`.

## Hand baseline (Legs L89)
Root nominal 177 / 255 / 269 MPa (C1/C2/C3) → SF 1.48/1.54/1.46 net, 1.05/1.10/1.04 at Kt 1.4 [EST]. The FEA replaces the Kt.

## Stop rules
Stop if any converged case fails its gate at the R8 fillet and the 10 mm floor; report the minimum section that passes instead. Compute budget ≤ 2 h on the bryan PC.
