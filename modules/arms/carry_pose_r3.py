"""RL Arms A39/P-028: carry pose search with the R1 load model (sim/v3 masses, 10 kg/hand at hand-box centre, static).
Grid over shoulder_pitch and elbow within P-026 ROM (elbow -125..0). Reports elbow/shoulder torque and hand position
relative to the shoulder_pitch axis and to the waist_pitch axis. Output carry_pose_r3.json"""
import mujoco, numpy as np, json, os
H=os.path.dirname(os.path.abspath(__file__)); m=mujoco.MjModel.from_xml_path(os.path.join(H,'../../sim/v3/humanoid_v3.xml')); d=mujoco.MjData(m)
jid=lambda n:mujoco.mj_name2id(m,mujoco.mjtObj.mjOBJ_JOINT,n); bid=lambda n:mujoco.mj_name2id(m,mujoco.mjtObj.mjOBJ_BODY,n)
hand=bid('L_hand'); shP=bid('L_shoulderP'); torso=bid('torso'); PAY=10.0; G=9.81
def load(sp,el,sy=0.0):
    mujoco.mj_resetData(m,d); d.qpos[2]=1.16
    for n,a in [('l_shoulder_pitch',sp),('l_elbow',el),('l_shoulder_yaw',sy)]: d.qpos[m.jnt_qposadr[jid(n)]]=np.radians(a)
    mujoco.mj_forward(m,d)
    pt=d.xpos[hand]+d.xmat[hand].reshape(3,3)@np.array([0,0,-0.10]); jp=np.zeros((3,m.nv)); mujoco.mj_jac(m,d,jp,None,pt,hand)
    tau=d.qfrc_bias+jp.T@np.array([0,0,PAY*G])
    r=lambda n:round(abs(float(tau[m.jnt_dofadr[jid(n)]])),2)
    rel=pt-d.xpos[torso]  # torso body origin = waist_pitch axis
    return dict(sp=sp,el=el,elbow=r('l_elbow'),shoulder_pitch=r('l_shoulder_pitch'),shoulder_roll=r('l_shoulder_roll'),
                hand_x_fwd=round(float(rel[0]),3),hand_z_above_waist_pitch=round(float(rel[2]),3))
rows=[load(sp,el) for sp in range(-60,31,5) for el in range(-125,1,5)]
ok=[r for r in rows if r['elbow']<=15.0]
# choose: elbow<=15, hand forward >=0.20 m (load clear of thighs/torso front [EST]), min shoulder torque, highest hand
cand=[r for r in ok if r['hand_x_fwd']>=0.20]
best=min(cand,key=lambda r:(r['shoulder_pitch'],-r['hand_z_above_waist_pitch'])) if cand else None
ref=load(-30,-60)
json.dump(dict(model='sim/v3/humanoid_v3.xml',payload_kg_per_hand=PAY,rule='elbow<=15 N·m (R-030 A39 / P-042), hand_x>=0.20 m [EST clearance]',
               r1_carry_ref=ref,selected=best,n_ok=len(ok),grid=rows),open(os.path.join(H,'carry_pose_r3.json'),'w'),indent=1)
print('ref',ref); print('best',best)
for r in sorted(cand,key=lambda r:r['shoulder_pitch'])[:8]: print(r)
