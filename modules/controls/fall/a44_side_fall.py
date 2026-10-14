"""A44 side-fall shoulder_pitch bearing load. Same energy model as v3/analysis/v3.py fall_model()
(constant-force pad crush, F = share*E/s, s = 0.7*pad + 3 mm, M = F*0.06) so numbers are comparable to the 690 N*m baseline.
Bearing check: IKO P0r = Fr + 2M/Dpw + 0.44Fa (CAT-57151 eq. 2), CRBH 7013 A C0 = 27.7 kN (CAT-57151), Dpw = (d+D)/2 = 85 mm [EST]."""
import json
G=9.81; PAD=30; ARM=0.06; C0=27700; DPW=0.085
s=(PAD*0.7+3)/1000
def case(name,m,zc,share,note):
    E=m*G*zc; F=share*E/s; M=F*ARM
    fs_ax=C0/(2*M/DPW+0.44*F); fs_rad=C0/(F+2*M/DPW)
    return dict(case=name,m=m,zc=zc,share=share,E_sh_J=share*E,F_N=round(F),M_Nm=round(M,1),fs_axial=round(fs_ax,2),fs_radial=round(fs_rad,2),pass_550=M<=550,note=note)
M0=613.3113633879221/(G*0.98)   # mass implied by v3.json fall.E_J
R=[case('baseline v3.json',M0,0.98,0.45,'reproduces 690 N*m'),
   case('baseline @ R-039 mass',66.21,0.98,0.45,'same fall, current credible mass'),
   case('S1 crouch only',66.21,0.78,0.45,'knee drop of 0.20 m before impact [EST achievable]'),
   case('S2 hip-first only',66.21,0.98,0.35,'tuck+lean so hip pad takes 65 % [EST]'),
   case('S3 crouch 0.15 + hip-first 0.40 (proposed)',66.21,0.83,0.40,'combined [EST]'),
   case('S3 sensitivity: share 0.45 (hip-first fails)',66.21,0.83,0.45,''),
   case('S3 sensitivity: crouch only 0.08 m',66.21,0.90,0.40,'')]
req=lambda m,zc: 550/ARM*s/(m*G*zc)
out=dict(cases=R,share_max_for_550_no_crouch=round(req(66.21,0.98),3),share_max_for_550_crouch_015=round(req(66.21,0.83),3),
 M_pure_moment_fs1_Nm=round(C0*DPW/2))
json.dump(out,open('a44_results.json','w'),indent=1); print(json.dumps(out,indent=1))
