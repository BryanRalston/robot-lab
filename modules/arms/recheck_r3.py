"""Re-check P-042 pose and R1 worst cases with catalog inertials (arm_inertials_r3.json) applied in memory to sim/v3."""
import json,os,numpy as np,mujoco
H=os.path.dirname(os.path.abspath(__file__)); I=json.load(open(os.path.join(H,'arm_inertials_r3.json')))
import carry_pose_r3 as c
m=c.m
for side,s in (('L',1),('R',-1)):
    for b in ('shoulderP','upper_arm','forearm','hand'):
        v=I['L_'+b]; i=mujoco.mj_name2id(m,mujoco.mjtObj.mjOBJ_BODY,f'{side}_{b}')
        m.body_mass[i]=v['mass']; p=np.array(v['pos']); p[1]*=s; m.body_ipos[i]=p
        f=v['fullinertia']; M=np.array([[f[0],f[3],f[4]],[f[3],f[1],f[5]],[f[4],f[5],f[2]]]); w,V=np.linalg.eigh(M)
        m.body_inertia[i]=w; q=np.zeros(4); mujoco.mju_mat2Quat(q,V.flatten()); m.body_iquat[i]=q
res={k:c.load(*a) for k,a in {'P042_pose':(-60,-110),'band_edge_sp-60_el-100':(-60,-100),'band_edge_sp-45_el-115':(-45,-115),'R1_carry':(-30,-60),'reach':(-90,0)}.items()}
json.dump(res,open(os.path.join(H,'recheck_r3.json'),'w'),indent=1)
for k,v in res.items(): print(k,v)
