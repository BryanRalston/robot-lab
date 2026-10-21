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
