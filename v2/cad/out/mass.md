# v2 CAD mass and inertia vs budget

CAD total: **58.5 kg**; budget (checks.py final): **64.3 kg**; difference -5.8 kg (-9.1 %).

Densities: 7075 2810, CFRP 1550, steel 7850, Ti 4430, PA12 1010 kg/m³. Motors, gears, battery, compute and bearings use catalog/[EST] mass overrides applied over their envelope volume.

| group | CAD kg (per unit) | budget kg | Δ |
|---|---|---|---|
| foot | 2.36 | 0.90 | +1.46 |
| shank | 2.20 | 3.00 | -0.80 |
| thigh | 1.74 | 2.54 | -0.80 |
| pelvis | 15.88 | 10.90 | +4.98 |
| upper | 29.98 | 40.51 | -10.53 |

| segment | mass kg | COM mm (world, standing) | Ixx Iyy Izz about COM kg·m² |
|---|---|---|---|
| L_foot | 2.36 | [np.float64(13.6), np.float64(100.0), np.float64(58.3)] | [np.float64(0.01572), np.float64(0.02575), np.float64(0.01397)] |
| L_forearm | 1.39 | [np.float64(-0.0), np.float64(282.0), np.float64(1021.2)] | [np.float64(0.00641), np.float64(0.00641), np.float64(0.00073)] |
| L_hand | 0.31 | [np.float64(4.0), np.float64(279.5), np.float64(846.9)] | [np.float64(0.00073), np.float64(0.00064), np.float64(0.0003)] |
| L_hipR | 2.92 | [np.float64(0.0), np.float64(113.3), np.float64(921.3)] | [np.float64(0.00766), np.float64(0.00723), np.float64(0.00744)] |
| L_hipY | 2.39 | [np.float64(-3.2), np.float64(100.0), np.float64(1052.2)] | [np.float64(0.0048), np.float64(0.0054), np.float64(0.00451)] |
| L_pelvis | 1.23 | [np.float64(-0.0), np.float64(100.0), np.float64(1175.8)] | [np.float64(0.00198), np.float64(0.00211), np.float64(0.00129)] |
| L_shank | 2.20 | [np.float64(-35.0), np.float64(100.0), np.float64(384.3)] | [np.float64(0.03391), np.float64(0.03469), np.float64(0.00492)] |
| L_shoulderP | 1.40 | [np.float64(0.5), np.float64(282.0), np.float64(1460.0)] | [np.float64(0.00159), np.float64(0.00182), np.float64(0.00182)] |
| L_thigh | 1.74 | [np.float64(-44.3), np.float64(100.0), np.float64(723.0)] | [np.float64(0.0207), np.float64(0.02459), np.float64(0.00607)] |
| L_upper_arm | 1.76 | [np.float64(-0.0), np.float64(283.0), np.float64(1281.0)] | [np.float64(0.01289), np.float64(0.0127), np.float64(0.00149)] |
| R_foot | 2.36 | [np.float64(13.6), np.float64(-100.0), np.float64(58.3)] | [np.float64(0.01572), np.float64(0.02575), np.float64(0.01397)] |
| R_forearm | 1.39 | [np.float64(-0.0), np.float64(-282.0), np.float64(1021.2)] | [np.float64(0.00641), np.float64(0.00641), np.float64(0.00073)] |
| R_hand | 0.31 | [np.float64(4.0), np.float64(-279.5), np.float64(846.9)] | [np.float64(0.00073), np.float64(0.00064), np.float64(0.0003)] |
| R_hipR | 2.92 | [np.float64(-0.0), np.float64(-118.5), np.float64(921.3)] | [np.float64(0.00718), np.float64(0.00723), np.float64(0.00696)] |
| R_hipY | 2.39 | [np.float64(-3.2), np.float64(-100.0), np.float64(1052.2)] | [np.float64(0.0048), np.float64(0.0054), np.float64(0.00451)] |
| R_pelvis | 1.23 | [np.float64(-0.0), np.float64(-100.0), np.float64(1175.8)] | [np.float64(0.00198), np.float64(0.00211), np.float64(0.00129)] |
| R_shank | 2.20 | [np.float64(-35.0), np.float64(-100.0), np.float64(384.3)] | [np.float64(0.03391), np.float64(0.03469), np.float64(0.00492)] |
| R_shoulderP | 1.40 | [np.float64(0.5), np.float64(-282.0), np.float64(1460.0)] | [np.float64(0.00159), np.float64(0.00182), np.float64(0.00182)] |
| R_thigh | 1.74 | [np.float64(-44.3), np.float64(-100.0), np.float64(723.0)] | [np.float64(0.0207), np.float64(0.02459), np.float64(0.00607)] |
| R_upper_arm | 1.76 | [np.float64(-0.0), np.float64(-283.0), np.float64(1281.0)] | [np.float64(0.01289), np.float64(0.0127), np.float64(0.00149)] |
| head | 0.58 | [np.float64(44.9), np.float64(0.0), np.float64(1684.1)] | [np.float64(0.00219), np.float64(0.00257), np.float64(0.00305)] |
| neckY | 0.36 | [np.float64(-0.0), np.float64(2.8), np.float64(1604.0)] | [np.float64(0.00019), np.float64(0.0001), np.float64(0.00019)] |
| pelvis | 2.80 | [np.float64(-0.0), np.float64(0.0), np.float64(1182.8)] | [np.float64(0.02374), np.float64(0.01192), np.float64(0.02825)] |
| torso | 17.92 | [np.float64(-1.2), np.float64(-0.0), np.float64(1425.6)] | [np.float64(0.26358), np.float64(0.12403), np.float64(0.24479)] |
| waistY | 1.40 | [np.float64(-0.0), np.float64(0.5), np.float64(1280.0)] | [np.float64(0.00182), np.float64(0.00159), np.float64(0.00182)] |
## Reconciliation
Budget items not modeled as solids in the CAD: harness/connectors 2.0 kg, covers/padding 1.5 kg, thermal loop 1.0 kg (= 4.5 kg, from design.py MASS_ITEMS) plus fasteners and driver boards. CAD solids 58.5 kg + 4.5 kg = 63.0 kg vs 64.3 kg budget (−2 %). Per-group differences are mostly bookkeeping (the budget puts ankle actuators in the shank and hip actuators in "upper"; the CAD assigns parts to the body they ride on) — the foot is heavier in CAD (+1.5 kg: F/T sensor, universal cross, actuator rod ends ride on the foot) which matters for swing-leg inertia.
