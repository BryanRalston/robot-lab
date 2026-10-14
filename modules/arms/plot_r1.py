import json,os,matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
H=os.path.dirname(os.path.abspath(__file__)); L=json.load(open(os.path.join(H,'arm_loads_r1.json')))
J=['shoulder_pitch','shoulder_roll','shoulder_yaw','elbow','wrist_roll','wrist_pitch','wrist_yaw']
st={j:max(v['joints'][j]['static'] for k,v in L.items() if k[0]!='_') for j in J}
avail={'shoulder_pitch':167,'shoulder_roll':164,'shoulder_yaw':70,'elbow':76,'wrist_roll':36,'wrist_pitch':48,'wrist_yaw':48}
spd={'shoulder_pitch':4,'shoulder_roll':4,'shoulder_yaw':4,'elbow':6,'wrist_roll':6,'wrist_pitch':6,'wrist_yaw':6}
need={j:max(1.5*st[j],{'wrist_roll':7.4}.get(j,0)) for j in J}
fig,(a,b)=plt.subplots(1,2,figsize=(14,7),gridspec_kw=dict(width_ratios=[1,1.5]))
# schematic (sim/v3 geometry, left arm, front view-ish)
pts=[(0,0.22),(0.112,0.18),(0.112,0.08),(0.112,-0.08),(0.112,-0.33),(0.112,-0.43)]
a.plot([0,0],[0.0,0.30],'k-',lw=8,alpha=.3); a.plot(*zip(*pts),'-',color='#b8860b',lw=6)
for p,t in zip(pts,['shoulder pitch (y)','shoulder roll (x)','shoulder yaw (z), 0.10 below roll','elbow (y), 0.26 below roll','wrist roll/pitch/yaw, 0.25 below elbow','hand (tendon, 11 drives in forearm)']):
    a.plot(*p,'o',ms=12,mfc='w',mec='k'); a.text(p[0]+0.03,p[1],t,va='center',fontsize=9)
a.set_xlim(-0.1,0.45); a.set_ylim(-0.55,0.35); a.set_aspect('equal'); a.set_title('Left arm layout (sim/v3 offsets, m) [schematic]'); a.axis('off')
x=range(len(J)); w=0.27
b.bar([i-w for i in x],[st[j] for j in J],w,label='max static load, sim/v3 + 10 kg (N·m)',color='#888')
b.bar([i for i in x],[need[j] for j in J],w,label='need = 1.5 × static (N·m)',color='#d95f02')
b.bar([i+w for i in x],[avail[j] for j in J],w,label='selected avail peak (v3 catalog, N·m)',color='#1b9e77')
for i,j in enumerate(J): b.text(i+w,avail[j]+3,f"{avail[j]/need[j]:.2f}×\n{spd[j]} rad/s",ha='center',fontsize=8)
b.set_xticks(list(x)); b.set_xticklabels([j.replace('_','\n') for j in J]); b.set_ylabel('N·m'); b.legend(fontsize=8)
b.set_title('RL Arms R1: torque need vs selection (labels: avail/need, speed need [EST v2])')
fig.suptitle('2026-10-14 RL Arms & Hands R1 architecture'); fig.tight_layout()
for p in [os.path.join(H,'R1_arm_layout_torque.png'),'/workspace/2026-10-14_arms_R1_layout_torque.png',os.path.join(H,'../../media/progress/2026-10-14_arms_R1_layout_torque.png')]:
    os.makedirs(os.path.dirname(p),exist_ok=True); fig.savefig(p,dpi=110)
print(st,need)
