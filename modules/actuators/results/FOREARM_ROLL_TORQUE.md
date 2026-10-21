# Robot Lab job1 "forearm-roll" torque (566–773 N·m vs CSG-25 369) — Actuators D81, 2026-10-21
Script: `actuators/forearm_roll_torque.py` → `results/forearm_roll_torque.json`. Sources: HD CSF/CSG catalog (`datasheets/hd_csf_csg_catalog.txt` Table 3 ratings, Table 6 ratcheting, Table 8 OD/length, component weight row), HD SHG-2UH/2SO engineering data (`hd_shg_2uh_engineering.pdf` Tables 13.2/15.1, SHG-40), IKO CRB catalog (l.802–804), job1 `modules/design/fea/job1_pad_r8/REPORT.md` + `results.json`, RULINGS R-119/R-120/R-121, Arms R13.

## 1. Is the load case credible? Which joint?
- **It is not the forearm roll.** Job1 (R-079) is the **shoulder-pad side-fall** FEA: 9.17 kN at 15° on the pad (Fn 8.86 kN, Fs 2.37 kN), reacted at the **shoulder_roll** output (CRBH 6013 A, distal arm 6.05 kg). Mx is the spin moment about the **shoulder_roll** axis (CSG-25-100). The D76 wrist roll (elbow end, CSG-14) carries none of it; nothing in the forearm or the 285 mm cap is involved.
- **The line of action misses the roll axis** by the pad offset: Mx = Fn × 0.064 m = 566 N·m (axial shear), plus Fs × Y 87 mm = 773 N·m (downward shear). So it is a lever-arm case, and the load is real for that geometry (fall impact, credible).
- **That geometry is superseded.** R-120/R-121 (Arms R13) moved the pad centre to Z −20 on a 7075 stand-off with a CRBH 7013 A: Mx raw **321 N·m** (15° case, R10 core), 239 at μ 0.15 (not credited). R-120 already says job1's Z −64/6013 case "must not run"; the a556d44 numbers are the R8B geometry.
- On the adopted geometry: CSG-25-100 SF at fault ×1.05 = 369/337 = **1.09** (R-120 quotes 1.10); ratcheting 650 → 1.93. Momentary peaks are count-limited (catalog: N = 1.0e4 / (2·n/60·t)); fall events are few, so OK. On the job1 geometry it **fails** both momentary (0.45–0.62) and, at 773, ratcheting (650).

## 2. Option (a): bigger gear (catalog, per gear; Δ vs CSG-25-100, pair = 2 shoulder_roll joints)
| gear | rep. peak | mom. peak | ratchet | mass kg | OD×B mm | Δ mass pair | ΔOD / ΔB | SF@773 | SF@566 | SF@321 |
|---|---:|---:|---:|---:|---|---:|---|---:|---:|---:|
| CSG-25-50 | 127 | 242 | 580 | 0.42 | 85×37 | 0 | 0/0 | 0.30 | 0.41 | 0.72 |
| CSG-25-80 | 178 | 332 | 880 | 0.42 | 85×37 | 0 | 0/0 | 0.41 | 0.56 | 0.99 |
| **CSG-25-100 (now)** | 204 | 369 | 650 | 0.42 | 85×37 | — | — | 0.45 | 0.62 | **1.09** |
| CSG-25-120 | 217 | 395 | 610 | 0.42 | 85×37 | 0 | 0/0 | 0.49 | 0.66 | 1.17 |
| CSG-32-50 | 281 | 497 | 1200 | 0.89 | 110×44 | +0.94 | +25/+7 | 0.61 | 0.84 | 1.47 |
| CSG-32-80 | 395 | 738 | 1800 | 0.89 | 110×44 | +0.94 | +25/+7 | 0.91 | 1.24 | 2.19 |
| CSG-32-100 | 433 | 841 | 1300 | 0.89 | 110×44 | +0.94 | +25/+7 | 1.04 | 1.42 | 2.50 |
| CSG-32-120 | 459 | 892 | 1200 | 0.89 | 110×44 | +0.94 | +25/+7 | 1.10 | 1.50 | 2.65 |
| CSG-40-50…120 | 523–802 | 892–1530 | 2300–3600 | 1.70 | 135×53 | +2.56 | +50/+16 | 1.10–1.89 | 1.50–2.57 | 2.65–4.54 |
- SHG (hollow units) have the **same TR/TM** as CSG at each size/ratio (SHG Tables 13.2/15.1) and are heavier as units incl. output bearing: SHG-25-2SO 1.31, SHG-32-2SO 2.9, SHG-40-2SO 5.1 kg vs CSG component + CRBH 7013 A = 0.80 / ~1.3 [EST] / ~2.1 [EST]. No torque gain; rejected on mass.
- Housing growth for CSG-32 [EST, cad_mass.py rule: OD + 2·wall]: +25 mm dia, +7 mm length, ≈ +0.10 kg/joint housing → **≈ +1.1 kg pair** total. Envelope is the shoulder, not the forearm cap (285 mm unaffected). Against a reserve of about −0.89 kg (R-121), not affordable and not needed at Z −20.
- Ratio change within CSG-25 (120) gives +7% momentary at zero mass but needs a motor speed check (shoulder_roll 148 N·m peak need / speed); not needed.

