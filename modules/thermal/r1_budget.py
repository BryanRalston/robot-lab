"""RL Thermal R1: whole-robot heat budget, 1.0 m/s walk + 20 kg carry. Reuses actuators/regen_core.py loss model.
Gait: legs/results/r4/carry_20kg_1p0.npz (gait-ID, R-014). Output: results/r1_budget.json. [EST] values are in the EST dict."""
import json, math, os, sys, numpy as np
H=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,f'{H}/../actuators'); sys.path.insert(0,f'{H}/../../v3/analysis')
import regen_core as RC, parts as P
GAIT=f'{H}/../legs/results/r4/carry_20kg_1p0.npz'
t,tau,om=RC.load(GAIT); W=RC.steady_window(t,om); dt=np.gradient(t); mean=lambda x:float(np.sum((x*dt)[W])/np.sum(dt[W]))
EST=dict(h_air=12.0, fins=2.0, rcu_hot=1.4, h_cover_in=4.0, h_cover_out=12.0, cover_area_x=1.5, f_covered=0.5,
         dcm_eta=0.92, rp40_load_W=12.0, thor_W=120.0, sensors_W=40.0, drive_idle_W=3.3, n_drives=26, bms_W=3.0, eta_rot=0.75)
def mot(kk):
    sj=RC.SEL[RC.LEG[kk%6]]; x=tau[:,kk]; w=om[:,kk]; m=x*w>=0
    return np.where(m,x/(sj['ratio']*sj['eta']),x*RC.ETA_BACK[RC.LEG[kk%6]]/sj['ratio']), w*sj['ratio']
rows=[]
for side in (0,6):
  for k,j in enumerate(RC.LEG):
    if j=='ankle_roll': continue          # shared differential pair, handled with ankle_pitch
    s=RC.SEL[j]; n=s['nmot']; Km=s['Km']/math.sqrt(EST['rcu_hot']); Kt=s['Kt']; fe=RC.FE[RC.MOTKEY[j]]
    tm,wm=mot(side+k)
    if j=='ankle_pitch':
        tr,wr=mot(side+5); pairs=[((tm+tr)/2,wm+wr),((tm-tr)/2,wm-wr)]
    else: pairs=[(tm/n,wm)]*n
    cu=fe_=drv=0
    for a,w in pairs:
        I=np.abs(a)/Kt; krpm=np.abs(w)*60/(2*math.pi)/1000
        cu+=mean((a/Km)**2); fe_+=mean(fe['a_W_per_krpm']*krpm+fe['b_W_per_krpm2']*krpm**2); drv+=mean(28/49.5**2*I**2+28/49.5*I)
    nm=len(pairs); area=s['area_cad']; Rha=1/(EST['h_air']*area*EST['fins']); Rwh=0.6*P.MOT[s['d']['motor']]['Rth']
    Ac=area*EST['fins']*EST['f_covered']; Au=area*EST['fins']*(1-EST['f_covered'])
    Rout=1/(EST['h_cover_out']*Ac*EST['cover_area_x']); Rcov=1/(EST['h_cover_in']*Ac)+Rout; Rha_c=1/(EST['h_air']*Au+1/Rcov)
    Q=cu+fe_; dTc=Q*Rha_c; qc=dTc/Rcov
    rows.append(dict(joint=('L_' if side==0 else 'R_')+j,motors=nm,copper_W=cu,iron_W=fe_,drive_cond_W=drv,
        dT_wind_open=cu/nm*Rwh+Q*Rha,dT_wind_cov=cu/nm*Rwh+dTc,dT_case_open=Q*Rha,dT_case_cov=dTc,
        dT_cover_skin=qc*Rout,dT_cavity=qc*Rout+qc/(EST['h_cover_in']*Ac)*0.5))
arm=[]
for j,mn,T,D,L in [('shoulder_pitch','TBM2G-07608',61,96,80),('elbow','TBM2G-05013',40,70,75)]:   # housing D x L mm [EST]
    m=P.MOT[mn]; Km=m['Km'][1]/math.sqrt(EST['rcu_hot']); tm=T/(100*EST['eta_rot']); cu=(tm/Km)**2; I=tm/m['Kt_hot'][1]
    area=(math.pi*D*L+2*math.pi/4*D**2)*1e-6; Rha=1/(EST['h_air']*area*EST['fins'])
    arm.append(dict(joint=j,per_arm_copper_W=cu,drive_cond_W=28/49.5**2*I**2+28/49.5*I,dT_wind=cu*(0.6*m['Rth']+Rha)))
S=lambda key,L:sum(r[key] for r in L)
arm_cu=2*S('per_arm_copper_W',arm); arm_drv=2*S('drive_cond_W',arm)
rc=RC.run(GAIT); Pbus=0.5*(rc['P_noregen']+rc['P_regen'])+arm_cu+arm_drv
I_pack=Pbus/72.0; Rp=20*0.015/5
B=dict(leg_copper=S('copper_W',rows),leg_iron=S('iron_W',rows),leg_drive_cond=S('drive_cond_W',rows),drive_idle=EST['n_drives']*EST['drive_idle_W'],
       arm_hold_copper=arm_cu,arm_drive_cond=arm_drv,neck_waist_other_copper=8.0,thor=EST['thor_W'],sensors=EST['sensors_W'],
       dcm_loss=(EST['thor_W']+EST['sensors_W'])*(1/EST['dcm_eta']-1),rp40_loss=EST['rp40_load_W']*(1/0.905-1),pack_I2R=I_pack**2*Rp,bms=EST['bms_W'])
heat=sum(B.values()); eod=I_pack**2*Rp*1.5
Ab=2*(.185*.22+.185*.144+.22*.144); Rb=1/(4.0*Ab); tau_b=Rb*8.75*1000
dTb=lambda Q:Q*Rb*(1-math.exp(-7200/tau_b))
Ath=2*(.13*.2+.13*.04+.2*.04)
out=dict(gait='legs/results/r4/carry_20kg_1p0.npz',window_s=rc['window_s'],EST=EST,legs=rows,arms=arm,budget=B,pack_I2R_eod=eod,total_heat_W=heat,P_bus_W=Pbus,I_pack_A=I_pack,
  pack=dict(R_K_per_W=Rb,tau_h=tau_b/3600,dT_2h=dTb(B['pack_I2R']+3),dT_2h_eod=dTb(eod+3)),
  thor=dict(dT_natural=EST['thor_W']/(5.0*Ath),fan_cfm_10K=EST['thor_W']/(1.2*1005*10)/0.000471947))
os.makedirs(f'{H}/results',exist_ok=True); json.dump(out,open(f'{H}/results/r1_budget.json','w'),indent=1)
print(round(heat,1),round(Pbus,1),{k:round(v,1) for k,v in B.items()}); [print(r['joint'],round(r['dT_wind_open'],1),round(r['dT_wind_cov'],1),round(r['dT_case_open'],1)) for r in rows]; print(arm,out['pack'],out['thor'])
