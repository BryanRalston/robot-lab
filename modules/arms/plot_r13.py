import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt, matplotlib.patches as P, json, os, numpy as np
H=os.path.dirname(os.path.abspath(__file__)); d=json.load(open(f'{H}/pad_r13.json')); c=json.load(open(f'{H}/clash_r13.json'))
f,ax=plt.subplots(1,3,figsize=(18,6.5)); f.suptitle('2026-10-21 RL Arms R13 (R-120): 7075-T6 machined pad stand-off + CRBH 7013 A roll housing',fontsize=13)
a=ax[0]; a.set_title('Stand-off, side view (Y lateral, Z up; roll axis = origin)')
a.add_patch(P.Rectangle((0,-35),5,70,fc='#bbb',ec='k')); a.text(-2,26,'flange OD70/ID44 x5\n8xM4 PCD62 + 2x Ø4 dowel',fontsize=8)
a.add_patch(P.Polygon([(5,-15),(23,-51),(23,11),(5,15)],fc='#ddd',ec='k')); a.text(7,-2,'2 ribs\n5x30',fontsize=8)
a.add_patch(P.Rectangle((23,-51),4,62,fc='#999',ec='k')); a.text(20,14,'face plate 62x62x4\n4xM4 on ±24 sq',fontsize=8)
a.add_patch(P.Rectangle((27,-47.4),75.3,54.8,fc='#fd8',ec='k',alpha=.7)); a.text(45,-22,'R10 core 54.8 sq x75.3\n(ID, tray 0.5)',fontsize=8)
a.axhline(0,ls='--',c='b'); a.axhline(-20,ls=':',c='r'); a.text(70,-18,'pad centre Z -20',color='r',fontsize=8); a.text(60,2,'roll axis',color='b',fontsize=8)
a.annotate('',(0,-60),(102.3,-60),arrowprops=dict(arrowstyle='<->')); a.text(40,-66,'contact Y 102.3',fontsize=8)
a.set_xlim(-10,115); a.set_ylim(-75,40); a.set_aspect('equal'); a.grid(alpha=.3); a.set_xlabel('Y mm'); a.set_ylabel('Z mm')
a=ax[1]; a.set_title('Roll housing section: CRBH 6013 -> 7013 A')
for D,col,l in ((108,'#9cf','seat flange OD108 / bore Ø100 H7, 15 wide'),(100,'#f99','CRBH 7013 A 70x100x13'),(70,'#cfc','output hub Ø70 / Ø54 (8xM4x8 tapped PCD62)')):
    a.add_patch(P.Circle((0,0),D/2,fc=col,ec='k',label=l))
a.add_patch(P.Circle((0,0),27,fc='w',ec='k')); a.add_patch(P.Circle((0,0),45,fc='none',ec='k',ls='--',label='old OD90 (6013)'))
for t in np.linspace(0,2*np.pi,9)[:-1]: a.add_patch(P.Circle((31*np.cos(t),31*np.sin(t)),2.2,fc='k'))
a.set_xlim(-65,65); a.set_ylim(-65,65); a.set_aspect('equal'); a.legend(fontsize=7,loc='lower left')
a=ax[2]; a.axis('off'); k=d['check']; m=d['mass']; t=d['tolerance']; ab=c['abduction_sweep_worst']
txt=f"""Checks [CALC, hand]
s0 (7013, 15°, no mu credit) e0/5/10: {k['s0_7013']['e0']}/{k['s0_7013']['e5']}/{k['s0_7013']['e10']}
Mx {k['Mx_raw_Nm']} N·m, CSG-25 SF at fault {k['CSG25_SF_fault']}
Flange: ID 6xM4 PCD50 SF {d['bolts']['ID_6xM4_PCD50_EST']['SF']} -> 8xM4 PCD62 + dowels SF {d['bolts']['R13_8xM4_PCD62']['SF']}
Ribs strong axis: {d['ribs']['sigma_sum_MPa']} MPa, SF {d['ribs']['SF']} (weak axis -> FEA)
Tolerance e: worst {t['worst_case_mm']} / RSS {t['rss_mm']} mm vs 5.0

Clash (light model, >=10 mm gate)
tuck B: torso {c['tuck_B']['torso']} mm, head {c['tuck_B']['head']} mm
head/neck min over abduction: {ab['head']['head']} mm  (no head limit from pad)
roll 135 soft limit: torso >= {c['head_limit']['0']['at135']['torso']} mm
overhead pitch<=-150 & roll>=170: torso box {ab['torso']['torso']} mm (marginal, crude box)
elbow fold (4224 poses): min {c['elbow_fold_worst']['forearm_hand']} mm
7013 housing: needs pad x-range outboard of housing face, 3 mm [EST, CAD]

Mass pair [CALC]: stand-off net {m['stand_off_net_pair_vs_boss_booked']}, housing {m['housing_growth_pair']},
bearing {m['bearing_pair_cited']} (cited) = {m['R13_total_pair']} vs booked 0.212 ({m['delta_vs_booked_pair']:+})
Measured masses: G5"""
a.text(0,1,txt,va='top',family='monospace',fontsize=8.5)
plt.tight_layout(); out=os.path.join(H,'../../media/progress/2026-10-21_arms_R13_standoff_7013.png'); plt.savefig(out,dpi=110); plt.savefig(f'{H}/R13_standoff_7013.png',dpi=110); print(out)
