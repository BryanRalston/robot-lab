"""R4 CPU FEA of Legs structure parts (CadQuery -> gmsh -> scikit-fem P2 tets -> pyamg CG), units mm / N / MPa. One part per call (box RAM ~1 GB).
Usage: python3 fea_r4.py foot|clamp [h]   -> results/r4/fea_<part>.json"""
import cadquery as cq, numpy as np, json, os, sys, gmsh, meshio, gc
from skfem import MeshTet, ElementTetP2, ElementVector, Basis, FacetBasis, asm, LinearForm
from skfem.models.elasticity import linear_elasticity, lame_parameters
import pyamg
E,NU,RHO,SY,SU,SE=71700.,0.33,2.81e-6,503.,572.,159.   # 7075-T6; RHO kg/mm^3
H=os.path.dirname(os.path.abspath(__file__)); OUT=f'{H}/results/r4'; os.makedirs(OUT,exist_ok=True)
G=9.81; W=65*G; FALL=6*W
J3=json.load(open(f'{H}/results/r3/structure_check.json')); GRF=J3['GRF_peak_N']; FA=J3['loads']['F_ankle_screw']
def box(x0,x1,y0,y1,z0,z1): return cq.Workplane('XY').box(x1-x0,y1-y0,z1-z0).translate(((x0+x1)/2,(y0+y1)/2,(z0+z1)/2))
def foot(skin=4.0,web=4.0,nweb=4,pad=30.0,padt=None,toeskin=None,instep_wall=None):
    """closed box 240 x 100 x 18 (x -60..180, ankle at x=0), skins top/bottom, nweb webs incl. the 2 side walls, 4 mm end caps,
    solid bolt pad under the ankle F/T sensor (|x|<=pad), instep lever block 30x90 x 10..50 at x=70 (v3 geometry)."""
    s=box(-60,180,-50,50,0,skin).union(box(-60,180,-50,50,18-skin,18))
    ys=np.linspace(-50+web/2,50-web/2,nweb)
    for y in ys: s=s.union(box(-60,180,y-web/2,y+web/2,0,18))
    s=s.union(box(-60,-56,-50,50,0,18)).union(box(176,180,-50,50,0,18)).union(box(55,85,-45,45,10,50) if instep_wall is None else box(55,85,-45,45,10,50).cut(box(55+instep_wall,85-instep_wall,-45+instep_wall,45-instep_wall,18,50-instep_wall)))   # instep lever block solid or hollow (open to the plate)
    s=s.union(box(-pad,pad,-50,50,0,18) if padt is None else box(-pad,pad,-50,50,18-padt,18).union(box(-pad,pad,-50,50,0,padt)))   # solid pad, or locally thick skins (padt) under the sensor
    return s
def clamp(b=12.0,hz=22.0,ring_t=6.0,ring_h=30.0):
    """thigh clamp for the hip_pitch screw bodies (config B), recommended form: split collar on the femur ø50 (OD 50+2*ring_t, height ring_h)
    + one arm per side to y=±69 (section b (x) × hz (z)) ending in a 24×24×hz eye boss with a ø12 cross-hole (axis x) for an axial spherical
    rod-end eye at the body end (v3 'sphere' top) instead of side trunnion pin pairs (inner boss would intrude into the femur, L16)."""
    s=cq.Workplane('XY').circle(25+ring_t).circle(25).extrude(ring_h).translate((0,0,-ring_h/2))
    for sg in (1,-1):
        s=s.union(box(-b/2,b/2,min(sg*24,sg*57),max(sg*24,sg*57),-hz/2,hz/2))
        s=s.union(box(-12,12,sg*69-12,sg*69+12,-hz/2,hz/2).cut(cq.Workplane('YZ').circle(6).extrude(30).translate((-15,sg*69,0))))
    return s
def mesh(s,h,fn):
    cq.exporters.export(s,fn+'.step'); gmsh.initialize(); gmsh.option.setNumber('General.Terminal',0)
    gmsh.model.occ.importShapes(fn+'.step'); gmsh.model.occ.synchronize()
    gmsh.option.setNumber('Mesh.MeshSizeMax',h); gmsh.option.setNumber('Mesh.MeshSizeMin',h/3)
    gmsh.model.mesh.generate(3); gmsh.write(fn+'.msh'); gmsh.finalize()
    mm=meshio.read(fn+'.msh'); return MeshTet(mm.points.T.copy(),mm.cells_dict['tetra'].T.copy())
