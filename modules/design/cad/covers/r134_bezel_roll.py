"""Bezel/fairing vs W2 carrier+pad across shoulder roll incl. negative range (reuses r133 kinematics). Torso frame mm.
Bezel+tapered fairing envelope (conservative box): x 110..176, y +-75, z 145..295."""
import sys, json, os, numpy as np
sys.argv=['x']; H=os.path.dirname(os.path.abspath(__file__))
src=open(os.path.join(H,'r133_roll_sweep.py')).read().split('out = {')[0]; exec(src)
BX=np.array([[110,-75,145],[176,75,295]])
def boxgap(L):
    d=np.maximum(np.maximum(BX[0]-L, L-BX[1]),0); return np.linalg.norm(d,axis=1)
lo,hi=m.jnt_range[mujoco.mj_name2id(m,mujoco.mjtObj.mjOBJ_JOINT,'l_shoulder_roll')]
res={}
for sp in (-150,-90,-30,0,5,30):
    best=(1e9,None)
    for sr in range(int(np.degrees(lo)), 1):
        mujoco.mj_resetData(m,d); d.qpos[2]=1.16; d.qpos[J('l_shoulder_pitch')]=np.radians(sp); d.qpos[J('l_shoulder_roll')]=np.radians(sr); mujoco.mj_forward(m,d)
        Rs=d.xmat[B('L_shoulderP')].reshape(3,3); o=(d.xpos[B('L_shoulderP')]+Rs@np.array([0,.112,-.04]))*1000
        Rt,ot=d.xmat[B('torso')].reshape(3,3),d.xpos[B('torso')]*1000
        for f in ('carrier_w2','pad_envelope_w2'):
            Lp=((Rs@Rx(np.radians(sr))@pts[f].T).T+o-ot)@Rt; g=float(boxgap(Lp).min())
            if g<best[0]: best=(round(g,1),[sr,f])
    res[sp]=best
out=dict(roll_range_deg=[round(float(np.degrees(lo)),1),round(float(np.degrees(hi)),1)], min_gap_neg_roll=res)
json.dump(out,open(os.path.join(H,'r134_bezel_roll.json'),'w'),indent=1); print(out)
