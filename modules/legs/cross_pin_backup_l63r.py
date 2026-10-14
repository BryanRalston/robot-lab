"""L63-R: re-check of L63 8x ø7 radial pins against Materials L63 conditions (e/D>=2 tube end, pitch>=2.5D, 720 MPa static only,
600 MPa at e/D 1.5 [EST, Materials]). Bond SF rescaled from R110_HOT_BOND §4 (fault SF 1.58 @82C, 1.45 @95C on 5341 mm2). Hand calc."""
import math,json
F=29600.; t=1.2; D=50.; Lc=34.; Atube=183.97; Fw=0.52*8763.86; Kt=2.909; rho=7.8e-6
TUBE_Z=(-12.,46.)   # tube extent in grokbuild/fea_retain.py bond model; CAD not confirmed [EST]
def lay(n,d,z,stagger_deg,brg_allow=720):
    per=n//len(z); circ=math.pi*D/per; dz=abs(z[1]-z[0])
    arc=math.pi*D*stagger_deg/360; diag=math.hypot(dz,arc)
    e_tube=min(z[0]-TUBE_Z[0],TUBE_Z[1]-z[1]); e_col=min(z[0],Lc-z[1])
    brg=F/(n*d*t); net=Atube-n*d*t; tear=F/(n*2*(e_col-d/2)*6.0); fat=Fw/net*Kt
    hole=n*math.pi*d*d/4; Ab=math.pi*D*Lc-hole
    return dict(layout=f"{n}x ø{d} radial, rows z {z[0]}/{z[1]}, row 2 rotated {stagger_deg}°",
      inrow_pitch_mm=round(circ,1),inrow_pitch_over_D=round(circ/d,2),row_axial_mm=dz,
      row_hole_to_hole_mm=round(diag,1),row_pitch_over_D=round(diag/d,2),
      tube_end_e_mm=e_tube,tube_end_e_over_D=round(e_tube/d,2),collar_end_e_over_D=round(e_col/d,2),
      bearing_MPa=round(brg,1),SF_bearing_720=round(720/brg,2),SF_bearing_600=round(600/brg,2),
      SF_tearout=round(330/tear,2),SF_net=round(480/(F/net),2),SF_fatigue=round(160/fat,2),
      bond_area_mm2=round(Ab),bond_SF_82C=round(1.58*Ab/(math.pi*D*Lc),3),bond_SF_95C=round(1.45*Ab/(math.pi*D*Lc),3),
      pin_mass_leg_kg=round(n*math.pi*d*d/4*10*rho,4))
R=dict(L63_as_adopted=lay(8,7,(8.5,25.5),0),
       L63R_adopted=lay(8,7,(8.25,25.75),45),
       fallback_flush_tube_end_8x8=lay(8,8,(8.25,25.75),45),
       fallback_10x7=lay(10,7,(8.25,25.75),36))
R['L63R_adopted']['mass_delta_vs_L63_robot_kg']=0.0
json.dump(R,open('results/a38/cross_pin_backup_l63r.json','w'),indent=1); print(json.dumps(R,indent=1))
