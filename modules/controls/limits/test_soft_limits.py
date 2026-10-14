"""Light tests for soft limits + R-085 accel blend."""
import math
from soft_limits import roll_soft_limit_rad, clamp_q, elbow_hard_cap_Nm
from elbow_accel_limit import accel_scale, alpha_limit, elbow_total_est, ALPHA_R1

def test_roll_soft():
    lo, hi = roll_soft_limit_rad('l')
    assert abs(hi - math.radians(135)) < 1e-9
    assert clamp_q('shoulder_roll', math.radians(150), 'l') == hi

def test_elbow_cap():
    assert elbow_hard_cap_Nm() == 69.0

def test_r085_blend():
    assert accel_scale(0.40, 10.0) == 1.0
    assert abs(accel_scale(0.667, 10.0) - 0.84) < 1e-9
    assert accel_scale(0.665, 8.0) == 1.0
    mid = accel_scale(0.58, 10.0)
    assert 0.84 < mid < 1.0
    # after +15 mm forearm hand estimate
    tot = elbow_total_est(42.62, 31.06, 0.667, 10.0)
    assert tot <= 69.0  # 0.84 -> 68.71
    assert abs(alpha_limit(0.667, 10.0) - ALPHA_R1 * 0.84) < 1e-9

if __name__ == '__main__':
    test_roll_soft(); test_elbow_cap(); test_r085_blend(); print('ok')
