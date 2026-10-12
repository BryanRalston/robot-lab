import mujoco,numpy as np
m=mujoco.MjModel.from_xml_path('humanoid.xml');d=mujoco.MjData(m);mujoco.mj_forward(m,d);q0=d.qpos.copy()
jid=m.actuator_trnid[:,0];qa=m.jnt_qposadr[jid];va=m.jnt_dofadr[jid]
kp=np.maximum(50,m.actuator_ctrlrange[:,1]*4);kd=kp*0.05
names=[m.actuator(i).name for i in range(m.nu)];ap=[names.index(s+'_ankle_pitch') for s in 'lr'];hp=[names.index(s+'_hip_pitch') for s in 'lr']
def run(F,bal):
    mujoco.mj_resetData(m,d);mujoco.mj_forward(m,d)
    for t in range(int(6/m.opt.timestep)):
        tau=kp*(q0[qa]-d.qpos[qa])-kd*d.qvel[va]
        if bal:
            # pelvis pitch (from quat) & rate -> ankle strategy
            w,x,y,z=d.qpos[3:7];pitch=np.arcsin(np.clip(2*(w*y-z*x),-1,1));com=d.subtree_com[1][0]-0.5*(d.xpos[m.body('l_foot').id][0]+d.xpos[m.body('r_foot').id][0])
            for i in ap: tau[i]+= 900*com+60*d.qvel[0]
            for i in hp: tau[i]+= -300*pitch-30*d.qvel[4]
        d.ctrl[:]=np.clip(tau,m.actuator_ctrlrange[:,0],m.actuator_ctrlrange[:,1])
        d.xfrc_applied[1,0]=F if 1.0<d.time<1.2 else 0
        mujoco.mj_step(m,d)
    return d.qpos[2]>0.85 and d.xmat[1][8]>0.9
print('stand still:',run(0,False))
for bal in (False,True):
    ok=[F for F in range(0,401,25) if run(F,bal)]
    print('balance' if bal else 'plain PD','max push survived (N for 0.2s):',max(ok) if ok else 0)
