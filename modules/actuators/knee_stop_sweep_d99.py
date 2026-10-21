"""D99 (contact 130, 83 mm stacks) from the D98 placement sweep (Legs L78 method, model_v4 + r116b housing): r75 PU stop, contact 135 deg (rev B), 2 stacks outboard of the
knee screws (y 32-60 / 200-228, L leg y0=130). Pad stacks + seat bracket + collar bar thigh-fixed; strikers = 7075 lugs + arms on the
tibia (shank-fixed). Candidates differ by the striker face offset t0 (mm, tangential from the 133-deg plane through the knee axis).
Gate 3 mm vs every non-mount part over knee 0..145 (fault crush to 145) + ankle/hip poses; pad<->own striker gated only for knee <=131 (contact at 133)."""
import os,sys,json,math
HERE=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,os.path.join(HERE,'../model'))
import cadquery as cq, model_v4 as M
_st=M.step; M.step=lambda n,*a,**k: _st('knee_twin_housing_release_r116b' if n=='knee_twin_housing' else n,*a,**k)
kz=M.P['knee_z']; Y0=130; C=130.0; R=75.0; HS=7*10.17+6*1.0+2*3; YS=(46,214)
th=math.radians(C); ur=(-math.sin(th),-math.cos(th)); ut=(-math.cos(th),math.sin(th))
def rtbox(r0,r1,t0,t1,y0,y1):
    """box spanning radial r0..r1, tangential t0..t1 (133-deg frame), y0..y1"""
    b=cq.Workplane('XY').box(t1-t0,y1-y0,r1-r0).val()          # local x=t, z=r
    ang=math.degrees(math.atan2(-ut[1],ut[0]))                    # rotate local x->ut in xz
    b=b.rotate(cq.Vector(0,0,0),cq.Vector(0,1,0),ang)
    rc,tc=(r0+r1)/2,(t0+t1)/2
    return b.translate(cq.Vector(rc*ur[0]+tc*ut[0],(y0+y1)/2,kz+rc*ur[1]+tc*ut[1]))
def parts(t0):
    pad=[];seat=[];strk=[]
    for yc in YS:
        pad.append(rtbox(R-10,R+10,t0,t0+HS,yc-12,yc+12))
        seat.append(rtbox(R-15,R+15,t0+HS,t0+HS+8,yc-18,yc+18))
        strk.append(rtbox(R-11,R+11,t0-10,t0,yc-16,yc+16))
        yi,yo=(yc+16,Y0-21) if yc<Y0 else (Y0+21,yc-16)
        strk.append(rtbox(R-12,R+12,t0-16,t0-4,yi,yo))
    # collar bar: from both seats to the femur collar (x~-8,z~600), at the seat back level, through y 28..232
    seat.append(rtbox(R-15,R+15,t0+HS+8,t0+HS+18,28,232))
    u=lambda L:L[0] if len(L)==1 else cq.Workplane('XY').add(L[0]).union(cq.Workplane('XY').add(L[1:])).val()
    s=strk[0]
    for x in strk[1:]: s=s.fuse(x)
    s=s.rotate(cq.Vector(0,kz*0,0),cq.Vector(0,1,0),0)
    return pad,seat,s
T0S=[float(a) for a in os.environ.get('T0S','-4,-20,10').split(',')]
_bl=M.build_leg
def bl(sgn):
    _bl(sgn)
    if sgn>0:
        for t0 in T0S:
            pad,seat,s=parts(t0); tag=f'{t0:+.0f}'
            for i,p in enumerate(pad): M.add(f'X_pad{i}_{tag}','L_thigh',p,asm=f'Xp{i}{tag}')
            for i,p in enumerate(seat): M.add(f'X_seat{i}_{tag}','L_thigh',p,asm=f'Xs{i}{tag}')
            # striker built at q=C -> shank frame q=0: rotate by -C about the knee axis
            s0=s.translate(cq.Vector(0,0,-kz)).rotate(cq.Vector(0,0,0),cq.Vector(0,1,0),-C*SG).translate(cq.Vector(0,0,kz))
            M.add(f'X_strk_{tag}','L_shank',s0,asm=f'Xk{tag}')
M.build_leg=bl
SG=float(os.environ.get('SG','1'))
if os.environ.get('CHECK'):
    ps=M.build({'L_knee':C}); X={p['name']:p['solid'] for p in ps if p['name'].startswith('X_')}
    for t0 in T0S:
        tag=f'{t0:+.0f}'; print(tag,'pad0-strk',round(X[f'X_pad0_{tag}'].distance(X[f'X_strk_{tag}']),2))
    sys.exit()
P=[{'L_knee':k} for k in (0,20,45,70,90,110,120,124,128,133,138,143.6,145)]+[{'L_knee':145,'L_ankle_pitch':a} for a in (-45,30)]+\
  [{'L_knee':128,'L_ankle_pitch':a} for a in (-45,30)]+[{'L_knee':145,'L_ankle_roll':r} for r in (-18,18)]+\
  [{'L_hip_pitch':-100,'L_knee':145},{'L_hip_pitch':20,'L_knee':145},{'L_hip_roll':-20,'R_hip_roll':-20,'L_knee':145},{'L_hip_yaw':45,'R_hip_yaw':45,'L_knee':90},{'L_hip_roll':-20,'R_hip_roll':-20}]
res={}
for pz in P:
    try: ps=M.build(pz)
    except Exception as e: print('pose fail',pz,e); continue
    X=[p for p in ps if p['name'].startswith('X_')]
    for p in ps:
        if p['name'].startswith('X_') and False: pass
        for v in X:
            tag=v['name'].split('_')[-1]
            if p is v: continue
            if p['name'].startswith('X_'):
                if not p['name'].endswith(tag): continue
                if v['seg']==p['seg']: continue                     # pad/seat/strk same body: integral
                if pz.get('L_knee',0)>128: continue                 # pad<->striker in contact
            elif v['seg']==p['seg'] and 'knee twin housing' not in p['name']:
                if v['name'].startswith('X_seat') or v['name'].startswith('X_strk'): continue   # mounts onto own segment
                if not ('femur tube' in p['name'] or 'collar' in p['name']): pass
            b=p['solid'].BoundingBox(); bb=v['solid'].BoundingBox(); m=12
            if b.xmin>bb.xmax+m or b.xmax<bb.xmin-m or b.ymin>bb.ymax+m or b.ymax<bb.ymin-m or b.zmin>bb.zmax+m or b.zmax<bb.zmin-m: continue
            d=round(float(v['solid'].distance(p['solid'])),1); k=tag+' | '+v['name'].rsplit('_',1)[0]+' | '+p['name'][:60]
            if d<res.get(k,(1e9,))[0]: res[k]=(d,str(pz))
    print('done',pz,flush=True)
rows=sorted([[k,d,pz] for k,(d,pz) in res.items()],key=lambda t:t[1])
out={t:[r for r in rows if r[0].startswith(f'{t:+.0f} ')][:15] for t in T0S}
out={f'{t:+.0f}':v for t,v in out.items()}
json.dump(out,open(f'{HERE}/results/knee_stop_sweep_d99.json','w'),indent=1); print(json.dumps(out,indent=0))
