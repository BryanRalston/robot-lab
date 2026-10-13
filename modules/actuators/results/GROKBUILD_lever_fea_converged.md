# Grok Build brief: converged FEA of the hip_pitch lever (closes O13)
- Input: `modules/actuators/hp_lever_fea.py`. Geometry: `HUB=needle ROOT=37.5,26` with args `25 25 15 0 <h>`. Output STEP: `cad/hip_pitch_lever_B_needle_sf15.step`.
- Run h = 4, 3, 2.5, 2 mm (and 1.5 mm locally at the arm/cheek junction |y| ≈ 34 via gmsh Field Box) on a machine with ≥ 8 GB free. The shared box had < 1.5 GB, and h ≤ 3 was OOM-killed or swapped.
- Add a drawn R3 fillet at the arm-to-cheek junction in geom4 (OCC fillet on BSPLINE edges near |y| 33.5) before refining. A sharp edge is singular and never converges.
- Report the max and p99.9 von Mises for all 14 cases, plus the Richardson-extrapolated peak at φ −60°.
- Pass: SF_yield ≥ 1.5 on the converged peak. Otherwise increase d0 by 1 mm steps; mass grows about 4 g per mm.
- Deliver: results JSON per h, a convergence plot, and an updated `results/hp_lever_fea_r4.json`.
