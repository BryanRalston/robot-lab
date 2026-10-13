"""Round-3 progress image: steady walking power (no / half / full regen) vs 729 W line, and sweep retention histograms."""
import json, os, numpy as np, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
H=os.path.dirname(os.path.abspath(__file__)); R=os.path.join(H,'../..'); S=json.load(open(f'{H}/results/regen_sim.json'))
fig,ax=plt.subplots(1,2,figsize=(15,5.5))
a=ax[0]; gs=['walk_0p8','walk_1p0','walk_1p2']; x=np.arange(3); c=dict(P_noregen='tab:red',P_half='tab:orange',P_full='tab:green')
for i,k in enumerate(['P_noregen','P_half','P_full']):
    v=[S[g][k] for g in gs]; a.bar(x+(i-1)*.27,v,.27,color=c[k],label={'P_noregen':'no regen','P_half':'half credit (R-009 ×0.5)','P_full':'full regen (model)'}[k])
    for xx,vv in zip(x+(i-1)*.27,v): a.text(xx,vv+8,f"{vv:.0f}\n{1458/vv:.2f} h",ha='center',fontsize=7)
a.axhline(729,color='k',ls='--',lw=1,label='T7 pass line 729 W (2 h on 1620 Wh × 0.9)')
a.set_xticks(x); a.set_xticklabels(['0.8 m/s','1.0 m/s','1.2 m/s']); a.set_ylabel('steady robot power W (iron loss incl.)'); a.set_ylim(0,1100); a.legend(fontsize=8,loc='upper left'); a.grid(alpha=.3,axis='y')
a.set_title('Steady walking power on the shared 20S bus')
b=ax[1]
for g,col in (('walk_1p2','tab:blue'),('walk_1p0','tab:purple')):
    J=json.load(open(f'{H}/results/regen_sweep_{g}.json')); b.axvline(J['retention']['min'],color=col,ls=':')
    rows=[]  # histogram from one-at-a-time is too coarse; re-run full grid retentions
import regen_core as rc, itertools
for g,col in (('walk_1p2','tab:blue'),('walk_1p0','tab:purple')):
    J=json.load(open(f'{H}/results/regen_sweep_{g}.json')); G=J['grid']; path=J['gait']; R0=J['nominal']['regen_W']; ret=[]
    for combo in itertools.product(*G.values()):
        p=dict(zip(G,combo)); vc,ir=p.pop('batt'); p.update(vcell=vc,ir_x=ir); ret.append(rc.run(path,p)['regen_W']/R0)
    b.hist(ret,bins=60,alpha=.5,color=col,label=f"{g}: {len(ret)} corners, min {min(ret):.2f}, 5th pct {np.percentile(ret,5):.2f}")
b.axvline(0.77,color='k',ls='--',label='R-009 requirement 0.77'); b.set_xlabel('fraction of modeled regen retained'); b.set_ylabel('corners'); b.legend(fontsize=8); b.grid(alpha=.3)
b.set_title('Sensitivity sweep (efficiency, iron, Cu temp, charge, battery, mass, cadence)')
fig.suptitle('RL Actuators round 3 (2026-10-13): iron loss added; 1.0 m/s fallback; regen retention sweep',fontsize=11); fig.tight_layout()
out=f'{R}/media/progress/2026-10-13_actuators_r3_regen_sweep.png'; fig.savefig(out,dpi=110); print(out)
