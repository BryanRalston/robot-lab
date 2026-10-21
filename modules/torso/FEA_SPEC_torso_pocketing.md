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
**Pass:** SF ≥2.0 on yield (7075 503 MPa cited; CFRP [EST] Tsai-Wu ≥2); land deflection ≤0.05 mm at LC1 (≥10× pad stiffness of 0.53 MN/m); no pack-gap closure; first mode ≥80 Hz; buckling factor ≥3.
**Inputs:** `modules/torso/cad/torso_r1.step`, `fea_job3.yaml` (materials and loads above). **Outputs:** `modules/torso/fea/job3/` holding results.json (SF, deflection and mode per LC), pocket map STEP, pocketed mass, and report.md.
**Run:** `cd robot-lab && python modules/torso/fea_job3.py --cfg modules/torso/fea_job3.yaml --out modules/torso/fea/job3`
