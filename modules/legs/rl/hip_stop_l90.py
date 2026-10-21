"""L90 coupled hip yaw/roll stop (Legs 8569e3a, final surface incl. yaw_min -12 update, 2026-10-21).
Left, degrees, roll r (neg = adduction), yaw y (pos = toe-out):
  r >= -3:        y in [-12, +28]
  -3 > r >= -12:  y_max = 28 - 2(-3-r), y_min = -12 + (7/9)(-3-r)   -> +10/-5 at r=-12
  roll controlled limit -10 (first contact; -12.3 full crush). Right: mirrored (roll, yaw sign flipped).
Works on numpy or jax arrays (radians in/out). MuJoCo has no coupled limit, so the env uses:
  hip_stop_l90 violation -> penalty + termination, and clip_hip_l90 in the action->target map."""
import math
D = math.pi / 180.0
ROLL_MIN = -10.0 * D   # controlled adduction limit (left frame)
TERM_RAD = 3.6 * D     # stop is rigid by ~3.6 deg of crush: beyond this the violation terminates


def _bounds(xp, r_left):
    a = xp.clip(-3.0 * D - r_left, 0.0, None)          # adduction depth past -3 deg
    return -12.0 * D + (7.0 / 9.0) * a, 28.0 * D - 2.0 * a


def _to_left(roll, yaw, side):
    s = 1.0 if side in ('L', 'l', 0) else -1.0
    return s * roll, s * yaw, s


def hip_stop_l90(roll, yaw, side, xp=None):
    """Violation (rad, >=0) of the L90 surface: max of roll past -10 and yaw outside the coupled band."""
    if xp is None:
        import numpy as xp
    r, y, _ = _to_left(roll, yaw, side)
    ymin, ymax = _bounds(xp, r)
    return xp.maximum(xp.maximum(ROLL_MIN - r, 0.0), xp.maximum(xp.maximum(ymin - y, y - ymax), 0.0))


def clip_hip_l90(roll, yaw, side, xp=None):
    """Project a (roll, yaw) target into the surface: clip roll at -10, then yaw into the band at that roll."""
    if xp is None:
        import numpy as xp
    r, y, s = _to_left(roll, yaw, side)
    r = xp.maximum(r, ROLL_MIN)
    ymin, ymax = _bounds(xp, r)
    return s * r, s * xp.clip(y, ymin, ymax)


# ---- L93/L93b (Legs 955d2c8 / 7b519dd): final job 10 surface, both legs (2026-10-21) ----
# dp = |pitch_L - pitch_R|. Per leg, in the left frame (right mirrored):
#   adduction limit a_lim: dp<10: 5 deg if the other leg is not adducted, 2.5 deg if both adduct; dp>=20: 10; linear in 10..20.
#   toe-out max: dp<10: 16 at r>=0, linear to 13 at r=-3 [EST], below -3 min(13, L92); dp>=10: min(L92, 27).
#   inward yaw min: L92 (-12, coupled). Mechanical box stays at -10 roll.

def _lim_pair(xp, r_self, r_other, dp):
    both = (r_self < 0.0) & (r_other < 0.0)
    a_small = xp.where(both, 2.5 * D, 5.0 * D)
    t = xp.clip((dp - 10.0 * D) / (10.0 * D), 0.0, 1.0)
    a_lim = a_small + t * (10.0 * D - a_small)
    ymin, ymax92 = _bounds(xp, r_self)
    small = xp.minimum(xp.maximum(16.0 * D + r_self, 13.0 * D), 16.0 * D)   # 16 @ r>=0 -> 13 @ r<=-3 [EST]
    ymax = xp.where(dp < 10.0 * D, xp.minimum(small, ymax92), xp.minimum(ymax92, 27.0 * D))
    return -a_lim, ymin, ymax


def hip_stop_pair(rL, yL, pL, rR, yR, pR, xp=None):
    """L93 violation (rad, >=0) for (left, right). Inputs in the joint frame (right roll/yaw mirrored internally)."""
    if xp is None:
        import numpy as xp
    dp = xp.abs(pL - pR)
    l_r, l_y, r_r, r_y = rL, yL, -rR, -yR
    out = []
    for r, y, ro in ((l_r, l_y, r_r), (r_r, r_y, l_r)):
        rmin, ymin, ymax = _lim_pair(xp, r, ro, dp)
        out.append(xp.maximum(xp.maximum(rmin - r, 0.0), xp.maximum(xp.maximum(ymin - y, y - ymax), 0.0)))
    return out[0], out[1]


def clip_hip_pair(rL, yL, pL, rR, yR, pR, xp=None):
    """Project both hips' (roll, yaw) targets onto the L93 surface (roll first, then yaw at the clipped roll)."""
    if xp is None:
        import numpy as xp
    dp = xp.abs(pL - pR)
    l_r, r_r = rL, -rR
    rminL, _, _ = _lim_pair(xp, l_r, r_r, dp); rminR, _, _ = _lim_pair(xp, r_r, l_r, dp)
    l_r = xp.maximum(l_r, rminL); r_r = xp.maximum(r_r, rminR)
    _, a, b = _lim_pair(xp, l_r, r_r, dp); yl = xp.clip(yL, a, b)
    _, a, b = _lim_pair(xp, r_r, l_r, dp); yr = xp.clip(-yR, a, b)
    return l_r, yl, -r_r, -yr
