# A37 break requirement + A43B grip hold. Hand calcs, RL Thermal 2026-10-14.
import math, json
out={}
# ---- A37 ----
k={'G10':0.29,'PEI':0.20}
def Rsleeve(kk,od,id_=12,L=16e-3): return math.log(od/id_)/(2*math.pi*kk*L)
def Rface(kk,t,od,id_): return t/(kk*math.pi/4*((od*1e-3)**2-(id_*1e-3)**2))
cases={'A35 h15 vented':50.0,'R1 open h12':62.6,'case at 130C trip':73.9}
Rcol=[3,8,14]
a37={}
for nm,dT in cases.items():
  a37[nm]={'Rb_req_for_Rcol':{rc:round(rc*(dT/25-1),1) for rc in Rcol}}
  for Rb in (10,4.6,20):
    a37[nm][f'Rb{Rb}']={rc:{'Q_W':round(dT/(Rb+rc),2),'collar_C':round(35+dT*rc/(Rb+rc),1)} for rc in Rcol}
a37['R_G10_sleeve_OD16']=round(Rsleeve(.29,16),1)
a37['R_PEI_sleeve_OD16']=round(Rsleeve(.20,16),1)
a37['R_G10_1mm_washer_face_OD20_ID12_each']=round(Rface(.29,1e-3,20,12),1)
fw=Rface(.29,1e-3,20,12)/2; a37['R_A37_as_drawn_par']=round(1/(1/Rsleeve(.29,16)+1/fw),1)
# options reaching >=20 total
for m in ('G10','PEI'):
  for od in (16,18,20,22):
    for t in (1,2,3):
      rs=Rsleeve(k[m],od); rf=Rface(k[m],t*1e-3,20,12)/2
      a37.setdefault('opts',[]).append((m,od,t,round(rs,1),round(rf,1),round(1/(1/rs+1/rf),1)))
out['A37']=a37
# ---- A43B ----
R25,Rth1,Rth2,tw,tm,Tmax,Inom=3.69,7.0,16.0,20.0,528.0,125.0,0.869
R=lambda T:R25*(234.5+T)/259.5
def steady(I,Ta,Rext_shared=0.0,n=6,Rmount=None):
  Tw=Ta+50
  for _ in range(200):
    P=I*I*R(Tw); Rh=Rth2 if Rmount is None else Rmount
    Tw=Ta+n*P*Rext_shared+P*(Rth1+Rh)
    if Tw>400: return float('inf'),P
  return Tw,P
def Imax(Ta,**kw):
  lo,hi=0,2
  for _ in range(60):
    m=(lo+hi)/2; T,_=steady(m,Ta,**kw); lo,hi=(m,hi) if T<Tmax else (lo,m)
  return lo
def t_limit(I,Ta,Rs=0.0,n=6,Rh=Rth2,Cs=None):
  # 2-node motor (winding, housing) + shared forearm node; Euler
  Cw=tw/Rth1; Ch=tm/Rh; Cs=Cs or 0
  Tw=Th=Tsh=Ta; t=0; dt=0.05
  while t<7200:
    P=I*I*R(Tw)
    qwh=(Tw-Th)/Rth1; qhs=(Th-Tsh)/Rh
    Tw+=dt*(P-qwh)/Cw; Th+=dt*(qwh-qhs)/Ch
    if Rs: Tsh+=dt*(n*qhs-(Tsh-Ta)/Rs)/Cs
    t+=dt
    if Tw>=Tmax: return round(t)
  return None
I=0.952
A=steady(I,40); out['free_air_single']={'Tw':round(A[0],1),'P':round(A[1],2),'Imax':round(Imax(40),3),'t_lim_s':t_limit(I,40)}
# forearm: shell OD70 x 270 Al, h 12 -> Rs; motors clamped Rmount 4 K/W [EST]
As=math.pi*0.07*0.27; Rs=1/(12*As); Cs=0.25*900+6*0.066*500  # shell ~0.25 kg Al + motors' share
for Rm in (4.0,8.0):
  T,P=steady(I,40,Rext_shared=Rs,Rmount=Rm)
  out[f'forearm_Rm{Rm}']={'Rs':round(Rs,2),'Tw':T if T==float('inf') else round(T,1),'P_each':round(P,2),
    'Imax_6':round(Imax(40,Rext_shared=Rs,Rmount=Rm),3),'t_lim_s':t_limit(I,40,Rs,6,Rm,Cs)}
# duty: allowed RMS current = Imax; hold fraction at 0.952 A with 0 between
for kname in ('forearm_Rm4.0','forearm_Rm8.0'):
  out[kname]['hold_duty_at_0.952A']=round((out[kname]['Imax_6']/I)**2,2)
print(json.dumps(out,indent=1,default=str))
json.dump(out,open('/workspace/rl-thermal-wt/modules/thermal/results/a37_a43b.json','w'),indent=1,default=str)
