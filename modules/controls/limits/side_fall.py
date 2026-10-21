"""Side-fall sim set for T&R SIDE_FALL_LOAD (3c73260 S1/S2a/S2b/S2c, rev B 3b4c449 L39 hip-roll PU bumpers). Light MuJoCo.
sim/v3 + pads [EST]. Knee stop-zone cap (513a7d5) ON in every motors-on run. Hip-roll L39 bumper modelled as a
joint-space spring past the swept contact (-12 / +15 deg, sim jnt range widened to +-45): k 8.4 kN.m/rad linear to
2.3 deg (334 N.m), stiffening x4 to 3.6 deg, then 400 kN.m/rad 'bottomed' [all EST, T&R rev B]; unload x0.34.
Scenarios (side = direction of fall; mass 65/68/68.5 x push 250/400/550 N (0.15 s lateral on torso)):
  S1  : standing double support, lateral push, fall-mode derated hold (both feet planted at start).
  S2b : upright kneel on the pads (POSE_KNEEL), lateral push.
  S2c : stumble: the leg on the fall side unloaded in swing (hip pitch -0.6, knee 1.0, foot lifted ~10 cm), push.
Controller variants: base (derated pose hold + caps), tuck (swing-leg rule: on detect, swing knee -> 0.15 rad and
hip pitch -> 0 so the foot is the lowest point of the leg), damp (fall-mode hip-roll damping B on the roll joints,
derated), tuck+damp. Fall detect: |torso roll| > 0.15 rad or roll rate > 0.8 rad/s. Writes side_fall_results.json and
side_fall_hiproll_history.json (hip-roll angle/rate at 5 ms)."""
import os, sys, json, itertools, math
os.environ.setdefault('MUJOCO_GL', 'disable')
import numpy as np, mujoco
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import prone_data as P
from soft_limits import knee_torque_limit

BUMP_LO, BUMP_HI = math.radians(-12.0), math.radians(15.0)
K1, D1, D2 = 8400.0, math.radians(2.3), math.radians(3.6)
K2 = 4 * K1; KB = 400e3
RES = 0.34
DERATE = 0.5
E_GATE = 6.6
B_ROLL = 120.0   # N.m.s/rad fall-mode hip-roll damping


def bump_tau(pen):
    if pen <= 0: return 0.0
    if pen <= D1: return K1 * pen
    t1 = K1 * D1
    if pen <= D2: return t1 + K2 * (pen - D1)
    return t1 + K2 * (D2 - D1) + KB * (pen - D2)


def leg_geoms(m, side):
    return {g: m.geom(f'{side}_{g}').id for g in ('thigh', 'knee_pad', 'shank', 'calf', 'foot')}


