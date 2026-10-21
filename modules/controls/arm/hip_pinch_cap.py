"""Actuators D100 (31875a1) fallback: inside the hip-pinch zone (governing gap <= warn 35 mm, rev 8c rigid geometry) cap
hip roll and yaw torque at 14 N.m on both legs. Hip pitch is not capped. Applied to the drive torque command after every other cap."""
from __future__ import annotations
import numpy as np
try:
    import hip_pinch as H
except ImportError:
    from . import hip_pinch as H
TAU_CAP = 14.0
CAPPED = [f'{s}_hip_{j}' for s in 'lr' for j in ('roll', 'yaw')]

class HipPinchTorqueCap:
    def __init__(s, period_s=0.010):
        s.period = period_s; s.t_last = -1e9; s.gap = 1e9; s.active = False; s.n_active = 0
    def update(s, q: dict, t: float):
        if t - s.t_last >= s.period:
            s.gap = H.min_gap(q); s.t_last = t; s.active = s.gap <= H.WARN; s.n_active += s.active
        return s.active
    def apply(s, tau: dict, q: dict, t: float):
        """tau: joint name -> N.m. Returns capped copy."""
        out = dict(tau)
        if s.update(q, t):
            for n in CAPPED:
                if n in out: out[n] = float(np.clip(out[n], -TAU_CAP, TAU_CAP))
        return out
