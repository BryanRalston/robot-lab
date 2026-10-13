"""Round 3b: hip_pitch lever, thigh-mounted config B (Legs L10), CPU FEA (CadQuery -> gmsh -> scikit-fem P2 tets, pyamg CG).
Topology (new, replaces lever(r,dy) crossbar+outboard cheeks): lever is the pelvis-side link. Central hub = hollow spigot ø50/ø40 that carries the
inner ring of one IKO CRBH 5013 A (outer ring in the femur upper lug, tongue width 25), flanged by two cheeks ø62 (|y| 12.5..22) whose outer faces
bolt to the hip-roll output yoke. Two tapered arms run from the cheeks to rod-end ears at (x 0, y ±69, z -50) (lever r 50, screw half-spacing 69).
Ear ø26 x 12 (y 50..62) with a pressed ø12 steel pin stub (single shear, y 62..75) carrying the RV12 rod-end eye.
Nothing of the pivot lies in the screw planes |y| >= 63 -> boss-clearance becomes lateral (see hp_clearance.py).
Loads: per screw F = T_out/r/2 = 454.2/0.050/2 = 4542 N (both motors at peak), direction in the lever frame at angle phi from tangential
(phi = acos(arm/r): loaded ROM -80..+40 -> |phi| <= 60.4 deg; deep flexion through toggle -> 90 deg), both signs; fault case: one screw at 4542 N, other 0.
Supports: bearing seat (r 25, |y|<=6.5) and cheek bolt faces (|y| = 22) fixed (rigid bearing + yoke) -> stresses at supports excluded from the check
(evaluated in arms/ears |y| in [24, 62]; pin stub is steel, hand-checked). 7075-T6 plate: E 71.7 GPa, nu 0.33, Sy 503 MPa, Su 572 MPa (MMPDS),
fatigue 159 MPa @ 5e8 (R=-1 unnotched) x 0.8 surface/size = 127 MPa.
Usage: python3 hp_lever_fea.py [b d0 d1 fr h] [--export]  (x-depth b, arm yz-width root d0 / tip d1, profile fillet fr, mesh h); writes results/hp_lever_fea*.json, cad/'+os.environ.get('STEPNAME','hip_pitch_lever_B')+'.step"""
import cadquery as cq, numpy as np, json, os, sys, gmsh, meshio
from skfem import MeshTet, ElementTetP2, ElementVector, Basis, FacetBasis, asm, condense
from skfem.models.elasticity import linear_elasticity, lame_parameters
from skfem.helpers import dot
import pyamg
H=os.path.dirname(os.path.abspath(__file__))
E,NU,RHO,SY,SU,SE=71.7e3,0.33,2.81e-6,503.,572.,159*0.8   # MPa, kg/mm3
F=454.2/0.050/2; DY=69.0; R=50.0; FR=float(os.environ.get('FR','2.0')); FILLET_OK=None
def geom4(b=26,d0=24,d1=16,fr=0):
    """round hub (|y|<=22, ø56, bore ø40, bearing groove r25 |y|<12.5 with r0.6 shoulders) + 3-section smooth lofted arms + ears + pins"""
    NEEDLE=os.environ.get('HUB','crbh')=='needle'   # R4: needle straddle -> two cheeks ø52 x 20 with TLA 3520 Z outer-ring bores ø42, |y| 13.5..33.5
    RB,HW=(21.0,33.5) if NEEDLE else (20.0,22.0)
    RW0,RW1=[float(x) for x in os.environ.get('ROOT','44,30').split(',')]
    hub=cq.Workplane('XZ').circle(26 if NEEDLE else 28).circle(RB).extrude(HW,both=True)
    if not NEEDLE:
        g=(cq.Workplane('XY').moveTo(25,-12.5).lineTo(31,-12.5).lineTo(31,12.5).lineTo(25,12.5).close().revolve(360,(0,0,0),(0,1,0)))
        hub=hub.cut(g)
    s=hub
    for sg in (1,-1):
        pts=[(np.array([0,sg*17.0,-12.0]),RW0,RW1),(np.array([0,sg*30.0,-26.0]),b,d0),(np.array([0,sg*54.0,-48.0]),b*0.85,d1)]
        def rect(c,bb,dd,ax):
            n=np.cross(ax,[1,0,0]); n/=np.linalg.norm(n)
            return cq.Wire.makePolygon([cq.Vector(*(c+u*bb/2*np.array([1,0,0])+v*dd/2*n)) for u,v in ((1,1),(-1,1),(-1,-1),(1,-1))],close=True)
        ax=(pts[2][0]-pts[0][0]); ax/=np.linalg.norm(ax)
        arm=cq.Workplane().add(cq.Solid.makeLoft([rect(c,bb,dd,ax) for c,bb,dd in pts],False))
        ear=(cq.Workplane('XZ').center(0,-50).circle(13).extrude(-12).translate((0,50,0)) if sg>0 else cq.Workplane('XZ').center(0,-50).circle(13).extrude(12).translate((0,-50,0)))
        pin=(cq.Workplane('XZ').center(0,-50).circle(6).extrude(-25).translate((0,50,0)) if sg>0 else cq.Workplane('XZ').center(0,-50).circle(6).extrude(25).translate((0,-50,0)))
        arm=arm.cut(cq.Workplane('XZ').circle(RB).extrude(HW,both=True))
        s=s.union(arm).union(ear).union(pin)
    s=s.cut(cq.Workplane('XZ').circle(RB).extrude(HW,both=True))
    if NEEDLE: s=s.cut(cq.Workplane('XY').box(200,27,200))   # femur tongue + shaft between the cheeks: no lever material at |y|<13.5 (two halves joined by the hip-roll yoke)
    s=s.cut(cq.Workplane('XY').moveTo(25,-13.5).lineTo(120,-13.5).lineTo(120,13.5).lineTo(25,13.5).close().revolve(360,(0,0,0),(0,1,0)))   # femur-tongue sweep space |y|<13.5, r>25
    s=s.cut(cq.Workplane('XY').box(200,200,200).translate((0,0,0)).cut(cq.Workplane('XZ').circle(200).extrude(75,both=True)))
    es=[e for e in s.edges().vals() if 21.5<abs(e.Center().y)<23 and e.Center().z<-0.5 and abs(e.Center().x)<25 and (e.geomType()=='BSPLINE' or (e.geomType()=='CIRCLE' and e.Length()<20))]
    geom4.fillet='none'
    for r in (2.0,1.5):   # arm-flank / hub-face junction fillets (re-entrant edges); the two straight root edges stay sharp (OCC fails) -> drawing R2 all round
        try:
            t=s.newObject(es).fillet(r)
            if t.val().isValid() and len(t.solids().vals())==1: s=t; geom4.fillet=f'R{r} on {len(es)} junction edges'; break
        except Exception: pass
    assert len(s.solids().vals())==(2 if NEEDLE else 1), [x.Volume() for x in s.solids().vals()]
    return s
