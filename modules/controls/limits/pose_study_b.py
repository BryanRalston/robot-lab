"""Robot Lab pose study (b): hands on the floor with knee <= 120 deg, hip pitch >= -105 deg, wider stance (+0.05/+0.10 m
per foot via hip roll), torso leaned over the hands; 50 N.m knee cap from 120 deg. sim/v3 + pads [EST].
1) STATIC: grid over knee / hip pitch / shoulder pitch / waist pitch / stance; for each, root pitch + ankle are solved so
   both feet are flat on the floor and both hands touch it (|z| <= 10 mm). Then CoM-over-support (x between heel and
   hand, y inside) and the torque budget from the contact-consistent static feed-forward (chest_lower_wbc.static_ff,
   min-norm support forces over feet + hands [EST: one of many force distributions]): leg derate x0.5, knee <= derate,
   elbow 38 (or 49) N.m, and hand normal force <= 875 N.
2) DYNAMIC: best static candidates placed in the pose and held 2 s (derated PD + static ff + knee cap); fall, hand peak N.
Writes pose_study_b.json."""
import os, sys, json, itertools, math
os.environ.setdefault('MUJOCO_GL', 'disable')
import numpy as np, mujoco
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import chest_lower_wbc as CL
from soft_limits import apply_knee_stop_cap

L_LEG = 0.80


def geom_zmin(m, d, g):
    R = d.geom_xmat[g].reshape(3, 3); c = d.geom_xpos[g]; h = m.geom_size[g]
    if m.geom_type[g] == mujoco.mjtGeom.mjGEOM_BOX:
        return min((c + R @ (np.array(sg) * h))[2] for sg in itertools.product((-1, 1), repeat=3))
    return c[2] - h[0]


def pose_state(s, spec, pitch, ankle):
    m, d = s.m, s.d
    sp = dict(spec, ankle_pitch=ankle)
    d.qpos[:] = 0; d.qvel[:] = 0; d.qpos[3:7] = [math.cos(pitch / 2), 0, math.sin(pitch / 2), 0]
    d.qpos[s.qadr] = s.target(sp)
    for side, sg in (('l', 1), ('r', -1)):
        d.qpos[s.qadr[s.names.index(f'{side}_hip_roll')]] = sg * spec.get('_roll', 0.0)
        d.qpos[s.qadr[s.names.index(f'{side}_ankle_roll')]] = -sg * spec.get('_roll', 0.0)
    d.qpos[2] = 1.0; mujoco.mj_forward(m, d)
    feet = [m.geom('l_foot').id, m.geom('r_foot').id]; hands = [m.geom('l_hand').id, m.geom('r_hand').id]
    zf = min(geom_zmin(m, d, g) for g in feet); d.qpos[2] -= zf; mujoco.mj_forward(m, d)
    tilt = max(abs(math.asin(np.clip(d.geom_xmat[g].reshape(3, 3)[2, 0], -1, 1))) for g in feet)
    zh = min(geom_zmin(m, d, g) for g in hands)
    others = min(geom_zmin(m, d, g) for g in range(m.ngeom) if g not in feet + hands and g not in s.floor and m.geom_bodyid[g] != 0)
    return tilt, zh, others


def solve(s, spec):
    best = None
    for pitch in np.linspace(0.6, 1.6, 41):
        for ank in np.linspace(-0.95, 0.7, 34):
            tilt, zh, oth = pose_state(s, spec, pitch, ank)
            sc = 0.5 * tilt + abs(zh) * 20 + (0 if oth > 0.01 else 5)   # toe support allowed (heels may lift)
            if best is None or sc < best[0]: best = (sc, pitch, ank, tilt, zh, oth)
    return best


def static_check(s, spec, pitch, ank, elbow_cap):
    m, d = s.m, s.d
    pose_state(s, spec, pitch, ank)
    feet = [m.geom('l_foot').id, m.geom('r_foot').id]; hands = [m.geom('l_hand').id, m.geom('r_hand').id]
    sup = feet + hands
    jp = np.zeros((3, m.nv)); Js = []
    for g in sup:
        mujoco.mj_jacGeom(m, d, jp, None, g); Js.append(jp.copy())
    Jc = np.vstack(Js); A = Jc[:, :6].T; b = d.qfrc_bias[:6]
    f = A.T @ np.linalg.solve(A @ A.T + 1e-6 * np.eye(6), b)
    tau = d.qfrc_bias[s.vadr] - Jc[:, s.vadr].T @ f
    lim = s.lim.copy()
    for i, n in enumerate(s.names):
        if n.endswith('elbow'): lim[i] = elbow_cap
    ratio = np.abs(tau) / lim; worst = int(np.argmax(ratio[:28]))
    fz = f.reshape(-1, 3)[:, 2]
    com = d.subtree_com[1]
    xs = [d.geom_xpos[g][0] for g in sup]
    return dict(hand_N=[round(float(fz[2]), 1), round(float(fz[3]), 1)], foot_N=[round(float(fz[0]), 1), round(float(fz[1]), 1)],
                com_in_x=bool(min(xs) - 0.12 <= com[0] <= max(xs)), worst_joint=s.names[worst], worst_ratio=round(float(ratio[worst]), 2),
                knee_tau=round(float(max(abs(tau[i]) for i, n in enumerate(s.names) if n.endswith('knee'))), 1),
                elbow_tau=round(float(max(abs(tau[i]) for i, n in enumerate(s.names) if n.endswith('elbow'))), 1))


