# v3 CAD mass and inertia vs v3 catalog rollup

CAD total: **57.3 kg**; catalog-part rollup (v3/analysis): **62.0 kg**; difference -4.7 kg (-7.6 %).

Densities: 7075 2810, CFRP 1550, steel 7850, Ti 4430, PA12 1010 kg/m³. Motors, gears, battery, compute and bearings use catalog/[EST] mass overrides applied over their envelope volume.


| segment | mass kg | COM mm (world, standing) | Ixx Iyy Izz about COM kg·m² |
|---|---|---|---|
| L_foot | 2.25 | [np.float64(17.5), np.float64(130.7), np.float64(49.2)] | [np.float64(0.01206), np.float64(0.02126), np.float64(0.0135)] |
| L_forearm | 1.72 | [np.float64(-0.0), np.float64(282.0), np.float64(1041.8)] | [np.float64(0.00748), np.float64(0.00748), np.float64(0.00117)] |
| L_hand | 0.72 | [np.float64(2.9), np.float64(280.9), np.float64(854.1)] | [np.float64(0.00124), np.float64(0.00094), np.float64(0.00053)] |
| L_hipR | 1.65 | [np.float64(-0.0), np.float64(132.3), np.float64(929.9)] | [np.float64(0.0033), np.float64(0.00287), np.float64(0.00243)] |
| L_hipY | 1.79 | [np.float64(5.9), np.float64(130.0), np.float64(1054.2)] | [np.float64(0.00286), np.float64(0.00385), np.float64(0.00306)] |
| L_pelvis | 1.37 | [np.float64(-0.0), np.float64(130.0), np.float64(1172.9)] | [np.float64(0.00298), np.float64(0.00312), np.float64(0.00206)] |
| L_shank | 2.31 | [np.float64(-34.0), np.float64(130.9), np.float64(375.5)] | [np.float64(0.03622), np.float64(0.03617), np.float64(0.00641)] |
| L_shoulderP | 1.22 | [np.float64(5.2), np.float64(282.0), np.float64(1460.0)] | [np.float64(0.00132), np.float64(0.00168), np.float64(0.00168)] |
| L_thigh | 1.50 | [np.float64(-30.9), np.float64(130.0), np.float64(719.7)] | [np.float64(0.02279), np.float64(0.02613), np.float64(0.00492)] |
| L_upper_arm | 1.59 | [np.float64(-0.0), np.float64(285.3), np.float64(1274.9)] | [np.float64(0.01217), np.float64(0.01185), np.float64(0.00149)] |
| R_foot | 2.25 | [np.float64(17.5), np.float64(-130.7), np.float64(49.2)] | [np.float64(0.01206), np.float64(0.02126), np.float64(0.0135)] |
| R_forearm | 1.72 | [np.float64(-0.0), np.float64(-282.0), np.float64(1041.8)] | [np.float64(0.00748), np.float64(0.00748), np.float64(0.00117)] |
| R_hand | 0.72 | [np.float64(2.9), np.float64(-280.9), np.float64(854.1)] | [np.float64(0.00124), np.float64(0.00094), np.float64(0.00053)] |
| R_hipR | 1.65 | [np.float64(-0.0), np.float64(-119.4), np.float64(929.9)] | [np.float64(0.00312), np.float64(0.00287), np.float64(0.00225)] |
| R_hipY | 1.79 | [np.float64(5.9), np.float64(-130.0), np.float64(1054.2)] | [np.float64(0.00286), np.float64(0.00385), np.float64(0.00306)] |
| R_pelvis | 1.37 | [np.float64(-0.0), np.float64(-130.0), np.float64(1172.9)] | [np.float64(0.00298), np.float64(0.00312), np.float64(0.00206)] |
| R_shank | 2.31 | [np.float64(-34.0), np.float64(-130.9), np.float64(375.5)] | [np.float64(0.03622), np.float64(0.03617), np.float64(0.00641)] |
| R_shoulderP | 1.22 | [np.float64(5.2), np.float64(-282.0), np.float64(1460.0)] | [np.float64(0.00132), np.float64(0.00168), np.float64(0.00168)] |
| R_thigh | 1.50 | [np.float64(-30.9), np.float64(-130.0), np.float64(719.7)] | [np.float64(0.02279), np.float64(0.02613), np.float64(0.00492)] |
| R_upper_arm | 1.59 | [np.float64(-0.0), np.float64(-285.3), np.float64(1274.9)] | [np.float64(0.01217), np.float64(0.01185), np.float64(0.00149)] |
| head | 0.57 | [np.float64(45.6), np.float64(0.0), np.float64(1734.8)] | [np.float64(0.00209), np.float64(0.00246), np.float64(0.00301)] |
| neckY | 0.43 | [np.float64(-0.0), np.float64(0.4), np.float64(1650.0)] | [np.float64(0.00036), np.float64(0.00021), np.float64(0.00036)] |
| pelvis | 3.20 | [np.float64(0.0), np.float64(-0.0), np.float64(1184.9)] | [np.float64(0.03856), np.float64(0.01453), np.float64(0.04396)] |
| torso | 19.55 | [np.float64(1.4), np.float64(-0.0), np.float64(1440.0)] | [np.float64(0.27313), np.float64(0.15681), np.float64(0.24492)] |
| waistY | 1.29 | [np.float64(-0.0), np.float64(8.3), np.float64(1280.0)] | [np.float64(0.00173), np.float64(0.00148), np.float64(0.00173)] |