def run(scn, fall_side, mass, push, ctrl='base', T=2.5, hist=False):
    s = P.Sim(mass); m, d = s.m, s.d
    sg = 1.0 if fall_side == 'l' else -1.0       # +y is left
    rj = {k: m.joint(f'{k}_hip_roll').id for k in 'lr'}
    for j in rj.values():
        m.jnt_range[j] = [-math.radians(45), math.radians(45)]
    if scn == 'S1':
        pose = dict(hip_pitch=-0.1, knee=0.2, ankle_pitch=-0.1); swing = None
    elif scn == 'S2b':
        pose = dict(P.POSE_KNEEL); swing = None
    else:
        pose = dict(hip_pitch=-0.1, knee=0.2, ankle_pitch=-0.1); swing = fall_side
    s.place(pose, 0.0)
    q = s.target(pose)
    if swing:
        for i, n in enumerate(s.names):
            if n == f'{swing}_hip_pitch': q[i] = -0.6
            if n == f'{swing}_knee': q[i] = 1.0
            if n == f'{swing}_ankle_pitch': q[i] = -0.3
        # stance on the other leg: shift by holding pose; lift happens under PD within settle
    for _ in range(300 if swing else 30):
        d.ctrl[:] = np.clip(s.pd(q), -s.lim, s.lim)
        if swing:   # support the torso while the leg lifts (settle only)
            d.xfrc_applied[s.torso, 1] = 0
        mujoco.mj_step(m, d)
    lim = s.lim.copy()
    ki = {k: s.names.index(f'{k}_knee') for k in 'lr'}
    ri = {k: s.names.index(f'{k}_hip_roll') for k in 'lr'}
    hp = {k: s.names.index(f'{k}_hip_pitch') for k in 'lr'}
    rq = {k: m.jnt_qposadr[rj[k]] for k in 'lr'}; rv = {k: m.jnt_dofadr[rj[k]] for k in 'lr'}
    kq = {k: m.jnt_qposadr[m.joint(f'{k}_knee').id] for k in 'lr'}
    LG = {k: leg_geoms(m, k) for k in 'lr'}
    gid2 = {}
    for k in 'lr':
        for g, i in LG[k].items(): gid2[i] = (k, g)
    first = {}; speeds = {}
    E = {'l': 0.0, 'r': 0.0}; bump_peak = {'l': 0.0, 'r': 0.0}; bump_pen = {'l': 0.0, 'r': 0.0}; wc = {'l': None, 'r': None}
    roll_tau_peak = {'l': 0.0, 'r': 0.0}
    zmin = 9.0; detected = None; H = []; zone_knee_cmd = 0.0
    t0 = m.opt.timestep
    for step in range(int(T / t0)):
        t = step * t0
        d.xfrc_applied[s.torso, 1] = sg * push if t < 0.15 else 0.0
        R = d.xmat[s.torso].reshape(3, 3); roll = math.atan2(R[2, 1], R[2, 2])
        w = d.qvel[3:6]
        if detected is None and (abs(roll) > 0.15 or abs(w[0]) > 0.8): detected = t
        qt = q.copy()
        if detected is not None and 'tuck' in ctrl and swing:
            qt[ki[swing]] = 0.15; qt[hp[swing]] = 0.0
        tau = np.clip(s.pd(qt), -DERATE * lim, DERATE * lim) if detected is not None else np.clip(s.pd(qt), -lim, lim)
        if detected is not None and 'damp' in ctrl:
            for k in 'lr':
                tau[ri[k]] = float(np.clip(-B_ROLL * d.qvel[rv[k]], -DERATE * lim[ri[k]], DERATE * lim[ri[k]]))
        if detected is not None:
            for k in 'lr':
                L = knee_torque_limit(float(d.qpos[kq[k]]), 'FALL', float(DERATE * lim[ki[k]]))
                tau[ki[k]] = float(np.clip(tau[ki[k]], -L, L))
                if d.qpos[kq[k]] >= math.radians(125): zone_knee_cmd = max(zone_knee_cmd, abs(tau[ki[k]]))
        for k in 'lr': roll_tau_peak[k] = max(roll_tau_peak[k], abs(tau[ri[k]]))
        d.ctrl[:] = tau
        for k in 'lr':
            qr, vr = float(d.qpos[rq[k]]), float(d.qvel[rv[k]])
            lo, hi = (BUMP_LO, BUMP_HI) if k == 'l' else (-BUMP_HI, -BUMP_LO)   # right side mirrored (-15/+12)
            pen, dirn = (lo - qr, -1) if qr < lo else ((qr - hi, 1) if qr > hi else (0.0, 0))
            tb = bump_tau(pen); comp = dirn * vr > 0
            if tb > 0:
                if wc[k] is None: wc[k] = round(abs(vr), 3)
                if not comp: tb *= RES
                else: E[k] += tb * abs(vr) * t0
                bump_peak[k] = max(bump_peak[k], tb); bump_pen[k] = max(bump_pen[k], pen)
            d.qfrc_applied[rv[k]] = -dirn * tb
        mujoco.mj_step(m, d)
        zmin = min(zmin, float(d.xpos[s.torso][2]))
        for i in range(d.ncon):
            c = d.contact[i]
            for a, b in ((c.geom1, c.geom2), (c.geom2, c.geom1)):
                if a in s.floor and b in gid2 and gid2[b] not in first:
                    first[gid2[b]] = round(t, 4)
                    v6 = np.zeros(6); mujoco.mj_objectVelocity(m, d, mujoco.mjtObj.mjOBJ_GEOM, b, v6, 0)
                    speeds[gid2[b]] = round(float(np.linalg.norm(v6[3:])), 3)
        if hist and step % 5 == 0:
            H.append([round(t, 3)] + [round(float(d.qpos[rq[k]]), 4) for k in 'lr'] + [round(float(d.qvel[rv[k]]), 3) for k in 'lr'] + [round(roll, 4)])
    # per fall-side leg: first leg contact, knee vs foot speed
    out = dict(scn=scn, side=fall_side, mass=mass, push_N=push, ctrl=ctrl, detect_s=detected)
    for k in 'lr':
        fo = sorted(((tt, g) for (kk, g), tt in first.items() if kk == k))
        kn = [first.get((k, g)) for g in ('knee_pad', 'shank', 'thigh')]; kn = min([x for x in kn if x is not None], default=None)
        ft = first.get((k, 'foot'))
        # foot speed at the time the knee landed (rel. to knee ~ knee arrested): record foot speed at knee contact via history not stored; use contact speeds
        out[k] = dict(contact_order=[g for _, g in fo], t_knee=kn, t_foot=ft,
                      knee_first_with_foot_airborne=bool(kn is not None and (ft is None or kn < ft - 0.005)),
                      v_knee_contact=next((speeds[(k, g)] for g in ('knee_pad', 'shank', 'thigh') if first.get((k, g)) == kn), None) if kn is not None else None,
                      v_foot_contact=speeds.get((k, 'foot')),
                      hip_roll_wc_rad_s=wc[k], bumper_E_J=round(E[k], 2), bumper_peak_Nm=round(bump_peak[k], 1),
                      bumper_pen_deg=round(math.degrees(bump_pen[k]), 2), hip_roll_motor_peak_Nm=round(roll_tau_peak[k], 1))
    out['torso_z_min_m'] = round(zmin, 3); out['fell'] = zmin < 0.5
    out['knee_zone_cmd_max_Nm'] = round(zone_knee_cmd, 1)
    out['E_max_J'] = max(out['l']['bumper_E_J'], out['r']['bumper_E_J'])
    out['pass_bumper'] = out['E_max_J'] <= E_GATE
    return (out, H) if hist else out


