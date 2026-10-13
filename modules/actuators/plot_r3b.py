"""R3b progress image: hip_pitch lever (config B) von Mises at worst symmetric case, plus clearance vs angle."""
import numpy as np, json, os, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
import hp_clearance as C
H=os.path.dirname(os.path.abspath(__file__)); d=np.load(f'{H}/results/hp_lever_fea_field.npz'); r=json.load(open(f'{H}/results/hp_lever_fea.json'))
p,t,vm=d['p'],d['t'],d['vm']; c=p[:,t].mean(1); o=np.argsort(vm)
fig,ax=plt.subplots(1,3,figsize=(17,5.4))
for a,(i,j,lab) in zip(ax[:2],((1,2,'front view (y-z), lever radius down'),(1,0,'top view (y-x), x = tangential'))):
    sc=a.scatter(c[i,o],c[j,o],c=np.clip(vm[o],0,300),s=4,cmap='turbo',vmin=0,vmax=300); a.set_aspect('equal'); a.set_title(lab); a.set_xlabel('y mm')
fig.colorbar(sc,ax=ax[:2],label='von Mises MPa (7075-T6 Sy 503; SF 2 line 251)')
R=C.run(); th=[x['theta'] for x in R]; ax[2].plot(th,[x['rod'] for x in R],label='rod vs ø32 boss in screw plane (L10 layout)')
ax[2].axhline(41,color='g',label='new layout: lateral clearance 41 mm (any angle)'); ax[2].axhline(2,color='r',ls='--',label='2 mm target')
ax[2].axvspan(-120,-78,color='0.9',label='outside R-012/L12 range'); ax[2].set_ylim(-25,50); ax[2].set_xlabel('hip_pitch deg'); ax[2].set_ylabel('clearance mm'); ax[2].legend(fontsize=7)
fig.suptitle(f"hip_pitch lever, thigh-mounted (B): {r['mass_kg']:.3f} kg, {r['worst_sym']} at 4542 N/screw: SF_yield {r['SF_sym']:.2f} (fault {r['SF_fault']:.2f}); P2 tets h 4 mm")
out='/workspace/robot-lab/media/progress/2026-10-13_actuators_r3b_hip_lever_fea.png'; fig.savefig(out,dpi=110,bbox_inches='tight'); print(out)
