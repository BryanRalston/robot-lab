import sys, os, pytest, numpy as np
H_ = os.path.dirname(__file__); sys.path.insert(0, os.path.join(H_, '..')); sys.path.insert(0, os.path.join(H_, '../../limits'))
import mo_off_rule as R, hip_pinch as H, hip_pinch_cap as C
D = np.radians

def test_mo_off_refused_standing_allowed_kneel_sit():
    for p in ('stand', 'walk', 'carry', 'crouch'):
        with pytest.raises(R.UnsupportedMoOff): R.command_mo_off(p)
    for p in ('kneel', 'sit'): assert R.command_mo_off(p)
    assert R.mo_off_allowed('stand', fault='power_loss')

def test_derate_state_machine_refuses_mo_off_standing():
    import test_drive_thermal_derate as T, drive_thermal_derate as DT
    io, sup, _ = T.make()
    with pytest.raises(DT.UnsupportedMoOff): sup._mo_off()
    assert all(io.mo.values())

def _q(a, b):
    return {'l_hip_pitch': D(a[0]), 'l_hip_roll': D(a[1]), 'l_hip_yaw': D(a[2]), 'r_hip_pitch': D(b[0]), 'r_hip_roll': D(-b[1]), 'r_hip_yaw': D(-b[2])}

def test_torque_cap_14_in_zone_only():
    tau = {'l_hip_roll': 80.0, 'r_hip_yaw': -60.0, 'l_hip_pitch': 200.0}
    c = C.HipPinchTorqueCap(); out = c.apply(tau, _q((38.9, 0.1, 37.7), (23.2, 3.2, 39.0)), 0.0)
    assert out['l_hip_roll'] == 14.0 and out['r_hip_yaw'] == -14.0 and out['l_hip_pitch'] == 200.0
    c = C.HipPinchTorqueCap(); assert c.apply(tau, _q((0, 0, 0), (0, 0, 0)), 0.0) == tau
