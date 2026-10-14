"""Interference + floating-part check for model_v4, and a sweep through every joint's range.
Writes modules/model/out/clash_v4.json. usage: clash_v4.py [--stand] [joint ...]"""
import sys,json,os,itertools,time,math
import model_v4 as M
# intended contacts between different sub-assemblies (pins in bores, eyes on pins, bolted faces)
MATES=[('PU bumper','femur tube'),('bumper arm','bracket web'),('bumper arm','bumper'),('axial GE12','body'),('wrist pitch pin','fork'),('wrist pitch pin','cross'),('wrist pitch pin','palm wrist lug'),('wrist end cap','wrist_roll'),('stereo camera','head shell'),('neck mount deck','head shell'),('compute bay','battery'),('eye stub flange','body'),('eye stub','eye stub'),('tongue neck','tibia'),('tongue neck','doubler'),('torso waist bracket','battery'),('mount deck','pelvis shell'),('mount deck','hip yaw housing'),('mount deck','waist_yaw'),('eye stub','body'),('eye tine','clamp eye pin'),('eye tine','clamp arm root'),('strut','femur tube'),('strut','tibia tube'),('strut','top plate'),('strut','doubler'),('axial GE12','eye stub'),('axial GE12','clamp'),('knee trunnion','femur'),('knee trunnion','body'),('ankle trunnion','tibia'),('ankle trunnion','body'),('ankle trunnion','trunnion'),('knee trunnion','trunnion'),('roll pin stub','roll lug'),('roll pin stub','ankle cross'),('pitch pin stub','ankle cross'),('pitch pin stub','fork cheek'),('roll-stop shoulder','foot closed box'),('bumper','pad'),('waist yaw output','waist_yaw'),('waist yoke','waist yaw output'),('torso waist bracket','torso shell'),('hip yaw housing','mount ring'),('hip yaw housing','yoke plate'),('hip roll housing','yoke cheek'),('hip roll housing','roll-output bracket'),
 ('lever B','shaft'),('lever B','TLA3520'),('lever B','roll-output bracket'),('lever B','GE12'),('lever B','RV12'),('shaft','tongue'),('TLA3520','tongue'),('TLA3520','shaft'),
 ('body','RV12'),('GE12','RV12'),('body','clamp eye pin'),('body','clamp arm'),('body','trunnion pin'),('knee lever','GE12'),('knee lever','RV12'),
 ('knee pin','clevis cheek'),('knee pin','tongue'),('knee pin','knee lever'),('instep pin','GE12'),('instep pin','instep lug'),
 ('ankle pitch pin','fork cheek'),('ankle roll pin','ankle cross'),('ankle roll pin','roll lug'),('ankle pitch pin','ankle cross'),('ankle cross','stop block'),
 ('hard-stop lug','housing'),('crossed-roller','housing'),('torso waist bracket','waist_pitch'),('waist yoke','waist_pitch'),('waist yaw-pitch yoke','waist_yaw'),
 ('waist_yaw','mount plate'),('shoulder_pitch','torso shell'),('shoulder pitch output flange','shoulder_pitch'),('shoulder roll bracket','shoulder_roll'),
 ('roll-yaw link','shoulder_roll'),('roll-yaw link','shoulder_yaw'),('upper arm tube','shoulder_yaw'),('elbow clevis','elbow'),('forearm shell','elbow'),
 ('forearm shell','wrist_roll'),('wrist roll output fork','wrist_roll'),('wrist roll output fork','wrist pitch/yaw cross'),('palm wrist lug','wrist pitch/yaw cross'),
 ('neck_yaw','torso shell'),('neck yoke','neck_yaw'),('neck yoke','neck_pitch'),('head neck mount','neck_pitch'),('elbow clevis','upper arm tube'),
('crossed-roller','output flange'),('crossed-roller','yoke'),
 ('crossed-roller','bracket'),('crossed-roller','link'),('crossed-roller','clevis'),('crossed-roller','fork'),('crossed-roller','mount plate'),('crossed-roller','torso shell'),('crossed-roller','neck mount')]
def mate(a,b):
    if a['asm']==b['asm']: return True
    x,y=a['name'],b['name']
    return any((p in x and q in y) or (p in y and q in x) for p,q in MATES)
def bb(p,m=0):
    b=p['solid'].BoundingBox(); return (b.xmin-m,b.xmax+m,b.ymin-m,b.ymax+m,b.zmin-m,b.zmax+m)
def ov(a,b): return not(a[1]<b[0] or b[1]<a[0] or a[3]<b[2] or b[3]<a[2] or a[5]<b[4] or b[5]<a[4])
def vol(a,b):
    try: return a['solid'].intersect(b['solid']).Volume()
    except Exception: return -1
def clashes(parts,moved=None,thr=2.0):
    B=[bb(p) for p in parts]; out=[]
    for i,j in itertools.combinations(range(len(parts)),2):
        if moved is not None and (moved(parts[i])==moved(parts[j])): continue
        if not ov(B[i],B[j]) or mate(parts[i],parts[j]): continue
        v=vol(parts[i],parts[j])
        if v>thr: out.append((parts[i]['name'],parts[j]['name'],round(v,1)))
    return out
