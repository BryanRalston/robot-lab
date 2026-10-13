"""Round 2: knee lever sweep (58.5 -> 40 mm) and hip_pitch twin-screw geometry, 2-D sagittal slider-crank.
Joint-angle-resolved needs come from the gait ID (results/<dir>/*.npz): per 5-deg bin, need torque = 1.5 x max|tau| (R-004 margin rule,
non-carry cases) and carry check = 1.2 x carry max|tau| (R-003); need speed = max|omega| in the bin.
Actuator side (Actuators' current selection, modules/actuators/results/sizing.json, not changed here):
  total screw force F = T_out / arm_nominal (both screws, incl. efficiency); max screw speed v = 0.95*Nmax*lead.
  joint torque(theta) = F*arm(theta); joint speed(theta) = v/arm(theta), arm = perpendicular distance of the screw line from the joint axis.
Geometry search per lever radius: lever clock angle and trunnion position (x,z) on the parent; a geometry is valid if arm >= 8 mm everywhere
in the ROM (no toggle) and the screw stroke (Lmax-Lmin) is reported. Pin-to-pin length must be >= 250 mm (actuator stack). Clearance to structure is NOT checked here (needs CAD, see grokbuild brief)."""
import json,os,sys,itertools,numpy as np
from gait_lib import LEG,HERE
D=os.path.join(HERE,'results',sys.argv[1] if len(sys.argv)>1 else 'r2')
A=json.load(open(os.path.join(HERE,'..','actuators','results','sizing.json')))['sel']
NONCARRY=['walk_1p2','walk_1p0','walk_0p8','stairs_18cm','push_recover','sit_to_stand']; CARRY=['carry_20kg']
def needs(j,rom,step=5):
    bins=np.arange(rom[0],rom[1]+step,step); T=np.zeros(len(bins)); W=np.zeros(len(bins)); C=np.zeros(len(bins))
    for s in NONCARRY+CARRY:
        f=os.path.join(D,s+'.npz')
        if not os.path.exists(f): continue
        d=np.load(f); i=LEG.index(j)
        for off in (0,6):
            q=np.degrees(d['Q'][:,d['qa'][i+off]]); t=np.abs(d['TAU'][:,d['va'][i+off]]); w=np.abs(d['V'][:,d['va'][i+off]])
            b=np.clip(np.round((q-rom[0])/step).astype(int),0,len(bins)-1)
            for k in range(len(bins)):
                sel=b==k
                if sel.any():
                    if s in CARRY: C[k]=max(C[k],1.2*t[sel].max())
                    else: T[k]=max(T[k],1.5*t[sel].max()); W[k]=max(W[k],w[sel].max())
    return bins,T,W,C
def profile(th_deg,r,clock,tx,tz,sign):
    """joint at origin; lever end E rotates with the child: E = r*(sin(a),cos(a)) style in x-z; trunnion T fixed on parent."""
    a=np.radians(clock+sign*th_deg); E=np.stack([-r*np.sin(a),-r*np.cos(a)],1); d=np.array([tx,tz])-E; L=np.hypot(d[:,0],d[:,1])
    arm=np.abs(E[:,0]*d[:,1]-E[:,1]*d[:,0])/L
    return arm,L
LMIN=250.0   # mm, minimum pin-to-pin length: v3 knee unit stack 247 mm (REVISIONS F / CONTRACTS 1b)
def study(j,rom,levers,Fdict,vmax,sign,tx_r,tz_r,clocks):
    bins,T,W,C=needs(j,rom); out=[]
    for r in levers:
        best=None
        for c,tx,tz in itertools.product(clocks,tx_r,tz_r):
            arm,L=profile(bins.astype(float),r,c,tx,tz,sign)
            if arm.min()<8 or L.min()<LMIN: continue
            F=Fdict; Ta=F*arm/1000; Wa=vmax/(arm/1000)
            tr=np.min(np.where(T>0,Ta/np.maximum(T,1e-9),9)); wr=np.min(np.where(W>0,Wa/np.maximum(W,1e-9),9)); cr=np.min(np.where(C>0,Ta/np.maximum(C,1e-9),9))
            sc=min(tr,wr,cr)   # torque (1.5x non-carry), speed, and carry (1.2x) all at worst angle
            if best is None or sc>best['score']:
                best=dict(score=float(sc),torque_ratio_min=float(tr),speed_ratio_min=float(wr),carry_ratio_min=float(cr),geom=dict(lever_mm=r,clock_deg=c,trunnion_x_mm=tx,trunnion_z_mm=tz),
                          stroke_mm=float(L.max()-L.min()),Lmin_mm=float(L.min()),arm_min_mm=float(arm.min()),arm_max_mm=float(arm.max()),
                          worst_torque_angle_deg=float(bins[np.argmin(np.where(T>0,Ta/np.maximum(T,1e-9),9))]),worst_speed_angle_deg=float(bins[np.argmin(np.where(W>0,Wa/np.maximum(W,1e-9),9))]),
                          arm_profile=[(int(b),round(float(x),1)) for b,x in zip(bins,arm)])
        out.append(best); print(j,r,best and {k:(round(v,3) if isinstance(v,float) else v) for k,v in best.items() if k!='arm_profile'},flush=True)
    return dict(bins=bins.tolist(),need_T=T.tolist(),need_W=W.tolist(),carry_T=C.tolist(),results=out)
