"""R14: Arms verification of ID stand-off R11 (ec12542, design/pad_r11_standoff.json) after Job 8 add-on FAIL (e02c34b, bc6ad91).
FEA frame: origin on roll axis, +X roll axis (= sim l_shoulder_roll axis 1 0 0), +Y outboard (pad normal), +Z up. N, mm, MPa.
Gate (task): SF >= 1.5 vs yield 503 (i.e. <= 335); FEA case limit 337 (0.67 Sy). Loads 15 deg, no mu credit."""
import json,os,numpy as np
H=os.path.dirname(os.path.abspath(__file__)); rho=2.81e-6; SY=503.
Fn=7000*np.cos(np.radians(15)); Fs=7000*np.sin(np.radians(15)); Kcal=2.86   # ID calibration R10 hand->FEA
G=json.load(open(os.path.join(H,'../design/pad_r11_standoff.json')))
# 1 box 44x44x2.5, centred Z -15; pad centre Z -20, contact Y 102.3, e5 (X)
Bo,t=44.,2.5; Bi=Bo-2*t; A=Bo**2-Bi**2; I=(Bo**4-Bi**4)/12; S=I/(Bo/2)
Mx=Fs*102.3+Fn*5.0       # down case: Fs lever + Fn x (pad Z -20 vs box Z -15)
Mz=Fn*5.0                # e5 along X
sig_hand=Fn/A+Mx/S+Mz/S; sig_cal=Kcal*sig_hand
box=dict(A_mm2=A,S_mm3=round(S),sigma_hand_MPa=round(sig_hand,1),sigma_cal_MPa=round(sig_cal),ID_cal_MPa=G['stress_MPa']['box_calibrated'],
         SF_yield=round(SY/max(sig_cal,G['stress_MPa']['box_calibrated']),2),gate='>=1.5 PASS',
         note='Arms hand (biaxial, Fn offset 5 mm, e5) x2.86 gives the same order as ID 215; governs 215 -> SF 2.34 vs yield, 1.57 vs 337 FEA limit')
plate=dict(ID_span_MPa=149,SF=round(SY/149,2),overhang_MPa=25)
# 2 flange ring OD70/ID44 x5, 8xM4 (4.5 clr) + 2xD6 on PCD62
def lig(OD,ID,pcd,d): r=pcd/2; return dict(outer_mm=round(OD/2-r-d/2,2),inner_mm=round(r-d/2-ID/2,2),edge_dist_over_d=round((OD/2-r)/d,2))
flange=dict(R13_OD70={'M4_4.5':lig(70,44,62,4.5),'D6_dowel':lig(70,44,62,6)},
            R14_OD76={'M4_4.5':lig(76,44,62,4.5),'D6_dowel':lig(76,44,62,6)},
            rule='edge distance >= 1.5 d (bearing-joint practice) [EST]; OD70 gives 0.89 d (M4) / 0.67 d (D6): FAIL; OD76 gives 1.56 d / 1.17 d',
            fix='flange + hub shoulder OD 76 (= CRBH 7013 A inner-ring shoulder 76, IKO l.802) and dowels on PCD 57 between bolts: D6 ligaments 3.5 / 6.5 mm',
            dowel_PCD57=dict(tau_MPa=round(229*31/28.5),SF_vs600=round(600/(229*31/28.5),2)),
            bearing_OD76_t5_MPa=round(216*0.89/1.0),note2='ID bearing 216 MPa (SF 2.22) assumed full ring; with OD76 edge distance the 2.22 holds')
flange['dm_side_kg_OD70_to_76']=round(rho*np.pi/4*(76**2-70**2)*5,4)
# 3 bolt access: which of 8 M4 heads (PCD62, D7 head) lie under the closed box / solid plate (box X+-22, Z -37..+7)
acc={}
for off in (0,22.5):
    blocked=[]
    for k in range(8):
        a=np.radians(off+45*k); x,z=31*np.cos(a),31*np.sin(a)
        if abs(x)-3.5<22 and -37<z+3.5 and z-3.5<7: blocked.append([round(x,1),round(z,1)])
    acc[f'pattern_offset_{off}deg']=dict(blocked=len(blocked),pos=blocked)
access=dict(cases=acc,verdict='FAIL: 2-3 flange bolt heads sit under the closed box/solid plate; no tool access once one-piece',
            fix='3 x D8 wrench holes through the plate on the blocked bolt axes (tray covers them; pad fitted after the stand-off) or a split stand-off (flange bolts, then box/plate bolted) - Job 8b checks plate with holes')
# 4 machinability
mach=dict(billet_mm='76 x 88 x 32 (X x Z x Y) 7075-T6 plate',ops='2 setups: (1) flange side: turn/mill ring, bore D44, box ID 39x39 pocket through the bore 28 deep with D8 end mill (R4 inner corners, L/D 3.5); (2) plate side: plate, R3 fillets, 4xM4 bosses',
          issue='box walls X+-22 coincide with ring bore D44: the box root lands on the ring only where r>=22 (corners and Z<-22); top/side walls sit over the bore -> FE root fix at Y0 is non-conservative',
          fix='box root fillet R3 into a 3 mm root land; or reduce bore to D36 under the box (keeps M4 at PCD62, hub ID54 unaffected since bore only needs clearance) - Arms picks bore D36',
          verdict='machinable (no 3D printing); conventional 3-axis')
