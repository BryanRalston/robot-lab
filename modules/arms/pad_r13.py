"""R13 (R-120, 12f68a4; ID stand-off layout 00ff254). Hand calcs only; FEA = Job 8 add-on. Units N, mm unless noted.
Loads: R10 core 7.0 kN peak, 15 deg governing: Fn 6.76 kN, Fs 1.81 kN (mu credit none, R-119/R-120). Y 102.3, Z 20. Fault x1.05.
CRBH 7013 A: 70x100x13, C0 27.7 kN, 0.38 kg, shoulders 76/94 -> dp ~85 (iko_crb_catalog.txt l.802). rho 7075 2.81 g/cc."""
import json,os,numpy as np
H=os.path.dirname(os.path.abspath(__file__)); rho=2.81e-3  # g/mm3
Fn=7000*np.cos(np.radians(15)); Fs=7000*np.sin(np.radians(15)); Y,Z=102.3,20.0
def s0(C0,dp,e): M=Fs*np.hypot(Y,Z)+Fn*e; return round(C0/(Fn+2*M/dp+0.44*Fs),2)
Mx=(Fn*Z+Fs*Y)/1e3
chk=dict(s0_7013={f'e{e}':s0(27700,85,e) for e in (0,5,10)},Mx_raw_Nm=round(Mx),CSG25_SF_fault=round(369/(1.05*Mx),2),
         note='reproduces R-120 2.31/2.16/2.04, 321 N.m, SF 1.10')
ring=lambda D,d,t:np.pi/4*(D*D-d*d)*t
# stand-off flange: ID proposal OD60/ID40x4 vs Arms R13 OD70/ID44x5, 8xM4 12.9 on PCD 62 + 2x dia4 m6 dowels
def flange(n,pcd):
    Vt=Mx*1e3/(n*pcd/2); Vd=np.hypot(Fn,Fs)/n; return round(Vt+Vd)
M4_shear_cap=5000  # N, M4 12.9 single shear (R7 basis)
bolts={'ID_6xM4_PCD50_EST':dict(per_bolt_N=flange(6,50),SF=round(M4_shear_cap/flange(6,50),2)),
       'R13_8xM4_PCD62':dict(per_bolt_N=flange(8,62),SF=round(M4_shear_cap/flange(8,62),2)),
       'friction_8xM4_12.9_preload_4.6kN_mu0.15_N':round(8*4600*0.15),'verdict':'joint is bearing-type: 2 dowels dia4 m6 carry shear, bolts clamp; 6xM4 PCD50 SF 1.53 too thin'}
# ribs: 2 x 5 x 30, root moment from Fs at Y lever (worst, ribs bending strong axis) and Fn*Z
I=2*5*30**3/12; sig_Fs=Fs*Y*15/I; sig_n=Fn/(2*5*30); sig_Fn_Z=Fn*Z*15/I
ribs=dict(sigma_Fs_bend_MPa=round(sig_Fs),sigma_FnZ_bend_MPa=round(sig_Fn_Z),sigma_axial_MPa=round(sig_n),
          sigma_sum_MPa=round(sig_Fs+sig_n),allow_MPa='503/1.5=335 (7075-T6)',SF=round(335/(sig_Fs+sig_n),2),
          note='strong-axis only; weak-axis (5 mm) and plate pocket need FEA (Job 8 add-on)')
m=dict(ID_EST=dict(face_plate=0.0194,web_neck=0.0177,roll_flange_OD60=0.0141),
       R13_CALC=dict(face_plate=0.0194,web_neck=0.0177,roll_flange_OD70x5=round(ring(70,44,5)*rho/1000-8*np.pi/4*4.5**2*5*rho/1000,4),dowels_bolts=0.0040))
m['R13_CALC']['total_side']=round(sum(m['R13_CALC'].values()),4)
# roll housing, 6013 -> 7013 (Arms owns geometry, Actuators books)
hous=dict(old=dict(seat_flange=round(ring(98,90,15)*rho/1e3,4),hub=round(ring(60,48,20)*rho/1e3,4),clamp=round(ring(98,84,3)*rho/1e3,4)),
          new=dict(seat_flange=round(ring(108,100,15)*rho/1e3,4),hub=round(ring(70,54,20)*rho/1e3,4),clamp=round(ring(108,94,3)*rho/1e3,4)))
hous['delta_side']=round(sum(hous['new'].values())-sum(hous['old'].values()),4)
mass=dict(stand_off_side=m['R13_CALC']['total_side'],stand_off_net_pair_vs_boss_booked=round(2*(m['R13_CALC']['total_side']-0.024),3),
          housing_growth_pair=round(2*hous['delta_side'],3),bearing_pair_cited=round(2*(0.38-0.33),3),
          booked_R120=dict(bearing=0.100,housing=0.060,standoff_net=0.052))
mass['R13_total_pair']=round(mass['stand_off_net_pair_vs_boss_booked']+mass['housing_growth_pair']+mass['bearing_pair_cited'],3)
mass['delta_vs_booked_pair']=round(mass['R13_total_pair']-0.212,3)
# tolerance stack for e (pad force-line offset from design point, perpendicular to Fn), mm
tol={'bearing seat in housing (H7, position)':0.05,'CRBH 7013 A runout/width centre':0.05,'roll-output hub face to bearing plane':0.10,
     'stand-off flange thickness/flatness':0.05,'flange dowel location (2xdia4 m6/H7)':0.03,'rib/face plate machined position (one setup)':0.10,
     'tray M4 clearance float (4.5 holes, tray not doweled)':0.25,'tray lip to core (bond fixture)':0.50,'core cut position/squareness over 75.3':0.50,
     'link/stand-off elastic deflection at 7 kN [EST, FEA]':0.50}
wc=round(sum(tol.values()),2); rss=round(float(np.sqrt(sum(v*v for v in tol.values()))),2)
tst=dict(contributors_mm=tol,worst_case_mm=wc,rss_mm=rss,budget_mm=5.0,margin_wc_mm=round(5-wc,2),
         note='as-built e <= 2.1 mm worst case; remaining ~2.9 mm is for impact-centroid shift on the core, which FEA (e 0/5/10) brackets')
out=dict(check=chk,bolts=bolts,ribs=ribs,mass_parts=m,housing=hous,mass=mass,tolerance=tst)
json.dump(out,open(os.path.join(H,'pad_r13.json'),'w'),indent=1); print(json.dumps(out,indent=1))