def floating(parts,tol=0.3):
    """connectivity graph via touching (distance<=tol) between ANY parts; components not containing the pelvis shell are floating."""
    n=len(parts); B=[bb(p,tol) for p in parts]; adj={i:set() for i in range(n)}
    for i,j in itertools.combinations(range(n),2):
        if not ov(B[i],B[j]): continue
        try: d=parts[i]['solid'].distance(parts[j]['solid'])
        except Exception: d=0
        if d<=tol: adj[i].add(j); adj[j].add(i)
    root=[i for i,p in enumerate(parts) if p['name'].startswith('pelvis shell')][0]; seen={root}; st=[root]
    while st:
        k=st.pop()
        for q in adj[k]-seen: seen.add(q); st.append(q)
    return [parts[i]['name'] for i in range(n) if i not in seen]
LIM={'hip_yaw':(-35,45),'hip_roll':(-12,15),'hip_pitch':(-105,40),'knee':(0,135),'ankle_pitch':(-45,40),'ankle_roll':(-18,18),
     'waist_yaw':(-90,90),'waist_pitch':(-30,60),'shoulder_pitch':(-180,60),'shoulder_roll':(-15,180),'shoulder_yaw':(-150,150),'elbow':(-140,0),
     'wrist_roll':(-170,170),'wrist_pitch':(-70,70),'wrist_yaw':(-40,40),'neck_yaw':(-80,80),'neck_pitch':(-40,40)}   # sim/v3 humanoid_v3.xml (ankle roll ±18 per L31)
def jname(k): return k if k.startswith(('waist','neck')) else 'L_'+k
def steps(lim,st):
    a=list(range(0,int(lim),st if lim>0 else -st))[1:]+[lim]; return a
ARM=('uarm','farm','wR','wP','hand'); LEG=('hipY','hipR','thigh','shank','ankX','foot')
def armleg(c,parts):
    seg={p['name']:p['seg'] for p in parts}
    f=lambda n:any(seg[n].endswith(a) for a in ARM); g=lambda n:any(seg[n].endswith(a) for a in LEG)
    return [x for x in c if (f(x[0]) and g(x[1])) or (f(x[1]) and g(x[0]))]
def pose_for(k,jn,a):
    if (k=='hip_roll' and a<0) or (k=='hip_yaw' and a<0): return {'L_'+k:a,'R_'+k:a}   # adduction / inward yaw: pelvis shift or turning step (v3 rule)
    return {jn:a}
def test(k,jn,a,r):
    pose=pose_for(k,jn,a); parts=M.build(pose); c=clashes(parts,moved=lambda p:any(j in p['deps'] for j in pose))
    al=armleg(c,parts); c=[x for x in c if x not in al]
    if al: r['arm_leg'].append(dict(angle=a,pairs=al[:4]))
    return c
def sweep(joints,st=15):
    res={}
    for k in joints:
        jn=jname(k); r=dict(limit=LIM[k],free=[0,0],clashes=[],arm_leg=[])
        for side,lim in ((0,LIM[k][0]),(1,LIM[k][1])):
            free=0; d=1 if lim>0 else -1
            for a in (steps(lim,st) if lim else []):
                c=test(k,jn,a,r)
                if c:
                    hit=(a,c)
                    for b in range(int(free)+5*d,int(a),5*d):
                        cb=test(k,jn,b,r)
                        if cb: hit=(b,cb); break
                        free=b
                    r['clashes'].append(dict(angle=hit[0],pairs=hit[1])); break
                free=a
            r['free'][side]=free
        r['full_range_clear']=(r['free'][0]==LIM[k][0] and r['free'][1]==LIM[k][1])
        print(k,r['free'],LIM[k],[ (c['angle'],c['pairs'][:3]) for c in r['clashes']],flush=True); res[k]=r
    return res
if __name__=='__main__':
    os.makedirs(os.path.join(M.HERE,'out'),exist_ok=True); args=[a for a in sys.argv[1:] if not a.startswith('--')]
    t=time.time(); parts=M.build(); out={}
    c=clashes(parts); f=floating(parts); out['standing']=dict(clashes=c,floating=f)
    print('standing clashes',len(c)); [print('  ',x) for x in c]; print('floating',len(f)); [print('  ',x) for x in f]
    if '--stand' not in sys.argv:
        out['sweep']=sweep(args or list(LIM))
        combo={}
        for lbl,pose in (('sit hip-90 knee120',{'L_hip_pitch':-90,'L_knee':120}),('deep squat hip-100 knee135',{'L_hip_pitch':-100,'L_knee':135}),('stance ankle -45 + roll 18',{'L_ankle_pitch':-45,'L_ankle_roll':18}),('ankle +40 roll -18',{'L_ankle_pitch':40,'L_ankle_roll':-18})):
            combo[lbl]=clashes(M.build(pose)); print(lbl,combo[lbl],flush=True)
        out['combos']=combo
    json.dump(out,open(os.path.join(M.HERE,'out','clash_v4.json' if '--stand' not in sys.argv else 'clash_v4_stand.json'),'w'),indent=1); print('t',round(time.time()-t))
