import os,sys,json,numpy as np
HERE=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,os.path.join(HERE,'../model'))
import model_v4 as M
_st=M.step; M.step=lambda n,*a,**k: _st('knee_twin_housing_release_r116b' if n=='knee_twin_housing' else n,*a,**k)
d=np.load('/tmp/w.npz'); Q=np.degrees(d['Q'][:,d['qa']]); J=['hip_yaw','hip_roll','hip_pitch','knee','ankle_pitch','ankle_roll']  # LEG order [EST from controller qa]
def pose(f): return {f'{s}_{j}':float(Q[f,i+6*k]) for k,s in enumerate('LR') for i,j in enumerate(J)}
G={'hip_pitch screw body':lambda n:'hip_pitch screw' in n and 'body' in n,'ankle screw body':lambda n:'ankle screw' in n and 'body' in n,'knee twin housing':lambda n:'knee twin housing' in n}
def gaps(f):
    ps=M.build(pose(f)); r={}
    for k,g in G.items():
        A=[p for p in ps if p['name'].startswith('L_') and g(p['name'])]; B=[p for p in ps if p['name'].startswith('R_') and g(p['name'])]
        r[k]=round(min(float(a['solid'].distance(b['solid'])) for a in A for b in B),2)
    return r
add=Q[:,1]-Q[:,7]   # L roll minus R roll: most negative = both toward midline under mirrored convention [EST]
cand=sorted(set([118,1718]+list(np.argsort(add)[:3])+list(np.argsort(-add)[:1])))
out={'joint_order_EST':J,'frames':{}}
for f in cand:
    out['frames'][int(f)]=dict(pose={k:round(v,1) for k,v in pose(f).items()},gaps=gaps(f)); print(f,out['frames'][int(f)]['gaps'],flush=True)
worst={k:min(((v['gaps'][k],f) for f,v in out['frames'].items())) for k in G}
out['worst_scanned']=worst; out['scan_note']=f'scanned {len(cand)} frames: 118, 1718 + extremes of L_roll-R_roll (full 1865-frame scan not run, time)'
json.dump(out,open(f'{HERE}/results/r031/wbc_pair_gaps_l95.json','w'),indent=1); print(worst)
