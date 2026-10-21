# Job 9 (c) knee twin housing: release geometry and material (Actuators D83, 2026-10-21)
For T&R `reliability/JOB9_SPEC.md` (7e55be7) item (c). Script `knee_release_r116.py` → `results/knee_release_r116.json`.

## Answer
- **Body:** use **`actuators/cad/knee_twin_housing_release_r116.step`** (new). It is the **rev B** finned housing (`knee_twin_housing_finned_revb.step`, 0.0703 m² added fin area, kept by Thermal f2da3ab) **plus the R-116 trunnion change**: boss Ø20 → **Ø23**, 7 mm proud (x ±85…92), with a **Ø12 blind bore, 6 mm deep** (D80). One valid solid, 143 034 mm³.
- **Do not use `knee_twin_housing_finned_revc.step`.** In JOB9_SPEC "rev C" means the **trimmed fin set** (R-069, 0.0459 m²), which was withdrawn after Controls a5e14ff (D69C/R077). It is not a newer housing revision, and it has no R-116 boss either.
- **Material: 7075-T6, one-piece machined (housing, web and fins together). Run 7075-T6 as the primary case.** A 6061-T6 run is optional, as a conservative lower bound (D80 already passed the Ø23 boss on 6061: fatigue 1.65, static ≥ 3.6).
- Mass of the release body: **0.402 kg/knee at 7075** (0.386 at 6061).

## Why 7075 (the sources conflict)
| source | says |
|---|---|
| `cad_mass.py` l.77–78 (knee_body_x1, knee_twin_housing) | **7075** — this is the booked mass in the rollup |
| DECISIONS l.65 (lever/knee checks) | 7075 yield |
| CONTRACTS | no material given for the knee housing |
| DECISIONS D69 (l.696, 714), `knee_fins_revb.py`, Thermal D69C/R077 | **fins** 6061, 1.0 mm (density 2.70 used for fin mass) |
| D80 / `knee_trunnion_bore_r114.py` | 6061 for the boss check, "as asked"; it notes 7075 is no worse |
- The booking (cad_mass) is the only source that sets the **housing** alloy; 6061 appears only for the **fins** and as a requested conservative check. The rev B STEP fuses the fins into the housing as one solid, so as modelled it is one part and must be one alloy. **We book 7075-T6 for all of it.**
- Consequence: the fin mass was computed at 6061 density. At 7075 it is 0.0932 × 2.81/2.70 = 0.0970 kg/knee: **+0.004 kg/knee, +0.008 kg robot [CALC]**. That is above the R-066 0.005 freeze, so it is flagged for the Arbiter, not booked. The fins could stay 6061 only as a separate clip-on part. Thermal D69B allowed either. That needs its own interface and thermal contact resistance, so I don't recommend it.
- Thermal: 7075-T6 k ≈ 130 vs 6061 ≈ 167 W/m·K. Fin efficiency for 1.0 × 25 mm fins is ≈ 0.96 at 7075 vs 0.97 at 6061 [CALC, tanh(mL)/mL, m = √(2h/kt), h 12], so the Thermal/Controls rev B results stand.

## Release STEP vs R-116
- The rev B STEP **did not include R-116**. It had the Ø20 boss with **no bore** (probed: solid at x 86–91.5; boundary at r 10). D80 modelled the bore only inside its hand check.
- I generated it (cheap): Ø23 cylinder from x 84 (sunk 1 mm so it fuses fully to the r41 can; the can surface at y ±11.5 is x 84.35) to 92, then a Ø12 × 6 blind bore from the face. Δ volume vs rev B is +6 mm³ (the annulus gain is offset by the bore). The R-116 +0.008 booking stays (that was vs the Ø9-bore L62 baseline).

## Notes for the JOB9_SPEC text (T&R's file, not edited)
- The "Ø12 trunnion bosses grown to Ø23 (D69 rev B note)" line should read: Ø12 bore in a Ø23 boss, R-116/D80.
- Pin loads (3634 N max, 2526 N design, 1682 N walk) match D80/Legs L61.
- The stator bond land is in the body. The 2.0 mm can wall between the bore floor and the stator cavity is the thinnest section near the pins (D80). Mesh ≥ 4 quadratic elements through it.

## R-128/R-132 update (D87)
- Material for job 9 (c): run **7075-T7351 at 211 MPa static / 317 fall (R-132 §2, ST)**, not 320. The part needs ≥ 4.25 in stock (105.1 mm body + stock), above the 4.0 in limit, so the stock form is open: forging or split nut sections (`STOCK_GRAIN.md`). D80 net 75.7 MPa passes 211.
