"""Export the 0.8 m/s forward-sim gait (65 kg, CONTRACTS R1.2 limits, fsim completes) as joint trajectories: CSV + JSON in modules/legs/exports/.
Columns: t; base x,y,z,qw,qx,qy,qz (fsim); every hinge joint q [rad] from the forward sim (100 Hz); leg qd [rad/s] (central difference);
leg reference q and ID feed-forward torque [N·m] from the gait-ID plan (results/r2/walk_0p8.npz, interpolated to the same clock)."""
import os,json,numpy as np,mujoco
os.environ.setdefault('LEGS_MASS','65'); os.environ.setdefault('LEGS_LIMITS','r1')
from gait_lib import load,LEG
H=os.path.dirname(os.path.abspath(__file__)); DT=0.01
Q=np.load(f'{H}/results/r2/fsim/walk_0p8_fb1_kr4_export_qpos.npy'); m=load(); t=np.arange(len(Q))*DT
Z=np.load(f'{H}/results/r2/walk_0p8.npz'); tr=Z['t']-Z['t'][0]+0.0; qa=Z['qa']; va=Z['va']
hinges=[i for i in range(m.njnt) if m.jnt_type[i]==3]; names=[m.joint(i).name for i in hinges]; adr=[m.jnt_qposadr[i] for i in hinges]
legn=[f'{s}_{j}' for s in 'lr' for j in LEG]
qd=np.gradient(Q[:,[m.jnt_qposadr[m.joint(n).id] for n in legn]],DT,axis=0)
# the fsim clock starts at the first frame of the trimmed ID plan (fsim.py reads the same npz) -> align by sample time
qref=np.stack([np.interp(t,tr,Z['Q'][:,a]) for a in qa],1); tff=np.stack([np.interp(t,tr,Z['TAU'][:,v]) for v in va],1)
cols=['t_s','base_x','base_y','base_z','base_qw','base_qx','base_qy','base_qz']+[f'q_{n}' for n in names]+[f'qd_{n}' for n in legn]+[f'qref_{n}' for n in legn]+[f'tauff_{n}' for n in legn]
D=np.c_[t,Q[:,:7],Q[:,adr],qd,qref,tff]
np.savetxt(f'{H}/exports/walk_0p8_fsim_65kg.csv',D,delimiter=',',header=','.join(cols),comments='',fmt='%.6g')
meta=dict(description='Legs forward-sim walk 0.8 m/s, v3 model scaled to 65 kg, CONTRACTS R1.2 torque limits; completes the plan (16 touchdowns)',rate_hz=1/DT,duration_s=float(t[-1]),
          units=dict(q='rad',qd='rad/s',tau='N·m',base='m / unit quaternion (w,x,y,z)'),joint_sign='MuJoCo v3 model (hip_pitch negative = flexion, knee positive = flexion)',
          sources=dict(fsim='results/r2/fsim/walk_0p8_fb1_kr4_export.json',plan='results/r2/walk_0p8.npz'),repro='LEGS_OUT=r2 LEGS_MASS=65 LEGS_LIMITS=r1 python3 fsim.py walk_0p8 --kc 10 --kr 4 --record 0.01 --tag _kr4_export && python3 export_gait.py',
          columns=cols)
json.dump(dict(meta=meta,t=t.round(4).tolist(),base=Q[:,:7].round(6).tolist(),joints={n:Q[:,a].round(6).tolist() for n,a in zip(names,adr)},
               leg_qd={n:qd[:,i].round(5).tolist() for i,n in enumerate(legn)},leg_qref={n:qref[:,i].round(6).tolist() for i,n in enumerate(legn)},leg_tau_ff={n:tff[:,i].round(3).tolist() for i,n in enumerate(legn)}),
          open(f'{H}/exports/walk_0p8_fsim_65kg.json','w'))
print(D.shape,len(cols),'max |q-qref| leg rad',float(np.abs(Q[:,[m.jnt_qposadr[m.joint(n).id] for n in legn]]-qref).max()))
