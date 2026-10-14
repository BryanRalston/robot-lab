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

class R081Rule:
    """Arbiter R-081 / Thermal interim rule (enforced default, P-042 carry x1.1): a carry bout may run <= BOUT s; after a
    bout that reached BOUT, >= REST s unloaded before the next; OR keep carry time <= DUTY of any rolling WINDOW s.
    Planner reports carrying (load in hands) each tick. Unloaded = load set down (knee ~idle, NOT the 64.4 N·m loaded
    stand: with loaded rest the rule does not hold 120 C, see CARRY_LIMIT.md). Parameters configurable (tighter: BOUT 480)."""
    def __init__(self, bout=600.0, rest=600.0, duty=0.40, window=1800.0, dt_bin=1.0):
        self.bout, self.rest, self.duty, self.win, self.db = bout, rest, duty, window, dt_bin
        self.bins = np.zeros(int(window / dt_bin)); self.i = 0; self.acc = 0.0; self.cur = 0.0
        self.run = 0.0; self.rest_left = 0.0
    def step(self, carrying, dt):
        if carrying: self.run += dt; self.cur += dt
        else:
            if self.run >= self.bout: self.rest_left = self.rest
            self.run = 0.0; self.rest_left = max(0.0, self.rest_left - dt)
        self.acc += dt
        while self.acc >= self.db:
            self.acc -= self.db; self.i = (self.i + 1) % len(self.bins); self.bins[self.i] = 0.0
        self.bins[self.i] += dt if carrying else 0.0
    def window_carry(self): return float(self.bins.sum())
    def remaining(self):
        """Seconds of carry allowed now under the rule (either branch)."""
        if self.rest_left > 0.0: return 0.0
        a = max(0.0, self.bout - self.run)                      # 10-on/10-off branch
        b = max(0.0, self.duty * self.win - self.window_carry())  # rolling-duty branch (conservative: no window expiry credit)
        return max(a, b)

class CarryGovernor:
    """Enforced: remaining = min(R-081 rule, model remaining at h); torque backstop = WindingModel derate (130->145)."""
    def __init__(self, thermal, scale=1.1, rule=None):
        self.th = thermal; self.model = CarryLimiter(thermal, scale); self.rule = rule or R081Rule()
    def step(self, tau, dt, omega=0.0, carrying=False):
        self.th.step(tau, dt, omega); self.rule.step(carrying, dt)
    def remaining(self): return min(self.rule.remaining(), self.model.remaining())
    def allow(self, min_bout=10.0): return self.remaining() >= min_bout
