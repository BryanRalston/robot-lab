"""A40 / P-029 (R-030), updated to Actuators THERMAL_DATA_PACK (f205f7b, D69).

2-node model per joint actuator (the joint's motors lumped; size.py / r1_budget.py convention):
    winding  Cw dTw/dt = P_cu(Tw) + P_fe(n) - (Tw - Th)/Rwh
    housing  Ch dTh/dt = (Tw - Th)/Rwh + P_drv(I) - (Th - Ta)/Rha
P_cu = nmot*(Tm/Km(Tw))^2, Tm = |tau|/(ratio*eta*nmot); Km(T) = Km25/sqrt(1+ALPHA_CU*(T-25))
  (equivalent to R(T) = R25*(1+0.00393*(T-25)); R155 = 1.511*R25 per the pack).
P_fe = nmot*(a*n + b*n^2), n motor krpm (pack §5, iron_loss.json); iron loss lumped in the winding node (conservative).
P_drv = Elmo Gold Twitter loss vs motor current amplitude (pack §6, worst-case chart), per motor, into the housing node
  (drives chassis-mounted on the housing, pack §6).
Limits: derate from 120 °C, continuous point 130 °C, torque off 140 °C, hard limit 155 °C (TBM2G manual §1.2.2).
Knee = D69: 2x TBM2G-08513D + conductive shank path (Rha x0.5 [EST]); same convention as actuators/knee_thermal.py.
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
T_LIMIT = 130.0         # °C, continuous-torque point (our margin, pack §1)
T_TRIP = 140.0          # °C, torque off (pack §1 recommendation; 15 K margin to T_HARD)
T_HARD = 155.0          # °C, TBM2G winding hard limit (manual §1.2.2, Class F inferred)
LEG = ['hip_yaw', 'hip_roll', 'hip_pitch', 'knee', 'ankle_pitch', 'ankle_roll']
UPPER = ['waist_yaw', 'waist_pitch', 'shoulder_pitch', 'shoulder_roll', 'shoulder_yaw', 'elbow', 'wrist_roll']
# Elmo Gold Twitter loss (W) vs motor current amplitude (A), MAN-G-TWI v2.011 §11.2.1 worst case (pack §6)
DRV_I = np.array([0.0, 5, 10, 20, 30, 40, 50]); DRV_W = np.array([0.0, 2, 5, 13, 22, 32, 44])
# iron loss fits a, b (W/krpm, W/krpm^2), pack §5; frames without a fit use the nearest fitted frame scaled by kit mass [EST]
IRON = {'TBM2G-06008': (1.56, 0.0), 'TBM2G-08508': (1.07, 0.489), 'TBM2G-07613': (1.83, 0.195), 'TBM2G-06013': (1.02, 0.058)}
IRON_EST = {'TBM2G-08513': 'TBM2G-07613', 'TBM2G-07608': 'TBM2G-07613', 'TBM2G-06813': 'TBM2G-07613',
            'TBM2G-06008C': 'TBM2G-06008', 'TBM2G-05013': 'TBM2G-06008', 'TBM2G-05008': 'TBM2G-06008'}
WIND = {'A': 0, 'C': 1, 'D': 2}
# Upper body (Arms R1_ARCHITECTURE table owns the mapping; waist O-T2 per pack). CSG x100, eta 0.75 (r1_budget eta_rot),
# housing D x L mm: shoulder_pitch 96x80, elbow 70x75 (r1_budget [EST]); others [EST] by frame. Housing mass [EST].
UPPER_SPEC = {
    'waist_yaw':      ('TBM2G-08508A', 1, 100, 0.75, 96, 80, 0.30),
    'waist_pitch':    ('TBM2G-08508A', 1, 100, 0.75, 96, 80, 0.30),
    'shoulder_pitch': ('TBM2G-07608C', 1, 100, 0.75, 96, 80, 0.30),
    'shoulder_roll':  ('TBM2G-06813C', 1, 100, 0.75, 96, 80, 0.30),
    'shoulder_yaw':   ('TBM2G-06008C', 1, 100, 0.75, 70, 75, 0.20),
    'elbow':          ('TBM2G-05013C', 1, 100, 0.75, 70, 75, 0.20),
    'wrist_roll':     ('TBM2G-05008C', 1, 100, 0.75, 60, 60, 0.12),
}
KNEE_D69 = dict(motor='TBM2G-08513D', rha_scale=0.5)   # D69: 2x 08513D + shank path Rha x0.5 [EST]


def _iron(model_w):
    base = model_w[:11]
    if base in IRON and not model_w.endswith('C'):
        return IRON[base], False
    ref = IRON_EST.get(model_w, IRON_EST.get(base, 'TBM2G-07613'))
    return IRON[ref], True


def _p(M, model_w, n, ratio, eta, area, m_house, t_out, extra_est=()):
    w = WIND[model_w[-1]]; k = 1.0
    (a, b), iron_est = _iron(model_w)
    if iron_est:   # scale by kit mass vs the fitted frame [EST]
        ref = IRON_EST.get(model_w, IRON_EST.get(model_w[:11], 'TBM2G-07613'))
        k = M['mass'] / MOT_CACHE[ref]['mass']; a, b = a * k, b * k
    m_mot = M['mass'] * n
    return dict(motor=model_w, nmot=n, ratio=ratio, eta=eta, Km25=M['Km'][w] if not (model_w.startswith('TBM2G-07613') and w == 1) else 0.201,
                Kt=M['Kt_hot'][w], R25=M['Rm'][w], R155=M['Rm'][w] * (1 + ALPHA_CU * 130), T_out=t_out,
                Rwh=0.6 * M['Rth'] / n, Rha=1.0 / (H_AIR * FINS * area), Cw=F_CU * m_mot * C_CU,
                Ch=m_house * C_AL + (1 - F_CU) * m_mot * C_FE, iron_a=a, iron_b=b,
                est=['Cw (F_CU 0.25)', 'Rwh 0.6*Rth', 'Rha h12 x fins2'] + (['iron fit scaled by mass'] if iron_est else []) + list(extra_est))


MOT_CACHE = {}


def load_params(root=ROOT, knee='D69'):
    """knee='D69' (default, Actuators D69) or '07613D' (as sized; used by actuators/knee_thermal.py base case)."""
    sel = json.load(open(os.path.join(root, 'modules/actuators/results/sizing.json')))['sel']
    mot = json.load(open(os.path.join(root, 'v3/analysis/tbm2g.json'))); MOT_CACHE.update(mot)
    P = {}
    for j in LEG:
        s = sel[j]; mw = s['label'].split(' ')[0]
        area = s['area_cad'] or sel['ankle_pitch']['area_cad']
        mh = s['housing_cad'] or s['housing_model']
        P[j] = _p(mot[mw[:11]], mw, s['nmot'], s['ratio'], s['eta'], area, mh, s['T_out'],
                  [] if s['area_cad'] else ['ankle_roll area = ankle_pitch area (cnt 0 in sizing)'])
        P[j]['Km25'] = s['Km']   # sizing.json value (07613D 0.201, D15 typo fix)
    if knee == 'D69':
        mw = KNEE_D69['motor']; M = mot[mw[:11]]; s = sel['knee']
        k = _p(M, mw, 2, s['ratio'], s['eta'], s['area_cad'], s['housing_cad'], s['T_out'],
               ['D69 shank path Rha x0.5', 'housing = 07613D CAD housing + motor mass delta'])
        k['Rha'] *= KNEE_D69['rha_scale']
        k['Ch'] = P['knee']['Ch'] + (1 - F_CU) * 2 * (M['mass'] - mot['TBM2G-07613']['mass']) * C_FE   # as knee_thermal.py
        P['knee'] = k
    for j, (mw, n, ratio, eta, D, L, mh) in UPPER_SPEC.items():
        area = (np.pi * D * L + 2 * np.pi / 4 * D ** 2) * 1e-6
        P[j] = _p(mot[mw[:11]], mw, n, ratio, eta, area, mh, None, ['upper-body housing D x L, mass, ratio, eta'])
    return P


def p_fe(p, omega_joint):
    n = np.abs(omega_joint) * p['ratio'] * 60.0 / (2 * np.pi) / 1000.0
    return p['nmot'] * (p['iron_a'] * n + p['iron_b'] * n ** 2)


def p_drv(p, tau):
    I_amp = np.abs(tau) / (p['ratio'] * p['eta'] * p['nmot']) / p['Kt'] * np.sqrt(2.0)
    return p['nmot'] * np.interp(I_amp, DRV_I, DRV_W)


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

    def step(self, tau, dt, omega=None, p_fe_W=None, drive=True):
        """tau: joint torques (N·m). omega: joint speeds (rad/s) for iron loss, or p_fe_W: per-joint iron loss (W)."""
        for i, p in enumerate(self.p):
            q = p_cu(p, tau[i], self.Tw[i])
            if omega is not None: q += p_fe(p, omega[i])
            elif p_fe_W is not None: q += p_fe_W[i]
            qd = p_drv(p, tau[i]) if drive else 0.0
            qwh = (self.Tw[i] - self.Th[i]) / p['Rwh']; qha = (self.Th[i] - self.ta) / p['Rha']
            self.Tw[i] += dt * (q - qwh) / p['Cw']; self.Th[i] += dt * (qwh + qd - qha) / p['Ch']
        return self.Tw.copy()

    def correct(self, i, T_meas, gain=0.02):
        """Optional slow PT1000 correction (code A sensor, pack §2): nudge the housing/winding estimate toward
        the stator reading. The sensor is too slow for peaks, so the I2t prediction stays primary."""
        e = T_meas - self.Tw[i]; self.Tw[i] += gain * e; self.Th[i] += gain * e

    def torque_limits(self, tau_peak):
        return np.array([derate(self.Tw[i], tau_peak[i], tau_cont(p, self.ta)) for i, p in enumerate(self.p)])


def _base(name):
    return name[2:] if name[:2] in ('l_', 'r_') else name


def tau_cont(p, t_amb=T_AMB, t_w=T_LIMIT, p_fe_W=0.0):
    """Joint torque that holds the winding at t_w in steady state (Ch drops out). Copper (+ optional mean iron
    loss); drive loss not included (it depends on tau and only heats the housing)."""
    P = max(0.0, (t_w - t_amb) / (p['Rwh'] + p['Rha']) - p_fe_W)
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
