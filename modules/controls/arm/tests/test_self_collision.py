import sys, numpy as np, mujoco
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import self_collision as S

def _mk():
    m, d = S.build_model(); d.qpos[:] = 0; d.qpos[2] = 1.16; d.qpos[3] = 1
    return m, d, S.Supervisor(m, d)

def _set(m, d, **kw):
    for k, v in kw.items(): d.qpos[m.jnt_qposadr[m.joint(k).id]] = np.radians(v)

def _step(m, d, q, dt=1e-3):
    for j in range(1, m.njnt):
        a = m.jnt_qposadr[j]; d.qpos[a] = np.clip(d.qpos[a] + q[m.jnt_dofadr[j]] * dt, *m.jnt_range[j])

def test_geometry_rev6b_and_chest():
    m, d, s = _mk(); mujoco.mj_kinematics(m, d); ft = np.zeros(6)
    dd = mujoco.mj_geomDistance(m, d, m.geom('l_hand').id, m.geom('ko_shroud_l').id, 1, ft)
    assert abs(dd - 0.087) < 0.002  # hand inboard face y 0.239 vs 0.150 + 2 mm skin
    assert m.geom('ko_chest').bodyid == m.body('torso').id

def test_shroud_follows_thigh():
    m, d, s = _mk(); mujoco.mj_kinematics(m, d); p0 = d.geom_xpos[m.geom('ko_shroud_l').id].copy()
    _set(m, d, l_hip_pitch=-60); mujoco.mj_kinematics(m, d)
    assert np.linalg.norm(d.geom_xpos[m.geom('ko_shroud_l').id] - p0) > 0.02

def test_damping_holds_target_in_walk():
    m, d, s = _mk(); _set(m, d, l_hip_pitch=-50)
    for _ in range(2000):
        qd = np.zeros(m.nv)
        qd[m.jnt_dofadr[m.joint('l_shoulder_roll').id]] = -3.0
        qd[m.jnt_dofadr[m.joint('l_wrist_yaw').id]] = -3.0
        _step(m, d, s.filter(qd, 'walk'))
    dmin = min(x for p, x, _ in s.last if p.kind == 'shroud' and p.side == 'l')
    assert dmin >= 0.010  # never below warn while commanded straight in

def test_thresholds_by_mode():
    m, d, s = _mk()
    assert np.allclose(s.thresholds('shroud', 'walk'), (0.015, 0.010, 0.005))
    assert np.allclose(s.thresholds('shroud', 'kneel'), (0.020, 0.015, 0.010))
    assert s.thresholds('chest', 'walk')[0] == 0.0

def test_transit_timer_per_pass():
    t = S.TransitTimer(1e-3, 0.5, 10.0, 0.2)
    for _ in range(499): assert t.allowed(); t.step(True)
    t.step(True); assert not t.allowed()
    t.step(False); assert t.allowed()

def test_transit_timer_window():
    t = S.TransitTimer(1e-3, 0.5, 10.0, 0.2); used = 0; peak = 0
    for k in range(30000):
        inside = (k % 1000) < 400 and t.allowed()
        t.step(inside); used += inside; peak = max(peak, t.window_used)
    assert peak <= 0.2 + 1e-9

def test_plume_exempt_only_in_walk():
    m, d, s = _mk()
    s.filter(np.zeros(m.nv), 'walk'); assert s.timers['l'].allowed()
    s.timers['l'].cur = 0.5  # pass budget used up
    s.filter(np.zeros(m.nv), 'walk'); assert not s.timers['l'].allowed() or s.timers['l'].cur == 0

def test_fall_override_only_if_clear():
    m, d, s = _mk()
    ok, _ = s.fall_pose_clear({'l_shoulder_pitch': np.radians(5)}, 'crouch'); assert ok
    bad = {'l_shoulder_pitch': np.radians(-60), 'l_shoulder_roll': np.radians(-15), 'l_shoulder_yaw': np.radians(-110),
           'l_elbow': np.radians(-130)}
    ok2, worst = s.fall_pose_clear(bad, 'crouch'); assert not ok2 and 'chest' in worst[1]

def test_wbc_hook():
    m, d, s = _mk(); _set(m, d, l_shoulder_roll=-15, l_hip_pitch=-60); s.filter(np.zeros(m.nv), 'walk')
    got = []
    class H:
        def add_nullspace_task(self, name, row, rate, weight): got.append((row.shape, rate))
    s.repulsive_tasks(H())
    assert got and all(g[0] == (m.nv,) and g[1] > 0 for g in got)

def test_panels_follow_thighs_and_id_worst_collides():
    m, d, s = _mk(); ft = np.zeros(6)
    def g(**kw):
        d.qpos[7:] = 0; _set(m, d, **kw); mujoco.mj_kinematics(m, d)
        return mujoco.mj_geomDistance(m, d, m.geom('ko_panel_l').id, m.geom('ko_panel_r').id, 0.3, ft)
    assert g() > 0.10
    assert g(l_hip_pitch=-100, r_hip_pitch=-100, l_hip_roll=-20, r_hip_roll=20) < 0.003  # ID df1e9e3 worst
    assert g(l_hip_yaw=45, r_hip_yaw=-45) < 0.003

def test_bilateral_soft_limit():
    r = np.radians
    ok, q, why = S.bilateral_soft_limit({'l_hip_pitch': r(-100), 'r_hip_pitch': r(-100), 'l_hip_roll': r(-20), 'r_hip_roll': r(20)})
    assert not ok and min(-q['l_hip_roll'], q['r_hip_roll']) <= 1e-9
    ok, q, _ = S.bilateral_soft_limit({'l_hip_yaw': r(45), 'r_hip_yaw': r(-45)})
    assert not ok and np.degrees(q['l_hip_yaw'] - q['r_hip_yaw']) <= 80 + 1e-6
    assert S.bilateral_soft_limit({'l_hip_pitch': r(-100), 'r_hip_pitch': r(-100), 'l_hip_roll': r(-20)})[0]  # one leg only

def test_leg_rows_stop_bilateral_approach():
    m, d, s = _mk(); dt = 1e-3
    legs = s.arm_dofs['legs']
    for _ in range(1500):
        qd = np.zeros(m.nv)
        for sd, sg in (('l', 1), ('r', -1)):
            qd[m.jnt_dofadr[m.joint(f'{sd}_hip_pitch').id]] = -2.0
            qd[m.jnt_dofadr[m.joint(f'{sd}_hip_roll').id]] = -1.0 * sg
        s.filter(np.zeros(m.nv), 'crouch')
        for row, lb in s.leg_constraint_rows():  # WBC stand-in: min-norm on the hip dofs
            e = lb - row @ qd; a = row[legs]
            if e > 0 and a @ a > 1e-12: qd[legs] += a * e / (a @ a)
        _step(m, d, qd)
    dmin = min(x for p, x, _ in s.last if p.kind == 'panel')
    assert dmin >= 0.005  # >= warn
