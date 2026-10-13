# Legs r4 M2: structure + thigh clamp + instep lugs (per leg)

Baseline per R-015 M2: 4.85 parametric + 0.20 clamp [EST] + 0.084 lugs = 5.134 kg both legs; target ≤ 4.85 kg (−0.25 after absorbing the clamp).

| zone | part | kg per leg | basis |
|---|---|---|---|
| thigh | femur tube Ø50 wall 1.2 mm (was 1.6) | 0.154 | SF yield 6.56 (v3 FEA × BW × Z ratio); +9084 N hip screw axial below the clamp: 49 MPa |
| thigh | femur collars ×2 | 0.063 | unchanged |
| thigh | femur hip ring: CRBH 5013 seat ø80 H7×13, OD 96 × 25 (|y|≤12.5) + neck | 0.226 | hand: net tension SF 5.39, shear-out SF 9.33, fatigue 3.28 at P 12440 N; replaces the 0.212 kg ø32 lug |
| thigh | knee clevis | 0.235 | r3 (SF ≥ 4.80 v3-scaled, hand 15.3) |
| shank | tibia tube Ø45 wall 1.2 mm (was 1.6) | 0.149 | SF yield 3.84 |
| shank | tibia collar | 0.029 | unchanged |
| shank | ankle fork (top plate pocketed) | 0.158 | r3 hand SF 3.44 |
| shank | knee tongue | 0.233 | r3 hand SF 35 |
| foot | foot closed box (3.5 mm skins, 4 webs, 6 mm skins under sensor, hollow instep 5 mm) | 0.870 | FEA P2 h5: fall 6 BW toe p99.9 182 MPa SF 2.77 (max 322 MPa at the rigid sensor-ring edge, SF 1.56, mesh-dependent); carry Goodman 4.81 |
| thigh | thigh clamp (hip_pitch bodies, axial eye form) | 0.237 | FEA P2 h2.5: 4542 N per screw max 174 MPa SF 2.9; walking 0.52× fully reversed SF 1.76 |
| foot | ankle rod-end lugs on instep (2) | 0.042 | Legs line (LINKAGE_TABLE); counted here once |
| | **per leg** | **2.396** | |
| | **both legs** | **4.792** | target ≤ 4.85 → margin +0.058 kg |

Not in this line: CRBH 5013 bearing + clamp ring (Actuators), levers, pins, hubs, rod ends (Actuators LINKAGE_TABLE), clamp split-collar bolts (~0.01 [EST]), hip stop bumper (~0.01 [EST]).
FEA caveats: P2 tets on a ~1 GB box (half models, symmetry), foot h 6→5 mm p99.9 178→182 MPa (converging), peak at the rigid fixture edge grows with refinement (singular); tubes, clevis, tongue, fork and ring are hand/v3-scaled, not FEA. Converged runs + flange-modelled sensor in grokbuild/structure_fea.md.
