"""R15 e stack for W2 (R-125: drawing limit e <= 2.4 mm; ID tightens tray lip and core cut to 0.3 each). e = axial (X) offset of pad load line from the CRBH 7013 A plane."""
import json,math,os
H=os.path.dirname(os.path.abspath(__file__)); c=json.load(open(os.path.join(H,'cad/r15/r15_w2.json')))
tol={'bearing seat (H7) position':0.05,'CRBH runout / width centre':0.05,'hub end face to bearing plane':0.10,'flange thickness/flatness':0.05,
     'dowel location (D6 m6/H7, PCD57)':0.03,'carrier arm/plate machined position (one setup)':0.10,'tray M4 float':0.25,
     'tray lip to core (ID, tightened)':0.30,'core cut position/squareness (ID, tightened)':0.30,
     'elastic deflection in X (max of ID R11 0.69, W2 carrier calc %.2f) until Job 8b'%c['deflection']['pad_dx_cal_mm']:max(0.69,c['deflection']['pad_dx_cal_mm'])}
wc=round(sum(tol.values()),2); rss=round(math.sqrt(sum(v*v for v in tol.values())),2)
Fn,Fs=7000*math.cos(math.radians(15)),7000*math.sin(math.radians(15)); Y=c['contact_Y']
s0=lambda e:round(27700/(Fn+2*(Fs*Y/1e3+Fn*e/1e3)/0.085+0.44*Fs),3)
out=dict(contributors_mm=tol,worst_mm=wc,rss_mm=rss,limit_mm=2.3,e_at_s0_2=c['e_at_s0_2'],margin_worst_mm=round(2.3-wc,2),margin_to_s0_crossing_mm=round(c['e_at_s0_2']-wc,2),s0_at_worst=s0(wc),s0_at_rss=s0(rss),s0_at_limit=s0(2.3),
         verdict='PASS' if wc<=min(2.3,c['e_at_s0_2']) else 'FAIL')
json.dump(out,open(os.path.join(H,'e_stack_r15.json'),'w'),indent=1); print(out)
