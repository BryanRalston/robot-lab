"""R15 W2 wrap carrier (R-125). CadQuery 2.8. Arms frame: X roll axis (sim l_shoulder_roll), Y outboard, Z up; origin on the roll axis at
the CRBH 7013 A bearing plane. mm. 7075-T6 basis Sy 480 / static limit 320 (R-125). Stator (does not roll): bearing r35-50 x+-6.5,
seat flange OD108 r50-54 x+-7.5 (housing_7013_real_coaxX). Rotating: output hub D70 x -6.5..12 [EST], stand-off flange (R14 fixes) on the
hub end face x 12..17. Carrier = radial box arm x 17..45 beyond the housing, outboard plate over the housing at Y >= 57.5, pad centred X0 Z0.
Hand stresses x2.86 (ID R10 FE calibration, conservative for closed sections) vs gate 320."""
import cadquery as cq, json, os, math, numpy as np
H=os.path.dirname(os.path.abspath(__file__)); os.chdir(H)
P=dict(r_h=54.0,gap=3.0,tp=6.0,ax0=17.0,ax1=42.0,az=56.0,aw=3.5,xh=10.5,rib_w=8.0,rib_y0=None,core=54.8,core_h=75.3,tray=0.5,fl_t=5.0,hub_end=12.0)
Ym=P['r_h']+P['gap']            # plate inner face
P['rib_y0']=round(math.sqrt((P['r_h']+P['gap'])**2-(31-P['rib_w'])**2)+0.1,2)  # rib follows housing at >=3 mm
Yf=Ym+P['tp']                    # pad mount face
Yc=Yf+P['tray']+P['core_h']      # contact face
def X(a): return cq.Workplane('YZ').workplane(offset=a)
hous=(X(-6.5).circle(50).circle(35).extrude(13)).union(X(-7.5).circle(54).circle(50).extrude(15))
hub=X(-6.5).circle(35).circle(27).extrude(6.5+P['hub_end'])
fl=X(P['hub_end']).circle(38).circle(18).extrude(P['fl_t'])
for k in range(8):
    t=math.radians(45*k); fl=fl.cut(X(P['hub_end']-1).center(31*math.cos(t),31*math.sin(t)).circle(2.25).extrude(8))
for t in (112.5,292.5):
    t=math.radians(t); fl=fl.cut(X(P['hub_end']-1).center(28.5*math.cos(t),28.5*math.sin(t)).circle(3).extrude(8))
L=P['ax1']-P['ax0']
arm=cq.Workplane('XY').box(L,Yf-0,P['az']).translate(((P['ax0']+P['ax1'])/2,Yf/2,0))
arm=arm.cut(cq.Workplane('XY').box(L-2*P['aw'],Ym-2*P['aw'],P['az']-2*P['aw']).translate(((P['ax0']+P['ax1'])/2,(Ym)/2,0)))
arm=arm.edges('|Y').fillet(3)
plate=cq.Workplane('XY').box(P['ax1']+31,P['tp'],62).translate(((P['ax1']-31)/2,Ym+P['tp']/2,0))
haunch=cq.Workplane('XY').box(P['ax0']-P['xh'],12,P['az']).translate(((P['ax0']+P['xh'])/2,Ym-6,0))
ribs=None
for sz in (1,-1):
    r=cq.Workplane('XY').box(31+P['xh'],Ym-P['rib_y0'],P['rib_w']).translate(((P['xh']-31)/2,(Ym+P['rib_y0'])/2,sz*(31-P['rib_w']/2)))
    ribs=r if ribs is None else ribs.union(r)
plate=plate.union(haunch).union(ribs)
carrier=fl.union(arm).union(plate)
pad=cq.Workplane('XY').box(P['core'],P['tray']+P['core_h'],P['core']).translate((0,Yf+(P['tray']+P['core_h'])/2,0))
for n,w in (('carrier_w2',carrier),('housing_7013_coaxX',hous),('hub_r15',hub),('pad_envelope_w2',pad)):
    cq.exporters.export(w,n+'.step'); cq.exporters.export(w,n+'.stl')
