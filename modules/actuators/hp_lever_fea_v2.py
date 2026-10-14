"""O13b: hip_pitch lever v2 (needle cheeks). Changes vs hp_lever_fea.geom4:
 - analytic geometry: cheek = plain cylinder r RB..RO (RO param, was 26), arms = RULED loft (planar/ruled faces, no B-spline cheek),
   junction fillet RJ (>=5) on the arm/cheek-face edges at |y|=33.5.
 - supports: NO bore clamp. Bearing reaction applied as cosine-distributed radial pressure on each bore (r 21, |y| 13.5..33.5),
   equal and opposite to the net pin force (half per cheek); pitch torque reacted by the yoke bolt face (cheek inner face |y|=13.5, fixed).
 - mesh: global h, gmsh Ball refinement h_loc at the hot spot(s) (arm root/cheek junction, both sides), P2 tets.
Usage: RO= RJ= D0= H= HLOC= python3 hp_lever_fea_v2.py [--export]"""
import os,sys,json,tempfile,numpy as np
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
os.environ['HUB']='needle'
import hp_lever_fea as L, cadquery as cq, gmsh, meshio, pyamg, skfem
from skfem import MeshTet,ElementTetP2,ElementVector,Basis,FacetBasis,asm,LinearForm
from skfem.models.elasticity import linear_elasticity,lame_parameters
H=L.H; RB,HW,HI=21.0,33.5,13.5
P=dict(RO=float(os.environ.get('RO',30)),RJ=float(os.environ.get('RJ',5)),b=float(os.environ.get('B',25)),d0=float(os.environ.get('D0',28)),d1=float(os.environ.get('D1',15)),
       rw0=float(os.environ.get('RW0',37.5)),rw1=float(os.environ.get('RW1',26)))
def geom():
    """old smooth 3-section loft arms (one clean B-spline loft per arm), cheek r RB..RO, bore pocket ends in a revolved R=RJ relief
    (bore r21 runs RD=RJ past the bearing seat and the bottom corner is a true torus R=RJ: removes the sharp bore-lip re-entrant corner),
    plus junction fillet RJ on the arm/cheek-face edges."""
    RO,RJ=P['RO'],P['RJ']; s=cq.Workplane('XZ').circle(RO).circle(RB).extrude(HW,both=True)
    for sg in (1,-1):
        pts=[(np.array([0,sg*17.0,-12.0]),P['rw0'],P['rw1']),(np.array([0,sg*30.0,-26.0]),P['b'],P['d0']),(np.array([0,sg*54.0,-48.0]),P['b']*0.85,P['d1'])]
        ax=pts[2][0]-pts[0][0]; ax/=np.linalg.norm(ax)
        def rect(c,bb,dd):
            n=np.cross(ax,[1,0,0]); n/=np.linalg.norm(n)
            return cq.Wire.makePolygon([cq.Vector(*(c+u*bb/2*np.array([1,0,0])+v*dd/2*n)) for u,v in ((1,1),(-1,1),(-1,-1),(1,-1))],close=True)
        arm=cq.Workplane().add(cq.Solid.makeLoft([rect(*q) for q in pts],False))
        ear=cq.Workplane('XZ').center(0,-50).circle(13).extrude(-12 if sg>0 else 12).translate((0,sg*50,0))
        pin=cq.Workplane('XZ').center(0,-50).circle(6).extrude(-25 if sg>0 else 25).translate((0,sg*50,0))
        s=s.union(arm).union(ear).union(pin)
    s=s.cut(cq.Workplane('XY').box(200,2*HI,200))
    s=s.cut(cq.Workplane('XY').moveTo(RB+4,-HI).lineTo(120,-HI).lineTo(120,HI).lineTo(RB+4,HI).close().revolve(360,(0,0,0),(0,1,0)))
    s=s.cut(cq.Workplane('XY').box(400,400,400).cut(cq.Workplane('XZ').circle(200).extrude(75,both=True)))
    geom.fillet='none'
    es=[e for e in s.edges().vals() if abs(abs(e.Center().y)-HW)<0.6 and e.geomType()=='BSPLINE' and e.Center().z<-RB+1]
    for r in (RJ,RJ-1,4,3,2.8):
        try:
            t=s.newObject(es).fillet(r)
            if t.val().isValid() and len(t.solids().vals())==2: s=t; geom.fillet=f'R{r:g} on {len(es)} junction edges'; break
        except Exception: pass
    tool=cq.Workplane('XZ').circle(RB).extrude(HW+RJ,both=True).edges('%CIRCLE').fillet(RJ-0.01)
    s=s.cut(tool); geom.fillet+=f' + bore-end relief torus R{RJ:g} (pocket to |y|={HW+RJ:g})'
    assert len(s.solids().vals())==2
    return s
