"""40 mm shoulder impact pad (R-042) - analytic estimate, RL Industrial Design. Same model as controls/fall/a44_side_fall.py:
constant-force crush over s = 0.7*t + 3 mm (v3 fall_model), F = E_shoulder / s, bearing moment = F * 0.060 m."""
import json,os
H=os.path.dirname(os.path.abspath(__file__))
m,g,zc=66.21,9.81,0.98; E=m*g*zc            # J, R-039 credible mass
E_cap=220.0                                  # J max shoulder energy with A44 strategy (A44_side_fall.md)
s30=0.7*30+3; s40=0.7*40+3                   # mm
F30=E_cap/(s30/1e3); F40=E_cap/(s40/1e3)
red=1-s30/s40
# foam: EPP 80 g/L [EST plateau 0.65 MPa @ 25-60 % strain; verify vs ARPRO/Neopolen TDS - Materials Q]
FOAMS={'EPP 45 g/L':(45,0.30),'EPP 60 g/L':(60,0.45),'EPP 80 g/L':(80,0.65),'EVA 100 (closed cell)':(100,0.55),'PORON-class PU 240':(240,0.50)}
rows={}
for k,(rho,sig) in FOAMS.items():
    A=F40/(sig*1e6)                          # m2 needed for plateau force = F40
    rows[k]=dict(rho=rho,plateau_MPa=sig,area_cm2=round(A*1e4),kg_per_pad=round(A*0.040*rho,4))
pick='EPP 80 g/L'; foam=rows[pick]['kg_per_pad']
sleeve=0.30*0.030                            # kg: TPU-coated nylon sleeve 0.03 m2 @ 0.30 kg/m2 [EST]
carrier=0.006                                # kg: 2x M4 moulded-in inserts + 25 mm hook strap anchor [EST]
pad=foam+sleeve+carrier; pair=2*pad
out=dict(P='P-051 (proposed; R-042 assigns none)',E_total_J=round(E),E_shoulder_cap_J=E_cap,s_30mm=s30,s_40mm=s40,
 F_30mm_kN=round(F30/1e3,2),F_40mm_kN=round(F40/1e3,2),M_bearing_30_Nm=round(F30*0.06),M_bearing_40_Nm=round(F40*0.06),
 force_reduction=round(red,3),foams=rows,pick=pick,kg_foam=round(foam,4),kg_sleeve=sleeve,kg_carrier=carrier,
 kg_per_side=round(pad,4),kg_pair=round(pair,3),cap_pair=0.10,pass_cap=pair<=0.10,measured=False)
json.dump(out,open(os.path.join(H,'shoulder_pad.json'),'w'),indent=1); print(json.dumps(out,indent=1))
