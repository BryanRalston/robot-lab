"""D99 (Actuators 63f9a24) knee stop: contact 130 deg, quasi-static curve 130/0 131.1/75 132.7/152 135.4/329 138.2/491
140.9/645 143.6/790 N.m (bottoming 95.8 J), and x1.3 stiffness [EST fall rate]; unload x0.34. Armature J(q) table, 0.1 at >= 130.
Cap >= 120 deg (50 N.m), ramp 90->120 deg (departs from the ruled 95-125). Powered gate 44.1 J/knee.
Original: D98 (f771262) interim knee stop: contact 133 deg, PU curve 133/0, 133.85/93, 135.12/188, 137.24/408, 139.36/608,
141.48/799, 143.6/978 N.m (bottoming 92.5 J; beyond 143.6 a rigid 400 kN.m/rad [EST]); unload x0.34.
Knee armature angle-dependent (D98 J_refl table, interpolated each step): 0/0.079 30/0.314 75/0.553 120/0.230 133/0.10 135/0.083.
Same 90-case fall set as knee_stop_impact (3 cases x leans x mass 65/68/68.5); the old armature DR axis is replaced by
the J(q) table, so the 3rd DR axis is J(q) x {0.8, 1.0, 1.2} [EST spread].
Modes:
  contract   : Robot Lab contract (R-146a TUCK): knee drives ON, fall_mode.knee_fall_torque (ramp 95->123, cap 50 >=123),
               every other drive tripped (MO=0, D94 friction) - knees drop last.
  contract_hold : same knees, other drives holding the start pose derated x0.5.
  mo0        : knee drive tripped too (no guarantee claimed).
  short_brake: knee tripped with phase short [EST]: tau = -B_sb(q)*qdot, B_sb = 2 rotors x b_m x N(q)^2,
               N(q) = 2 pi arm(q)/5 mm (D98 linkage), b_m = Kt*Ke/R_ph [EST 0.05 N.m.s/rad per motor; NOT MODELLED by Electronics].
Writes knee_stop_d99_results.json."""
import os, sys, json, itertools, math
os.environ.setdefault('MUJOCO_GL', 'disable')
import numpy as np, mujoco
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import prone_data as P
import knee_stop_impact as K
from drive_thermal_derate import friction_hold
from fall_mode import knee_fall_torque

STOP = 130.0   # D99 (63f9a24) contact 130 deg
PU_DEG = np.array([130.0, 131.1, 132.7, 135.4, 138.2, 140.9, 143.6]) - STOP   # D99 quasi-static
PU_NM = np.array([0.0, 75, 152, 329, 491, 645, 790])
KSCALE = 1.0   # 1.3 = fall-rate stiffening [EST]
RES, KB = 0.34, 400e3
J_DEG = np.array([0, 30, 75, 120, 133, 135]); J_KG = np.array([0.079, 0.314, 0.553, 0.230, 0.10, 0.083])
E_DES, E_D98 = 44.1, 57.0   # powered-set gate 44.1 J (D99 design, ~5.58 rad/s); 57 J kept for reference
B_M = 0.05


def pu(delta_deg, dd):
    if delta_deg <= 0: return 0.0
    k = KSCALE * float(np.interp(delta_deg, PU_DEG, PU_NM)) if delta_deg <= PU_DEG[-1] else PU_NM[-1] + KB * math.radians(delta_deg - PU_DEG[-1])
    return k if dd > 0 else RES * k


def arm_mm(qdeg):
    t = math.radians(qdeg); p = (-47.5 * math.sin(t), -47.5 * math.cos(t)); u = (p[0] + 130, p[1] - 270); n = math.hypot(*u)
    return abs(p[0] * u[1] / n - p[1] * u[0] / n)


def B_sb(qdeg, b_m=B_M):
    return 2 * b_m * (2 * math.pi * arm_mm(qdeg) / 5.0) ** 2


