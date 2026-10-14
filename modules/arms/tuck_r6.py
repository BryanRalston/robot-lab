"""R-065 tuck search (sim/v3 kinematics; torso box x±0.11 y±0.17 z0.05..0.31 rel torso [same box as A44 checks, EST from sim geom]).
Req: forearm+hand x <= chest front (0.11) incl. radius; >=10 mm clearance; wrist fairing as sphere r 62 (124 mm width, conservative any roll).
Fall-torque EST: inertial only, arm 9.54 kg, a = v^2/2s = 3^2/(2*0.024) = 187.5 m/s^2 (A44 pad crush) x |z_com - z_shoulder|."""
import mujoco,numpy as np,itertools,json
m=mujoco.MjModel.from_xml_path('../../sim/v3/humanoid_v3.xml'); d=mujoco.MjData(m)
J=lambda n:m.jnt_qposadr[mujoco.mj_name2id(m,mujoco.mjtObj.mjOBJ_JOINT,n)]; B=lambda n:mujoco.mj_name2id(m,mujoco.mjtObj.mjOBJ_BODY,n)
lo=np.array([-0.11,-0.17,0.05]);hi=np.array([0.11,0.17,0.31]); A=187.5; M=9.54
box=lambda p:np.linalg.norm(np.maximum(np.maximum(lo-p,p-hi),0))
def ev(sp,sr,sy,el):
    mujoco.mj_resetData(m,d); d.qpos[2]=1.16
    for n,a in (('l_shoulder_pitch',sp),('l_shoulder_roll',sr),('l_shoulder_yaw',sy),('l_elbow',el)): d.qpos[J(n)]=np.radians(a)
    mujoco.mj_forward(m,d); t=B('torso'); R=d.xmat[t].reshape(3,3); rel=lambda p:R.T@(p-d.xpos[t])
    sh=rel(d.xpos[B('L_upper_arm')]) if mujoco.mj_name2id(m,mujoco.mjtObj.mjOBJ_BODY,'L_upper_arm')>=0 else rel(d.xpos[B('L_forearm')])
    e=rel(d.xpos[B('L_forearm')]); w=rel(d.xpos[B('L_hand')]); h=w+(w-e)/np.linalg.norm(w-e)*0.09
    seg=[e+(w-e)*s for s in np.linspace(0,1,41)]
    gf=min(box(p) for p in seg)-0.038; gw=box(w)-0.062; gh=min(box(p) for p in [w+(h-w)*s for s in np.linspace(0,1,11)])-0.045
    xmax=max(max(p[0] for p in seg)+0.038,w[0]+0.062,h[0]+0.045)
    com=(0.5*sh+0.5*(e+w)/2)  # crude: half mass upper arm, half forearm+hand
    return dict(pose=[sp,sr,sy,el],x_ahead_mm=round((xmax-0.11)*1000,1),gap_forearm=round(gf*1000,1),gap_wrist62=round(gw*1000,1),gap_hand=round(gh*1000,1),
                tau_fall_Nm_EST=round(M*A*abs(com[2]-sh[2]+0.0),0))
print('old -30 tuck',ev(-30,-5,-60,-110)); print('old R5 tuck',ev(-20,-5,-60,-110))
res=[ev(*q) for q in itertools.product(range(-10,61,10),range(-30,1,5),range(-90,91,15),range(-125,-59,15))]
ok=[r for r in res if r['x_ahead_mm']<=0 and min(r['gap_forearm'],r['gap_wrist62'],r['gap_hand'])>=10]
ok.sort(key=lambda r:(r['tau_fall_Nm_EST'],-min(r['gap_forearm'],r['gap_wrist62'],r['gap_hand'])))
print(len(ok)); [print(r) for r in ok[:8]]
json.dump(dict(ok=ok[:20]),open('tuck_r6.json','w'),indent=1)
