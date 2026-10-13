"""Side-view stick-figure frame strip from a recorded forward-sim qpos log (no GL on the box)."""
import sys,os,numpy as np,mujoco
from gait_lib import load
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
f,out,title=sys.argv[1],sys.argv[2],sys.argv[3]
Q=np.load(f); m=load(); d=mujoco.MjData(m)
chains=[['pelvis','torso'],['torso','head'],['torso','L_shoulderP','L_upper_arm','L_forearm','L_hand'],['torso','R_shoulderP','R_upper_arm','R_forearm','R_hand'],
        ['pelvis','L_hipY','L_thigh','L_shank','L_foot'],['pelvis','R_hipY','R_thigh','R_shank','R_foot']]
n=len(Q); fig,ax=plt.subplots(1,n,figsize=(1.25*n,2.6),sharey=True)
for i,q in enumerate(Q):
    d.qpos[:]=q; mujoco.mj_forward(m,d); x0=q[0]
    for c in chains:
        P=np.array([d.xpos[m.body(b).id] for b in c]); col='C0' if 'L_' in c[-1] else 'C3' if 'R_' in c[-1] else 'k'
        ax[i].plot(P[:,0]-x0,P[:,2],'-o',color=col,ms=2,lw=1.5)
    for s,col in (('l','C0'),('r','C3')):
        g=m.geom(f'{s}_foot').id; c=d.geom_xpos[g]; R=d.geom_xmat[g].reshape(3,3); hx=m.geom_size[g][0]
        a=c-R[:,0]*hx; b=c+R[:,0]*hx; ax[i].plot([a[0]-x0,b[0]-x0],[a[2],b[2]],color=col,lw=3)
    ax[i].axhline(0,color='gray',lw=.8); ax[i].set_xlim(-0.6,0.6); ax[i].set_ylim(-0.05,1.75); ax[i].set_aspect('equal'); ax[i].set_xticks([]); ax[i].set_title(f'{i*0.5:.1f} s\nx={x0:.2f} m',fontsize=7)
fig.suptitle(title,fontsize=9); fig.tight_layout(); fig.savefig(out,dpi=90); print(out)
