# L69 — review of G3 hip-pitch lever FEA FAIL (job 2, 334e848)

Source: `modules/actuators/fea/job2_g3_lever/REPORT.md` + `field_rc_*.npz` (light post-processing on the box, no re-solve).

## 1. The corner
- Location (finest mesh, case sym_phi+60): (-15.65, 38.61, -10.03) mm — the **upper arm/web edge at |y| = 38.5**, where the arm top face (z ≈ -10.7, arm x ±15) meets the hub end face at |y| = 38.5 (hub spans x ±28.5, z −50…+29 at |y| = 36). The STEP has a straight sharp re-entrant edge here (REPORT "Model": no fillet radius). Same edge exists at both |y| = +38.5 / −38.5.
- It is **in the lever STEP** `modules/actuators/cad/hip_pitch_lever_r031_mw_b30_d36_RC.step` (owner: **RL Actuators**), not in the Legs interface. Note: the L47 brief already demands "≥ R8 at the web/arm junction … as in RC" — the RC STEP does not carry that R8 on the upper edge (only the lower blends at z ≈ −27 have R8). CAD/brief mismatch.
- Mesh artifact: yes. Peak 168.9 → 198.3 → 246.6 MPa (+17%, +24%) at a fixed point while p99.9 stays ~105–121; that is the r^(λ−1) re-entrant-corner singularity, not a physical stress. The element max has no meaning on a sharp edge.
- Near-field from the saved fields (case sym_phi+60, median von Mises of nodes in shells around the peak, design load 4542 N/pin):

| shell (mm) | L1 h4 | L3 h2 | 
|---|---:|---:|
| 0–1 | 95.9 | 99.8 |
| 1–2 | 70.6 | 78.7 |
| 2–3 | 50.9 | 68.5 |
| 3–5 | 49.8 | 51.9 |
| 5–8 | 47.5 | 36.5 |
| 8–12 | 42.7 | 31.6 |

  (L2 governed by a different case, not comparable.) The 3–5 mm shell agrees between L1 and L3 within 4%: **σ_nom ≈ 50 MPa design [EST]** → walk amplitude 50 × 2030/4542 = **22.4 MPa [EST]**. Shell medians include sub-surface nodes, so as a sensitivity I also carry σ_nom,a = 30 MPa [EST] (≈ +35%).
- Secondary: L2's global peak (221 MPa, (-12.8, -50.6, -51.9), sym_phi-30) and the b35 peak (-12.6, -50.1, -52.3) sit on the **lower arm edge** near |y| ≈ 50, z ≈ −52 — also sharp, needs the same treatment.

## 2. Fillet sizing (Peterson)
- q = 1/(1 + a/r), Peterson a = 0.025 in = 0.635 mm for aluminium alloys (Pilkey & Pilkey, *Peterson's Stress Concentration Factors* 3rd ed., §1.9 eq. 1.53; Shigley 9th ed. §6-10) [cite from handbook memory, not re-read this session].
- Kt: shoulder fillet in bending, flat bar, D/d ≈ 2 (hub depth ~80 / arm depth ~41.7 mm from the mesh), Peterson chart 3.4 / Shigley Fig. A-15-6 read-offs [EST ±0.1]:

| r (mm) | r/d | Kt [EST] | q | Kf | σa = Kf·22.4 | σa @ 30 nom |
|---|---:|---:|---:|---:|---:|---:|
| 1 | 0.024 | 2.6 | 0.61 | 1.98 | 44 | 59 ✗ |
| 2 | 0.048 | 2.0 | 0.76 | 1.76 | 39 | 53 |
| 3 | 0.072 | 1.85 | 0.83 | 1.70 | 38 | 51 |
| 5 | 0.12 | 1.65 | 0.89 | 1.58 | 35 | 47 |
| 8 | 0.19 | 1.45 | 0.93 | 1.42 | 32 | 43 |

- Required Kf ≤ 58/22.4 = 2.59 (≤ 1.93 on the sensitivity nominal) → **R ≥ 2 mm is the hand-calc minimum [EST]; specify R8** (Kt ≈ 1.45, Kf ≈ 1.42, σa ≈ 32 MPa [EST], margin ~1.8; also matches the L47 R8 rule and the existing lower blends). Local thickening is **not needed**.
- Mass: added area (1 − π/4)·r² × 30 mm arm width × 2.81 g/cm³ per edge. R8: 13.7 mm² × 30 = 412 mm³ → 1.2 g/edge, 2 edges/lever → **+2.3 g/lever, +4.6 g robot [EST]** (+ same again if the lower edges get R8: ≈ +9 g robot total [EST]).
- Hand calc is a sizing screen only; the converged FEA is the gate.

## 3. Interface fit (R8 on the upper edge, fills y 38.5→46.5, z −10.7→−2.7, x ±15)
- Bearing seats (r 21, |y| 13.5…33.5): fillet starts at |y| = 38.5, 5 mm axially clear. OK.
- Pin bores (|y| > 62.5): > 16 mm away. OK.
- Envelope: fillet radius from the y axis ≤ √(15² + 10.7²) ≈ 18.4 mm < r ≤ 34 envelope; |y| bounds unchanged. It is a fill of a concave corner, so it is **not a subset of the RC body** — the L47 "subset of RC" rule needs an explicit exemption for fillets inside the RC convex hull/bounding envelope. ID fairing: no growth of bounding |y|/r, so the fairing is unaffected.
- Not verified here (needs the models): RV12 rod sweep (today 1.94 mm, ≥ 1.0) and femur tube (today 11.0 mm at +40°, ≥ 10). The fillet is on the arm top near the hub; must be re-run in `lever_r031.py` check 3 and `lever_l35_model.py`. Open.

## 4. Recommendation
Fold into L47: the L47 brief now has a **candidate 0 = RC + R8 upper (and lower) arm/web edge fillets**, run first at G3's mesh ladder with the same convergence rule (< 5 % over the last two levels). Candidate 0 passing = the G3 pass, so no separate G3 job is queued; shape-opt candidates then carry fillet radius as a variable with min R5 (R8 nominal). Needs Arbiter agreement to replace the G3 gate; if refused, run candidate 0 alone as the minimal G3 re-run (same BRIEF.md, STEP with R8 fillets, nothing else changed).
Actuators must add the fillets to the lever STEP (their file).
