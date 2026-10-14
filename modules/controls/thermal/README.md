# A40 / P-029 (R-030): per-joint winding temperature model + torque derate
Owner: RL Controls. Numpy only, light (demo < 10 s on CPU). Files: `winding_model.py`, `test_winding.py`.

## Model
Two nodes per leg joint actuator (the joint's motors are lumped, same convention as `actuators/size.py` and `thermal/r1_budget.py`):
- Winding: `Cw dTw/dt = P_cu − (Tw − Th)/Rwh`; housing: `Ch dTh/dt = (Tw − Th)/Rwh − (Th − Ta)/Rha`.
- `P_cu = nmot·(Tm/Km(Tw))²`, `Tm = |τ|/(ratio·η·nmot)` (`v3/analysis/v3.py` cu_loss); `Km(T) = Km25/√(1+0.00393·(T−25))` (copper α; equals the repo's ×1.4 hot factor at 127 °C).
- Derate (`derate()`): full peak up to **120 °C**, linear to the steady-state continuous torque `tau_cont` (winding held at 130 °C) at **130 °C**, linear to **0 at 140 °C** (fault/torque off).

## Sources
| param | value | source |
|---|---|---|
| motor, ratio, η, nmot, Km, Rm, T_out, housing mass, area_cad | per joint | `actuators/results/sizing.json` (sel) |
| Rth (Rthw-a) | 1.85–2.60 K/W | `v3/analysis/tbm2g.json`; TBM2G manual §9 (`actuators/datasheets/tbm2g_manual.txt`) |
| Rwh = 0.6·Rth/nmot; Rha = 1/(12·2·area_cad) | | `actuators/size.py`, `thermal/R1_BUDGET.md` (rule, [EST]) |
| 130 °C limit, 140 °C (ΔT 100 K at 40 °C) | | `thermal/R1_BUDGET.md`, CONTRACTS rule |
| 120 °C derate start | | P-029 / R-030 |

## Assumptions [EST]
- Copper = 25 % of TBM2G kit mass (no copper mass or thermal time constant in the TBM2G manual) → Cw. Housing capacity = CAD housing mass × Al 896 + 75 % motor mass × 450 J/kgK.
- Ambient 35 °C, open (uncovered) housing; covers (P-022/P-023, +35 K per Thermal) not modelled. Iron loss (+5–7 W hip_pitch/knee per Thermal) not included. Drive losses not included.
- ankle_roll has no CAD housing (cnt 0) → uses ankle_pitch area.
- No forced airflow from walking.

## Key numbers (`python3 modules/controls/thermal/test_winding.py`)
| joint | Rwh / Rha K/W | τ_winding / τ_housing s | τ_cont at 130 °C Nm (peak) |
|---|---|---|---|
| hip_yaw | 1.56 / 1.10 | 21 / 313 | 33 (70) |
| hip_roll | 1.16 / 1.05 | 33 / 365 | 84 (204) |
| hip_pitch | 0.56 / 1.44 | 34 / 770 | 110 (454) |
| knee | 0.56 / 1.44 | 34 / 770 | 83 (345) |
| ankle_pitch | 0.76 / 1.83 | 28 / 931 | 80 (324) |
| ankle_roll | 0.76 / 1.83 | 28 / 912 | 44 (177) |

Demo: WBC r6 1.2 m/s torque trace (`legs/grokbuild/results/walk_trace.npz`, cruise 1.0–4.5 s looped, no derate fed back) for 60 min at 35 °C: **knees reach 120 °C at 9 (R) / 10 (L) min** and would run away to 215–235 °C; hip_pitch 100–102 °C, ankle_pitch 88–89 °C, hip_roll 76–78 °C at 60 min. The WBC trace has knee RMS 96–118 Nm (REPORT.md), above τ_cont 83 Nm, so this gait cannot be sustained on the knee without a lower-torque gait or better knee cooling.

## Interface for the WBC / RL loop
```python
from winding_model import WindingModel
tm = WindingModel(joint_names)            # names like 'l_knee' or 'knee'; leg joints only
Tw = tm.step(tau_applied, dt)             # every control tick, measured or commanded joint torque (N·m)
lim = tm.torque_limits(tau_peak)          # per-joint |τ| limit to use as the QP / action clip
```
- WBC: replace the static R1.2 bounds in the QP torque box with `lim` each tick (1 kHz fine; can update at 100 Hz).
- RL: add `Tw` (normalized (Tw−35)/100) to the privileged obs, apply `lim` as the action torque clip, and penalize Tw > 120 °C. Needs `make_model.py` regen (after job 4) and a retrain (queued after jobs 4–6).
- Hardware: the same model runs on the brain as an observer, corrected by winding NTC / drive temperature when available.

## Gaps for Actuators / Thermal
1. TBM2G copper mass or winding thermal time constant (Cw is [EST]).
2. Housing-to-air: measured or CFD h and fin factor at walking airflow; covered case (J-T1).
3. Iron and drive losses vs speed (Actuators `iron_loss.py` to fold in).
4. Winding limit 130 vs 140 °C decision (Thermal open question).
5. ankle_roll housing area; arm/waist/neck joints not yet covered (needs their motor parameters).
6. Winding sensor: is a thermistor in the TBM2G stator available (needed to correct the observer)?