def solve(m,fix,loads,sym=False):
    e=ElementVector(ElementTetP2()); ib=Basis(m,e,intorder=2); lam,mu=lame_parameters(E,NU); K=asm(linear_elasticity(lam,mu),ib)
    D=ib.get_dofs(m.facets_satisfying(fix,boundaries_only=True)).all()
    if sym: D=np.union1d(D,ib.get_dofs(m.facets_satisfying(lambda x:np.abs(x[1])<1e-6,boundaries_only=True)).nodal['u^2'] if False else ib.get_dofs(m.facets_satisfying(lambda x:np.abs(x[1])<1e-6,boundaries_only=True)).all(['u^2']))
    I=ib.complement_dofs(D); Kc=K[I][:,I].tocsr(); del K; gc.collect()
    A=pyamg.smoothed_aggregation_solver(Kc,max_coarse=500,keep=False,smooth=("jacobi",{})); out={}
    for name,parts in loads.items():
        f=np.zeros(ib.N)
        for sel,vec in parts:
            fac=m.facets_satisfying(sel,boundaries_only=True); fb=FacetBasis(m,e,facets=fac); area=asm(LinearForm(lambda v,w:v[0]),fb).sum()
            vv=np.array(vec,float)/area; f+=asm(LinearForm(lambda v,w:v[0]*vv[0]+v[1]*vv[1]+v[2]*vv[2]),fb)
        u=np.zeros(ib.N); res=[]; u[I]=A.solve(f[I],tol=1e-8,accel='cg',maxiter=4000,residuals=res)
        g=ib.interpolate(u).grad; eps=0.5*(g+np.transpose(g,(1,0,2,3))); tr=np.einsum('iiek->ek',eps)
        sig=2*mu*eps+lam*np.einsum('ij,ek->ijek',np.eye(3),tr)
        s=sig; vm=np.sqrt(0.5*((s[0,0]-s[1,1])**2+(s[1,1]-s[2,2])**2+(s[2,2]-s[0,0])**2)+3*(s[0,1]**2+s[1,2]**2+s[0,2]**2))
        ve=vm.max(1); i=int(ve.argmax()); c=m.p[:,m.t[:,i]].mean(1)
        out[name]=dict(vm_max=float(ve.max()),vm_p999=float(np.percentile(ve,99.9)),vm_p99=float(np.percentile(ve,99)),at_mm=c.round(1).tolist(),umax_mm=float(np.abs(u).max()),cg_iters=len(res))
        print(name,{k:(round(v,2) if isinstance(v,float) else v) for k,v in out[name].items()},flush=True)
    return out,ib.N
part=sys.argv[1]; h=float(sys.argv[2]) if len(sys.argv)>2 else 4.0
if part=='foot':
    FP=json.loads(os.environ.get('FOOT','{}')); s=foot(**FP).intersect(box(-70,190,0,60,-5,60)); vol=2*s.val().Volume(); SYM=True; fix=lambda x:(x[2]>18-0.01)&(np.hypot(x[0],x[1])<=30.0)   # ankle F/T sensor face ø60 (rigid)
    toe=lambda x:(x[2]<0.01)&(x[0]>=150); heel=lambda x:(x[2]<0.01)&(x[0]<=-35); inst=lambda x:(x[2]>50-0.01)
    FT=283.2/0.165
    loads={'fall_6BW_toe':[(toe,[0,0,FALL/2])],'fall_6BW_heel':[(heel,[0,0,FALL/2])],
           'op_carry_toe_plus_screw':[(toe,[0,0,FT/2]),(inst,[0,0,-FA/2])]}   # half model: half loads
    note=f'op case: ankle_pitch carry peak 283.2 N·m as toe GRF {FT:.0f} N at x≈165 + screw {FA:.0f} N down on the instep block; fall cases 6 BW {FALL:.0f} N on toe / heel patches'
elif part=='clamp':
    CP=json.loads(os.environ.get('CLAMP','{}')); SYM=True; s=clamp(**CP).intersect(box(-60,60,0,100,-40,40)); vol=2*s.val().Volume()
    fix=lambda x:(np.hypot(x[0],x[1])<25.01)   # bore clamped on the femur (split collar, bolted)
    F=4542.0   # actuator max force per screw (D25), axial along the thigh, through the eye pin
    hole=lambda x:(np.hypot(x[0]*0,(x[1]-69))<6.05)&(np.hypot(x[1]-69,x[2])<6.05)
    loads={'screw_max_push':[(hole,[0,0,F])],'screw_max_pull':[(hole,[0,0,-F])]}   # half model = one side; symmetric both-screw load
    note='each hip_pitch screw body pushes/pulls 4542 N (actuator max) axially through a ø12 eye pin at y=69; half model (y>=0) with symmetry = both screws loaded; femur bore fixed'
gc.collect(); m=mesh(s,h,f'/tmp/legs_{part}'); print('mesh nodes',m.p.shape[1],'tets',m.t.shape[1],flush=True)
res,ndof=solve(m,fix,loads,sym=SYM)
mass=vol*RHO
for k,v in res.items(): v['SF_yield_max']=round(SY/v['vm_max'],2); v['SF_yield_p999']=round(SY/v['vm_p999'],2)
if part=='foot':   # Goodman for the operating case, 0->peak
    v=res['op_carry_toe_plus_screw']; sa=sm=v['vm_max']/2; v['goodman_SF']=round(1/(sa/SE+sm/SU),2)
json.dump(dict(params=os.environ.get('FOOT','{}') if part=='foot' else os.environ.get('CLAMP','{}'),part=part,h_mm=h,nodes=int(m.p.shape[1]),tets=int(m.t.shape[1]),dofs=int(ndof),mass_kg=round(mass,4),note=note,cases=res),open(f"{OUT}/fea_{part}_h{h:g}{os.environ.get('TAG','')}.json",'w'),indent=1)
print('mass',round(mass,4))
