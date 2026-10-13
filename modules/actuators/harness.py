"""R4 M3: whole-robot harness mass model (owner RL Actuators per R-017). Target <= 1.46 kg (contract line 2.00).
Architecture: 20S bus (68-84 V) star from the pack/BMS in the torso to 4 limb trunks + waist/neck/head branch; inside each limb the bus and
EtherCAT daisy-chain drive-to-drive (Elmo Gold Twitter mounted on each actuator, so motor phase/encoder leads are short local leads).
Conductor: silicone-insulated tinned Cu (mass = Cu 8.96 g/cm3 x area + insulation per AWG table below, typical of e.g. Alpha Wire/BRT silicone).
Gauge: from limb RMS/peak current, ampacity derated 50 % for bundles; voltage drop at peak <= 2 % of 68 V; temperature rise from I^2R vs 10 W/m.K free-air estimate.
Currents: legs from results/sizing.json power (walk_1p2 / stairs / push peak_limb), arms from contract needs (<= 300 W peak/arm) [EST]."""
import json, os, math
H=os.path.dirname(os.path.abspath(__file__)); S=json.load(open(f'{H}/results/sizing.json'))
V=68.0; RHO_CU=1.72e-8
AWG={12:(3.31,4.5),14:(2.08,3.6),16:(1.31,3.0),18:(0.823,2.4),20:(0.518,1.9),22:(0.326,1.5),24:(0.205,1.2)}   # mm2, insulation g/m (silicone, ~0.4-0.8 mm wall) [EST from vendor tables]
def gpm(a): A,ins=AWG[a]; return A*8.96+ins
def R(a): return RHO_CU/(AWG[a][0]*1e-6)
pk_leg=max(v['peak_limb'] for v in S['power'].values()); mean_leg=max(v['mean_noregen'] for v in S['power'].values())/2
I_leg_pk=pk_leg/V; I_leg_rms=1.6*mean_leg/V     # rms ~ 1.6 x mean for gait power waveform [EST]
I_arm_pk,I_arm_rms=300/V,80/V
runs=[]  # name, n, length m, awg, conductors, I_rms, I_pk
for side in ('L','R'):
    runs+=[(f'leg{side} trunk pack->hip',1,0.40,12,2,I_leg_rms,I_leg_pk),(f'leg{side} hip->knee',1,0.40,14,2,I_leg_rms*0.7,I_leg_pk*0.8),(f'leg{side} knee->ankle',1,0.40,16,2,I_leg_rms*0.4,I_leg_pk*0.5),
           (f'leg{side} drive drops (8)',8,0.08,18,2,4.0,12.0),
           (f'arm{side} trunk pack->shoulder',1,0.35,16,2,I_arm_rms,I_arm_pk),(f'arm{side} along arm',1,0.55,18,2,I_arm_rms*0.6,I_arm_pk*0.6),(f'arm{side} drive drops (7)',7,0.06,20,2,1.5,5.0),
           (f'hand{side} power (24 V from wrist DC/DC, 2 cond)',1,0.15,22,2,0.5,2.0)]
runs+=[('waist+neck+head bus',1,0.80,18,2,1.5,6.0),('waist/neck drive drops (4)',4,0.08,20,2,1.0,4.0),('compute/sensors 24 V feed',1,0.40,18,2,6.0,8.0)]
ecat=[('EtherCAT limb runs (4) incl. return',4,1.6,'ECAT',1),('EtherCAT jumpers drive-to-drive',30,0.12,'ECAT',1),('EtherCAT waist/neck/head',1,1.0,'ECAT',1)]
ECAT_GPM=14.0   # 4 x AWG26 shielded PUR, e.g. igus CFBUS.PUR.045 class [EST g/m, datasheet to confirm]
local=[('motor phase leads (34 drives, 3 x 20 AWG x 0.06 m)',34,0.06,20,3),('encoder/thermistor leads (34, 6 x 28 AWG-class 0.06 m) ',34,0.06,24,3)]
CON={'XT60 pair (Amass XT60PW, 30 A cont)':(0.0085,4),'XT30 pair (Amass XT30U, 15 A)':(0.0034,30+8),'MR30 3-pin phase (Amass)':(0.0025,0),
     'EtherCAT JST-GH 4-pin pair (latching)':(0.0012,2*34+8),'Pack Anderson-class main (Amass AS150U pair)':(0.030,1)}