# knee: force from Actuators' selection (T_out at its nominal arm), screw speed at 95 % Nmax 8000 rpm
k=A['knee']; arm0=float(k['label'].split('arm ')[1].split(' mm')[0]); F_k=k['T_out']/(arm0/1000); lead_k=5.0 if 'RV12x5' in k['label'] else 4.0
vk=0.95*8000/60*lead_k/1000
h=A['hip_pitch']; F_h=h['T_out']/0.050; vh=0.95*8000/60*4.0/1000   # TBM2G-07613D Nmax 8000 rpm [sizing.py RPM_MARGIN], RV12x4
print('knee F_total %.0f N, v_screw %.3f m/s (lead %.0f); hip F_total %.0f N, v %.3f m/s'%(F_k,vk,lead_k,F_h,vh))
res=dict(actuator_basis=dict(knee=dict(label=k['label'],F_total_N=F_k,v_screw_mps=vk),hip_pitch=dict(label=h['label'],F_total_N=F_h,v_screw_mps=vh)))
res['knee']=study('knee',(0,135),[58.5,55,52.5,50,47.5,45,42.5,40],F_k,vk,+1,range(-160,41,10),range(150,401,10),range(-40,61,5))
res['hip_pitch']=study('hip_pitch',(-120,40),[50],F_h,vh,+1,range(-300,301,10),range(-300,401,10),range(-180,180,10))
json.dump(res,open(os.path.join(D,'linkage_study.json'),'w'),indent=1)
# hip_pitch: packaging-constrained. (A) screw body on pelvis/lower torso (trunnion x -110..110, z +150..+450 mm above the hip axis), lever on thigh;
# (B) inverted: screw body along the thigh (trunnion x -60..60, z -150..-400), lever on the pelvis (relative rotation sign flips).
# Score over the loaded gait ROM (-80..+40); deep flexion (-120..-80, sit-to-stand only, need 111 N·m) reported separately.
for tag,sign,txr,tzr in (('A_pelvis_mounted',+1,range(-110,111,10),range(150,451,10)),('B_thigh_mounted',-1,range(-60,61,10),range(-400,-149,10))):
    g=study('hip_pitch',(-80,40),[50],F_h,vh,sign,txr,tzr,range(-180,180,5))
    if g['results'][0] is None: print(tag,'no valid geometry'); res['hip_pitch_'+tag]=g; continue
    bb=g['results'][0]['geom']; th=np.arange(-120,41,5.0); arm,L=profile(th,50,bb['clock_deg'],bb['trunnion_x_mm'],bb['trunnion_z_mm'],sign)
    g['full_rom_check']=dict(theta=th.tolist(),arm_mm=arm.round(1).tolist(),torque_Nm=(F_h*arm/1000).round(0).tolist(),stroke_mm=float(L.max()-L.min()),Lmin_mm=float(L.min()),
        sit_need_Nm=111.0,deep_flexion_min_torque_Nm=float((F_h*arm/1000)[th<=-80].min()),arm_factor_min_gait=float(arm[(th>=-76)&(th<=4)].min()/50))
    print(tag,'full ROM: min torque -120..-80 = %.0f N·m (sit need 111), stroke %.0f mm, Lmin %.0f, arm factor min -76..4 = %.2f'%(g['full_rom_check']['deep_flexion_min_torque_Nm'],g['full_rom_check']['stroke_mm'],g['full_rom_check']['Lmin_mm'],g['full_rom_check']['arm_factor_min_gait']))
    res['hip_pitch_'+tag]=g
json.dump(res,open(os.path.join(D,'linkage_study.json'),'w'),indent=1)
