import json, os
from fall_mode import swing_leg_tuck, fall_detected
H = os.path.dirname(__file__)

def test_rule():
    t = swing_leg_tuck({'l_knee': 1.0, 'r_knee': 0.2, 'l_hip_pitch': -0.6}, 'l')
    assert t['l_knee'] == 0.15 and t['l_hip_pitch'] == 0.0 and t['r_knee'] == 0.2
    assert fall_detected(0.2, 0) and not fall_detected(0.1, 0.5)

def test_results():
    d = json.load(open(os.path.join(H, 'side_fall_results.json')))
    for sc in ('S1', 'S2b', 'S2c'):
        assert d['tuck']['summary'][sc]['n_bump_fail'] == 0
        assert d['tuck']['summary'][sc]['knee_zone_cmd_max'] <= 50.0

def test_tuck_gated_in_swing():
    q = {'l_knee': 1.0, 'l_hip_pitch': -0.6}
    assert swing_leg_tuck(q, 'l', 'ss') == q
    assert swing_leg_tuck(q, 'l', 'ds')['l_knee'] == 0.15
