"""Limp-mode hip hold (TP-G5-18): keep the limp L/R skirt clamp force <= 140 N. D94 drives: no brakes, backdrivable.
All forces are [EST] lever-arm statics with the T&R R_HIP_PINCH numbers. No bench data exists yet.
  - Gravity/backdrive closing moment of a limp leg M_g = 25 N.m (T&R: ~10 kg at ~0.25 m), panel edge lever r = 0.150 m.
  - D94 friction hold at the hip: 7 N.m (DRIVE_DERATE static_hold_ok; HANDLING_MAP C3 says 7-9).
  - ID 8c foam: L/R strip load-limited 127 N, hem strip 115 N (hip_skirt_r8c_foam.json).
Options:
  A low-current hold: MO=1, hip roll/yaw position hold with a current (torque) clamp TAU_HOLD. Covers motors-on-but-limp only.
  B short-brake: phase short (drive feature [EST]). Velocity damping only, zero static torque. Covers trip/power loss only if
    Actuators provide a fail-safe short (normally-closed or self-powered), otherwise none.
  C pre-limp posture: before a commanded MO=0, drive both hips to a posture whose L/R and hem gaps are >= warn and that friction
    holds. Covers planned limp only (R-145 stop / fall_mode end state). It does not cover a trip or power loss."""
from __future__ import annotations
import numpy as np
try:
    from . import hip_pinch as H
except ImportError:
    import hip_pinch as H

M_G, R_EDGE, TAU_FRIC, F_LIM = 25.0, 0.150, 7.0, 140.0
FOAM_LR, FOAM_HEM = 127.0, 115.0

def clamp_force(tau_hold=0.0, friction=TAU_FRIC, m_g=M_G, r=R_EDGE):
    """Static closing force on the edge [N]: whichever is larger, the gravity drive net of friction and the hold, or the force the hold itself can apply."""
    grav = max(0.0, m_g - friction - tau_hold) / r
    servo = tau_hold / r  # worst case: hold reference behind the hand, drive pushes up to its clamp
    return max(grav, servo)

def tau_hold_max(f_lim=min(F_LIM, FOAM_LR), r=R_EDGE):
    return f_lim * r

def options():
    tau = round(min(tau_hold_max(), 15.0), 1)
    return {
        'none (D94 friction only, static)': dict(F_N=round(clamp_force(0.0), 0), covers=['power loss', 'tripped', 'limp'],
            note='static only; a swinging leg adds impact, not bounded'),
        f'A low-current hold tau<={tau} N.m (hip roll+yaw)': dict(F_N=round(clamp_force(tau), 0), covers=['motors-on-but-limp'],
            note='needs MO=1 and a drive hardware current clamp; not available when tripped or unpowered'),
        'B short-brake damping [EST]': dict(F_N=round(clamp_force(0.0), 0), covers=['tripped / power loss IF fail-safe short'],
            note='zero static torque, so static force = friction-only case; limits closing speed (impact) only'),
        'C pre-limp posture + friction': dict(F_N=round(clamp_force(0.0, m_g=pose_gravity_moment()), 0), covers=['planned MO=0 only'],
            note='gaps >= warn at entry; friction must hold M_g at the posture [EST]'),
    }

def pose_gravity_moment(roll_deg=4.0):
    """[EST] small-roll abducted posture: gravity roll moment of a ~10 kg leg at 0.25 m, sin-scaled from the T&R full value."""
    return M_G * abs(np.sin(np.radians(roll_deg))) + 0.0

def pre_limp_posture(q: dict, roll_target_deg=4.0, warn=None):
    """Hip roll/yaw targets for a planned MO=0. Keep pitch and set yaw 0 and roll +roll_target (abducted) on both legs,
    then verify gaps >= warn. Returns (q_target, gaps, ok)."""
    warn = H.WARN if warn is None else warn
    t = dict(q)
    for sd in 'lr':
        t[f'{sd}_hip_yaw'] = 0.0
        t[f'{sd}_hip_roll'] = np.radians(roll_target_deg) * (1 if sd == 'l' else -1)
    g = H.gaps(t)
    return t, g, min(g.values()) >= warn

class LimpHipHold:
    """Supervisor/fall_mode hook. On a limp request (motors on): low-current hip roll/yaw hold at TAU_HOLD. On a planned
    MO=0 (fall_mode end state, R-145): first go to the pre-limp posture, and allow MO=0 only once it is reached (gap >= warn)."""
    def __init__(s, tau_hold=None):
        s.tau_hold = min(tau_hold_max(), 15.0) if tau_hold is None else tau_hold
        assert clamp_force(s.tau_hold) <= min(F_LIM, FOAM_LR)
    def limp_command(s, q: dict, mo_on: bool):
        """Returns per hip joint (mode, ref, tau_max). mo_on False: nothing can be commanded (report only)."""
        if not mo_on: return {}
        return {f'{sd}_hip_{j}': ('hold', q.get(f'{sd}_hip_{j}', 0.0), s.tau_hold) for sd in 'lr' for j in ('roll', 'yaw')}
    def mo_off_allowed(s, q: dict):
        g = H.gaps(q); return min(g.values()) >= H.WARN, g
