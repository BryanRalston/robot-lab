"""Round-2 progress image: regen bus-power trace (walk 1.2 m/s) + leg-actuator mass recovery."""
import json, os, numpy as np, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
H=os.path.dirname(os.path.abspath(__file__)); R=os.path.join(H,'../..')
z=np.load(f'{H}/results/regen_sim_trace.npz'); g=json.load(open(f'{H}/results/regen_sim.json'))['cases']; S=json.load(open(f'{H}/results/sizing.json'))
fig,ax=plt.subplots(1,2,figsize=(15,5.5),gridspec_kw=dict(width_ratios=[1.6,1]))
a=ax[0]; t=z['t']
a.plot(t,z['PA'],color='tab:red',lw=.8,label=f"no regen (each drive dumps): steady 2-7 s {g['A_no_regen']['P_chem_steady_2to7s']:.0f} W → {g['A_no_regen']['runtime_h_steady']:.2f} h")
a.plot(t,z['PB'],color='tab:green',lw=.8,label=f"shared bus + charge ≤30 A: steady 2-7 s {g['C_netting_plus_charge']['P_chem_steady_2to7s']:.0f} W → {g['C_netting_plus_charge']['runtime_h_steady']:.2f} h")
a.fill_between(t,z['PB'],0,where=z['PB']<0,color='tab:blue',alpha=.5,label='net regen into battery')
a.axvspan(2,7,color='gray',alpha=.08); a.axhline(0,color='k',lw=.5); a.set_xlabel('time s (Legs walk_1p2 gait ID)'); a.set_ylabel('DC bus power W (incl. 254 W rest of robot)')
a.set_title('Regen sim, 20S5P 1620 Wh: runtime at 1.2 m/s (90 % usable)'); a.legend(fontsize=8,loc='upper right'); a.grid(alpha=.3)
b=ax[1]; sel=S['sel']; L=['hip_yaw','hip_roll','hip_pitch','knee','ankle_pitch']
r1=dict(hip_yaw=1.11,hip_roll=1.56,hip_pitch=2.37,knee=2.37,ankle_pitch=1.89)
x=np.arange(len(L)); b.bar(x-.2,[2*r1[j] for j in L],.4,color='tab:red',label=f"round 1 (housing model ×1.25 + 1.30 kg linkage EST): {2*sum(r1.values()):.2f} kg")
b.bar(x+.2,[2*sel[j]['mass'] for j in L],.4,color='tab:green',label=f"round 2 (CadQuery housings + linkage): {sum(2*sel[j]['mass'] for j in L):.2f} kg")
b.set_xticks(x); b.set_xticklabels(L,rotation=20); b.set_ylabel('both legs, kg'); b.legend(fontsize=8); b.grid(alpha=.3,axis='y')
b.set_title(f"Leg actuator mass; robot {S['mass']['total_new']:.2f} kg (before Legs/Torso items)")
fig.suptitle('RL Actuators round 2 (2026-10-13): knee 7565 rpm (≤7600), CAD mass recovery, DC-bus regen sim',fontsize=11); fig.tight_layout()
out=f'{R}/media/progress/2026-10-13_actuators_r2_regen_mass.png'; fig.savefig(out,dpi=110); print(out)
