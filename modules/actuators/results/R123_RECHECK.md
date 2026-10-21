# R-123(a) re-check of Actuators stress results against 7075-T6 Sy 480 / static allowable 320 MPa (D84, 2026-10-21)
Fatigue basis unchanged (R-123: Se 87 stands). Briefs updated: `GROKBUILD_lever_fea_r031.md` (G3) and `GROKBUILD_housing_pocket_fea.md` (G4): E 70, Sy 480, Su 560, static 320, overload (Sy/1.2) 419 → 400. Endurance and fatigue values unchanged. `cad_mass.py` lever SF basis 503 → 480 (`SY_7075`); re-run changes only the two SF values below (STEP outputs unchanged, regenerated files reverted).

| result | source | peak MPa | was | now (Sy 480) | status |
|---|---|---:|---|---|---|
| hip_pitch lever crossbar (hand) | cad_mass.py | 240 | SF 2.09 | **SF 2.00** | pass (< 320) |
| knee lever crossbar (hand) | cad_mass.py | 192 | SF 2.62 | **SF 2.50** | pass |
| knee lever r47.5 longer crossbar | DECISIONS l.410 | 208 | SF 2.42 | SF 2.31 | pass |
| hip lever needle hub, max (h ~3.5) | DECISIONS l.163 | 237 / hub 293 | SF 2.13 / 1.72 | 2.03 / **1.64** | pass, but unconverged |
| hip lever arm-root, h 3.2, no fillet | DECISIONS l.164 | 343 | already over 335 | **FAIL** (> 320) | superseded geometry (fillet added); L47 (Legs) is the live lever |
| hip lever needle, h 4, unfilleted | O13 report / `PROOF_TEST_hip_lever.md` | 332 | SF 1.51 (pass) | **SF 1.45 — FAIL** | in the 320–335 band → reopened per R-123; PROOF_TEST must stop citing it and use the G3/L47 converged result; its cert line "Sy ≥ 503" → 480 |
| thigh clamp tube hoop, clamp-only option | DECISIONS l.300 | 378 | SF 1.06 | SF 1.01 (incl. scatter) | already rejected (bond + light clamp adopted, hoop 61 → SF 7.9) |
| housing walls (hip_roll) | DECISIONS l.51 | 14 | — | SF 34 | pass |
| knee trunnion Ø12 / Ø23 boss (D80) | knee_trunnion_bore_r114.json | net 75.7 / 55.1 | on 6061 (Sy 276) | unchanged; 7075 at 480 is higher | pass (6061 basis governs as conservative) |
| knee release body (Job 9 c) | JOB9_KNEE_GEOMETRY.md | — | — | T&R must use 320 for 7075 (JOB9_SPEC lists 503) | flag to T&R file |
**New FAILs vs 320: one** — the h 4 unfilleted needle-lever figure (332 MPa) quoted in `PROOF_TEST_hip_lever.md`. It is superseded geometry, so no live part fails; the proof-test doc needed fixing (done: basis note below). Other scripts still hard-code 503 (`hp_lever_fea.py`, `hp_lever_fea_converge.py`, `clamp_review.py`, `plot_r3b.py`). They are historical; any re-run must set Sy 480.
