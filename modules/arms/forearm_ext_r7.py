"""R-076: forearm +EXT mm (board in forearm, CSG-14 yaw). Static torques with 10 kg/hand (R1 load model) before/after.
Extension mass: 7075 tube OD70/ID66 (model_v4 forearm shell) x EXT, rho 2.81 g/cm3 (ASM 7075-T6) + sheaths/leads [EST]."""
import mujoco,numpy as np,json,os
EXT=0.015; RHO=2810; A=np.pi/4*(0.070**2-0.066**2); M_EXT=A*EXT*RHO+0.001
H=os.path.dirname(os.path.abspath(__file__)); X=os.path.join(H,'../../sim/v3/humanoid_v3.xml')
def build(ext):
    m=mujoco.MjModel.from_xml_path(X)
    for s in 'LR':
        h=mujoco.mj_name2id(m,mujoco.mjtObj.mjOBJ_BODY,f'{s}_hand'); f=mujoco.mj_name2id(m,mujoco.mjtObj.mjOBJ_BODY,f'{s}_forearm')
        v=m.body_pos[h].copy(); u=v/np.linalg.norm(v); m.body_pos[h]=v+u*ext
        if ext: 
            mf=m.body_mass[f]; c=m.body_ipos[f]; pe=v+u*ext/2; m.body_ipos[f]=(mf*c+M_EXT*pe)/(mf+M_EXT); m.body_mass[f]=mf+M_EXT
    return m
def tq(m,sp,el):
    d=mujoco.MjData(m); d.qpos[2]=1.16
    J=lambda n:mujoco.mj_name2id(m,mujoco.mjtObj.mjOBJ_JOINT,n)
    for n,a in (('l_shoulder_pitch',sp),('l_elbow',el)): d.qpos[m.jnt_qposadr[J(n)]]=np.radians(a)
    mujoco.mj_forward(m,d); hb=mujoco.mj_name2id(m,mujoco.mjtObj.mjOBJ_BODY,'L_hand')
    pt=d.xpos[hb]+d.xmat[hb].reshape(3,3)@np.array([0,0,-0.10]); jp=np.zeros((3,m.nv)); mujoco.mj_jac(m,d,jp,None,pt,hb)
    t=d.qfrc_bias+jp.T@np.array([0,0,98.1]); r=lambda n:round(abs(float(t[m.jnt_dofadr[J(n)]])),2)
    tb=mujoco.mj_name2id(m,mujoco.mjtObj.mjOBJ_BODY,'torso')
    return dict(elbow=r('l_elbow'),shoulder_pitch=r('l_shoulder_pitch'),reach_x=round(float((pt-d.xpos[tb])[0]),3))
m0,m1=build(0),build(EXT); out=dict(EXT_mm=EXT*1000,M_EXT_kg_side=round(M_EXT,4))
for k,(sp,el) in dict(P042=(-20,0),R1_carry=(-30,-60),reach_horiz=(-90,0),reach_elbow90=(-90,-90) ).items():
    a,b=tq(m0,sp,el),tq(m1,sp,el); out[k]=dict(before=a,after=b,d_elbow=round(b['elbow']-a['elbow'],2),d_shoulder=round(b['shoulder_pitch']-a['shoulder_pitch'],2))
print(json.dumps(out,indent=1)); json.dump(out,open(os.path.join(H,'forearm_ext_r7.json'),'w'),indent=1)
