import mujoco,numpy as np
m=mujoco.MjModel.from_xml_path('humanoid.xml');d=mujoco.MjData(m)
print('nq',m.nq,'nv',m.nv,'nu',m.nu,'total mass %.1f kg'%m.body_subtreemass[1])
q0=d.qpos.copy()
mujoco.mj_forward(m,d)
# drop to ground: find lowest foot point, set height
mujoco.mj_forward(m,d)
lo=min(d.geom_xpos[i][2]-0.02 for i in range(m.ngeom) if 'foot' in m.geom(i).name)
d.qpos[2]-=lo-0.001;q0=d.qpos.copy()
jid=[m.actuator_trnid[i,0] for i in range(m.nu)];qa=[m.jnt_qposadr[k] for k in jid];va=[m.jnt_dofadr[k] for k in jid]
kp=np.array([max(50,m.actuator_ctrlrange[i,1]*4) for i in range(m.nu)]);kd=kp*0.05
for t in range(int(10/m.opt.timestep)):
    d.ctrl[:]=np.clip(kp*(q0[qa]-d.qpos[qa])-kd*d.qvel[va],m.actuator_ctrlrange[:,0],m.actuator_ctrlrange[:,1])
    mujoco.mj_step(m,d)
    if t%1000==0: print('t=%.0fs pelvis z=%.3f'%(d.time,d.qpos[2]))
up=d.xmat[1].reshape(3,3)[2,2]
print('final pelvis z %.3f (start %.3f), upright cos %.3f, max |tau| %.0f N·m'%(d.qpos[2],q0[2],up,np.abs(d.actuator_force).max()))
print('STANDS' if d.qpos[2]>q0[2]-0.05 and up>0.95 else 'FELL')
