"""Arm self-collision supervisor (RL Controls). 1 kHz, kinematic.

Keep-outs (all margins configurable in controller_config.json["arm_self_collision"]):
  * chest pad (Arms R18 bf228b1, CHEST_PAD_CLASH_R18.md): torso-frame box x <= +0.185, y +/-0.061, z 0.159..0.281
    (116 core + 10 mm gate already inside the box, so margin 0). Checked against forearm capsule + hand box; the hand
    box moves with the wrist joints, so wrist flexion is included.
  * knee rear-outlet shroud N1 (ID P-156 rev 6) on each thigh, rigid on the thigh body (follows hip yaw/roll/pitch),
    outboard edge y_out (default 0.176, T&R limit), margin 0.063 (T&R 2e9b25c; T&R to confirm 63 vs 30 mm).

Per cycle: FK (mj_kinematics) -> convex capsule/box and box/box distances (mj_geomDistance on the keep-out geoms, which
are added with contype=conaffinity=0 so they never touch physics) -> per pair a separation row
J_d = n^T (J_link_point - J_obstacle_point) (full nv) ->
  1. velocity damping (Faverjon-Tournassoud): require d_dot >= -xi (d - m)/(d_i - m) for d < d_i, i.e. the approach
     speed is scaled to zero at the margin; inside the margin require d_dot >= +xi_in (m - d)/m (push out).
     The excess is removed with a minimum-norm correction on the ARM columns only (legs/waist are not commanded here;
     their motion, e.g. hip flexion lifting the shroud, is part of d_dot and the arm moves away).
  2. repulsive tasks (rows + desired d_dot) for the WBC null space via WBCHook.add_nullspace_task().
Fall mode: the supervisor may be bypassed only when fall_pose_clear() confirms the commanded tuck pose clears every
keep-out at the current leg pose; otherwise it stays on.
"""
from __future__ import annotations
import json, re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Protocol, Sequence
import numpy as np, mujoco

ROOT = Path(__file__).resolve().parents[3]
XML = ROOT / 'sim/v3/humanoid_v3.xml'
CFG = ROOT / 'modules/controls/controller_config.json'
THIGH0 = np.array([0.0, 0.130, 0.920])  # L_thigh origin, standing, all joints 0 (sim/v3)
ARM_J = ['shoulder_pitch', 'shoulder_roll', 'shoulder_yaw', 'elbow', 'wrist_roll', 'wrist_pitch', 'wrist_yaw']

DEFAULT = dict(
    enabled=True, loop_hz=1000.0,
    chest=dict(ref='Arms R18 bf228b1', body='torso', x=[0.0, 0.185], y=[-0.061, 0.061], z=[0.159, 0.281], margin=0.0),
    knee_shroud=dict(ref='ID P-156 rev 6b (baad131); T&R 925d72e', x=[-0.100, -0.020], y=[0.086, 0.150], y_out=0.150,
                     z=[0.840, 0.904], z_top_front=0.8615, chamfer_deg=40.0, chamfer_w=0.015, skin=0.002, status='FINAL rev 6b (valid through rev 8): ID confirmed 40 deg / 15 mm face + R10; z840 final (Thermal PASS 5fd6a54)',
                     note='convex hull: sloped top z 861.5 (x -20) -> 904 (x -100), 40 deg chamfer on the outboard-top edge, '
                          'chamfer 15 mm face (ID confirmed); R10 blends ignored = conservative; '
                          '+2 mm skin (T&R). Set chamfer_w 0 / z_top_front = z[1] for a plain box.'),
    plume=dict(ref='T&R 925d72e (a) K_plume', offset=0.030, length=0.060, half_angle_deg=15.0,
               openings='aft face [EST: ID rev 6 slots are on the walls; aft-only per T&R fix 1]',
               transit_max_s=0.5, window_s=10.0, window_frac=0.20, exit_at_s=0.30,
               admit_note='entry admitted only if a full 0.5 s pass still fits in the 10 s / 20 % budget; '
                          'after exit_at_s inside, the plume becomes a keep-out (push-out) so the pass ends by 0.5 s'),
    thresholds_mm=dict(ref='T&R 925d72e', walk=[15, 10, 5], carry=[15, 10, 5], stand=[15, 10, 5],
                       crouch=[20, 15, 10], sit=[20, 15, 10], kneel=[20, 15, 10], lowering=[20, 15, 10]),
    plume_mm=[5, 2, 0],
    payload=dict(ref='P-042 (carry_balance_r1, legs scenarios CARRY_POS)', body='torso', pos=[0.32, 0.0, 0.415],
                 size_full=[0.212, 0.274, 0.212],
                 size_note='sim has no payload geom; box sized from the sim inertia (20 kg, diag 0.2/0.15/0.2) [DERIVED]',
                 modes=['carry'], hook='PENDING T&R: no hook geometry in repo; placeholder disabled'),
    links=['forearm', 'hand'], influence=0.10, aim_offset=0.004, xi=1.0, xi_in=8.0, repulse_gain=1.0, passes=6,
    shoulder_roll_inward_soft_limit_deg=None,
    fall_override='only if fall_pose_clear()')

