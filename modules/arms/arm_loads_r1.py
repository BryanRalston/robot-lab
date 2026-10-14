"""RL Arms R1: arm joint loads from sim/v3/humanoid_v3.xml (committed masses/geometry).
Static gravity + payload via MuJoCo (qfrc_bias + J^T F), plus an inertial term at a stated [EST] acceleration.
Payload point = hand box centre (L_hand origin + (0,0,-0.10)). Output: arm_loads_r1.json"""
import mujoco, numpy as np, json, os
H=os.path.dirname(os.path.abspath(__file__)); XML=os.path.join(H,'../../sim/v3/humanoid_v3.xml')
m=mujoco.MjModel.from_xml_path(XML); d=mujoco.MjData(m); G=9.81
J=['shoulder_pitch','shoulder_roll','shoulder_yaw','elbow','wrist_roll','wrist_pitch','wrist_yaw']
dof={j:m.jnt_dofadr[mujoco.mj_name2id(m,mujoco.mjtObj.mjOBJ_JOINT,'l_'+j)] for j in J}
hand=mujoco.mj_name2id(m,mujoco.mjtObj.mjOBJ_BODY,'L_hand')
POSES={ # deg, left arm; T5 cases
 'reach_horizontal_10kg':dict(q={'shoulder_pitch':-90},payload=10.0),   # T5 one-hand 10 kg at full reach
 'carry_waist_10kg_per_hand':dict(q={'shoulder_pitch':-30,'elbow':-60},payload=10.0),  # T5 20 kg two-hand at waist, forearm horizontal [pose EST]
 'reach_horizontal_noload':dict(q={'shoulder_pitch':-90},payload=0.0),
 'yaw_upperarm_fwd_elbow90_10kg':dict(q={'shoulder_pitch':-90,'shoulder_yaw':90,'elbow':-90},payload=10.0),
 'side_abduct_90_10kg':dict(q={'shoulder_roll':90},payload=10.0),      # lateral reach, roll worst case
}
ALPHA=20.0  # rad/s^2 [EST]: 4 rad/s reached in 0.2 s; each joint alone (diagonal term)
out={}
for name,p in POSES.items():
    mujoco.mj_resetData(m,d); d.qpos[2]=1.16
    for j,a in p['q'].items(): d.qpos[m.jnt_qposadr[mujoco.mj_name2id(m,mujoco.mjtObj.mjOBJ_JOINT,'l_'+j)]]=np.radians(a)
    mujoco.mj_forward(m,d)
    pt=d.xpos[hand]+d.xmat[hand].reshape(3,3)@np.array([0,0,-0.10])
    jp=np.zeros((3,m.nv)); mujoco.mj_jac(m,d,jp,None,pt,hand)
    F=np.array([0,0,-p['payload']*G]); tau_pay=-(jp.T@F)   # torque actuator must supply
    # inertial: M*qacc on arm dofs (+payload point mass ~ m r^2 approx via Jacobian)
    # per-joint (diagonal) inertia at ALPHA, one joint accelerating at a time, payload as point mass
    Mq=np.zeros((m.nv,m.nv)); mujoco.mj_fullM(m,d,Mq)
    tau_in=np.array([(Mq[i,i]+p['payload']*float(jp[:,i]@jp[:,i]))*ALPHA for i in range(m.nv)])
    row={}
    for j in J:
        i=dof[j]; s=d.qfrc_bias[i]+tau_pay[i]
        row[j]=dict(static=round(abs(float(s)),2),inertial=round(abs(float(tau_in[i])),2),total=round(abs(float(s))+abs(float(tau_in[i])),2))
    out[name]=dict(pose_deg=p['q'],payload_kg=p['payload'],point=[round(float(x),3) for x in pt],joints=row)
arm_mass=sum(m.body_mass[mujoco.mj_name2id(m,mujoco.mjtObj.mjOBJ_BODY,b)] for b in ['L_shoulderP','L_upper_arm','L_forearm','L_hand'])
out['_meta']=dict(xml='sim/v3/humanoid_v3.xml',alpha_rad_s2_EST=ALPHA,sim_arm_mass_one_side_kg=round(float(arm_mass),3))
json.dump(out,open(os.path.join(H,'arm_loads_r1.json'),'w'),indent=1)
for k,v in out.items():
    if k[0]!='_': print(k,{j:(x['static'],x['total']) for j,x in v['joints'].items()})
print(out['_meta'])
