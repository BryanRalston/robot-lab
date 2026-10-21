"""L75 hand checks [EST] for the L74 twin straps (T&R fall load 2e9b25c) + housing-to-plate gap fix.
Couple scaling: L61 8.66 kN couple for 5053 N screw force; taken conservatively as 8.66 kN PER 5053 N of TOTAL screw thrust -> fall 29 kN -> 49.7 kN couple.
Straps 20x8 7075-T7351, y 84-104 / 156-176, free length x -40 -> -8.5 = 31.5 mm, ends fixed (integral with the plate; bolted pad on the G10 block)."""
import json,math
out={}; E=71700.; A=160.; I=20*8**3/12; r=math.sqrt(I/A)
C_fall=8.66*29.0/5.053; C_des=8.66*2*5053/5053/2
for name,share in (('equal',0.5),('65/35',0.65)):
    F=C_fall*share*1000; s=F/A; Kt=1.5   # R8 plan fillet strap root, r/d 0.4 [EST Peterson]
    out[f'fall_{name}']=dict(strap_kN=round(F/1000,1),sigma=round(s,1),SF_net_393=round(393/s,2),sigma_root_Kt=round(s*Kt,1),SF_root_393=round(393/(s*Kt),2))
L=31.5; Le_pin=L; Le_fix=0.5*L
out['buckling']=dict(L_free_mm=L,r_mm=round(r,2),L_r_pinned=round(Le_pin/r,1),sigma_euler_pinned=round(math.pi**2*E/(Le_pin/r)**2),
    note='L/r 13.6 pinned (6.8 fixed-fixed) << Johnson transition (~60 for 7075): no buckling; compression governed by yield, same SF as tension. T&R 120 mm pinned basis does not apply (real 31.5 mm, ends fixed).')
# end joint: per strap pad 30 wide x 8, 4 x M6 12.9 in double row; bolts in single shear through the G10 block into PEM inserts (threads do not meet)
F=out['fall_65/35']['strap_kN']*1000; nb=4; d=6.; As=20.1; Ash=28.3
tau_b=F/(nb*Ash); out['joint']=dict(bolts='4 x M6 12.9 per strap end (shank in shear plane), e/D 2.0, pitch 3D',
   bolt_shear_MPa=round(tau_b),SF_bolt_shear=round(0.6*1220/tau_b,2),
   bearing_7075_pad_MPa=round(F/(nb*d*8)),SF_bearing_tier455_eD2=round(455/(F/(nb*d*8)),2),
   bearing_G10_MPa=round(F/(nb*d*12)),G10_note='G10 bearing/compression allowable: Materials to cite; pad keyed 2 mm into the G10 face both sides (tongue-in-groove) so tension and compression bear on G10, bolts carry preload',
   bond_alt='DP490 at 82 C would need ~4600 mm2 (T&R) -> rejected, bolts')
# slip at L58 clamp: z-component of screw thrust into the femur tube by friction
mu=0.3; Fz=29000; out['L58_clamp_slip']=dict(required_clamp_normal_kN=round(Fz/mu/1000),result='FAIL by friction alone (L61 same finding); fix: clamp ear abuts a positive shoulder on the L22 bonded split collar (axial key), friction only for walk',
   walk_check=dict(Fz_walk_N=2*3364,required_normal_kN=round(2*3364/0.3/1000,1)))
# G10 heat path (k G10 ~0.29 W/mK [EST, Materials to cite]); per block 30x25 face
k=0.29; Ab=30*25e-6
for t in (3,5,6):
    R1=t/1000/(k*Ab); out[f'G10_web_{t}mm']=dict(R_per_block_K_W=round(R1,1),R_two_parallel=round(R1/2,1))
out['G10_rec']='6 mm web -> 13.8 K/W two blocks in parallel (>= 10 K/W, L61/Thermal trunnion basis)'
out['strap_vs_release_housing']=dict(min_mm='>= 21 (straps x -40..-8.5 vs housing front x -61.0 at zero pose; housing pivots, max zmax rise at knee 145 is +1.6 mm, front x shift not swept - FEA clearance step)')
# housing-plate gap
gap={'0':2.04,'30':5.28,'90':7.12,'130':2.9,'135':2.12,'140':1.31,'145':0.48}
tol=dict(housing_machining=0.2,plate_flatness=0.1,stack_assembly=0.15,thermal_growth_dT40=round(129*23.6e-6*40,2),plate_deflection_fall=0.15)
rss=round(math.sqrt(sum(v*v for v in tol.values())),2); worst=round(sum(tol.values()),2)
out['housing_plate_gap']=dict(true_OCC_gap_by_knee=gap,static=False,why='the twin housing is trunnion-mounted and pivots with the screw angle: fin tops rise 1.6 mm from knee 0 to 145 (zmax 813.96 -> 815.52)',
   min_mm=0.48,at_knee=145,tolerances_EST=tol,RSS=rss,worst_case=worst,
   fix='raise the L60 top plate + straps 4.0 mm (z 820-828): nominal 4.48 at knee 145, worst-case 4.48-%.2f=%.2f, RSS %.2f (>= 3 both); cheeks +4 mm (L60 DZ precedent); ID rev 6 stack/shroud move up 4 mm'%(worst,4.48-worst,4.48-rss))
json.dump(out,open('results/r031/l75_strap_checks.json','w'),indent=1); print(json.dumps(out,indent=0))
