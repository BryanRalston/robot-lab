"""R-022 A14: ankle_roll ±18° hard stop (geometry/mass/sizing) and thigh-clamp cross-pin access panel. Hand sizing; [EST] = estimate, unverified."""
import json,math,os
H=os.path.dirname(os.path.abspath(__file__)); R=json.load(open(f'{H}/results/r7/aroll_push.json'))
# --- ankle_roll stop
J=0.1115            # kg m^2 swing-foot inertia about roll axis incl. armature 0.0944 (66.054 kg model)
T=177.0             # N m R1.2 ankle_roll avail (LIM_R1) -> stall load the stop must hold
alpha=T/J; w_hit=10.26   # rad/s worst speed at 18° in fsim push (stop run, right foot, during the fall)
brake_deg=math.degrees(w_hit**2/(2*alpha))
r=45.0; F=T/(r/1000); A=20*12; p=F/A
t_pu=2.0; E_pu=40.0   # mm, MPa [EST PU 95A, unverified]
x=p/E_pu*t_pu; over_pad=math.degrees(x/r)
E_imp=0.5*J*w_hit**2
blk=20*12*10e-3*2.81  # g, 7075 block 20x12x10
mass_leg=(2*blk+2*20*12*t_pu*1.2e-3+2*1.0)/1000   # 2 blocks + 2 PU pads + 2 M4x10 [EST]
margin18=10.9; mm_per_deg=(10.9-2.9)/(25-18)
sim_over=max(abs(R['stop'][s][k]) for s in 'lr' for k in ('min_all','max_all'))-18
stop=dict(range_deg=18,model='jnt_range ±18°, solref [2dt,1] solimp [.95,.99,.001] (gait_lib LEGS_AROLL)',
  geometry='2 x 7075 stop blocks 20x12x10 mm on the ankle cross (±roll), contact face at r 45 mm, faces strike foot-fork shoulders; 2 mm PU 95A pad bonded on each face; 1 x M4x10 + dowel per block',
  hold_force_N=round(F),face_pressure_MPa=round(p,1),pad_deflection_mm=round(x,2),overtravel_pad_deg=round(over_pad,2),
  sim_overtravel_deg=round(sim_over,1),clearance_margin_mm_at_sim_overtravel=round(margin18-mm_per_deg*sim_over,1),
  soft_limit=dict(decel_rad_s2=round(alpha),brake_deg_from_10p26=round(brake_deg,2),start_deg=round(18-brake_deg,1)),
  impact_energy_J_if_unbraked=round(E_imp,1),mass_kg_per_leg=round(mass_leg,4),mass_both=round(2*mass_leg,3))
# --- thigh panel for cross pins (collar ø50 tube, collar L34, 2 x ø6 x 62 pins along x, 17 mm apart in z) [pin axis/pitch EST]
pin_L=62; drift=pin_L+10; tool_side=25   # punch length to push the pin out; hand/hammer room
panel=dict(outline_mm='front (x+) panel 60 w x 70 h, R8 corners, centred on collar mid-height; matching rear 40x50 exit window',
  pins='2 x ø6 x 62 42CrMo4, x-axis, z ±8.5 from collar mid [EST layout]',
  access=dict(front_clear_mm=f'≥{tool_side} free in front of pin heads (cover 3 mm off collar OD ø64 → ~35 mm to fairing inner wall)',
              rear_push_out_mm=f'pin exits rear through 40x50 window, ≥{pin_L} mm needed, ≥{pin_L+8} available behind collar to the seat/hip envelope [EST]',
              tool='ø5 pin punch L≥{} mm + 200 g hammer, or M3 extractor thread'.format(drift),
              lateral_margin_mm=round((60-17-12)/2,1)),
  fasteners='front 4 x M3 captive quarter-turn (Southco-type) [EST]; rear 2 x M3',
  mass_kg_per_leg=round((60*70+40*50)*1.5e-3*1.15/1000+6*0.0012,4),material='PA12-CF 1.5 mm, 1.15 g/cc [EST]')
out=dict(ankle_roll_stop=stop,thigh_pin_panel=panel,push=R)
json.dump(out,open(f'{H}/results/r7/a14.json','w'),indent=1); print(json.dumps({k:v for k,v in out.items() if k!='push'},indent=0))
