# Hip pitch lever O13 — FEA convergence report

Status: the SF 1.5 criterion was not met. There is no converged peak. d0 was left at 25 mm.

The meshes below are the needle hip_pitch lever (`HUB=needle`, `ROOT=37.5,26`, args `25 25 15 0`) with a drawn fillet on the arm-to-cheek junction. Solver, material, loads, and the check region are the existing `hp_lever_fea.py` setup: 7075-T6, E 71.7 GPa, nu 0.33, Sy 503 MPa, F = 4542 N per pin, P2 tets, pyamg CG to about 1e-8. CPU only, 8 threads. The run is the Windows venv at `.venv` (Python 3.12).

## Geometry

The drawing callout is R3 on the BSPLINE edges where the arm meets the cheek end face at |y| = 33.5. Those four curves span the whole 5 mm cheek wall (r 21 to 26). A constant R3 self-intersects, and the solid fails `BRepCheck`. The largest valid constant radius is R2.8. Every mesh in this study used that fillet:

`R2.8 on 4 BSPLINE junction edges at |y|=33.5`

7075 mass went from 0.204759 kg (unfilled h=4 baseline) to 0.204849 kg, a change of 0.090 g. Total lever mass, including the two steel pins, is 0.249240 kg. The profile-fillet CLI argument stayed 0. The drawn radius is `junction_fillet`.

The fillet ends on the bore circle r = 21 at |y| = 33.5. That circle is the element-max in every mesh (about |x| 11–14, |y| 34.0–34.4, z −15.5 to −16.7). OCC fillet of the circle fails. A revolved R2 lip round, cut before the junction fillet, removes corner material but either leaves a sharp edge, will not volume-mesh once an R3 or R2 junction fillet is added (the fillet surface meets the torus), or, with the lip and no junction fillet, diverges faster: h = 4 mm peak 346 MPa, h = 3 mm peak 486 MPa at r ≈ 22. That solid was not used. The numbers below are the R2.8 fillet only.

## Meshes

| h (mm) | local (mm) | nodes | tets | ndof | worst sym | SF_sym | SF_fault |
|---:|---:|---:|---:|---:|---|---:|---:|
| 4 |  | 2811 | 9093 | 51426 | sym_phi-60 | 1.467 | 1.508 |
| 3 |  | 4696 | 16411 | 88686 | sym_phi+60 | 1.446 | 1.493 |
| 2.5 |  | 7500 | 28641 | 146913 | sym_phi+60 | 1.391 | 1.391 |
| 2 |  | 12432 | 50586 | 250542 | sym_phi+60 | 1.317 | 1.317 |
| 2 | 1.5 | 15133 | 64255 | 310827 | sym_phi+60 | 1.028 | 1.137 |

The 1.5 mm size is a gmsh Field Box on |y| 30..38, on top of h = 2 mm. It is a local check, not a Richardson point. Mass is identical across the five meshes.

## Element max (MPa)

| case | 4 | 3 | 2.5 | 2 | 2 / local 1.5 |
|---|---:|---:|---:|---:|---:|
| sym_phi-90 | 258.69 | 264.26 | 292.03 | 308.42 | 412.91 |
| fault_phi-90 | 252.18 | 256.48 | 292.03 | 308.42 | 367.19 |
| sym_phi-60 | 342.85 | 335.54 | 359.51 | 378.92 | 454.91 |
| fault_phi-60 | 333.58 | 322.76 | 359.51 | 378.92 | 437.95 |
| sym_phi-30 | 335.41 | 327.09 | 334.06 | 365.72 | 440.54 |
| fault_phi-30 | 325.85 | 315.46 | 334.06 | 365.72 | 395.02 |
| sym_phi+0 | 238.36 | 238.79 | 225.30 | 255.90 | 308.56 |
| fault_phi+0 | 231.07 | 231.36 | 225.30 | 254.66 | 300.83 |
| sym_phi+30 | 322.15 | 338.49 | 336.02 | 367.32 | 435.21 |
| fault_phi+30 | 322.15 | 327.95 | 336.02 | 354.75 | 428.99 |
| sym_phi+60 | 329.15 | 347.82 | 361.58 | 381.96 | 489.54 |
| fault_phi+60 | 329.15 | 336.93 | 361.58 | 381.96 | 442.58 |
| sym_phi+90 | 258.69 | 264.26 | 292.03 | 308.42 | 412.91 |
| fault_phi+90 | 252.18 | 256.48 | 292.03 | 308.42 | 367.19 |

