"""Fall/TUCK-state leg rules (side_fall.py / SIDE_FALL.md, T&R 3c73260 S2c + 3b4c449).
Swing-leg tuck rule: on fall detection (|torso roll| > 0.15 rad or roll rate > 0.8 rad/s), the unloaded (swing) leg
is commanded to knee 0.15 rad and hip pitch 0 (foot = lowest point of the leg, lands first). Torques then go through
the derate and the 513a7d5 knee cap (soft_limits.knee_torque_limit). Hip-roll damping is NOT enabled (it raised S1/S2b
bumper energy in sim)."""
SWING_KNEE_RAD, SWING_HIP_PITCH_RAD = 0.15, 0.0
DETECT_ROLL_RAD, DETECT_ROLL_RATE = 0.15, 0.8


def fall_detected(torso_roll, roll_rate):
    return abs(torso_roll) > DETECT_ROLL_RAD or abs(roll_rate) > DETECT_ROLL_RATE


def swing_leg_tuck(targets, swing_side):
    """targets: dict joint-name -> rad (modified copy). swing_side 'l'/'r' or None."""
    t = dict(targets)
    if swing_side:
        t[f'{swing_side}_knee'] = SWING_KNEE_RAD; t[f'{swing_side}_hip_pitch'] = SWING_HIP_PITCH_RAD
    return t
