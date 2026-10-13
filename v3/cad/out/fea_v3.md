# v3 FEA (full-length parts with fillet collars; 3-level mesh refinement)

Body weight 608 N (v3 mass 62.0 kg); landing 3 BW, walking 1.3 BW (0→peak, σa=σm=σ/2), 5 y × 8 h at 1 stride/s = 5.26e+07 cycles; 7075-T6 Sy 503 / Su 572 / Sf(5e8) 159 MPa; Goodman SF = 1/(σa/Sf + σm/Su).

| case | load | tets (finest) | peak vM (99.5 %) MPa | Δ last refinement % | converged | SF yield | Goodman SF |
|---|---|---|---|---|---|---|---|
| knee_clevis | bridge top fixed; pin bores loaded 3 BW + peak knee-actuator reaction 2909 N | 23697 | 42 (max el. 91) | 10.6 | NO | 11.94 | 13.63 |
| fall_hip_bracket | flange fixed; side-fall hip contact 13.7 kN lateral into the yaw ring | 31515 | 33 (max el. 98) | 2.7 | yes | 15.34 | — |
| fall_shoulder_housing | inboard flange fixed; side-fall shoulder impact 11.2 kN (through clutch+pad) at the outboard end, radial | 28612 | 56 (max el. 67) | 0.5 | yes | 8.92 | — |
| pelvis_hip | waist-yaw opening rim fixed; single-leg landing 3 BW (+0.15 lateral) into the hip-bracket ring | 42625 | 44 (max el. 95) | 1.7 | yes | 11.37 | 12.98 |
| femur_full | hip lug top fixed; knee-pin bore loaded 3 BW axial + lateral H (root moment 3 BW × 0.12 m) | 35703 | 47 (max el. 65) | 0.1 | yes | 10.62 | 12.13 |
| fall_torso_panel | torso side panel (CFRP 3 mm [EST isotropic]); front/back wall strips fixed; 50 % of shoulder impact at the pass-through rim | 17463 | 298 (max el. 383) | 4.3 | yes | 1.34 | — |