def lever_only_mass(s):   # steel pins ø12 x 25 (through ear + rod-end stub) excluded from the 7075 volume
    vp=2*np.pi*6**2*25; V=sum(x.Volume() for x in s.solids().vals()); return (V-vp)*RHO, vp*7.85e-6
def mesh(s,h,fn):
    cq.exporters.export(s,fn+'.step'); gmsh.initialize(); gmsh.option.setNumber('General.Terminal',0)
    gmsh.model.occ.importShapes(fn+'.step'); gmsh.model.occ.synchronize()
    gmsh.option.setNumber('Mesh.MeshSizeMax',h); gmsh.option.setNumber('Mesh.MeshSizeMin',h/3); gmsh.option.setNumber('Mesh.MeshSizeFromCurvature',int(os.environ.get('NCURV','6')))
    gmsh.model.mesh.generate(3); gmsh.write(fn+'.msh'); gmsh.finalize()
    m=meshio.read(fn+'.msh'); t=m.cells_dict['tetra']; return MeshTet(m.points.T.copy(),t.T.copy())
def solve(m):
    e=ElementVector(ElementTetP2()); ib=Basis(m,e,intorder=2)
    lam,mu=lame_parameters(E,NU); K=asm(linear_elasticity(lam,mu),ib)
    def isfix(x):
        r=np.hypot(x[0],x[2]); rb,hw=(21.0,33.51) if os.environ.get('HUB','crbh')=='needle' else (20.0,22.01); return (np.abs(r-rb)<0.3)&(np.abs(x[1])<=hw)   # bore clamped on rigid pelvis-side shaft (torque + force)
    fb_fix=m.facets_satisfying(lambda x:isfix(x),boundaries_only=True)
    D=ib.get_dofs(fb_fix).all()
    loads={}
    for sg in (1,-1):
        fac=m.facets_satisfying(lambda x:(sg*x[1]>62.5)&(np.hypot(x[0],x[2]+50)>5.7),boundaries_only=True)
        fbs=FacetBasis(m,e,facets=fac); area=asm(__import__('skfem').LinearForm(lambda v,w:v[0]),fbs).sum()   # sum of x-traction-unit loads = facet area
        for comp,vec in (('t',[1,0,0]),('r',[0,0,-1])):    # tangential (x), radial outward (-z, along lever radius away from pivot)
            vv=np.array(vec,float)*F/area
            f=asm(__import__('skfem').LinearForm(lambda v,w:v[0]*vv[0]+v[1]*vv[1]+v[2]*vv[2]),fbs)
            loads[(sg,comp)]=f
    I=ib.complement_dofs(D); Kc=K[I][:,I].tocsr(); del K; A=pyamg.smoothed_aggregation_solver(Kc,max_coarse=500,keep=False,improve_candidates=None,smooth=("jacobi",{})); nd=Kc.shape[0]+len(D)
    U={}
    for k,f in loads.items():
        u=np.zeros(nd); res=[]; u[I]=A.solve(f[I],tol=1e-8,accel='cg',maxiter=3000,residuals=res); U[k]=u; print('cg',k,len(res),res[-1]/res[0],flush=True)
    return ib,U
