import sys, os, numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
import hip_pinch as H
R = np.radians

def q(lp, lr, ly, rp, rr, ry):  # T&R (p, r, y) per leg; right leg -> sim mirror (p, -r, -y)
    return {'l_hip_pitch': R(lp), 'l_hip_roll': R(lr), 'l_hip_yaw': R(ly),
            'r_hip_pitch': R(rp), 'r_hip_roll': R(-rr), 'r_hip_yaw': R(-ry)}

def test_thresholds():
    assert (H.WARN, H.LIMIT, H.TRIP) == (35.0, 30.0, 28.0)
    assert [H.status(x) for x in (40, 33, 29, 27)] == ['ok', 'warn', 'limit', 'trip']

def test_zero_pose_clear():
    g = H.gaps(q(0, 0, 0, 0, 0, 0)); assert min(g.values()) > 100

def test_tr_04c7199_worst_case_extension_yaw():
    """T&R 04c7199: 0.77 mm, both legs extended (+23/+40 pitch), yaw 38/46, rigid edge to rigid edge."""
    g = min(H.gaps(q(23, 0, 38, 40, 0, 46)).values())
    assert g < H.TRIP

def test_guard_stops_closing_pair_at_trip():
    qq = q(23, 0, 38, 40, 0, 46); gd = H.HipPinchGuard()
    G = H.gaps(qq); key = min(G, key=G.get); gr = gd.grad(qq, key)
    qd = {n: -0.5 * np.sign(gr[n]) for n in gr}  # all joints closing
    out, g, st = gd.filter(qq, qd)
    assert st == 'trip'
    assert sum(gr[n] * out[n] for n in gr) >= -1e-9
