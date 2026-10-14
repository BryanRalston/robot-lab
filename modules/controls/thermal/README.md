# A40 / P-029 (R-030): per-joint winding temperature model + torque derate
Owner: RL Controls. v2 (2026-10-14) uses Actuators `THERMAL_DATA_PACK.md` (f205f7b, D69). Numpy only; `python3 modules/controls/thermal/test_winding.py` (~30 s CPU) writes `demo_60min.json`.

## Model
Two nodes per joint actuator; the joint's motors are lumped (convention of `actuators/size.py`, `thermal/r1_budget.py`, `actuators/knee_thermal.py`).
- Winding: `Cw dTw/dt = P_cu(Tw) + P_fe(n) − (Tw−Th)/Rwh`
- Housing: `Ch dTh/dt = (Tw−Th)/Rwh + P_drv(I) − (Th−Ta)/Rha`
- `P_cu = nmot·(Tm/Km(Tw))²`, `Km(T) = Km25/√(1+0.00393(T−25))` ≡ `R(T) = R25(1+α(T−25))`, R155 = 1.511·R25 (pack §4).
- `P_fe = nmot·(a·n + b·n²)`, n = motor krpm (pack §5; 07613D a 1.83 b 0.195; 06013D 1.02/0.058; 06008A 1.56/0; 08508A 1.07/0.489). Frames without a fit (08513D, arm C windings) use the nearest fitted frame scaled by kit mass [EST]. Iron loss sits in the winding node (conservative, same as knee_thermal.py).
- `P_drv`: Elmo Gold Twitter loss vs current amplitude 2/5/13/22/32/44 W at 5/10/20/30/40/50 A (MAN-G-TWI §11.2.1, worst case; Elmo says measured 20–30 % lower). The drive is chassis-mounted on the housing (pack §6), so its loss goes into the housing node.
- **Limits:** derate starts at **120 °C** (full peak torque below that), linear to τ_cont at **130 °C**, linear to 0 at **140 °C** (torque off). **Hard limit 155 °C** (TBM2G manual §1.2.2; Class F inferred) leaves 15 K for observer error and single-phase hot spots.
- **Knee = D69:** 2× TBM2G-08513D + conductive shank path (Rha ×0.5 [EST]). `load_params(knee='07613D')` gives the as-sized knee. `actuators/knee_thermal.py` calls that for its base case: a one-line edit by Controls, with no result change (it reproduces `knee_thermal.json` exactly).
- **PT1000 (code A, pack §2):** optional `WindingModel.correct(i, T_meas)` does a slow complementary correction. The sensor is too slow for peaks, so the I²t prediction stays primary and the derate uses the model.

## Parameters
- Leg actuators: `actuators/results/sizing.json`.
- Motor Kt_hot, R25, Km, kit mass and Rth w-a: `v3/analysis/tbm2g.json` (= pack §4 table, TBM2G manual §9).
- Arms and waist: Arms `R1_ARCHITECTURE.md` mapping + pack §4. Waist 08508A ×1 per joint (O-T2). All CSG ×100, η 0.75 (r1_budget `eta_rot`).

