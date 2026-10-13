"""R5 (O17/O22/ankle 73 mm): femur tongue ø35 press-fit for the needle straddle (Actuators D32), bonded thigh clamp with positive backup, M2 total.
Hand methods (no FEA run this round). Writes results/r5/structure_r5.md/.json."""
import json,math,os
H=os.path.dirname(os.path.abspath(__file__)); RHO=2.81e-6; SY,SU,SE=503.,572.,159.; g=9.81
r4=json.load(open(f'{H}/results/r4/structure_m2.json')); rows={r['part']:r['kg'] for r in r4['rows']}
# ---- O17 femur tongue: ø35 bore, press-fit of the 16MnCr5 hollow shaft ø35/ø30 (D32), tongue |y|<=13.5 -> t 27, OD 55, neck 50x27x20
D,Do,t=35.,55.,27.; P=2*4542+1.5*66.5*g; M=192e3   # N, N·mm (D27/D32 pivot load: both screws max + 1.5 BW; hip_roll/yaw moment couple)
net=3*P/((Do-D)*t); so=P/(2*(Do/2-D/2)*t); brg=P/(D*t); brgM=M/(D*t**2/6)   # Kt 3 net tension, shear-out, bearing, moment edge pressure
p=60.0   # MPa design contact pressure (> moment edge pressure 45 MPa so the fit does not gap)
Eh,Es,nh,ns,di=71700.,210000.,0.33,0.30,30.
hoop=p*(Do**2+D**2)/(Do**2-D**2)
delta=p*D*(((Do**2+D**2)/(Do**2-D**2)+nh)/Eh+((D**2+di**2)/(D**2-di**2)-ns)/Es)   # diametral interference, mm
dT_hot=60; lost=D*(23.6e-6-11.5e-6)*dT_hot; p_hot=p*(delta-lost)/delta
hold_ax=0.15*p_hot*math.pi*D*t
sa=0.5*0.52*net; sm=hoop+sa; good=1/(sa/SE+sm/SU)
tongue_kg=(math.pi/4*(Do**2-D**2)*t+50*t*20)*RHO
O17=dict(P_N=round(P),net_tension_MPa=round(net,1),SF_net=round(SY/net,2),shear_out_MPa=round(so,1),SF_shear=round(0.577*SY/so,2),bearing_MPa=round(brg+brgM,1),SF_bearing=round(SY/(brg+brgM),2),
         press_p_MPa=p,hoop_MPa=round(hoop,1),SF_hoop=round(SY/hoop,2),interference_mm=round(delta,3),p_at_plus60K_MPa=round(p_hot,1),axial_hold_kN=round(hold_ax/1000,1),goodman_SF=round(good,2),mass_kg=round(tongue_kg,3))
# ---- O22 clamp: bonded collar (DP490-class) + light ~3 MPa clamp + positive backup (internal 7075 sleeve + 2 cross pins ø6 42CrMo4)
d,L=50.,34.; Fax=8764.; Ftr=2390.; F1=4542.; Mfault=F1*69   # Actuators D46 loads; one-screw fault moment at the collar
A=math.pi*d*L; tau_ax=Fax/A; tau_fault=F1/A+Mfault/(math.pi*(d/2)**2*L); lap=31.0; kd=0.5   # DP490 lap shear on etched Al ~31 MPa [datasheet class], ×0.5 knock-down
tau_walk=0.52*Fax/A; fat_allow=0.20*lap
pins_d,pt=6.,1.2+2.0; tau_pin=Fax/(4*math.pi*pins_d**2/4); brg_tube=Fax/(4*pins_d*pt)
sleeve=math.pi/4*(47.6**2-43.6**2)*L*RHO; pins=2*math.pi/4*pins_d**2*62*7.85e-6; glue=0.003
clamp_kg=rows['thigh clamp (hip_pitch bodies, axial eye form)']+sleeve+pins+glue
O22=dict(bond_area_mm2=round(A),tau_max_both_MPa=round(tau_ax,2),SF_bond_static=round(kd*lap/tau_ax,1),tau_fault_one_screw_MPa=round(tau_fault,2),SF_bond_fault=round(kd*lap/tau_fault,2),
         tau_walk_MPa=round(tau_walk,2),SF_bond_fatigue=round(fat_allow/tau_walk,1),clamp_pressure_MPa=3.0,hoop_tube_MPa=round(3.0*d/2/1.2,1),
         backup_pin_tau_MPa=round(tau_pin,1),SF_pin_shear=round(0.577*900/tau_pin,1),backup_bearing_tube_plus_sleeve_MPa=round(brg_tube,1),SF_backup_bearing=round(SY/brg_tube,2),
         backup_fatigue_SF=round(SE/(0.52*brg_tube*1.0),2),FEA_body_SF=2.90,FEA_body_fatigue=1.76,
         added_kg=dict(sleeve=round(sleeve,4),pins=round(pins,4),adhesive=glue),mass_kg=round(clamp_kg,3),eyes='SKF GE 12 C / maintenance-free (PTFE) per D46, mass in Actuators line')
per=sum(rows.values())-rows['femur hip ring: CRBH 5013 seat ø80 H7×13, OD 96 × 25 (|y|≤12.5) + neck']+tongue_kg-rows['thigh clamp (hip_pitch bodies, axial eye form)']+clamp_kg
both=2*per; bolts=0.04
out=dict(O17=O17,O22=O22,ankle_pin='73 mm: see results/r5/ankle_clearance.json; foot mass unchanged (instep block moved +3 mm in x)',per_leg=per,both=both,both_incl_bolts_bumper=both+bolts)
json.dump(out,open(f'{H}/results/r5/structure_r5.json','w'),indent=1)
L=['# Legs r5 M2 update (O17 needle tongue, O22 bonded clamp, ankle 73 mm)','',f'Femur tongue ø35 press-fit: {O17}','',f'Thigh clamp: {O22}','',
   f'M2 per leg {per:.3f} kg, both legs **{both:.3f} kg** vs 4.85 → {4.85-both:+.3f}; incl. split-collar bolts + bumper 0.04 [EST] {both+bolts:.3f} → {4.85-both-bolts:+.3f}']
open(f'{H}/results/r5/structure_r5.md','w').write('\n'.join(L)+'\n'); print(json.dumps(out,indent=0)[:2500])
