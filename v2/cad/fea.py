"""Linear-elastic FEA (scikit-fem, quadratic P2 tets meshed by TetGen/meshpy) of femur, tibia and hip bracket
under the worst-case loads used in v2/analysis/checks.py. Units mm, N, MPa. Writes out/fea.json, out/fea.md"""
import sys, json, math, gc, numpy as np, model, cadquery as cq
from meshpy.tet import MeshInfo, build, Options
import skfem as fe
from skfem.models.elasticity import linear_elasticity, lame_parameters
from skfem.helpers import dot
P=model.P; BW=float(sys.argv[2]) if len(sys.argv)>2 else 64.3*9.81
E,NU,SY,SE=71700.,0.33,503.,159.   # 7075-T6 (yield; fatigue ~5e8 cycles, MIL-HDBK-5 typical, as in checks.py)
LAND,WALK=3.0,1.3
def parts(seg_names):
    model.PARTS.clear(); model.build_leg(1)
    sh=[p['solid'] for p in model.PARTS if p['name'].split('_',1)[1] in seg_names]
    s=sh[0]
    for o in sh[1:]: s=s.union(o)
    return s.translate((0,-P['hip_y'],0))
def tetmesh(wp,maxvol,tol=0.3):
    v,t=wp.val().tessellate(tol,0.3)
    mi=MeshInfo(); mi.set_points([(p.x,p.y,p.z) for p in v]); mi.set_facets([list(x) for x in t])
    m=build(mi,options=Options('pq2.0Q'),max_volume=maxvol)
    return fe.MeshTet(np.array(m.points).T,np.array(m.elements).T)
def solve(mesh,fixed,load_sel,Fvec,label,Mx=0.0,mc=1):
    print(label,'tets',mesh.t.shape[1],flush=True)
    if mesh.t.shape[1]>60000: raise SystemExit('mesh too big')
    e=fe.ElementVector(fe.ElementTetP2()); ib=fe.Basis(mesh,e,intorder=2)
    K=fe.asm(linear_elasticity(*lame_parameters(E,NU)),ib)
    fb=fe.FacetBasis(mesh,e,facets=mesh.facets_satisfying(load_sel,boundaries_only=True))
    area=fe.Functional(lambda w:1.0+0*w.x[0]).assemble(fb)
    tr=np.array(Fvec)/area
    yc=fe.Functional(lambda w:w.x[mc]).assemble(fb)/area; Iy=fe.Functional(lambda w:(w.x[mc]-yc)**2).assemble(fb)
    # optional pure moment about x (N*mm) as linearly varying normal (z) traction over the load face
    f=fe.LinearForm(lambda v,w: tr[0]*v[0]+tr[1]*v[1]+(tr[2]+Mx*(w.x[mc]-yc)/Iy)*v[2]).assemble(fb)
    D=ib.get_dofs(fixed).all()
    print(label,'tets',mesh.t.shape[1],'dofs',K.shape[0],'load area %.0f mm2'%area,flush=True)
    u=fe.solve(*fe.condense(K,f,D=D),solver=fe.solver_iter_pcg(rtol=1e-9,maxiter=20000)) if K.shape[0]>20000 else fe.solve(*fe.condense(K,f,D=D))
    # von Mises at element quadrature points
    lam,mu=lame_parameters(E,NU); sb=fe.Basis(mesh,e,intorder=2)
    gu=sb.interpolate(u).grad; eps=0.5*(gu+np.swapaxes(gu,0,1)); tr_=eps[0,0]+eps[1,1]+eps[2,2]
    s=2*mu*eps; [s.__setitem__((i,i),s[i,i]+lam*tr_) for i in range(3)]
    vm=np.sqrt(0.5*((s[0,0]-s[1,1])**2+(s[1,1]-s[2,2])**2+(s[2,2]-s[0,0])**2)+3*(s[0,1]**2+s[1,2]**2+s[0,2]**2))
    vme=vm.max(axis=1)
    # report the 99.5th-percentile element too (single-element peaks at fixtures/load edges are singularities)
    i=np.argmax(vme); c=mesh.p[:,mesh.t[:,i]].mean(axis=1)
    disp=np.abs(u[ib.nodal_dofs]).max()
    return dict(vm_max=float(vme.max()),vm_p995=float(np.percentile(vme,99.5)),at_mm=[round(x,1) for x in c],max_disp_mm=float(disp),tets=int(mesh.t.shape[1]),dofs=int(K.shape[0]))
