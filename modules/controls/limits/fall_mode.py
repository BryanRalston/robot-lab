"""Fall/TUCK-state leg rules (side_fall.py / SIDE_FALL.md, T&R 3c73260 S2c + 3b4c449).
Swing-leg tuck rule: on fall detection (|torso roll| > 0.15 rad or roll rate > 0.8 rad/s), the unloaded (swing) leg
is commanded to knee 0.15 rad and hip pitch 0 (foot = lowest point of the leg, lands first). Torques then go through
the derate and the 513a7d5 knee cap (soft_limits.knee_torque_limit). Hip-roll damping is NOT enabled (it raised S1/S2b
bumper energy in sim)."""
SWING_KNEE_RAD, SWING_HIP_PITCH_RAD = 0.15, 0.0
DETECT_ROLL_RAD, DETECT_ROLL_RATE = 0.15, 0.8


def fall_detected(torso_roll, roll_rate):
    return abs(torso_roll) > DETECT_ROLL_RAD or abs(roll_rate) > DETECT_ROLL_RATE


TUCK_PHASES = frozenset(('stand', 'balance', 'ds', 'double'))   # Robot Lab ruling on 976eca8: standing/double support only


def tuck_allowed(support_phase):
    """Swing-leg tuck only from standing / double support; disabled in single support (mid-stride whips the foot)."""
    return support_phase in TUCK_PHASES


def swing_leg_tuck(targets, swing_side, support_phase='stand'):
    """targets: dict joint-name -> rad (modified copy). swing_side 'l'/'r' or None. No-op in single support ('ss')."""
    t = dict(targets)
    if swing_side and tuck_allowed(support_phase):
        t[f'{swing_side}_knee'] = SWING_KNEE_RAD; t[f'{swing_side}_hip_pitch'] = SWING_HIP_PITCH_RAD
    return t


# Robot Lab CONTRACT (R-146a TUCK): knee drives stay ON through the fall, pre-stop damping ramp 95->123 deg
# (B 0->60 N.m.s/rad), |tau| <= 50 N.m at >= 123 deg (D98 contact 133 deg), knee drives are the LAST to drop.
import math, math as _m, json as _j, os as _o
_C = _j.load(open(_o.path.join(_o.path.dirname(_o.path.abspath(__file__)), 'soft_limits.json')))['knee_fall_ramp']
RAMP_START_RAD, RAMP_END_RAD, RAMP_B = _m.radians(_C['start_deg']), _m.radians(_C['end_deg']), _C['B_max_Nms_per_rad']
KNEE_DROP_LAST = True


def knee_fall_torque(q, qdot, derated_lim):
    """Fall/TUCK knee command: damping on flexion only, ramped, clipped to derate and the stop-zone cap."""
    from soft_limits import knee_torque_limit
    B = RAMP_B * min(1.0, max(0.0, (q - RAMP_START_RAD) / (RAMP_END_RAD - RAMP_START_RAD)))
    tau = -B * max(qdot, 0.0)
    L = knee_torque_limit(q, 'TUCK', derated_lim)
    return max(-L, min(L, tau))


def mo_off_order(drives):
    """Drop order for a fall/TUCK MO=0: every non-knee drive first, knees last (contract)."""
    return [d for d in drives if not d.endswith('knee')] + [d for d in drives if d.endswith('knee')]


# Waist-pitch TUCK damping (RL Controls, Robot Lab ask after Actuators D102): analogous to the knee ramp. Drive powered
# in TUCK; damping B ramps 0 -> B_max over the last WAIST_RAMP_DEG before each end (-30 / +60), applied only to motion
# toward that end, clipped to the drive limit, then the D102 stop-zone zero (last 3 deg: no torque toward the end;
# a damping torque opposes motion toward the end, so it is AWAY from the end and is kept by the zero).
WAIST_RAMP_DEG = 20.0
WAIST_DRIVE_PEAK_NM = 115.4   # CONTRACTS.md waist_pitch row (TBM2G-06808A + CSG-25-100)


def waist_fall_torque(q, qdot, B_max, lim=WAIST_DRIVE_PEAK_NM, ramp_deg=WAIST_RAMP_DEG):
    from soft_limits import WAIST_LO_RAD, WAIST_HI_RAD, waist_stop_zone_tau
    r = math.radians(ramp_deg); tau = 0.0
    if qdot > 0:
        tau = -B_max * min(1.0, max(0.0, (q - (WAIST_HI_RAD - r)) / r)) * qdot
    elif qdot < 0:
        tau = -B_max * min(1.0, max(0.0, ((WAIST_LO_RAD + r) - q) / r)) * qdot
    L = min(lim, WAIST_DRIVE_PEAK_NM)
    return waist_stop_zone_tau(q, max(-L, min(L, tau)))
