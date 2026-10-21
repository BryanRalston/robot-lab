# R-127 option C(b): magnesium actuator housings (Actuators D86, 2026-10-21)
Script `r127_mg_housings.py` → `results/r127_mg_housings.json`. CAD volumes are the CadQuery-measured G4 bodies (`GROKBUILD_housing_pocket_fea.md` §1). The knee twin housing is excluded: it is the thermal-limited part (rev B fins, R-077/R-096), and Mg conducts 57.6 vs 130 W/m·K. No other actuator housing has CAD.

## 1. Alloy choice (cited)
| alloy | ρ g/cm³ | E GPa | Fty / Ftu MPa | basis | k W/m·K | 120 °C / creep | source |
|---|---:|---:|---|---|---:|---|---|
| **Elektron 43 (WE43C) extruded/plate T5** | 1.83 | 44.1 | **195 / 303 A-basis** (typ 243/352) | **MMPDS-08 A/B-basis** | 57.6 | stable to 250 °C | Luxfer DS-490 (luxfermeltechnologies.com, DS-490-Elektron-43-0526.pdf) |
| WE43B cast | 1.84 | 45 | 172 / 220 min (typ 185/265) | spec min | 51 | to 250 °C, creep data at 200/250 °C | Luxfer DS-467 |
| AZ91D die cast | 1.81 | 45 | 160 / 230 typ; fatigue 70 @ 5e7 | typical | 72 | **poor above ~100–120 °C**: thermally activated creep from 100 °C (SAE 910416); bolt-load loss at 150 °C (SAE 970325) | NADCA A-3-11 |
| AZ80 / ZK60 | ~1.80 / 1.83 | 45 | [EST] ~250/340, ~270/340 typ | no repo source | — | Al-bearing AZ80 creeps like AZ91 | [EST] |
- **Recommended: Elektron 43 (machined from plate/bar).** It has a cited A-basis allowable, which makes it usable even for single-path parts under R-125(b), and it is creep-stable at 120 °C. **AZ91D is rejected**: these housings carry bonded stators at 80–120 °C, and preloaded joints lose clamp by creep (SAE 970325).

## 2. Mass [CALC from CAD volume × density]
| unit | n | 7075 kg | Mg equal-geometry | 7075 seat inserts | Δ/unit A (equal geom + inserts) | Δ/unit B (+25 % volume for stiffness [EST]) | load path |
|---|---:|---:|---:|---:|---:|---:|---|
| hip yaw | 2 | 0.2145 | 0.1397 | +0.015 | −0.060 | −0.025 | single (all leg load through it) |
| hip roll | 2 | 0.2264 | 0.1475 | +0.015 | −0.064 | −0.027 | single |
| hip-pitch screw body | 4 | 0.1425 | 0.0928 | +0.010 | −0.040 | −0.017 | multi (twin screws; one-screw fault case exists) |
| ankle screw body | 4 | 0.1924 | 0.1253 | +0.013 (seat + GE 12 C eye bush) | −0.054 | −0.023 | multi (twin diff.) |
| **robot, all four** | 12 | 2.221 | | | **−0.625** | **−0.263** | |
| **robot, multi-path only** | 8 | 1.339 | | | **−0.377** | **−0.159** | |
- Not additive with R-122 row 3 pocketing (−0.316) on the same parts: Mg on the pocketed volume gives about −0.54 (A, all four), so row 3 + Mg ≈ **−0.85 combined**, not −0.94.
- Credit now (calc/EST, half): multi-path **−0.08 to −0.19**; all four −0.13 to −0.31. Full after G4-Mg FEA + CAD-measured STEP.

## 3. Hand-calc FEA proxy (G4 load cases; thin wall, Kt where noted)
Allowables: Elektron 43 static **130 MPa** (A-basis 195/1.5, single path, R-125(b)); 162 (typical 243/1.5, multi-path only). Fatigue: no cited R=−1 Se for the product form; the R=0.1 axial 195 MPa max at 5e7 (DS-490) is for bar. I use **Se 42 MPa [EST]** (AZ91 70 × 0.6 for machined, size and reliability, conservative) → amplitude ≤ **28 MPa**.
| case | stress MPa | limit | result |
|---|---:|---:|---|
| hip roll R1, 369 N·m momentary, tube Ø96×2 | τ 13.3, vM 23 | 130 | SF 5.7 |
| hip roll R2, seat 117 N·m + 1944 N | 11.7 | 130 | SF 11 |
| hip roll R3, 204 N·m reversed | vM amp 12.7 | 28 | SF 2.2 |
| screw nut tube Ø41×2, 4542 N | 18.5 | 130 | SF 7 |
| screw nut tube, 2030 N reversed | 8.3 | 28 | SF 3.4 |
| **ankle GE 12 C eye lug, 4542 N, Kt 2.5** | net 56.8, **peak 142** | 130 | **FAIL in Mg**. Keep the eye as a 7075 (or steel) insert/bush (included in the insert line) or move the lug to the 7075 seat insert |
| 2.0 mm walls | — | — | stress is not governing (as for 7075, cad_mass.py l.14); **stiffness/ovality governs** (E 44 vs 70) |
- **Real FEA is needed** for bearing-seat ovality (< 10 µm, the T&R JOB9 criterion), insert bond/pin shear and the cone/neck. **G4 addendum below**; it runs on the bryan PC via Robot Lab, after G4 itself.