def case(name):
    kz,az,hz=P['knee_z'],P['ankle_z'],P['hip_z']
    if name=='femur':
        # critical region: hip-end lug + 150 mm of tube (bending moment is largest at the fixed hip end).
        # Cut-face loads = resultant of 3BW axial at the knee pin plus lateral H with H*L = 3BW*0.12 m (checks.py lever)
        wp=parts(['femur tube 7075 Ø50x2.0','femur upper lug']); bb=wp.val().BoundingBox(); zc=bb.zmax-180
        wp=wp.intersect(cq.Workplane('XY').box(400,400,400).translate((0,0,zc+200)))
        F=LAND*BW; Mroot=F*0.12*1000; L=bb.zmax-kz; H=Mroot/L; Mcut=H*(zc-kz)
        m=tetmesh(wp,200.,tol=0.8)
        return m,(lambda x: x[2]>bb.zmax-0.5),(lambda x: x[2]<zc+0.3),(H,0,F),dict(F_axial=F,H_lateral=round(H,1),M_root_Nm=round(Mroot/1000,1),region='hip-end lug + 150 mm tube',Mx=Mcut,mc=0)
    if name=='tibia':
        # critical region: ankle fork + 150 mm of tube (moment largest at the fixed ankle end); 3BW + lateral H with H*L = 3BW*0.10 m
        wp=parts(['tibia tube 7075 Ø45x2.0','ankle fork (shank)']); bb=wp.val().BoundingBox(); zc=az+52+150
        wp=wp.intersect(cq.Workplane('XY').box(400,400,400).translate((0,0,zc-200)))
        F=LAND*BW; Mroot=F*0.10*1000; L=kz-(az+15); H=Mroot/L; Mcut=H*(kz-zc)
        m=tetmesh(wp,200.,tol=0.8)
        return m,(lambda x: x[2]<bb.zmin+0.5),(lambda x: x[2]>zc-0.3),(H,0,-F),dict(F_axial=F,H_lateral=round(H,1),M_root_Nm=round(Mroot/1000,1),region='ankle fork + 150 mm tube',Mx=-Mcut,mc=0)
    if name=='hip bracket':
        wp=model.hip_bracket(); bb=wp.val().BoundingBox()
        F=LAND*BW; ring_bot=bb.zmin
        m=tetmesh(wp,15.)
        fixed=lambda x: x[2]>bb.zmax-0.5
        # leg load enters through the ring underside: axial 3BW plus lateral force giving 3BW*0.10 m moment about the flange
        load=lambda x: (x[2]<ring_bot+0.5)
        return m,fixed,load,(0,0,F),dict(F_axial=F,M_lateral_Nm=round(F*0.10,1),Mx=F*0.10*1000)
if __name__=='__main__':
    res={}
    for n in sys.argv[1].split(','):
        m,fx,ld,Fv,info=case(n); r=solve(m,fx,ld,Fv,n,info.pop('Mx',0.0),info.pop('mc',1)); r.update(info)
        r['SF_yield_landing']=SY/r['vm_p995']; r['SF_yield_landing_peak']=SY/r['vm_max']
        r['SF_fatigue_walk']=SE/(r['vm_p995']*WALK/LAND)
        print(n,json.dumps({k:(round(v,2) if isinstance(v,float) else v) for k,v in r.items()}),flush=True); res[n]=r; gc.collect()
    try: old=json.load(open('out/fea.json'))
    except Exception: old={}
    old.update(res); json.dump(old,open('out/fea.json','w'),indent=1)
