"""D104: hip_pitch inner screw body vs L/R adduction contact (Legs L94, f535463). Hand checks only (no OCC).
Geometry from legs/model_v4_l92.py P + cad_mass.linear_body('TBM2G-07613',bosses='none') + linkage_study hip_pitch_B geom."""
import json, math
H=__file__.rsplit('/',1)[0]
# --- body geometry (cad_mass.py: MOT 07613 = 76 x 23.09, WALL 2) ---
D=76+2*2+2; Lm=23.09+20; Dn=35+2*2+2; Ln=36+20; Lb=Lm+6+Ln          # 82, 43.09, 41, 56, 105.1
EYE_OFF=30.0                                                       # model_v4 screw_unit: body base 30 mm from the axial GE12 eye
hip_y,dy,femur_od,femur_x,tx=130,69,50,18,30
y_in=hip_y-dy                                                      # 61: inner screw axis
gap_femur=(hip_y-femur_od/2)-(y_in+D/2)                            # inner body OD to femur OD, same x band (body x -11..71, femur x -7..43)
# pin-to-pin length (thigh eye x30 z620 -> lever eye r50 clock 60 at hip z920)
ex,ez=50*math.sin(math.radians(60)),50*math.cos(math.radians(60))
L=math.hypot(ex-tx,(920+ez)-(920-300))
# --- (2) splay: body region rotates about the far (lever) eye; at the body d from the thigh eye it moves (L-d)*sin(b) ---
spl={}
for b in (3,4,5):
    s=math.sin(math.radians(b)); d_out=(L-EYE_OFF)*s
    spl[f'{b}deg']=dict(body_shift_out_mm=round(d_out,1),femur_gap_after_mm=round(gap_femur-d_out,1),
      L94_single_gain_deg=round(2*d_out/6.5,1),torque_factor_inner=round(math.cos(math.radians(b)),4),
      lateral_on_lever_eye_N_at_4542=round(4542*s),ok=gap_femur-d_out>=3)
# pivot the other way (body fixed at thigh eye, rod end moved): contact region only moves EYE_OFF..Lb from the pivot
rodend_pivot={b:round((EYE_OFF+10)*math.sin(math.radians(b)),1) for b in (3,4,5)}
# --- (1) clamp: thin wall can OD 82 t 2, stator bonded inside; limit radial deflection 0.01 mm [EST, << ~0.5 mm air gap] ---
E7075,t,R=71.7e3,2.0,(D-2)/2; dlim=0.01; w=10.0
p_max=dlim*E7075*t/R**2; hoop=p_max*R/t; T_band=p_max*R*w
# --- pad side load: body+rod is a two-force member on spherical eyes; transverse F at the pad is reacted 1-a/L at the thigh eye, a/L at the rod-end ---
a=EYE_OFF+24      # pad centre in the allowed band (body z 24 -> 54 mm from the eye)
z_nut=EYE_OFF+Lb  # nut / front bearing exit
f_top=a/L; M_rod=lambda F: F*f_top*(L-z_nut)                       # N mm, rod bending at the nut exit
Z=math.pi*10.4**3/32                                               # RV12 root ~10.4 [EST]
F_rod=60*Z/(f_top*(L-z_nut))                                       # 60 MPa rod bending [EST rare-event limit; Rollvis: avoid radial load on the nut]
F_nut=0.05*21e3/(f_top*(L-z_nut)/36+f_top)                         # nut radial <= 5 % C0a [EST C0a 21 kN RV12x4]
F_allow=min(F_rod,F_nut,300.)
# PU 95A pad 20x30x8 [EST], E~60 MPa [EST]; energy it may take at F_allow
k=60*20*30/8; E_pad=0.5*F_allow**2/k/1e3
# limp leg roll impact [EST]: leg 10.5 kg, r_g 0.42 m about hip roll, 2-3 rad/s limp adduction
I=10.5*0.42**2; E_imp={w_:round(0.5*I*w_**2,1) for w_ in (1.0,2.0,3.0)}
out=dict(body=dict(D_motor=D,Lm=round(Lm,2),D_nut=Dn,L_body=round(Lb,1),eye_offset=EYE_OFF,y_inner=y_in,pin_to_pin_L=round(L,1)),
 clamp=dict(zone_body_z_mm=[14,38],zone_from_eye_mm=[EYE_OFF+14,EYE_OFF+38],band_w_max_mm=12,
   keepouts='z 0-12 rear cap/encoder + eye stub flange; z 43-49 cone; z 49-105 nut + 7202 pair + front seal/wiper (z 102-105); no clamp on the RV12 rod',
   p_max_MPa=round(p_max,2),hoop_MPa=round(hoop,1),band_tension_max_N=round(T_band),bond='bond the pad saddle (as clamp_review bonded+light clamp)'),
 pad=dict(F_allow_N=round(F_allow),F_rod_limit_N=round(F_rod),F_nut_limit_N=round(F_nut),E_allow_J=round(E_pad,2),k_N_per_mm=round(k),E_impact_J=E_imp,
   verdict='pad is a touch/anti-fret buffer only (<=~1 J); it cannot be the energy stop'),
 splay=dict(femur_gap_now_mm=round(gap_femur,1),about_lever_eye=spl,about_thigh_eye_shift_mm=rodend_pivot,
   verdict='3-5 deg outboard about the lever eye puts the inner body into the femur/thigh clamp (gap 3 mm [EST]); about the thigh eye the contact zone moves only 2-3.5 mm: NOT feasible'))
json.dump(out,open(f'{H}/results/hip_screw_adduction_d104.json','w'),indent=1); print(json.dumps(out,indent=1))
