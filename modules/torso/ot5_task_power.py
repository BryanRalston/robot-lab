"""O-T5 per-phase power (torso power model, r1_torso.py lineage + R1.2/R1.4 adds) and runtime for Controls' tasks (fee4ed2)."""
import json
P = {"walk": 712.1,          # 703.4 (R1.3) + torso adds 8.4 (R1.2) + BMS +0.26 (R1.4)
     "carry-walk": round(712.1*837/772, 1),  # carry/walk ratio from sizing.md no-regen rows [EST]
     "stand": 262.7,         # 254 rest + 40 copper - 40 compute cap + 8.4 + 0.26 [EST]
     "pick/place": 262.7+40+3.6*2, # + compute uncap 40 [EST] + bay 3.6 W/side hold (Arms R4)
     "idle": 262.7-10.0}     # arms down, low copper [EST]
T = {"T-A 5 m tote": [("idle",20),("stand",2),("pick/place",6),("stand",3),("carry-walk",6),("pick/place",6),("stand",3),("walk",6)],
     "T-B 10 m tote": [("idle",20),("stand",2),("pick/place",6),("stand",3),("carry-walk",11),("pick/place",6),("stand",3),("walk",11)],
     "T-C 20 m tote": [("idle",20),("stand",2),("pick/place",6),("stand",3),("carry-walk",21),("pick/place",6),("stand",3),("walk",21)],
     "T-D shelf pick": [("stand",32),("pick/place",192),("walk",12),("carry-walk",16),("idle",30),("walk",25)],
     "T-E kitting": [("pick/place",120),("walk",10),("idle",60)]}
out = {"P_W": P, "tasks": {}}
for n, ph in T.items():
    t = sum(d for _, d in ph); E = sum(P[c]*d for c, d in ph); Pm = E/t
    out["tasks"][n] = dict(cycle_s=t, mean_W=round(Pm,1), h_typ=round(1458/Pm,2), h_binned=round(1425.6/Pm,2))
json.dump(out, open("ot5_task_power.json","w"), indent=1); print(json.dumps(out, indent=1))
