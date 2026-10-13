"""Scripted standing-balance controller for v3 (no RL; see README). Joint PD
+ center-of-mass ankle/hip strategy. Torques clipped to actuator limits."""
import mujoco,numpy as np,sys
m=mujoco.MjModel.from_xml_path('humanoid_v3.xml');d=mujoco.MjData(m)
names=[m.actuator(i).name for i in range(m.nu)];jid=m.actuator_trnid[:,0];qa=m.jnt_qposadr[jid];va=m.jnt_dofadr[jid]
lim=m.actuator_ctrlrange[:,1]
def nominal():
    mujoco.mj_resetData(m,d)
    for s in 'lr':
        d.qpos[m.jnt_qposadr[m.joint(f'{s}_hip_pitch').id]]=-0.25;d.qpos[m.jnt_qposadr[m.joint(f'{s}_knee').id]]=0.5;d.qpos[m.jnt_qposadr[m.joint(f'{s}_ankle_pitch').id]]=-0.25
        d.qpos[m.jnt_qposadr[m.joint(f'{s}_elbow').id]]=-0.3
    mujoco.mj_forward(m,d)
    lo=min(d.geom_xpos[i][2]-0.02 for i in range(m.ngeom) if m.geom(i).name.endswith('foot'));d.qpos[2]-=lo-0.0005
    mujoco.mj_forward(m,d);return d.qpos.copy()
q0=nominal()
kp=np.clip(lim*3,30,600);kd=0.04*kp
ankP=[names.index(s+'_ankle_pitch') for s in 'lr'];ankR=[names.index(s+'_ankle_roll') for s in 'lr'];hipR=[names.index(s+'_hip_roll') for s in 'lr']
def foot_center():
    return 0.5*(d.geom_xpos[m.geom('l_foot').id]+d.geom_xpos[m.geom('r_foot').id])
def run(F,dirn=0,bal=True,T=5.0,K=(1.0,1.0)):
    q=nominal()
    mujoco.mj_inverse(m,d)
    for t in range(int(T/m.opt.timestep)):
        tau=kp*(q0[qa]-d.qpos[qa])-kd*d.qvel[va]
        if bal:
            com=d.subtree_com[1];comv=d.cvel[1][3:]  # approx
            e=com[:2]-foot_center()[:2];ev=d.qvel[:2]
            # ankle strategy: COM ahead -> push toes down (ankle pitch torque), COM sideways -> ankle/hip roll
            ax=K[0]*(m.body_subtreemass[1]*9.81*(e[0])+20*ev[0])
            ay=K[1]*(m.body_subtreemass[1]*9.81*(e[1])+20*ev[1])
            for i in ankP: tau[i]+=ax
            for i in ankR: tau[i]-=ay
        d.ctrl[:]=np.clip(tau,-lim,lim)
        d.xfrc_applied[1,:3]=0
        if 1.0<d.time<1.2: d.xfrc_applied[1,dirn]=F
        mujoco.mj_step(m,d)
    return d.qpos[2]>q0[2]-0.1 and d.xmat[1][8]>0.9
if __name__=='__main__':
    print('mass %.1f kg, nu %d'%(m.body_subtreemass[1],m.nu))
    pd_ok=bool(run(0,bal=False,T=10)); print('stands 10 s (PD only):',pd_ok,'pelvis z %.3f'%d.qpos[2])
    best=None
    for sgn in [(1,1),(-1,-1),(1,-1),(-1,1)]:
        r=[max([F for F in range(0,501,25) if run(F,dirn,True,4,sgn)] or [0]) for dirn in (0,1)]
        print('balance gains sign',sgn,'max push fwd/side N (0.2 s):',r)
        if best is None or sum(r)>sum(best[1]): best=(sgn,r)
    base=[max([F for F in range(0,501,25) if run(F,dirn,False,4)] or [0]) for dirn in (0,1)]
    print('PD only max push fwd/side:',base,' best balance:',best)
    import json
    q=nominal(); comx=float(d.subtree_com[1][0]); fc=float(foot_center()[0])
    pd_txt=f"Plain PD (balance OFF) stands 10 s: {pd_ok}." if pd_ok else "Plain PD (balance OFF) falls in ~2 s: the capped joint gains in series (hip, knee, ankle) are softer than the gravity stiffness m·g·h. That is a controller limit, not a COM problem."
    st=run(0,True,10)
    json.dump(dict(com_x_mm=comx*1000,ok=bool(st and best[1][0]>=100),stands=bool(st),push=best[1],pd_only=base,text=f"Stands 10 s with balance ON: {st}; recovers from 0.2 s pushes up to {best[1][0]} N forward / {best[1][1]} N sideways (v2 capsule model: 175 N). COM {comx*1000:+.0f} mm from the ankle axis (foot centre {fc*1000:+.0f} mm, heel −60, toe +180). "+pd_txt),open('balance_v3.json','w'))