def dynamic(spec, pitch, ank, elbow_cap, mass=68.0, T=2.0):
    s = CL.make_sim(mass); m, d = s.m, s.d
    for i, n in enumerate(s.names):
        if n.endswith('elbow'): s.lim[i] = elbow_cap
    pose_state(s, spec, pitch, ank); d.qpos[2] += 0.002; mujoco.mj_forward(m, d)
    q = d.qpos[s.qadr].copy()
    sup = [m.geom(g).id for g in ('l_foot', 'r_foot', 'l_hand', 'r_hand')]
    hands = sup[2:]; hpk = [0.0, 0.0]; f6 = np.zeros(6); kmax = 0.0; fell = False
    for _ in range(int(T / m.opt.timestep)):
        tau = np.clip(s.pd(q) + CL.static_ff(m, d, sup, s.vadr), -s.lim, s.lim)
        apply_knee_stop_cap(s.names, lambda n: float(d.qpos[s.qadr[s.names.index(n)]]), tau, 'KNEEL')
        d.ctrl[:] = tau; mujoco.mj_step(m, d)
        for ci in range(d.ncon):
            c = d.contact[ci]
            for k, g in enumerate(hands):
                if g in (c.geom1, c.geom2) and (c.geom1 in s.floor or c.geom2 in s.floor):
                    mujoco.mj_contactForce(m, d, ci, f6); hpk[k] = max(hpk[k], float(f6[0]))
        kmax = max(kmax, max(float(d.qpos[s.qadr[i]]) for i, n in enumerate(s.names) if n.endswith('knee')))
        if s.contacts()['chest_pad'] > 1 or s.contacts()['other'] > 50: fell = True
    return dict(fell=fell, hand_peak_N=[round(x, 1) for x in hpk], knee_max_deg=round(math.degrees(kmax), 1))


if __name__ == '__main__':
    s = CL.make_sim(68.0)
    rows = []
    for knee, hip, sh, wa, wid in itertools.product((1.75, 1.95, 2.09), (-1.30, -1.55, -1.83), (-1.4, -1.9), (0.0, 0.4), (0.0, 0.05, 0.10)):
        spec = dict(hip_pitch=hip, knee=knee, shoulder_pitch=sh, elbow=-0.13, wrist_pitch=-0.96, waist_pitch=wa, _roll=math.asin(wid / L_LEG))
        sc, pitch, ank, tilt, zh, oth = solve(s, spec)
        ok_geo = abs(zh) < 0.01 and oth > 0.01   # feet may be on the toes (tilt reported)
        row = dict(knee_deg=round(math.degrees(knee), 1), hip_deg=round(math.degrees(hip), 1), shoulder=sh, waist=wa, width_m=wid,
                   root_pitch=round(float(pitch), 3), ankle=round(float(ank), 3), foot_tilt=round(tilt, 3), hand_z=round(zh, 4), other_min_z=round(oth, 3), geom_ok=ok_geo)
        if ok_geo:
            for ec in (38.0, 49.0):
                row[f'static_{int(ec)}'] = static_check(s, spec, pitch, ank, ec)
        rows.append(row)
    stat_pass = [r for r in rows if r['geom_ok'] and any(r.get(f'static_{e}', {}).get('worst_ratio', 9) <= 1.0 and max(r[f'static_{e}']['hand_N']) <= 875 and r[f'static_{e}']['com_in_x'] for e in (38, 49))]
    print('geom_ok', sum(r['geom_ok'] for r in rows), 'of', len(rows), 'static pass', len(stat_pass), flush=True)
    dyn = []
    cand = sorted([r for r in rows if r['geom_ok']], key=lambda r: min(r[f'static_{e}']['worst_ratio'] for e in (38, 49)))[:6]
    for r in cand:
        spec = dict(hip_pitch=math.radians(r['hip_deg']), knee=math.radians(r['knee_deg']), shoulder_pitch=r['shoulder'], elbow=-0.13, wrist_pitch=-0.96, waist_pitch=r['waist'], _roll=math.asin(r['width_m'] / L_LEG))
        for ec in (38.0, 49.0):
            dd = dict(r, elbow_cap=ec, **dynamic(spec, r['root_pitch'], r['ankle'], ec)); dyn.append(dd); print(json.dumps({k: dd[k] for k in ('knee_deg', 'hip_deg', 'shoulder', 'waist', 'width_m', 'elbow_cap', 'fell', 'hand_peak_N', 'knee_max_deg')}), flush=True)
    json.dump(dict(static=rows, static_pass=len(stat_pass), dynamic=dyn), open(os.path.join(HERE, 'pose_study_b.json'), 'w'), indent=1, default=float)