## Assumptions [EST]
- F_CU 0.25 → Cw (the copper mass isn't published; the bench step-heating test will fit it).
- Rwh = 0.6·Rth (no winding-to-housing value in the manual).
- Rha = 1/(12 W/m²K · fins 2 · area). Ambient 35 °C, housing uncovered; the Thermal cover penalty (+35 K) is not modelled.
- Upper-body housing D×L and mass by frame (shoulder_pitch 96×80, elbow 70×75 from r1_budget; others are my estimates).
- Drive loss is worst case with no pulsed-duty uplift. The demo's iron loss uses the mean over `legs/results/walk_1p2.npz` speeds.

## Results (35 °C, open housing; WBC r6 1.2 m/s cruise 1.0–4.5 s looped 60 min, torques not derated)
| joint (motor) | τ_cont 130 °C Cu / Cu+Fe N·m | Tw 60 min, Cu+Fe L/R | Tw 60 min, Cu+Fe+drive L/R | to 120 °C (with drive) |
|---|---|---|---|---|
| hip_yaw (06008A) | 33 / 33 | 47 / 45 | 48 / 46 | never |
| hip_roll (08508A) | 84 / 84 | 79 / 76 | 81 / 78 | never |
| **hip_pitch (2× 07613D)** | 110 / 103 | 113 / 115 | **134 / 136** | **28.5 / 26.9 min** |
| **knee D69 (2× 08513D + shank)** | **141** / 136 | **89 / 92** | 103 / 108 | never |
| ankle_pitch (2× 06013D) | 80 / 73 | 106 / 106 | 118 / 119 | never (1–2 K short) |
| ankle_roll (2× 06013D) | 44 / 44 | 45 / 40 | 49 / 42 | never |

Upper body, τ_cont at 130 °C: waist 83, shoulder_pitch 62, shoulder_roll 62, shoulder_yaw 30, elbow 26, wrist_roll 17 N·m. Static holds (r1_budget torques):
- **elbow 40 N·m:** 120 °C in 0.7 min, 155 °C in 1.3 min. It runs away, consistent with Thermal's FAIL and the P-028 15 N·m limit.
- **shoulder_pitch 61 N·m:** 120 °C in 12.1 min, about 133 °C at 30 min.

## Reconciliation with Actuators (pack §7, knee_thermal.py)
- **Knee D69 τ_cont 141 N·m: matches.** Tw60 is 89/92 °C (Cu+Fe) here vs 87/91 °C in the pack.
- The 1–2 K gap is iron loss: I scale the 07613D fit by kit mass for 08513D (5.8 W per knee), while knee_thermal.py uses the 07613D fit unscaled (4.6 W). Both are [EST].
- The pack's D69 run leaves out drive loss (pack §6 says so). With worst-case Elmo loss in the housing, the knee is 103/108 °C, still below 120.
- **New:** with drive loss, **hip_pitch crosses 120 °C at about 27–29 min and is about 135 °C at 60 min**, and ankle_pitch is about 1–2 K below 120. Before drive loss, hip_pitch was 113–115 °C.
- The ankle is a differential pair. sizing.json lists ankle_pitch and ankle_roll each with 2 motors, so modelling them as separate joints splits one motor pair's heat across two nodes. A combined model needs the Actuators differential mapping (gap 5).

## Interface for the WBC / RL loop
```python
from winding_model import WindingModel, load_params
tm = WindingModel(joint_names)                 # 'l_knee', 'waist_pitch', 'elbow', ... (legs, waist, arms)
Tw = tm.step(tau, dt, omega=joint_speeds)      # every control tick (≥ 10 Hz); omega enables iron loss
lim = tm.torque_limits(tau_peak)               # per-joint |τ| bound for the QP torque box / RL action clip
tm.correct(i, T_pt1000)                        # optional, slow (e.g. 1 Hz) PT1000 correction
```
- **WBC:** replace the static R1.2 torque bounds with `lim`.
- **RL:** add `(Tw−35)/100` to the privileged obs, clip actions to `lim`, and penalize Tw > 120 °C. Wiring waits for the `make_model.py` regen after job 4 and the retrain queued after jobs 4–6.

## Gaps for Actuators / Thermal / Arms / Electronics
1. Copper mass or winding τ (bench step-heating fit, added by Actuators to BENCH_TEST_PLAN).
2. Rwh split and the housing-to-air h; covered case (J-T1); arm and waist housing geometry and mass.
3. Iron-loss fits for 08513D and the arm C windings.
4. Drive mounting and drive loss at the measured (not worst-case) level. hip_pitch now depends on it.
5. Ankle differential mapping (which motor carries pitch vs roll torque).
6. Arms joint-to-motor mapping: the pack lists elbow 06008C and wrist roll 05013C, but Arms R1 lists shoulder_yaw 06008C, elbow 05013C, wrist_roll 05008C. I followed Arms R1; Arms should confirm.
7. Electronics: one analog input per motor for the PT1000.
