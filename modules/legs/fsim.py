"""Forward-dynamics walking test on sim/v3/humanoid_v3.xml (contacts on, torques clipped to v3 catalog peak = ctrlrange).
Controller (no RL, ~0.1 ms/step on CPU): inverse-dynamics feed-forward from scenarios.py + joint PD to the reference
+ balance feedback: (a) stance-hip torso attitude PD, (b) stance-ankle COM/ZMP feedback, (c) swing-foot placement shift from COM error (capture-point style).
usage: python3 fsim.py <scenario> [--fb 0|1] [--T seconds]"""
import sys,json,argparse,numpy as np,mujoco
from gait_lib import *
ap=argparse.ArgumentParser(); ap.add_argument('scenario'); ap.add_argument('--fb',type=int,default=1); ap.add_argument('--kp',type=float,default=800); ap.add_argument('--tag',default=''); ap.add_argument('--kc',type=float,default=20.0); ap.add_argument('--kr',type=float,default=1.0); ap.add_argument('--tscale',type=float,default=1.0); ap.add_argument('--fp',type=float,default=0.0); ap.add_argument('--cop',type=int,default=0); ap.add_argument('--kyaw',type=float,default=0.3); ap.add_argument('--fprate',type=float,default=1.5)
a=ap.parse_args()
R=np.load(os.path.join(HERE,'results',os.environ.get('LEGS_OUT',''),a.scenario+'.npz')); Qr=R['Q'].astype(float); Vr=R['V'].astype(float); Tr=R['TAU'].astype(float); AL=R['AL']
m=load(20.0,(0.25,0,0.10)) if a.scenario.startswith('carry') else load(); print('mass',round(sum(m.body_mass),2),'limits',[round(m.actuator_ctrlrange[i,1]) for i in range(6)]); d=mujoco.MjData(m); r=Robot(m)
jid=m.actuator_trnid[:,0]; qa=m.jnt_qposadr[jid]; va=m.jnt_dofadr[jid]; lim=m.actuator_ctrlrange[:,1]*a.tscale
names=[m.actuator(i).name for i in range(m.nu)]; idx=lambda n:names.index(n)
kp=np.clip(lim*4,40,a.kp); kd=2*np.sqrt(kp*np.maximum(m.dof_armature[va],0.05))+0.02*kp
d.qpos[:]=Qr[0]; d.qvel[:]=Vr[0]; mujoco.mj_forward(m,d)
# settle feet exactly on floor
lo=min(d.geom_xpos[m.geom(g).id][2]-0.009 for g in ('l_foot','r_foot')); d.qpos[2]-=lo; mujoco.mj_forward(m,d)
dz=d.qpos[2]-Qr[0,2]
Nr=len(Qr); T=Nr*DT; steps=0; log=[]; contact_prev=None; fell=None; mg=m.body_subtreemass[1]*G
def ref(t):
    x=min(t/DT,Nr-1.001); i=int(x); f=x-i
    q=Qr[i]*(1-f)+Qr[i+1]*f; q[3:7]/=np.linalg.norm(q[3:7]); return q,Vr[i]*(1-f)+Vr[i+1]*f,Tr[i]*(1-f)+Tr[i+1]*f,AL[i]*(1-f)+AL[i+1]*f
def foot_contact(side):
    g=m.geom(f'{side}_foot').id; f=0.0
    for c in d.contact[:d.ncon]:
        if g in (c.geom1,c.geom2):
            fr=np.zeros(6); mujoco.mj_contactForce(m,d,list(d.contact).index(c) if False else 0,fr)
    return any(g in (c.geom1,c.geom2) for c in d.contact[:d.ncon])
