"""A38 L2b: grown tine (lug end R20 about the clamp-eye pin, i.e. e=20 all round = worst-case envelope) vs the hip screw unit
(body, eye stub/flange [EST], rod) and other thigh/hip parts over hip_pitch -107.3..+40. Light."""
import os,sys,json,math; HERE=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,os.path.join(HERE,'../model'))
import cadquery as cq, model_v4 as M
res={}
for th in (-107.3,-90,-60,-30,0,20,40):
    parts=M.build({'L_hip_pitch':th}); out=[]
    pins=[p for p in parts if p['name'].startswith('L_clamp eye pin')]
    for pin in pins:
        b=pin['solid'].BoundingBox(); c=((b.xmin+b.xmax)/2,(b.ymin+b.ymax)/2,(b.zmin+b.zmax)/2); sy=1 if c[1]>130 else -1
        for k in (-1,1):
            yc=c[1]+k*10; env=cq.Workplane('XZ').circle(20).circle(10).extrude(4,both=True).translate((c[0],yc,c[2])).val()
            for p in parts:
                n=p['name']
                if not n.startswith('L_') or 'tine' in n or 'clamp eye pin' in n or 'GE12' in n or 'clamp arm' in n: continue
                q=p['solid'].BoundingBox()
                if q.xmin>c[0]+40 or q.xmax<c[0]-40 or q.zmin>c[2]+40 or q.zmax<c[2]-40 or q.ymin>yc+30 or q.ymax<yc-30: continue
                d=env.distance(p['solid']) if hasattr(env,'distance') else None
                d=cq.Compound.makeCompound([env]).distance(cq.Compound.makeCompound([p['solid']]))
                out.append((round(float(d),2),f"{'+' if sy>0 else '-'}y {'o' if k*sy>0 else 'i'}",n))
    out.sort(); res[th]=out[:6]; print(th,out[:4],flush=True)
json.dump(res,open(f'{HERE}/results/a38/tine_clear_a38.json','w'),indent=1)
