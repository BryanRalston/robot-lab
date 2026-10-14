"""Re-split sim torso body (frame = waist_pitch joint, as body 'torso' in sim/v3/humanoid_v3.xml) -> sim_torso_body_r1.json.
For Controls to merge; sim/v3 not edited. Boxes: (name, kg, pos xyz m, size full xyz m, line/owner)."""
import json, numpy as np
P = [("torso shell CFRP 2 mm (hollow box 0.22x0.33x0.36)", 1.705, (0,0,0.18), (0.22,0.33,0.36), "torso", True),
     ("shoulder bulkhead 7075 12 mm", 0.600, (0,0,0.22), (0.10,0.30,0.12), "torso", False),
     ("waist ring 7075", 0.250, (0,0,0.02), (0.12,0.12,0.03), "torso", False),
     ("pack rails + latch", 0.200, (-0.01,0,0.10), (0.19,0.22,0.02), "torso", False),
     ("power distribution board/busbars", 0.250, (0.06,0,0.16), (0.03,0.15,0.10), "torso", False),
     ("duct, partition, fan, TSR", 0.187, (0.05,0,0.27), (0.08,0.12,0.12), "torso", False),
     ("regen clamp P-045", 0.150, (-0.07,0,0.25), (0.05,0.15,0.04), "torso", False),
     ("pack disconnect (contactor, pre-charge)", 0.232, (0.07,0.05,0.18), (0.05,0.05,0.07), "torso", False),
     ("battery 20S5P 185x220x144 (lower chest bay)", 8.750, (-0.01,0,0.11), (0.144,0.22,0.185), "battery", False),
     ("brain (Thor+AGX301+DCM+JCB022), credited", 1.261, (0.03,0,0.29), (0.10,0.15,0.06), "brain", False),
     ("L shoulder_pitch actuator (housing in torso wall)", 1.52, (0,0.17,0.22), None, "arms (arm_inertials_r3.json)", False),
     ("R shoulder_pitch actuator (housing in torso wall)", 1.52, (0,-0.17,0.22), None, "arms (arm_inertials_r3.json)", False)]
m = sum(p[1] for p in P); com = sum(p[1]*np.array(p[2]) for p in P)/m
I = np.zeros((3,3))
for n, k, pos, sz, own, hollow in P:
    Ic = np.zeros((3,3))
    if n.startswith(("L shoulder","R shoulder")):
        Ic = np.diag([0.001812,0.001751,0.001812])          # from arm_inertials_r3.json
    elif sz:
        a,b,c = sz; f = 1/6 if hollow else 1/12   # thin-shell approx for the shell
        Ic = np.diag([f*k*(b*b+c*c), f*k*(a*a+c*c), f*k*(a*a+b*b)])
    d = np.array(pos)-com; I += Ic + k*(np.dot(d,d)*np.eye(3)-np.outer(d,d))
out = {"body": "torso", "frame": "waist_pitch joint (sim/v3 body 'torso' origin)", "mass": round(m,3),
       "pos": [round(x,4) for x in com], "fullinertia": [round(I[0,0],5),round(I[1,1],5),round(I[2,2],5),round(I[0,1],6),round(I[0,2],6),round(I[1,2],6)],
       "replaces": "sim/v3 torso inertial mass 18.762 pos (-0.0008,0,0.1687)",
       "notes": "Excludes head/neck (own body), arms below shoulder_pitch output, waistY, pelvis, harness/covers (not localized; add 0.3-0.5 kg [EST] if Controls wants them lumped). Shoulder_pitch 2x1.52 belongs to Arms' mass line, not torso. Geometry [EST] until CAD.",
       "parts": [dict(name=p[0], mass=p[1], pos=list(p[2]), line=p[4]) for p in P]}
json.dump(out, open("sim_torso_body_r1.json","w"), indent=1); print(out["mass"], out["pos"], out["fullinertia"])
