"""Plan pre-pass: limit stance ankle dorsiflexion in the r2 1.2 m/s plan by heel rise (early toe-off).
Frames where ankle_pitch < A get ankle = A (foot pitches heel-up about the ankle), pelvis z raised by the toe
penetration that causes. Usage: python3 plan_ankle_heel.py A out.npz [heel|knee]  (run from modules/legs).
2026-10-21 RL Controls retune for sim/v3 ddfcff8 (ankle hard -0.916 rad, no -45 deg stop)."""
import sys, numpy as np, mujoco; sys.path.insert(0,'.')
from gait_lib import load
A=float(sys.argv[1]); out=sys.argv[2]; mode=sys.argv[3] if len(sys.argv)>3 else 'heel'
z=dict(np.load('results/r2/walk_1p2_r2.npz')); m=load(); d=mujoco.MjData(m)
Q=z['Q'].copy(); qa=[m.jnt_qposadr[m.joint(f'{s}_ankle_pitch').id] for s in 'lr']; qk=[m.jnt_qposadr[m.joint(f'{s}_knee').id] for s in 'lr']; qh=[m.jnt_qposadr[m.joint(f'{s}_hip_pitch').id] for s in 'lr']
fg=[m.geom(f'{s}_foot').id for s in 'lr']
def low(q):
    d.qpos[:]=q; mujoco.mj_kinematics(m,d); mujoco.mj_comPos(m,d)
    out=[]
    for g in fg:
        R=d.geom_xmat[g].reshape(3,3); c=d.geom_xpos[g]; sz=m.geom_size[g]
        out.append(min((c+R@np.array([x,y,-sz[2]]))[2] for x in (sz[0],-sz[0]) for y in (sz[1],-sz[1])))
    return out
n=0
for k in range(len(Q)):
    q=Q[k]; l0=low(q); ch=False
    for i in range(2):
        if q[qa[i]]<A:
            dd=A-q[qa[i]]; q[qa[i]]=A; ch=True
            if mode=='knee': q[qk[i]]-=dd   # keep the foot flat: straighten the knee instead
    if ch:
        n+=1; l1=low(q); q[2]+=max(0.0,max(l0[i]-l1[i] for i in range(2)))
    Q[k]=q
z['Q']=Q; np.savez(out,**z); print('frames changed',n,'of',len(Q),'ankle min',Q[:,qa].min().round(3))
