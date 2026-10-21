# Job 2R — G3 hip-pitch lever FEA (brief G3-R2)

Solver: `hp_lever_fea_v2.mesh` / `solve` (gmsh OCC tets, Ball size fields, scikit-fem P2, pyamg CG). Same boundary-condition selectors as job 2: cosine pressure on the ø42 bore, yoke face fixed at |y| = 13.5, pin traction on the ear pins. Design load 4542 N per pin. Fully reversed amplitude is the design von Mises times 2030/4542. Linear elasticity, so that scale is exact for one load case.

Material: 7075-T651 plate, thickness along x (ST), single load path. Static gate ≤ 271 MPa. Fatigue gate ≤ 58 MPa at 2030 N/pin, R = −1. E = 71.7 GPa and ν = 0.33 are the job 2 solver constants. The von Mises field is force-driven, so E cancels; ν is unchanged from job 2.

Mesh: Ball radius 4 mm and thickness 4 mm, 14 centres only. Levels h/hloc = 4/1.5, 3/1.0, 2.5/0.6. A level over 300k tets would be remeshed at Ball radius 3 mm. That did not happen unless a level record says so.

Ball centres, case A (case B shifts the upper and lower x with the arm width):

- Upper R8, 45° point on the blend cylinder at z = −14: A (±19.34, ±40.84, −14), B (±17.34, ±40.84, −14).
- Ear-root R5, brief centres: both cases (±13, ±48, −52).
- Lower R8, fillet-edge midpoints: A (±17.37, ±38.50, −25.71), B (±15.09, ±38.50, −27.30).
- Bore lips, arm side of the r = 21 circle: both cases (0, ±33.5, −21).

Check mask is the job 2 mask: drop elements within 2.5 mm of the yoke face and the steel pin stubs. Peak is the element-maximum von Mises on the symmetric (both pins) cases.

D92 hand estimate to compare, not a gate: upper R8 peak about 119 MPa and amplitude about 53 MPa; ear R5 amplitude about 48–64 MPa.

Overall verdict (case A, the b34/d40 lever): **FAIL**.

## Case a: b34/d40/e26, governing geometry

Volume 175164.0 mm³. Mass 0.5207 kg per lever (7075 body 0.4763 kg, steel pins 0.0444 kg).

| level | h / hloc | ball r | tets | ndof | governing | peak MPa | p99.9 | p99.9/peak | location mm | amp MPa |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 4 / 1.5 | 4 | 23071 | 117993 | sym_phi-30 | 526.21 | 111.25 | 0.211 | (-12.73, 49.84, -52.44) | 235.19 |
| 2 | 3 / 1 | 4 | 55549 | 266193 | sym_phi+30 | 503.78 | 106.62 | 0.212 | (12.73, 49.84, -52.44) | 225.16 |
| 3 | 2.5 / 0.6 | 4 | 136023 | 615777 | sym_phi-30 | 759.77 | 119.47 | 0.157 | (-12.71, -49.84, -52.69) | 339.57 |

Family maxima inside each Ball, peak / amplitude in MPa:

| level | upper R8 | ear R5 | lower R8 | bore lip |
|---|---|---|---|---|
| 1 | 59.6 / 26.6 | 526.2 / 235.2 | 111.9 / 50.0 | 10.1 / 4.5 |
| 2 | 62.5 / 27.9 | 503.8 / 225.2 | 115.5 / 51.6 | 10.3 / 4.6 |
| 3 | 93.4 / 41.7 | 759.8 / 339.6 | 145.0 / 64.8 | 13.8 / 6.2 |

Finest-level families (max inside the Ball radius on the governing case): upper_r8: 93.4 MPa / amp 41.7 at (16.68, -42.79, -16.18); ear_r5: 759.8 MPa / amp 339.6 at (-12.71, -49.84, -52.69); lower_r8: 145.0 MPa / amp 64.8 at (16.90, 38.40, -22.11); bore_lip: 13.8 MPa / amp 6.2 at (3.52, 33.29, -20.84).