def mesh(s,h,hloc,fn,spots):
    cq.exporters.export(s,fn+'.step'); gmsh.initialize(); gmsh.option.setNumber('General.Terminal',0); gmsh.option.setNumber('General.NumThreads',2)
    gmsh.model.occ.importShapes(fn+'.step'); gmsh.model.occ.synchronize()
    gmsh.option.setNumber('Mesh.MeshSizeMax',h); gmsh.option.setNumber('Mesh.MeshSizeMin',hloc*0.7)
    ids=[]
    for i,c in enumerate(spots,1):
        gmsh.model.mesh.field.add('Ball',i); 
        for k,v in zip(('XCenter','YCenter','ZCenter'),c): gmsh.model.mesh.field.setNumber(i,k,v)
        gmsh.model.mesh.field.setNumber(i,'Radius',7); gmsh.model.mesh.field.setNumber(i,'Thickness',8)
        gmsh.model.mesh.field.setNumber(i,'VIn',hloc); gmsh.model.mesh.field.setNumber(i,'VOut',h); ids.append(i)
    n=len(ids)+1; gmsh.model.mesh.field.add('Min',n); gmsh.model.mesh.field.setNumbers(n,'FieldsList',ids); gmsh.model.mesh.field.setAsBackgroundMesh(n)
    for o in ('MeshSizeExtendFromBoundary','MeshSizeFromPoints','MeshSizeFromCurvature'): gmsh.option.setNumber('Mesh.'+o,0)
    gmsh.model.mesh.generate(3); gmsh.write(fn+'.msh'); gmsh.finalize()
    m=meshio.read(fn+'.msh'); return MeshTet(m.points.T.copy(),m.cells_dict['tetra'].T.copy())
def solve(m):
    e=ElementVector(ElementTetP2()); ib=Basis(m,e,intorder=2); lam,mu=lame_parameters(L.E,L.NU); K=asm(linear_elasticity(lam,mu),ib)
    D=ib.get_dofs(m.facets_satisfying(lambda x:np.abs(np.abs(x[1])-HI)<0.05,boundaries_only=True)).all()
    W=HW-HI; loads={}
    for sg in (1,-1):
        fac=m.facets_satisfying(lambda x:(sg*x[1]>62.5)&(np.hypot(x[0],x[2]+50)>5.7),boundaries_only=True); fbs=FacetBasis(m,e,facets=fac)
        area=asm(LinearForm(lambda v,w:v[0]),fbs).sum()
        for comp,vec in (('t',[1.,0,0]),('r',[0,0,-1.])):
            vv=np.array(vec)*L.F/area; f=asm(LinearForm(lambda v,w:v[0]*vv[0]+v[1]*vv[1]+v[2]*vv[2]),fbs)
            R=-np.array(vec)*L.F; th=np.arctan2(R[2],R[0]); p0=np.linalg.norm(R)/2/(RB*W*np.pi/2)   # half the reaction per cheek bore
            for cs in (1,-1):
                bf=FacetBasis(m,e,facets=m.facets_satisfying(lambda x:(np.abs(np.hypot(x[0],x[2])-RB)<0.2)&(cs*x[1]>HI-0.01)&(cs*x[1]<HW+0.01),boundaries_only=True))
                def lf(v,w):
                    a=np.arctan2(w.x[2],w.x[0]); c=np.maximum(np.cos(a-th),0)*p0
                    return c*(np.cos(a)*v[0]+np.sin(a)*v[2])
                f=f+asm(LinearForm(lf),bf)
            loads[(sg,comp)]=f
    I=ib.complement_dofs(D); Kc=K[I][:,I].tocsr(); del K
    A=pyamg.smoothed_aggregation_solver(Kc,max_coarse=500,smooth=('jacobi',{})); U={}
    for k,f in loads.items():
        u=np.zeros(ib.N); res=[]; u[I]=A.solve(f[I],tol=1e-9,accel='cg',maxiter=6000,residuals=res); U[k]=u
        if res[-1]/res[0]>1e-6: raise RuntimeError(f'CG {k} {res[-1]/res[0]}')
    return ib,U
