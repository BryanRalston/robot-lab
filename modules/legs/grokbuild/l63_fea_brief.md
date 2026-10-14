# L63-R 3D FEA brief: A38 femur collar, 8-hole tube (G3 gate, R-115)
Owner RL Legs. Runs on Grok Build, heavy compute on the bryan PC. Inputs: `results/a38/CROSS_PIN_BACKUP.md` (L63-R), `cross_pin_backup_l63r.json`, `grokbuild/fea_retain.py` (bond geometry), `grokbuild/fea_tet.py` (materials).

## Geometry
- Tube: 7075-T6 ø50 × 1.2. Collar: 7075-T6 ID 50.20, wall 6, L 34 (z 0–34). Bondline: EA 9396, 0.10 mm, E 2500 [EST as fea_retain]. Sleeve: 47.6/43.6 × 34.
- **First, confirm the tube's z extent from the CAD.** The model assumes z −12…46. If the tube is flush (end at z 0), stop and report: the 720 MPa basis is void.
- Holes: 8 × ø7 H7 radial, through collar, tube and sleeve. Row A at z 8.25 (θ 0/90/180/270°), row B at z 25.75 (θ 45/135/225/315°). Pins: 42CrMo4 ø7 m6, bonded (no interference, no pin preload).
- Mesh: quadratic tets, ≥ 4 elements through the 1.2 mm wall at the holes, hole-edge size ≤ 0.3 mm. Do a convergence check (2 levels, peak change < 5 %).

## Case 1: walking fatigue, bond intact and bond failed
- Load: Fw = 0.52 × 8763.86 = 4557 N axial, plus the Actuators D46 walking moment and torsion at the collar if they're available (state them if used). Fully reversed, per fea_retain.
- Bond failed: no bond elements, load through the pins only. Bond intact: bonded contact.
- Output: max principal and von Mises at each hole edge in the tube. **Pass: SF ≥ 1.4 against 160 MPa (7075 fatigue, MATERIALS_DB)** at the worst hole, plus hole-to-hole interaction (rows A–B). The hand estimate is 1.41 [EST, coupon Kt 2.909].

## Case 2: collar hoop stress from the fit
- H7/m6 on ø7: worst-case interference +0.015 mm (m6 max +0.015 / H7 min 0) [EST, ISO 286]. Model the pin–hole contact with that radial interference (pin in the collar and tube), at 23 °C and 95 °C (ΔT on steel vs 7075).
- Also check the collar hoop stress at the bond from the adhesive cure shrinkage/CTE mismatch at 95 °C (7075 23.6e-6, steel 11.5e-6).
- Output: peak hoop stress at the collar and tube hole edges, and the contact pressure. Pass: static hoop < 480/1.5 = 320 MPa; adding the case 1 alternating stress must keep fatigue SF ≥ 1.4 (Goodman, mean = fit stress).

## Case 3 (optional, cheap): static fault 29.6 kN bond failed
- Bearing at the tube holes ≤ 720/1.5 = 480 MPa average, and report the peak.

## Report
Write `results/a38/L63_FEA_G3.md` + json: mesh stats, convergence, SF per case, and pass/fail against G3. Label anything assumed [EST].
