"""R4 M2 leg structure (R-015/R-017): structure + thigh clamp + instep lugs <= 4.85 kg both legs. Masses: FEA solids (fea_r4.py), hand formulas, r3 rows.
Writes results/r4/structure_m2.md/.json and media bar chart."""
import json,math,os,sys
H=os.path.dirname(os.path.abspath(__file__)); R=f'{H}/results/r4'; RHO=2.81e-6
f=lambda n:json.load(open(f'{R}/{n}.json'))
foot=f('fea_foot_h5_r4a'); foot6=f('fea_foot_h6_r4a'); cl=f('fea_clamp_h2.5_hz30')
r3=json.load(open(f'{H}/results/r2/structure_mass.json'))
def r3m(name): return [r for r in r3['rows'] if r['part']==name][0]['new_kg']
def Z(D,t): d=D-2*t; return (D**4-d**4)/D
def tube(D,t,m16): return m16*(t*(D-t))/(1.6*(D-1.6))
ring=(math.pi/4*(96**2-80**2)*25+50*25*20)*RHO   # CRBH 5013 seat ring OD96/ID80 x 25 (|y|<=12.5) + neck 50x25x20 to the femur collar
# ring lug hand check (Kt 3 net tension, shear-out, bearing), load per D27: 2x4542 + 1.5 BW + M 192 N·m as 192/0.080 edge couple
P=2*4542+1.5*65*9.81+192/0.080
lug=dict(P_N=round(P),net_tension_MPa=round(3*P/((96-80)*25),1),shear_out_MPa=round(P/(2*8*25),1),bearing_MPa=round(P/(80*13),1))
lug.update(SF_net=round(503/lug['net_tension_MPa'],2),SF_shear=round(0.577*503/lug['shear_out_MPa'],2),fatigue_SF_net=round(159/(lug['net_tension_MPa']*0.52),2))
sf_fem=8.54*Z(50,1.2)/Z(50,1.6); sf_tib=4.99*Z(45,1.2)/Z(45,1.6)
rows=[('thigh','femur tube Ø50 wall 1.2 mm (was 1.6)',tube(50,1.2,r3m('femur tube 7075 Ø50')),f'SF yield {sf_fem:.2f} (v3 FEA × BW × Z ratio); +9084 N hip screw axial below the clamp: {9084/(math.pi*(50-1.2)*1.2):.0f} MPa'),
 ('thigh','femur collars ×2',r3m('femur collars ×2'),'unchanged'),
 ('thigh','femur hip ring: CRBH 5013 seat ø80 H7×13, OD 96 × 25 (|y|≤12.5) + neck',ring,f"hand: net tension SF {lug['SF_net']}, shear-out SF {lug['SF_shear']}, fatigue {lug['fatigue_SF_net']} at P {lug['P_N']} N; replaces the 0.212 kg ø32 lug"),
 ('thigh','knee clevis',r3m('knee clevis'),'r3 (SF ≥ 4.80 v3-scaled, hand 15.3)'),
 ('shank','tibia tube Ø45 wall 1.2 mm (was 1.6)',tube(45,1.2,r3m('tibia tube 7075 Ø45')),f'SF yield {sf_tib:.2f}'),
 ('shank','tibia collar',r3m('tibia collar'),'unchanged'),
 ('shank','ankle fork (top plate pocketed)',r3m('ankle fork'),'r3 hand SF 3.44'),
 ('shank','knee tongue',r3m('knee tongue (pin lug, lever removed)'),'r3 hand SF 35'),
 ('foot','foot closed box (3.5 mm skins, 4 webs, 6 mm skins under sensor, hollow instep 5 mm)',foot['mass_kg'],
   f"FEA P2 h5: fall 6 BW toe p99.9 {foot['cases']['fall_6BW_toe']['vm_p999']:.0f} MPa SF {foot['cases']['fall_6BW_toe']['SF_yield_p999']} (max {foot['cases']['fall_6BW_toe']['vm_max']:.0f} MPa at the rigid sensor-ring edge, SF {foot['cases']['fall_6BW_toe']['SF_yield_max']}, mesh-dependent); carry Goodman {foot['cases']['op_carry_toe_plus_screw']['goodman_SF']}"),
 ('thigh','thigh clamp (hip_pitch bodies, axial eye form)',cl['mass_kg'],f"FEA P2 h2.5: 4542 N per screw max {cl['cases']['screw_max_push']['vm_max']:.0f} MPa SF {cl['cases']['screw_max_push']['SF_yield_max']}; walking 0.52× fully reversed SF {159/(0.52*cl['cases']['screw_max_push']['vm_max']):.2f}"),
 ('foot','ankle rod-end lugs on instep (2)',0.042,'Legs line (LINKAGE_TABLE); counted here once')]
