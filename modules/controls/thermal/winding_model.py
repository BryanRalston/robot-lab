"""A40 / P-029 (R-030), updated to Actuators THERMAL_DATA_PACK (f205f7b, D69).

2-node model per joint actuator (the joint's motors lumped; size.py / r1_budget.py convention):
    winding  Cw dTw/dt = P_cu(Tw) + P_fe(n) - (Tw - Th)/Rwh
    housing  Ch dTh/dt = (Tw - Th)/Rwh + P_drv(I) - (Th - Ta)/Rha
P_cu = nmot*(Tm/Km(Tw))^2, Tm = |tau|/(ratio*eta*nmot); Km(T) = Km25/sqrt(1+ALPHA_CU*(T-25))
  (equivalent to R(T) = R25*(1+0.00393*(T-25)); R155 = 1.511*R25 per the pack).
P_fe = nmot*(a*n + b*n^2), n motor krpm (pack §5, iron_loss.json); iron loss lumped in the winding node (conservative).
P_drv = Elmo Gold Twitter loss vs motor current amplitude (pack §6, worst-case chart), per motor, into the housing node
  (drives chassis-mounted on the housing, pack §6).
Limits (RL Thermal 26412c7): design target <=120 °C; linear derate 130 -> 145 °C to the continuous rating;
  hard torque-off 150 °C (PT1000); 155 °C absolute (TBM2G manual §1.2.2).
Drive placement: P-027 drives off the housings; D69 knee drives on the shank spreader saddle (~60-65 °C). So by
  default no leg drive heats its motor housing (DRIVE_ON_HOUSING); arms/waist placement not specified -> off, flag.
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
# Limits: RL Thermal D69_KNEE_CHECK.md §5 (26412c7), authoritative; supersede the Actuators pack §1 suggestion
T_TARGET = 120.0        # °C, design target at 35 °C ambient, sustained worst duty (acceptance, not a control limit)
T_DERATE = 130.0        # °C, derate trip (PT1000, or the model estimate if higher)
T_LIMIT = 145.0         # °C, end of linear derate: torque limit = continuous rating
T_TRIP = 150.0          # °C, hard torque-off (measured via PT1000)
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
DRIVE_ON_HOUSING = {}   # joint -> True to put the Elmo loss into the housing node (sensitivity); default off (P-027, D69)
TAU_CONT_AT = 130.0     # °C winding at which the continuous rating is evaluated (derate end value)
KNEE_FIN_A, KNEE_FIN_H = 0.05, 12.0   # superseded rev B paper fins (m2 wetted, W/m2K) [EST], knee='07613D_fins' only
# As-built D69 rev B (Actuators fbd762b, R-062/R-070): 2x 07613D + 0.0703 m2 CAD fins; housing-air G = h*(A_bare + eta_f*A_fin),
# size.py x2 'fins' factor DROPPED; still air h 8, eta_f 0.7 (conservative, Controls 2e2d593); drives off housing.
REVB_A_FIN, REVB_H, REVB_ETA = 0.0703, 8.0, 0.7
KNEE_D69 = dict(   # superseded by D69 rev B (4366d32); kept for history
    motor='TBM2G-08513D', rha_scale=0.5)   # D69: 2x 08513D + shank path Rha x0.5 [EST]


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


def load_params(root=ROOT, knee='revB', h=REVB_H, eta_f=REVB_ETA):
    """knee='revB' (DEFAULT since R-070: as built fbd762b, 0.0703 m2 fins, x2 dropped, h/eta_f args),
    knee='07613D_fins' (default, D69 rev B 4366d32 / R-044: 2x 07613D + 0.05 m2 housing fins at h 12, eta_f 1),
    '07613D' (bare, as sized; actuators/knee_thermal.py base case) or 'D69' (superseded 2x 08513D + shank path)."""
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
    if knee == 'revB':
        k = P['knee']; a_bare = 1.0 / (k['Rha'] * H_AIR * FINS)
        k['Rha'] = 1.0 / (h * (a_bare + eta_f * REVB_A_FIN))
        k['est'] = k['est'] + [f'D69 rev B as built: A_bare {a_bare:.4f} + {eta_f} x 0.0703 m2 fins, h {h} [EST h, eta_f]']
    if knee == '07613D_fins':
        P['knee']['Rha'] = 1.0 / (1.0 / P['knee']['Rha'] + KNEE_FIN_H * KNEE_FIN_A)
        P['knee']['est'] = P['knee']['est'] + ['D69 rev B fins 0.05 m2 x h 12, fin efficiency 1 [EST]']
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
        self.hold = None   # HoldLimiter, created lazily (defined below)

    def step(self, tau, dt, omega=None, p_fe_W=None, drive=None):
        """tau: joint torques (N·m). omega: joint speeds (rad/s) for iron loss, or p_fe_W: per-joint iron loss (W)."""
        for i, p in enumerate(self.p):
            q = p_cu(p, tau[i], self.Tw[i])
            if omega is not None: q += p_fe(p, omega[i])
            elif p_fe_W is not None: q += p_fe_W[i]
            on = DRIVE_ON_HOUSING.get(_base(self.j[i]), False) if drive is None else drive
            qd = p_drv(p, tau[i]) if on else 0.0
            qwh = (self.Tw[i] - self.Th[i]) / p['Rwh']; qha = (self.Th[i] - self.ta) / p['Rha']
            self.Tw[i] += dt * (q - qwh) / p['Cw']; self.Th[i] += dt * (qwh + qd - qha) / p['Ch']
        if self.hold is None: self.hold = HoldLimiter(self.j)
        self.hold.step(tau, dt)
        return self.Tw.copy()

    def correct(self, i, T_meas, gain=0.02):
        """Optional slow PT1000 correction (code A sensor, pack §2): nudge the housing/winding estimate toward
        the stator reading. The sensor is too slow for peaks, so the I2t prediction stays primary."""
        e = T_meas - self.Tw[i]; self.Tw[i] += gain * e; self.Th[i] += gain * e

    def torque_limits(self, tau_peak):
        if self.hold is None: self.hold = HoldLimiter(self.j)
        return np.array([min(derate(self.Tw[i], tau_peak[i], tau_cont(p, self.ta)), self.hold.limit(i, tau_peak[i]))
                         for i, p in enumerate(self.p)])


def _base(name):
    return name[2:] if name[:2] in ('l_', 'r_') else name


def tau_cont(p, t_amb=T_AMB, t_w=TAU_CONT_AT, p_fe_W=0.0):
    """Joint torque that holds the winding at t_w in steady state (Ch drops out). Copper (+ optional mean iron
    loss); drive loss not included (it depends on tau and only heats the housing)."""
    P = max(0.0, (t_w - t_amb) / (p['Rwh'] + p['Rha']) - p_fe_W)
    Km = p['Km25'] / np.sqrt(1.0 + ALPHA_CU * (t_w - 25.0))
    return np.sqrt(P / p['nmot']) * Km * p['ratio'] * p['eta'] * p['nmot']


def derate(Tw, tau_peak, tau_c, T_meas=None):
    """Torque limit vs winding temperature (RL Thermal 26412c7): full peak below T_DERATE (130), linear to the
    continuous rating tau_c at T_LIMIT (145), held there to T_TRIP, 0 at/above T_TRIP (150, torque-off).
    The derate uses max(model, PT1000); the hard torque-off is on the measured PT1000 when given, else the model."""
    T = Tw if T_meas is None else max(Tw, T_meas)
    T_off = Tw if T_meas is None else T_meas
    if T_off >= T_TRIP:
        return 0.0
    tc = min(tau_c, tau_peak)
    if T <= T_DERATE:
        return tau_peak
    if T <= T_LIMIT:
        return tau_peak + (tc - tau_peak) * (T - T_DERATE) / (T_LIMIT - T_DERATE)
    return tc


# ---- P-042 carry primitive + P-043 hold limits (Arms & Hands R3b a618ce0, PROPOSALS P-042 (b)/(c)) ----
CARRY_POSE = dict(shoulder_pitch=np.deg2rad(-60.0), elbow=np.deg2rad(-110.0), shoulder_roll=0.0, shoulder_yaw=0.0,
                  wrist_roll=0.0, wrist_pitch=0.0, wrist_yaw=0.0)
CARRY_BAND = dict(shoulder_pitch=np.deg2rad([-60.0, -50.0]), elbow=np.deg2rad([-115.0, -100.0]))
# joint: (threshold N·m, over-threshold cap N·m, allowed time s, cap after time N·m)
HOLD_LIMITS = {'elbow': (15.0, 40.0, 180.0, 28.0),          # >15 N·m: <=3 min at <=40, then <=28
               'shoulder_pitch': (55.0, None, 600.0, 55.0)}  # >55 N·m: <=10 min, then <=55


class HoldLimiter:
    """Time-over-threshold budget per arm joint. The timer runs while |tau| > threshold and recovers at the same
    rate below it [EST recovery rule, not in P-042]. limit() is min'd with the thermal derate."""
    def __init__(self, joints):
        self.j = list(joints); self.t = np.zeros(len(self.j))

    def step(self, tau, dt):
        for i, n in enumerate(self.j):
            h = HOLD_LIMITS.get(_base(n))
            if h is None: continue
            self.t[i] = self.t[i] + dt if abs(tau[i]) > h[0] else max(0.0, self.t[i] - dt)

    def limit(self, i, tau_peak):
        h = HOLD_LIMITS.get(_base(self.j[i]))
        if h is None: return tau_peak
        thr, cap, t_max, after = h
        if self.t[i] >= t_max: return min(tau_peak, after)
        return min(tau_peak, cap) if cap is not None else tau_peak


def in_carry_band(q):
    """q: dict joint -> angle (rad). True if shoulder_pitch and elbow sit in the P-042 band."""
    return all(lo <= q[k] <= hi for k, (lo, hi) in CARRY_BAND.items())
