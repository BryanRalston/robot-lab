import sys, os, numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
import hip_pinch as H
R = np.radians

def q(lp, lr, ly, rp, rr, ry):  # T&R (p, r, y) per leg; right leg -> sim mirror (p, -r, -y)
    return {'l_hip_pitch': R(lp), 'l_hip_roll': R(lr), 'l_hip_yaw': R(ly),
            'r_hip_pitch': R(rp), 'r_hip_roll': R(-rr), 'r_hip_yaw': R(-ry)}

def test_thresholds():
    assert (H.WARN, H.LIMIT, H.TRIP) == (40.0, 35.0, 33.0)
    assert [H.status(x) for x in (45, 38, 34, 32)] == ['ok', 'warn', 'limit', 'trip']

def test_zero_pose_clear():
    g = H.gaps(q(0, 0, 0, 0, 0, 0)); assert min(g.values()) > 100

def test_tr_76de66a_worst_pair_trips():
    """T&R 76de66a (corrected 04c7199 pose): L (23.1, -13.0, 38.0) / R (40.4, +2.7, 46.1); T&R rev 8b 0.77 mm, rev 8c -1.7 mm."""
    g = H.gaps(q(23.1, -13.0, 38.0, 40.4, 2.7, 46.1))
    assert g['lr'] < H.TRIP and H.status(min(g.values())) == 'trip'

def test_tr_76de66a_untripped_pair_now_trips():
    """T&R 76de66a: L (38.9, 0.1, 37.7) / R (23.2, 3.2, 39.0), rev 8c 23.6 mm, was 28.4 (untripped) in the rev 8b model."""
    g = H.gaps(q(38.9, 0.1, 37.7, 23.2, 3.2, 39.0))
    assert g['lr'] < H.TRIP and H.status(min(g.values())) == 'trip'


def test_guard_stops_closing_pair_at_trip():
    qq = q(23.1, -13.0, 38.0, 40.4, 2.7, 46.1); gd = H.HipPinchGuard()
    G = H.gaps(qq); key = min(G, key=G.get); gr = gd.grad(qq, key)
    qd = {n: -0.5 * np.sign(gr[n]) for n in gr}  # all joints closing
    out, g, st = gd.filter(qq, qd)
    assert st == 'trip'
    assert sum(gr[n] * out[n] for n in gr) >= -1e-9

def test_tr_42c4e50_8f_closures_all_trip_at_33():
    """T&R 42c4e50: rev 8f L/R closures (nominal, +2.5, +3.6 deg overtravel) that the old model missed at 28 must trip at 33."""
    import json, pathlib
    rows = json.loads((pathlib.Path(__file__).resolve().parents[1] / 'hip_pinch_8f_untripped_check.json').read_text())
    assert len(rows) == 15
    for r in rows:
        g = H.gaps(q(*r['a'], *r['b'])); assert min(g.values()) < H.TRIP, r
        assert abs(g['lr'] - r['tr_8f']) < 1.0, r  # agrees with T&R 8f within 1 mm
