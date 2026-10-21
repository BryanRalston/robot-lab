"""P-052 rev 2 chest pad + bezel STEP for Arms R18 G2 sweep. GLOBAL frame (torso frame + z 1280, waist joints zero), mm, x fwd y left z up.
Light: simple B-rep solids (boxes/lofts/cylinders), no meshes. Land thickness 6 mm (x 52-58) is [EST]; Torso owns the land."""
import cadquery as cq, os, json
H=os.path.dirname(os.path.abspath(__file__)); ZC=1500.0
def yz(x0,dx,w,h): return cq.Workplane("YZ").workplane(offset=x0).center(0,ZC).rect(w,h).extrude(dx)
core=yz(58,116,98,98); face=yz(174,1,98,98); land=yz(52,6,101,101)
def frustum(fw,bw,x_back=110.0,x_front=173.0):
    return (cq.Workplane("YZ").workplane(offset=x_back).center(0,ZC).rect(bw,bw)
            .workplane(offset=x_front-x_back).rect(fw,fw).loft(combine=True))
outer=frustum(100,150)
fe=outer.faces(">X").edges().vals()+outer.faces("<X").edges().vals()
side=[e for e in outer.edges().vals() if not any(e.isSame(f) for f in fe)]
outer=outer.newObject(side).chamfer(4)
outer=outer.faces(">X").edges().fillet(6)
bezel=outer.cut(frustum(98,148,109.0,174.0))
posts=None
for y in (-63,63):
    for z in (ZC-63,ZC+63):
        c=cq.Workplane("YZ").workplane(offset=110).center(y,z).circle(4).circle(2.25).extrude(63)
        posts=c if posts is None else posts.union(c)
asm=cq.Assembly()
for n,s in (("pad_core_116",core),("pad_face_CF",face),("land",land),("bezel_fairing_P052r2",bezel),("crush_posts_x4",posts)): asm.add(s,name=n)
asm.save(os.path.join(H,"chest_pad_bezel_r2.step"))
bb=cq.Compound.makeCompound([s.val() for s in (core,face,land,bezel,posts)]).BoundingBox()
out=dict(frame="global",bbox=[[round(bb.xmin,1),round(bb.ymin,1),round(bb.zmin,1)],[round(bb.xmax,1),round(bb.ymax,1),round(bb.zmax,1)]])
json.dump(out,open(os.path.join(H,"chest_pad_bezel_r2.json"),"w"),indent=1); print(out)
