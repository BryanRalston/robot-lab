"""Round 3b: hip_pitch pivot bearing (Actuators-owned from R3b). IKO CRBH catalogue (datasheets/iko_crb_catalog.pdf, CRBH table + eq. (1)):
P = X(Fr + 2M/Dpw) + Y Fa (X 1, Y 0.45 if Fa/(Fr+2M/Dpw) <= 1.5), P0 = Fr + 2M/Dpw + 0.44 Fa, Dpw ~ (d+D)/2, L10 = (C/P)^(10/3) 1e6 rev.
Loads (per leg): screw net force at actuator max 2 x 4542 N; hip contact 1.5 x BW (65 kg); moments from hip_roll / hip_yaw needs (R-011, 180 / 66 N·m incl. 1.5 margin);
fault: one screw at max (4542 N x 69 mm offset adds to M). Life: walking peak (need/1.5) with cubic-mean factor 0.65, 1/3 rev per stride, 1 stride/s."""
import json, os, numpy as np
H=os.path.dirname(os.path.abspath(__file__))
CAT={'CRBH 4010 A':(40,65,10,0.15,8610,10600),'CRBH 4510 A':(45,70,10,0.16,8860,11300),'CRBH 5013 A':(50,80,13,0.29,17300,20900),'CRBH 6013 A':(60,90,13,0.33,18800,24300)}
BW=65*9.81; Fs=454.2/0.050/2; Fa=0.3*BW
M_need=np.hypot(180,66); M_walk=M_need/1.5
out={}
for k,(d,D,B,m,C,C0) in CAT.items():
    dp=(d+D)/2/1000
    P0_max=2*Fs+1.5*BW+2*M_need/dp+0.44*Fa
    P0_fault=Fs+1.5*BW+2*(M_need+Fs*0.069)/dp+0.44*Fa
    Pw=(2*Fs*0.52+1.5*BW+2*M_walk/dp)*0.65+0.45*Fa
    L=(C/Pw)**(10/3)*1e6; h=L/(1/3)/3600
    out[k]=dict(d=d,D=D,B=B,mass=m,C=C,C0=C0,fs_max=C0/P0_max,fs_fault=C0/P0_fault,P_walk_N=Pw,L10_h_walking=h)
    print(k,{a:round(b,2) for a,b in out[k].items()})
sel='CRBH 5013 A'
seat=dict(inner_clamp_ring_7075=0.012,fasteners_6xM4=0.012)
out['selected']=dict(part=sel,why='lightest with fs>=1.3 at actuator max + design moments (4010/4510 fs<0.8); fs~1 only in the one-screw fault case; L10 >> 20 000 h',
   mass_bearing=CAT[sel][3],seat_extra=seat,mass_line=CAT[sel][3]+sum(seat.values()),note='inner ring on lever spigot (lever mass includes spigot), outer ring in femur tongue: Legs pivot bore ø32 -> ø80 H7 seat, tongue 25 >= B 13')
json.dump(out,open(f'{H}/results/hp_bearing.json','w'),indent=1)
