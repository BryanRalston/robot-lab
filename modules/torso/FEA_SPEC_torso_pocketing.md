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
