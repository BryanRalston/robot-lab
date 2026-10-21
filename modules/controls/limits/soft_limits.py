"""Controls soft joint limits (abduction 127 deg, R-133; elbow caps are documented in SOFT_LIMITS.md)."""
import json, math, os
_HERE = os.path.dirname(os.path.abspath(__file__))
CFG = json.load(open(os.path.join(_HERE, 'soft_limits.json')))

def roll_soft_limit_rad(side='l'):
    """Return (lo, hi) rad soft limits for shoulder_roll. side 'l' or 'r'."""
    lim = math.radians(CFG['shoulder_roll_abduction_deg'])
    hard_lo, hard_hi = math.radians(-15), math.radians(180)
    if side.lower().startswith('r'):
        return (-lim, math.radians(15))  # mirrored
    return (hard_lo, lim)

def clamp_q(joint, q, side='l'):
    if joint == 'shoulder_roll':
        lo, hi = roll_soft_limit_rad(side)
        return max(lo, min(hi, q))
    return q

def elbow_hard_cap_Nm():
    return float(CFG['elbow_torque_hard_cap_Nm'])


# Knee stop-zone torque cap (Robot Lab ruling per T&R 513a7d5): |tau_knee| <= 50 N.m once knee >= 125 deg
# (10 deg before the 135 deg PU stop) in fall / TUCK / R-146 kneel-lower states. Applied on top of the thermal
# derate: the effective limit is min(derated limit, cap).
KNEE_CAP_NM = float(CFG['knee_stop_zone_cap_Nm'])
KNEE_CAP_START_RAD = math.radians(CFG['knee_stop_zone_start_deg'])
KNEE_CAP_STATES = frozenset(CFG['knee_stop_zone_states'])


def knee_cap_active(q_knee, state):
    return state in KNEE_CAP_STATES and q_knee >= KNEE_CAP_START_RAD


def knee_torque_limit(q_knee, state, tau_lim):
    """Effective knee |torque| limit = min(tau_lim (already derated), 50 N.m in the stop zone)."""
    return min(tau_lim, KNEE_CAP_NM) if knee_cap_active(q_knee, state) else tau_lim


def apply_knee_stop_cap(names, q_knee_by_name, tau, state):
    """Clip knee entries of tau (array, same order as names) in place. q_knee_by_name(name) -> knee angle rad."""
    if state not in KNEE_CAP_STATES:
        return tau
    for i, n in enumerate(names):
        if n.endswith('knee') and q_knee_by_name(n) >= KNEE_CAP_START_RAD:
            tau[i] = max(-KNEE_CAP_NM, min(KNEE_CAP_NM, tau[i]))
    return tau
