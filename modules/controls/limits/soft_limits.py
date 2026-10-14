"""Controls soft joint limits (abduction interim 135 deg; elbow caps are documented in SOFT_LIMITS.md)."""
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