def vm_elem(ib,u):
    lam,mu=lame_parameters(E,NU); g=ib.interpolate(u).grad   # (3,3,nel,nqp)
    eps=0.5*(g+g.transpose(1,0,2,3)); tr=eps[0,0]+eps[1,1]+eps[2,2]
    s=2*mu*eps; 
    for i in range(3): s[i,i]+=lam*tr
    vm=np.sqrt(0.5*((s[0,0]-s[1,1])**2+(s[1,1]-s[2,2])**2+(s[2,2]-s[0,0])**2)+3*(s[0,1]**2+s[1,2]**2+s[0,2]**2))
    return vm.max(1)
def run(b=26,d0=24,d1=16,fr=4,h=3.0,tag='',export=False):
    s=geom4(b,d0,d1,fr); fn=f'/tmp/hplever{tag}'; m=mesh(s,h,fn); ib,U=solve(m)
    c=m.p[:,m.t].mean(1); ay=np.abs(c[1]); ev=(ay>24)&(ay<62)&~((ay>60.5)&(np.hypot(c[0],c[2]+50)<8))&~((ay<=34)&(np.hypot(c[0],c[2])<23.5))
    cases={}
    for ph in (-90,-60,-30,0,30,60,90):
        ct,sr=np.cos(np.radians(ph)),np.sin(np.radians(ph))
        u=sum(U[(sg,'t')]*ct+U[(sg,'r')]*sr for sg in (1,-1)); cases[f'sym_phi{ph:+d}']=(u,1.0)
        u=U[(1,'t')]*ct+U[(1,'r')]*sr; cases[f'fault_phi{ph:+d}']=(u,1.0)
    out={}; worst=None
    for k,(u,_) in cases.items():
        vm=vm_elem(ib,u); smax=float(vm[ev].max()); s999=float(np.percentile(vm[ev],99.9)); hub=float(vm[(ay<24)&(np.hypot(c[0],c[2])>21.5)].max()); hub995=float(np.percentile(vm[(ay<24)&(np.hypot(c[0],c[2])>21.5)],99.5))
        pinx=ib.doflocs; sel=np.where(np.abs(np.abs(pinx[1])-69)<0.6)[0]
        dmax=float(np.abs(u[sel]).max())
        iw=np.where(ev)[0][np.argmax(vm[ev])]; out[k]=dict(at=[round(float(x),1) for x in c[:,iw]],vm_max_MPa=smax,vm_p999_MPa=s999,hub_max_MPa=hub,hub_p995_MPa=hub995,SF_yield=SY/smax,pin_disp_mm=dmax)
        if k.startswith('sym') and (worst is None or smax>out[worst]['vm_max_MPa']): worst=k; wvm=vm
    mal,mst=lever_only_mass(s)
    res=dict(params=dict(b=b,d0=d0,d1=d1,fillet=fr,h=h,topology='round hub + smooth 3-section loft arms',junction_fillet=geom4.fillet),nodes=int(m.p.shape[1]),tets=int(m.t.shape[1]),mass_7075_kg=mal,mass_pins_steel_kg=mst,mass_kg=mal+mst,
             cases=out,worst_sym=worst,SF_sym=SY/out[worst]['vm_max_MPa'],SF_fault=SY/max(v['vm_max_MPa'] for k,v in out.items() if k.startswith('fault')))
    if export:
        cq.exporters.export(s,f'{H}/cad/'+os.environ.get('STEPNAME','hip_pitch_lever_B')+'.step')
        np.savez_compressed(f'{H}/results/hp_lever_fea_field.npz',p=m.p,t=m.t,vm=wvm,case=worst)
    return res
if __name__=='__main__':
    a=[float(x) for x in sys.argv[1:6] if not x.startswith('--')] or [26,24,16,4,3.0]
    r=run(*a,export='--export' in sys.argv); print(json.dumps({k:v for k,v in r.items() if k!='cases'},indent=1))
    for k,v in r['cases'].items(): print(k,{a:(round(b,2) if isinstance(b,float) else b) for a,b in v.items()})
    json.dump(r,open(f'{H}/results/hp_lever_fea_last.json','w'),indent=1)
