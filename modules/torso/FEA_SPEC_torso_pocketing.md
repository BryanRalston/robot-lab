# FEA job spec (for Bryan's PC via Grok Interface, not the box): torso pelvis/shell pocketing
- **Goal:** cited mass-down for R-069. Pocket the pelvis (1.45 kg [EST]) and the bulkhead web outside the 120 mm shoulder bosses. Keep SF ≥ 2.0 (7075-T6 yield 503 MPa) and G3 fatigue (Goodman, walking 14 600 h).
- **Geometry:** parametric boxes per R1_ARCHITECTURE §1/§9 (no CAD yet). Pelvis 7075 box with 2 × hip brackets 8 × M5 (y ±130) and hip_pitch trunnions.
- **Loads:**
  1. landing 3 BW + 0.10 m moment per hip (CONTRACTS §1c);
  2. side fall: shoulder_F 11.5 kN at 60 mm (v3.json) on the bulkhead, and hip 55 % share on the pelvis;
  3. forward fall: arms tucked (Arms D71 ≤ 550 N·m gate, T-030), loads through pads/bearing, so no hands-first case;
  4. 20 kg carry, waist_pitch 188 N·m.
- **Outputs:** mass after pocketing, peak von Mises per case, fatigue SF, and a mesh convergence check (2 refinements).
- **Expected:** pelvis −0.15…−0.25 kg [EST]. Credit only on the converged result.

## Readiness additions (R-079, high priority)
- **Software / host:** CalculiX or FreeCAD FEM on Bryan's PC via Grok Interface, one session (CHARTER). Not on the box.
- **Material:** 7075-T6, E 71.7 GPa, ν 0.33, σy 503 MPa, σu 572 MPa, fatigue (Goodman) Se 159 MPa at 5e8 cycles [MMPDS-class values; Materials DB to confirm].
- **BCs:** pelvis fixed at the waist_yaw bearing seat. Loads at the hip bracket bolt circles (RBE2 spiders). Bulkhead fixed at the shell bond line; shoulder loads at the 80 mm bolt circles (RBE2).
- **Mesh:** C3D10 tets, global 3 mm, 1 mm at fillets/holes. Two refinements; converged when peak σ changes < 5 %.
- **Pocketing design variables:** web 3–6 mm, ribs ≥ 4 mm, keep ≥ 2d around every bolt (M5/M8), 12 mm full thickness at the shoulder bosses.
- **Pass criteria:** SF ≥ 2.0 on yield in fall cases, ≥ 1.5 in landing; Goodman SF ≥ 1.5 on walking; no buckling (linear eigen, λ ≥ 3).
- **Deliverables:** `modules/torso/results/fea_pocket/` with the summary .md (mass, σ per case, SF table, convergence) + JSON, plots, and the input deck.
**Status: ready to run.**

