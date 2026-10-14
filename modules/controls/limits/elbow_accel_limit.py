"""R-085: at full reach with payload > 8.5 kg, scale arm accel to <=87% of R1 profile.
Blend smoothly with reach so there is no step at the threshold.
R1 profile alpha = 20 rad/s^2 [EST] (arm_loads_r1.py)."""
import json, math, os
_HERE = os.path.dirname(os.path.abspath(__file__))
CFG = json.load(open(os.path.join(_HERE, 'soft_limits.json')))
ALPHA_R1 = 20.0  # rad/s^2 [EST]

def accel_scale(reach_m, payload_kg):
    """Return scale in (0,1] on R1 alpha. 1.0 = unrestricted."""
    if payload_kg is None or payload_kg <= CFG['R085_payload_thresh_kg']:
        return 1.0
    r0 = CFG['R085_blend_start_reach_m']
    r1 = CFG['R085_full_reach_m']
    s_full = CFG['R085_accel_scale_at_full_reach']
    if reach_m <= r0:
        return 1.0
    if reach_m >= r1:
        return s_full
    # smoothstep blend 1 -> s_full over [r0, r1]
    t = (reach_m - r0) / (r1 - r0)
    t = t * t * (3 - 2 * t)
    return 1.0 + t * (s_full - 1.0)

def alpha_limit(reach_m, payload_kg):
    return ALPHA_R1 * accel_scale(reach_m, payload_kg)

def elbow_total_est(static_Nm, inertial_at_R1_Nm, reach_m, payload_kg):
    """Estimate elbow |static|+|inertial| under the scaled alpha."""
    return abs(static_Nm) + abs(inertial_at_R1_Nm) * accel_scale(reach_m, payload_kg)
