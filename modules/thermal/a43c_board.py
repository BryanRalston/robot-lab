# A43C rev R-047: hand board + 6 DCX22 flexors in forearm, 35 C, ladder derate transient. RL Thermal.
import json
R25=3.69;R=lambda T:R25*(234.5+T)/259.5
import sys
RM=float(sys.argv[1]) if len(sys.argv)>1 else 8.0
Rth1,Rm,Cw,Ch=7.0,RM,20/7,528/16       # winding-housing, housing-shell (loose, A43B worst), caps J/K
Cs=0.25*900+6*0.149*500                 # shell + drives J/K
Pb,Rbs=4.3,2.0                          # board W (worst), board->shell K/W [EST]
Rds,thJA=0.30,45.0                      # DRV8874 HS+LS hot ohm [EST from ~0.2 typ], theta to board K/W [EST]
def ladder(Ts,state,L):
  # L list of (on_thresh, I); hysteresis 5 K
  lvl=state
  while lvl+1<len(L) and Ts>=L[lvl+1][0]: lvl+=1
  while lvl>0 and Ts<L[lvl][0]-5: lvl-=1
  return lvl
def sim(Rs,L=None,I0=0.952,t_end=4*3600):
  Ta=35;Tw=Th=Ts=Ta;lvl=0;dt=0.05;t=0;Tsmax=Twmax=0;hist=[];lv=set()
  while t<t_end:
    if L: lvl=ladder(Ts,lvl,L); I=min(I0,L[lvl][1])
    else: I=I0
    lv.add(lvl);P=I*I*R(Tw)
    q1=(Tw-Th)/Rth1;q2=(Th-Ts)/Rm
    Tw+=dt*(P-q1)/Cw;Th+=dt*(q1-q2)/Ch
    Ts+=dt*(6*q2+Pb-(Ts-Ta)/Rs)/Cs
    t+=dt
    if t>t_end-1800: Tsmax=max(Tsmax,Ts);Twmax=max(Twmax,Tw)
  Tb=Ts+Pb*Rbs;Tj=Tb+I*I*Rds*thJA
  return dict(shell_end=round(Ts,1),shell_max_last30min=round(Tsmax,1),wind_max=round(Twmax,1),I_end=I,
              board=round(Tb,1),Tj_hbridge=round(Tsmax+Pb*Rbs+I0**2*Rds*thJA,1),levels=sorted(lv))
L0=[(-99,0.84),(60,0.70),(80,0.5),(90,0.0)]
L1=[(-99,0.84),(55,0.70),(70,0.5),(80,0.35),(88,0.0)]
out={}
for nm,Rs in (('walk',1.4),('still',2.4)):
  out[nm]={'no_derate':sim(Rs),'ladder_tuned':sim(Rs,L1),'ladder_tuned_I0.88_fric1.2':sim(Rs,L1,I0=0.88)}
  for k in out[nm]: out[nm][k]['Tj_MCU_RthJB10']=round(out[nm][k]['board']+0.9*10,1)
print(json.dumps(out,indent=1));json.dump(out,open(f'results/a43c_board_4p3W_Rm{RM}.json','w'),indent=1)
