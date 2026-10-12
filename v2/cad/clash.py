"""Interference check at standing pose and at hip/knee/ankle range extremes (left leg; right is mirror). Writes out/clash.json"""
import itertools,sys,json
import model
LIM_V2_0={'hip_pitch':(-150,40),'hip_roll':(-30,90),'knee':(0,150),'ankle_pitch':(-45,40),'ankle_roll':(-25,25),'hip_yaw':(-45,45)}  # sim limits before CAD
# FIX: hard-stop limits after CAD clash checks (each still covers the functional need: walk, stairs, 110° squat, sitting)
LIM={'hip_pitch':(-105,40),'hip_roll':(-12,20),'knee':(0,120),'ankle_pitch':(-45,40),'ankle_roll':(-25,25),'hip_yaw':(-35,45)}
import sys as _s
if '--v20' in _s.argv: LIM=LIM_V2_0
# intended mates: pinned/bolted interfaces that touch or pass through by design
MATES=[('trunnion stub','body'),
       ('rod-end','lever'),('knee tongue','tibia tube'),('rod-end','knee tongue'),('rod-end','foot plate'),('rod-end','screw rod'),('screw rod','body'),
       ('hip bracket','hip yaw housing'),('ankle cross','ankle fork'),('ankle cross','F/T'),('top spherical bearing','body')]
def mate(a,b): return any((x in a and y in b) or (x in b and y in a) for x,y in MATES)
def run(pose,label):
    model.PARTS.clear();model.CHAINS.clear();model.POSE.clear();model.POSE.update(pose)
    model.build_leg(1);model.build_leg(-1);model.build_upper()
    P=model.PARTS;vals=[p['solid'].val() for p in P];bb=[v.BoundingBox() for v in vals]
    res=[]
    for i,j in itertools.combinations(range(len(P)),2):
        a,b=bb[i],bb[j]
        if a.xmax<b.xmin or b.xmax<a.xmin or a.ymax<b.ymin or b.ymax<a.ymin or a.zmax<b.zmin or b.zmax<a.zmin: continue
        if mate(P[i]['name'],P[j]['name']): continue
        try: v=vals[i].intersect(vals[j]).Volume()
        except Exception: v=-1
        if v>1.0: res.append((P[i]['name'],P[j]['name'],round(v)))
    print(f'== {label}: {len(res)} clashes',flush=True);[print('   ',r,flush=True) for r in res]
    return res
if __name__=='__main__':
    only=[a for a in sys.argv[1:] if not a.startswith('--')]
    poses=[({},'standing')]
    for jn,(lo,hi) in LIM.items():
        for v in (lo,hi):
            if jn=='hip_roll' and v<0:   # adduction only happens with the pelvis shifted over the stance foot: both hips roll together
                poses.append(({'L_hip_roll':v,'R_hip_roll':v},f'L+R_hip_roll={v} (pelvis shift)'))
            elif jn=='hip_yaw' and v<0:   # inward toe yaw: other foot turned the same way (turning step), not toe-to-toe
                poses.append(({'L_hip_yaw':v,'R_hip_yaw':v},f'L+R_hip_yaw={v} (turn)'))
            else: poses.append(({f'L_{jn}':v},f'L_{jn}={v}'))
    poses.append(({'L_hip_pitch':-90,'L_knee':120},'L hip -90 + knee 120 (sit)'))
    if only: poses=[p for p in poses if p[1] in only]
    out={l:run(p,l) for p,l in poses}
    json.dump(out,open('out/clash.json','w'),indent=1)
    print('TOTAL clashes:',sum(len(v) for v in out.values()))
