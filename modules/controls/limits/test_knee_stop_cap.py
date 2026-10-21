import math, json, os
from soft_limits import knee_torque_limit, apply_knee_stop_cap, KNEE_CAP_NM, KNEE_CAP_START_RAD
import numpy as np

def test_cap_values():
    assert KNEE_CAP_NM == 50.0 and abs(math.degrees(KNEE_CAP_START_RAD) - 120.0) < 1e-9

def test_cap_on_top_of_derate():
    q = math.radians(124)
    assert knee_torque_limit(q, 'TUCK', 172.0) == 50.0
    assert knee_torque_limit(q, 'TUCK', 30.0) == 30.0          # derate lower -> derate wins
    assert knee_torque_limit(math.radians(119.9), 'TUCK', 172.0) == 172.0
    assert knee_torque_limit(q, 'RUN', 172.0) == 172.0          # walking unaffected

def test_apply():
    names = ['l_knee', 'r_knee', 'l_hip_pitch']
    tau = np.array([-200.0, 200.0, 300.0]); qs = {'l_knee': math.radians(130), 'r_knee': math.radians(100)}
    apply_knee_stop_cap(names, lambda n: qs[n], tau, 'KNEEL')
    assert list(tau) == [-50.0, 200.0, 300.0]

def test_results_capped_modes_pass():
    p = os.path.join(os.path.dirname(__file__), 'knee_stop_cap_results.json')
    d = json.load(open(p))
    for md in ('cap', 'ramp', 'ramp_knee_only'):
        assert d[md]['summary']['all']['n_fail'] == 0
        assert d[md]['summary']['all']['zone_cmd_max_Nm'] <= 50.0 + 1e-6
