"""R4 progress image: needle-cheek hip lever FEA (SF 1.5) + mass waterfall (M1 items, M3 harness) vs 66.5 kg."""
import numpy as np, json, os, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
H=os.path.dirname(os.path.abspath(__file__)); d=np.load(f'{H}/results/hp_lever_fea_field.npz'); r=json.load(open(f'{H}/results/hp_lever_fea_r4.json'))
R4=json.load(open(f'{H}/results/mass_rollup_r4.json'))
p,t,vm=d['p'],d['t'],d['vm']; c=p[:,t].mean(1); o=np.argsort(vm)
fig,ax=plt.subplots(1,2,figsize=(16,5.6),gridspec_kw=dict(width_ratios=[1.1,1]))
sc=ax[0].scatter(c[1,o],c[2,o],c=np.clip(vm[o],0,340),s=4,cmap='turbo',vmin=0,vmax=340); ax[0].set_aspect('equal'); fig.colorbar(sc,ax=ax[0],label='von Mises MPa (SF 1.5 line 335)')
ax[0].set_title(f"hip_pitch lever, needle cheeks: {r['mass_kg']:.3f} kg, SF {r['SF_sym']:.2f} ({r['worst_sym']}, 4542 N/pin)"); ax[0].set_xlabel('y mm'); ax[0].set_ylabel('z mm')
steps=R4['waterfall']; x=0; lv=R4['base']
ax[1].bar(0,lv,color='0.6'); ax[1].text(0,lv+0.05,f'{lv:.2f}',ha='center')
for i,(k,v) in enumerate(steps.items(),1):
    ax[1].bar(i,v,bottom=lv,color='g' if v<0 else 'r'); lv+=v; ax[1].text(i,lv+0.05 if v>0 else lv-0.12,f'{v:+.3f}',ha='center',fontsize=8)
ax[1].bar(len(steps)+1,lv,color='C0'); ax[1].text(len(steps)+1,lv+0.05,f'{lv:.2f}',ha='center')
ax[1].axhline(66.5,color='r',ls='--',label='T2 hard 66.5 (R-017)'); ax[1].set_ylim(65.5,68.3)
ax[1].set_xticks(range(len(steps)+2)); ax[1].set_xticklabels(['R-016\nbase']+[k.replace(' ','\n') for k in steps]+['R4'],fontsize=7); ax[1].legend(); ax[1].set_ylabel('robot kg')
ax[1].set_title('R4 mass: M1 actuator items + M3 harness')
out='/workspace/robot-lab/media/progress/2026-10-13_actuators_r4_mass_cuts.png'; fig.savefig(out,dpi=110,bbox_inches='tight'); print(out)
