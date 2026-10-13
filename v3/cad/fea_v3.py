"""v3 FEA: full-length femur, tibia, knee clevis, pelvis+hip bracket (walking/landing) and side-fall cases on
hip bracket, shoulder-pitch housing and torso side panel. P2 tets (TetGen via meshpy) + scikit-fem, AMG-preconditioned CG.
3 mesh levels per case; peak = 99.5th-percentile element von Mises (single-element singularities at fixtures excluded);
converged when the last refinement changes it by < 10 %. Units mm, N, MPa. Writes out/fea_v3.json, out/fea_v3.md."""
import sys, json, math, gc, os, numpy as np, model, cadquery as cq
from meshpy.tet import MeshInfo, build, Options
import skfem as fe
from skfem.models.elasticity import linear_elasticity, lame_parameters
V3=model.V3; BW=V3['m']*9.81; FALL=V3['fall']; P=model.P
AL=dict(E=71700.,nu=0.33,Sy=503.,Su=572.,Sf=159.)          # 7075-T6 (MIL-HDBK-5 typical; Sf at 5e8)
CF=dict(E=50000.,nu=0.30,Sy=400.)                            # quasi-isotropic CFRP laminate [EST]
LAND,WALK=3.0,1.3; CYC=5*365*8*3600*1.0
def build_all():
    model.PARTS.clear(); model.CHAINS.clear(); model.POSE.clear(); model.ACT_DIM.clear()
    model.build_leg(1); model.build_upper()
def get(names,exact=False):
    sh=[p['solid'] for p in model.PARTS if any((n==p['name']) if exact else (n in p['name']) for n in names)]
    s=sh[0]
    for o in sh[1:]: s=s.union(o)
    return s
def tetmesh(wp,lev,tol):
    q,maxvol=lev
    v,t=wp.val().tessellate(tol,0.4)
    mi=MeshInfo(); mi.set_points([(p.x,p.y,p.z) for p in v]); mi.set_facets([list(x) for x in t])
    o=Options(f'pq{q}Q'); o.fixedvolume=1; o.maxvolume=maxvol
    m=build(mi,options=o)
    return fe.MeshTet(np.array(m.points).T,np.array(m.elements).T)
def solve(mesh,mat,fixed,load,F,sym_y=None):
    if mesh.t.shape[1]>85000: raise RuntimeError('mesh too big %d'%mesh.t.shape[1])
    e=fe.ElementVector(fe.ElementTetP2()); ib=fe.Basis(mesh,e,intorder=2)
    lam,mu=lame_parameters(mat['E'],mat['nu'])
    K=fe.asm(linear_elasticity(lam,mu),ib)
    fac=mesh.facets_satisfying(load,boundaries_only=True)
    if len(fac)==0: raise RuntimeError('no load facets')
    fb=fe.FacetBasis(mesh,e,facets=fac); area=fe.Functional(lambda w:1.0+0*w.x[0]).assemble(fb); tr=np.array(F)/area
    f=fe.LinearForm(lambda v,w: tr[0]*v[0]+tr[1]*v[1]+tr[2]*v[2]).assemble(fb)
    D=ib.get_dofs(fixed).all()
    if sym_y is not None:   # v3.2: half model about the y-symmetry plane -> u_y = 0 there (halves memory, allows one more mesh level)
        D=np.unique(np.concatenate([D,ib.get_dofs(lambda x:np.abs(x[1]-sym_y)<1e-3).all('u^2')]))
    A,b,x,I=fe.condense(K,f,D=D)
    try: Mpc=fe.build_pc_amg(A)
    except Exception: Mpc=None
    xs=fe.solver_iter_pcg(M=Mpc,rtol=1e-8,maxiter=5000)(A,b) if Mpc is not None else fe.solver_iter_pcg(rtol=1e-8,maxiter=20000)(A,b)
    u=np.zeros(K.shape[0]); u[I]=xs
    gu=ib.interpolate(u).grad; eps=0.5*(gu+np.swapaxes(gu,0,1)); t_=eps[0,0]+eps[1,1]+eps[2,2]
    s=2*mu*eps; [s.__setitem__((i,i),s[i,i]+lam*t_) for i in range(3)]
    vm=np.sqrt(0.5*((s[0,0]-s[1,1])**2+(s[1,1]-s[2,2])**2+(s[2,2]-s[0,0])**2)+3*(s[0,1]**2+s[1,2]**2+s[0,2]**2)).max(axis=1)
    i=np.argsort(vm)[int(len(vm)*0.995)]; c=mesh.p[:,mesh.t[:,i]].mean(axis=1)
    r=dict(vm_max=float(vm.max()),vm=float(np.percentile(vm,99.5)),at_mm=[round(float(x),1) for x in c],disp_mm=float(np.abs(u[ib.nodal_dofs]).max()),tets=int(mesh.t.shape[1]),dofs=int(K.shape[0]),load_area=float(area))
    del K,A,ib,fb; gc.collect(); return r
