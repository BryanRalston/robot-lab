"""Find clash-free range per leg joint (others at 0, other leg standing, arms hanging) in 5° steps. Writes out/sweep.json"""
import json,clash,sys
NEED={'hip_pitch':(-100,30),'hip_roll':(0,15),'knee':(0,120),'ankle_pitch':(-35,30),'ankle_roll':(-20,20),'hip_yaw':(-20,30)}  # functional need [EST]
base=json.loads(sys.argv[1]) if len(sys.argv)>1 else {}
res={}
import io,contextlib
for jn,(lo,hi) in clash.LIM_V2_0.items():
    r=[]
    for sgn,end in ((-1,lo),(1,hi)):
        ok=0;a=0
        while True:
            a2=a+sgn*5
            if (sgn<0 and a2<end) or (sgn>0 and a2>end): break
            with contextlib.redirect_stdout(io.StringIO()): c=clash.run(dict(base,**{f'L_{jn}':a2}),'x')
            if c: break
            ok=a2;a=a2
        r.append(ok)
    res[jn]=dict(clash_free=r,need=NEED[jn],ok=r[0]<=NEED[jn][0] and r[1]>=NEED[jn][1])
    print(jn,res[jn],flush=True)
# combined test: pelvis shifted over the left foot = both hips rolled the same way (stance adduction + swing abduction)
import io as _io
for a in (-5,-8,-10,-12):
    with contextlib.redirect_stdout(_io.StringIO()): c=clash.run({'L_hip_roll':a,'R_hip_roll':a},'x')
    res[f'both_hip_roll={a}']=dict(clashes=len(c));print('both hips roll',a,'clashes',len(c),flush=True)
json.dump(res,open('out/sweep.json','w'),indent=1)