## FINAL — Job 3, bryan PC (2026-10-21)
**Status: FINAL.** Runs after Legs L47 and the pad case (R-074 queue).
**Geometry (current):** 12 mm 7075-T651 shoulder bulkhead with the 101×101 sternum land and integral 60×6 back rib (R-079/Materials c859e43); 2× shoulder flanges, 80 mm bolt circle, 8×M8 12.9 each side, plus the 22-lead grommets; 4 M4 captive bezel inserts (§25.1, edge ≥2d); 1 mm CFRP partition with the A41 duct; EtherCAT junction board, 4 M3 bosses on the partition cold face, ≥5 mm standoff (R-087); pelvis 7075 and the CFRP shell 2.0 mm [EST laminate]; pack rails.
**Load cases:** LC1 chest pad plateau 22.35 kN ×1.5 = 33.5 kN on the land; LC2 side fall through the shoulder pad/bearing, D71 ≤550 N·m (T-030); LC3 10 kg payload at full reach with 30° lean, waist 204 N·m ×1.5; LC4 pack 8.75 kg at 10 g on the rails; LC5 EtherCAT and bezel bosses at 50 g; LC6 static stand 66.5 kg through the pelvis.
**Pass:** SF ≥2.0 against the per-part allowable (R-128: single-path bulkhead 257, pelvis 271; multi-path 320; 7075-T6 yield 480, UTS 560, E 70 GPa; CFRP [EST] Tsai-Wu ≥2); land deflection ≤0.05 mm at LC1 (≥10× pad stiffness of 0.53 MN/m); no pack-gap closure; first mode ≥80 Hz; buckling factor ≥3.
**Inputs:** `modules/torso/cad/torso_r1.step`, `fea_job3.yaml` (materials and loads above). **Outputs:** `modules/torso/fea/job3/` holding results.json (SF, deflection and mode per LC), pocket map STEP, pocketed mass, and report.md.
**Run (PC):** `pip install gmsh pyyaml` and CalculiX `ccx` on PATH, then `python modules/torso/fea_job3.py --cfg modules/torso/fea_job3.yaml --out modules/torso/fea/job3`. Smoke test: add `--coarse --no-solve`. The script builds the geometry and exports torso_r1.step itself. Parts are fragmented into one conformal mesh (shared nodes); results.json carries SF, land deflection, LC6 mode 1 and the LC1 buckle factor with PASS/FAIL. ccx via conda-forge: `micromamba create -n ccx -c conda-forge calculix`, or pass `--ccx PATH`. Coarse end-to-end run proven on the box (13 s).


### R-128 (9e49b7a) stock, grain and load-path classification (2026-10-21)
| Part | Stock | Grain | Path | Allowable (MPa) |
|---|---|---|---|---|
| Shoulder bulkhead, 12 mm web + 101×101 land + integral 60×6 rib (with posts) | 7075-T651 plate 3.0 in (76 mm) | L along y (span); LT/ST used | **single** (only chest→torso and shoulder→torso path) | **257** (ST 2.501–3.0 in; M8 flange clamp is through-thickness) |
| Pelvis incl. hip/waist hardpoint nodes | 7075-T651 plate 2.5 in (63.5 mm) | L along y | **single** (only legs↔torso path) | **271** (ST, through-thickness hip/waist bolts) |
| Waist ring | 7075-T651 plate 1.5 in [EST] | L along y | **single** (waist torque path) | **271** (ST, ≤2.0 in) |
| Pack rails + latch | 7075-T651 plate 0.75 in | L along x (rail axis) | multi (2 rails) | 320 |
| Partition | CFRP QI 1.0 mm | 0/±45/90 | multi / secondary | skin 300 [EST] |
| Torso shell | CFRP 2.0 mm | QI | multi / secondary | skin 300 [EST] |
| Sternum land inserts, EtherCAT bosses | in the bulkhead / partition | – | carried by the parent | parent |
- Applied in fea_job3.yaml/.py and fea_job3b.yaml as per-part allowables. The script refuses a single-path metal part without one. Drawings state stock and grain as above; if the drawing fixes grain L, the L value may be used only after the R-128 table is checked.


## JOB 3c (supersedes job 3 / 3b gates), bryan PC
- **Config:** `fea_job3c.yaml` (closed pack-bay torsion box + closed sternum box; model_v4 pelvis + 8 mm deck; partition above the pack).
- **Loads/gates:** T&R b1fe48f (CHEST_DESIGN_LOAD.md). LC1a/b/c at 29 kN against the fall allowable; LC1u at 43.5 kN, no rupture; buckling ≥ 1.5; land k ≥ 5.3 MN/m (≤ 5.5 mm); mode 1 ≥ 80 Hz; LC2 per R-127. **The 0.05 mm gate and SF ≥ 2 stacking are deleted** (DIAGNOSIS.md §2).
- **Run:** `python modules/torso/fea_job3.py --cfg modules/torso/fea_job3c.yaml --out modules/torso/fea/job3c`. Mesh 6 mm, then 4 mm for convergence.
- **Box coarse result:** k 19 MN/m, buckling 4.6 and mode 382 Hz pass; LC2 passes; stress SF 0.56–0.86 at junctions (unconverged); +1.43 kg full. See DIAGNOSIS.md §4.
- **Pocketing credit: pulled.** P-148/P-149 on hold.