## 3. Option (b): limiting the torque
- **Slip clutch / torque limiter:** Arms cites R-057 clutch candidates at **1.6–4.0 kg** (catalog torque limiters in the 300 N·m class, e.g. R+W SL/ Mayr EAS-compact size range); the CONTRACTS row's "300 N·m slip clutch" has no booked mass. R-120 withdrew the clutch as torque basis. Needed only if Mx > 369/1.05 = **351 N·m**. At 321 it is not needed; cost +1.6–4.0 kg pair-equivalent per joint [cited range via Arms R-057], list price not found [EST].
- **Motor current limit + backdrivability:** does **not** protect the gear in an impact. The pad torque enters at the output; the flexspline sees it before the motor can slip. Reflected input inertia (CSG-25 0.413e-4 kg·m² × 100² = 0.41 kg·m² plus rotor) makes the gear resist a ms-scale impact; current limit only caps motor-side contribution (148 N·m peak). Useful as a fall-mode setting (drive to low-current/compliant on fall detect, Controls) but gets no gear credit.
- **Mechanical stop / bypass path:** an end stop only acts at ROM ends; the pad impact can occur at any roll angle (tuck B roll 0), so a stop does not bypass the gear. The real bypass is geometry: put the pad force line through the roll axis (R-120 stand-off, Z −64 → −20). Fully on-axis (Z 0) leaves Fs × Y ≈ 1.81 kN × 0.102 ≈ 185 N·m [EST, R10 Y 102.3].

## 4. Option (c): load-case change (Controls/Arms)
- Fall strategy that lands on the pad with the arm at roll 0 and pitch tuck B is already the basis. A Controls fall-mode (compliant roll, low current) and a pad slip skin (μ ≤ 0.15, Materials G5 test) cut Mx to 239 N·m (SF 1.47). Not credited until measured (R-119/R-120).

## 5. Output bearing (same loads)
| bearing | case | s0 (gate ≥ 2.0) |
|---|---|---|
| CRBH 6013 A, C0 24.3 kN, job1 Z −64 | axial e0/e10, down e0/e10 | 1.45 / 1.29 / 2.63 / 2.09 — **FAIL** axial |
| **CRBH 7013 A, C0 27.7 kN, R-120 Z −20** | e0 / e5 / e10 | **2.31 / 2.16 / 2.04 PASS** |
A bigger gear does not change bearing s0 (the CRBH carries the moment). CRBH 8016 A (C0 43.4 kN, 0.74 kg) stays the R-120 fallback.

## 6. Recommendation
- **Keep CSG-25-100 + CRBH 7013 A on the R-120/R13 geometry. No gear change, no clutch.** Mass Δ **0** beyond R-121's booked +0.271 pair; cost 0 (HD prices not public; [EST]).
- Job1's 566–773 N·m is the superseded Z −64 geometry and is mislabelled "forearm roll"; it is not a new case.
- Remove the unbooked "300 N·m slip clutch" from the shoulder_roll contract row and "(+ clutch, TBD)" from its envelope (P-055), per R-120.
- Gate: Job 8 add-on FEA (R-120 geometry) must show Mx ≤ **351 N·m** (369/1.05). If it shows more: first fallback CSG-25-120 (395 → ≤ 376 N·m, 0 kg, motor speed check); second CSG-32-100 (+≈1.1 kg pair [EST]); a clutch (1.6–4.0 kg) last.
