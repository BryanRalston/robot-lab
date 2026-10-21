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


from hip_stop_l90 import hip_stop_pair, clip_hip_pair


def P(rL, yL, pL, rR, yR, pR):
    a, b = hip_stop_pair(rL * D, yL * D, pL * D, rR * D, yR * D, pR * D)
    return a / D, b / D


def test_l93_adduction_limits():
    assert abs(P(-5, 0, 0, 0, 0, 0)[0]) < 1e-9 and abs(P(-6, 0, 0, 0, 0, 0)[0] - 1) < 1e-9       # dp<10, other not adducted
    assert abs(P(-3.5, 0, 0, 3.5, 0, 0)[0] - 1) < 1e-9                                         # both adduct (R +3.5) -> 2.5
    assert abs(P(-3.5, 0, 0, 3.5, 0, 0)[1] - 1) < 1e-9                                         # mirrored right
    assert abs(P(-10, 0, 25, 0, 0, 0)[0]) < 1e-9 and abs(P(-7.5, 0, 15, 0, 0, 0)[0]) < 1e-9    # dp>=20 -> 10; dp 15 -> 7.5
    assert abs(P(-8.5, 0, 15, 0, 0, 0)[0] - 1) < 1e-9


def test_l93_toe_out():
    assert abs(P(0, 16, 0, 0, 0, 0)[0]) < 1e-9 and abs(P(0, 17, 0, 0, 0, 0)[0] - 1) < 1e-9
    assert abs(P(-3, 14, 0, 0, 0, 0)[0] - 1) < 1e-9                                            # 13 at r=-3 [EST]
    assert abs(P(0, 28, 30, 0, 0, 0)[0] - 1) < 1e-9 and abs(P(0, 27, 30, 0, 0, 0)[0]) < 1e-9   # cap 27
    assert abs(P(-10, 14, 30, 0, 0, 0)[0]) < 1e-9 and abs(P(-10, 15, 30, 0, 0, 0)[0] - 1) < 1e-9  # L92 below
    assert abs(P(0, -12, 0, 0, 0, 0)[0]) < 1e-9 and abs(P(0, -13, 0, 0, 0, 0)[0] - 1) < 1e-9
    assert abs(P(0, 0, 0, 0, -17, 0)[1] - 1) < 1e-9                                            # right toe-out mirrored


def test_l93_clip():
    rng = np.random.default_rng(1); n = 2000
    x = [rng.uniform(-15, 15, n) * D, rng.uniform(-35, 35, n) * D, rng.uniform(-40, 40, n) * D,
         rng.uniform(-15, 15, n) * D, rng.uniform(-35, 35, n) * D, rng.uniform(-40, 40, n) * D]
    rL, yL, rR, yR = clip_hip_pair(*x)
    a, b = hip_stop_pair(rL, yL, x[2], rR, yR, x[5])
    assert a.max() < 1e-9 and b.max() < 1e-9