from OCP.BRepExtrema import BRepExtrema_DistShapeShape
def dist(a,b): d=BRepExtrema_DistShapeShape(a.val().wrapped,b.val().wrapped); d.Perform(); return round(d.Value(),2)
rho=2.81e-6
mass=dict(carrier_side_kg=round(carrier.val().Volume()*rho+8*0.0021+2*0.0022,4))
booked_side=0.102+0.044/2+0.140/2
mass.update(booked_side=round(booked_side,4),delta_pair_vs_booked=round(2*(mass['carrier_side_kg']-booked_side),3),
            note='booked = R-121/R-123 0.102/side + R-125 (a) stand-off net +0.044 pair + carrier +0.140 pair [EST]')
clr=dict(carrier_to_housing=dist(carrier,hous),pad_to_housing=dist(pad,hous),carrier_to_hub_interference_cm3=round(carrier.intersect(hous).val().Volume()/1e3,3) if True else None)
# loads (R-125 W2): Fn 6761, Fs 1812, contact Y Yc, pad Z0
Fn,Fs=7000*math.cos(math.radians(15)),7000*math.sin(math.radians(15))
def s0(e): M=Fs*math.hypot(Yc,0)/1e3+Fn*e/1e3; return round(27700/(Fn+2*M/0.085+0.44*Fs),3)
Mx=round(Fs*Yc/1e3); xa=(P['ax0']+P['ax1'])/2
# arm root (at flange, Y~0..38): bending about Z from Fn at lever xa (pad centre X0) ; about X from Fs (down) at lever Yc
b,dz,w=L,P['az'],P['aw']; A=b*dz-(b-2*w)*(dz-2*w)
Iz=(dz*b**3-(dz-2*w)*(b-2*w)**3)/12; Ix=(b*dz**3-(b-2*w)*(dz-2*w)**3)/12
sig_arm=Fn/A+Fn*xa*(b/2)/Iz+Fs*Yc*(dz/2)/Ix
# plate cantilever from arm (x=ax0) toward -X: root moment = Fn*(ax0-0) (pad centred X0), width 62
q=Fn/P['core']; a=P['xh']+P['core']/2; Mpl=q*a*a/2   # load on x<xh about root x=xh
tp,d,bw=P['tp'],Ym-P['rib_y0'],P['rib_w']; Ap=62*tp; Ar=2*bw*d; yc=(Ap*tp/2-Ar*d/2)/(Ap+Ar)
Ipl=62*tp**3/12+Ap*(tp/2-yc)**2+2*bw*d**3/12+Ar*(d/2+yc)**2; cbot=yc+d
sig_pl=Mpl*cbot/Ipl
K=2.86
st=dict(arm_hand=round(sig_arm,1),arm_cal_x2p86=round(K*sig_arm),plate_root_hand=round(sig_pl,1),plate_root_Kt1p5=round(1.5*sig_pl),plate_root_M_Nmm=round(Mpl),gate=320,note='plate: rib-stiffened T (ribs follow housing, >=3 mm), Kt 1.5 at R3 root [EST]; FEA decides')
# pad-centre X displacement under load (feeds e): arm rotation about Z * Yc lever? Fn bends arm in X: tip dx = Fn*xa*Lr^2/(2EIz)
E=70000; Lr=Ym
dx=Fn*xa*Lr**2/(2*E*Iz); dpl=q*a**4/(8*E*Ipl)  # plate tip (Y) deflection
defl=dict(pad_dx_arm_mm=round(dx,3),plate_tip_dy_mm=round(dpl,3),pad_dx_cal_mm=round(dx*37.4/ (37.4/2.86) ,3))
out=dict(params=P,Ym=Ym,Yf=Yf,contact_Y=Yc,s0={'e0':s0(0),'e2.4':s0(2.4)},Mx_Nm=Mx,CSG25_SF_fault=round(369/(1.05*Mx),2),
         stress=st,deflection=defl,clearance_mm=clr,mass=mass)
json.dump(out,open('r15_w2.json','w'),indent=1); print(json.dumps(out,indent=1))
