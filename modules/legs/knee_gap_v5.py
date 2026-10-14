"""Per-angle gap: shank-side knee-cap keep-out (r<=110 about knee axis, hull+5) vs thigh_fairing keep-out (hull+5), thigh frame."""
import json,os,numpy as np,trimesh
import fairings_v5 as F
M=F.M; th=trimesh.load(os.path.join(F.OUT,'thigh_fairing_keepout.stl')); out=[]
for k in range(0,136,5):
    parts=M.build({'L_knee':k}); inv=F.seg_inv('L_thigh'); P=[]
    for p in parts:
        if p['seg']!='L_shank': continue
        v=inv(F.verts(p)); v=v[np.linalg.norm(v-np.array([0,130,500]),axis=1)<=110]
        if len(v): P.append(v)
    kc,_=F.offset_hull(np.vstack(P),F.OFF)
    sd=trimesh.proximity.signed_distance(th,kc.vertices)   # +inside thigh keep-out
    pen=float(sd.max()); q=trimesh.proximity.closest_point(kc,th.vertices)[1]
    gap=float(min(q.min(),(-sd).min())) if pen<=0 else -pen
    out.append(dict(knee_deg=k,gap_mm=round(gap,1))); print(out[-1],flush=True)
json.dump(out,open(os.path.join(F.OUT,'knee_cap_vs_thigh_gap.json'),'w'),indent=1)