def load_cfg():
    c = json.loads(CFG.read_text()).get('arm_self_collision') if CFG.exists() else None
    out = json.loads(json.dumps(DEFAULT))
    if c:
        for k, v in c.items():
            if isinstance(v, dict) and k in out: out[k].update(v)
            else: out[k] = v
    return out

def _box(name, a, b, off=np.zeros(3), mirror=1):
    cc = (a + b) / 2 - off; hh = (b - a) / 2; cc[1] *= mirror
    return (f'<geom name="{name}" type="box" pos="{cc[0]:.4f} {cc[1]:.4f} {cc[2]:.4f}" size="{hh[0]:.4f} {hh[1]:.4f} '
            f'{hh[2]:.4f}" contype="0" conaffinity="0" group="5" mass="0"/>')

def build_model(cfg=None, xml_text=None):
    """sim/v3 model + keep-out geoms (non-colliding): ko_chest (torso), ko_shroud_l/r and ko_plume_l/r (thighs)."""
    cfg = cfg or load_cfg(); x = xml_text or XML.read_text()
    ch = cfg['chest']
    g = _box('ko_chest', np.array([ch['x'][0], ch['y'][0], ch['z'][0]]), np.array([ch['x'][1], ch['y'][1], ch['z'][1]]))
    py = cfg.get('payload')
    if py:
        c = np.array(py['pos']); h = np.array(py['size_full']) / 2
        g += _box('ko_payload', c - h, c + h)
    x = re.sub(r'(<body name="torso"[^>]*>)', lambda mm: mm.group(1) + g, x, count=1)
    ks, pl = cfg['knee_shroud'], cfg['plume']; sk = ks.get('skin', 0.0)
    x0, x1 = ks['x'][0] - sk, ks['x'][1] + sk; y0, y1 = ks['y'][0] - sk, ks['y_out'] + sk; z0 = ks['z'][0] - sk
    ztf, zta = ks.get('z_top_front', ks['z'][1]) + sk, ks['z'][1] + sk  # top at x1 (front) and x0 (aft)
    cw = ks.get('chamfer_w', 0.0); ch = cw * np.tan(np.radians(ks.get('chamfer_deg', 45.0)))
    V = []
    for xx, zt in ((x0, zta), (x1, ztf)):
        V += [(xx, y0, z0), (xx, y1, z0), (xx, y0, zt), (xx, y1 - cw, zt), (xx, y1, zt - ch)]
    w = pl['offset'] + pl['length'] * np.tan(np.radians(pl['half_angle_deg']))
    plo = np.array([x0 - pl['offset'] - pl['length'], y0 - w, z0 - w]); phi = np.array([x0, y1 + w, zta + w])
    assets = ''
    for side, sg in (('L', 1), ('R', -1)):
        vv = ' '.join(f'{a - THIGH0[0]:.4f} {sg * (b - THIGH0[1]):.4f} {c - THIGH0[2]:.4f}' for a, b, c in V)
        assets += f'<mesh name="m_shroud_{side.lower()}" vertex="{vv}"/>'
        g = (f'<geom name="ko_shroud_{side.lower()}" type="mesh" mesh="m_shroud_{side.lower()}" contype="0" conaffinity="0" '
             f'group="5" mass="0"/>' + _box(f'ko_plume_{side.lower()}', plo, phi, THIGH0, sg))
        x = re.sub(rf'(<body name="{side}_thigh"[^>]*>)', lambda mm: mm.group(1) + g, x, count=1)
    if '<asset>' in x: x = x.replace('<asset>', '<asset>' + assets, 1)
    else: x = re.sub(r'(<worldbody>)', lambda mm: f'<asset>{assets}</asset>' + mm.group(1), x, count=1)
    m = mujoco.MjModel.from_xml_string(x)
    return m, mujoco.MjData(m)

class WBCHook(Protocol):
    """Interface the WBC implements; rows are full-nv separation Jacobians, rate is the desired d_dot (m/s)."""
    def add_nullspace_task(self, name: str, row: np.ndarray, rate: float, weight: float) -> None: ...

