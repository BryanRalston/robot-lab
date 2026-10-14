"""R-070 software pick-pose (deep squat) knee limit. Table from pick_limit_gen.py (A40 winding model, as-built
D69 rev B, h 8 / eta_f 0.7, 35 C, hot start = steady 64.4 N·m standing carry hold, target winding 120 C).
Use in the WBC per leg, each tick: lim = PickLimiter.limit(); tau_knee_cmd = clip(tau, -lim, lim);
then min with WindingModel.torque_limits() (derate 130->145, trip 150 stays the backstop).
Rule: a squat episode starts when |tau_knee| > TAU_ON. Budget b += dt / DWELL(|tau|) (DWELL = 50 % of the hot
dwell to 120 C, so a repeat after REST stays <= 120 C). b >= 1 -> knee cap TAU_ON (task must rise/abort the pick).
After the episode (|tau| <= TAU_ON) a new episode is blocked (cap TAU_ON) until REST(peak tau of episode) has elapsed.
The planner should query allowed_dwell(tau) before committing to a pick."""
import numpy as np
TAU_ON = 77.0   # N·m, = tau_cont at 120 C (rev B as built); below this the knee is continuous-rated
# tau N·m, dwell s (50 % of hot dwell to 120 C), rest s at <= 64.4 N·m before the next squat (pick_limit_table.json)
TAB_TAU   = np.array([80., 100., 120., 150., 180., 220., 260., 300., 345.])
TAB_DWELL = np.array([775., 97., 25.6, 10.5, 6.1, 3.7, 2.5, 1.8, 1.3])
TAB_REST  = np.array([471., 657., 274., 181., 162., 149., 144., 139., 132.])

def allowed_dwell(tau):
    """Max continuous dwell (s) at |tau| (log-interp, conservative at ends); inf below TAU_ON."""
    t = abs(tau)
    if t <= TAU_ON: return np.inf
    return float(np.exp(np.interp(t, TAB_TAU, np.log(TAB_DWELL), left=np.log(TAB_DWELL[0]), right=np.log(TAB_DWELL[-1]) - (t - 345.) / 50.)))

def rest_needed(tau_peak):
    """Rest (s, knee <= 64.4 N·m) after an episode before the next deep squat; max over table rows at or below tau_peak."""
    t = abs(tau_peak)
    if t <= TAU_ON: return 0.0
    return float(TAB_REST[: max(1, np.searchsorted(TAB_TAU, t, side='right'))].max())

class PickLimiter:
    def __init__(self): self.b = 0.0; self.pk = 0.0; self.rest_left = 0.0; self.active = False
    def step(self, tau, dt):
        t = abs(tau)
        if t > TAU_ON:
            self.active = True; self.pk = max(self.pk, t); self.b += dt / allowed_dwell(t)
        else:
            if self.active: self.rest_left = rest_needed(self.pk); self.active = False; self.b = 0.0; self.pk = 0.0
            self.rest_left = max(0.0, self.rest_left - dt)
    def limit(self, tau_peak=345.0):
        if self.b >= 1.0 or (not self.active and self.rest_left > 0.0): return min(tau_peak, TAU_ON)
        return tau_peak
