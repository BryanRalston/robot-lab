# Grok Build brief: FEA of the 4.84 kg leg structure (Legs, round 2)

`results/r2/structure_mass.md` cuts the structure 6.13 → 4.84 kg (both legs). Its margin against the R-001 4.90 kg budget is +0.06 kg. Several parts are marked "FEA required" because they are pocketed or ribbed with no v3 FEA case behind them.

## Parts
- femur upper lug, pocketed 20 %
- knee clevis, pocketed 15 %
- knee tongue, pocketed 15 %
- ankle fork, pocketed 15 %
- foot plate, ribbed: 4 mm skin + 3 mm ribs at 40 mm pitch, 25 % lighter than v3
- femur and tibia tubes at 1.6 mm wall (analytic SF 8.5 / 5.0; confirm)

## Load cases (65 kg)
- 3 BW vertical on one leg at heel strike, and at toe-off with the CoP at the sole extremes
- knee screw force 7267 N (Actuators RV12x5) through the clevis and the tongue
- hip_pitch screw 9084 N through the lug
- 1.5 × ID peak joint torques (results/r2/requirements.md)
- a fall case at 6 BW

Material: 7075-T6 (yield 503 MPa, fatigue 159 MPa at 5e8 cycles).

## Acceptance
- SF yield ≥ 2 on the fall case.
- SF ≥ 3 at 3 BW.
- Goodman SF ≥ 1.5 for walking cycles.
- Final mass per part, and both-legs total ≤ 4.90 kg.
- If a part fails, report the minimum added mass that fixes it.

## Inputs
- v3 CAD/FEA scripts in v3/ (parametric solids)
- modules/legs/structure.py (mass basis)

## r3 update (2026-10-13)
`structure_check_r3.py` → `results/r3/structure_check.md` used hand methods (lug net tension with Kt 3, bearing, shear-out; foot as a beam section). It is not FEA.
- Clevis, tongue, lug and fork pass. Minimum SF is 3.44 (fork walls, 3 BW).
- The open-ribbed foot failed (SF 0.44 fall). The foot is now a closed 18 mm box: 4 mm skins and 4 webs of 4 mm. Hand check gives SF 2.70 fall and Goodman 4.92.

FEA must confirm:
- the closed-box foot, including skin buckling and sole contact pressure
- the hip pivot boss once the pivot bearing exists (bore ø32 assumed)
- the ankle fork with the real pin (ø12 assumed)

Worst ID GRF is from `results/r3/structure_check.json`.

## r4 refresh (2026-10-13), queued behind the 1.2 m/s controller
Box FEA was done with `fea_r4.py`: scikit-fem P2, half models, h 5–6 mm for the foot and 2.5 mm for the clamp. The box OOMs above about 15k P2 tets.
Results so far:
- foot closed box 0.870 kg: p99.9 SF 2.77 (fall 6 BW). The peak, SF 1.56, is singular at the rigid sensor edge.
- thigh clamp 0.237 kg: SF 2.90.

Grok Build to do:
1. Foot at h ≤ 2 mm, with the ankle F/T sensor flange and bolts modelled instead of a rigid face. Add skin buckling and sole contact.
2. Clamp at h ≤ 1.5 mm with fillets drawn, plus a fatigue check at 0.52× fully reversed.
3. Femur hip ring (ø80 seat, OD 96 × 25) under the D27 bearing loads (12.4 kN + 192 N·m).
4. Femur and tibia at 1.2 mm wall: 3 BW and fall, local buckling and denting.
5. Clevis, tongue and fork with real pin sizes.

Acceptance: SF ≥ 2 fall, Goodman ≥ 1.5, total M2 line ≤ 4.85 kg (results/r4/structure_m2.md).

## r5 additions (R-020 A1')
6. **Femur tongue with Ø35 press-fit** (OD 55 × 27, |y| ≤ 13.5, plus neck to the femur collar; `results/r5/structure_r5.json`).
   - Model the 16MnCr5 shaft Ø35/Ø30 with 0.141 mm diametral interference: contact with friction μ 0.15, or an equivalent 60 MPa pressure.
   - Loads: 10.06 kN + 192 N·m pivot load (D32 bearing reactions 9.1 kN per needle at max), one-screw fault, 6 BW fall.
   - Check hoop plus load stress (hand: 142 MPa hoop, SF 3.55), contact gapping under the moment, and fretting-relevant micro-slip. Repeat at +60 K (interference −0.025 mm).
7. **Thigh clamp retention:** collar (bonded, 0.10 mm DP490 layer as a cohesive or tied layer with E ≈ 2–3 GPa [EST]), internal sleeve 47.6/43.6 × 34, and **2 cross-pin holes Ø6 through collar, tube and sleeve**.
   - Cases: 8.76 kN axial + 2.39 kN transverse (both screws max), one-screw fault (313 N·m), 13.1 kN proof load.
   - Report: bond shear peak at the collar ends (hand average 1.64 MPa; allowable 11.5 at 23 °C and 4.75 at 82 °C), and Kt at the pin holes in the 1.2 mm tube under walking fatigue (0.52×) with bond intact and with bond failed (hand bearing 114 MPa, SF 4.41).
Acceptance is unchanged: SF ≥ 2 fall, Goodman ≥ 1.5, at 66.5 kg loads.