def cases(U):
    out={}
    for ph in (-90,-60,-30,0,30,60,90):
        ct,sr=np.cos(np.radians(ph)),np.sin(np.radians(ph))
        out[f'sym_phi{ph:+d}']=sum(U[(sg,'t')]*ct+U[(sg,'r')]*sr for sg in (1,-1))
        out[f'fault_phi{ph:+d}']=U[(1,'t')]*ct+U[(1,'r')]*sr
        out[f'faultL_phi{ph:+d}']=U[(-1,'t')]*ct+U[(-1,'r')]*sr
    return out
def stress(ib,u):
    lam,mu=lame_parameters(L.E,L.NU); g=ib.interpolate(u).grad; eps=0.5*(g+g.transpose(1,0,2,3)); tr=eps[0,0]+eps[1,1]+eps[2,2]; s=2*mu*eps
    for i in range(3): s[i,i]+=lam*tr
    vm=np.sqrt(0.5*((s[0,0]-s[1,1])**2+(s[1,1]-s[2,2])**2+(s[2,2]-s[0,0])**2)+3*(s[0,1]**2+s[1,2]**2+s[0,2]**2))
    return vm.max(1),s.mean(3)
def run(h,hloc,spots,export=False):
    s=geom(); fn=os.path.join(tempfile.gettempdir(),'hpv2'); m=mesh(s,h,hloc,fn,spots); ib,U=solve(m)
    c=m.p[:,m.t].mean(1); ay=np.abs(c[1]); rr=np.hypot(c[0],c[2])
    ev=(ay>HI+2.5)&(ay<62)&~((ay>60.5)&(np.hypot(c[0],c[2]+50)<8))      # everything except 2.5 mm at the fixed yoke face and the steel pin stubs
    out={}; fields={}
    for k,u in cases(U).items():
        vm,_=stress(ib,u); i=np.where(ev)[0][np.argmax(vm[ev])]; out[k]=dict(vm_max=float(vm[i]),at=[round(float(x),1) for x in c[:,i]],p999=float(np.percentile(vm[ev],99.9)))
        # peak away from fixed face, inside 10 mm balls at spots (hot-spot measure used for convergence)
        for j,sp in enumerate(spots):
            sel=ev&(np.linalg.norm(c-np.array(sp)[:,None],axis=0)<10)
            out[k][f'spot{j}']=float(vm[sel].max()) if sel.any() else None
        fields[k]=vm
    V=sum(x.Volume() for x in s.solids().vals()); vp=2*np.pi*36*25
    r=dict(params=P,fillet=geom.fillet,h=h,hloc=hloc,nodes=int(m.p.shape[1]),tets=int(m.t.shape[1]),ndof=int(ib.N),mass_7075_kg=(V-vp)*L.RHO,mass_pins_kg=vp*7.85e-6,mass_kg=(V-vp)*L.RHO+vp*7.85e-6,cases=out)
    pin=np.where(np.abs(np.abs(ib.doflocs[1])-69)<0.6)[0]; r['pin_disp_mm']={k:float(np.abs(u[pin]).max()) for k,u in cases(U).items() if k in('sym_phi+60','sym_phi-60','sym_phi+0')}
    w=max((k for k in out if k.startswith('sym')),key=lambda k:out[k]['vm_max']); r['worst']=w
    np.savez_compressed(f'{H}/results/hp_lever_v2_field_h{h}_{hloc}.npz',p=m.p,t=m.t,vm=fields[w],case=w)
    if export: cq.exporters.export(s,f'{H}/cad/hip_pitch_lever_B_v2.step')
    return r
if __name__=='__main__':
    h=float(os.environ.get('H',4)); hl=float(os.environ.get('HLOC',2)); sp=json.loads(os.environ.get('SPOTS','[[-11,-34,-17],[11,34,-17],[11,-34,-17],[-11,34,-17]]'))
    if os.environ.get('GEOMONLY'):
        s=geom(); V=sum(x.Volume() for x in s.solids().vals()); print(geom.fillet,(V-2*np.pi*36*25)*L.RHO+2*np.pi*36*25*7.85e-6, s.val().isValid()); sys.exit()
    r=run(h,hl,sp,'--export' in sys.argv); tag=os.environ.get('TAG',f'h{h}_l{hl}')
    json.dump(r,open(f'{H}/results/hp_lever_v2_{tag}.json','w'),indent=1)
    print(r['fillet'],r['ndof'],round(r['mass_kg'],4),r['worst'])
    for k,v in r['cases'].items(): print(k,round(v['vm_max'],1),v['at'],[round(v[f'spot{j}'] or 0,1) for j in range(len(sp))])