Off-surface samples on the finest governing case: outward normal [-0.9783, 0.0, -0.2073], surface gap 0.028 mm; 2 mm inward: 160.4 MPa (amp 71.7) at (-10.74, -49.76, -52.15), 0.15 mm from the target; 4 mm inward: 60.2 MPa (amp 26.9) at (-8.89, -49.97, -51.79), 0.18 mm from the target.

Convergence, levels 2 to 3: peak change 50.81% (5% or more), same fillet after folding ±x/±y: shift 0.25 mm (yes, within 2 mm), absolute coordinate shift 102.88 mm, p99.9/peak 0.157 (below 0.75).
Not converged. Singular at (-12.71, -49.84, -52.69). The level-3 element max is 759.8 MPa and the amplitude is 339.6 MPa. Those numbers are not a pass and are not extrapolated.
Case verdict: **FAIL**.

## Case b: b30/d36/e26, fillet-only comparison

Volume 156129.5 mm³. Mass 0.4672 kg per lever (7075 body 0.4228 kg, steel pins 0.0444 kg).

| level | h / hloc | ball r | tets | ndof | governing | peak MPa | p99.9 | p99.9/peak | location mm | amp MPa |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 4 / 1.5 | 4 | 20961 | 109380 | sym_phi+30 | 307.61 | 117.16 | 0.381 | (12.56, 49.36, -53.13) | 137.49 |
| 2 | 3 / 1 | 4 | 50207 | 244860 | sym_phi+60 | 433.89 | 138.99 | 0.320 | (12.53, 49.63, -53.33) | 193.92 |

Family maxima inside each Ball, peak / amplitude in MPa:

| level | upper R8 | ear R5 | lower R8 | bore lip |
|---|---|---|---|---|
| 1 | 145.9 / 65.2 | 307.6 / 137.5 | 127.7 / 57.1 | 10.8 / 4.8 |
| 2 | 238.2 / 106.4 | 433.9 / 193.9 | 137.0 / 61.2 | 18.3 / 8.2 |

Finest-level families (max inside the Ball radius on the governing case): upper_r8: 238.2 MPa / amp 106.4 at (-14.55, 43.50, -14.51); ear_r5: 433.9 MPa / amp 193.9 at (12.53, 49.63, -53.33); lower_r8: 137.0 MPa / amp 61.2 at (-14.54, -38.25, -23.97); bore_lip: 18.3 MPa / amp 8.2 at (-3.86, 33.26, -20.92).

Off-surface samples on the finest governing case: outward normal [0.9669, -0.0, -0.2551], surface gap 0.07 mm; 2 mm inward: 111.8 MPa (amp 50.0) at (10.57, 49.44, -52.26), 0.59 mm from the target; 4 mm inward: 136.3 MPa (amp 60.9) at (9.00, 49.73, -51.99), 0.48 mm from the target.

Gate: INCOMPLETE (2 of 3 levels). No pass, and no extrapolation. Level 3 was meshed (121448 tets, Ball radius 4 mm) and was still in the CG solve at the 11:15 ET checkpoint, so it is not in this table.

## Hand estimate

D92 estimate: upper R8 peak about 119 MPa and amplitude about 53 MPa (nominal 88/39, Kt 1.35). Ear R5 amplitude about 48–64 MPa. The FEA columns below are the maxima inside those Balls. A value is not a converged Kt when it is still moving, or when p99.9 is far below the element max.

Case a: upper R8 60/27 → 62/28 → 93/42 MPa (peak/amp), last step 49%; ear R5 526/235 → 504/225 → 760/340 MPa (peak/amp), last step 51%.

Case b: upper R8 146/65 → 238/106 MPa (peak/amp), last step 63%; ear R5 308/137 → 434/194 MPa (peak/amp), last step 41%.

Where the last step is over 5%, that blend is not converged. Do not read it as beating or missing the hand estimate.

## If this fails

The next geometry step in G3-R2 is ear Ø26 → 28 with the R5 kept. The rod sweep has to be checked again (Ø32 was 0.5 mm). This re-run does not switch the lever to 17-4PH.
