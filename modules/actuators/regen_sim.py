"""RL Actuators round 2: time-domain DC-bus energy sim over the Legs walk_1p2 gait (R-002 evidence).
Per joint: joint torque/speed (Legs gait ID) -> transmission (direction-dependent efficiency) -> motor (TBM2G Km/Kt hot, datasheet)
-> drive (Gold Twitter, conduction + switching loss) -> shared 20S DC bus -> battery (Molicel P45B: DC IR 15 mOhm, max charge 13.5 A/cell,
datasheets/molicel_p45b.pdf) with BMS regen-charge limit and a brake chopper for the excess (clamp 90 V).
Run: python3 regen_sim.py -> results/regen_sim.json, results/regen_sim.md"""
import json, math, os, numpy as np
H=os.path.dirname(os.path.abspath(__file__)); R=os.path.join(H,'../..')
S=json.load(open(f'{H}/results/sizing.json')); SEL=S['sel']
LEG=['hip_yaw','hip_roll','hip_pitch','knee','ankle_pitch','ankle_roll']
d=np.load(f'{R}/modules/legs/results/walk_1p2.npz'); va=d['va']; t=d['t']; dt=np.gradient(t)
# Drive loss model from the Gold Twitter R70/100 datasheet: >99 % at 5.6 kW rated (49.5 A rms, 85 V nominal) -> <= 56 W loss at rated.
# Split [EST] half conduction (I^2 R_eq) and half switching (proportional to |I|): R_eq = 28/49.5^2, k_sw = 28/49.5 W/A
R_EQ=28/49.5**2; K_SW=28/49.5
# Battery: 20S5P P45B. OCV nominal 3.6 V/cell (mid-SOC [EST flat]), DC IR 15 mOhm/cell -> pack 20*15/5 = 60 mOhm.
NS,NP=20,5; OCV=NS*float(os.environ.get("VCELL",3.6)); RPACK=NS*0.015/NP*float(os.environ.get("RX",1.0)); I_CH_CELL=13.5
I_CH_BMS=30.0      # decision D16: BMS regen-charge acceptance 30 A (6 A/cell, below 13.5 A/cell max and standard 4.5 A x ~1.3) [design limit]
ETA_COUL=0.99      # coulombic efficiency on charge [EST]
P_OTHER=120+40+26*3.3+8.0   # compute, sensors, drive idle (26 x 3.3 W), other-joint copper (CONTRACTS R1.3 basis)
def joint_elec(j,tau,w):
    s=SEL[j]; N,eta,n=s['ratio'],s['eta'],s['nmot']; Kmh=s['Km']/math.sqrt(1.4); Kt=s['Kt']
    wm=w*N; mot=tau*w>=0
    tm=np.where(mot,tau/(N*eta),tau*eta/N)/n        # per-motor torque
    Pm=n*tm*wm                                       # motor shaft power (neg = generating)
    I=np.abs(tm)/Kt                                  # per-motor rms phase current
    Pcu=n*(tm/Kmh)**2; Pdrv=n*(R_EQ*I**2+K_SW*I)
    return Pm+Pcu+Pdrv, Pcu, Pdrv, I
PJ={}; CU=0; DRV=0
for i,j in enumerate(LEG):
    for off in (0,6):
        k=va[i+off]; pe,cu,dr,I=joint_elec(j,d['TAU'][:,k].astype(float),d['V'][:,k].astype(float))
        PJ[f'{j}_{"L" if off==0 else "R"}']=pe; CU=CU+cu; DRV=DRV+dr
P_joints=np.array(list(PJ.values()))
def battery(Pbus,charge_limit_A):
    """Pbus: demand at the bus (W, + = from battery). Returns chemical power drawn from cells (W), brake power (W), bus V."""
    # solve I from P = (OCV - I R) I  (discharge) / P = (OCV + |I| R)|I| on charge (bus above OCV)
    I=np.where(Pbus>=0,(OCV-np.sqrt(np.maximum(OCV**2-4*RPACK*Pbus,0)))/(2*RPACK),0.0)
    Pch=np.minimum(-np.minimum(Pbus,0),charge_limit_A*(OCV+charge_limit_A*RPACK))     # power accepted on charge
    Ich=(-OCV+np.sqrt(OCV**2+4*RPACK*Pch))/(2*RPACK)
    Pbrake=-np.minimum(Pbus,0)-Pch
    Pchem=np.where(Pbus>=0,OCV*I,-OCV*Ich*ETA_COUL)
    Vbus=np.where(Pbus>=0,OCV-I*RPACK,OCV+Ich*RPACK)
    return Pchem,Pbrake,Vbus
CASES={}
# A: no regen credit at all: each drive dumps its own negative power (no netting, no charging)
PA=np.maximum(P_joints,0).sum(0)+P_OTHER; c,b,v=battery(PA,0); CASES['A_no_regen']=(c,b,v,PA)
# B: shared bus netting, no battery charging (chopper takes any net negative)
PB=P_joints.sum(0)+P_OTHER; c,b,v=battery(PB,0); CASES['B_bus_netting_only']=(c,b,v,PB)
# C: shared bus netting + battery charge acceptance up to the BMS limit, rest to chopper
c,b,v=battery(PB,I_CH_BMS); CASES['C_netting_plus_charge']=(c,b,v,PB)
WH=NS*NP*16.2; USE=0.9
OUT=dict(inputs=dict(gait='walk_1p2',duration_s=float(t[-1]-t[0]),R_eq=R_EQ,k_sw=K_SW,OCV=OCV,R_pack=RPACK,I_charge_BMS=I_CH_BMS,P_other=P_OTHER,
        selections={j:SEL[j]['label'] for j in LEG}),mean_W=dict(copper_legs=float(np.mean(CU)),drive_loss_legs=float(np.mean(DRV)),
        legs_positive_sum=float(np.mean(np.maximum(P_joints,0).sum(0))),legs_negative_sum=float(np.mean(np.minimum(P_joints,0).sum(0)))),cases={})
for k,(c,b,v,P) in CASES.items():
    Pm=float(np.sum(c*dt)/np.sum(dt)); ss=(t>=2.0)&(t<=7.0); Pss=float(np.sum((c*dt)[ss])/np.sum(dt[ss]))
    OUT['cases'][k]=dict(P_chem_mean=Pm,P_chem_steady_2to7s=Pss,runtime_h_steady=WH*USE/Pss,P_brake_mean=float(np.sum(b*dt)/np.sum(dt)),runtime_h=WH*USE/Pm,
        Vbus_min=float(v.min()),Vbus_max=float(v.max()),P_bus_min=float(P.min()),P_bus_max=float(P.max()),frac_time_bus_negative=float(np.mean(P<0)))
json.dump(OUT,open(f'{H}/results/regen_sim.json','w'),indent=1)
np.savez_compressed(f'{H}/results/regen_sim_trace.npz',t=t,PA=CASES['A_no_regen'][3],PB=CASES['B_bus_netting_only'][3],chemC=CASES['C_netting_plus_charge'][0],brakeC=CASES['C_netting_plus_charge'][1],V=CASES['C_netting_plus_charge'][2])
print(json.dumps(OUT['mean_W'],indent=0)); [print(k,{a:round(b,2) for a,b in v.items()}) for k,v in OUT['cases'].items()]
