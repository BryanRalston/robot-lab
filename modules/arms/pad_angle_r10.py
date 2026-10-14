"""Controls 92f2cea follow-up: pad normal (roll-yaw link, = +y of the body after l_shoulder_roll) vs ground outward normal at impact.
Fall model (Controls T-030 FK convention): trunk tips ~85 deg toward the fall azimuth, so ground outward in the pelvis frame
d = (sin85 cos az, sin85 sin az, -cos85); az 90 = left side, 45 = left-forward (LF), 135 = left-back (LB). Torso frame d_t = Rz(-waist_yaw) d.
Arm geometry: sim/v3 with forearm 287 (+17 mm, hand moved, ext mass). Clearances as tuck_r6 (torso box, forearm r38, fairing sphere r62, hand r45),
plus pelvis box / thigh capsule. Fall torque EST as tuck_r6 (inertial, 9.54 kg x 187.5 m/s^2 x COM drop)."""
import mujoco,numpy as np,itertools,json,os
H=os.path.dirname(os.path.abspath(__file__)); EXT=0.017
m=mujoco.MjModel.from_xml_path(os.path.join(H,'../../sim/v3/humanoid_v3.xml'))
for s in 'LR':
    h=mujoco.mj_name2id(m,mujoco.mjtObj.mjOBJ_BODY,f'{s}_hand'); v=m.body_pos[h].copy(); m.body_pos[h]=v+v/np.linalg.norm(v)*EXT
d=mujoco.MjData(m); J=lambda n:m.jnt_qposadr[mujoco.mj_name2id(m,mujoco.mjtObj.mjOBJ_JOINT,n)]
B=lambda n:mujoco.mj_name2id(m,mujoco.mjtObj.mjOBJ_BODY,n)
rollbody=m.jnt_bodyid[mujoco.mj_name2id(m,mujoco.mjtObj.mjOBJ_JOINT,'l_shoulder_roll')]
lo=np.array([-0.11,-0.17,0.05]);hi=np.array([0.11,0.17,0.31]); plo=np.array([-0.085,-0.185,-0.154]);phi=np.array([0.085,0.185,-0.05])
bx=lambda p,a,b:np.linalg.norm(np.maximum(np.maximum(a-p,p-b),0))
def ev(sp,sr,sy,el,wy=0.0,az=90.0):
    mujoco.mj_resetData(m,d); d.qpos[2]=1.16
    for n,a in (('l_shoulder_pitch',sp),('l_shoulder_roll',sr),('l_shoulder_yaw',sy),('l_elbow',el)): d.qpos[J(n)]=np.radians(a)
    mujoco.mj_forward(m,d); t=B('torso'); R=d.xmat[t].reshape(3,3); rel=lambda p:R.T@(p-d.xpos[t])
    n=R.T@d.xmat[rollbody].reshape(3,3)[:,1]
    a=np.radians(az); g=np.array([np.sin(np.radians(85))*np.cos(a),np.sin(np.radians(85))*np.sin(a),-np.cos(np.radians(85))])
    w_=np.radians(wy); Rz=np.array([[np.cos(w_),-np.sin(w_),0],[np.sin(w_),np.cos(w_),0],[0,0,1]]); gt=Rz.T@g
    ang=np.degrees(np.arccos(np.clip(n@gt,-1,1)))
    sh=rel(d.xpos[B('L_upper_arm')]); e=rel(d.xpos[B('L_forearm')]); w=rel(d.xpos[B('L_hand')]); hh=w+(w-e)/np.linalg.norm(w-e)*0.09
    seg=[e+(w-e)*s for s in np.linspace(0,1,41)]; hs=[w+(hh-w)*s for s in np.linspace(0,1,11)]
    # pelvis/thigh in torso frame: valid only for waist_yaw 0 (flag otherwise)
    gap=min(min(bx(p,lo,hi) for p in seg)-0.038,bx(w,lo,hi)-0.062,min(bx(p,lo,hi) for p in hs)-0.045,
            min(bx(p,plo,phi) for p in seg)-0.038,bx(w,plo,phi)-0.062,min(bx(p,plo,phi) for p in hs)-0.045)
    xa=max(max(p[0] for p in seg)+0.038,w[0]+0.062,hh[0]+0.045)-0.11
    com=0.5*sh+0.25*(e+w); tau=9.54*187.5*abs(com[2]-sh[2])
    return dict(pose=[sp,sr,sy,el],waist_yaw=wy,az=az,pad_angle_deg=round(float(ang),1),min_gap_mm=round(gap*1000,1),x_ahead_mm=round(xa*1000,1),tau_fall_Nm_EST=round(tau))
out={'ref':{'B_side':ev(5,0,0,0),'R5_side':ev(-20,-5,-60,-110),'B_LF':ev(5,0,0,0,az=45),'B_LB':ev(5,0,0,0,az=135)}}
ok=lambda r:r['pad_angle_deg']<=15 and r['min_gap_mm']>=10 and r['x_ahead_mm']<=0 and r['tau_fall_Nm_EST']<=369
grid=list(itertools.product(range(-30,61,5),range(-15,61,5),range(-90,91,15),range(-125,1,25)))
for az in (90,45,135):
    rs=[ev(*q,az=az) for q in grid]; good=[r for r in rs if ok(r)]
    good.sort(key=lambda r:(r['tau_fall_Nm_EST'],r['pad_angle_deg']))
    out[f'az{az}_arm_only']=dict(n_ok=len(good),best=good[:5],min_angle=min(r['pad_angle_deg'] for r in rs))
for az in (45,135):  # tuck B + waist yaw turning the shoulder into the fall
    out[f'az{az}_B_waistyaw']=[ev(5,0,0,0,wy=w,az=az) for w in (-45,-30,-15,0,15,30,45)]
json.dump(out,open(os.path.join(H,'pad_angle_r10.json'),'w'),indent=1); print(json.dumps(out,indent=0)[:5000])
