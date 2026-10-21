"""T&R owed case: mid-walk stumble start (Legs WBC walk 1.2 m/s, walk_1p2_r2 plan, gait_lib model, mass via LEGS_MASS),
lateral push on the pelvis 0.15 s in single support (first SS phase at/after t_push), push direction +/-y.
On fall detection (|pelvis roll| > 0.15 rad or roll rate > 0.8 rad/s) the WBC is dropped and fall mode takes over:
derated (x0.5) PD hold of the joint pose at detection [kp 300 kd 15 legs EST], knee cap 513a7d5/D98 (>=123 deg 50 N.m).
tuck variant: fall_mode.swing_leg_tuck on the WBC swing leg at detection. Logs first floor contact per leg geom
(order, speeds), peak foot contact force per foot, ankle pitch/roll hard-stop hits (angle + actuator torque at hit).
No gait files edited. Writes stumble_fall_results.json."""
import os, sys, json, itertools, math
os.environ.setdefault('MUJOCO_GL', 'disable')
import numpy as np, mujoco
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
LEGS = os.path.join(ROOT, 'modules', 'legs'); sys.path[:0] = [HERE, LEGS, os.path.join(LEGS, 'wbc')]
os.environ.setdefault('LEGS_LIMITS', 'r1')
from gait_lib import load
from controller import WalkController
from soft_limits import knee_torque_limit
from fall_mode import swing_leg_tuck, fall_detected

PLAN = os.path.join(LEGS, 'results', 'r2', 'walk_1p2_r2.npz')