def run(case, lean, mass, jscale, mode, T=2.0, b_m=B_M):
    s = P.Sim(mass); m, d = s.m, s.d
    kn = [m.joint(j).id for j in ('l_knee', 'r_knee')]
    for j in kn: m.jnt_range[j, 1] = np.radians(170.0)
    pose, _ = K.CASES[case]
    s.place(pose, lean); q = s.target(pose)
    for _ in range(30):
        d.ctrl[:] = s.pd(q); mujoco.mj_step(m, d)
    for i, n in enumerate(s.names): m.dof_frictionloss[s.vadr[i]] = friction_hold(n)
    kq = [m.jnt_qposadr[j] for j in kn]; kv = [m.jnt_dofadr[j] for j in kn]
    ki = [s.names.index(n) for n in ('l_knee', 'r_knee')]
    lim = 0.5 * s.lim
    E = [0.0, 0.0]; peak = [0.0, 0.0]; qmax = [0.0, 0.0]; vc = [None, None]; zone = 0.0
    for _ in range(int(T / m.opt.timestep)):
        tau = np.clip(s.pd(q), -lim, lim) if mode == 'contract_hold' else np.zeros(m.nu)
        for k in range(2):
            qk, vk = float(d.qpos[kq[k]]), float(d.qvel[kv[k]])
            m.dof_armature[kv[k]] = jscale * (0.1 if math.degrees(qk) >= STOP else float(np.interp(math.degrees(qk), J_DEG, J_KG)))   # 0.1 in the stop zone
            if mode.startswith('contract'):
                tau[ki[k]] = knee_fall_torque(qk, vk, float(lim[ki[k]]))
                if math.degrees(qk) >= 120: zone = max(zone, abs(tau[ki[k]]))
            elif mode == 'short_brake':
                d.qfrc_applied[kv[k]] = -B_sb(math.degrees(qk), b_m) * vk
            dl = math.degrees(qk) - STOP; tq = pu(dl, vk)
            if mode != 'short_brake': d.qfrc_applied[kv[k]] = 0.0
            d.qfrc_applied[kv[k]] += -tq
            if tq > 0:
                if vc[k] is None: vc[k] = vk
                peak[k] = max(peak[k], tq)
                if vk > 0: E[k] += tq * vk * m.opt.timestep
        d.ctrl[:] = tau
        mujoco.mj_step(m, d)
        for k in range(2): qmax[k] = max(qmax[k], float(d.qpos[kq[k]]))
    return dict(case=case, lean=lean, mass=mass, jscale=jscale, mode=mode, E_J=[round(e, 1) for e in E], E_max_J=round(max(E), 1),
                v_at_contact_rad_s=max([v for v in vc if v is not None], default=None), peak_Nm=round(max(peak), 1),
                knee_max_deg=round(math.degrees(max(qmax)), 2), zone_cmd_max_Nm=round(zone, 1),
                pass_44=max(E) <= E_DES, pass_57=max(E) <= E_D98)


def sweep(mode, **kw):
    return [run(c, l, ms, js, mode, **kw) for c, (_, leans) in K.CASES.items() for l, ms, js in itertools.product(leans, (65.0, 68.0, 68.5), (0.8, 1.0, 1.2))]


def summ(rows):
    o = {}
    for c in list(K.CASES) + ['all']:
        r = [x for x in rows if c == 'all' or x['case'] == c]
        o[c] = dict(n=len(r), E_max_J=max(x['E_max_J'] for x in r), vc_max=round(max((x['v_at_contact_rad_s'] or 0) for x in r), 2),
                    peak_Nm=max(x['peak_Nm'] for x in r), knee_max_deg=max(x['knee_max_deg'] for x in r),
                    fail_44=sum(not x['pass_44'] for x in r), fail_57=sum(not x['pass_57'] for x in r), zone_cmd_max=max(x['zone_cmd_max_Nm'] for x in r))
    return o


if __name__ == '__main__':
    res = {}
    for ks in (1.0, 1.3):
      globals()['KSCALE'] = ks
      for md, kw in (('contract', {}), ('contract_hold', {}), ('mo0', {}), ('short_brake', {}), ('short_brake_bm0.025', dict(b_m=0.025))):
        rows = sweep(md.split('_bm')[0], **kw); md = f'{md}_k{ks}'; res[md] = dict(summary=summ(rows), rows=rows)
        print(md, json.dumps(res[md]['summary']['all']), json.dumps({c: res[md]['summary'][c]['E_max_J'] for c in K.CASES}), flush=True)
    res['meta'] = dict(B_sb_knee_Nms_per_rad={q: round(B_sb(q), 1) for q in (60, 95, 110, 123, 133)}, b_m_EST=B_M, gates=dict(design=E_DES, d98=E_D98))
    json.dump(res, open(os.path.join(HERE, 'knee_stop_d99_results.json'), 'w'), indent=1)
