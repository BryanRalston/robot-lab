"""R2: independent convergence benchmark of job 1's hex8 element (imports its element/assembly)."""
import sys,json,numpy as np
sys.path.insert(0,'../design/fea/job1_pad_r8')
import fea_job1 as f
from scipy.sparse.linalg import spsolve
def cant(n,L=100.,b=10.,h=10.,F=100.):
    nx=ny=n; nz=int(n*L/b)
    m=f.Mesh(); m.add_block(np.linspace(0,b,nx+1),np.linspace(0,h,ny+1),np.linspace(0,L,nz+1),"link")
    m.xyz=np.asarray(m.xyz,float); x=m.xyz; K,_=f.assemble(m); nd=3*len(x)
    fv=np.zeros(nd); top=np.where(abs(x[:,2]-L)<1e-8)[0]; fv[3*top+1]=F/len(top)
    bot=np.where(abs(x[:,2])<1e-8)[0]; fd=np.r_[3*bot,3*bot+1,3*bot+2]
    fr=np.setdiff1d(np.arange(nd),fd); u=np.zeros(nd); u[fr]=spsolve(K[fr][:,fr],fv[fr])
    tip=u.reshape(-1,3)[top,1].mean(); I=b*h**3/12; G=f.E_MPA/2/(1+f.NU)
    ref=F*L**3/3/f.E_MPA/I+1.2*F*L/G/(b*h)
    return dict(n_through=n,elems=nx*ny*nz,tip=tip,ref=ref,err_pct=100*(tip-ref)/ref)
out=[cant(n) for n in (1,2,4)]
print(json.dumps(out,indent=1)); json.dump(out,open('r2_hex8_bench.json','w'),indent=1)
