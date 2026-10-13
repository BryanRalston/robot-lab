"""R3 sit-to-stand with the chair in the scene: clearance of every robot geom to the seat over the rise, and a side-view strip."""
import os,sys,json,numpy as np,mujoco
XF=float(os.environ.get('CHAIR_XF','-0.06'))   # seat front edge x (m); must stay behind the shanks when standing (ankle at x=0)
R=json.load(open(os.path.join(os.path.dirname(__file__),'results/r3/sit_to_stand_r3.json')))['info']; H=float(os.environ.get('CHAIR_H',R['seat_h']))   # seat top; the plan's seat_h is the hip-height basis (hip at seat_h+0.04)
os.environ['LEGS_CHAIR']=f'{XF},{H}'
from gait_lib import load
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
m=load(); d=mujoco.MjData(m); Z=np.load('results/r3/sit_to_stand_r3.npz'); Q=Z['Q'].astype(float); t=Z['t']
seat=m.geom('chair_seat').id; back=m.geom('chair_back').id; posts=[m.geom(f'chair_post{i}').id for i in range(4)]
rob=[g for g in range(m.ngeom) if m.geom_bodyid[g]!=0]
dmin=[]; who=[]
for q in Q:
    d.qpos[:]=q; mujoco.mj_forward(m,d); best=(9,None)
    for g in rob:
        for c in [seat,back]+posts:
            fr=np.zeros(6); v=mujoco.mj_geomDistance(m,d,g,c,0.5,fr)
            if v<best[0]: best=(v,m.geom(g).name or m.body(m.geom_bodyid[g]).name)
    dmin.append(best[0]); who.append(best[1])
dmin=np.array(dmin); i=int(dmin.argmin())
out=dict(seat_h_m=H,seat_front_x_m=XF,min_clearance_m=float(dmin.min()),at_t_s=float(t[i]),geom=who[i],clearance_at_start_m=float(dmin[0]),penetration_frames=int((dmin<0).sum()))
json.dump(out,open('results/r3/sit_chair_clearance.json','w'),indent=1); print(out)
chains=[['pelvis','torso'],['torso','head'],['torso','L_shoulderP','L_upper_arm','L_forearm','L_hand'],['pelvis','L_hipY','L_thigh','L_shank','L_foot'],['pelvis','R_hipY','R_thigh','R_shank','R_foot']]
idx=np.linspace(0,len(Q)-1,7).astype(int); fig,ax=plt.subplots(1,len(idx),figsize=(11,2.9),sharey=True)
for a,k in zip(ax,idx):
    d.qpos[:]=Q[k]; mujoco.mj_forward(m,d)
    a.add_patch(plt.Rectangle((XF-0.42,H-0.03),0.42,0.03,color='peru')); a.add_patch(plt.Rectangle((XF-0.45,H),0.03,0.5,color='peru')); a.plot([XF-0.40,XF-0.40],[0,H-0.03],color='peru'); a.plot([XF-0.02]*2,[0,H-0.03],color='peru')
    for c in chains:
        P=np.array([d.xpos[m.body(b).id] for b in c]); a.plot(P[:,0],P[:,2],'-o',ms=2,lw=1.5,color='C0' if 'L_' in c[-1] else 'C3' if 'R_' in c[-1] else 'k')
    a.axhline(0,color='gray',lw=.8); a.set_xlim(-0.55,0.45); a.set_ylim(-0.02,1.7); a.set_aspect('equal'); a.set_xticks([]); a.set_title(f't={t[k]:.2f} s\nclear {dmin[k]*1000:.0f} mm',fontsize=7)
fig.suptitle(f'Legs r3 sit-to-stand (R-012 re-plan): seat {H:.2f} m, waist lean {R["waist_lean_deg"]:.0f}°, hip ≥ {R["hip_min_traj_deg"]:.0f}°, 65 kg, R1.2 limits',fontsize=9)
fig.tight_layout(); fig.savefig(sys.argv[1] if len(sys.argv)>1 else 'plots/r3_sit.png',dpi=90)
