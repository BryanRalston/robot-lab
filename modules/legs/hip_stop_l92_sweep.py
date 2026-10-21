"""L92: coupled hip yaw/roll stop surface re-sweep on model_v4_l92 (legs copy, yaw bumpers at contact -10/+26 i.e. crushed -12/+28).
Boundary of the L92 limit: roll r in {0,-3,-6,-9,-12,-12.3}, yaw_max=28-2(-3-r), yaw_min=-12+(7/9)(-3-r) (r<-3), both legs (R mirrored: R_yaw=-yaw, R_roll=-roll),
mirrored pairs + crossed (L at max / R at min), pitch -105/0/+40, knee 0/145. Gates 3 mm: L<->R knee housings, tab<->brackets (non-contacting side),
hanging hand <-> thigh parts."""
import os,sys,json,itertools
HERE=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,HERE)
import model_v4_l92 as M
_st=M.step; M.step=lambda n,*a,**k: _st('knee_twin_housing_release_r116b' if n=='knee_twin_housing' else n,*a,**k)
def lim(r):
    d=max(0,-3-min(r,-3)) if r<-3 else 0; d=min(d,9)
    return -12+7/9*d, 28-2*d
pts=[]
for r in (0,-3,-6,-9,-12,-12.3):
    lo,hi=lim(r); pts+= [(r,lo),(r,hi)]
poses=[]
for (rl,yl),(rr,yr) in itertools.product(pts,pts):
    if not ((rl,yl)==(rr,yr) or (rl==rr==0 and yl!=yr)): continue
    for pi,k in (((0,0),(0,145)) if (rl,yl)==(rr,yr) else ((0,0),)):
        poses.append({'L_hip_roll':rl,'L_hip_yaw':yl,'R_hip_roll':-rr,'R_hip_yaw':-yr,'L_hip_pitch':pi,'R_hip_pitch':pi,'L_knee':k,'R_knee':k})
B={}
def upd(k,d,pz):
    if d<B.get(k,(1e9,))[0]: B[k]=(round(d,2),pz)
for n,pz in enumerate(poses):
    ps=M.build(pz); g=lambda f:[p for p in ps if f(p['name'],p['seg'])]
    hL=g(lambda n,s:'knee twin housing' in n and s.startswith('L_')); hR=g(lambda n,s:'knee twin housing' in n and s.startswith('R_'))
    for a in hL:
        for b in hR: upd('L-R knee housings',float(a['solid'].distance(b['solid'])),pz)
    for sd in 'LR':
        tab=g(lambda n,s:n.startswith(sd+'_hip_yaw stop tab 10x12'))[0]
        for b in g(lambda n,s:n.startswith(sd+'_hip_yaw PU bumper')):
            upd(f'{sd} tab <-> {b["name"][2:]}',float(tab['solid'].distance(b['solid'])),pz)
        hand=g(lambda n,s:s==sd+'_hand'); th=g(lambda n,s:s==sd+'_thigh')
        for a in hand:
            ab=a['solid'].BoundingBox()
            for b in th:
                bb=b['solid'].BoundingBox()
                if bb.zmax<ab.zmin-20 or bb.xmin>ab.xmax+20 or bb.xmax<ab.xmin-20 or bb.ymin>ab.ymax+20 or bb.ymax<ab.ymin-20: continue
                upd(f'{sd} hand <-> thigh',float(a['solid'].distance(b['solid'])),pz)
    print(n,len(poses),flush=True)
out={k:[v[0],str(v[1])] for k,v in sorted(B.items(),key=lambda t:t[1][0])}
json.dump(out,open(f'{HERE}/results/r031/hip_stop_l92_sweep.json','w'),indent=1); print(json.dumps(out,indent=0))
