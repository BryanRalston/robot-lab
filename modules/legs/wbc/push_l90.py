"""Lateral push vs L90 hip stop (2026-10-21). Runs run.py's walk+push loop with: LEGS_MASS=68, L90 box limits
(L yaw -12..28, roll -10..15; R mirrored) as joint limits, push force/sign from env PUSH_F (N, 0.2 s) / PUSH_SIGN (+1 = +Y,
during left swing; -1 = -Y, during right swing). Coupled surface checked post-hoc with hip_stop_l90 (MuJoCo can't limit it).
Usage: PUSH_F=300 PUSH_SIGN=-1 python3 push_l90.py 8"""
import os, sys, json, numpy as np
os.environ['LEGS_MASS'] = '68'
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(HERE, '..', 'rl'))
from hip_stop_l90 import hip_stop_l90
F = float(os.environ.get('PUSH_F', '300')); SG = float(os.environ.get('PUSH_SIGN', '1'))
src = open(os.path.join(HERE, 'run.py')).read()
src = src.replace("and ctrl.swing == 'l' and", "and ctrl.swing == ('l' if SG > 0 else 'r') and")
src = src.replace("and 0.06 <= local <= 0.18", "and 0.06 <= (local - (0.5 if SG < 0 else 0.0)) <= 0.18")
src = src.replace("d.xfrc_applied[torso, 1] = 300.0", "d.xfrc_applied[torso, 1] = SG * F")
src = src.replace("push_impulse += 300.0 * dt", "push_impulse += F * dt; HIPLOG.append(None)")
src = src.replace("        mujoco.mj_step(m, d)\n", "        mujoco.mj_step(m, d); HQ.append([d.qpos[m.jnt_qposadr[m.joint(n).id]] for n in ('l_hip_roll','l_hip_yaw','r_hip_roll','r_hip_yaw')])\n", 1)
src = src.replace("if __name__ == '__main__':", "if False:")
os.environ['WBC_OUT'] = '/workspace/tmp/push_l90_out'; os.makedirs('/workspace/tmp/push_l90_out', exist_ok=True)
g = dict(__name__='push_l90', __file__=os.path.join(HERE, 'run.py'), SG=SG, F=F, HIPLOG=[], HQ=[])
exec(compile(src, 'run.py', 'exec'), g)
_load = g['load']
def load_l90(*a, **k):
    m = _load(*a, **k)
    for n, r in (('l_hip_yaw', (-12, 28)), ('r_hip_yaw', (-28, 12)), ('l_hip_roll', (-10, 15)), ('r_hip_roll', (-15, 10))):
        j = m.joint(n).id; m.jnt_range[j] = np.radians(r); m.jnt_limited[j] = 1
    return m
if os.environ.get('NO_L90') != '1': g['load'] = load_l90
os.environ['WBC_OUT'] = '/workspace/tmp/push_l90_out'; os.makedirs('/workspace/tmp/push_l90_out', exist_ok=True)
r = g['run'](mode='push', seconds=float(sys.argv[1]) if len(sys.argv) > 1 else 8.0, push=True)
H = np.array(g['HQ']); D = np.pi / 180
vl = hip_stop_l90(H[:, 0], H[:, 1], 'L'); vr = hip_stop_l90(H[:, 2], H[:, 3], 'R')
out = dict(F=F, sign=SG, impulse_Ns=r.get('push_impulse_Ns'), fell=r.get('fell', r.get('fall_t')), keys=sorted(r.keys()),
           L_roll_min=H[:, 0].min() / D, L_yaw=[H[:, 1].min() / D, H[:, 1].max() / D],
           R_roll_max=H[:, 2].max() / D, R_yaw=[H[:, 3].min() / D, H[:, 3].max() / D],
           coupled_viol_max_deg=[vl.max() / D, vr.max() / D])
print('RESULT', json.dumps({k: (round(v, 2) if isinstance(v, float) else v) for k, v in out.items()}, default=str))
