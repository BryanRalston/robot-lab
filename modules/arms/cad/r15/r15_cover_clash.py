"""R15: carrier_w2 + pad_envelope_w2 vs ID cover STEP/STL (design/cad/covers, site frame Y-up, mm) over abduction ROM.
Site->sim world: x_w = x_s, y_w = -z_s (right-handed, Y-up), z_w = y_s + dz; dz fixed by matching the head_shell bbox centre to the sim head
geom centre (standing, qpos z 1.16). Site frame is symmetric in z, so L/R sign does not change gaps. Arms frame -> world through
L_shoulderP xform * Rx(roll) at L_upper_arm origin (same as clash_r13). Torso cover is a coarse 28-tri envelope (indicative)."""
import trimesh,numpy as np,mujoco,json,os,itertools
H=os.path.dirname(os.path.abspath(__file__)); C=os.path.join(H,'../../../design/cad/covers')
m=mujoco.MjModel.from_xml_path(os.path.join(H,'../../../../sim/v3/humanoid_v3.xml')); d=mujoco.MjData(m)
J=lambda n:m.jnt_qposadr[mujoco.mj_name2id(m,mujoco.mjtObj.mjOBJ_JOINT,n)]; B=lambda n:mujoco.mj_name2id(m,mujoco.mjtObj.mjOBJ_BODY,n)
def fk(sp,sr):
    mujoco.mj_resetData(m,d); d.qpos[2]=1.16; d.qpos[J('l_shoulder_pitch')]=np.radians(sp); d.qpos[J('l_shoulder_roll')]=np.radians(sr); mujoco.mj_forward(m,d)
fk(0,0); g=mujoco.mj_name2id(m,mujoco.mjtObj.mjOBJ_GEOM,'head'); hc=d.geom_xpos[g]*1000
cov={k:trimesh.load(os.path.join(C,k+'.stl')) for k in ('head_shell','torso_cover')}
bb=cov['head_shell'].bounds; dz=hc[2]-(bb[0][1]+bb[1][1])/2
def s2w(v): return np.c_[v[:,0],-v[:,2],v[:,1]+dz]
W={k:trimesh.Trimesh(s2w(v.vertices),v.faces) for k,v in cov.items()}
from scipy.spatial import cKDTree
S={}
for k,w in W.items():
    w.fix_normals(); sp_,fi=trimesh.sample.sample_surface_even(w,60000) if k=='torso_cover' else trimesh.sample.sample_surface(w,60000)
    S[k]=(cKDTree(sp_),sp_,w.face_normals[fi])
pts=np.vstack([trimesh.load(os.path.join(H,f)).sample(3000) for f in ('carrier_w2.stl','pad_envelope_w2.stl')])
Rx=lambda a:np.array([[1,0,0],[0,np.cos(a),-np.sin(a)],[0,np.sin(a),np.cos(a)]])
def ev(sp,sr):
    fk(sp,sr); Rs=d.xmat[B('L_shoulderP')].reshape(3,3); o=(d.xpos[B('L_shoulderP')]+Rs@np.array([0,.112,-.04]))*1000
    P=(Rs@Rx(np.radians(sr))@pts.T).T+o; r={}
    for k,w in W.items():
        t,sp_,nn=S[k]; dist,ix=t.query(P); sgn=np.einsum('ij,ij->i',P-sp_[ix],nn[ix])
        inside=bool(((sgn<0)&(dist<30)).any())
        r[k]=dict(min_gap_mm=round(float(dist.min()),1),penetrates=inside)
    return r
out=dict(dz_mm=round(float(dz),1),head_centre_sim_mm=[round(float(x),1) for x in hc],watertight={k:bool(w.is_watertight) for k,w in W.items()})
sw={}
for sp,sr in itertools.product((-150,-90,-30,0,30),(0,45,90,135,150,170,180)): sw[f'{sp},{sr}']=ev(sp,sr)
out['tuckB']=ev(5,0); out['sweep']=sw
for k in W: 
    v=min(sw.items(),key=lambda kv:kv[1][k]['min_gap_mm']); out[f'worst_{k}']=dict(pose=v[0],**v[1][k])
    out[f'worst_{k}_roll_le135']=min(((p,r[k]['min_gap_mm']) for p,r in sw.items() if int(p.split(',')[1])<=135),key=lambda t:t[1])
json.dump(out,open(os.path.join(H,'r15_cover_clash.json'),'w'),indent=1)
print({k:out[k] for k in out if k!='sweep'})
lim={}
for sp in (-150,-90,-30,0,30):
    ok=None
    for sr in range(90,136,2):
        r=ev(sp,sr)['torso_cover']
        if r['penetrates'] or r['min_gap_mm']<3: break
        ok=(sr,r['min_gap_mm'])
    lim[sp]=ok
out['torso_roll_limit_ge3mm']=lim; json.dump(out,open(os.path.join(H,'r15_cover_clash.json'),'w'),indent=1); print(lim)
