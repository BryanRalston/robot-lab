"""P-023 rev 8b hem re-sweep on T&R ca68f3a's grid (r_hip_pinch_check.py: 2240 poses, roll stops -12/+15 + 2.5 deg overtravel, yaw -37.5..47.5).
Uses hip_skirt_r8.py geometry with the rev 8b panel (inboard edge y 86 + 40 mm inboard-rear chamfer) and a fixed hem radius; L/R part skipped (see hip_skirt_r8_asym.py)."""
import sys, json, os
H=os.path.dirname(os.path.abspath(__file__)); p=os.path.join(H,'hip_skirt_r8.py')
out={}
for R1 in [float(a) for a in (sys.argv[1:] or ['152.8','146.5'])]:
    src=open(p).read().split("AX=np.array")[0]
    src=src.replace("POSES=[(p,r,y) for p in list(range(-100,41,10))+[-107.3,-60] for r in (-20,0,15,30,45) for y in (-35,0,45)]",
     "POSES=[(p,r,y) for p in list(range(-105,41,5))+[-107.5,42.5] for r in (-20,-14.5,-12,-8,-4,0,5,10,15,17.5) for y in (-37.5,-35,-17,0,22,45,47.5)]")
    src=src.replace("P=cyl(150,35,60,y0=60)","P=cyl(150,35,60,y0=86)")
    src=src.replace("R1=dmin[0]-25",f"R1={R1}")
    ns={'__file__':p}; exec(compile(src,'x','exec'),ns); hem=ns['hem']
    rom=[(g,q) for g,q in hem if -12<=q[1]<=15 and -35<=q[2]<=45 and -105<=q[0]<=40]
    ovt=[(g,q) for g,q in hem if -14.5<=q[1]<=17.5]
    out[R1]=dict(poses=len(hem),min_ROM=[round(min(rom)[0],1),min(rom)[1]],min_ROM_ovt=[round(min(ovt)[0],1),min(ovt)[1]],
                 min_ovt_minus_tol2=round(min(ovt)[0]-2,1),retained_pct=round(100*ns['ret'],1),band_5_25_ovt=sum(5<g<25 for g,q in ovt))
    print(R1,out[R1],flush=True)
json.dump(out,open(os.path.join(H,'hip_skirt_r8b.json'),'w'),indent=1)
