"""A40 / P-029 (R-030): per-joint lumped winding-temperature model + torque derate.

2-node model per leg joint actuator (all motors of the joint lumped, same rule as
actuators/size.py and thermal/r1_budget.py):
    winding node  Cw dTw/dt = P_cu(Tw) - (Tw - Th)/Rwh
    housing node  Ch dTh/dt = (Tw - Th)/Rwh - (Th - Ta)/Rha
P_cu = nmot * (Tm / Km(Tw))^2,  Tm = |tau_joint| / (ratio * eta * nmot)   (v3/analysis/v3.py cu_loss)
Km(T) = Km25 / sqrt(1 + ALPHA_CU * (T - 25))   (copper R rises with T; repo uses x1.4 'hot' = 127 °C)
Rwh = 0.6 * Rth(TBM2G) / nmot (motors in parallel); Rha = 1 / (h 12 * fins 2 * area_cad)   (size.py, r1_budget.py)
Parameters [EST] are flagged in PARAMS[...]['est'] and README.md.
"""
import json, os
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
ALPHA_CU = 0.00393      # 1/K, copper resistance temperature coefficient (standard annealed Cu)
C_CU = 385.0            # J/kgK copper
C_AL = 896.0            # J/kgK aluminium housing
C_FE = 450.0            # J/kgK lamination steel / magnets
F_CU = 0.25             # [EST] copper fraction of TBM2G stator+rotor kit mass (no datasheet value)
H_AIR, FINS = 12.0, 2.0  # W/m2K, fin factor (size.py; thermal R1_BUDGET.md [EST])
T_AMB = 35.0            # °C, Thermal R1 hot-ambient case
T_DERATE = 120.0        # °C, P-029 derate start
T_LIMIT = 130.0         # °C, TBM2G Tc130 basis (thermal R1_BUDGET.md)
T_TRIP = 140.0          # °C, CONTRACTS rule ΔT<=100 K at 40 °C -> torque off
LEG = ['hip_yaw', 'hip_roll', 'hip_pitch', 'knee', 'ankle_pitch', 'ankle_roll']


def _motor_model(label):
    return label.split(' ')[0][:11]


def load_params(root=ROOT):
    sel = json.load(open(os.path.join(root, 'modules/actuators/results/sizing.json')))['sel']
    mot = json.load(open(os.path.join(root, 'v3/analysis/tbm2g.json')))
    P = {}
    for j in LEG:
        s = sel[j]; mm = _motor_model(s['label']); M = mot[mm]
        n = s['nmot']; area = s['area_cad'] or sel['ankle_pitch']['area_cad']
        m_mot = M['mass'] * n
        Cw = F_CU * m_mot * C_CU
        Ch = (s['housing_cad'] or s['housing_model']) * C_AL + (1 - F_CU) * m_mot * C_FE
        P[j] = dict(motor=mm, nmot=n, ratio=s['ratio'], eta=s['eta'], Km25=s['Km'], Kt=s['Kt'], Rm=s['Rm'],
                    T_out=s['T_out'], Rwh=0.6 * M['Rth'] / n, Rha=1.0 / (H_AIR * FINS * area), Cw=Cw, Ch=Ch,
                    est=['Cw (F_CU 0.25)', 'Ch (housing mass x Al + iron)', 'Rwh 0.6*Rth', 'Rha h12 x fins2'] +
                        (['ankle_roll area = ankle_pitch area (cnt 0 in sizing)'] if not s['area_cad'] else []))
    return P


def p_cu(p, tau, Tw):
    Tm = np.abs(tau) / (p['ratio'] * p['eta'] * p['nmot'])
    Km = p['Km25'] / np.sqrt(1.0 + ALPHA_CU * (Tw - 25.0))
    return p['nmot'] * (Tm / Km) ** 2


class WindingModel:
    """State per joint; call step(tau, dt) every control tick (any rate >= 10 Hz)."""
    def __init__(self, joints, params=None, t_amb=T_AMB):
        self.P = params or load_params(); self.j = list(joints); self.ta = t_amb
        self.Tw = np.full(len(self.j), t_amb); self.Th = np.full(len(self.j), t_amb)
        self.p = [self.P[_base(n)] for n in self.j]

    def step(self, tau, dt):
        for i, p in enumerate(self.p):
            q = p_cu(p, tau[i], self.Tw[i]); qwh = (self.Tw[i] - self.Th[i]) / p['Rwh']
            qha = (self.Th[i] - self.ta) / p['Rha']
            self.Tw[i] += dt * (q - qwh) / p['Cw']; self.Th[i] += dt * (qwh - qha) / p['Ch']
        return self.Tw.copy()

    def torque_limits(self, tau_peak):
        return np.array([derate(self.Tw[i], tau_peak[i], tau_cont(p, self.ta)) for i, p in enumerate(self.p)])


def _base(name):
    return name[2:] if name[:2] in ('l_', 'r_') else name


def tau_cont(p, t_amb=T_AMB, t_w=T_LIMIT):
    """Joint torque that holds the winding at t_w in steady state (Ch drops out)."""
    P = (t_w - t_amb) / (p['Rwh'] + p['Rha'])
    Km = p['Km25'] / np.sqrt(1.0 + ALPHA_CU * (t_w - 25.0))
    return np.sqrt(P / p['nmot']) * Km * p['ratio'] * p['eta'] * p['nmot']


def derate(Tw, tau_peak, tau_c):
    """Torque limit vs winding temperature: full peak below T_DERATE, linear to the
    steady-state continuous torque at T_LIMIT, linear to 0 at T_TRIP (fault)."""
    if Tw <= T_DERATE:
        return tau_peak
    if Tw <= T_LIMIT:
        return tau_peak + (min(tau_c, tau_peak) - tau_peak) * (Tw - T_DERATE) / (T_LIMIT - T_DERATE)
    return max(0.0, min(tau_c, tau_peak) * (T_TRIP - Tw) / (T_TRIP - T_LIMIT))
