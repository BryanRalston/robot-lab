"""v4 audit fixes: clash/clearance verification in the Model v4 assembly (modules/model/model_v4.py, read-only) with the new Actuators STEPs.
Patches (local to this run, mirror what Legs/Model must adopt): knee -y body = mirrored knee_body_x1 (outer boss outboard, half web inboard);
ankle bodies on the axial top eye (eye centre = old trunnion point, raised to z 450; base 15 mm ahead of the eye).
Checks: interference volume > 0.5 mm3 between actuator parts and anything not mated (clash_v4.MATES), and min distance body->neighbours.
Ankle rod-end head vs instep lug is checked analytically in ankle_v4.py (the model eye is a fixed ø30x12 disc, not a misaligning ball)."""
import sys,os,json,itertools,time
R=os.path.abspath(os.path.join(os.path.dirname(__file__),'../model')); sys.path.insert(0,R); os.chdir(R)
import model_v4 as M, clash_v4 as K, numpy as np
_step=M.step
def step(n):
    if n.endswith('_m'): return _step(n[:-2]).mirror('YZ')
    return _step(n)
M.step=step; M.BOSS_Z['knee_body_x1_m']=M.BOSS_Z['knee_body_x1']; M.BOSS_Z['ankle_body_x1']=-15.0; M.P['ankle_tz']=450
_su=M.screw_unit
def su(name,body_step,*a,**k):
    if body_step=='knee_body_x1' and ' -y' in name: body_step='knee_body_x1_m'
    return _su(name,body_step,*a,**k)
M.screw_unit=su
def build(pose):
    M.PARTS.clear();M.JOINTS.clear();M.PARENT.clear();M.POSE.clear();M.POSE.update(pose);M.build_leg(1); return M.PARTS
def check(pose,keys,skip=()):
    P=build(pose); A=[p for p in P if any(k in p['name'] for k in keys)]; out=[]; dmin={}
    for a in A:
        ba=K.bb(a,3)
        for o in P:
            if o is a or K.mate(a,o) or any(k in o['name'] for k in keys) and o['asm']==a['asm']: continue
            if any(s1 in a['name'] and s2 in o['name'] or s1 in o['name'] and s2 in a['name'] for s1,s2 in skip): continue
            if not K.ov(ba,K.bb(o)): continue
            v=K.vol(a,o)
            if v>0.5: out.append((a['name'],o['name'],round(v,1)))
            elif 'body (' in a['name']:
                d=a['solid'].distance(o['solid']); k=o['name']
                if d<dmin.get(k,1e9): dmin[k]=d
    return out,dmin
if __name__=='__main__':
    res={}; t=time.time()
    SK=(('rod-end eye','instep lug'),('roller-screw rod','instep lug'),('trunnion pin','body'),('trunnion cheek','body'))   # ankle eye/lug: analytic (ankle_v4); old trunnion pins/cheeks are retired by D60
    for kq in range(0,136,15):
        c,d=check({'L_knee':kq},('knee screw',),SK); res[f'knee{kq}']=dict(clash=c,min_body_gap=min(d.values()) if d else None); print('knee',kq,c,round(min(d.values()),2) if d else '-',round(time.time()-t),flush=True)
    for ap in (-45,-20,0,20,40):
        for ar in (-18,0,18):
            c,d=check({'L_ankle_pitch':ap,'L_ankle_roll':ar},('ankle screw',),SK); res[f'ankle{ap}_{ar}']=dict(clash=c,min_body_gap=min(d.values()) if d else None); print('ankle',ap,ar,c,round(min(d.values()),2) if d else '-',round(time.time()-t),flush=True)
    for hp in range(-105,41,15):
        c,d=check({'L_hip_pitch':hp},('hip_pitch screw',),SK); dd={k[2:]:round(v,2) for k,v in d.items()}; res[f'hip{hp}']=dict(clash=c,gaps=dd,min_body_gap=min(d.values()) if d else None); print('hip',hp,c,sorted(dd.items(),key=lambda x:x[1])[:2],round(time.time()-t),flush=True)
    json.dump(res,open(os.path.join(os.path.dirname(os.path.abspath(__file__)),'results/verify_v4.json'),'w'),indent=1,default=str)
