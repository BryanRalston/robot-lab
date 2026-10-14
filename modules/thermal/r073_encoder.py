# R-073 ENX22 encoder-end temperature on DCX22 flexors, a43c_board model (4.3 W board). RL Thermal hand calc.
# Encoder end: Te = Th + f*(Tw-Th) + Pe*Re  (rear flange/bearing picks up fraction f of the winding-housing drop) [EST f 0.3, Pe 0.15 W, Re 15 K/W]
# Clamped-encoder fix: encoder end tied to shell, Te = Ts + 0.5*(Th-Ts) + Pe*Re
import json
R25=3.69;R=lambda T:R25*(234.5+T)/259.5
Rth1,Cw,Ch=7.0,20/7,528/16; Cs=0.25*900+6*0.149*500; Pb=4.3; f,Pe,Re=0.3,0.15,15
def ladder(Ts,l,L):
  while l+1<len(L) and Ts>=L[l+1][0]: l+=1
  while l>0 and Ts<L[l][0]-5: l-=1
  return l
def sim(Rs,Rm,L,I0=0.952,t_end=4*3600):
  Tw=Th=Ts=35.;l=0;dt=0.05;t=0;pk=dict(Te=0,Te_cl=0,Tw=0,Ts=0);Is=[]
  while t<t_end:
    l=ladder(Ts,l,L);I=min(I0,L[l][1]);P=I*I*R(Tw)
    q1=(Tw-Th)/Rth1;q2=(Th-Ts)/Rm
    Tw+=dt*(P-q1)/Cw;Th+=dt*(q1-q2)/Ch;Ts+=dt*(6*q2+Pb-(Ts-35)/Rs)/Cs;t+=dt
    Te=Th+f*(Tw-Th)+Pe*Re; Tec=Ts+0.5*(Th-Ts)+Pe*Re
    for k,v in (('Te',Te),('Te_cl',Tec),('Tw',Tw),('Ts',Ts)): pk[k]=max(pk[k],v)
    if t>t_end-1800: Is.append(I)
  return {k:round(v,1) for k,v in pk.items()}|{'I_sust':min(Is)}
Ls={'adopted 55/70/80/88':[(-99,.84),(55,.70),(70,.5),(80,.35),(88,0)],
    'tight 50/60/70/80':[(-99,.80),(50,.70),(60,.55),(70,.40),(80,0)]}
out={}
for lad,L in Ls.items():
  for mnt,Rm in (('clamped',4.0),('loose',8.0)):
    for env,Rs in (('walk/carry',1.4),('still',2.4)):
      out[f'{lad}|{mnt}|{env}']=sim(Rs,Rm,L)
# tip force ~ current (A42: 30 N at 0.952 A friction 1.3; 0.88 A at 1.2)
for k,v in out.items(): v['grip_N_fric1.3']=round(30*v['I_sust']/0.952,1); v['grip_N_fric1.2']=round(30*v['I_sust']/0.88,1)
print(json.dumps(out,indent=1)); json.dump(out,open('results/r073_encoder.json','w'),indent=1)
