import json,numpy as np,matplotlib,os
matplotlib.use('Agg'); import matplotlib.pyplot as plt
R=json.load(open('results/r2/linkage_study.json')); F=R['actuator_basis']
fig,ax=plt.subplots(1,3,figsize=(16,4.6))
k=R['knee']; lev=[r['geom']['lever_mm'] for r in k['results']]
for key,lab in (('torque_ratio_min','torque / 1.5×peak (non-carry)'),('speed_ratio_min','speed / need'),('carry_ratio_min','torque / 1.2×carry')): ax[0].plot(lev,[r[key] for r in k['results']],'o-',label=lab)
ax[0].axhline(1,color='k',lw=.8); ax[0].invert_xaxis(); ax[0].set_xlabel('knee lever mm'); ax[0].set_ylabel('worst-angle ratio'); ax[0].legend(fontsize=8); ax[0].set_title('knee lever sweep (geometry re-optimised per lever)'); ax[0].grid(alpha=.3)
b=np.array(k['bins'])
for r in k['results']:
    if r['geom']['lever_mm'] in (58.5,47.5,42.5,40): arm=np.array([a for _,a in r['arm_profile']]); ax[1].plot(b,F['knee']['F_total_N']*arm/1000,label=f"avail, lever {r['geom']['lever_mm']}")
ax[1].step(b,k['need_T'],'k',where='mid',label='1.5×ID peak (non-carry)'); ax[1].step(b,k['carry_T'],'k--',where='mid',label='1.2×carry peak'); ax[1].set_xlabel('knee angle deg'); ax[1].set_ylabel('N·m'); ax[1].legend(fontsize=7); ax[1].grid(alpha=.3); ax[1].set_title('knee torque vs angle')
h=R['hip_pitch_A_pelvis_mounted']; c=h['full_rom_check']; hb=np.array(R['hip_pitch']['bins'])
ax[2].plot(c['theta'],c['torque_Nm'],label='avail, pelvis-mounted geometry (gait-optimised)'); ax[2].step(hb,R['hip_pitch']['need_T'],'k',where='mid',label='1.5×ID peak'); ax[2].step(hb,R['hip_pitch']['carry_T'],'k--',where='mid',label='1.2×carry')
ax[2].set_xlabel('hip pitch deg (− = flexion)'); ax[2].legend(fontsize=7); ax[2].grid(alpha=.3); ax[2].set_title('hip_pitch twin screw, 50 mm lever')
fig.tight_layout(); os.makedirs('plots/r2',exist_ok=True); fig.savefig('plots/r2/linkage_study.png',dpi=80)
