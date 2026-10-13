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
