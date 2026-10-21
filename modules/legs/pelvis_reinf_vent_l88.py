"""L88: Torso 9700df9 pelvis internal reinforcement (lip 20x8, ribs 8 mm at y +-(57..65) deck-top->pelvis-top, ring r55-66 at the waist-yaw seat)
vs leg-side parts (hip-yaw drives/housings, L39/L80 bumpers, HP1/HP2) over hip yaw +-45 (covers L-35..+40 / R-40..+35, mirrored) x pitch -105/0/+40
x roll -14.5/0/+17.5, 3 mm; plus the vent plume box (x -157..-107, |y|<=50, z 1340..1440, 50 mm downstream [EST]) with waist motions."""
import os,sys,json,itertools
HERE=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,os.path.join(HERE,'../model'))
import cadquery as cq, model_v4 as M
P=M.P; pt=P['pelvis_top']
def bx(x0,x1,y0,y1,z0,z1): return M.box(x1-x0,y1-y0,z1-z0,c=((x0+x1)/2,(y0+y1)/2,(z0+z1)/2))
p0=M.build({}); dk=[p for p in p0 if p['name'].startswith('hip yaw + waist mount deck')][0]['solid'].BoundingBox(); dt=dk.zmax
X0,X1,Y0,Y1=dk.xmin,dk.xmax,dk.ymin,dk.ymax
R=[bx(X0,X1,-65,-57,dt,pt),bx(X0,X1,57,65,dt,pt),cq.Workplane('XY').circle(66).circle(55).extrude(pt-dt).translate((0,0,dt)).val(),
   bx(X0,X1,Y0,Y1,pt-8,pt).cut(bx(X0+20,X1-20,Y0+20,Y1-20,pt-8,pt))]
plume=bx(-157,-107,-50,50,1340,1440)
key=lambda n: any(k in n.lower() for k in ('hip_yaw','hip yaw','elmo','bumper','hp1','hp2','drive plate','hip_roll','hip roll','harness','cable'))
res=[];pl=[];zmax=0
poses=[{'L_hip_yaw':yw,'R_hip_yaw':-yw,'L_hip_pitch':pi,'R_hip_pitch':pi,'L_hip_roll':ro,'R_hip_roll':-ro} for yw,pi,ro in itertools.product((-45,0,45),(-105,0,40),(-14.5,0,17.5))]
poses+=[{'waist_yaw':w,'waist_pitch':q} for w,q in ((45,30),(-45,-20),(0,40))]
for pz in poses:
    for p in M.build(pz):
        if p['seg'] in ('torso','waistY') or p['name'].startswith('hip yaw + waist mount deck'): continue
        if p['seg']=='pelvis' and not key(p['name']): continue
        b=p['solid'].BoundingBox(); zmax=max(zmax,b.zmax) if not p['seg'].startswith(('pelvis',)) or key(p['name']) else zmax
        if b.zmax>dt-60:
            for i,r in enumerate(R): res.append((round(float(r.distance(p['solid'])),1),['rib-y','rib+y','ring','lip'][i],p['name'],str(pz)))
        if b.zmax>1290: pl.append((round(float(plume.distance(p['solid'])),1),p['name'],str(pz)))
res.sort(); pl.sort()
out=dict(deck_top=round(dt,1),pelvis_top=pt,reinf_min=res[:8],plume_hits=pl[:5],max_leg_side_part_z=round(zmax,1))
json.dump(out,open(f'{HERE}/results/r031/pelvis_reinf_vent_l88.json','w'),indent=1); print(json.dumps(out))
