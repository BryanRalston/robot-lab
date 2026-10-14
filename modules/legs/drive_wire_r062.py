"""R-062: knee drive bay G2 (femur rear, thigh frame box 26x52x104 at (-20.5,130,740)) -> knee motor wire length from model_v4.
Motor end = the knee twin housing, measured to its nearest point and to its far (motor-can) end; knee 0..135 (housing pivots on the
trunnion). Route = straight + bends: reported as straight-line CAD distance and an L-route (|dx|+|dz| in the thigh x-z plane + |dy|) as the upper bound."""
import os,sys,json,numpy as np
HERE=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,os.path.join(HERE,'../model'))
import cadquery as cq, model_v4 as M
bay=np.array([-20.5,130,740]); face=np.array([-33.5,130,740]); rows=[]
for a in (0,45,90,135):
    P=M.build({'L_knee':a}); H=[p for p in P if p['name'].startswith('L_knee twin housing')][0]['solid']
    vs,_=H.tessellate(2.0); V=np.array([[v.x,v.y,v.z] for v in vs]); c=V.mean(0)
    for sy in (1,-1):
        m=V[np.sign(V[:,1]-130)==sy]; far=m[np.argmax(np.linalg.norm(m-face,axis=1))]; near=m[np.argmin(np.linalg.norm(m-face,axis=1))]
        rows.append(dict(knee=a,side=sy,centroid=c.round(1).tolist(),near_mm=round(float(np.linalg.norm(near-face)),1),far_mm=round(float(np.linalg.norm(far-face)),1),
                         Lroute_far_mm=round(float(np.abs(far-face).sum()),1)))
    print(rows[-2:],flush=True)
json.dump(rows,open(f'{HERE}/results/r031/drive_wire_r062.json','w'),indent=1)