## p99.9 (MPa)

| case | 4 | 3 | 2.5 | 2 | 2 / local 1.5 |
|---|---:|---:|---:|---:|---:|
| sym_phi-90 | 234.23 | 238.03 | 202.25 | 213.17 | 234.52 |
| fault_phi-90 | 222.83 | 190.10 | 184.24 | 185.21 | 207.52 |
| sym_phi-60 | 292.16 | 248.21 | 235.32 | 237.78 | 262.64 |
| fault_phi-60 | 197.22 | 217.12 | 198.22 | 189.56 | 205.94 |
| sym_phi-30 | 280.54 | 238.60 | 228.53 | 229.80 | 251.26 |
| fault_phi-30 | 192.97 | 211.55 | 190.03 | 184.30 | 190.94 |
| sym_phi+0 | 205.23 | 200.64 | 181.30 | 187.68 | 204.81 |
| fault_phi+0 | 189.17 | 166.22 | 164.59 | 160.64 | 175.68 |
| sym_phi+30 | 271.53 | 240.40 | 234.19 | 226.89 | 239.78 |
| fault_phi+30 | 217.22 | 194.07 | 208.17 | 181.58 | 181.54 |
| sym_phi+60 | 282.05 | 249.12 | 240.20 | 234.71 | 250.83 |
| fault_phi+60 | 222.64 | 203.08 | 216.73 | 191.68 | 187.96 |
| sym_phi+90 | 234.23 | 238.03 | 202.25 | 213.17 | 234.52 |
| fault_phi+90 | 222.83 | 190.10 | 184.24 | 185.21 | 207.52 |

The ±90 rows match. From h = 3 mm on, the worst symmetric case is phi +60, not phi −60.

## Richardson

The pass is SF_yield ≥ 1.5 on the converged peak, which means the peak must be at or under 335.33 MPa. The extrapolation uses the three finest uniform meshes (h = 3, 2.5, 2 mm) and is accepted only when the three values are monotone and p is in [0.4, 4].

Symmetric phi −60 element max: p = 2.052, vm0 = 412.34 MPa. three-point Richardson on the finest uniform meshes. The four uniform values are not monotone (h = 4 is 342.85 MPa, h = 3 is 335.54 MPa). The local mesh at the same case is 454.91 MPa, which is above that intercept. This is not a converged peak.

Symmetric phi +60 element max, which governs: no finite intercept. The difference ratio on the three finest uniform meshes is 0.675, and the p→0 floor for these mesh sizes is 0.817, so no positive p fits. The differences grow as h shrinks, from 347.82 to 361.58 to 381.96 MPa, and the local mesh reaches 489.54 MPa. There is no finite extrapolated peak.

p99.9 for phi −60: no finite intercept. three finest values are not monotone.

p99.9 for phi +60 on the uniform meshes: p = 3.423, vm0 = 229.92 MPa. three-point Richardson on the finest uniform meshes. The local mesh reverses it (234.71 MPa at h = 2, then 250.83 MPa with the box). p99.9 is not the pass criterion, and it has not settled either.

## Result

Governing peak: 489.54 MPa, sym_phi+60, on the finest mesh, at [-11.1, -34.3, -16.7]. SF_yield = 1.028. The h = 2 mm uniform mesh is already 381.96 MPa, SF 1.317. Both are past 335.33 MPa, and the max is still climbing.

d0 was not increased. The brief's 1 mm d0 steps apply once a converged peak is above the allowables. This peak is a mesh singularity at the bore-lip end of the fillet. A thicker arm (about 4 g per mm in the brief's estimate; not measured here) does not delete that edge, so a d0 loop would not produce a finite peak under 335 MPa. Reporting one would be a pass on a corner that has not converged.

`results/hp_lever_fea_r4.json` now stores this finest mesh. `SF_sym` is 1.028 and matches `cases`. `converged` is false. The per-h JSON files, `hp_lever_fea_convergence.json`, the plot `hp_lever_fea_convergence.png`, the STEP `cad/hip_pitch_lever_B_needle_sf15.step`, and `hp_lever_fea_field.npz` are the same run.

## What was left unchanged

`PROOF_TEST_hip_lever.md` still cites the unfilled h = 4 mm result (332 MPa, SF 1.51, 0.16 mm). D33 and the rulings that gate the −0.245 kg credit on O13 were not edited. O13 is not closed. `linkage_table.py` was not re-run; it reads `mass_kg`, which moved by 0.090 g. `CONTRACTS.md` and the actuator selections were not edited.
