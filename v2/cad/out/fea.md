# v2 FEA (scikit-fem, quadratic P2 tetrahedra, TetGen mesh via meshpy, linear elastic 7075-T6 E=71.7 GPa ν=0.33)

Loads = worst cases from v2/analysis/checks.py: landing 3×BW (BW = 64.3 kg × 9.81 = 631 N) with the checks.py bending levers (femur 0.12 m, tibia 0.10 m, hip lateral 0.10 m). Walking fatigue = 1.3×BW (linear scaling of the same field). Allowables: yield 503 MPa, fatigue ~159 MPa (as in checks.py, typical, not a certified value).

| part | model region | tets / DOF | max von Mises MPa (single element) | 99.5th pct MPa | where (mm, local) | SF yield (landing, p99.5) | SF yield (landing, peak) | SF fatigue (walk) | max disp mm |
|---|---|---|---|---|---|---|---|---|---|
| hip bracket | whole part | 15861 / 80106 | 109 | 45 | [26.7, 34.4, 1208.1] | 11.2 | 4.6 | 8.2 | 0.06 |
| femur | hip-end lug + 150 mm tube | 20352 / 120123 | 95 | 63 | [42.0, 4.6, 824.6] | 8.0 | 5.3 | 5.8 | 0.39 |
| tibia | ankle fork + 150 mm tube | 18154 / 107049 | 77 | 62 | [34.6, 7.5, 130.3] | 8.2 | 6.5 | 6.0 | 0.54 |

Hand check (beam theory, checks.py): femur ~72 MPa, tibia ~75 MPa at the root — FEA agrees within ~10 %.
All SF ≥ 2, so no redesign was needed for strength. FEA did find a real CAD defect: the tibia tube stopped 2 mm short of the ankle fork (solver had a floating body); fixed by extending the tube to the fork and widening the fork to 62 mm.
Limits: peaks sit at sharp re-entrant corners and load-application edges (no fillets modeled) and are mesh-dependent; femur/tibia were modeled at their highest-moment end only (lug/fork + 150 mm tube, cut-face loads = exact resultant). Pin/bearing contact, bolts and welds/bonds not modeled.