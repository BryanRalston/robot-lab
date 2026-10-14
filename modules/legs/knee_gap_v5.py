"""Per-angle gap: shank-side knee-cap keep-out (r<=110 about knee axis, hull+5) vs thigh_fairing keep-out (hull+5), thigh frame."""
import json,os,numpy as np,trimesh
import fairings_v5 as F
M=F.M; n=20000;i=np.arange(n)+.5;ph=np.arccos(1-2*i/n);tt=np.pi*(1+5**.5)*i
U=np.c_[np.cos(tt)*np.sin(ph),np.sin(tt)*np.sin(ph),np.cos(ph)]
def sep(A,B,D):  # convex sets: max_u (min u.A - max u.B) over u and -u; >0 gap (lower bound, ~exact w/ dense u), <0 = -min penetration depth along best axis
    D=np.vstack([D,-D]); return float(np.max((A@D.T).min(0)-(B@D.T).max(0)))
th=trimesh.load(os.path.join(F.OUT,'thigh_fairing_keepout.stl')); out=[]
for k in range(0,136,5):
    parts=M.build({'L_knee':k}); inv=F.seg_inv('L_thigh'); P=[]
    for p in parts:
        if p['seg']!='L_shank': continue
        v=inv(F.verts(p)); v=v[np.linalg.norm(v-np.array([0,130,500]),axis=1)<=110]
        if len(v): P.append(v)
    kc,_=F.offset_hull(np.vstack(P),F.OFF)
    gap=sep(kc.vertices,th.vertices,np.vstack([U,kc.face_normals,th.face_normals]))
    out.append(dict(knee_deg=k,gap_mm=round(gap,1))); print(out[-1],flush=True)
json.dump(out,open(os.path.join(F.OUT,'knee_cap_vs_thigh_gap.json'),'w'),indent=1)
