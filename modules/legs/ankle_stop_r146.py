"""R-146: can the ankle dorsiflexion stop go past -0.79 rad? Sign: model_v4 ankle_pitch about +y, x forward, so NEGATIVE = dorsiflexion
(toe up / shank forward), same as Controls/MJCF (range -0.785..+0.698) and CONTRACTS (mech -60..+40, loaded -50..+40).
(A) kneel need: rigid foot (box x -60..180, sole z 0, no toe joint) pivots on the toe edge (180,0); knee 145; thigh/shank 420/420;
    ankle axis 80 above sole. CoM proxy = hip over the toe edge [EST]. Solve shank angle for each heel-lift; need = most negative q.
(B) screw: 2D pin-to-pin L(q) trunnion (90,450) -> instep pin R(q)(73,20) about ankle (0,80); arm = moment arm; need_min_len 250.7
    (Actuators ankle_stroke_73_r18_p60: Lmin 262.6 at -60 incl roll 18, margin 11.9). F per screw from avail 323.8 N.m / (2 x 0.073) [EST].
(C) OCC clearance shank/ankle linkage vs foot/cross at knee 145, ankle -45..-75 (model_v4)."""
import os,sys,json,math,numpy as np
H=os.path.dirname(os.path.abspath(__file__)); out={}
Ls=Lt=420.; AZ=80.; T=np.array([90.,450.]); PIN=np.array([73.,20.]); A0=np.array([0.,80.])
def R(q): c,s=math.cos(q),math.sin(q); return np.array([[c,s],[-s,c]])   # q>0 toe down (x->-z)
# (A) foot pitch b (toe-down heel lift, rad); ankle position from toe pivot; shank angle psi forward from vertical; ankle q = -(psi - b)
need=[]
for bd in np.arange(0,61,5):
    b=math.radians(bd); A=np.array([180.,0.])+R(b)@(np.array([0.,AZ])-np.array([180.,0.]))  # foot rotated toe-down about toe edge
    best=None
    for psid in np.arange(0,120,0.25):
        p=math.radians(psid); K=A+Ls*np.array([math.sin(p),math.cos(p)])
        th=p-math.radians(145)   # thigh direction: knee flex 145 between shank and thigh
        Hp=K+Lt*np.array([-math.sin(th)*-1,math.cos(th)]) if False else K+Lt*np.array([math.sin(th),math.cos(th)])
        e=abs(Hp[0]-180.)
        if best is None or e<best[0]: best=(e,psid,Hp[1],K[1])
    e,psid,hz,kz=best; q=-(psid-bd)
    need.append(dict(heel_lift_deg=int(bd),shank_fwd_deg=psid,ankle_q_deg=round(q,1),ankle_q_rad=round(math.radians(q),3),hip_z=round(hz),knee_z=round(kz),hip_err=round(e,1)))
out['A_kneel_need_knee145']=need
# (B)
F=323.8/2/0.073; rows=[]
for qd in np.arange(-45,-91,-2.5):
    q=math.radians(qd); P=A0+R(q)@PIN; u=(P-T)/np.linalg.norm(P-T); L=float(np.linalg.norm(P-T)); r=P-A0; arm=abs(r[0]*u[1]-r[1]*u[0])
    rows.append(dict(q_deg=qd,L2d=round(L,1),arm_mm=round(arm,1),tau_avail_Nm=round(2*F*arm/1000,1)))
L60=[r for r in rows if r['q_deg']==-60][0]['L2d']; 
for r in rows: r['L_with_roll18_est']=round(r['L2d']-(L60-262.6),1); r['len_margin_mm']=round(r['L_with_roll18_est']-250.7,1)
out['B_screw']=dict(F_screw_N_est=round(F),rows=rows)
# (C)
if os.environ.get('OCC','1')=='1':
    sys.path.insert(0,os.path.join(H,'../model')); import model_v4 as M
    C=[]
    for qd in (-45,-55,-60,-65,-70,-75):
        parts=M.build({'L_knee':145,'L_ankle_pitch':qd}); fo=[p for p in parts if p['seg'] in ('L_foot','L_ankX') and 'pin stub' not in p['name']]; sh=[p for p in parts if p['seg']=='L_shank' and 'ankle screw' not in p['name']]
        scr=[p for p in parts if p['seg']=='L_shank' and 'ankle screw' in p['name']]
        best=(1e9,'')
        for a in fo:
            ba=a['solid'].BoundingBox()
            for b in sh+([s for s in scr if 'eye' not in s['name']]):
                bb=b['solid'].BoundingBox(); m=20
                if bb.xmin>ba.xmax+m or bb.xmax<ba.xmin-m or bb.zmin>ba.zmax+m or bb.zmax<ba.zmin-m or bb.ymin>ba.ymax+m or bb.ymax<ba.ymin-m: continue
                d=float(a['solid'].distance(b['solid']))
                if d<best[0]: best=(round(d,1),a['name']+' | '+b['name'])
        C.append(dict(q_deg=qd,min_mm=best[0],pair=best[1])); print(C[-1],flush=True)
    out['C_clearance_knee145']=C
json.dump(out,open(f'{H}/results/r146/ankle_stop_r146.json','w'),indent=1)
print(json.dumps({k:v for k,v in out.items() if k!='C_clearance_knee145'},indent=0))