def sweep(ctrl):
    return [run(sc, sd, ms, pu, ctrl) for sc, sd, ms, pu in itertools.product(('S1', 'S2b', 'S2c'), 'lr', (65.0, 68.0, 68.5), (250.0, 400.0, 550.0))]


if __name__ == '__main__':
    res = {}
    for c in ('base', 'tuck', 'damp', 'tuck+damp'):
        rows = sweep(c)
        sm = {}
        for sc in ('S1', 'S2b', 'S2c'):
            r = [x for x in rows if x['scn'] == sc]
            legs = [x[k] for x in r for k in 'lr']
            sm[sc] = dict(n=len(r), n_fell=sum(x['fell'] for x in r), E_max_J=max(x['E_max_J'] for x in r),
                          wc_max=max((l['hip_roll_wc_rad_s'] or 0) for l in legs), bump_peak_Nm=max(l['bumper_peak_Nm'] for l in legs),
                          bump_pen_deg=max(l['bumper_pen_deg'] for l in legs), n_bump_fail=sum(not x['pass_bumper'] for x in r),
                          n_knee_first=sum(l['knee_first_with_foot_airborne'] for l in legs),
                          v_knee_max=max((l['v_knee_contact'] or 0) for l in legs), v_foot_max=max((l['v_foot_contact'] or 0) for l in legs),
                          knee_zone_cmd_max=max(x['knee_zone_cmd_max_Nm'] for x in r), roll_motor_peak=max(l['hip_roll_motor_peak_Nm'] for l in legs))
        res[c] = dict(summary=sm, rows=rows); print(c, json.dumps(sm), flush=True)
    res['meta'] = dict(E_gate_J=E_GATE, B_roll=B_ROLL, bumper='L39 PU [EST] k 8.4 kN.m/rad lin 2.3 deg, x4 to 3.6, bottom 400 kN.m/rad', basis='3c73260/3b4c449; sim/v3 + pads [EST]; knee cap 513a7d5 on')
    json.dump(res, open(os.path.join(HERE, 'side_fall_results.json'), 'w'), indent=1)
    hist = {}
    for c in ('base', 'damp'):
        for sc in ('S1', 'S2b', 'S2c'):
            _, H = run(sc, 'l', 68.0, 550.0, c, hist=True); hist[f'{sc}_l_68_550_{c}'] = dict(cols=['t', 'l_roll', 'r_roll', 'l_roll_rate', 'r_roll_rate', 'torso_roll'], data=H)
    json.dump(hist, open(os.path.join(HERE, 'side_fall_hiproll_history.json'), 'w'))