def near_axis_y(x0,z0,r):   # pin-bore faces: within r of a y-axis through (x0,z0)
    return lambda x: np.sqrt((x[0]-x0)**2+(x[2]-z0)**2)<r
def cases():
    hz,kz,az=P['hip_z'],P['knee_z'],P['ankle_z']; y=P['hip_y']
    C={}
    def femur():
        wp=get(['L_femur upper lug','L_femur tube','L_femur root fillet','L_femur knee fillet','L_knee clevis (thigh)']); bb=wp.val().BoundingBox()
        F=LAND*BW; H=F*120/(bb.zmax-kz)
        return wp,AL,(lambda x:x[2]>bb.zmax-0.5),near_axis_y(0,kz,8.6),(H,0,F),'hip lug top fixed; knee-pin bore loaded 3 BW axial + lateral H (root moment 3 BW × 0.12 m)',((3.0,2000),(3.0,50),(3.0,15)),0.5
    def tibia():
        wp=get(['L_tibia tube','L_tibia ankle fillet','L_ankle fork','L_knee tongue']); bb=wp.val().BoundingBox()
        F=LAND*BW; H=F*100/(kz-az)
        return wp,AL,near_axis_y(0,kz,8.6),(lambda x:x[2]<bb.zmin+0.5),(H,0,F),'knee-pin bore fixed; ankle fork underside loaded 3 BW + lateral H (3 BW × 0.10 m)',((40.0,4000),(6.0,2000),(3.0,2000)),0.5
    def knee_clevis():
        wp=get(['L_knee clevis (thigh)']); bb=wp.val().BoundingBox()
        T=V3['rows'][[r['joint'] for r in V3['rows']].index('knee')]['T']; arm=V3['state']['J']['knee']['arm']; Fa=T/arm
        F=LAND*BW+Fa
        return wp,AL,(lambda x:x[2]>bb.zmax-0.5),near_axis_y(0,kz,8.6),(0,0,F),f'bridge top fixed; pin bores loaded 3 BW + peak knee-actuator reaction {Fa:.0f} N',((3.0,25),(3.0,8),(2.0,4),(2.0,2.5)),0.3   # v3.2: 4 levels, finer surface tessellation (3-level run changed 10.6 %)
    def pelvis():
        wp=get(['pelvis shell','L_hip bracket (yaw mount)']); bb=wp.val().BoundingBox()
        F=LAND*BW; ring=[p for p in model.PARTS if p['name']=='L_hip bracket (yaw mount)'][0]['solid'].val().BoundingBox()
        return wp,AL,(lambda x:(x[2]>P['pelvis_top']-4.5)&(np.hypot(x[0],x[1])<60)),(lambda x:(x[2]<ring.zmin+0.5)&(x[1]>0)),(0,F*0.15,F),'waist-yaw opening rim fixed; single-leg landing 3 BW (+0.15 lateral) into the hip-bracket ring',((3.0,300),(3.0,100),(3.0,40)),0.5
    def fall_hip():
        wp=get(['L_hip bracket (yaw mount)']); bb=wp.val().BoundingBox()
        return wp,AL,(lambda x:x[2]>bb.zmax-0.5),(lambda x:x[2]<bb.zmin+0.5),(0,-FALL['hip_F'],0),f"flange fixed; side-fall hip contact {FALL['hip_F']/1000:.1f} kN lateral into the yaw ring",((3.0,100),(3.0,25),(3.0,8)),0.5
    def fall_shoulder():
        wp=get(['L_shoulder pitch housing']); bb=wp.val().BoundingBox()
        return wp,AL,(lambda x:x[1]<bb.ymin+0.5),(lambda x:x[1]>bb.ymax-0.5),(0,0,-FALL['shoulder_F']),f"inboard flange fixed; side-fall shoulder impact {FALL['shoulder_F']/1000:.1f} kN (through clutch+pad) at the outboard end, radial",((3.0,100),(3.0,25),(3.0,8)),0.5
    def fall_torso_panel():
        ts=[p for p in model.PARTS if p['name'].startswith('torso shell')][0]['solid']
        bb=ts.val().BoundingBox()
        wp=ts.intersect(cq.Workplane('XY').box(400,40,400).translate((0,bb.ymax-20,(bb.zmin+bb.zmax)/2)))
        z=P['shoulder_z']; ymax=bb.ymax
        return wp,CF,(lambda x:(np.abs(x[0])>105)&(x[1]<ymax-37)),(lambda x:(np.hypot(x[0],x[2]-z)<52)&(x[1]>ymax-4)),(0,-0.5*FALL['shoulder_F'],0),'torso side panel (CFRP 3 mm [EST isotropic]); front/back wall strips fixed; 50 % of shoulder impact at the pass-through rim',((3.0,100),(3.0,25),(3.0,10)),0.5
    return dict(femur_full=femur,tibia_full=tibia,knee_clevis=knee_clevis,pelvis_hip=pelvis,fall_hip_bracket=fall_hip,fall_shoulder_housing=fall_shoulder,fall_torso_panel=fall_torso_panel)