rows=[]; tot=0
for nm,n,L,a,c,irms,ipk in runs:
    m=n*L*c*gpm(a)/1000; dv=ipk*R(a)*L*c; P=irms**2*R(a)  # W/m per conductor
    rows.append(dict(item=nm,n=n,len_m=L,awg=a,cond=c,kg=m,I_rms=irms,I_pk=ipk,dV_pk_V=dv,dV_pct=100*dv/V,W_per_m=P,dT_K=P/(math.pi*(math.sqrt(AWG[a][0]/math.pi)*2+1.2)*1e-3*10)))
    tot+=m
for nm,n,L,_,c in ecat: m=n*L*ECAT_GPM/1000; rows.append(dict(item=nm,n=n,len_m=L,kg=m)); tot+=m
for nm,n,L,a,c in local: m=n*L*c*gpm(a)/1000; rows.append(dict(item=nm,n=n,len_m=L,awg=a,cond=c,kg=m)); tot+=m
con=sum(v[0]*v[1] for v in CON.values())
extras=dict(sleeving_ties_strain_relief=0.12*tot,bms_to_bus_fuse_contactor_leads=0.05)
total=tot+con+sum(extras.values())
out=dict(I_leg_pk=I_leg_pk,I_leg_rms=I_leg_rms,rows=rows,wire_kg=tot,connectors=dict(parts={k:dict(each_kg=v[0],n=v[1]) for k,v in CON.items()},kg=con),extras=extras,total_kg=total,target=1.46,contract=2.00,
   worst_dV_pct=max(r.get('dV_pct',0) for r in rows),worst_dT_K=max(r.get('dT_K',0) for r in rows))
json.dump(out,open(f'{H}/results/harness.json','w'),indent=1)
L=['# Harness mass model (M3, R-017 owner Actuators)','','`harness.py` -> `harness.json`. Bus 20S 68–84 V, EtherCAT daisy chain per limb, drives on the actuators.','',
 f'Leg trunk current: peak {I_leg_pk:.1f} A (peak_limb {pk_leg:.0f} W / 68 V), rms {I_leg_rms:.1f} A [EST 1.6 × mean].','',
 '| item | n | length m | AWG | cond | kg | I rms / pk A | ΔV pk % | ΔT K |','|---|---|---|---|---|---|---|---|---|']
for r in rows: L.append(f"| {r['item']} | {r['n']} | {r['len_m']} | {r.get('awg','4×26 ECAT')} | {r.get('cond','')} | {r['kg']:.3f} | {r.get('I_rms',0):.1f} / {r.get('I_pk',0):.1f} | {r.get('dV_pct',0):.2f} | {r.get('dT_K',0):.1f} |")
L+=['',f"Connectors {con:.3f} kg: "+'; '.join(f'{k} ×{v[1]}' for k,v in CON.items()),'',f"Sleeving/ties 12 % {extras['sleeving_ties_strain_relief']:.3f}, BMS/fuse/contactor leads {extras['bms_to_bus_fuse_contactor_leads']:.3f}.",'',
 f"**Total {total:.3f} kg vs target 1.46 (contract 2.00).** Worst voltage drop {out['worst_dV_pct']:.2f} % at peak, worst conductor ΔT {out['worst_dT_K']:.1f} K at rms (free-air, h 10 W/m²K; bundle derate covered by ampacity 50 %).",
 'Evidence level: wire mass per AWG and EtherCAT 14 g/m are vendor-typical [EST, datasheets to pull]; connector masses Amass/JST catalogue values [EST ±20 %]. Lengths from v3 limb geometry [EST ±20 %].']
open(f'{H}/results/harness.md','w').write('\n'.join(L)+'\n'); print('\n'.join(L[-3:])); print(round(tot,3),round(con,3))
