"""A6: hip_pitch hard-stop bumper at -105 deg (toggle -114.5 deg => overtravel budget 9.5 deg). Hand sizing; PU properties are [EST] (no datasheet in repo).
Inertia: MuJoCo joint-space diagonal for l_hip_pitch at 66.5 kg (whole robot, floating base, incl. v3 armature 0.441) = 3.575 kg m^2."""
import json,math,os
H=os.path.dirname(os.path.abspath(__file__)); J=3.575
T_max=350.0; alpha=T_max/J   # decel available from the hip actuators (R1.2 avail)
w_gait=8.11
zone=w_gait**2/(2*alpha)     # rad needed to brake from the gait peak speed
r=80.0; d=25.0; Lb=12.0; strain=0.25; Epu=25.0   # mm, MPa [EST: Shore 90A PU compressive modulus ~20-30 MPa, unverified]
A=math.pi/4*d**2; x=strain*Lb; F=Epu*strain*A; Ecap=0.5*F*x/1000   # linear approx, J
w_lim=math.sqrt(2*Ecap/J)
theta_dyn=math.degrees(x/r); T_hold=150.0; F_hold=T_hold/(r/1000); x_hold=F_hold/(Epu*A)*Lb; theta_hold=math.degrees(x_hold/r)
theta_struct=math.degrees(0.16/50)   # lever pin deflection 0.16 mm at 50 mm (Actuators D33)
E_full=0.5*J*w_gait**2; F_full=None
mass_bumper=1.2e-3*A*Lb/1000 + 0.006 + 0.002   # PU 1.2 g/cm^3 + 7075 cup + 1 M4 [EST]
mass_bolts=0.016   # split-collar 2 x M6x30 10.9 per leg [EST]
out=dict(J_kgm2=J,decel_rad_s2=round(alpha,1),brake_zone_deg_from_8p11=round(math.degrees(zone),1),soft_limit_start_deg=round(-105+math.degrees(zone)+math.degrees(0.0),1),
         bumper=dict(material='PU Shore 90A [EST props]',d_mm=d,L_mm=Lb,radius_mm=r,max_compression_mm=x,F_at_25pct_N=round(F),energy_J=round(Ecap,2),k_N_per_mm=round(F/x)),
         w_contact_limit_rad_s=round(w_lim,2),energy_at_gait_peak_J=round(E_full,1),
         overtravel_deg=dict(bumper_full=round(theta_dyn,2),hold_150Nm=round(theta_hold,2),structure=round(theta_struct,2),total=round(theta_dyn+theta_struct,2),budget=9.5),
         mass_kg_per_leg=dict(bumper=round(mass_bumper,4),collar_bolts=mass_bolts,total=round(mass_bumper+mass_bolts,4)),allowance_both_legs=0.04)
out['mass_both_legs']=round(2*(mass_bumper+mass_bolts),3)
json.dump(out,open(f'{H}/results/r5/hip_stop.json','w'),indent=1); print(json.dumps(out,indent=0))