def save(n,lv,mat,desc,res,op):
    last=lv[-1]; dp=abs(lv[-1]['vm']-lv[-2]['vm'])/lv[-2]['vm']*100 if len(lv)>1 else None
    o=dict(desc=desc,levels=lv,vm=last['vm'],vm_max=last['vm_max'],SF_yield=mat['Sy']/last['vm'],delta_pct=dp,converged=(dp is not None and dp<10),material='7075-T6' if mat is AL else 'CFRP [EST]')
    if not n.startswith('fall'):
        sw=last['vm']*WALK/LAND; sa=sm=sw/2; o['goodman']=1/(sa/AL['Sf']+sm/AL['Su']); o['walk_vm']=sw; o['cycles']=CYC
    cur=json.load(open(op)) if os.path.exists(op) else {}
    cur[n]=o; res.clear(); res.update(cur); json.dump(cur,open(op,'w'),indent=1)
SYM={'knee_clevis':((3.0,8),(2.0,4),(2.0,2))}   # tibia half model lost its load facets (fork underside cut) -> full model
if __name__=='__main__':
    names=sys.argv[1].split(',') if len(sys.argv)>1 else list(cases())
    op='out/fea_v3.json'; res=json.load(open(op)) if os.path.exists(op) else {}
    for n in names:
        build_all(); wp,mat,fx,ld,F,desc,levels,tol=cases()[n]()
        sym=None
        if n in SYM and not os.environ.get('NOSYM'):   # half model: loads and geometry symmetric about the leg's y plane; half the load on the half part
            sym=model.P['hip_y']; wp=wp.intersect(cq.Workplane('XY').box(600,300,1400).translate((0,sym+150,700))); F=tuple(f/2 for f in F); levels=SYM[n]; desc+=' [half model, symmetry plane]'
        lv=[]
        if os.environ.get('MAXLEV'): levels=levels[:int(os.environ['MAXLEV'])]
        for mv in levels:
            try:
                m=tetmesh(wp,mv,tol); r=solve(m,mat,fx,ld,F,sym); r['mesh']=list(mv); lv.append(r)
                print(n,mv,r['tets'],'%.0f MPa (max %.0f)'%(r['vm'],r['vm_max']),flush=True)
            except Exception as ex: print(n,mv,'FAILED',ex,flush=True); break
            gc.collect(); save(n,lv,mat,desc,res,op)
        if not lv: continue
    res=json.load(open(op))
    L=['# v3 FEA (full-length parts with fillet collars; 3-level mesh refinement)','',f'Body weight {BW:.0f} N (v3 mass {V3["m"]:.1f} kg); landing 3 BW, walking 1.3 BW (0→peak, σa=σm=σ/2), 5 y × 8 h at 1 stride/s = {CYC:.2e} cycles; 7075-T6 Sy 503 / Su 572 / Sf(5e8) 159 MPa; Goodman SF = 1/(σa/Sf + σm/Su).','','| case | load | tets (finest) | peak vM (99.5 %) MPa | Δ last refinement % | converged | SF yield | Goodman SF |','|---|---|---|---|---|---|---|---|']
    for k,o in res.items():
        L.append(f"| {k} | {o['desc']} | {o['levels'][-1]['tets']} | {o['vm']:.0f} (max el. {o['vm_max']:.0f}) | {('%.1f'%o['delta_pct']) if o['delta_pct'] is not None else '—'} | {'yes' if o['converged'] else 'NO'} | {o['SF_yield']:.2f} | {('%.2f'%o['goodman']) if 'goodman' in o else '—'} |")
    open('out/fea_v3.md','w').write('\n'.join(L)); print('\n'.join(L))
