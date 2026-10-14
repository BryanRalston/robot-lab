"""R-079 software knee CARRY duty limit (walking 20 kg carry, P-042 profile), A40 winding model, as-built D69 rev B,
eta_f 0.7, 35 C, drives off housing, target winding <= 120 C; WindingModel.torque_limits() derate stays the backstop.
h (housing-air W/m2K) is a config parameter: default 8 (still air, R-079); raise only when Thermal validates a walking h.
Shared state: KneeThermal integrates the 2-node model on the MEASURED knee torque/speed every tick (one per leg) and is
the single thermal state for both this limit and the pick limit (PickLimiter is gated by KneeThermal.pick_ok()).
Carry prediction uses the cycle-equivalent load of the P-042 profile: copper at RMS torque (T-dependent) + mean iron loss
(validated vs the full profile in test_carry_limit.py). See CARRY_LIMIT.md, tables from carry_limit_gen.py."""
import os, sys, numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(HERE, '..', 'thermal'))
import winding_model as W
T_TGT = W.T_TARGET          # 120 C
HOLD = 64.4                 # N·m worst standing carry hold (rest torque, conservative)
# P-042 carry_20kg_1p0 worst knee (col 3), 1.0 m/s: RMS torque and mean iron loss (W) at x1.0 (carry_limit_gen.py)
CARRY_RMS, CARRY_PFE = 76.7, 4.28   # overwritten below from carry_limit_table.json if present
try:
    import json; _T = json.load(open(os.path.join(HERE, 'carry_limit_table.json')))
    CARRY_RMS, CARRY_PFE = _T['profile']['rms_x1.0'], _T['profile']['pfe_mean_W']
except Exception: pass
MARGIN = 0.9                # planner gets 90 % of the predicted time (model + profile variance)

def params(h=W.REVB_H, eta_f=W.REVB_ETA):
    return W.load_params(knee='revB', h=h, eta_f=eta_f)['knee']

class KneeThermal:
    """One per leg. step() with measured knee torque (N·m) and speed (rad/s)."""
    def __init__(self, h=W.REVB_H, eta_f=W.REVB_ETA, Tw=None, Th=None, p=None):
        self.p = p or params(h, eta_f); self.Tw = W.T_AMB if Tw is None else Tw; self.Th = self.Tw if Th is None else Th
    def _d(self, Tw, Th, q):
        qwh = (Tw - Th) / self.p['Rwh']
        return (q - qwh) / self.p['Cw'], (qwh - (Th - W.T_AMB) / self.p['Rha']) / self.p['Ch']
    def heat(self, tau_rms, pfe, Tw): return W.p_cu(self.p, tau_rms, Tw) + pfe
    def step(self, tau, dt, omega=0.0):
        dw, dh = self._d(self.Tw, self.Th, self.heat(tau, float(W.p_fe(self.p, omega)), self.Tw))
        self.Tw += dt * dw; self.Th += dt * dh
    def time_to_target(self, tau_rms, pfe=0.0, tmax=7200.0, dt=0.5, Tw=None, Th=None):
        """Seconds of constant-equivalent load from the given (default current) state until Tw = 120 C; inf if never."""
        Tw = self.Tw if Tw is None else Tw; Th = self.Th if Th is None else Th; t = 0.0
        if Tw >= T_TGT: return 0.0
        while t < tmax:
            dw, dh = self._d(Tw, Th, self.heat(tau_rms, pfe, Tw)); Tw += dt * dw; Th += dt * dh; t += dt
            if Tw >= T_TGT: return t
        return np.inf
    def steady(self, tau_rms, pfe=0.0):
        Ts = W.T_AMB
        for _ in range(200): Ts = W.T_AMB + self.heat(tau_rms, pfe, Ts) * (self.p['Rwh'] + self.p['Rha'])
        return Ts
    def pick_ok(self, tau, dwell):
        """Composition with pick_limit: a squat of dwell s at |tau| must also keep Tw <= 120 C from the CURRENT state."""
        return self.time_to_target(abs(tau), 0.0, tmax=dwell + 1.0, dt=0.05) > dwell