tot=sum(r[2] for r in rows)
L=['# Legs r4 M2: structure + thigh clamp + instep lugs (per leg)','',"Baseline per R-015 M2: 4.85 parametric + 0.20 clamp [EST] + 0.084 lugs = 5.134 kg both legs; target ≤ 4.85 kg (−0.25 after absorbing the clamp).",'',
   '| zone | part | kg per leg | basis |','|---|---|---|---|']+[f'| {z} | {p} | {m:.3f} | {b} |' for z,p,m,b in rows]
L+=[f'| | **per leg** | **{tot:.3f}** | |',f'| | **both legs** | **{2*tot:.3f}** | target ≤ 4.85 → margin {4.85-2*tot:+.3f} kg |','',
    'Not in this line: CRBH 5013 bearing + clamp ring (Actuators), levers, pins, hubs, rod ends (Actuators LINKAGE_TABLE), clamp split-collar bolts (~0.01 [EST]), hip stop bumper (~0.01 [EST]).',
    f"FEA caveats: P2 tets on a ~1 GB box (half models, symmetry), foot h 6→5 mm p99.9 {foot6['cases']['fall_6BW_toe']['vm_p999']:.0f}→{foot['cases']['fall_6BW_toe']['vm_p999']:.0f} MPa (converging), peak at the rigid fixture edge grows with refinement (singular); tubes, clevis, tongue, fork and ring are hand/v3-scaled, not FEA. Converged runs + flange-modelled sensor in grokbuild/structure_fea.md."]
open(f'{R}/structure_m2.md','w').write('\n'.join(L)+'\n'); json.dump(dict(rows=[dict(zone=z,part=p,kg=m,basis=b) for z,p,m,b in rows],per_leg=tot,both=2*tot,ring_lug=lug),open(f'{R}/structure_m2.json','w'),indent=1)
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
r3rows=[('femur tube',r3m('femur tube 7075 Ø50')),('collars',r3m('femur collars ×2')+r3m('tibia collar')),('hip lug/ring',r3m('femur upper lug')),('clevis+tongue',r3m('knee clevis')+r3m('knee tongue (pin lug, lever removed)')),('tibia tube',r3m('tibia tube 7075 Ø45')),('fork',r3m('ankle fork')),('foot',r3m('foot plate + instep lever')),('thigh clamp',0.10),('instep lugs',0.042)]
r4m=[rows[0][2],rows[1][2]+rows[5][2],rows[2][2],rows[3][2]+rows[7][2],rows[4][2],rows[6][2],rows[8][2],rows[9][2],rows[10][2]]
fig,ax=plt.subplots(figsize=(8.5,3.6)); x=range(len(r3rows)); ax.bar([i-0.2 for i in x],[2*v for _,v in r3rows],0.4,label=f'R-015 baseline (r3 + 0.20 clamp [EST]) {2*sum(v for _,v in r3rows):.2f} kg')
ax.bar([i+0.2 for i in x],[2*v for v in r4m],0.4,label=f'r4 M2 design {2*tot:.2f} kg (target ≤ 4.85)'); ax.set_xticks(list(x)); ax.set_xticklabels([n for n,_ in r3rows],rotation=20,fontsize=8); ax.set_ylabel('kg, both legs')
ax.set_title(f"Legs r4 M2: foot FEA SF {foot['cases']['fall_6BW_toe']['SF_yield_p999']} (p99.9, fall 6 BW), clamp FEA SF {cl['cases']['screw_max_push']['SF_yield_max']}",fontsize=9); ax.legend(fontsize=8); fig.tight_layout()
fig.savefig(sys.argv[1] if len(sys.argv)>1 else f'{H}/plots/r4_m2.png',dpi=90); print('\n'.join(L[4:]))