nsteps=int(T/m.opt.timestep); rd=mujoco.MjData(m); off={'l':np.zeros(2),'r':np.zeros(2)}; OMG=np.sqrt(G/0.94); sat=np.zeros(m.nu)
KC=np.array([a.kc,a.kc,30.0]); DC=2*np.sqrt(KC); KR=a.kr*np.array([400.,600.,100.])*m.body_subtreemass[1]/60; DR=0.15*KR
for k in range(nsteps):
    t=d.time; q,v,tff,al=ref(t)
    if a.fp>0:   # capture-point foot placement: shift the swing foot by kfp*(xi - xi_ref); offset persists through the next stance
        mujoco.mj_subtreeVel(m,d); rd.qpos[:]=q; rd.qvel[:]=v; mujoco.mj_kinematics(m,rd); mujoco.mj_comPos(m,rd); mujoco.mj_subtreeVel(m,rd)
        xi=d.subtree_com[1][:2]+d.subtree_linvel[1][:2]/OMG; xir=rd.subtree_com[1][:2]+rd.subtree_linvel[1][:2]/OMG
        for i,sd in enumerate('lr'):
            if al[i]<0.02:   # swinging
                tgt=np.clip(a.fp*(xi-xir),-0.2,0.2); off[sd]+=np.clip(tgt-off[sd],-a.fprate*m.opt.timestep,a.fprate*m.opt.timestep)
        q=q.copy()
        for sd in 'lr':
            if np.any(off[sd]!=0):
                jp=np.zeros((3,m.nv)); mujoco.mj_jacBody(m,rd,jp,None,r.foot[sd]); J=jp[:2][:,r.legv[sd]]
                q[r.legq[sd]]+=J.T@np.linalg.solve(J@J.T+1e-4*np.eye(2),off[sd])
    tau=tff[va]+kp*(q[qa]-d.qpos[qa])-kd*(d.qvel[va]-v[va])
    if a.fb:
        # virtual-model balance: desired corrective wrench on the body at the COM, produced by the stance legs (tau = -J_leg^T dW)
        rd.qpos[:]=q; rd.qvel[:]=v; mujoco.mj_kinematics(m,rd); mujoco.mj_comPos(m,rd); mujoco.mj_comVel(m,rd); mujoco.mj_subtreeVel(m,rd)
        mujoco.mj_subtreeVel(m,d)
        c=d.subtree_com[1]; cv=d.subtree_linvel[1]; cr=rd.subtree_com[1]; cvr=rd.subtree_linvel[1]
        Fc=mg*(KC*(cr-c)+DC*(cvr-cv))
        qe=np.zeros(3); mujoco.mju_subQuat(qe,q[3:7],d.qpos[3:7]); Rp=d.xmat[1].reshape(3,3)
        Mc=Rp@((KR*qe+DR*(v[3:6]-d.qvel[3:6]))*np.array([1,1,a.kyaw]))
        for i,sd in enumerate('lr'):
            if al[i]<0.05: continue
            b_=r.foot[sd]; jp=np.zeros((3,m.nv)); jr=np.zeros((3,m.nv)); mujoco.mj_jacBody(m,d,jp,jr,b_)
            pf=d.xpos[b_]; W=np.r_[al[i]*Fc, al[i]*(Mc+np.cross(c-pf,Fc))]
            cols=r.legv[sd]; J=np.r_[jp,jr][:,cols]
            dt_=-J.T@W
            for n,jn in enumerate(LEG): tau[idx(f'{sd}_{jn}')]+=dt_[n]
    if a.cop:   # keep stance-ankle torque inside what the sole can carry (CoP within sole) so the foot does not roll onto an edge
        for i,sd in enumerate('lr'):
            if al[i]>0.05:
                fz=max(al[i],0.3)*mg; ia=idx(f'{sd}_ankle_roll'); ip=idx(f'{sd}_ankle_pitch')
                tau[ia]=np.clip(tau[ia],-0.045*fz,0.045*fz); tau[ip]=np.clip(tau[ip],-0.17*fz,0.17*fz)
    d.ctrl[:]=np.clip(tau,-lim,lim); sat+=np.abs(tau)>lim
    mujoco.mj_step(m,d)
    if d.qpos[2]<Qr[0,2]+dz-0.35 or d.xmat[1][8]<0.7: fell=d.time; break
    cs=(foot_contact('l'),foot_contact('r'))
    if contact_prev is None: air=[0.0,0.0]
    for i in range(2):
        if not cs[i]: air[i]+=m.opt.timestep
        else:
            if air[i]>0.1 and d.time>0.3: steps+=1    # real step: foot airborne >0.1 s then lands
            air[i]=0.0
    contact_prev=cs
    if k%25==0:
        Rm=d.xmat[1].reshape(3,3); log.append([d.time,d.qpos[0],d.qpos[1],d.qpos[2],ref(d.time)[0][0],ref(d.time)[0][1],np.degrees(np.arctan2(Rm[2,1],Rm[2,2])),np.degrees(-np.arcsin(Rm[2,0])),cs[0],cs[1]])
log=np.array(log)
res=dict(scenario=a.scenario,feedback=bool(a.fb),kp_max=a.kp,kc=a.kc,sim_time_s=float(d.time),planned_s=T,fell_at_s=fell,touchdowns=steps,
         pelvis_x_m=float(d.qpos[0]),ref_x_m=float(ref(d.time)[0][0]),mean_speed_mps=float(d.qpos[0]/max(d.time,1e-6)),
         track_err_x_final_m=float(d.qpos[0]-ref(d.time)[0][0]),kr=a.kr,torque_limit_scale=a.tscale,foot_placement_gain=a.fp,cop_clamp=a.cop,kyaw=a.kyaw,saturated_frac={names[i]:round(float(sat[i]/max(k,1)),3) for i in range(m.nu) if sat[i]>0})
print(json.dumps(res))
FS=os.path.join(HERE,'results',os.environ.get('LEGS_OUT',''),'fsim'); os.makedirs(FS,exist_ok=True)
json.dump(res,open(os.path.join(FS,f'{a.scenario}_fb{a.fb}{a.tag}.json'),'w'),indent=1)
np.save(os.path.join(FS,f'{a.scenario}_fb{a.fb}{a.tag}_log.npy'),log)