class CarryLimiter:
    """Planner interface. remaining() = carry seconds left at load scale s before 120 C (x MARGIN);
    allow() False -> planner must set the load down / stand (rest at <= HOLD). rest_for(t_carry) = rest needed now
    (at HOLD) so a following bout of t_carry fits."""
    def __init__(self, thermal, scale=1.1):
        self.th = thermal; self.s = scale
    def remaining(self, scale=None):
        s = self.s if scale is None else scale
        return MARGIN * self.th.time_to_target(CARRY_RMS * s, CARRY_PFE * s)
    def allow(self, min_bout=10.0): return self.remaining() >= min_bout
    def rest_for(self, t_carry, rest_tau=HOLD, scale=None, dt=1.0, tmax=7200.0):
        s = self.s if scale is None else scale; Tw, Th, t = self.th.Tw, self.th.Th, 0.0
        while t < tmax:
            if MARGIN * self.th.time_to_target(CARRY_RMS * s, CARRY_PFE * s, Tw=Tw, Th=Th) >= t_carry: return t
            dw, dh = self.th._d(Tw, Th, self.th.heat(rest_tau, 0.0, Tw)); Tw += 10 * dw; Th += 10 * dh; t += 10
        return np.inf

class R096Rule:
    """Arbiter R-096 (replaces R-081 10/10 OR 40 %): carry <= DUTY of any rolling WINDOW s AND each continuous carry bout
    <= MAX_BOUT s. 'Carrying' = load held (walking OR standing holding the load); unloaded = load set down.
    A bout ends only after >= MIN_GAP s unloaded; shorter breaks do not reset the bout timer (Controls: with 2-30 s
    breaks a compliant 5/5/2 min burst reaches 121.6-125.1 C; with MIN_GAP 60 s worst compliant = 119.1 C, h 8 x1.1).
    Arbiter R-100: MIN_GAP default 120 s set down (worst compliant 116.4 C); 60 s rejected; relax only after G5 hot-start data.
    remaining() = min(bout left, duty left) (window-expiry credit not counted: conservative)."""
    def __init__(self, max_bout=300.0, duty=0.40, window=1800.0, min_gap=120.0, dt_bin=1.0):
        self.bout, self.duty, self.win, self.gap, self.db = max_bout, duty, window, min_gap, dt_bin
        self.bins = np.zeros(int(window / dt_bin)); self.i = 0; self.acc = 0.0
        self.run = 0.0; self.idle = 0.0
    def step(self, load_held, dt):
        if load_held: self.run += dt; self.idle = 0.0
        else:
            self.idle += dt
            if self.idle >= self.gap - 1e-6: self.run = 0.0
        self.acc += dt
        while self.acc >= self.db:
            self.acc -= self.db; self.i = (self.i + 1) % len(self.bins); self.bins[self.i] = 0.0
        if load_held: self.bins[self.i] += dt
    def window_carry(self): return float(self.bins.sum())
    def remaining(self):
        return max(0.0, min(self.bout - self.run, self.duty * self.win - self.window_carry()))

R081Rule = R096Rule   # legacy name; R-081 defaults (10/10 OR 40 %) retired by R-096

class CarryGovernor:
    """Enforced: remaining = min(R-096 rule, model remaining at h); torque backstop = WindingModel derate (130->145)."""
    def __init__(self, thermal, scale=1.1, rule=None):
        self.th = thermal; self.model = CarryLimiter(thermal, scale); self.rule = rule or R096Rule()
    def step(self, tau, dt, omega=0.0, load_held=False):
        self.th.step(tau, dt, omega); self.rule.step(load_held, dt)
    def remaining(self): return min(self.rule.remaining(), self.model.remaining())
    def allow(self, min_bout=10.0): return self.remaining() >= min_bout