SUSTAINED = {'carry', 'stand', 'crouch', 'sit', 'kneel', 'lowering'}

class TransitTimer:
    """K_plume walk-swing pass-through budget: <= transit_max_s per entry and <= window_frac of any window_s."""
    def __init__(s, dt, transit_max_s=0.5, window_s=10.0, window_frac=0.2):
        s.dt, s.tmax, s.frac = dt, transit_max_s, window_frac
        s.buf = np.zeros(int(round(window_s / dt)), bool); s.k = 0; s.sum = 0; s.cur = 0.0
    def step(s, inside: bool):
        s.sum += int(inside) - int(s.buf[s.k]); s.buf[s.k] = inside; s.k = (s.k + 1) % len(s.buf)
        s.cur = s.cur + s.dt if inside else 0.0
    @property
    def window_used(s): return s.sum / len(s.buf)
    def allowed(s, exit_at=None):
        """May the hand be (or stay) inside the plume next cycle? Outside: admit only if a whole pass fits the window.
        Inside: allowed until exit_at (default tmax) and while the window budget lasts."""
        n = len(s.buf); lim = s.frac * n
        if s.cur == 0.0:
            return s.sum + s.tmax / s.dt <= lim + 1e-9
        return s.cur + s.dt <= (exit_at if exit_at is not None else s.tmax) + 1e-12 and s.sum + 1 <= lim + 1e-9

@dataclass
class Pair:
    name: str; arm_geom: int; obs_geom: int; kind: str; side: str

