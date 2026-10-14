"""A38 L2: hip clamp-eye tine with the A37 rev B PEI sleeve (bore 20) - light 2D plane-stress FEA (scikit-fem, Q2 quads,
O-grid mapped mesh, no gmsh). Tine = 7075-T6 plate t 8, width W 30 (x), hole centre at e from the free end, root (fixed) at Lr 24
on the other side. Load 6550 N/body fault (BOND_SPEC 5) shared by 2 tines -> 3275 N/tine; 4542 N/body walk -> 2271 N/tine.
Bore loading: cosine radial pressure over the loaded half (pin/sleeve bearing). Two directions: toward the free end (tension
lug, worst) and toward the root. Reports peak von Mises and net-section/bearing hand values. Plane stress through-thickness uniform
=> no pin bending/peaking (EST, real peak higher by ~1.1-1.3)."""
import numpy as np, json, sys
from skfem import MeshQuad, ElementQuad2, ElementVector, Basis, FacetBasis, asm, LinearForm, condense, solve
from skfem.models.elasticity import linear_elasticity, lame_parameters
E,NU,t=71700.,0.33,8.0
def mesh(D,e,W=float(__import__('os').environ.get('W',30)),Lr=24.,nr=24,nth=128):
    # rectangle x in [-W/2,W/2], z in [-Lr,e]; hole r=D/2 at origin. O-grid: ray from hole to boundary.
    th=np.linspace(0,2*np.pi,nth+1)[:-1]; pts=[]
    def bnd(a):
        c,s=np.cos(a),np.sin(a); ts=[]
        if abs(c)>1e-12: ts+= [ (W/2)/c if c>0 else (-W/2)/c ]
        if abs(s)>1e-12: ts+= [ e/s if s>0 else -Lr/s ]
        tt=min(x for x in ts if x>0); return np.array([c*tt,s*tt])
    R=D/2; g=np.linspace(0,1,nr+1)**1.8
    for k in range(nr+1):
        for a in th:
            p0=R*np.array([np.cos(a),np.sin(a)]); p1=bnd(a); pts.append(p0+(p1-p0)*g[k])
    P=np.array(pts).T; idx=lambda k,i:k*nth+(i%nth); T=[]
    for k in range(nr):
        for i in range(nth): T.append([idx(k,i),idx(k,i+1),idx(k+1,i+1),idx(k+1,i)])
    return MeshQuad(P,np.array(T).T)
def run(D,e,F,dirn):
    m=mesh(D,e); el=ElementVector(ElementQuad2()); ib=Basis(m,el,intorder=4)
    lam,mu=lame_parameters(E,NU); lam=2*lam*mu/(lam+2*mu)   # plane stress
    K=asm(linear_elasticity(lam,mu),ib)
    R=D/2; th0=np.pi/2 if dirn>0 else -np.pi/2; p0=F/(t*R*np.pi/2)   # int cos^2 over half = pi/2
    fb=FacetBasis(m,el,facets=m.facets_satisfying(lambda x:np.abs(np.hypot(x[0],x[1])-R)<0.05))
    @LinearForm
    def L(v,w):
        a=np.arctan2(w.x[1],w.x[0]); c=np.maximum(np.cos(a-th0),0)*p0
        return c*(np.cos(a)*v[0]+np.sin(a)*v[1])   # pressure pushes material outward from the hole along the load
    f=asm(L,fb)
    D_=ib.get_dofs(lambda x:np.abs(x[1]+24.)<1e-6).all()
    u=solve(*condense(K,f,D=D_))
    # stress at quad points
    du=ib.interpolate(u).grad; exx,ezz=du[0,0],du[1,1]; exz=0.5*(du[0,1]+du[1,0])
    sxx=lam*(exx+ezz)+2*mu*exx; szz=lam*(exx+ezz)+2*mu*ezz; sxz=2*mu*exz
    vm=np.sqrt(sxx**2-sxx*szz+szz**2+3*sxz**2)
    X=ib.global_coordinates().value; far=X[1]>-20   # ignore the fixed-root singularity
    pk=float(vm[far].max()); j=np.unravel_index(np.argmax(np.where(far,vm,0)),vm.shape)
    return pk,[round(float(X[0][j]),1),round(float(X[1][j]),1)]
out=[]
CASES=json.loads(__import__('os').environ.get('CASES','null')) or [(12,12,'as-is ø12 e12'),(20,12,'rev B ø20 in current tine e12'),(20,16,'ø20 e16 (+4)'),(20,20,'ø20 e20 (+8, Materials)')]
for D,e,tag in CASES:
    for F,lc in ((3275,'fault'),(2271,'walk')):
        for dn in (1,-1):
            pk,at=run(D,e,F,dn)
            out.append(dict(case=tag,D=D,e=e,load=lc,F_N=F,dir='to free end' if dn>0 else 'to root',vm_peak=round(pk,1),at=at,
                 net_section_MPa=round(F/((float(__import__('os').environ.get('W',30))-D)*t),1),shear_out_MPa=round(F/(2*(e-D/2*0.7)*t),1),bearing_MPa=round(F/(D*t),1),e_over_D=round(e/D,2),lig_mm=e-D/2))
            print(out[-1],flush=True)
json.dump(dict(basis=__doc__,rows=out),open(__import__('os').environ.get('OUT','results/a38/tine_fea_a38.json'),'w'),indent=1)
