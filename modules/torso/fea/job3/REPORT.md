# Job 3 report — torso pocketing FEA

**Overall: FAIL.** Job 3 (7075 pelvis) and job 3b (homogenized sandwich pelvis) both fail.

The governing case is LC1, the 33.5 kN chest load on the sternum land. On the refined mesh the land moves 58.5 mm (gate 0.05 mm), the buckling factor is 1.00 (gate 3), and the post ligament is 1576 MPa (SF 0.16 against 257 MPa). The raw von Mises peak is a singularity at the post-to-pelvis corner. Mode 1 under standing weight is 64.1 Hz (gate 80 Hz).

## Gates

| Gate | Limit | Job 3 | Job 3b |
|---|---|---|---|
| SF, bulkhead and posts | ≥ 2 on 257 MPa | FAIL (LC1 ligament SF 0.16) | FAIL (LC1 ligament SF 0.19) |
| SF, pelvis | ≥ 2 on 271 MPa (job 3) or sandwich Sy 60 (job 3b) | FAIL (LC1 SF 0.22) | FAIL (LC1 SF 0.09, LC2 SF 0.87) |
| SF, partition | ≥ 2 on CFRP Sy 450 (yaml). 320 and skin 300 shown beside it | FAIL on LC1 at all three | FAIL on LC1 at all three |
| Land deflection, LC1 | ≤ 0.05 mm | 58.5 mm FAIL | 72.8 mm FAIL |
| Buckling factor, LC1 | ≥ 3 | 1.00 FAIL | 1.00 FAIL |
| Mode 1, LC6 | ≥ 80 Hz | 64.1 Hz FAIL | 64.4 Hz FAIL |
| Force balance | residual under 2% or 5 N | pass, under 0.05 N | pass, under 0.05 N |

LC3, LC4 and LC5 pass every stress gate on both variants. They do not carry the verdict.

## Mass

Mesh mass at 6 mm (tonne/mm³ × mm³). The 4 mm mesh matches to 0.001 kg.

| Part | Allowable | Job 3 kg | Job 3b kg |
|---|---|---:|---:|
| Bulkhead, land, rib | 257 single-path | 1.797 | 1.797 |
| Posts | 257 single-path | 0.189 | 0.189 |
| Pelvis | 271 (job 3); Sy 60 sandwich (job 3b) | 1.855 | 0.469 |
| Partition, CFRP 1 mm | Sy 450; path multi | 0.121 | 0.121 |
| Total | | 3.962 | 2.576 |

A solid pelvis of the same outer box (140 × 260 × 60 mm, 7075) is 6.14 kg. The job 3 hollow (6 mm wall) is 1.855 kg. Job 3b replaces that wall with 11 mm of homogenized CF/honeycomb and weighs 0.469 kg, 1.386 kg less. No mass is credited. The gates fail, and job 3b is the yaml screening model (the whole pelvis wall, not the R-127 top and bottom webs).

## Job 3 — safety factors at 6 mm

SF is allowable / vm_struct. vm_struct is the peak outside a fixed 5 mm band on the fixed face, the post junctions, the hole walls, the land step and the rib root. The post ligament is the peak whose centroid sits at 40–100 mm up the post, clear of both ends. That ligament is the stress that converged.

| Case | Bulkhead 257 | Posts 257 | Post ligament | Pelvis 271 | Partition 450 | Land mm | Extra | Case |
|---|---:|---:|---:|---:|---:|---:|---|---|
| LC1 chest 33.5 kN | 0.14 | 0.10 | 0.17 (1503 MPa) | 0.22 | 0.21 | 58.24 | buckle 1.004 | FAIL |
| LC2 side 9 kN | 1.39 | 0.77 | 1.64 (157 MPa) | 1.52 | 2.34 | 2.69 | | FAIL |
| LC3 waist 306 N·m | 246 | 65 | | 38 | 80 | 0.019 | | PASS |
| LC4 pack 858 N | 165 | 152 | | 26 | 24 | 0.071 | | PASS |
| LC5 bosses 35 N | 31 | 288 | | 81 | 17 | 0.019 | | PASS |
| LC6 stand 652 N | 1375 | 358 | | 89 | 87 | 0.015 | 64.5 Hz | FAIL |

Partition SF against 320 MPa (multi-path metal number) and against the R-128 skin 300 MPa [EST] is lower by 450/320 and 450/300. LC1 still fails (SF 0.15 and 0.14). LC2 partition SF 2.34 versus 450 becomes 1.67 versus 320 and 1.56 versus 300. The metal parts already fail LC2.

## Job 3b — safety factors at 6 mm

The pelvis allowable in this column is the homogenized sandwich Sy, 60 MPa. The yaml names 7075 hardpoints at 271 MPa. Those nodes are not in the mesh, so a 271 MPa check of the post feet is not this run.

| Case | Bulkhead 257 | Posts 257 | Post ligament | Pelvis Sy 60 | Partition 450 | Land mm | Extra | Case |
|---|---:|---:|---:|---:|---:|---:|---|---|
| LC1 chest 33.5 kN | 0.12 | 0.10 | 0.20 (1266 MPa) | 0.09 | 0.22 | 71.65 | buckle 0.991 | FAIL |
| LC2 side 9 kN | 1.24 | 0.71 | 1.31 (196 MPa) | 0.87 | 2.87 | 3.37 | | FAIL |
| LC3 waist 306 N·m | 244 | 72 | | 21 | 97 | 0.034 | | PASS |
| LC4 pack 858 N | 165 | 190 | | 14 | 33 | 0.085 | | PASS |
| LC5 bosses 35 N | 30 | 307 | | 27 | 17 | 0.024 | | PASS |
| LC6 stand 652 N | 1411 | 502 | | 49 | 120 | 0.018 | 64.4 Hz | FAIL |