@dataclass
class Supervisor:
    m: mujoco.MjModel; d: mujoco.MjData; cfg: dict = field(default_factory=load_cfg)
    def __post_init__(s):
        m = s.m; s.pairs: list[Pair] = []
        for side in 'lr':
            for ln in s.cfg['links']:
                ag = m.geom(f'{side}_{ln}').id
                s.pairs.append(Pair(f'{side}_{ln}:chest', ag, m.geom('ko_chest').id, 'chest', side))
                for ss in 'lr':
                    for kd in ('shroud', 'plume'):
                        s.pairs.append(Pair(f'{side}_{ln}:{kd}_{ss}', ag, m.geom(f'ko_{kd}_{ss}').id, kd, side))
        if 'ko_payload' in [m.geom(i).name for i in range(m.ngeom)]:
            for ss in 'lr':
                for kd in ('shroud', 'plume'):
                    s.pairs.append(Pair(f'payload:{kd}_{ss}', m.geom('ko_payload').id, m.geom(f'ko_{kd}_{ss}').id,
                                        kd, 'payload'))
        s.arm_dofs = {sd: np.array([m.jnt_dofadr[m.joint(f'{sd}_{j}').id] for j in ARM_J]) for sd in 'lr'}
        dt = 1.0 / s.cfg['loop_hz']; pl = s.cfg['plume']
        s.timers = {sd: TransitTimer(dt, pl['transit_max_s'], pl['window_s'], pl['window_frac']) for sd in 'lr'}
        s._jp1 = np.zeros((3, m.nv)); s._jp2 = np.zeros((3, m.nv)); s._ft = np.zeros(6)
        s.last = []; s.events = []; s.mode = 'stand'; s.t = 0.0

    def thresholds(s, kind, mode=None):
        """(target, warn, trip) in m for a pair kind in a mode."""
        mode = mode or s.mode
        if kind == 'chest': return (s.cfg['chest']['margin'],) * 3
        if kind == 'plume': return tuple(v / 1000 for v in s.cfg['plume_mm'])
        return tuple(v / 1000 for v in s.cfg['thresholds_mm'][mode])

    def distances(s, kin=True):
        m, d = s.m, s.d
        if kin:
            mujoco.mj_kinematics(m, d); mujoco.mj_comPos(m, d)
        out = []
        for p in s.pairs:
            if p.side == 'payload' and s.mode not in s.cfg['payload']['modes']: out.append((p, 9.0, None)); continue
            tg = s.thresholds(p.kind)[0]
            dmax = tg + s.cfg['influence'] + 0.05
            dist = mujoco.mj_geomDistance(m, d, p.arm_geom, p.obs_geom, dmax, s._ft)
            if dist >= dmax: out.append((p, dist, None)); continue
            pa, po = s._ft[:3].copy(), s._ft[3:].copy()
            if dist > 1e-3:
                n = pa - po
            else:  # touching/penetrating: witness direction is unreliable, use obstacle centre -> arm geom centre
                n = d.geom_xpos[p.arm_geom] - d.geom_xpos[p.obs_geom]
            n /= max(np.linalg.norm(n), 1e-9)
            mujoco.mj_jac(m, d, s._jp1, None, pa, m.geom_bodyid[p.arm_geom])
            mujoco.mj_jac(m, d, s._jp2, None, po, m.geom_bodyid[p.obs_geom])
            out.append((p, dist, n @ (s._jp1 - s._jp2)))
        s.last = out
        return out

    def _lb(s, dist, tg):
        di = tg + s.cfg['influence']
        if dist >= di: return None
        if dist >= tg: return -s.cfg['xi'] * (dist - tg) / (di - tg)
        return s.cfg['xi_in'] * (tg - dist) / max(tg, 0.01)

    def filter(s, qdot_cmd: np.ndarray, mode='stand', fall_mode=False, fall_target=None, kin=True, bypass=False):
        """Supervised joint velocity (nv); only arm dofs change. Also updates plume timers and warn/trip events."""
        s.mode = mode; qd = qdot_cmd.copy(); s.t += 1.0 / s.cfg['loop_hz']
        if fall_mode and fall_target is not None and s.fall_pose_clear(fall_target)[0]:
            return qd
        dl = s.distances(kin)
        if bypass: return qd  # measurement only (used by the sweep's 'without supervisor' runs)
        inside = {sd: any(dd <= 0 for p, dd, _ in dl if p.kind == 'plume' and p.side == sd) for sd in 'lr'}
        # payload pairs: warn/trip events only (torso-fixed in this model; legs/WBC must act), no arm correction
        plume_ok = {sd: (mode == 'walk' and s.timers[sd].allowed(s.cfg['plume'].get('exit_at_s'))) for sd in 'lr'}
        for sd in 'lr': s.timers[sd].step(inside[sd])
        act = []
        for p, dist, row in dl:
            if p.kind == 'plume' and p.side in plume_ok and plume_ok[p.side]: continue  # walk swing transit inside budget
            tg, wn, tr = s.thresholds(p.kind)
            if p.kind != 'chest' and dist < wn: s.events.append((round(s.t, 3), 'trip' if dist < tr else 'warn', p.name, dist))
            if row is not None and p.side != 'payload': act.append((p, dist, row, tg + s.cfg.get('aim_offset', 0.0)))
        for _ in range(s.cfg['passes']):
            hit = False
            for p, dist, row, tg in act:
                lb = s._lb(dist, tg)
                if lb is None: continue
                e = lb - row @ qd
                if e <= 0: continue
                a = row[s.arm_dofs[p.side]]; aa = a @ a
                if aa < 1e-12: continue
                qd[s.arm_dofs[p.side]] += a * e / aa; hit = True
            if not hit: break
        return qd

    def repulsive_tasks(s, hook: WBCHook | None = None):
        tasks = []
        for p, dist, row in s.last:
            if row is None or p.side == 'payload': continue
            tg = s.thresholds(p.kind)[0] + s.cfg.get('aim_offset', 0.0); di = tg + s.cfg['influence']
            if dist >= di: continue
            rate = s.cfg['repulse_gain'] * (di - dist); w = (di - dist) / s.cfg['influence']
            tasks.append((p.name, row, rate, w))
            if hook is not None: hook.add_nullspace_task('sc_' + p.name, row, rate, w)
        return tasks

    def fall_pose_clear(s, target: dict, mode='crouch'):
        """Distances at the commanded fall pose with the CURRENT leg/waist pose. Clear = chest >= 0, shroud >= trip
        of `mode`, plume entry allowed (fall is transient). Returns (clear, (worst_slack, pair))."""
        save = s.d.qpos.copy()
        for k, v in target.items(): s.d.qpos[s.m.jnt_qposadr[s.m.joint(k).id]] = v
        mujoco.mj_kinematics(s.m, s.d); res = []
        for p in s.pairs:
            if p.kind == 'plume' or p.side == 'payload': continue
            dd = mujoco.mj_geomDistance(s.m, s.d, p.arm_geom, p.obs_geom, 1.0, s._ft)
            res.append((dd - s.thresholds(p.kind, mode)[2], p.name))
        s.d.qpos[:] = save; mujoco.mj_kinematics(s.m, s.d)
        w = min(res); return w[0] >= 0, w

def write_config_entry():
    c = json.loads(CFG.read_text())
    c['arm_self_collision'] = DEFAULT | {'module': 'modules/controls/arm/self_collision.py',
                                         'doc': 'modules/controls/arm/SELF_COLLISION.md'}
    CFG.write_text(json.dumps(c, indent=2) + '\n')
