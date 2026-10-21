import sys, os, numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
import limp_hip_hold as L, hip_pinch as H, self_collision as S
R = np.radians

def test_low_current_hold_force_le_foam_limit():
    assert L.clamp_force(L.LimpHipHold().tau_hold) <= 127.0

def test_pre_limp_posture_clears_warn():
    q = {'l_hip_pitch': R(23.1), 'l_hip_roll': R(-13), 'l_hip_yaw': R(38), 'r_hip_pitch': R(40.4), 'r_hip_roll': R(-2.7), 'r_hip_yaw': R(-46.1)}
    t, g, ok = L.pre_limp_posture(q); assert ok and min(g.values()) >= H.WARN

def test_supervisor_blocks_planned_mo_off_in_pinch():
    m, d = S.build_model(); s = S.Supervisor(m, d)
    q = {'l_hip_pitch': R(23.1), 'l_hip_roll': R(-13), 'l_hip_yaw': R(38), 'r_hip_pitch': R(40.4), 'r_hip_roll': R(-2.7), 'r_hip_yaw': R(-46.1)}
    cmd, ok, g = s.limp_hip(q, mo_on=True, planned_mo_off=True)
    assert ok is False and len(cmd) == 4 and all(v[2] <= 19.05 for v in cmd.values())
    assert s.limp_hip({}, mo_on=False)[0] == {}
