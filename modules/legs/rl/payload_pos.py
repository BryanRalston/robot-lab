"""Carry payload position (torso frame, origin = waist_pitch axis). Arbiter R-117.

The gate point is P-042 (0.32, 0, 0.415). Training randomizes over a box that also covers Legs' (0.25, 0, 0.10).
Pure python so it can be tested on the box without JAX.
"""
P042 = (0.32, 0.0, 0.415)
LEGS = (0.25, 0.0, 0.10)
# Default DR box: both points plus 1-2 cm margin.
DEFAULT_LOW = (0.24, -0.02, 0.09)
DEFAULT_HIGH = (0.33, 0.02, 0.425)


def bounds(stage):
    """(low, high) from a train_cfg stage's `payload_pos: [[lo..], [hi..]]`, else the default box."""
    pp = stage.get('payload_pos') if stage else None
    if not pp:
        return DEFAULT_LOW, DEFAULT_HIGH
    lo, hi = tuple(float(v) for v in pp[0]), tuple(float(v) for v in pp[1])
    if any(l > h for l, h in zip(lo, hi)):
        raise ValueError(f'payload_pos low > high: {lo} {hi}')
    return lo, hi


def covers(lo, hi, point):
    return all(l - 1e-9 <= p <= h + 1e-9 for l, h, p in zip(lo, hi, point))
