import math, numpy as np
from hip_stop_l90 import hip_stop_l90, clip_hip_l90
D = math.pi / 180


def v(r, y, s): return hip_stop_l90(r * D, y * D, s) / D


def test_corners_left():
    for r, lo, hi in [(0, -12, 28), (-3, -12, 28), (-10, -12 + 7 * 7 / 9, 28 - 14)]:
        assert abs(v(r, lo, 'L')) < 1e-9 and abs(v(r, hi, 'L')) < 1e-9
        assert abs(v(r, hi + 1, 'L') - 1) < 1e-9 and abs(v(r, lo - 1, 'L') - 1) < 1e-9
    assert abs(v(-11, 0, 'L') - 1) < 1e-9          # roll past -10 controlled limit


def test_r12_corner_band():
    import numpy as np
    from hip_stop_l90 import _bounds
    lo, hi = _bounds(np, -12 * D)
    assert abs(lo / D + 5) < 1e-9 and abs(hi / D - 10) < 1e-9
    assert abs(v(-12, 0, 'L') - 2) < 1e-9          # -12 is past the -10 controlled limit by 2 deg
    lo, hi = _bounds(np, -12 * D)                  # right mirror: r=+12 -> yaw -10..+5
    assert abs(v(12, -10, 'R') - v(-12, 10, 'L')) < 1e-12


def test_corners_right_mirrored():
    for r, y in [(0, 28), (0, -12), (12, 5), (12, -10), (3, -28)]:
        assert abs(v(r, -y if False else y, 'R') - v(-r, -y, 'L')) < 1e-12
    assert abs(v(0, -28, 'R')) < 1e-9 and abs(v(0, 12, 'R')) < 1e-9 and abs(v(0, 13, 'R') - 1) < 1e-9
    assert abs(v(12, -10, 'R')) > 0                 # +12 roll on right > +10 limit


def test_clip_lands_on_surface():
    rng = np.random.default_rng(0)
    for s in 'LR':
        r = rng.uniform(-20, 20, 500) * D; y = rng.uniform(-40, 40, 500) * D
        rc, yc = clip_hip_l90(r, y, s)
        assert np.all(hip_stop_l90(rc, yc, s) < 1e-12)