## 4. Galvanic and corrosion plan
- Mg is the most anodic structural metal. Steel bearings, 12.9 screws, Ti and even 7075 inserts are all cathodic to it. A small anode against a large cathode is the bad case, so the Mg must be **isolated, not just coated**.
- **Coating:** PEO (Keronite/Tagnite-class) 10–20 µm + epoxy/PTFE sealant topcoat on all Mg surfaces; machine bearing seats into inserts, not Mg. Re-seal the machined faces before assembly.
- **Inserts:** 7075-T7351 (not T6, for SCC) bearing-seat rings and the ankle eye bush, bonded (DP490-class) + 2 dowels, wet-assembled with chromate-free primer (Mg ↔ Al is the mildest couple; Al 5xxx/6xxx inserts are milder still, if the seat stiffness allows).
- **Fasteners into Mg:** thread inserts (Al 7075 Keensert-type [EST]) or through-bolts. Steel 12.9 screws Zn-Ni or Geomet coated with **Al 6061/5052 isolating washers** under heads, wet with sealant. **No Ti fasteners in Mg**: R-123 row 12 Ti screws (rear caps, readheads, drive mounts) must stay off any Mg housing. That removes about 0.010 kg of row-12 saving on these 12 units [EST].
- Bearings: steel outer rings sit in the 7075 inserts, never in Mg.
- Environment: indoor humanoid; add salt-fog/humidity coupons at G5 (Materials).

## 5. Creep and thermal at 120 °C
- Elektron 43/WE43: properties retained to 250 °C and long-term stable (DS-467/490). Housing service is ≤ 120 °C (knee is the hot unit and is excluded). **No creep issue** at the < 25 MPa sustained stress here. AZ91D: creep from 100 °C and bolt-load relaxation, so rejected.
- Thermal path: the stator is bonded to the housing. k 57.6 vs 130 raises the spreading resistance; through a 2 mm wall ΔT is negligible, but axial spreading to the outer surface is worse. **Thermal must re-run the hip and ankle unit ΔT** (hip pitch/ankle copper loss per size.py) before credit.
- CTE 25.6 vs 7075 23.4 vs bearing steel 11.7: the inserts keep the seat fit as today (7075 ↔ steel); the Mg ↔ insert bond sees 2.2 ppm/K × 100 K → negligible shear [CALC].

## 6. Cost [EST]
- Elektron 43 plate/bar: no public price in the repo; **[EST] $40–80/kg** vs 7075 $8–15/kg. 12 billets × ~0.6 kg ≈ $300–600 of material.
- PEO + sealant: [EST] $30–60/part → $0.4–0.7k. Inserts, bonding, dowels: [EST] $20/part.
- **Total delta ≈ $1–2k** for a robot set [EST], within R-126's $2–5k for option (b).

## 7. G4 addendum brief (Mg), bryan PC via Robot Lab, after G4
- Bodies: G4 STEPs (pocketed result if G4 lands first), material Elektron 43 T5 (E 44.1, ν 0.3, ρ 1.83), 7075-T7351 seat inserts bonded (tie) + dowels, ankle eye bush in 7075.
- Cases: the G4 R1–R4 and P1–P3/A1–A4 set unchanged.
- Gates: vM ≤ 130 MPa (Elektron 43 A-basis/1.5) for hip yaw/roll (single path per R-128 classification, `STOCK_GRAIN.md`); hip-pitch/ankle bodies are multi path, but stay at 130 until Materials cites a typical-basis rule for Mg; 7075-T7351 inserts ≤ 239 (ST); fatigue amplitude ≤ 28 MPa [EST Se 42] (Materials to cite an R=−1 value); insert bond shear ≤ 7.7 MPa; bearing-seat ovality < 10 µm; deflection as G4.
- Variants: A (equal geometry) and B (walls ×1.25 at the nut section/seats). Report mass from the solid.
- Same mesh-convergence rules as G4/JOB9.

## Asks (for the Arbiter ruling)
1. Rule hip yaw/roll housings **single path** (they carry all leg load) and allow Mg there only at the A-basis 130 MPa limit, or exclude them (then −0.38 / −0.16 multi-path only).
2. Accept Elektron 43; reject AZ91D for actuator housings.
3. Accept that no Ti fasteners go into Mg (row 12 −0.010 [EST]).
4. Thermal re-check of the hip/ankle unit ΔT and Materials (galvanic plan, Se cite) as gates.