# 5 e stack with 0.69 deflection
tol={'bearing seat (H7)':0.05,'CRBH runout/width centre':0.05,'hub face to bearing plane':0.10,'flange thickness/flatness':0.05,
     'dowel location (D6 m6/H7)':0.03,'box/plate machined position (one setup)':0.10,'tray M4 float':0.25,'tray lip to core':0.50,
     'core cut position/squareness':0.50,'elastic deflection (ID calibrated)':0.69}
st=dict(contributors_mm=tol,worst_mm=round(sum(tol.values()),2),rss_mm=round(float(np.sqrt(sum(v*v for v in tol.values()))),2),budget=5.0)
st['verdict']='PASS (within e<=5) - but see geometry blocker'
# 6 geometry blocker: housing position. sim roll axis = X. In ID CAD the 7013 ring is coaxial with Y (placeholder y0 -18).
pts=[(y,z) for y in np.linspace(0,102.3,60) for z in np.linspace(-51,11,40)]
rmin=min(np.hypot(y,z) for y,z in pts)
geo=dict(ID_CAD_frame='housing_7013 / OD108 / stand-off flange modelled coaxial with Y (ring axis y) - inconsistent with the roll axis X used for Mx, s0 and in sim/v3',
         consistent_frame='7013 A coaxial with X at the bearing plane (x=0, e measured from it) occupies r 35..50, seat flange r..54 over x -6.5..+6.5',
         standoff_pad_min_r_mm=round(rmin,1),overlap_with_bearing_envelope=bool(rmin<54),
         clear_option_axial_e_mm=31+6.5+3,s0_7013_at_e40_5=round(27700/(Fn+2*(Fs*np.hypot(.1023,.02)+Fn*.0405)/0.085+0.44*Fs),2),
         verdict='BLOCKER: with e<=5 the stand-off/pad (Y 0..102, Z -51..+11, |X|<=31) sits inside the CRBH 7013 A / OD108 envelope. Their CAD does not show it only because the housing ring is drawn on the wrong axis. Axial gap >=3 mm to OD108 is therefore not achievable at e<=5.')
def s0(C0,dp,Y,Z,e): M=Fs*np.hypot(Y,Z)/1e3+Fn*e/1e3; return round(C0/(Fn+2*M/(dp/1e3)+0.44*Fs),2)
def gear(Y,Z): Mx_=(Fn*abs(Z)+Fs*Y)/1e3; return round(Mx_),round(369/(1.05*Mx_),2)
alts={}
for name,(C0,dp,Z,ym,dkg) in {'W2 wrap carrier, 7013, pad on axis (Z0)':(27700,85,0,63.,'carrier ~+0.14 pair [EST]'),
                              'W3 wrap carrier, 8016, Z0':(43400,100,0,69.,'+0.72 bearing (cited) + housing ~+0.2 + carrier ~+0.14 [EST] (= R11 B, rejected for mass)'),
                              'W1 wrap carrier, 7013, Z-20':(27700,85,20,63.,'')}.items():
    Y=ym+0.5+75.3; m_,sf=gear(Y,Z)
    alts[name]=dict(contact_Y=round(Y,1),s0_e0=s0(C0,dp,Y,Z,0),s0_e5=s0(C0,dp,Y,Z,5),Mx=m_,gear_SF=sf,pad_proud_extra_mm=round(Y-102.3,1),mass=dkg)
# 7 cover / STL checks in ID frame (only bodies present: pad, stand-off, tray, local cover, housing placeholder)
cov=dict(window='68x68 R6 at (X0,Z-20): box X+-22 / Z+7..-37 margins 12 / 7 / 17 mm; plate 62 vs window 68: 3 mm/side; PASS',
         housing_relief='cover relief OD114 vs OD108 flange: 3 mm radial; PASS in ID frame (moot under blocker)',
         flange_vs_housing_flange_ID_frame='stand-off flange y -5..0 abuts housing flange face y -10..-5: 0 mm axial gap (radially separated r35 vs r50): FAIL vs >=3 mm even in ID frame',
         not_checkable='head shell, torso cover, abduction ROM: no CAD; light-model R13 results stand (head >=141, overhead roll>=170 torso 9.4 marginal, keep 135 soft limit)')
# 8 mass
m_side=G['kg_side']+flange['dm_side_kg_OD70_to_76']-rho*3*np.pi/4*8**2*4
mass=dict(ID_R11_side=G['kg_side'],R14_side_CALC=round(m_side,4),R13_side=0.072,delta_pair_vs_R121=round(2*(m_side-0.072),3),
          R121_pair=0.271,new_pair=round(0.271+2*(m_side-0.072),3),note='addition >0.005: needs a ruling under the R-066 freeze; Arms does NOT book it while the geometry blocker stands')
out=dict(rev='R14',basis='ID ec12542 stand-off R11',box=box,plate=plate,flange=flange,bolt_access=access,machining=mach,e_stack=st,geometry=geo,
         buildable_alternatives=alts,covers=cov,mass=mass)
json.dump(out,open(os.path.join(H,'pad_r14.json'),'w'),indent=1); print(json.dumps(out,indent=1))