def run(t_push, push, sgn, tuck, T_after=1.6, tuck_s=0.0):
    m = load(); m.opt.timestep = 0.001; d = mujoco.MjData(m)
    c = WalkController(m); c.initialize(d); c.use_plan(PLAN, d)
    names = [m.actuator(i).name for i in range(m.nu)]
    jid = [m.actuator_trnid[i, 0] for i in range(m.nu)]
    qa = np.array([m.jnt_qposadr[j] for j in jid]); va = np.array([m.jnt_dofadr[j] for j in jid])
    lim = 0.5 * m.actuator_ctrlrange[:, 1]
    leg = np.array([any(k in n for k in ('hip', 'knee', 'ankle')) for n in names])
    kp = np.where(leg, 300.0, 60.0); kd = np.where(leg, 15.0, 3.0)
    pel = c.pelvis; floor = {i for i in range(m.ngeom) if m.geom_type[i] == mujoco.mjtGeom.mjGEOM_PLANE}
    gname = {i: (m.geom(i).name or m.body(m.geom_bodyid[i]).name) for i in range(m.ngeom)}
    def side_of(i):
        b = m.body(m.geom_bodyid[i]).name.lower()
        return 'l' if b.startswith('l') else ('r' if b.startswith('r') else None)
    def part(i):
        b = m.body(m.geom_bodyid[i]).name.lower()
        return 'foot' if 'foot' in b or 'toe' in b else ('shank' if 'shank' in b or 'knee' in b or 'calf' in b else ('thigh' if 'thigh' in b else b))
    ank = {f'{s}_ankle_{a}': m.joint(f'{s}_ankle_{a}').id for s in 'lr' for a in ('pitch', 'roll')}
    t = 0.0; pushing = None; det = None; hold = None; swing = None; fell_walk = None
    first = {}; spd = {}; fpeak = {'l': 0.0, 'r': 0.0}; ank_hit = {}; f6 = np.zeros(6); zmin = 9
    n = int((t_push + 1.5 + T_after) / 0.001)
    for k in range(n):
        t = k * 0.001
        if pushing is None and t >= t_push and getattr(c, 'phase', '') == 'ss':
            pushing = t; swing = c.swing
        if pushing is not None and t < pushing + 0.15:
            d.xfrc_applied[pel, 1] = sgn * push
        else:
            d.xfrc_applied[pel, 1] = 0.0
        R = d.xmat[pel].reshape(3, 3); roll = math.atan2(R[2, 1], R[2, 2])
        if pushing is not None and det is None and fall_detected(roll, float(d.qvel[3])):
            det = t; hold = d.qpos[qa].copy(); hold0 = hold.copy()
            if tuck and swing:
                tg = swing_leg_tuck({nm: hold[i] for i, nm in enumerate(names)}, swing)
                hold = np.array([tg[nm] for nm in names])
        if det is None:
            try:
                c.step(d)
            except Exception as e:
                fell_walk = str(e)[:60]; det = t; hold = d.qpos[qa].copy()
        else:
            a_ = min(1.0, (t - det) / tuck_s) if tuck_s > 0 else 1.0
            tgt = hold0 + a_ * (hold - hold0)
            tau = np.clip(kp * (tgt - d.qpos[qa]) - kd * d.qvel[va], -lim, lim)
            for i, nm in enumerate(names):
                if nm.endswith('knee'):
                    L = knee_torque_limit(float(d.qpos[qa[i]]), 'FALL', float(lim[i])); tau[i] = float(np.clip(tau[i], -L, L))
            d.ctrl[:] = tau
        mujoco.mj_step(m, d)
        zmin = min(zmin, float(d.xpos[pel][2]))
        if det is None: continue
        for i in range(d.ncon):
            cc = d.contact[i]
            for a, b in ((cc.geom1, cc.geom2), (cc.geom2, cc.geom1)):
                if a in floor and b not in floor:
                    sd = side_of(b); p = part(b)
                    mujoco.mj_contactForce(m, d, i, f6)
                    if sd and p == 'foot': fpeak[sd] = max(fpeak[sd], float(f6[0]))
                    key = (sd, p)
                    if key not in first and t > det:
                        first[key] = round(t, 4); v6 = np.zeros(6)
                        mujoco.mj_objectVelocity(m, d, mujoco.mjtObj.mjOBJ_GEOM, b, v6, 0); spd[key] = round(float(np.linalg.norm(v6[3:])), 3)
        for r in range(d.nefc):
            if d.efc_type[r] == mujoco.mjtConstraint.mjCNSTR_LIMIT_JOINT:
                for nm, j in ank.items():
                    if d.efc_id[r] == j and nm not in ank_hit:
                        ai = names.index(nm)
                        ank_hit[nm] = dict(t=round(t, 4), angle_deg=round(math.degrees(float(d.qpos[m.jnt_qposadr[j]])), 1),
                                           motor_tau_Nm=round(float(d.ctrl[ai]), 1), limit_force_Nm=round(abs(float(d.efc_force[r])), 1))
    out = dict(tuck_s=tuck_s, t_push=t_push, push_N=push, dir=sgn, tuck=tuck, push_start=pushing, swing=swing, detect=det, walk_exc=fell_walk,
               fell=zmin < 0.5, pelvis_zmin=round(zmin, 3), foot_peak_N={k: round(v) for k, v in fpeak.items()}, ankle_stop_hits=ank_hit)
    for s_ in 'lr':
        fo = sorted((tt, p) for (sd, p), tt in first.items() if sd == s_)
        tk = min([first[(s_, p)] for p in ('shank', 'thigh') if (s_, p) in first], default=None); tf = first.get((s_, 'foot'))
        out[s_] = dict(order=[p for _, p in fo], t_knee=tk, t_foot=tf, v={p: spd[(s_, p)] for _, p in fo},
                       knee_first_foot_moving=bool(tk is not None and (tf is None or tk < tf - 0.005)))
    return out


if __name__ == '__main__':
    rows = []
    for tp, pu, sg, (tk, ts) in itertools.product((0.8, 1.4, 2.0), (250.0, 400.0, 550.0), (1, -1), ((False, 0.0), (True, 0.0), (True, 0.15))):
        r = run(tp, pu, sg, tk, tuck_s=ts); rows.append(r); print(json.dumps(r), flush=True)
    json.dump(dict(rows=rows), open(os.path.join(HERE, 'stumble_fall_results.json'), 'w'), indent=1)