LC2 on the sandwich wall (SF 0.87) is the same side-wall failure as the R-127 hand calc. LC3, LC4 and LC5 stay under Sy/2 on that wall.

## Convergence

Governing case: LC1. Production mesh 6 mm (yaml). Refined mesh 4 mm. A 3 mm mesh (588,225 nodes, 337,789 tets) aborted in CalculiX with 0xC0000005 before a result was written. It is not used.

Job 3, LC1, 6 mm → 4 mm (126,082 → 288,896 nodes):

| Quantity | 6 mm | 4 mm | Change |
|---|---:|---:|---:|
| Post raw peak, MPa | 4544 | 5417 | +19% |
| Post ligament, MPa | 1503 | 1576 | +4.8% |
| Land deflection, mm | 58.24 | 58.51 | +0.5% |
| Buckling factor | 1.004 | 0.995 | 0.9% |
| Mode 1, Hz (LC6) | 64.50 | 64.13 | 0.6% |

The raw peak is a singularity. Its centroid moved from (51.1, 109.1, 3.3) mm to (51.3, −109.3, 2.5) mm, onto the front outboard corner of a waist post at the pelvis top. The post section is x = 40–52 mm, y = ±(90–110) mm, z = 0–140 mm, so the corner is about (52, ±110, 0). The peak swaps between the +Y and −Y posts as the mesh changes. A second singularity sits where the post enters the bulkhead plate, about (40, ±90, 140) mm: the raw peak there rose from 2578 MPa to 2918 MPa (+13%), centroid (41.0, −90.0, 141.7) mm on the 4 mm mesh.

Job 3b LC1, 6 mm → 4 mm (138,303 → 337,053 nodes): raw post peak 5518 → 6396 MPa (+16%) at the same pelvis corner; ligament 1266 → 1322 MPa (+4.4%); land deflection 71.65 → 72.76 mm (+1.6%); buckling factor 0.991 → 0.998 (0.7%).

Deflection, buckling factor, mode 1 and the post ligament are the converged numbers. They all miss their gates. The 58 mm land motion is about five times the 12 mm bulkhead thickness, so the linear MPa values are not a small-strain design stress. The displacement gate fails on its own.

## Method

Parametric solid from `fea_job3.yaml` / `fea_job3b.yaml`, gmsh OCC, one conformal tet mesh, CalculiX 2.23 C3D10 (straight-sided). Units mm, N, MPa, tonne. `ccx` is the conda-forge build in the micromamba env `ccx` (CalculiX 2.23, Spooles, 16 threads). The deck is linear static. LC6 adds a preload frequency step (3 modes). LC1 adds a linear buckling step (2 factors); the reported factor is the smallest positive one.

Posts are the same fused solid as the bulkhead. Elements whose corner centroid lies in a post (x = 40–52 mm, y = ±100 ± 10 mm, z = 0–140 mm) are a separate elset so the 257 MPa post allowable is scored on its own.

Only the static step is read for stress, displacement and reactions. Frequency-mode and buckling-mode stresses are mass-normalized and are not the load stress. A patch test (10 × 1 × 1 mm bar, 100 N, E 70 GPa) recovered mean σxx 100.0 MPa, reaction −100.0 N, and the fixed-free bending frequency within 0.3% of the analytical 8064 Hz.

Every case balances: the support reaction matches the applied force to better than 0.05 N, including 33,500 N on LC1.

A fixed-free beam estimate for the two posts alone (I = 5760 mm⁴, moment arm from the land at z = 220 mm) is several GPa at mid-height and a deflection of tens of millimetres. The FEA ligament is lower, near 1.5 GPa, because the partition is offset in x and shares the moment. The order of magnitude matches. A rocking estimate of the bulkhead on the posts is about 75 Hz. The computed mode is 64 Hz.

## Assumptions

- The only support is the pelvis bottom face, as in the yaml (`fixed: pelvis_bottom`). The CFRP shell, pack rails and hip brackets are not in this mesh.
- 7075 is isotropic, E 70 GPa, ν 0.33. Single-path allowables are the yaml values (bulkhead 257, posts 257, pelvis 271). Partition uses CFRP Sy 450 because the part has no allowable field. 320 MPa is the multi-path metal number and is not the partition field in the yaml.
- Job 3b pelvis is one homogenized solid, E 9.1 GPa, ν 0.30, ρ 0.42e-9, Sy 60. Hardpoint inserts at 271 MPa are not modeled. Peaks in the pelvis wall next to the posts are sandwich-element stresses, not a 7075 bearing check.
- Holes are empty. Bolt preload and bearing are not applied. Peaks on the hole wall are inside the 5 mm exclusion.
- The 5 mm band does not remove the post-root singularity. The ligament cut (z = 40–100 mm) does. That is why the ligament is the reported section stress.
- Linear geometry. At 58 mm the assumption is past its range. The run was not repeated with NLGEOM. A geometric-nonlinear rerun would not bring 58 mm under 0.05 mm.
- No fatigue gate is in the yaml. Goodman was not scored.

## Files

- `modules/torso/fea_job3.py` — geometry, C3D10 deck, ccx parse, gates
- `modules/torso/fea/job3/results.json` — job 3 at 6 mm, plus the 4 mm convergence block
- `modules/torso/fea/job3b/results.json` — job 3b at 6 mm, plus the LC1 4 mm block
- `torso_r1.step` in each output directory — the gmsh solid the mesh was built on
