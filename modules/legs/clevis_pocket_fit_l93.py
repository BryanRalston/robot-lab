"""L93 quick fit: PU stack in a knee-clevis-bridge pocket, struck by the tibia tongue-neck block, contact 130 deg, r50-60, stack 44-56 mm.
Stack modelled as a 28 (y) x 24 (w) prism from the neck face point at r55 (130 deg) along the arc tangent toward the bridge. Reports stack length
available to the bridge rear face, intersections (mm^3) with every other part at knee 0..145, free volume."""
import os,sys,json,math
HERE=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,os.path.join(HERE,'../model'))
import cadquery as cq, model_v4 as M
_st=M.step; M.step=lambda n,*a,**k: _st('knee_twin_housing_release_r116b' if n=='knee_twin_housing' else n,*a,**k)
kz=M.P['knee_z']; y0=130
out={}
for r in (50,55,60):
  th=math.radians(130); p=(-r*math.sin(th)-8*math.cos(th)*0, kz+(-r*math.cos(th)))   # point on the shank axis at r (shank axis x~10 offset ignored)
  t=(math.cos(th)*-1*-1, math.sin(th))  # tangent toward +flexion travel reversed (toward thigh): (-cos, sin) rotated
  ut=(-math.cos(th),math.sin(th)); ut=(-ut[0],-ut[1]) if ut[0]<0 else ut
  for L in (44,50,56):
    c=(p[0]+ut[0]*L/2, p[1]+ut[1]*L/2); ang=math.degrees(math.atan2(ut[1],ut[0]))
    s=cq.Workplane('XY').box(L,28,24).val().rotate(cq.Vector(0,0,0),cq.Vector(0,1,0),-ang).translate(cq.Vector(c[0],y0,c[1]))
    hits={}
    for k in (0,60,120,130,143.6):
      for q in M.build({'L_knee':k}):
        if not q['name'].startswith('L_'): continue
        b=q['solid'].BoundingBox(); sb=s.BoundingBox()
        if b.xmin>sb.xmax or b.xmax<sb.xmin or b.zmin>sb.zmax or b.zmax<sb.zmin or b.ymin>sb.ymax or b.ymax<sb.ymin: continue
        try: v=s.intersect(q['solid']).Volume()
        except Exception: v=-1
        if abs(v)>1: hits[q['name'][:40]]=max(hits.get(q['name'][:40],0),round(v))
    tot=sum(v for k_,v in hits.items() if 'clevis bridge' not in k_ and 'tongue' not in k_)
    out[f'r{r}_L{L}']=dict(start=[round(p[0],1),round(p[1],1)],dir=[round(ut[0],3),round(ut[1],3)],stack_mm3=round(s.Volume()),hits=hits,
        clash_mm3_excl_bridge_neck=tot,free_mm3=round(s.Volume()-tot))
    print(r,L,out[f'r{r}_L{L}'],flush=True)
json.dump(out,open(f'{HERE}/results/r031/clevis_pocket_fit_l93.json','w'),indent=1)
