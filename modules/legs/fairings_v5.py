"""v5 fairing clearance envelopes (Legs rows 1-3, 8 of modules/design/V5_POLISH_PLAN.md).
Sweeps model_v4 (left leg), collects tessellated part vertices in the fairing's mount-segment frame,
convex hull + 5 mm offset -> STL + JSON (results/v5/). Right leg = mirror in y about y=0."""
import os,sys,json,math,itertools,numpy as np,trimesh
from scipy.spatial import ConvexHull
H=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,os.path.join(H,'..','model'))
import model_v4 as M
OUT=os.path.join(H,'results','v5'); os.makedirs(OUT,exist_ok=True); OFF=5.0
def seg_inv(seg):
    ref=np.array([[0,0,0],[100,0,0],[0,100,0],[0,0,100]],float)+np.array([0,M.P['hip_y'],500])
    W=np.array([M.xf_pt(seg,p) for p in ref]); A=W[1:]-W[0]; B=ref[1:]-ref[0]
    R=np.linalg.solve(B,A).T   # W = R*(p-ref0)+W0
    return lambda X:(X-W[0])@R+ref[0]   # R orthonormal: inverse = R^T, (X-W0)@R == (R^T (X-W0))^T
def verts(p,tol=1.5):
    v,_=p['solid'].tessellate(tol); return np.array([[q.x,q.y,q.z] for q in v])
ENV={
 'shin_fairing':dict(frame='L_shank',segs=('L_shank',),extra=('L_ankle screw',),zmin=150,zmax=470,poses=[{'L_ankle_pitch':p,'L_ankle_roll':r} for p in (-45,-30,-15,0,15,30,40) for r in (-18,-9,0,9,18)]),
 'ankle_boot':dict(frame='L_shank',segs=('L_foot','L_ankX'),extra=('L_ankle screw',),zmin=None,zmax=170,xmin=None,poses=[{'L_ankle_pitch':p,'L_ankle_roll':r} for p in (-45,-30,-15,0,15,30,40) for r in (-18,-9,0,9,18)],note='flexible TPU-nylon boot over rod ends / instep lugs; z<=170 in shank frame; excludes the foot box'),
 'thigh_fairing':dict(frame='L_thigh',segs=('L_thigh',),extra=('L_hip_pitch screw','L_knee screw'),zmin=560,zmax=880,poses=[{'L_hip_pitch':h,'L_knee':k} for h in (-105,-74.6,0,40) for k in (0,45,90,135)]),
 'knee_cap':dict(note2='r<=110 about knee axis',frame='L_thigh',segs=('L_shank',),extra=('L_knee screw',),zmin=None,zmax=None,rclip=(('L_shank',),(0,130,500),110),poses=[{'L_knee':k} for k in range(0,136,15)],note='shank-side knee lever + rod ends swept 0-135 in the thigh frame; cap (shank-mounted) must stay outside the thigh fairing and inside this keep-out complement'),
 'hip_skirt':dict(frame='pelvis',segs=('L_hipY','L_hipR','L_thigh'),extra=('L_hip_pitch screw',),zmin=None,zmax=1130,rclip=(('L_thigh','L_hipR'),(0,130,920),150),poses=[{'L_hip_yaw':y,'L_hip_roll':r,'L_hip_pitch':p} for y in (-35,0,45) for r in (-12,0,15) for p in (-105,-74.6,0,40)]),
 'foot_upper':dict(frame='L_foot',segs=('L_foot',),extra=(),exclude=('ankle screw',),zmin=18,zmax=165,poses=[{}],note='upper shell over the 240x100x18 box; sole contact patch unchanged'),
}
def collect(name,e):
    pts=[]
    for pose in e['poses']:
        parts=M.build(pose); inv=seg_inv(e['frame']) if e['frame']!='pelvis' else (lambda X:X)
        for p in parts:
            if not (p['seg'] in e['segs'] or any(p['name'].startswith(x) for x in e['extra'])): continue
            if 'foot closed box' in p['name'] and name!='foot_upper': continue
            v=inv(verts(p))
            if e.get('zmin') is not None: v=v[v[:,2]>=e['zmin']]
            if e.get('zmax') is not None: v=v[v[:,2]<=e['zmax']]
            if e.get('rclip') and p['seg'] in e['rclip'][0]:
                c=np.array(e['rclip'][1],float); v=v[np.linalg.norm(v-c,axis=1)<=e['rclip'][2]]
            if any(x in p['name'] for x in e.get('exclude',())): continue
            if len(v): pts.append(v)
        print(name,pose,flush=True)
    return np.vstack(pts)
def offset_hull(P,d):
    h=ConvexHull(P); V=P[h.vertices]
    dirs=np.array([v for v in itertools.product((-1,0,1),repeat=3) if any(v)],float); dirs/=np.linalg.norm(dirs,axis=1)[:,None]
    Q=(V[:,None,:]+d*dirs[None]).reshape(-1,3); h2=ConvexHull(Q)
    return trimesh.Trimesh(Q,h2.simplices).convex_hull,h
def main():
    res={}
    sel=sys.argv[1:] or list(ENV)
    for n in sel:
        e=ENV[n]; P=collect(n,e); mesh,h=offset_hull(P,OFF)
        mesh.export(os.path.join(OUT,f'{n}_keepout.stl'))
        b=mesh.bounds; res[n]=dict(frame=e['frame'],poses=len(e['poses']),offset_mm=OFF,bbox_min=np.round(b[0],1).tolist(),bbox_max=np.round(b[1],1).tolist(),
            volume_cm3=round(mesh.volume/1e3,1),area_cm2=round(mesh.area/1e2,1),stl=f'results/v5/{n}_keepout.stl',note=e.get('note',''))
        np.save(os.path.join(OUT,f'{n}_pts.npy'),P[ConvexHull(P).vertices].astype(np.float32))
        j=os.path.join(OUT,'envelopes.json'); old=json.load(open(j)) if os.path.exists(j) else {}
        old.update({n:res[n]}); json.dump(old,open(j,'w'),indent=1); print(n,res[n],flush=True)
if __name__=='__main__': main()
